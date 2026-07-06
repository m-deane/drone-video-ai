"""Edit-manifest dataclasses and JSON (de)serialization.

This is Capability 2's *input* schema, exactly as fixed in
``.claude/specs/drone-video-pipeline/plan.md`` section "2. Edit manifest".
It is intentionally decoupled from Capability 1's ``HighlightManifest``
output schema (``common/manifest.py``) -- an edit manifest MAY be authored
by hand, by copying segments out of one or more highlight manifests, or by
any future selection tool; ``EditManifest`` only needs to parse this shape.

Timecode fields (``in_tc``/``out_tc``) reuse the same "float seconds"
convention as Capability 1's ``Segment.start_time``/``end_time``, per the
instruction to keep timecode representation consistent where the two
schemas overlap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

EDIT_MANIFEST_VERSION = 1

# transition_to_next.type == "cut" means "concat-demuxer hard cut, no xfade
# filter invoked" (plan.md). Any other string names an ffmpeg xfade
# transition (e.g. "fade", "wipeleft", "wiperight", ...).
CUT_TRANSITION_TYPE = "cut"


@dataclass
class TransitionSpec:
    type: str = CUT_TRANSITION_TYPE
    duration: float = 0.0

    def __post_init__(self) -> None:
        if self.type == CUT_TRANSITION_TYPE and self.duration != 0.0:
            raise ValueError(
                "TransitionSpec.duration must be 0.0 when type == 'cut' "
                f"(got duration={self.duration!r})"
            )
        if self.duration < 0.0:
            raise ValueError(f"TransitionSpec.duration must be >= 0.0 (got {self.duration!r})")

    @property
    def is_cut(self) -> bool:
        return self.type == CUT_TRANSITION_TYPE

    def to_dict(self) -> dict:
        return {"type": self.type, "duration": self.duration}

    @classmethod
    def from_dict(cls, d: dict) -> "TransitionSpec":
        return cls(type=d["type"], duration=d["duration"])


@dataclass
class EditEntry:
    clip_path: str
    in_tc: float
    out_tc: float
    transition_to_next: TransitionSpec

    def __post_init__(self) -> None:
        if not self.clip_path:
            raise ValueError("EditEntry.clip_path must be a non-empty string")
        if self.out_tc <= self.in_tc:
            raise ValueError(
                f"EditEntry.out_tc ({self.out_tc}) must be greater than "
                f"in_tc ({self.in_tc}) for clip_path={self.clip_path!r}"
            )

    @property
    def duration(self) -> float:
        return self.out_tc - self.in_tc

    def to_dict(self) -> dict:
        return {
            "clip_path": self.clip_path,
            "in_tc": self.in_tc,
            "out_tc": self.out_tc,
            "transition_to_next": self.transition_to_next.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EditEntry":
        return cls(
            clip_path=d["clip_path"],
            in_tc=d["in_tc"],
            out_tc=d["out_tc"],
            transition_to_next=TransitionSpec.from_dict(d["transition_to_next"]),
        )


@dataclass
class EditManifest:
    entries: list
    target_duration: "float | None" = None
    version: int = EDIT_MANIFEST_VERSION

    def __post_init__(self) -> None:
        if not self.entries:
            raise ValueError("EditManifest.entries must be non-empty")
        last = self.entries[-1]
        if not last.transition_to_next.is_cut or last.transition_to_next.duration != 0.0:
            raise ValueError(
                "The final EditManifest entry's transition_to_next must be the "
                "{'type': 'cut', 'duration': 0.0} sentinel -- there is no clip "
                "after the last entry to transition into"
            )

    @property
    def content_duration(self) -> float:
        """Sum of per-entry durations minus transition-window overlaps --
        i.e. the actual wall-clock length of the rendered reel (a crossfade
        of duration D between two clips shortens the combined timeline by D,
        since the transition window is shared between them, not appended)."""
        total = sum(e.duration for e in self.entries)
        overlap = sum(
            e.transition_to_next.duration for e in self.entries if not e.transition_to_next.is_cut
        )
        return total - overlap

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "target_duration": self.target_duration,
            "entries": [e.to_dict() for e in self.entries],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "EditManifest":
        return cls(
            version=d.get("version", EDIT_MANIFEST_VERSION),
            target_duration=d.get("target_duration"),
            entries=[EditEntry.from_dict(e) for e in d["entries"]],
        )

    @classmethod
    def from_json(cls, s: str) -> "EditManifest":
        return cls.from_dict(json.loads(s))
