"""AC2.1: given an all-"cut" edit manifest over a single-source synthetic
clip, the rendered output's stream-copied regions must be byte-exact to
source, verified via ffmpeg framemd5 -- not a manual/visual spot check."""

from __future__ import annotations

from drone_video_ai.reel_stitching.edit_manifest import EditEntry, EditManifest, TransitionSpec
from drone_video_ai.reel_stitching.render import render_edit_manifest
from drone_video_ai.reel_stitching.verify import verify_render_result


def test_all_cut_manifest_stream_copy_is_byte_exact(cuttable_clip_factory, tmp_path):
    clip = cuttable_clip_factory(duration=6.0, fps=10, size="160x120")

    manifest = EditManifest(
        entries=[
            EditEntry(str(clip), 0.0, 2.0, TransitionSpec("cut", 0.0)),
            EditEntry(str(clip), 2.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(str(clip), 4.0, 6.0, TransitionSpec("cut", 0.0)),
        ]
    )

    output_path = tmp_path / "output.mp4"
    result = render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))

    # All three entries are cut-connected -> exactly one stream-copy run,
    # no transition segments.
    assert len(result.run_outputs) == 1
    assert len(result.transition_outputs) == 0
    assert len(result.run_outputs[0].checks) == 3

    # The mechanical, tool-grounded check itself (Constitution rule 6) --
    # raises VerificationError on any divergence.
    verify_render_result(result)


def test_all_cut_manifest_with_gap_is_still_byte_exact(cuttable_clip_factory, tmp_path):
    """Segments need not be contiguous in source time -- e.g. skipping a
    middle region entirely -- and must still stream-copy byte-exact."""
    clip = cuttable_clip_factory(duration=6.0, fps=10, size="160x120")

    manifest = EditManifest(
        entries=[
            EditEntry(str(clip), 0.0, 1.0, TransitionSpec("cut", 0.0)),
            EditEntry(str(clip), 5.0, 6.0, TransitionSpec("cut", 0.0)),
        ]
    )

    output_path = tmp_path / "output.mp4"
    result = render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))

    assert len(result.run_outputs) == 1
    verify_render_result(result)


def test_verification_detects_corruption(cuttable_clip_factory, tmp_path):
    """Negative control: if the rendered file is tampered with (simulating a
    stream-copy path that silently altered pixels), verification must fail
    -- proving the check is not a tautology."""
    import shutil

    from drone_video_ai.reel_stitching.verify import VerificationError, verify_frame_range

    clip = cuttable_clip_factory(duration=6.0, fps=10, size="160x120")
    manifest = EditManifest(
        entries=[EditEntry(str(clip), 0.0, 2.0, TransitionSpec("cut", 0.0))]
    )
    output_path = tmp_path / "output.mp4"
    result = render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))

    # Corrupt the run output by pointing verification at a visually
    # different clip (a solid color, not the testsrc pattern) instead of
    # the real render -- guarantees genuinely different pixel content
    # rather than relying on testsrc's deterministic-but-possibly-matching
    # output.
    import subprocess

    decoy = tmp_path / "decoy.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", "color=c=red:s=160x120:d=2.0:r=10",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-g", "1", "-keyint_min", "1", "-sc_threshold", "0",
            str(decoy),
        ],
        check=True,
    )

    check = result.run_outputs[0].checks[0]
    import pytest

    with pytest.raises(VerificationError):
        verify_frame_range(check, str(decoy))

    shutil.rmtree(tmp_path / "work", ignore_errors=True)
