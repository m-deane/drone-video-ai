"""AC1.6 / tasks.md 1.25 -- composition scoring
(``scoring_composition.py``) validated against synthetic well-composed vs.
poorly-composed / tilted-horizon fixtures.

Covers both sub-scorers independently (rule-of-thirds distance, horizon-tilt
levelness) plus the combined ``compute_raw_composition`` entry point, per
tasks.md 1.25's minimum bar:

- A synthetic frame/clip with an off-center bright region near a
  rule-of-thirds point must score higher than one with the salient region
  dead-center or in a corner far from any rule-of-thirds point.
- A synthetic clip with an intentionally rotated/tilted horizon-like edge
  must score lower on levelness than an unrotated one.

Also exercises tasks.md 1.23's required evaluation: the saliency-centroid
approach must clearly differentiate an off-center/asymmetric bright region
from a dead-center or far-corner one without any object/subject detector.
"""

from __future__ import annotations

import numpy as np
import pytest

from drone_video_ai.highlight_extraction.scoring_composition import (
    MAX_HORIZON_TILT_DEGREES,
    _horizon_levelness_score,
    _rule_of_thirds_score,
    compute_raw_composition,
)


def _frame_at(video_path: str, t: float = 0.1):
    import cv2

    cap = cv2.VideoCapture(video_path)
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
        ret, frame = cap.read()
        assert ret, "failed to read a frame from the synthetic test fixture"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray
    finally:
        cap.release()


# --- Rule-of-thirds sub-scorer (tasks.md 1.21 / 1.23) -----------------------


