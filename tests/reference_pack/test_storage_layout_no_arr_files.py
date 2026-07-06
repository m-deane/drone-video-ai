"""Storage-layout tests for Capability 3 (Reference Pack) -- spec AC3.2.

Covers:
- the true-positive path: the validator passes against this repo's actual
  ``data/reference_pack/`` contents as they exist right now;
- the true-negative path: a synthetic fixture (an in-memory
  all-rights-reserved record paired with a deliberately placed stray file
  under a synthetic ``media/`` dir) that the validator must correctly flag.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from drone_video_ai.reference_pack.schema import check_local_media_storage_rule
from drone_video_ai.reference_pack.storage import (
    StorageLayoutError,
    find_storage_layout_violations,
    validate_storage_layout,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_EXEMPLARS_DIR = REPO_ROOT / "data" / "reference_pack" / "exemplars"
REAL_MEDIA_DIR = REPO_ROOT / "data" / "reference_pack" / "media"


# --- True positive: real repo contents are clean ---

def test_real_reference_pack_contents_pass_storage_layout_validation():
    validate_storage_layout(REAL_EXEMPLARS_DIR, REAL_MEDIA_DIR)  # should not raise


def test_real_reference_pack_has_no_violations_reported():
    violations = find_storage_layout_violations(REAL_EXEMPLARS_DIR, REAL_MEDIA_DIR)
    assert violations == []


# --- Pure in-memory record check (no filesystem involved) ---

def test_all_rights_reserved_record_with_local_media_path_violates_rule():
    doc = {"license_category": "all-rights-reserved", "local_media_path": "media/should_not_exist.mp4"}
    assert check_local_media_storage_rule(doc) is not None


def test_cc0_record_with_local_media_path_does_not_violate_rule():
    doc = {"license_category": "cc0", "local_media_path": "media/ok.mp4"}
    assert check_local_media_storage_rule(doc) is None


def test_all_rights_reserved_record_with_null_media_path_does_not_violate_rule():
    doc = {"license_category": "all-rights-reserved", "local_media_path": None}
    assert check_local_media_storage_rule(doc) is None


# --- True negative: synthetic fixture that must fail ---

def _write_exemplar(exemplars_dir: Path, exemplar_id: str, license_category: str, local_media_path=None) -> None:
    doc = {
        "version": 1,
        "source_url": "https://www.youtube.com/watch?v=synthetic00000",
        "platform": "youtube",
        "license_category": license_category,
        "title": "Synthetic Fixture Exemplar",
        "creator": "Fixture Creator",
        "duration": 30.0,
        "retrieval_date": "2026-01-01",
        "scores": {
            "sharpness": 0.5, "exposure": 0.5, "motion_smoothness": 0.5,
            "composition": None, "composite_score": 0.5,
        },
        "award_or_showcase_provenance": None,
        "local_media_path": local_media_path,
    }
    (exemplars_dir / f"{exemplar_id}.json").write_text(json.dumps(doc))


def test_stray_media_file_for_all_rights_reserved_exemplar_fails_validation(tmp_path):
    exemplars_dir = tmp_path / "exemplars"
    media_dir = tmp_path / "media"
    exemplars_dir.mkdir()
    media_dir.mkdir()

    # A clean, permissively-licensed exemplar that legitimately owns local media.
    _write_exemplar(exemplars_dir, "cc0_clean_example", "cc0", local_media_path="media/cc0_clean_example.mp4")
    (media_dir / "cc0_clean_example.mp4").write_bytes(b"fake-mp4-bytes")

    # The violating fixture: an all-rights-reserved record whose
    # local_media_path is (correctly) null, but a stray file matching its id
    # has been deliberately placed under media/ anyway.
    _write_exemplar(exemplars_dir, "arr_bad_example", "all-rights-reserved", local_media_path=None)
    (media_dir / "arr_bad_example.mp4").write_bytes(b"should-not-be-here")

    violations = find_storage_layout_violations(exemplars_dir, media_dir)
    assert any("arr_bad_example" in v for v in violations)
    assert not any("cc0_clean_example" in v for v in violations)

    with pytest.raises(StorageLayoutError) as excinfo:
        validate_storage_layout(exemplars_dir, media_dir)
    assert any("arr_bad_example" in v for v in excinfo.value.violations)


def test_all_rights_reserved_record_with_non_null_local_media_path_fails_even_without_stray_file(tmp_path):
    exemplars_dir = tmp_path / "exemplars"
    media_dir = tmp_path / "media"
    exemplars_dir.mkdir()
    media_dir.mkdir()

    _write_exemplar(exemplars_dir, "arr_field_violation", "all-rights-reserved", local_media_path="media/ghost.mp4")

    with pytest.raises(StorageLayoutError):
        validate_storage_layout(exemplars_dir, media_dir)


def test_gitkeep_placeholder_in_media_dir_is_ignored_not_a_violation(tmp_path):
    exemplars_dir = tmp_path / "exemplars"
    media_dir = tmp_path / "media"
    exemplars_dir.mkdir()
    media_dir.mkdir()

    _write_exemplar(exemplars_dir, "arr_no_media", "all-rights-reserved", local_media_path=None)
    (media_dir / ".gitkeep").write_text("")

    validate_storage_layout(exemplars_dir, media_dir)  # should not raise
