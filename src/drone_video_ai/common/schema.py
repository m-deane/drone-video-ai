"""JSON-schema dicts for the highlight manifest and edit manifest, plus
machine-checkable validator functions (not merely docstrings), per
Constitution rule 6 (tool-grounded verification) and spec AC1.1/AC1.5/AC2.1.

The exemplar-record schema (Capability 3) is a separate concern and is out
of scope for this module.

No third-party ``jsonschema`` dependency is introduced (it is not in the
plan's approved Milestone-1 dependency list); this module implements small,
purpose-built structural validators sufficient to check the fields this
project actually emits.
"""

from __future__ import annotations

from typing import Any

# JSON-schema-shaped dict describing the highlight manifest (Draft-07-ish
# subset: type/properties/required/items only -- enough to document the
# shape; validate_highlight_manifest() below implements the actual checks).
HIGHLIGHT_MANIFEST_SCHEMA: dict = {
    "type": "object",
    "required": [
        "version",
        "source_file",
        "scoring_weights",
        "candidate_boundaries",
        "normalization",
        "segments",
        "excluded_segments",
        "summary",
    ],
    "properties": {
        "version": {"type": "integer"},
        "source_file": {
            "type": "object",
            "required": [
                "path", "name", "duration", "width", "height", "fps", "codec", "pix_fmt",
            ],
        },
        "scoring_weights": {
            "type": "object",
            "required": ["weights_version", "weights"],
            "properties": {
                "weights": {
                    "type": "object",
                    "required": ["sharpness", "exposure", "motion_smoothness", "composition"],
                }
            },
        },
        "candidate_boundaries": {
            "type": "object",
            "required": ["scene_boundaries", "motion_minima_boundaries", "union_boundaries"],
        },
        "normalization": {
            "type": "object",
            "required": ["sharpness", "exposure", "motion_smoothness", "composition"],
        },
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "segment_id", "start_time", "end_time", "duration",
                    "scores", "composite_score", "gate_status",
                ],
            },
        },
        "excluded_segments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "segment_id", "start_time", "end_time", "duration",
                    "scores", "gate_status", "gate_failures",
                ],
            },
        },
        "summary": {
            "type": "object",
            "required": [
                "total_segments", "total_duration", "avg_composite_score",
                "scenes_detected", "motion_minima_detected", "segments_excluded",
            ],
        },
    },
}

# Fields from the legacy (v1) manifest schema that must never appear in this
# pipeline's output -- per spec Scope-out line 44 / AC1.5.
FORBIDDEN_POST_PROCESSING_KEYS = {"post_processing", "color", "stabilize", "auto_speed"}


class ManifestValidationError(ValueError):
    """Raised by validate_highlight_manifest on any structural violation."""


def _require_keys(obj: Any, keys: list, context: str) -> None:
    if not isinstance(obj, dict):
        raise ManifestValidationError(f"{context}: expected an object, got {type(obj).__name__}")
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ManifestValidationError(f"{context}: missing required key(s) {missing}")


