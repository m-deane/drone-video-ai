"""Weighted composite score from per-signal scores using weights.py's
configuration.

Composition's weight is always 0.0 in Milestone 1 (see weights.py), so its
``None`` score never needs to enter the weighted sum -- this module still
defensively skips any signal whose weight is exactly 0.0 regardless of the
score value, so a future nonzero composition weight (Milestone 2) is the
only change needed to include it, not a change to this function.
"""

from __future__ import annotations

from typing import Optional

from drone_video_ai.common.manifest import ScoringWeights


def compute_composite_score(
    sharpness: float,
    exposure: float,
    motion_smoothness: float,
    composition: Optional[float],
    weights: ScoringWeights,
) -> float:
    """Weighted sum of per-signal scores, normalized by the sum of weights
    actually applied (so composite_score stays in [0, 1] even if weights
    don't sum to exactly 1.0)."""
    signal_scores = {
        "sharpness": sharpness,
        "exposure": exposure,
        "motion_smoothness": motion_smoothness,
        "composition": composition,
    }
    signal_weights = {
        "sharpness": weights.sharpness,
        "exposure": weights.exposure,
        "motion_smoothness": weights.motion_smoothness,
        "composition": weights.composition,
    }

    weighted_sum = 0.0
    total_weight = 0.0
    for signal, score in signal_scores.items():
        w = signal_weights[signal]
        if w == 0.0 or score is None:
            continue
        weighted_sum += w * score
        total_weight += w

    if total_weight == 0.0:
        return 0.0
    return weighted_sum / total_weight
