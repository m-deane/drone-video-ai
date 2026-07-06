"""AC1.2 -- a black-frame clip and a frozen-frame clip must both hard-gate-fail
with the correct gate_failures entry, and (via the pipeline) land in
excluded_segments, not segments."""

from __future__ import annotations

from drone_video_ai.highlight_extraction.gates import (
    GateConfig,
    detect_black_frames,
    detect_frozen_frames,
    evaluate_gates,
)


def test_black_clip_triggers_blackdetect(tmp_path, clip_factory):
    path = tmp_path / "black.mp4"
    clip_factory["black"](path, duration=2.0)
    assert detect_black_frames(str(path), 0.0, 2.0) is True


def test_frozen_clip_triggers_freezedetect_but_not_blackdetect(tmp_path, clip_factory):
    path = tmp_path / "frozen.mp4"
    clip_factory["frozen"](path, duration=2.0, color="green")
    assert detect_frozen_frames(str(path), 0.0, 2.0) is True
    assert detect_black_frames(str(path), 0.0, 2.0) is False


def test_moving_testsrc_clip_does_not_trigger_either_gate(tmp_path, clip_factory):
    path = tmp_path / "testsrc.mp4"
    clip_factory["testsrc"](path, duration=2.0)
    assert detect_black_frames(str(path), 0.0, 2.0) is False
    assert detect_frozen_frames(str(path), 0.0, 2.0) is False


def test_evaluate_gates_reports_blackdetect_failure(tmp_path, clip_factory):
    path = tmp_path / "black.mp4"
    clip_factory["black"](path, duration=2.0)
    failures = evaluate_gates(
        str(path), 0.0, 2.0, sharpness_score=1.0, exposure_score=1.0, config=GateConfig()
    )
    assert "blackdetect" in failures


def test_evaluate_gates_reports_freezedetect_failure(tmp_path, clip_factory):
    path = tmp_path / "frozen.mp4"
    clip_factory["frozen"](path, duration=2.0, color="green")
    failures = evaluate_gates(
        str(path), 0.0, 2.0, sharpness_score=1.0, exposure_score=1.0, config=GateConfig()
    )
    assert "freezedetect" in failures
    assert "blackdetect" not in failures


def test_evaluate_gates_reports_min_sharpness_and_exposure_floor_failures(tmp_path, clip_factory):
    path = tmp_path / "testsrc.mp4"
    clip_factory["testsrc"](path, duration=2.0)
    config = GateConfig(min_sharpness_floor=2.0, min_exposure_floor=2.0)
    failures = evaluate_gates(
        str(path), 0.0, 2.0, sharpness_score=0.5, exposure_score=0.5, config=config
    )
    assert "min_sharpness_floor" in failures
    assert "min_exposure_floor" in failures


def test_evaluate_gates_passes_clean_segment(tmp_path, clip_factory):
    path = tmp_path / "testsrc.mp4"
    clip_factory["testsrc"](path, duration=2.0)
    failures = evaluate_gates(
        str(path), 0.0, 2.0, sharpness_score=1.0, exposure_score=1.0, config=GateConfig()
    )
    assert failures == []
