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
