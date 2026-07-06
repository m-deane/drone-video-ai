"""Thin subprocess wrapper around ``ffprobe`` used to populate the
``source_file`` block of the highlight manifest (and, in Capability 2,
Capability 2's color-metadata pinning step).

Per the plan's grounding notes, real sample footage in this repo reports
``color_range``/``color_space``/``color_transfer``/``color_primaries`` as the
literal string ``"unknown"`` (or the tag is entirely absent from the ffprobe
JSON) on every sample clip. This module never substitutes a default value for
those tags -- it passes through whatever ffprobe reports (including the
string ``"unknown"``) or ``None`` if the tag is missing altogether, so
downstream consumers can tell "asserted unknown" apart from "tag absent".
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Optional


class FFProbeError(RuntimeError):
    """Raised when ffprobe fails to run or returns unparseable output."""


@dataclass(frozen=True)
class SourceFileInfo:
    """Subset of ffprobe-derived metadata needed for the highlight manifest's
    ``source_file`` block plus the color-metadata tags Capability 2 needs."""

    path: str
    name: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    pix_fmt: str
    color_range: Optional[str]
    color_space: Optional[str]
    color_transfer: Optional[str]
    color_primaries: Optional[str]
    # Additive field (Capability 2): stream time_base (e.g. "1/12800"), used by
    # reel_stitching's stream-copy compatibility precheck (plan.md's "codec/
    # resolution/pixel-format/timebase" precondition). Optional/defaulted so
    # existing Capability 1 call sites and tests are unaffected.
    time_base: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "codec": self.codec,
            "pix_fmt": self.pix_fmt,
        }


def _parse_fps(rate_str: Optional[str]) -> float:
    """Parse ffprobe's ``r_frame_rate`` (e.g. "30000/1001") into a float."""
    if not rate_str:
        return 0.0
    try:
        return float(Fraction(rate_str))
    except (ValueError, ZeroDivisionError):
        return 0.0


def _normalize_tag(value: Any) -> Optional[str]:
    """Pass through a color-metadata tag verbatim. ``None`` means the tag was
    absent from ffprobe's output; the literal string "unknown" (ffprobe's own
    "I don't know" sentinel) is passed through unchanged, never coerced to a
    default."""
    if value is None:
        return None
    return str(value)


def probe_source_file(path: str, ffprobe_bin: str = "ffprobe") -> SourceFileInfo:
    """Run ffprobe against ``path`` and return a :class:`SourceFileInfo`.

    Raises :class:`FFProbeError` if ffprobe is not found, exits non-zero, or
    returns JSON that lacks a usable video stream.
    """
    p = Path(path)
    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        str(p),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise FFProbeError(f"ffprobe binary not found: {ffprobe_bin}") from exc

    if proc.returncode != 0:
        raise FFProbeError(
            f"ffprobe failed on {path!r} (exit {proc.returncode}): {proc.stderr.strip()}"
        )

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise FFProbeError(f"ffprobe returned unparseable JSON for {path!r}") from exc

    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    if not video_streams:
        raise FFProbeError(f"No video stream found in {path!r}")
    vstream = video_streams[0]
    fmt = data.get("format", {})

    duration_str = vstream.get("duration") or fmt.get("duration")
    try:
        duration = float(duration_str) if duration_str is not None else 0.0
    except ValueError:
        duration = 0.0

    return SourceFileInfo(
        path=str(p),
        name=p.name,
        duration=duration,
        width=int(vstream.get("width", 0) or 0),
        height=int(vstream.get("height", 0) or 0),
        fps=_parse_fps(vstream.get("r_frame_rate")),
        codec=str(vstream.get("codec_name", "") or ""),
        pix_fmt=str(vstream.get("pix_fmt", "") or ""),
        color_range=_normalize_tag(vstream.get("color_range")),
        color_space=_normalize_tag(vstream.get("color_space")),
        color_transfer=_normalize_tag(vstream.get("color_transfer")),
        color_primaries=_normalize_tag(vstream.get("color_primaries")),
        time_base=_normalize_tag(vstream.get("time_base")),
    )


def probe_keyframe_times(
    path: str, ffprobe_bin: str = "ffprobe"
) -> list:
    """Return a sorted list of presentation timestamps (float seconds) of
    every keyframe (IDR/I-frame) in ``path``'s first video stream.

    Used by Capability 2's stream-copy precondition check: the ffmpeg
    concat demuxer's ``-c copy`` path silently seeks to the nearest
    *preceding* keyframe when an entry's ``in_tc`` isn't itself a keyframe,
    which would silently render a different (earlier) start point than
    requested. Callers must verify each cut point against this list and
    fail loudly rather than accept that silent drift.
    """
    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-select_streams", "v:0",
        "-skip_frame", "nokey",
        "-show_entries", "frame=pts_time",
        "-of", "csv=p=0",
        str(path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise FFProbeError(f"ffprobe binary not found: {ffprobe_bin}") from exc
    if proc.returncode != 0:
        raise FFProbeError(
            f"ffprobe keyframe probe failed on {path!r} (exit {proc.returncode}): "
            f"{proc.stderr.strip()}"
        )
    times = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # ffprobe's csv=p=0 output occasionally emits a trailing comma (an
        # empty extra field) on the first row only -- split defensively
        # rather than assuming exactly one token per line.
        token = line.split(",")[0].strip()
        if not token:
            continue
        try:
            times.append(float(token))
        except ValueError:
            continue
    return sorted(times)
