"""Schema tests for Capability 3 (Reference Pack) -- spec AC3.1.

Covers required fields + correct types via a couple of synthetic in-memory
records plus the one manually-curated worked example committed under
``data/reference_pack/exemplars/`` (spec AC3.4).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from drone_video_ai.reference_pack.schema import (
    EXEMPLAR_RECORD_SCHEMA,
    ExemplarRecord,
    ExemplarScores,
    ExemplarValidationError,
    LICENSE_CATEGORIES,
    PLATFORMS,
    validate_exemplar_record,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXEMPLARS_DIR = REPO_ROOT / "data" / "reference_pack" / "exemplars"
WORKED_EXAMPLE_PATH = EXEMPLARS_DIR / "skypixel11_africa_unseen_ellisvanjason.json"


def _build_synthetic_record(
    license_category: str = "cc-by",
    local_media_path=None,
    scores_provenance: str = "computed",
) -> ExemplarRecord:
    return ExemplarRecord(
        source_url="https://vimeo.com/000000000",
        platform="vimeo",
        license_category=license_category,
        title="Synthetic Test Exemplar",
        creator="Test Creator",
        retrieval_date="2026-01-01",
        duration=42.5,
        scores=ExemplarScores(
            sharpness=0.7, exposure=0.6, motion_smoothness=0.9, composite_score=0.73, composition=None
        ),
        award_or_showcase_provenance="Synthetic Test Awards 2026 Winner",
        local_media_path=local_media_path,
        scores_provenance=scores_provenance,
    )


# --- Synthetic in-memory record: valid, permissively-licensed, locally stored ---

def test_synthetic_permissive_record_with_local_media_is_valid():
    record = _build_synthetic_record(license_category="cc0", local_media_path="media/synthetic.mp4")
    doc = record.to_dict()
    validate_exemplar_record(doc)  # should not raise


def test_synthetic_record_round_trips_through_json():
    record = _build_synthetic_record()
    restored = ExemplarRecord.from_json(record.to_json())
    assert restored.source_url == record.source_url
    assert restored.scores.composite_score == record.scores.composite_score
    assert restored.scores.composition is None


# --- Synthetic in-memory record: invalid, all-rights-reserved + local media ---

def test_synthetic_all_rights_reserved_record_with_local_media_fails_validation():
    record = _build_synthetic_record(license_category="all-rights-reserved", local_media_path="media/leaked.mp4")
    doc = record.to_dict()
    with pytest.raises(ExemplarValidationError):
        validate_exemplar_record(doc)


def test_synthetic_record_missing_required_field_fails_validation():
    record = _build_synthetic_record()
    doc = record.to_dict()
    del doc["retrieval_date"]
    with pytest.raises(ExemplarValidationError):
        validate_exemplar_record(doc)


def test_synthetic_record_bad_license_category_fails_validation():
    record = _build_synthetic_record()
    doc = record.to_dict()
    doc["license_category"] = "not-a-real-license"
    with pytest.raises(ExemplarValidationError):
        validate_exemplar_record(doc)


def test_synthetic_record_bad_platform_fails_validation():
    record = _build_synthetic_record()
    doc = record.to_dict()
    doc["platform"] = "tiktok"
    with pytest.raises(ExemplarValidationError):
        validate_exemplar_record(doc)


def test_synthetic_record_wrong_duration_type_fails_validation():
    record = _build_synthetic_record()
    doc = record.to_dict()
    doc["duration"] = "forty-two"
    with pytest.raises(ExemplarValidationError):
        validate_exemplar_record(doc)


def test_schema_enums_match_spec_ac71():
    # spec AC 71: platform (YouTube/Vimeo/other); license_category
    # (all-rights-reserved / CC BY / CC BY-NC / CC BY-SA / CC BY-ND / CC0 /
    # public-domain / owned).
    assert PLATFORMS == {"youtube", "vimeo", "other"}
    assert LICENSE_CATEGORIES == {
        "all-rights-reserved", "cc-by", "cc-by-nc", "cc-by-sa", "cc-by-nd",
        "cc0", "public-domain", "owned",
    }


def test_schema_dict_declares_all_ac71_required_fields():
    required = set(EXEMPLAR_RECORD_SCHEMA["required"])
    for field_name in (
        "source_url", "platform", "license_category", "title", "creator",
        "duration", "retrieval_date", "scores", "award_or_showcase_provenance",
    ):
        assert field_name in required, f"{field_name} missing from EXEMPLAR_RECORD_SCHEMA['required']"


# --- The one real, manually-curated worked example (spec AC3.4) ---

def test_worked_example_file_exists():
    assert WORKED_EXAMPLE_PATH.exists(), (
        f"expected the manually-curated worked example at {WORKED_EXAMPLE_PATH}"
    )


def test_worked_example_validates_against_schema():
    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())
    validate_exemplar_record(doc)  # should not raise


def test_worked_example_has_all_ac71_fields_and_correct_types():
    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())

    assert isinstance(doc["source_url"], str) and doc["source_url"].startswith("https://")
    assert doc["platform"] in PLATFORMS
    assert doc["license_category"] in LICENSE_CATEGORIES
    assert isinstance(doc["title"], str) and doc["title"]
    assert isinstance(doc["creator"], str) and doc["creator"]
    assert doc["duration"] is None or isinstance(doc["duration"], (int, float))
    assert isinstance(doc["retrieval_date"], str)
    assert set(["sharpness", "exposure", "motion_smoothness", "composition", "composite_score"]) <= set(
        doc["scores"].keys()
    )
    # award_or_showcase_provenance is nullable, but this worked example
    # specifically documents real award provenance (spec AC 71/74).
    assert isinstance(doc["award_or_showcase_provenance"], str) and doc["award_or_showcase_provenance"]


def test_worked_example_is_not_a_real_youtube_shortlink_or_placeholder():
    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())
    # Guards against accidentally shipping an invented/placeholder URL.
    assert "example.com" not in doc["source_url"]
    assert doc["source_url"] != ""
    assert "watch?v=" in doc["source_url"] or "vimeo.com/" in doc["source_url"]


def test_worked_example_scores_are_honestly_labeled_not_computed():
    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())
    # No source media file was downloaded for this worked example (per spec
    # Scope-out), so its per-signal scores must be labeled as estimates, not
    # presented as if they were measured by Capability 1's scoring functions.
    assert doc.get("scores_provenance") == "manually_estimated"
    assert doc["scores"]["composition"] is None


def test_worked_example_composite_score_matches_capability1_composite_function():
    """Reuses Capability 1's actual composite-scoring module (per this task's
    instruction to reuse the quality-scoring module) to confirm the worked
    example's composite_score is a genuine, reproducible computation over its
    manually-estimated per-signal inputs -- not an independently fabricated
    number."""
    from drone_video_ai.highlight_extraction.composite import compute_composite_score
    from drone_video_ai.highlight_extraction.weights import default_weights

    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())
    scores = doc["scores"]
    expected = compute_composite_score(
        sharpness=scores["sharpness"],
        exposure=scores["exposure"],
        motion_smoothness=scores["motion_smoothness"],
        composition=scores["composition"],
        weights=default_weights(),
    )
    assert scores["composite_score"] == pytest.approx(expected, abs=1e-3)


def test_worked_example_local_media_path_is_null_for_all_rights_reserved():
    doc = json.loads(WORKED_EXAMPLE_PATH.read_text())
    assert doc["license_category"] == "all-rights-reserved"
    assert doc["local_media_path"] is None
