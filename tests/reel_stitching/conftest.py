"""Shared synthetic-clip fixtures for the Capability 2 (Reel Stitching)
Milestone 1 test suite.

Every clip is generated at test time via ffmpeg lavfi ``testsrc`` (a
moving, per-frame-distinct pattern, so framemd5 hashes actually differ
frame-to-frame -- a meaningful correctness signal, not a degenerate
all-identical-hash pass) encoded with ``-g 1`` (every frame forced to be a
keyframe/IDR). This keeps every timecode in a test manifest trivially
keyframe-aligned, which is the realistic precondition an edit manifest's
author is expected to satisfy for the concat-demuxer stream-copy path (see
render.py's module docstring) without needing GOP-boundary arithmetic in
every test. No large binaries are checked into the repo.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _run_ffmpeg(args) -> None:
    cmd = ["ffmpeg", "-y", "-v", "error"] + list(args)
    subprocess.run(cmd, check=True)


def make_cuttable_clip(
    path: Path,
    duration: float = 6.0,
    size: str = "160x120",
    fps: int = 10,
) -> None:
    """An h264/yuv420p clip with a keyframe on every frame, so any timecode
    that lands on a frame boundary is keyframe-aligned. No explicit color
    metadata is set (mirrors this repo's real sample footage, which reports
    color tags as absent/"unknown" -- see plan.md's grounding notes)."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"testsrc=size={size}:rate={fps}:duration={duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-g", "1", "-keyint_min", "1", "-sc_threshold", "0",
        str(path),
    ])


@pytest.fixture
def cuttable_clip_factory(tmp_path):
    def _make(name: str = "clip.mp4", **kwargs) -> Path:
        path = tmp_path / name
        make_cuttable_clip(path, **kwargs)
        return path

    return _make
