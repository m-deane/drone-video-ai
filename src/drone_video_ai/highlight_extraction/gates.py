"""Hard-gate exclusion checks: ffmpeg ``blackdetect``/``freezedetect`` plus
configurable minimum sharpness/exposure floors.

Segments failing any gate here are excluded from the manifest's ``segments``
array entirely and routed to ``excluded_segments`` with a non-empty
``gate_failures`` list -- distinguishable from segments that merely score
low but pass every gate (spec AC1.2).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List

# Conservative, documented default thresholds for blackdetect/freezedetect.
# Not buried magic numbers -- named constants configurable via GateConfig.
DEFAULT_BLACK_MIN_DURATION = 0.5  # seconds; blackdetect d= parameter
DEFAULT_BLACK_PIX_TH = 0.10       # blackdetect pix_th= parameter
DEFAULT_FREEZE_NOISE_TOLERANCE = 0.001  # freezedetect n= parameter
DEFAULT_FREEZE_MIN_DURATION = 0.5       # freezedetect d= parameter

DEFAULT_MIN_SHARPNESS_FLOOR = 0.0   # normalized [0,1]; 0.0 == "no floor" by default
DEFAULT_MIN_EXPOSURE_FLOOR = 0.0    # normalized [0,1]; 0.0 == "no floor" by default


@dataclass
class GateConfig:
    black_min_duration: float = DEFAULT_BLACK_MIN_DURATION
    black_pix_threshold: float = DEFAULT_BLACK_PIX_TH
    freeze_noise_tolerance: float = DEFAULT_FREEZE_NOISE_TOLERANCE
    freeze_min_duration: float = DEFAULT_FREEZE_MIN_DURATION
    min_sharpness_floor: float = DEFAULT_MIN_SHARPNESS_FLOOR
    min_exposure_floor: float = DEFAULT_MIN_EXPOSURE_FLOOR


def _run_ffmpeg_filter_stderr(
    video_path: str,
    start_time: float,
    duration: float,
    filter_str: str,
    ffmpeg_bin: str = "ffmpeg",
) -> str:
    """Run ffmpeg with a single video filter over ``[start_time, start_time +
    duration)`` of ``video_path``, discarding output, and return stderr text
    (where blackdetect/freezedetect log their findings)."""
    cmd = [
        ffmpeg_bin,
        "-v", "info",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", video_path,
        "-vf", filter_str,
        "-an",
        "-f", "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.stderr


def detect_black_frames(
    video_path: str,
    start_time: float,
    end_time: float,
    min_duration: float = DEFAULT_BLACK_MIN_DURATION,
    pix_threshold: float = DEFAULT_BLACK_PIX_TH,
    ffmpeg_bin: str = "ffmpeg",
) -> bool:
    """Return True if ffmpeg's ``blackdetect`` reports any black interval
    within the segment."""
    duration = end_time - start_time
    filt = f"blackdetect=d={min_duration}:pix_th={pix_threshold}"
    stderr = _run_ffmpeg_filter_stderr(video_path, start_time, duration, filt, ffmpeg_bin)
    return "black_start" in stderr


def detect_frozen_frames(
    video_path: str,
    start_time: float,
    end_time: float,
    min_duration: float = DEFAULT_FREEZE_MIN_DURATION,
    noise_tolerance: float = DEFAULT_FREEZE_NOISE_TOLERANCE,
    ffmpeg_bin: str = "ffmpeg",
) -> bool:
    """Return True if ffmpeg's ``freezedetect`` reports any frozen interval
    within the segment."""
    duration = end_time - start_time
    filt = f"freezedetect=n={noise_tolerance}:d={min_duration}"
    stderr = _run_ffmpeg_filter_stderr(video_path, start_time, duration, filt, ffmpeg_bin)
    return "freeze_start" in stderr or "lavfi.freezedetect.freeze_start" in stderr


def evaluate_gates(
    video_path: str,
    start_time: float,
    end_time: float,
    sharpness_score: float,
    exposure_score: float,
    config: GateConfig = None,
    ffmpeg_bin: str = "ffmpeg",
) -> List[str]:
    """Run all hard-gate checks for one segment; return a list of failure
    reason strings (empty list == segment passes every gate). Reason strings
    match the manifest schema's documented enum: "blackdetect" |
    "freezedetect" | "min_sharpness_floor" | "min_exposure_floor"."""
    cfg = config or GateConfig()
    failures: List[str] = []

    if detect_black_frames(
        video_path, start_time, end_time,
        min_duration=cfg.black_min_duration, pix_threshold=cfg.black_pix_threshold,
        ffmpeg_bin=ffmpeg_bin,
    ):
        failures.append("blackdetect")

    if detect_frozen_frames(
        video_path, start_time, end_time,
        min_duration=cfg.freeze_min_duration, noise_tolerance=cfg.freeze_noise_tolerance,
        ffmpeg_bin=ffmpeg_bin,
    ):
        failures.append("freezedetect")

    if sharpness_score < cfg.min_sharpness_floor:
        failures.append("min_sharpness_floor")

    if exposure_score < cfg.min_exposure_floor:
        failures.append("min_exposure_floor")

    return failures
