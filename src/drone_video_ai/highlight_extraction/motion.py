"""Per-frame camera-motion transform time series via pure-OpenCV optical
flow (``goodFeaturesToTrack`` + ``calcOpticalFlowPyrLK``), plus a
derivative/local-minima boundary detector over that series.

This deliberately avoids ffmpeg ``vid.stab``/``vidstabdetect`` (GPL-licensed)
per plan.md's resolution of spec Open Question 5 -- the whole point of this
module is to be the permissively-licensed replacement for that GPL path,
tracking the MIT-licensed ``vidstab``/``python_video_stab`` package's
technique (sparse feature tracking -> per-frame motion magnitude) without
depending on it.

The resulting per-frame magnitude series is reused by
``scoring_motion_smoothness.py`` for jerk/acceleration-based smoothness
scoring, and by this module's own ``find_local_minima_boundaries`` for
``motion_minima_boundaries`` (the other half of Capability 1's candidate
boundary set, alongside PySceneDetect's scene boundaries).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np

# Sparse-feature-tracking parameters (goodFeaturesToTrack / calcOpticalFlowPyrLK).
# Documented, not buried magic numbers -- tuned for general handheld/aerial
# footage; not footage-specific to this repo's sample clips.
FEATURE_PARAMS = dict(maxCorners=200, qualityLevel=0.01, minDistance=8, blockSize=7)
LK_PARAMS = dict(
    winSize=(21, 21),
    maxLevel=3,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
)

MIN_TRACKED_POINTS = 4  # re-seed goodFeaturesToTrack once tracked points drop below this


@dataclass
class MotionSample:
    """One frame's motion-magnitude sample."""

    time: float          # seconds from video start
    frame_index: int
    magnitude: float      # mean optical-flow displacement magnitude vs. previous frame (pixels)


def compute_motion_series(
    video_path: str, max_frames: Optional[int] = None
) -> List[MotionSample]:
    """Compute a per-frame camera-motion magnitude time series for the whole
    video using sparse optical flow.

    ``magnitude`` for frame *i* is the mean Euclidean displacement of tracked
    feature points between frame *i-1* and frame *i*. The first frame always
    has magnitude 0.0 (no previous frame to compare against).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    samples: List[MotionSample] = []
    prev_gray: Optional[np.ndarray] = None
    prev_pts: Optional[np.ndarray] = None
    frame_idx = 0

    try:
        while True:
            if max_frames is not None and frame_idx >= max_frames:
                break
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            t = frame_idx / fps
            magnitude = 0.0

            if prev_gray is None:
                prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **FEATURE_PARAMS)
            else:
                if prev_pts is None or len(prev_pts) < MIN_TRACKED_POINTS:
                    prev_pts = cv2.goodFeaturesToTrack(prev_gray, mask=None, **FEATURE_PARAMS)

                if prev_pts is not None and len(prev_pts) > 0:
                    next_pts, status, _err = cv2.calcOpticalFlowPyrLK(
                        prev_gray, gray, prev_pts, None, **LK_PARAMS
                    )
                    status = status.reshape(-1)
                    good_new = next_pts[status == 1]
                    good_old = prev_pts[status == 1]
                    if len(good_new) > 0:
                        displacements = np.linalg.norm(good_new - good_old, axis=1)
                        magnitude = float(np.mean(displacements))
                        prev_pts = good_new.reshape(-1, 1, 2)
                    else:
                        prev_pts = None

            samples.append(MotionSample(time=t, frame_index=frame_idx, magnitude=magnitude))
            prev_gray = gray
            frame_idx += 1
    finally:
        cap.release()

    return samples


def find_local_minima_boundaries(
    samples: List[MotionSample],
    smoothing_window: int = 5,
    min_gap_seconds: float = 1.0,
) -> List[float]:
    """Find local minima of the (smoothed) motion-magnitude series --
    candidate cut points at "the point between two maneuvers" (spec line 20),
    e.g. the still moment between the end of one orbit and the start of the
    next reveal.

    Returns sorted timestamps (seconds), each separated by at least
    ``min_gap_seconds`` to avoid a cluster of near-duplicate boundaries from
    a single quiet moment.
    """
    if len(samples) < 3:
        return []

    magnitudes = np.array([s.magnitude for s in samples], dtype=float)
    times = np.array([s.time for s in samples], dtype=float)

    if smoothing_window > 1:
        kernel = np.ones(smoothing_window) / smoothing_window
        smoothed = np.convolve(magnitudes, kernel, mode="same")
    else:
        smoothed = magnitudes

    boundaries: List[float] = []
    last_boundary_time = -min_gap_seconds
    for i in range(1, len(smoothed) - 1):
        is_minimum = smoothed[i] <= smoothed[i - 1] and smoothed[i] <= smoothed[i + 1]
        is_strict_somewhere = smoothed[i] < smoothed[i - 1] or smoothed[i] < smoothed[i + 1]
        if is_minimum and is_strict_somewhere:
            t = float(times[i])
            if t - last_boundary_time >= min_gap_seconds:
                boundaries.append(t)
                last_boundary_time = t

    return boundaries


def compute_jerk_series(samples: List[MotionSample]) -> np.ndarray:
    """Second derivative (acceleration-of-acceleration -- "jerk") of the
    motion-magnitude series, used by ``scoring_motion_smoothness.py``.

    Returns an array the same length as ``samples``, with the first two
    entries set to 0.0 (insufficient history to compute a second derivative).
    """
    n = len(samples)
    jerk = np.zeros(n, dtype=float)
    if n < 3:
        return jerk
    magnitudes = np.array([s.magnitude for s in samples], dtype=float)
    velocity = np.diff(magnitudes)        # acceleration of position -> here "velocity" of motion magnitude
    accel = np.diff(velocity)             # jerk
    jerk[2:] = accel
    return jerk
