"""Motion-smoothness scoring from the jerk/acceleration of the optical-flow
motion series computed in ``motion.py``.

Per plan.md: "in-video min-max over inverse jerk magnitude -> [0,1]". This
module produces the raw (un-inverted, un-normalized) per-segment jerk
statistic; ``pipeline.py`` inverts and min-max normalizes across all
segments of one video, mirroring ``scoring_sharpness.min_max_normalize``.
"""

from __future__ import annotations

from typing import List

import numpy as np

from drone_video_ai.highlight_extraction.motion import MotionSample, compute_jerk_series


def compute_raw_jerk_magnitude(
    samples: List[MotionSample], start_time: float, end_time: float
) -> float:
    """Mean absolute jerk magnitude of the motion series within
    ``[start_time, end_time)``. Higher = less smooth (more erratic
    camera motion)."""
    if not samples:
        return 0.0
    jerk = compute_jerk_series(samples)
    mask = [(s.time >= start_time and s.time < end_time) for s in samples]
    if not any(mask):
        return 0.0
    segment_jerk = jerk[np.array(mask)]
    if segment_jerk.size == 0:
        return 0.0
    return float(np.mean(np.abs(segment_jerk)))


def invert_and_normalize(raw_jerk_values: List[float]) -> List[float]:
    """Invert (lower jerk -> higher score) then min-max normalize to [0, 1].

    If every segment has identical raw jerk (degenerate case), every score
    is 1.0 -- there is no "shakier" segment to compare against.
    """
    if not raw_jerk_values:
        return []
    inverted = [-v for v in raw_jerk_values]
    lo = min(inverted)
    hi = max(inverted)
    if hi - lo < 1e-9:
        return [1.0 for _ in inverted]
    return [(v - lo) / (hi - lo) for v in inverted]
