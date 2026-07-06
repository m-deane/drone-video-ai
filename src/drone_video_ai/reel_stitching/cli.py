"""``drone-stitch`` CLI entrypoint: render an edit manifest (JSON) into a
stitched reel, honoring an optional target duration, and verify the
stream-copy regions before reporting success (plan.md task 2.7)."""

from __future__ import annotations

import argparse
import sys

from drone_video_ai.common.schema import EditManifestValidationError, validate_edit_manifest
from drone_video_ai.reel_stitching.edit_manifest import EditManifest
from drone_video_ai.reel_stitching.pacing import DEFAULT_TOLERANCE, PacingError, apply_target_duration
from drone_video_ai.reel_stitching.render import RenderError, render_edit_manifest
from drone_video_ai.reel_stitching.verify import VerificationError, verify_render_result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drone-stitch",
        description=(
            "Capability 2 (Reel Stitching), Milestone 1: render a JSON edit "
            "manifest into a stitched reel via ffmpeg concat-demuxer hard "
            "cuts and xfade transition windows. No color grading, exposure/ "
            "white-balance adjustment, sharpening, stabilization, "
            "letterboxing, or speed-ramping is ever performed."
        ),
    )
    parser.add_argument("edit_manifest", help="Path to the input edit-manifest JSON file.")
    parser.add_argument("-o", "--output", required=True, help="Path to write the rendered reel to.")
    parser.add_argument(
        "--target-duration",
        type=float,
        default=None,
        help="Target total reel duration in seconds (overrides the manifest's own target_duration).",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=f"Pacing tolerance in seconds (default {DEFAULT_TOLERANCE}).",
    )
    parser.add_argument(
        "--paced-manifest-out",
        default=None,
        help="Optional path to also write the paced (post-trim) edit manifest JSON to, for inspection.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validating the input edit manifest against the schema before rendering.",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip the post-render framemd5 stream-copy verification step.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    with open(args.edit_manifest) as f:
        raw = f.read()

    if not args.skip_validation:
        import json

        try:
            validate_edit_manifest(json.loads(raw))
        except EditManifestValidationError as exc:
            print(f"Input edit manifest failed schema validation: {exc}", file=sys.stderr)
            return 1

    manifest = EditManifest.from_json(raw)

    try:
        paced = apply_target_duration(manifest, args.target_duration, tolerance=args.tolerance)
    except PacingError as exc:
        print(f"Could not honor target duration: {exc}", file=sys.stderr)
        return 1

    if args.paced_manifest_out:
        with open(args.paced_manifest_out, "w") as f:
            f.write(paced.to_json())

    try:
        result = render_edit_manifest(paced, args.output)
    except RenderError as exc:
        print(f"Render failed: {exc}", file=sys.stderr)
        return 1

    if not args.skip_verify:
        try:
            verify_render_result(result)
        except VerificationError as exc:
            print(f"Post-render verification failed: {exc}", file=sys.stderr)
            return 1

    print(
        f"Wrote stitched reel to {args.output} "
        f"({len(result.run_outputs)} stream-copy run(s), "
        f"{len(result.transition_outputs)} transition(s)).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
