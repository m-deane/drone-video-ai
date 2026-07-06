"""Duration/pacing control: given an :class:`EditManifest` and a
``target_duration``, compute per-clip trims that bring the manifest's
:pyattr:`EditManifest.content_duration` within a configurable tolerance of
the target -- as an explicit, inspectable intermediate ``EditManifest``,
never applied silently during render (plan.md task 2.3, spec AC2.5).

Trimming/extension is applied uniformly (a single scale factor across every
entry's duration, from each entry's tail) rather than favoring one clip,
since Milestone 1 has no per-clip priority signal to weight unevenly.
Extension (growing entries beyond their current ``out_tc``) is bounded by
each source clip's real duration, probed via ``ffprobe``, and never allowed
to exceed it or to grow to a non-positive-duration entry.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Optional

from drone_video_ai.common.ffprobe import probe_source_file
from drone_video_ai.reel_stitching.edit_manifest import EditEntry, EditManifest

DEFAULT_TOLERANCE = 0.5  # seconds, per spec's stated default (+/-0.5s)

# Never let a paced entry's duration collapse below this floor, even under
# aggressive proportional shrink -- an entry must still contain at least one
# real frame's worth of content.
MIN_ENTRY_DURATION = 0.04  # seconds (~1 frame at 25fps)


class PacingError(RuntimeError):
    """Raised when a target duration cannot be honored within tolerance even
    after maximal shrink/extend, so the caller is never silently handed a
    manifest whose real duration diverges from what it asked for."""


def _probe_durations(entries, ffprobe_bin: str) -> Dict[str, float]:
    durations: Dict[str, float] = {}
    for e in entries:
        if e.clip_path not in durations:
            info = probe_source_file(e.clip_path, ffprobe_bin=ffprobe_bin)
            durations[e.clip_path] = info.duration
    return durations


def apply_target_duration(
    manifest: EditManifest,
    target_duration: Optional[float] = None,
    tolerance: float = DEFAULT_TOLERANCE,
    ffprobe_bin: str = "ffprobe",
) -> EditManifest:
    """Return a new :class:`EditManifest` whose ``content_duration`` is
    within ``tolerance`` seconds of ``target_duration``.

    ``target_duration=None`` (or the manifest's own ``target_duration`` when
    the argument is omitted) means "use full entries as-is" per plan.md --
    the manifest is returned unchanged (a shallow copy) in that case.

    Raises :class:`PacingError` if the target cannot be reached within
    tolerance (e.g. requesting a duration larger than every source clip's
    combined real length can support).
    """
    target = target_duration if target_duration is not None else manifest.target_duration
    if target is None:
        return EditManifest(
            entries=list(manifest.entries),
            target_duration=manifest.target_duration,
            version=manifest.version,
        )

    current = manifest.content_duration
    diff = target - current
    if abs(diff) <= tolerance:
        return EditManifest(
            entries=list(manifest.entries), target_duration=target, version=manifest.version
        )

    overlap = sum(
        e.transition_to_next.duration
        for e in manifest.entries
        if not e.transition_to_next.is_cut
    )
    target_content_total = target + overlap  # sum-of-entry-durations needed
    current_total = sum(e.duration for e in manifest.entries)
    if current_total <= 0:
        raise PacingError("EditManifest has zero total entry duration; cannot pace.")
    ratio = target_content_total / current_total

    source_durations = None
    if ratio > 1.0:
        source_durations = _probe_durations(manifest.entries, ffprobe_bin)

    new_entries = []
    for e in manifest.entries:
        new_duration = e.duration * ratio
        if new_duration < MIN_ENTRY_DURATION:
            raise PacingError(
                f"Cannot shrink entry for {e.clip_path!r} to duration "
                f"{new_duration:.4f}s (below the {MIN_ENTRY_DURATION}s floor) "
                f"while reaching target_duration={target}."
            )
        new_out_tc = e.in_tc + new_duration
        if source_durations is not None:
            available = source_durations[e.clip_path]
            if new_out_tc > available:
                raise PacingError(
                    f"Cannot extend entry for {e.clip_path!r} to out_tc="
                    f"{new_out_tc:.3f}s: source clip is only {available:.3f}s long."
                )
        new_entries.append(replace(e, out_tc=new_out_tc))

    paced = EditManifest(entries=new_entries, target_duration=target, version=manifest.version)

    achieved = paced.content_duration
    if abs(achieved - target) > tolerance:
        raise PacingError(
            f"Paced manifest's content_duration ({achieved:.3f}s) is still outside "
            f"tolerance ({tolerance}s) of target ({target}s) after proportional "
            "trim/extend -- source clips cannot support this target duration."
        )
    return paced
