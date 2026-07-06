"""AC1.1, AC1.4, AC1.5 -- end-to-end pipeline run against a synthetic
multi-segment fixture: manifest validates against the schema, version == 2,
no post_processing key anywhere, every emitted segment's duration is within
configured min/max bounds, and the normalization block is present and
non-empty for all three scored signals.

Also exercises AC1.2 end-to-end: a deliberately black segment must land in
excluded_segments with a non-empty gate_failures list, not in segments.
"""

from __future__ import annotations

import json
import subprocess

from drone_video_ai.common.schema import validate_highlight_manifest
from drone_video_ai.highlight_extraction.gates import GateConfig
from drone_video_ai.highlight_extraction.pipeline import PipelineConfig, run_pipeline


def _run_ffmpeg(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, check=True)


def _make_pipeline_test_video(tmp_path, seg_duration=3.0, size="320x240", fps=25):
    """testsrc (good) -> black (must be gated out) -> testsrc (good), three
    3s segments concatenated -> 9s total, two clear scene cuts at 3s/6s."""
    seg_paths = []

    testsrc1 = tmp_path / "_seg_testsrc1.mp4"
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"testsrc=size={size}:rate={fps}:duration={seg_duration}",
        "-pix_fmt", "yuv420p", str(testsrc1),
    ])
    seg_paths.append(testsrc1)

    black = tmp_path / "_seg_black.mp4"
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c=black:s={size}:d={seg_duration}:r={fps}",
        "-pix_fmt", "yuv420p", str(black),
    ])
    seg_paths.append(black)

    testsrc2 = tmp_path / "_seg_testsrc2.mp4"
    _run_ffmpeg([
        "-f", "lavfi", "-i", f"testsrc2=size={size}:rate={fps}:duration={seg_duration}",
        "-pix_fmt", "yuv420p", str(testsrc2),
    ])
    seg_paths.append(testsrc2)

    concat_list = tmp_path / "_concat_list.txt"
    with open(concat_list, "w") as f:
        for sp in seg_paths:
            f.write(f"file '{sp}'\n")

    output_path = tmp_path / "pipeline_test_video.mp4"
    _run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(output_path),
    ])
    return output_path


def test_pipeline_end_to_end_manifest_shape(tmp_path):
    video_path = _make_pipeline_test_video(tmp_path, seg_duration=3.0)

    config = PipelineConfig(
        min_duration=2.0,
        max_duration=15.0,
        min_scene_len_frames=5,
        gate_config=GateConfig(),
    )
    manifest = run_pipeline(str(video_path), config=config)
    doc = manifest.to_dict()

    # (a) validates against schema
    validate_highlight_manifest(doc)

    # (b) version == 2
    assert doc["version"] == 2

    # (c) no post_processing key anywhere
    assert "post_processing" not in json.dumps(doc)

    # (d) every emitted segment's duration within configured min/max bounds
    for seg in doc["segments"]:
        assert config.min_duration <= seg["duration"] <= config.max_duration + 1e-6
    for seg in doc["excluded_segments"]:
        assert seg["duration"] > 0

    # (e) normalization block present and non-empty for all three scored signals
    normalization = doc["normalization"]
    for key in ("sharpness", "exposure", "motion_smoothness"):
        assert key in normalization
        assert normalization[key]

    # composition stays null/deferred in Milestone 1
    assert normalization["composition"]
    for seg in doc["segments"]:
        assert seg["scores"]["composition"] is None
    assert doc["scoring_weights"]["weights"]["composition"] == 0.0


def test_pipeline_gates_out_the_black_segment(tmp_path):
    video_path = _make_pipeline_test_video(tmp_path, seg_duration=3.0)

    config = PipelineConfig(min_duration=2.0, max_duration=15.0, min_scene_len_frames=5)
    manifest = run_pipeline(str(video_path), config=config)

    # The black segment (roughly 3.0-6.0s) must be excluded, not merely
    # low-scoring, and must carry the blackdetect gate failure.
    assert len(manifest.excluded_segments) >= 1
    black_excluded = [
        s for s in manifest.excluded_segments if "blackdetect" in s.gate_failures
    ]
    assert len(black_excluded) >= 1

    excluded_ids = {s.segment_id for s in manifest.excluded_segments}
    accepted_ids = {s.segment_id for s in manifest.segments}
    assert excluded_ids.isdisjoint(accepted_ids)

    for s in manifest.segments:
        assert s.gate_status == "passed"
    for s in manifest.excluded_segments:
        assert s.gate_status == "failed"
        assert len(s.gate_failures) > 0


def test_pipeline_summary_counts_are_consistent(tmp_path):
    video_path = _make_pipeline_test_video(tmp_path, seg_duration=3.0)

    config = PipelineConfig(min_duration=2.0, max_duration=15.0, min_scene_len_frames=5)
    manifest = run_pipeline(str(video_path), config=config)

    assert manifest.summary.total_segments == len(manifest.segments)
    assert manifest.summary.segments_excluded == len(manifest.excluded_segments)
    assert manifest.summary.scenes_detected == len(manifest.candidate_boundaries.scene_boundaries)
