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
``composition``/``composite_score`` fields -- see
``drone_video_ai.common.manifest.SegmentScores`` -- though this is a distinct,
independently-populated schema: an exemplar's ``composition`` here stays
``null`` until that specific exemplar is individually reviewed enough to
populate it, regardless of what Capability 1's own composition-scoring
milestone status is), and ``award_or_showcase_provenance`` (nullable).

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

``editorial_style`` is likewise not part of the spec's minimum AC71 field
list, but extends the same "derived analysis" idea the spec's own Scope-in
text calls for (spec line 37: "this project's own derived analysis ... plus
shot-length/cut/transition-style notes") -- a schema slot for this was never
actually added when Capability 3 was first implemented; this closes that
gap. It captures editorial/pacing characteristics (short-form-reel vs.
long-form-cinematic, approximate cut count/shot length, transition styles,
pacing notes) so the pack can inform Capability 2's stitching heuristics,
not just Capability 1's quality-scoring heuristics. Like ``scores_provenance``,
it is honest about its own provenance via ``review_method``: ``"not_reviewed"``
(default -- no editorial analysis attempted), ``"text_provenance_only"``
(inferred from creator description/press coverage, not actual playback), or
``"live_playback_review"`` (an actual human/agent watched or scrubbed the
video). Never presented as frame-accurate measurement -- these are qualitative
observations, same epistemic tier as ``scores_provenance: "manually_estimated"``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, List, Optional

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

# editorial_style.format: the axis this pack uses to track content-genre
# variety (spec's "professional editing" reference goal) -- deliberately not
# part of LICENSE_CATEGORIES/PLATFORMS since it describes editing style, not
# rights or hosting. None is valid for records not yet format-classified
# (e.g. the still-photo exemplar, or any not-yet-reviewed video).
EDITORIAL_FORMAT_VALUES = {"short-form-reel", "long-form-cinematic"}

# editorial_style.review_method: honesty tag, mirrors scores_provenance's
# computed/manually_estimated distinction -- see module docstring.
REVIEW_METHOD_VALUES = {"live_playback_review", "text_provenance_only", "not_reviewed"}

EXEMPLAR_RECORD_VERSION = 1


class ExemplarValidationError(ValueError):
    """Raised by validate_exemplar_record on any structural/policy violation."""


@dataclass
class EditorialStyle:
    """Qualitative editing/pacing observations for one exemplar -- see the
    module docstring's ``editorial_style`` section for the honesty contract
    ``review_method`` encodes. All fields except ``review_method`` are
    ``None``/empty until an actual review (playback or text-based) populates
    them; never fill these in as a guess dressed up as an observation."""

    format: Optional[str] = None  # "short-form-reel" | "long-form-cinematic" | None
    estimated_cut_count: Optional[int] = None
    avg_shot_length_seconds: Optional[float] = None
    transition_styles_observed: List[str] = field(default_factory=list)
    pacing_notes: Optional[str] = None
    review_method: str = "not_reviewed"

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "estimated_cut_count": self.estimated_cut_count,
            "avg_shot_length_seconds": self.avg_shot_length_seconds,
            "transition_styles_observed": list(self.transition_styles_observed),
            "pacing_notes": self.pacing_notes,
            "review_method": self.review_method,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EditorialStyle":
        return cls(
            format=d.get("format"),
            estimated_cut_count=d.get("estimated_cut_count"),
            avg_shot_length_seconds=d.get("avg_shot_length_seconds"),
            transition_styles_observed=list(d.get("transition_styles_observed", [])),
            pacing_notes=d.get("pacing_notes"),
            review_method=d.get("review_method", "not_reviewed"),
        )


@dataclass
class ExemplarScores:
    sharpness: Optional[float]
    exposure: Optional[float]
    motion_smoothness: Optional[float]
    composite_score: Optional[float]
    composition: Optional[float] = None  # null until an exemplar is individually
    # reviewed enough to populate it; NOT tied to Capability 1's own
    # composition-scoring milestone status (Capability 1's scores.composition
    # is populated for real as of its Milestone 2 -- see common/manifest.py --
    # but that is a separate, unrelated schema from this reference-pack
    # ExemplarScores).

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
    editorial_style: EditorialStyle = field(default_factory=EditorialStyle)
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
            "editorial_style": self.editorial_style.to_dict(),
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
            editorial_style=EditorialStyle.from_dict(d.get("editorial_style", {})),
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

    # editorial_style is optional (not in EXEMPLAR_RECORD_SCHEMA["required"],
    # same tier as scores_provenance/notes -- see module docstring), but if
    # present its shape and enums are validated.
    editorial_style = doc.get("editorial_style")
    if editorial_style is not None:
        if not isinstance(editorial_style, dict):
            raise ExemplarValidationError("exemplar.editorial_style must be an object or absent")
        if editorial_style.get("format") not in EDITORIAL_FORMAT_VALUES | {None}:
            raise ExemplarValidationError(
                f"exemplar.editorial_style.format must be one of {sorted(EDITORIAL_FORMAT_VALUES)} or null"
            )
        review_method = editorial_style.get("review_method", "not_reviewed")
        if review_method not in REVIEW_METHOD_VALUES:
            raise ExemplarValidationError(
                f"exemplar.editorial_style.review_method must be one of {sorted(REVIEW_METHOD_VALUES)}"
            )
        transitions = editorial_style.get("transition_styles_observed", [])
        if not isinstance(transitions, list) or not all(isinstance(t, str) for t in transitions):
            raise ExemplarValidationError(
                "exemplar.editorial_style.transition_styles_observed must be a list of strings"
            )
