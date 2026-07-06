"""AC1.6 -- a high-Laplacian-variance clip must score above a low-variance
clip."""

from __future__ import annotations

from drone_video_ai.highlight_extraction.scoring_sharpness import (
    compute_raw_sharpness,
    min_max_normalize,
)


def test_high_variance_clip_scores_above_low_variance_clip(tmp_path, clip_factory):
    sharp_path = tmp_path / "sharp.mp4"
    blurred_path = tmp_path / "blurred.mp4"
    clip_factory["testsrc"](sharp_path, duration=2.0)
    clip_factory["flat"](blurred_path, duration=2.0)

    sharp_raw = compute_raw_sharpness(str(sharp_path), 0.0, 2.0)
    blurred_raw = compute_raw_sharpness(str(blurred_path), 0.0, 2.0)

    assert sharp_raw > blurred_raw
    assert blurred_raw == 0.0  # a perfectly flat frame has zero Laplacian variance


def test_min_max_normalize_maps_to_zero_one_range():
    normalized = min_max_normalize([10.0, 50.0, 100.0])
    assert normalized[0] == 0.0
    assert normalized[-1] == 1.0
    assert 0.0 < normalized[1] < 1.0


def test_min_max_normalize_degenerate_equal_values_returns_all_ones():
    normalized = min_max_normalize([5.0, 5.0, 5.0])
    assert normalized == [1.0, 1.0, 1.0]


def test_min_max_normalize_empty_list():
    assert min_max_normalize([]) == []
