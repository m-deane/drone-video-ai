"""Highlight-manifest dataclasses and JSON (de)serialization.

This is Capability 1's output schema (and, by contract, Capability 2's
future input source) exactly as fixed in
``.claude/specs/drone-video-pipeline/plan.md`` section
"1. Highlight manifest". Schema version is ``2`` -- bumped from the legacy
``DJI_0355/manifest.json`` precedent's ``1`` because this schema drops the
legacy ``post_processing`` pixel-editing block entirely and adds per-signal
quality scores.

``composition`` is always ``null`` / ``0.0``-weighted in this schema version
(Milestone 1). Composition scoring (OpenCV ``saliency`` rule-of-thirds +
Hough-line horizon-tilt) is deferred to Milestone 2 per plan.md; this is not a
stub -- it is a documented, deliberate omission with an explicit schema slot
reserved for additive population later (see plan.md's "Milestone 2 (composition
scoring) changes to this schema" note: adding real values bumps this to
version 3, not silently overwriting version 2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

MANIFEST_VERSION = 2


@dataclass
class SourceFile:
    path: str
    name: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    pix_fmt: str

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "codec": self.codec,
            "pix_fmt": self.pix_fmt,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SourceFile":
        return cls(
            path=d["path"],
            name=d["name"],
            duration=d["duration"],
            width=d["width"],
            height=d["height"],
            fps=d["fps"],
            codec=d["codec"],
            pix_fmt=d["pix_fmt"],
        )


@dataclass
class ScoringWeights:
    weights_version: str
    sharpness: float
    exposure: float
    motion_smoothness: float
    composition: float = 0.0  # MUST stay 0.0 in Milestone 1 -- see module docstring.

    def to_dict(self) -> dict:
        return {
            "weights_version": self.weights_version,
            "weights": {
                "sharpness": self.sharpness,
                "exposure": self.exposure,
                "motion_smoothness": self.motion_smoothness,
                "composition": self.composition,
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ScoringWeights":
        w = d["weights"]
        return cls(
            weights_version=d["weights_version"],
            sharpness=w["sharpness"],
            exposure=w["exposure"],
            motion_smoothness=w["motion_smoothness"],
            composition=w.get("composition", 0.0),
        )


@dataclass
class CandidateBoundaries:
    scene_boundaries: List[float] = field(default_factory=list)
    motion_minima_boundaries: List[float] = field(default_factory=list)
    union_boundaries: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scene_boundaries": list(self.scene_boundaries),
            "motion_minima_boundaries": list(self.motion_minima_boundaries),
            "union_boundaries": list(self.union_boundaries),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CandidateBoundaries":
        return cls(
            scene_boundaries=list(d.get("scene_boundaries", [])),
            motion_minima_boundaries=list(d.get("motion_minima_boundaries", [])),
            union_boundaries=list(d.get("union_boundaries", [])),
        )


# Default normalization-method descriptions, per plan.md's "normalization" block.
DEFAULT_NORMALIZATION = {
    "sharpness": "in-video min-max over sampled frames -> [0,1]",
    "exposure": "1 - (clipped-pixel fraction from histogram) -> [0,1]",
    "motion_smoothness": "in-video min-max over inverse jerk magnitude -> [0,1]",
    "composition": "not scored in this schema version (Milestone 2, deferred)",
}


@dataclass
class SegmentScores:
    sharpness: float
    exposure: float
    motion_smoothness: float
    composition: Optional[float] = None  # always None in Milestone 1 output

    def to_dict(self) -> dict:
        return {
            "sharpness": self.sharpness,
            "exposure": self.exposure,
            "motion_smoothness": self.motion_smoothness,
            "composition": self.composition,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SegmentScores":
        return cls(
            sharpness=d["sharpness"],
            exposure=d["exposure"],
            motion_smoothness=d["motion_smoothness"],
            composition=d.get("composition"),
        )


@dataclass
class Segment:
    segment_id: str
    start_time: float
    end_time: float
    duration: float
    scores: SegmentScores
    composite_score: float
    gate_status: str = "passed"  # "passed" | "failed"

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "scores": self.scores.to_dict(),
            "composite_score": self.composite_score,
            "gate_status": self.gate_status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Segment":
        return cls(
            segment_id=d["segment_id"],
            start_time=d["start_time"],
            end_time=d["end_time"],
            duration=d["duration"],
            scores=SegmentScores.from_dict(d["scores"]),
            composite_score=d["composite_score"],
            gate_status=d.get("gate_status", "passed"),
        )


@dataclass
class ExcludedSegment:
    segment_id: str
    start_time: float
    end_time: float
    duration: float
    scores: SegmentScores
    gate_failures: List[str]
    gate_status: str = "failed"

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "scores": self.scores.to_dict(),
            "gate_status": self.gate_status,
            "gate_failures": list(self.gate_failures),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ExcludedSegment":
        return cls(
            segment_id=d["segment_id"],
            start_time=d["start_time"],
            end_time=d["end_time"],
            duration=d["duration"],
            scores=SegmentScores.from_dict(d["scores"]),
            gate_status=d.get("gate_status", "failed"),
            gate_failures=list(d["gate_failures"]),
        )


@dataclass
class ManifestSummary:
    total_segments: int
    total_duration: float
    avg_composite_score: float
    scenes_detected: int
    motion_minima_detected: int
    segments_excluded: int

    def to_dict(self) -> dict:
        return {
            "total_segments": self.total_segments,
            "total_duration": self.total_duration,
            "avg_composite_score": self.avg_composite_score,
            "scenes_detected": self.scenes_detected,
            "motion_minima_detected": self.motion_minima_detected,
            "segments_excluded": self.segments_excluded,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ManifestSummary":
        return cls(
            total_segments=d["total_segments"],
            total_duration=d["total_duration"],
            avg_composite_score=d["avg_composite_score"],
            scenes_detected=d["scenes_detected"],
            motion_minima_detected=d["motion_minima_detected"],
            segments_excluded=d["segments_excluded"],
        )


@dataclass
class HighlightManifest:
    source_file: SourceFile
    scoring_weights: ScoringWeights
    candidate_boundaries: CandidateBoundaries
    segments: List[Segment]
    excluded_segments: List[ExcludedSegment]
    summary: ManifestSummary
    normalization: dict = field(default_factory=lambda: dict(DEFAULT_NORMALIZATION))
    version: int = MANIFEST_VERSION

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "source_file": self.source_file.to_dict(),
            "scoring_weights": self.scoring_weights.to_dict(),
            "candidate_boundaries": self.candidate_boundaries.to_dict(),
            "normalization": dict(self.normalization),
            "segments": [s.to_dict() for s in self.segments],
            "excluded_segments": [s.to_dict() for s in self.excluded_segments],
            "summary": self.summary.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "HighlightManifest":
        return cls(
            version=d.get("version", MANIFEST_VERSION),
            source_file=SourceFile.from_dict(d["source_file"]),
            scoring_weights=ScoringWeights.from_dict(d["scoring_weights"]),
            candidate_boundaries=CandidateBoundaries.from_dict(d["candidate_boundaries"]),
            normalization=dict(d.get("normalization", DEFAULT_NORMALIZATION)),
            segments=[Segment.from_dict(s) for s in d.get("segments", [])],
            excluded_segments=[
                ExcludedSegment.from_dict(s) for s in d.get("excluded_segments", [])
            ],
            summary=ManifestSummary.from_dict(d["summary"]),
        )

    @classmethod
    def from_json(cls, s: str) -> "HighlightManifest":
        import json

        return cls.from_dict(json.loads(s))