def _check_no_post_processing(obj: Any, context: str) -> None:
    """Recursively assert no forbidden post_processing-style key appears
    anywhere in the document."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_POST_PROCESSING_KEYS:
                raise ManifestValidationError(
                    f"{context}: forbidden post-processing key '{k}' present -- "
                    "the highlight manifest must never carry pixel-editing fields"
                )
            _check_no_post_processing(v, f"{context}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _check_no_post_processing(item, f"{context}[{i}]")


def validate_highlight_manifest(doc: dict) -> None:
    """Validate ``doc`` against the highlight-manifest schema.

    Raises :class:`ManifestValidationError` on any violation. Returns
    ``None`` (no exception) when the document is structurally valid.
    """
    _check_no_post_processing(doc, "manifest")

    _require_keys(doc, HIGHLIGHT_MANIFEST_SCHEMA["required"], "manifest")

    if not isinstance(doc["version"], int):
        raise ManifestValidationError("manifest.version must be an integer")

    _require_keys(
        doc["source_file"],
        HIGHLIGHT_MANIFEST_SCHEMA["properties"]["source_file"]["required"],
        "manifest.source_file",
    )

    sw = doc["scoring_weights"]
    _require_keys(sw, ["weights_version", "weights"], "manifest.scoring_weights")
    _require_keys(
        sw["weights"],
        ["sharpness", "exposure", "motion_smoothness", "composition"],
        "manifest.scoring_weights.weights",
    )

    _require_keys(
        doc["candidate_boundaries"],
        ["scene_boundaries", "motion_minima_boundaries", "union_boundaries"],
        "manifest.candidate_boundaries",
    )

    _require_keys(
        doc["normalization"],
        ["sharpness", "exposure", "motion_smoothness", "composition"],
        "manifest.normalization",
    )

    if not isinstance(doc["segments"], list):
        raise ManifestValidationError("manifest.segments must be an array")
    for i, seg in enumerate(doc["segments"]):
        _require_keys(
            seg,
            [
                "segment_id", "start_time", "end_time", "duration",
                "scores", "composite_score", "gate_status",
            ],
            f"manifest.segments[{i}]",
        )
        _require_keys(
            seg["scores"],
            ["sharpness", "exposure", "motion_smoothness", "composition"],
            f"manifest.segments[{i}].scores",
        )
        if seg["gate_status"] != "passed":
            raise ManifestValidationError(
                f"manifest.segments[{i}].gate_status must be 'passed'; "
                f"failing segments belong in excluded_segments"
            )

    if not isinstance(doc["excluded_segments"], list):
        raise ManifestValidationError("manifest.excluded_segments must be an array")
    for i, seg in enumerate(doc["excluded_segments"]):
        _require_keys(
            seg,
            [
                "segment_id", "start_time", "end_time", "duration",
                "scores", "gate_status", "gate_failures",
            ],
            f"manifest.excluded_segments[{i}]",
        )
        if seg["gate_status"] != "failed":
            raise ManifestValidationError(
                f"manifest.excluded_segments[{i}].gate_status must be 'failed'"
            )
        if not seg["gate_failures"]:
            raise ManifestValidationError(
                f"manifest.excluded_segments[{i}].gate_failures must be non-empty"
            )

    _require_keys(
        doc["summary"],
        [
            "total_segments", "total_duration", "avg_composite_score",
            "scenes_detected", "motion_minima_detected", "segments_excluded",
        ],
        "manifest.summary",
    )


# ---------------------------------------------------------------------------
# Capability 2 -- Edit manifest (reel_stitching input), per plan.md section
# "2. Edit manifest".
# ---------------------------------------------------------------------------

EDIT_MANIFEST_SCHEMA: dict = {
    "type": "object",
    "required": ["version", "target_duration", "entries"],
    "properties": {
        "version": {"type": "integer"},
        "target_duration": {"type": ["number", "null"]},
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["clip_path", "in_tc", "out_tc", "transition_to_next"],
                "properties": {
                    "clip_path": {"type": "string"},
                    "in_tc": {"type": "number"},
                    "out_tc": {"type": "number"},
                    "transition_to_next": {
                        "type": "object",
                        "required": ["type", "duration"],
                        "properties": {
                            "type": {"type": "string"},
                            "duration": {"type": "number"},
                        },
                    },
                },
            },
        },
    },
}


class EditManifestValidationError(ValueError):
    """Raised by validate_edit_manifest on any structural violation."""


def validate_edit_manifest(doc: dict) -> None:
    """Validate ``doc`` (a plain dict, e.g. from ``json.loads``) against the
    edit-manifest schema. Raises :class:`EditManifestValidationError` on any
    violation; returns ``None`` when the document is structurally valid.

    Per plan.md: ``entries`` must be non-empty; every entry's ``out_tc`` must
    exceed its ``in_tc``; ``transition_to_next.duration`` must be ``0.0``
    whenever ``transition_to_next.type == "cut"``; the final entry's
    ``transition_to_next`` must be the ``{"type": "cut", "duration": 0.0}``
    sentinel (there is no clip after the last entry to transition into).
    """
    _require_keys(doc, EDIT_MANIFEST_SCHEMA["required"], "edit_manifest")

    if not isinstance(doc["version"], int):
        raise EditManifestValidationError("edit_manifest.version must be an integer")

    td = doc["target_duration"]
    if td is not None and not isinstance(td, (int, float)):
        raise EditManifestValidationError(
            "edit_manifest.target_duration must be a number or null"
        )

    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        raise EditManifestValidationError("edit_manifest.entries must be a non-empty array")

    for i, entry in enumerate(entries):
        ctx = f"edit_manifest.entries[{i}]"
        _require_keys(entry, ["clip_path", "in_tc", "out_tc", "transition_to_next"], ctx)
        if not isinstance(entry["clip_path"], str) or not entry["clip_path"]:
            raise EditManifestValidationError(f"{ctx}.clip_path must be a non-empty string")
        if entry["out_tc"] <= entry["in_tc"]:
            raise EditManifestValidationError(
                f"{ctx}: out_tc ({entry['out_tc']}) must be greater than in_tc ({entry['in_tc']})"
            )
        tr = entry["transition_to_next"]
        _require_keys(tr, ["type", "duration"], f"{ctx}.transition_to_next")
        if tr["type"] == "cut" and tr["duration"] != 0.0:
            raise EditManifestValidationError(
                f"{ctx}.transition_to_next.duration must be 0.0 when type == 'cut'"
            )
        if tr["duration"] < 0.0:
            raise EditManifestValidationError(f"{ctx}.transition_to_next.duration must be >= 0.0")
        if i == len(entries) - 1:
            if tr["type"] != "cut" or tr["duration"] != 0.0:
                raise EditManifestValidationError(
                    f"{ctx}: the final entry's transition_to_next must be the "
                    "{'type': 'cut', 'duration': 0.0} sentinel -- there is no next clip"
                )
