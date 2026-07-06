"""AC1.6 -- a synthetic smooth-pan clip must score above a synthetic
jittery/shaky-motion clip."""

from __future__ import annotations

from drone_video_ai.highlight_extraction.motion import compute_motion_series
from drone_video_ai.highlight_extraction.scoring_motion_smoothness import (
    compute_raw_jerk_magnitude,
    invert_and_normalize,
)


def test_smooth_pan_has_lower_jerk_than_jittery_motion(tmp_path, clip_factory):
    smooth_path = tmp_path / "smooth.mp4"
    jitter_path = tmp_path / "jitter.mp4"
    clip_factory["motion"](smooth_path, motion="smooth", duration=2.0)
    clip_factory["motion"](jitter_path, motion="jitter", duration=2.0)

    smooth_samples = compute_motion_series(str(smooth_path))
    jitter_samples = compute_motion_series(str(jitter_path))

    smooth_jerk = compute_raw_jerk_magnitude(smooth_samples, 0.0, 2.0)
    jitter_jerk = compute_raw_jerk_magnitude(jitter_samples, 0.0, 2.0)

    assert smooth_jerk < jitter_jerk


def test_smooth_pan_scores_above_jittery_motion_after_normalization(tmp_path, clip_factory):
    smooth_path = tmp_path / "smooth.mp4"
    jitter_path = tmp_path / "jitter.mp4"
    clip_factory["motion"](smooth_path, motion="smooth", duration=2.0)
    clip_factory["motion"](jitter_path, motion="jitter", duration=2.0)

    smooth_samples = compute_motion_series(str(smooth_path))
    jitter_samples = compute_motion_series(str(jitter_path))

    smooth_jerk = compute_raw_jerk_magnitude(smooth_samples, 0.0, 2.0)
    jitter_jerk = compute_raw_jerk_magnitude(jitter_samples, 0.0, 2.0)

    normalized = invert_and_normalize([smooth_jerk, jitter_jerk])
    smooth_score, jitter_score = normalized

    assert smooth_score > jitter_score
    assert smooth_score == 1.0  # smoothest segment normalizes to 1.0
    assert jitter_score == 0.0  # shakiest segment normalizes to 0.0


def test_invert_and_normalize_degenerate_equal_values():
    assert invert_and_normalize([3.0, 3.0]) == [1.0, 1.0]


def test_invert_and_normalize_empty():
    assert invert_and_normalize([]) == []
