"""Sharpness scoring via OpenCV Laplacian variance.

Per spec/plan: ``cv2.Laplacian(...).var()`` over sampled frames within a
segment, in-video min-max normalized to ``[0, 1]`` (normalization across
segments happens in ``pipeline.py``; this module produces the raw,
un-normalized per-segment statistic).
"""

from __future__ import annotations

from typing import List

import cv2
import numpy as np


def _sample_frame_indices(start_frame: int, end_frame: int, max_samples: int) -> List[int]:
    """Evenly sample up to ``max_samples`` frame indices within
    ``[start_frame, end_frame)``. Always includes at least one frame."""
    n_available = max(1, end_frame - start_frame)
    n_samples = min(max_samples, n_available)
    if n_samples <= 1:
        return [start_frame]
    step = n_available / n_samples
    return [start_frame + int(i * step) for i in range(n_samples)]


def compute_raw_sharpness(
    video_path: str, start_time: float, end_time: float, max_samples: int = 10
) -> float:
    """Return the mean Laplacian-variance sharpness statistic over up to
    ``max_samples`` frames evenly sampled within ``[start_time, end_time)``.

    This is a *raw* (un-normalized) value -- higher means sharper. Cross-segment
    min-max normalization into ``[0, 1]`` is applied by the pipeline, per the
    manifest's documented normalization method.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        start_frame = int(round(start_time * fps))
        end_frame = int(round(end_time * fps))
        indices = _sample_frame_indices(start_frame, end_frame, max_samples)

        variances: List[float] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            variances.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))

        if not variances:
            return 0.0
        return float(np.mean(variances))
    finally:
        cap.release()


def min_max_normalize(raw_values: List[float]) -> List[float]:
    """In-video min-max normalization to [0, 1]. If all values are equal
    (degenerate case, e.g. a single-segment video), returns 1.0 for every
    value rather than dividing by zero -- there is no "worse" segment to
    compare against."""
    if not raw_values:
        return []
    lo = min(raw_values)
    hi = max(raw_values)
    if hi - lo < 1e-9:
        return [1.0 for _ in raw_values]
    return [(v - lo) / (hi - lo) for v in raw_values]
