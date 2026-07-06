"""``ffmpeg -f framemd5`` byte-exact verification between source frame
ranges and the corresponding stream-copied output frame ranges (plan.md
task 2.6, spec AC2.1).

Checked against each stream-copy run's *isolated* rendered file (see
``render.py``'s module docstring for why: it removes any ambiguity from
seeking across a codec-parameter boundary inside the final, possibly
transition-containing, merged output) -- this is a mechanical, tool-grounded
check (Constitution rule 6), not a manual/visual spot check, and it is
exercised by ``tests/reel_stitching/test_concat_demuxer_framemd5.py``.
"""

from __future__ import annotations

import subprocess
from typing import List

from drone_video_ai.reel_stitching.render import FrameRangeCheck, RenderResult


class VerificationError(RuntimeError):
    """Raised when a stream-copy region's framemd5 hashes diverge from its
    corresponding source region -- i.e. the stream-copy path silently
    altered pixel data, which must never happen."""


def _framemd5_hashes(path: str, start: float, duration: float, ffmpeg_bin: str = "ffmpeg") -> List[str]:
    """Return the list of per-frame MD5 hash lines ffmpeg's ``framemd5``
    muxer emits for the video stream over ``[start, start + duration)`` of
    ``path``. Comment/header lines (starting with ``#``) are stripped."""
    cmd = [
        ffmpeg_bin, "-v", "error",
        "-ss", str(start), "-i", path, "-t", str(duration),
        "-map", "0:v:0",
        "-f", "framemd5", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise VerificationError(
            f"ffmpeg framemd5 failed on {path!r} [{start}, {start + duration}): {proc.stderr.strip()}"
        )
    return [line for line in proc.stdout.splitlines() if line and not line.startswith("#")]


def verify_frame_range(check: FrameRangeCheck, run_output_path: str, ffmpeg_bin: str = "ffmpeg") -> None:
    """Assert byte-exact equality between ``check``'s source range and the
    corresponding range of ``run_output_path``. Raises
    :class:`VerificationError` on any divergence (including a differing
    frame count)."""
    src_hashes = _framemd5_hashes(check.clip_path, check.src_start, check.src_end - check.src_start, ffmpeg_bin)
    out_hashes = _framemd5_hashes(run_output_path, check.out_start, check.out_end - check.out_start, ffmpeg_bin)

    if len(src_hashes) != len(out_hashes):
        raise VerificationError(
            f"Frame-count mismatch for {check.clip_path!r} range "
            f"[{check.src_start}, {check.src_end}): source has {len(src_hashes)} "
            f"frames, output range [{check.out_start}, {check.out_end}) in "
            f"{run_output_path!r} has {len(out_hashes)} frames."
        )
    for i, (s, o) in enumerate(zip(src_hashes, out_hashes)):
        if s != o:
            raise VerificationError(
                f"framemd5 mismatch for {check.clip_path!r} at frame {i} of range "
                f"[{check.src_start}, {check.src_end}): source={s!r} output={o!r} "
                f"(output file {run_output_path!r})."
            )


def verify_render_result(result: RenderResult, ffmpeg_bin: str = "ffmpeg") -> None:
    """Verify every stream-copy region across every run in ``result``.
    Raises :class:`VerificationError` on the first divergence found."""
    for run in result.run_outputs:
        for check in run.checks:
            verify_frame_range(check, run.output_path, ffmpeg_bin=ffmpeg_bin)
