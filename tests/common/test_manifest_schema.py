"""Schema/manifest round-trip tests for common/manifest.py + common/schema.py."""

from __future__ import annotations

import pytest

from drone_video_ai.common.manifest import (
    CandidateBoundaries,
    ExcludedSegment,
    HighlightManifest,
    ManifestSummary,
    ScoringWeights,
    Segment,
    SegmentScores,
    SourceFile,
)
from drone_video_ai.common.schema import ManifestValidationError, validate_highlight_manifest


def _build_sample_manifest() -> HighlightManifest:
    source_file = SourceFile(
        path="/tmp/example.mp4", name="example.mp4", duration=10.0,
        width=1920, height=1080, fps=30.0, codec="h264", pix_fmt="yuv420p",
    )
    weights = ScoringWeights(
        weights_version="default-v1", sharpness=1 / 3, exposure=1 / 3, motion_smoothness=1 / 3,
        composition=0.0,
    )
    boundaries = CandidateBoundaries(
        scene_boundaries=[5.0], motion_minima_boundaries=[3.0], union_boundaries=[0.0, 3.0, 5.0, 10.0]
    )
    segment = Segment(
        segment_id="seg_0001", start_time=0.0, end_time=5.0, duration=5.0,
        scores=SegmentScores(sharpness=0.8, exposure=0.9, motion_smoothness=0.7, composition=None),
        composite_score=0.8, gate_status="passed",
    )
    excluded = ExcludedSegment(
        segment_id="seg_0002", start_time=5.0, end_time=10.0, duration=5.0,
        scores=SegmentScores(sharpness=0.1, exposure=0.1, motion_smoothness=0.1, composition=None),
        gate_failures=["blackdetect"], gate_status="failed",
    )
    summary = ManifestSummary(
        total_segments=1, total_duration=5.0, avg_composite_score=0.8,
        scenes_detected=1, motion_minima_detected=1, segments_excluded=1,
    )
    return HighlightManifest(
        source_file=source_file, scoring_weights=weights, candidate_boundaries=boundaries,
        segments=[segment], excluded_segments=[excluded], summary=summary,
    )


def test_manifest_version_is_3():
    # Bumped from 2 to 3 in Milestone 2: composition scoring changes the
    # composite-score computation for consumers (see common/manifest.py
    # module docstring / plan.md's "Milestone 2 (composition scoring)
    # changes to this schema" note).
    manifest = _build_sample_manifest()
    assert manifest.version == 3


def test_manifest_to_json_from_json_round_trip():
    manifest = _build_sample_manifest()
    json_str = manifest.to_json()
    restored = HighlightManifest.from_json(json_str)

    assert restored.version == manifest.version
    assert restored.source_file.path == manifest.source_file.path
    assert restored.segments[0].segment_id == "seg_0001"
    assert restored.excluded_segments[0].gate_failures == ["blackdetect"]


def test_manifest_no_post_processing_field():
    manifest = _build_sample_manifest()
    doc = manifest.to_dict()
    assert "post_processing" not in doc
    import json
    assert "post_processing" not in json.dumps(doc)


def test_valid_manifest_passes_schema_validation():
    manifest = _build_sample_manifest()
    validate_highlight_manifest(manifest.to_dict())  # should not raise


def test_manifest_with_forbidden_post_processing_key_fails_validation():
    manifest = _build_sample_manifest()
    doc = manifest.to_dict()
    doc["post_processing"] = {"color": "drone_aerial"}
    with pytest.raises(ManifestValidationError):
        validate_highlight_manifest(doc)


def test_manifest_missing_required_key_fails_validation():
    manifest = _build_sample_manifest()
    doc = manifest.to_dict()
    del doc["summary"]
    with pytest.raises(ManifestValidationError):
        validate_highlight_manifest(doc)


def test_manifest_segment_with_wrong_gate_status_fails_validation():
    manifest = _build_sample_manifest()
    doc = manifest.to_dict()
    doc["segments"][0]["gate_status"] = "failed"
    with pytest.raises(ManifestValidationError):
        validate_highlight_manifest(doc)


def test_manifest_excluded_segment_requires_nonempty_gate_failures():
    manifest = _build_sample_manifest()
    doc = manifest.to_dict()
    doc["excluded_segments"][0]["gate_failures"] = []
    with pytest.raises(ManifestValidationError):
        validate_highlight_manifest(doc)
