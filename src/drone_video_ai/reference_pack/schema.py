"""Exemplar-record dataclass and JSON schema for Capability 3 (Reference Pack).

Per ``.claude/specs/drone-video-pipeline/spec.md`` AC 71-74 and plan.md
section "3. Exemplar record", this module defines the record shape used to
describe one award-winning/showcase drone landscape or wildlife video as a
scoring exemplar. This capability is intentionally metadata-first (spec
Scope-in line 37-40) -- no bulk scraping/downloading is performed anywhere in
this module; it only defines and validates the shape of hand-authored (or
single ad hoc, human-reviewed) exemplar records.

Field-by-field mapping back to spec AC 71:
``source_url``, ``platform``, ``license_category``, ``title``, ``creator``,
``duration``, ``retrieval_date``, per-signal + composite quality scores
(matching Capability 1's ``sharpness``/``exposure``/``motion_smoothness``/
``composition``/``composite_score`` fields and its Milestone-1 convention of
``composition: null`` -- see
``drone_video_ai.common.manifest.SegmentScores``), and
``award_or_showcase_provenance`` (nullable).

``local_media_path`` (nullable) additionally encodes AC 72/73's storage rule:
it must stay ``null`` unless the exemplar's license genuinely permits local
footage retention (spec line 38: "content individually verified as CC BY /
CC0 / public domain / owned footage -- verified per-upload"). The mechanical
check for this lives in ``reference_pack/storage.py``; this module's
``validate_exemplar_record`` also enforces the same rule at the single-record
level so it can be asserted against in-memory records without touching the
filesystem.

``scores_provenance`` is not part of the spec's minimum field list but is
included here as an honest, mechanically-checkable distinction (mirroring
Capability 1's ``gate_status`` distinguishing excluded vs. passing segments):
it records whether ``scores`` were produced by actually running Capability
1's scoring functions (``"computed"``) against real footage, or by manual
review without access to the source file (``"manually_estimated"``) -- per
this task's instruction not to present manually-estimated numbers as if they
were measured.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

# Full license-category enum per spec AC 71.
LICENSE_CATEGORIES = {
    "all-rights-reserved",
    "cc-by",
    "cc-by-nc",
    "cc-by-sa",
    "cc-by-nd",
    "cc0",
    "public-domain",
    "owned",
}

# Platforms named in spec AC 71 ("YouTube/Vimeo/other").
PLATFORMS = {"youtube", "vimeo", "other"}

# Per spec line 38 ("Actual footage-file retention reserved strictly for
# content individually verified as CC BY / CC0 / public domain / owned
# footage"): only these four categories may ever carry a non-null
# ``local_media_path``. Note this is a stricter (narrower) list than the
# full LICENSE_CATEGORIES enum -- cc-by-nc/cc-by-sa/cc-by-nd exemplars are
# metadata-only in this project's default posture even though they are valid
# license_category values for the field itself.
LOCAL_MEDIA_PERMITTED_LICENSES = {"cc-by", "cc0", "public-domain", "owned"}

SCORES_PROVENANCE_VALUES = {"computed", "manually_estimated"}

EXEMPLAR_RECORD_VERSION = 1


class ExemplarValidationError(ValueError):
    """Raised by validate_exemplar_record on any structural/policy violation."""


@dataclass
class ExemplarScores:
    sharpness: Optional[float]
    exposure: Optional[float]
    motion_smoothness: Optional[float]
    composite_score: Optional[float]
    composition: Optional[float] = None  # always None -- Capability 1 Milestone 1 convention

    def to_dict(self) -> dict:
        return {
            "sharpness": self.sharpness,
            "exposure": self.exposure,
            "motion_smoothness": self.motion_smoothness,
            "composition": self.composition,
            "composite_score": self.composite_score,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ExemplarScores":
        return cls(
            sharpness=d.get("sharpness"),
            exposure=d.get("exposure"),
            motion_smoothness=d.get("motion_smoothness"),
            composite_score=d.get("composite_score"),
            composition=d.get("composition"),
        )


@dataclass
class ExemplarRecord:
    source_url: str
    platform: str
    license_category: str
    title: str
    creator: str
    retrieval_date: str  # "YYYY-MM-DD"
    scores: ExemplarScores
    duration: Optional[float] = None  # None when not independently verified this session
    award_or_showcase_provenance: Optional[str] = None
    local_media_path: Optional[str] = None
    scores_provenance: str = "manually_estimated"
    notes: Optional[str] = None
    version: int = EXEMPLAR_RECORD_VERSION

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "source_url": self.source_url,
            "platform": self.platform,
            "license_category": self.license_category,
            "title": self.title,
            "creator": self.creator,
            "duration": self.duration,
            "retrieval_date": self.retrieval_date,
            "scores": self.scores.to_dict(),
            "award_or_showcase_provenance": self.award_or_showcase_provenance,
            "local_media_path": self.local_media_path,
            "scores_provenance": self.scores_provenance,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "ExemplarRecord":
        return cls(
            version=d.get("version", EXEMPLAR_RECORD_VERSION),
            source_url=d["source_url"],
            platform=d["platform"],
            license_category=d["license_category"],
            title=d["title"],
            creator=d["creator"],
            duration=d.get("duration"),
            retrieval_date=d["retrieval_date"],
            scores=ExemplarScores.from_dict(d["scores"]),
            award_or_showcase_provenance=d.get("award_or_showcase_provenance"),
            local_media_path=d.get("local_media_path"),
            scores_provenance=d.get("scores_provenance", "manually_estimated"),
            notes=d.get("notes"),
        )

    @classmethod
    def from_json(cls, s: str) -> "ExemplarRecord":
        return cls.from_dict(json.loads(s))


# JSON-schema-shaped dict (documentation) mirroring
# drone_video_ai.common.schema's structural-validator convention -- no
# third-party jsonschema dependency, per that module's precedent.
EXEMPLAR_RECORD_SCHEMA: dict = {
    "type": "object",
    "required": [
        "version",
        "source_url",
        "platform",
        "license_category",
        "title",
        "creator",
        "duration",
        "retrieval_date",
        "scores",
        "award_or_showcase_provenance",
        "local_media_path",
    ],
    "properties": {
        "version": {"type": "integer"},
        "source_url": {"type": "string"},
        "platform": {"type": "string", "enum": sorted(PLATFORMS)},
        "license_category": {"type": "string", "enum": sorted(LICENSE_CATEGORIES)},
        "title": {"type": "string"},
        "creator": {"type": "string"},
        "duration": {"type": ["number", "null"]},
        "retrieval_date": {"type": "string"},
        "scores": {
            "type": "object",
            "required": ["sharpness", "exposure", "motion_smoothness", "composition", "composite_score"],
        },
        "award_or_showcase_provenance": {"type": ["string", "null"]},
        "local_media_path": {"type": ["string", "null"]},
    },
}


def _require_keys(obj: Any, keys: list, context: str) -> None:
    if not isinstance(obj, dict):
        raise ExemplarValidationError(f"{context}: expected an object, got {type(obj).__name__}")
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ExemplarValidationError(f"{context}: missing required key(s) {missing}")


def check_local_media_storage_rule(doc: dict) -> Optional[str]:
    """Pure, filesystem-free check of the storage-layout rule (spec AC3.2).

    Returns ``None`` if ``doc`` is consistent with the rule, or a human-
    readable violation message otherwise. Kept separate from
    ``validate_exemplar_record`` so ``reference_pack/storage.py`` can reuse
    the exact same rule for on-disk records without re-deriving it.

    Rule: ``local_media_path`` must be ``null`` for every ``license_category``
    outside ``LOCAL_MEDIA_PERMITTED_LICENSES`` -- this always includes, and is
    a superset of, the literal AC3.2 wording ("no exemplar record with
    license_category = all-rights-reserved has an associated locally-stored
    video file").
    """
    license_category = doc.get("license_category")
    local_media_path = doc.get("local_media_path")
    if local_media_path is not None and license_category not in LOCAL_MEDIA_PERMITTED_LICENSES:
        return (
            f"license_category={license_category!r} may not have a non-null "
            f"local_media_path (got {local_media_path!r}); only "
            f"{sorted(LOCAL_MEDIA_PERMITTED_LICENSES)} permit local media storage"
        )
    return None


def validate_exemplar_record(doc: dict) -> None:
    """Validate ``doc`` against the exemplar-record schema and the
    storage-layout policy. Raises :class:`ExemplarValidationError` on any
    violation; returns ``None`` when valid."""
    _require_keys(doc, EXEMPLAR_RECORD_SCHEMA["required"], "exemplar")

    if not isinstance(doc["version"], int):
        raise ExemplarValidationError("exemplar.version must be an integer")

    if doc["platform"] not in PLATFORMS:
        raise ExemplarValidationError(f"exemplar.platform must be one of {sorted(PLATFORMS)}")

    if doc["license_category"] not in LICENSE_CATEGORIES:
        raise ExemplarValidationError(
            f"exemplar.license_category must be one of {sorted(LICENSE_CATEGORIES)}"
        )

    for field_name in ("source_url", "title", "creator", "retrieval_date"):
        if not isinstance(doc[field_name], str) or not doc[field_name]:
            raise ExemplarValidationError(f"exemplar.{field_name} must be a non-empty string")

    if doc["duration"] is not None and not isinstance(doc["duration"], (int, float)):
        raise ExemplarValidationError("exemplar.duration must be a number or null")

    _require_keys(
        doc["scores"],
        ["sharpness", "exposure", "motion_smoothness", "composition", "composite_score"],
        "exemplar.scores",
    )

    if doc["award_or_showcase_provenance"] is not None and not isinstance(
        doc["award_or_showcase_provenance"], str
    ):
        raise ExemplarValidationError("exemplar.award_or_showcase_provenance must be a string or null")

    if doc["local_media_path"] is not None and not isinstance(doc["local_media_path"], str):
        raise ExemplarValidationError("exemplar.local_media_path must be a string or null")

    violation = check_local_media_storage_rule(doc)
    if violation is not None:
        raise ExemplarValidationError(f"exemplar: storage-layout rule violated -- {violation}")
