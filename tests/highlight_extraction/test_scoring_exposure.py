"""AC1.6 -- a correctly-exposed clip must score above an over/under-exposed
(clipped-histogram) clip."""

from __future__ import annotations

from drone_video_ai.highlight_extraction.scoring_exposure import compute_raw_exposure


def test_well_exposed_clip_scores_above_overexposed_clip(tmp_path, clip_factory):
    well_exposed_path = tmp_path / "gray.mp4"
    overexposed_path = tmp_path / "white.mp4"
    clip_factory["flat"](well_exposed_path, duration=2.0, color="gray")
    clip_factory["overexposed"](overexposed_path, duration=2.0)

    well_exposed_score = compute_raw_exposure(str(well_exposed_path), 0.0, 2.0)
    overexposed_score = compute_raw_exposure(str(overexposed_path), 0.0, 2.0)

    assert well_exposed_score > overexposed_score
    assert well_exposed_score == 1.0  # mid-gray: zero clipped pixels
    assert overexposed_score == 0.0  # solid white: fully clipped


def test_exposure_score_is_bounded_zero_one(tmp_path, clip_factory):
    path = tmp_path / "gray.mp4"
    clip_factory["flat"](path, duration=1.0, color="gray")
    score = compute_raw_exposure(str(path), 0.0, 1.0)
    assert 0.0 <= score <= 1.0
