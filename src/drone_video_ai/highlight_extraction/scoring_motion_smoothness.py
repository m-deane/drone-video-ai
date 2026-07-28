"""Motion-smoothness scoring from the jerk/acceleration of the optical-flow
motion series computed in ``motion.py``.

Per plan.md: "in-video min-max over inverse jerk magnitude -> [0,1]". This
module produces the raw (un-inverted, un-normalized) per-segment jerk
statistic; ``pipeline.py`` inverts and min-max normalizes across all
segments of one video, mirroring ``scoring_sharpness.min_max_normalize``.
"""

from __future__ import annotations

from typing import List, Optional

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


def invert_and_normalize(raw_jerk_values: List[float]) -> List[Optional[float]]:
    """Invert (lower jerk -> higher score) then rank within this video onto
    [0,1], or return ``None`` per element where that rank is not defined.

    Mirrors ``scoring_sharpness.min_max_normalize``'s contract exactly -- see
    its docstring for why the degenerate cases return ``None`` rather than a
    fabricated 1.0. Both are WITHIN-FILE RANKS and are not comparable across
    files; callers must carry ``raw_jerk`` alongside.
    """
    if not raw_jerk_values:
        return []
    if len(raw_jerk_values) < 2:
        return [None] * len(raw_jerk_values)
    inverted = [-v for v in raw_jerk_values]
    lo = min(inverted)
    hi = max(inverted)
    if hi - lo < 1e-9:
        return [None] * len(inverted)
    return [(v - lo) / (hi - lo) for v in inverted]