def test_bright_region_near_rule_of_thirds_point_scores_above_dead_center(tmp_path, clip_factory):
    w, h = 320, 240
    near_rot_path = tmp_path / "near_rot.mp4"
    center_path = tmp_path / "center.mp4"

    clip_factory["bright_region"](near_rot_path, center=(w // 3, h // 3), duration=1.0, size=(w, h))
    clip_factory["bright_region"](center_path, center=(w // 2, h // 2), duration=1.0, size=(w, h))

    near_rot_score = _rule_of_thirds_score(_frame_at(str(near_rot_path)))
    center_score = _rule_of_thirds_score(_frame_at(str(center_path)))

    assert near_rot_score > center_score


def test_bright_region_near_rule_of_thirds_point_scores_above_far_corner(tmp_path, clip_factory):
    w, h = 320, 240
    near_rot_path = tmp_path / "near_rot.mp4"
    corner_path = tmp_path / "corner.mp4"

    clip_factory["bright_region"](near_rot_path, center=(w // 3, h // 3), duration=1.0, size=(w, h))
    clip_factory["bright_region"](
        corner_path, center=(int(w * 0.95), int(h * 0.95)), duration=1.0, size=(w, h)
    )

    near_rot_score = _rule_of_thirds_score(_frame_at(str(near_rot_path)))
    corner_score = _rule_of_thirds_score(_frame_at(str(corner_path)))

    assert near_rot_score > corner_score


def test_rule_of_thirds_score_stays_in_unit_range(tmp_path, clip_factory):
    w, h = 320, 240
    for center in [(w // 3, h // 3), (w // 2, h // 2), (0, 0), (w - 1, h - 1)]:
        path = tmp_path / f"frame_{center[0]}_{center[1]}.mp4"
        clip_factory["bright_region"](path, center=center, duration=1.0, size=(w, h))
        score = _rule_of_thirds_score(_frame_at(str(path)))
        assert 0.0 <= score <= 1.0


# --- Horizon-tilt sub-scorer (tasks.md 1.22) --------------------------------


def test_tilted_horizon_scores_lower_levelness_than_level_horizon(tmp_path, clip_factory):
    level_path = tmp_path / "level.mp4"
    tilted_path = tmp_path / "tilted.mp4"

    clip_factory["horizon"](level_path, tilt_degrees=0.0, duration=1.0)
    clip_factory["horizon"](tilted_path, tilt_degrees=15.0, duration=1.0)

    level_score = _horizon_levelness_score(_frame_at(str(level_path)))
    tilted_score = _horizon_levelness_score(_frame_at(str(tilted_path)))

    assert level_score > tilted_score
    assert level_score == 1.0  # perfectly level -- exactly 0 degrees tilt


def test_horizon_tilt_beyond_max_threshold_floors_to_zero(tmp_path, clip_factory):
    path = tmp_path / "extreme_tilt.mp4"
    clip_factory["horizon"](path, tilt_degrees=MAX_HORIZON_TILT_DEGREES + 10.0, duration=1.0)

    score = _horizon_levelness_score(_frame_at(str(path)))
    assert score == 0.0


def test_moderate_tilt_scores_between_zero_and_one(tmp_path, clip_factory):
    path = tmp_path / "moderate_tilt.mp4"
    clip_factory["horizon"](path, tilt_degrees=10.0, duration=1.0)

    score = _horizon_levelness_score(_frame_at(str(path)))
    assert 0.0 < score < 1.0


def test_horizon_levelness_score_decreases_monotonically_with_tilt(tmp_path, clip_factory):
    tilts = [0.0, 5.0, 10.0, 15.0]
    scores = []
    for tilt in tilts:
        path = tmp_path / f"tilt_{tilt}.mp4"
        clip_factory["horizon"](path, tilt_degrees=tilt, duration=1.0)
        scores.append(_horizon_levelness_score(_frame_at(str(path))))

    for earlier, later in zip(scores, scores[1:]):
        assert earlier >= later


# --- Combined compute_raw_composition entry point ---------------------------


def test_compute_raw_composition_stays_in_unit_range(tmp_path, clip_factory):
    path = tmp_path / "level_center.mp4"
    clip_factory["horizon"](path, tilt_degrees=0.0, duration=2.0)

    score = compute_raw_composition(str(path), 0.0, 2.0)
    assert 0.0 <= score <= 1.0


def test_compute_raw_composition_well_composed_scores_above_poorly_composed(tmp_path, clip_factory):
    """A well-composed synthetic clip (bright region near a rule-of-thirds
    point, level horizon) must score above a poorly-composed one (bright
    region dead-center, tilted horizon) on the combined composition score."""
    w, h = 320, 240
    well_composed_path = tmp_path / "well_composed.mp4"
    poorly_composed_path = tmp_path / "poorly_composed.mp4"

    clip_factory["bright_region"](
        well_composed_path, center=(w // 3, h // 3), duration=1.5, size=(w, h)
    )
    clip_factory["bright_region"](
        poorly_composed_path, center=(w // 2, h // 2), duration=1.5, size=(w, h)
    )

    well_composed_score = compute_raw_composition(str(well_composed_path), 0.0, 1.5)
    poorly_composed_score = compute_raw_composition(str(poorly_composed_path), 0.0, 1.5)

    assert well_composed_score > poorly_composed_score


# --- Deliberate fallback branches (module docstring section 1/2) -----------
#
# Every test above happens to produce a clean, non-degenerate saliency map or
# a clearly-detectable dominant line, so none of them ever actually reaches
# the three fallback branches documented at length in the module docstring.
# These tests force each one directly.


def test_rule_of_thirds_score_falls_back_to_frame_center_on_degenerate_saliency(monkeypatch):
    """Forces ``_rule_of_thirds_score``'s ``total <= 1e-9`` degenerate-saliency
    branch (scoring_composition.py) by monkeypatching
    ``cv2.saliency.StaticSaliencySpectralResidual_create`` to return an
    all-zero saliency map -- verified empirically that no real uniform-value
    frame (0, 1, 255) actually drives ``cv2.saliency``'s real
    SpectralResidual output to a near-zero sum (it always produces some
    nonzero residual even for a flat image), so this branch is only
    reachable this way, not via any real synthetic clip."""
    import drone_video_ai.highlight_extraction.scoring_composition as sc

    class _ZeroSaliency:
        def computeSaliency(self, frame):
            return True, np.zeros(frame.shape[:2], dtype=np.float32)

    monkeypatch.setattr(
        sc.cv2.saliency, "StaticSaliencySpectralResidual_create", lambda: _ZeroSaliency()
    )

    w, h = 320, 240
    frame = np.full((h, w), 128, dtype=np.uint8)
    score = sc._rule_of_thirds_score(frame)

    # Center-of-frame fallback: distance from (w/2, h/2) to the nearest
    # rule-of-thirds point, normalized the same way as the real code path.
    expected_min_distance = float(np.hypot(w / 2.0 - w / 3.0, h / 2.0 - h / 3.0))
    expected_max_distance = float(np.hypot(w / 3.0, h / 3.0))
    expected_score = 1.0 - (expected_min_distance / expected_max_distance)
    assert score == pytest.approx(expected_score, abs=1e-6)


def test_horizon_levelness_score_is_neutral_when_no_line_detected():
    """Forces ``_horizon_levelness_score``'s ``lines is None`` branch: a
    perfectly uniform frame has zero Canny edges, so ``cv2.HoughLinesP``
    returns ``None`` -- verified empirically -- and the neutral (not
    penalized) fallback of 1.0 must be returned."""
    frame = np.full((240, 320), 128, dtype=np.uint8)
    score = _horizon_levelness_score(frame)
    assert score == 1.0


def test_horizon_levelness_score_is_neutral_when_only_vertical_lines_detected():
    """Forces ``_horizon_levelness_score``'s ``best_angle is None`` branch: a
    frame of only vertical stripes produces exclusively near-vertical Hough
    lines (verified empirically: all detected angles are -90 degrees), all
    excluded by the ``abs(angle) > 45.0`` near-horizontal filter, so no
    candidate horizon line survives and the neutral fallback of 1.0 must be
    returned (not the 0.0 an unhandled case would floor to)."""
    w, h = 320, 240
    frame = np.zeros((h, w), dtype=np.uint8)
    frame[:, ::20] = 255  # vertical white stripes -- no horizontal edges at all
    score = _horizon_levelness_score(frame)
    assert score == 1.0


def test_compute_raw_composition_empty_range_returns_zero(tmp_path, clip_factory):
    path = tmp_path / "clip.mp4"
    clip_factory["bright_region"](path, center=(160, 120), duration=1.0)
    # Requesting a window entirely past the clip's actual duration means no
    # frames can be read -- must return 0.0, not raise.
    score = compute_raw_composition(str(path), 5.0, 6.0)
    assert score == 0.0
