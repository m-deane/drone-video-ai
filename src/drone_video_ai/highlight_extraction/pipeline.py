"""Orchestrates segmentation -> scoring -> gating -> manifest emission for
one input video (Capability 1, Milestone 1).

Composition scoring is not implemented in this milestone (see
``common/manifest.py`` module docstring and plan.md's Milestone 2 section);
every emitted segment's ``scores.composition`` is ``None`` by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from drone_video_ai.common.ffprobe import probe_source_file
from drone_video_ai.common.manifest import (
    CandidateBoundaries,
    ExcludedSegment,
    HighlightManifest,
    ManifestSummary,
    Segment,
    SegmentScores,
    SourceFile,
)
from drone_video_ai.highlight_extraction import segmentation as seg_mod
from drone_video_ai.highlight_extraction.gates import GateConfig, evaluate_gates
from drone_video_ai.highlight_extraction.motion import compute_motion_series
from drone_video_ai.highlight_extraction.scoring_exposure import compute_raw_exposure
from drone_video_ai.highlight_extraction.scoring_motion_smoothness import (
    compute_raw_jerk_magnitude,
    invert_and_normalize,
)
from drone_video_ai.highlight_extraction.scoring_sharpness import (
    compute_raw_sharpness,
    min_max_normalize,
)
from drone_video_ai.highlight_extraction.composite import compute_composite_score
from drone_video_ai.highlight_extraction.weights import DEFAULT_DURATION_PROFILE, default_weights


@dataclass
class PipelineConfig:
    min_duration: float = DEFAULT_DURATION_PROFILE.min_duration
    max_duration: float = DEFAULT_DURATION_PROFILE.max_duration
    scene_threshold: float = seg_mod.DEFAULT_SCENE_THRESHOLD
    min_scene_len_frames: int = seg_mod.DEFAULT_MIN_SCENE_LEN_FRAMES
    motion_smoothing_window: int = 5
    motion_min_gap_seconds: float = 1.0
    max_score_samples_per_segment: int = 10
    gate_config: GateConfig = None
    ffmpeg_bin: str = "ffmpeg"
    ffprobe_bin: str = "ffprobe"

    def __post_init__(self):
        if self.gate_config is None:
            self.gate_config = GateConfig()


def run_pipeline(video_path: str, config: Optional[PipelineConfig] = None) -> HighlightManifest:
    """Run the full Capability 1 Milestone 1 pipeline against ``video_path``
    and return a populated :class:`HighlightManifest`."""
    cfg = config or PipelineConfig()

    probe = probe_source_file(video_path, ffprobe_bin=cfg.ffprobe_bin)
    source_file = SourceFile(
        path=probe.path,
        name=probe.name,
        duration=probe.duration,
        width=probe.width,
        height=probe.height,
        fps=probe.fps,
        codec=probe.codec,
        pix_fmt=probe.pix_fmt,
    )

    motion_samples = compute_motion_series(video_path)

    boundary_set = seg_mod.build_candidate_boundaries(
        video_path=video_path,
        duration=probe.duration,
        motion_samples=motion_samples,
        scene_threshold=cfg.scene_threshold,
        min_scene_len_frames=cfg.min_scene_len_frames,
        motion_smoothing_window=cfg.motion_smoothing_window,
        motion_min_gap_seconds=cfg.motion_min_gap_seconds,
    )

    raw_segments = seg_mod.split_segments(
        boundary_set.union_boundaries,
        min_duration=cfg.min_duration,
        max_duration=cfg.max_duration,
    )

    # --- Score each candidate segment (raw, un-normalized where applicable) ---
    raw_sharpness: List[float] = []
    raw_exposure: List[float] = []
    raw_jerk: List[float] = []

    for start, end in raw_segments:
        raw_sharpness.append(
            compute_raw_sharpness(video_path, start, end, max_samples=cfg.max_score_samples_per_segment)
        )
        raw_exposure.append(
            compute_raw_exposure(video_path, start, end, max_samples=cfg.max_score_samples_per_segment)
        )
        raw_jerk.append(compute_raw_jerk_magnitude(motion_samples, start, end))

    normalized_sharpness = min_max_normalize(raw_sharpness)
    normalized_motion_smoothness = invert_and_normalize(raw_jerk)
    # exposure is already normalized (1 - clipped_fraction) per-segment; no
    # cross-segment min-max step, per plan.md's documented normalization method.
    normalized_exposure = raw_exposure

    weights = default_weights()

    segments: List[Segment] = []
    excluded_segments: List[ExcludedSegment] = []

    for i, (start, end) in enumerate(raw_segments):
        sharpness_score = normalized_sharpness[i]
        exposure_score = normalized_exposure[i]
        motion_smoothness_score = normalized_motion_smoothness[i]

        gate_failures = evaluate_gates(
            video_path,
            start,
            end,
            sharpness_score=sharpness_score,
            exposure_score=exposure_score,
            config=cfg.gate_config,
            ffmpeg_bin=cfg.ffmpeg_bin,
        )

        scores = SegmentScores(
            sharpness=sharpness_score,
            exposure=exposure_score,
            motion_smoothness=motion_smoothness_score,
            composition=None,  # Milestone 1: never scored (see module docstring)
        )

        segment_id = f"seg_{i + 1:04d}"

        if gate_failures:
            excluded_segments.append(
                ExcludedSegment(
                    segment_id=segment_id,
                    start_time=start,
                    end_time=end,
                    duration=end - start,
                    scores=scores,
                    gate_failures=gate_failures,
                    gate_status="failed",
                )
            )
        else:
            composite_score = compute_composite_score(
                sharpness=sharpness_score,
                exposure=exposure_score,
                motion_smoothness=motion_smoothness_score,
                composition=None,
                weights=weights,
            )
            segments.append(
                Segment(
                    segment_id=segment_id,
                    start_time=start,
                    end_time=end,
                    duration=end - start,
                    scores=scores,
                    composite_score=composite_score,
                    gate_status="passed",
                )
            )

    total_duration = sum(s.duration for s in segments)
    avg_composite = (
        sum(s.composite_score for s in segments) / len(segments) if segments else 0.0
    )

    summary = ManifestSummary(
        total_segments=len(segments),
        total_duration=total_duration,
        avg_composite_score=avg_composite,
        scenes_detected=len(boundary_set.scene_boundaries),
        motion_minima_detected=len(boundary_set.motion_minima_boundaries),
        segments_excluded=len(excluded_segments),
    )

    candidate_boundaries = CandidateBoundaries(
        scene_boundaries=boundary_set.scene_boundaries,
        motion_minima_boundaries=boundary_set.motion_minima_boundaries,
        union_boundaries=boundary_set.union_boundaries,
    )

    return HighlightManifest(
        source_file=source_file,
        scoring_weights=weights,
        candidate_boundaries=candidate_boundaries,
        segments=segments,
        excluded_segments=excluded_segments,
        summary=summary,
    )
