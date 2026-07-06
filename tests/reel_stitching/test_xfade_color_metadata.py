"""AC2.2: for a transition-window region, the rendered output's color
metadata (color_primaries/color_trc/color_range/colorspace), as read by
ffprobe, must exactly match the source clips' -- verified programmatically,
including the realistic case (this repo's own sample footage, per plan.md's
grounding notes) where the source reports those tags as unknown/absent
entirely."""

from __future__ import annotations

from drone_video_ai.common.ffprobe import probe_source_file
from drone_video_ai.reel_stitching.edit_manifest import EditEntry, EditManifest, TransitionSpec
from drone_video_ai.reel_stitching.render import render_edit_manifest

_COLOR_FIELDS = ("color_range", "color_primaries", "color_transfer", "color_space")


def test_xfade_transition_color_metadata_matches_source_when_unknown(cuttable_clip_factory, tmp_path):
    clip_a = cuttable_clip_factory(name="a.mp4", duration=3.0, fps=10, size="160x120")
    clip_b = cuttable_clip_factory(name="b.mp4", duration=3.0, fps=10, size="160x120")

    source_info = probe_source_file(str(clip_a))
    # Sanity precondition for this test's premise: the synthetic clips (like
    # this repo's real sample footage) report these tags as unset.
    for field in _COLOR_FIELDS:
        assert getattr(source_info, field) in (None, "unknown"), (
            f"Expected synthetic test clip's {field} to be unset for this test's premise; "
            f"got {getattr(source_info, field)!r}"
        )

    manifest = EditManifest(
        entries=[
            EditEntry(str(clip_a), 0.0, 3.0, TransitionSpec("fade", 1.0)),
            EditEntry(str(clip_b), 0.0, 3.0, TransitionSpec("cut", 0.0)),
        ]
    )

    output_path = tmp_path / "output.mp4"
    result = render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))

    assert len(result.transition_outputs) == 1
    transition = result.transition_outputs[0]
    assert transition.transition_type == "fade"
    assert transition.duration == 1.0

    output_info = probe_source_file(transition.output_path)
    for field in _COLOR_FIELDS:
        src_value = getattr(source_info, field)
        out_value = getattr(output_info, field)
        assert out_value == src_value, (
            f"{field}: source={src_value!r} but rendered transition output={out_value!r} "
            "-- color metadata must exactly match source, including the unknown/unset case."
        )


def test_xfade_transition_color_metadata_pinned_when_explicit(cuttable_clip_factory, tmp_path):
    """When the source *does* carry explicit color tags, the rendered
    transition output must carry those same explicit values -- not fall
    back to unset."""
    import subprocess

    # NOTE: these clips are tagged via a single combined `-x264-params`
    # call (not the generic per-flag `-color_range`/`-color_primaries`/
    # `-color_trc`/`-colorspace` CLI options individually) -- empirically
    # confirmed in this environment that libx264's ffmpeg wrapper only
    # reliably writes the VUI color-description block when all four values
    # are supplied together via `-x264-params`; this is exactly the
    # mechanism `color_pinning.get_transition_pinned_x264_params` uses (see
    # its docstring), so the test fixture and the code under test agree on
    # how color tags actually get embedded by this codec.
    clip_a = tmp_path / "a_tagged.mp4"
    clip_b = tmp_path / "b_tagged.mp4"
    for path in (clip_a, clip_b):
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=3",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-g", "1", "-keyint_min", "1", "-sc_threshold", "0",
                "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off",
                str(path),
            ],
            check=True,
        )

    source_info = probe_source_file(str(clip_a))
    assert source_info.color_range == "tv"
    assert source_info.color_primaries == "bt709"
    assert source_info.color_transfer == "bt709"
    assert source_info.color_space == "bt709"

    manifest = EditManifest(
        entries=[
            EditEntry(str(clip_a), 0.0, 3.0, TransitionSpec("fade", 1.0)),
            EditEntry(str(clip_b), 0.0, 3.0, TransitionSpec("cut", 0.0)),
        ]
    )
    output_path = tmp_path / "output.mp4"
    result = render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))

    transition = result.transition_outputs[0]
    output_info = probe_source_file(transition.output_path)
    assert output_info.color_range == "tv"
    assert output_info.color_primaries == "bt709"
    assert output_info.color_transfer == "bt709"
    assert output_info.color_space == "bt709"


def test_color_pinning_raises_on_disagreeing_sources(cuttable_clip_factory, tmp_path):
    """If the two clips flanking a transition disagree on a color tag, the
    render must fail loudly rather than silently pick one side."""
    import subprocess

    import pytest

    from drone_video_ai.reel_stitching.render import RenderError

    # Uses `-x264-params colormatrix=...` (confirmed in this environment to
    # reliably embed a single tag on its own, unlike the generic
    # `-color_range`/`-color_primaries`/`-color_trc` output flags -- see the
    # note in the previous test) so the two clips genuinely disagree on
    # `color_space` as read back by ffprobe.
    clip_a = tmp_path / "a_bt709.mp4"
    clip_b = tmp_path / "b_bt2020.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=3",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-g", "1", "-keyint_min", "1", "-sc_threshold", "0",
            "-x264-params", "colormatrix=bt709",
            str(clip_a),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=3",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-g", "1", "-keyint_min", "1", "-sc_threshold", "0",
            "-x264-params", "colormatrix=bt2020nc",
            str(clip_b),
        ],
        check=True,
    )
    assert probe_source_file(str(clip_a)).color_space == "bt709"
    assert probe_source_file(str(clip_b)).color_space != "bt709"

    manifest = EditManifest(
        entries=[
            EditEntry(str(clip_a), 0.0, 3.0, TransitionSpec("fade", 1.0)),
            EditEntry(str(clip_b), 0.0, 3.0, TransitionSpec("cut", 0.0)),
        ]
    )
    output_path = tmp_path / "output.mp4"
    with pytest.raises(RenderError):
        render_edit_manifest(manifest, str(output_path), work_dir=str(tmp_path / "work"))
