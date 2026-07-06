"""AC2.5: duration/pacing parameters (target total reel length) must be
honored within a defined tolerance (default +/-0.5s) of the requested total
duration."""

from __future__ import annotations

import pytest

from drone_video_ai.reel_stitching.edit_manifest import EditEntry, EditManifest, TransitionSpec
from drone_video_ai.reel_stitching.pacing import DEFAULT_TOLERANCE, PacingError, apply_target_duration


def _multi_clip_manifest(clip_path: str) -> EditManifest:
    return EditManifest(
        entries=[
            EditEntry(clip_path, 0.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_path, 4.0, 8.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_path, 8.0, 12.0, TransitionSpec("cut", 0.0)),
        ]
    )


def test_paced_manifest_hits_target_within_tolerance(cuttable_clip_factory):
    clip = cuttable_clip_factory(duration=12.5, fps=10, size="160x120")
    manifest = _multi_clip_manifest(str(clip))
    assert manifest.content_duration == pytest.approx(12.0)

    target = 6.0
    paced = apply_target_duration(manifest, target, tolerance=DEFAULT_TOLERANCE)

    assert abs(paced.content_duration - target) <= DEFAULT_TOLERANCE
    # Pacing produces a new, explicit, inspectable manifest -- never applied
    # silently in place.
    assert paced is not manifest
    assert paced.target_duration == target


def test_paced_manifest_with_transition_overlap_hits_target(cuttable_clip_factory):
    """content_duration accounts for transition-window overlap (a crossfade
    shortens the combined timeline), so pacing must trim against that
    effective total, not the naive sum of per-entry durations."""
    clip = cuttable_clip_factory(duration=12.5, fps=10, size="160x120")
    manifest = EditManifest(
        entries=[
            EditEntry(str(clip), 0.0, 4.0, TransitionSpec("fade", 1.0)),
            EditEntry(str(clip), 4.0, 8.0, TransitionSpec("cut", 0.0)),
            EditEntry(str(clip), 8.0, 12.0, TransitionSpec("cut", 0.0)),
        ]
    )
    # 3 entries of 4s each = 12s, minus 1s transition overlap = 11s content.
    assert manifest.content_duration == pytest.approx(11.0)

    target = 6.0
    paced = apply_target_duration(manifest, target, tolerance=DEFAULT_TOLERANCE)
    assert abs(paced.content_duration - target) <= DEFAULT_TOLERANCE


def test_already_within_tolerance_is_returned_unchanged_in_duration(cuttable_clip_factory):
    clip = cuttable_clip_factory(duration=12.5, fps=10, size="160x120")
    manifest = _multi_clip_manifest(str(clip))
    target = manifest.content_duration + 0.1  # well within +/-0.5s tolerance
    paced = apply_target_duration(manifest, target, tolerance=DEFAULT_TOLERANCE)
    assert paced.content_duration == pytest.approx(manifest.content_duration)


def test_none_target_duration_leaves_manifest_as_is(cuttable_clip_factory):
    clip = cuttable_clip_factory(duration=12.5, fps=10, size="160x120")
    manifest = _multi_clip_manifest(str(clip))
    paced = apply_target_duration(manifest, None)
    assert paced.content_duration == pytest.approx(manifest.content_duration)


def test_unreachable_target_raises_pacing_error(cuttable_clip_factory):
    clip = cuttable_clip_factory(duration=12.5, fps=10, size="160x120")
    manifest = _multi_clip_manifest(str(clip))
    # A near-zero target well outside a sane shrink range for 3 clips.
    with pytest.raises(PacingError):
        apply_target_duration(manifest, 0.05, tolerance=DEFAULT_TOLERANCE)
