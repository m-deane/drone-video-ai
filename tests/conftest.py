"""Shared synthetic-clip fixture generators for the Capability 1 (Highlight
Extraction) Milestone 1 test suite.

No large binary fixtures are checked into the repo. Every clip used by the
fast/default test run is generated at test time -- either via ffmpeg
``lavfi`` source filters (solid colors, moving test patterns) for
black/frozen/exposure/scene-cut fixtures, or via ``cv2.VideoWriter`` for the
motion fixtures (smooth vs. jittery pans), since lavfi sources don't give
frame-by-frame control over trackable feature positions the way drawing
shapes directly does.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

import cv2
import numpy as np
import pytest


def _run_ffmpeg(args: List[str]) -> None:
    cmd = ["ffmpeg", "-y", "-v", "error"] + args
    subprocess.run(cmd, check=True)


def make_black_clip(path: Path, duration: float = 3.0, size: str = "320x240", fps: int = 25) -> None:
    """Solid black clip -- must hard-gate-fail blackdetect."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c=black:s={size}:d={duration}:r={fps}",
        "-pix_fmt", "yuv420p", str(path),
    ])


def make_frozen_clip(
    path: Path, duration: float = 3.0, size: str = "320x240", fps: int = 25, color: str = "green"
) -> None:
    """Solid, non-black color clip -- static/unchanging frames trigger
    freezedetect without also triggering blackdetect."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c={color}:s={size}:d={duration}:r={fps}",
        "-pix_fmt", "yuv420p", str(path),
    ])


def make_testsrc_clip(path: Path, duration: float = 3.0, size: str = "320x240", fps: int = 25) -> None:
    """High-detail moving test pattern -> high Laplacian-variance sharpness."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"testsrc=size={size}:rate={fps}:duration={duration}",
        "-pix_fmt", "yuv420p", str(path),
    ])


def make_flat_clip(
    path: Path, duration: float = 3.0, size: str = "320x240", fps: int = 25, color: str = "gray"
) -> None:
    """Flat, textureless clip -> low Laplacian-variance sharpness, and (with
    a mid-tone color) zero histogram clipping -- used as both the "blurred"
    sharpness baseline and the "well exposed" exposure baseline."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c={color}:s={size}:d={duration}:r={fps}",
        "-pix_fmt", "yuv420p", str(path),
    ])


def make_overexposed_clip(path: Path, duration: float = 3.0, size: str = "320x240", fps: int = 25) -> None:
    """Solid white clip -- maximal histogram highlight clipping."""
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c=white:s={size}:d={duration}:r={fps}",
        "-pix_fmt", "yuv420p", str(path),
    ])


def make_multiscene_clip(
    path: Path, tmp_path: Path, size: str = "320x240", fps: int = 25, seg_duration: float = 3.0
) -> List[float]:
    """Three visually distinct flat-color segments concatenated (via the
    concat demuxer, stream copy -- exact cut points, no re-encode blur across
    the boundary) -> two clear scene cuts. Returns the expected cut times."""
    colors = ["red", "blue", "yellow"]
    segment_paths = []
    for i, c in enumerate(colors):
        seg_path = tmp_path / f"_scene_seg_{i}.mp4"
        _run_ffmpeg([
            "-f", "lavfi", "-i", f"color=c={c}:s={size}:d={seg_duration}:r={fps}",
            "-pix_fmt", "yuv420p", str(seg_path),
        ])
        segment_paths.append(seg_path)

    concat_list = tmp_path / "_concat_list.txt"
    with open(concat_list, "w") as f:
        for sp in segment_paths:
            f.write(f"file '{sp}'\n")

    _run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(path),
    ])
    return [seg_duration, seg_duration * 2]


def make_motion_clip(
    path: Path,
    motion: str = "smooth",
    duration: float = 3.0,
    size=(320, 240),
    fps: int = 25,
) -> None:
    """Generate a clip with a grid of high-contrast squares that shift either
    with constant velocity ("smooth" pan) or with large random jumps every
    frame ("jittery" motion), via cv2.VideoWriter. This gives goodFeaturesToTrack
    strong, reliable corners to lock onto and gives full control over the
    frame-to-frame motion signal, which ffmpeg lavfi sources cannot provide."""
    w, h = size
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open VideoWriter for {path}")

    n_frames = int(duration * fps)
    rng = np.random.default_rng(42)
    offset = 0.0

    try:
        for _ in range(n_frames):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            if motion == "smooth":
                offset += 2.0
            else:
                offset += rng.uniform(-18, 18)

            for gx in range(-40, w + 40, 40):
                for gy in range(0, h + 40, 40):
                    x = int((gx + offset) % (w + 80)) - 40
                    y = gy
                    cv2.rectangle(frame, (x, y), (x + 24, y + 24), (255, 255, 255), -1)
            writer.write(frame)
    finally:
        writer.release()


@pytest.fixture
def clip_factory(tmp_path):
    """Returns a dict of helper functions bound to this test's tmp_path, so
    test bodies can call e.g. ``clip_factory['black'](path)`` uniformly."""
    return {
        "black": make_black_clip,
        "frozen": make_frozen_clip,
        "testsrc": make_testsrc_clip,
        "flat": make_flat_clip,
        "overexposed": make_overexposed_clip,
        "multiscene": make_multiscene_clip,
        "motion": make_motion_clip,
    }
