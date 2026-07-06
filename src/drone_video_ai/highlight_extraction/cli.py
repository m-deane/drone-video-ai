"""``drone-highlights`` CLI entrypoint: run the Capability 1 Milestone 1
pipeline against a video file and emit a JSON highlight manifest."""

from __future__ import annotations

import argparse
import sys

from drone_video_ai.common.schema import ManifestValidationError, validate_highlight_manifest
from drone_video_ai.highlight_extraction.gates import GateConfig
from drone_video_ai.highlight_extraction.pipeline import PipelineConfig, run_pipeline
from drone_video_ai.highlight_extraction.segmentation import (
    DEFAULT_MIN_SCENE_LEN_FRAMES,
    DEFAULT_SCENE_THRESHOLD,
)
from drone_video_ai.highlight_extraction.weights import DEFAULT_DURATION_PROFILE


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drone-highlights",
        description=(
            "Capability 1 (Highlight Extraction), Milestone 1: segment a raw drone "
            "video into quality-scored candidate highlight clips and emit a JSON "
            "manifest. Composition scoring is deferred to Milestone 2 -- every "
            "emitted segment's scores.composition is null."
        ),
    )
    parser.add_argument("input", help="Path to the input video file.")
    parser.add_argument(
        "-o", "--output", required=True, help="Path to write the JSON highlight manifest to."
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=DEFAULT_DURATION_PROFILE.min_duration,
        help=f"Minimum segment duration in seconds (default {DEFAULT_DURATION_PROFILE.min_duration}).",
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=DEFAULT_DURATION_PROFILE.max_duration,
        help=f"Maximum segment duration in seconds (default {DEFAULT_DURATION_PROFILE.max_duration}).",
    )
    parser.add_argument(
        "--scene-threshold",
        type=float,
        default=DEFAULT_SCENE_THRESHOLD,
        help=f"PySceneDetect AdaptiveDetector adaptive_threshold (default {DEFAULT_SCENE_THRESHOLD}).",
    )
    parser.add_argument(
        "--min-scene-len-frames",
        type=int,
        default=DEFAULT_MIN_SCENE_LEN_FRAMES,
        help=f"PySceneDetect AdaptiveDetector min_scene_len in frames (default {DEFAULT_MIN_SCENE_LEN_FRAMES}).",
    )
    parser.add_argument(
        "--min-sharpness-floor",
        type=float,
        default=GateConfig.min_sharpness_floor,
        help="Hard-gate: minimum normalized [0,1] sharpness score to pass (default 0.0 == no floor).",
    )
    parser.add_argument(
        "--min-exposure-floor",
        type=float,
        default=GateConfig.min_exposure_floor,
        help="Hard-gate: minimum normalized [0,1] exposure score to pass (default 0.0 == no floor).",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validating the emitted manifest against the schema before writing.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    gate_config = GateConfig(
        min_sharpness_floor=args.min_sharpness_floor,
        min_exposure_floor=args.min_exposure_floor,
    )
    config = PipelineConfig(
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        scene_threshold=args.scene_threshold,
        min_scene_len_frames=args.min_scene_len_frames,
        gate_config=gate_config,
    )

    manifest = run_pipeline(args.input, config=config)
    manifest_dict = manifest.to_dict()

    if not args.skip_validation:
        try:
            validate_highlight_manifest(manifest_dict)
        except ManifestValidationError as exc:
            print(f"Emitted manifest failed schema validation: {exc}", file=sys.stderr)
            return 1

    with open(args.output, "w") as f:
        f.write(manifest.to_json())

    print(
        f"Wrote highlight manifest to {args.output} "
        f"({manifest.summary.total_segments} segments, "
        f"{manifest.summary.segments_excluded} excluded).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
