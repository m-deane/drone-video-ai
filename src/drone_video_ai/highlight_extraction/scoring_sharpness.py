"""Sharpness scoring via OpenCV Laplacian variance.

Per spec/plan: ``cv2.Laplacian(...).var()`` over sampled frames within a
segment, in-video min-max normalized to ``[0, 1]`` (normalization across
segments happens in ``pipeline.py``; this module produces the raw,
un-normalized per-segment statistic).
"""

from __future__ import annotations

from typing import List, Optional

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
    video_path: str, start_time: float, end_time: float, max_samples: int = 10,
    active_rect: Optional["ActiveRect"] = None,
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
            if active_rect is not None:
                gray = active_rect.crop(gray)
            variances.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))

        if not variances:
            return 0.0
        return float(np.mean(variances))
    finally:
        cap.release()


def min_max_normalize(raw_values: List[float]) -> List[Optional[float]]:
    """Rank ``raw_values`` within this video onto [0,1], or return ``None`` per
    element where that rank is not defined.

    This is a WITHIN-FILE RANK, not an absolute quality measure. It answers
    "which of this video's segments is sharpest", not "is this segment sharp",
    and values are therefore NOT comparable across files.

    Returns ``None`` for every element when the rank carries no information:

    - ``n < 2`` -- there is nothing to rank against. Previously this returned
      ``[1.0]`` for ANY single value: ``[0.02] -> [1.0]`` and ``[123.4] -> [1.0]``
      were indistinguishable. Since data/reference_pack/ measured that every
      file in this project's corpus is a single continuous shot, that degenerate
      case was the NORM here, not an edge case -- 20 of 20 sharpness and
      motion_smoothness values across the 8-file corpus were saturated at 0.0 or
      1.0.
    - ``max == min`` -- every segment is equally sharp, so the rank is arbitrary.
      Previously returned 1.0 for all, asserting they were all maximal.

    Callers must carry the raw absolute value alongside this, so that a ``None``
    here costs no information.
    """
    if len(raw_values) < 2:
        return [None] * len(raw_values)
    lo, hi = min(raw_values), max(raw_values)
    if hi - lo <= 0.0:
        return [None] * len(raw_values)
    return [(v - lo) / (hi - lo) for v in raw_values]
