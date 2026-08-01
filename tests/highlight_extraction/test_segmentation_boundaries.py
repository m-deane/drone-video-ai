"""AC1.3 -- no emitted segment boundary falls strictly inside a detected
scene/shot or strictly inside a motion-maneuver: every emitted start/end
must be a member of the Stage-1 union_boundaries candidate set."""

from __future__ import annotations

from drone_video_ai.common.ffprobe import probe_source_file
from drone_video_ai.highlight_extraction.motion import compute_motion_series
from drone_video_ai.highlight_extraction.segmentation import (
    build_candidate_boundaries,
    detect_scene_boundaries,
    split_segments,
)


def test_scene_boundaries_detected_at_expected_cut_points(tmp_path, clip_factory):
    video_path = tmp_path / "multiscene.mp4"
    expected_cuts = clip_factory["multiscene"](video_path, tmp_path, seg_duration=2.0)

    scene_boundaries = detect_scene_boundaries(str(video_path), min_scene_len_frames=5)

    assert len(scene_boundaries) == len(expected_cuts)
    for detected, expected in zip(sorted(scene_boundaries), expected_cuts):
        assert abs(detected - expected) < 0.5, (detected, expected)


def test_every_emitted_segment_boundary_is_union_boundary_member(tmp_path, clip_factory):
    video_path = tmp_path / "multiscene.mp4"
    clip_factory["multiscene"](video_path, tmp_path, seg_duration=2.0)

    probe = probe_source_file(str(video_path))
    motion_samples = compute_motion_series(str(video_path))
    boundary_set = build_candidate_boundaries(
        str(video_path), probe.duration, motion_samples, min_scene_len_frames=5
    )

    segments = split_segments(boundary_set.union_boundaries, min_duration=1.0, max_duration=3.0)

    assert len(segments) > 0
    union_set = set(boundary_set.union_boundaries)
    for start, end in segments:
        assert start in union_set, f"segment start {start} not in union_boundaries {union_set}"
        assert end in union_set, f"segment end {end} not in union_boundaries {union_set}"


def test_split_segments_respects_min_max_duration_when_boundaries_allow():
    # A boundary set evenly spaced 2s apart; max_duration=3 forces one
    # boundary per segment (can't merge two 2s spans without exceeding 3s).
    boundaries = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
    segments = split_segments(boundaries, min_duration=1.0, max_duration=3.0)

    assert segments == [(0.0, 2.0), (2.0, 4.0), (4.0, 6.0), (6.0, 8.0), (8.0, 10.0)]
    for start, end in segments:
        duration = end - start
        assert 1.0 <= duration <= 3.0


def test_split_segments_does_not_collapse_a_span_that_fits_inside_max_duration():
    # Audit finding 0, guarded directly. Boundaries every 1.5s across a 9s span
    # with a 15s cap: the whole span fits inside max_duration, and the old rule
    # (farthest boundary within max) therefore returned ONE segment (0.0, 9.0),
    # discarding all five interior boundaries it had just been handed. Measured
    # 2026-08-01: that made segmentation inert on 5 of the 6 corpus clips, which
    # pinned sharpness and motion_smoothness to null and left the extractor with
    # nothing to rank.
    boundaries = [0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0]
    segments = split_segments(boundaries, min_duration=2.0, max_duration=15.0)

    assert segments == [(0.0, 3.0), (3.0, 6.0), (6.0, 9.0)]
    for start, end in segments:
        assert 2.0 <= (end - start) <= 15.0


def test_split_segments_folds_a_sub_min_tail_into_its_predecessor():
    # The last boundary sits 1.0s after the previous one, below min_duration=2.0.
    # Emitting it alone would violate AC1.4, so it is folded backwards -- the
    # merged span is 3.0s, still inside max_duration.
    segments = split_segments([0.0, 2.0, 4.0, 5.0], min_duration=2.0, max_duration=15.0)

    assert segments == [(0.0, 2.0), (2.0, 5.0)]


def test_split_segments_keeps_a_sub_min_tail_when_folding_would_break_max_duration():
    # Same shape, but merging (0.0, 14.0) with the 1.0s tail would produce a 15.0s
    # segment against a 14.0s cap. A bounds-violating segment beats an invented
    # cut point, so the tail is left where the boundary set put it.
    segments = split_segments([0.0, 14.0, 15.0], min_duration=2.0, max_duration=14.0)

    assert segments == [(0.0, 14.0), (14.0, 15.0)]


def test_split_segments_merges_short_spans_to_meet_min_duration():
    # Boundaries every 1s; min_duration=2.5 forces merging across multiple
    # 1s spans, but every chosen start/end must still be a set member.
    boundaries = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    segments = split_segments(boundaries, min_duration=2.5, max_duration=4.0)

    boundary_set = set(boundaries)
    for start, end in segments:
        assert start in boundary_set
        assert end in boundary_set
        assert (end - start) >= 2.5 - 1e-6 or end == boundaries[-1]
