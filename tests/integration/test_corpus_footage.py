"""Integration tests against the real corpus footage.

Each test locks in a fact that `data/reference_pack/` established by
independent measurement, so a regression here is detectable rather than silent.
Every asserted number cites the pack leaf it came from.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from drone_video_ai.highlight_extraction.letterbox import detect_active_rect
from drone_video_ai.highlight_extraction.pipeline import PipelineConfig, run_pipeline
from drone_video_ai.highlight_extraction.scoring_exposure import compute_raw_exposure

from .conftest import (
    SPLIT_ACTIVE_RECT,
    SPLIT_FAMILY,
    VERTICAL_ACTIVE_RECT,
    VERTICAL_FAMILY,
    corpus_clip,
)

pytestmark = pytest.mark.integration


def _run(clip: Path, out: Path | None = None, config: PipelineConfig | None = None) -> dict:
    """Run the real pipeline and return its manifest as a plain dict.

    ``run_pipeline`` returns a ``HighlightManifest`` rather than writing a file,
    so serialisation happens here. ``sort_keys=True`` makes the determinism
    comparison depend on manifest CONTENT, not on dict insertion order.

    ``config`` is passed through so a test that depends on the SEGMENT COUNT can
    force it explicitly rather than inheriting whatever the default duration
    profile happens to produce on this footage -- see
    ``test_single_segment_yields_null_rank_but_real_raw_measurement``.
    """
    manifest = run_pipeline(str(clip), config)
    payload = json.dumps(manifest.to_dict(), indent=2, sort_keys=True)
    if out is not None:
        out.write_text(payload)
    return json.loads(payload)


@pytest.mark.parametrize("name", SPLIT_FAMILY)
def test_letterbox_detection_matches_pack_measured_geometry(corpus_dir, name):
    """cropdetect must reproduce the pack's measured active picture exactly.

    Source: editorial_style.json -> letterbox.horizontal_split_family
    .active_picture_px == [1280, 544] and .coded_frame_px == [1280, 720],
    both confidence == "measured"; README.md section 5 records
    `247 crop=1280:544:0:88` for split_003_s66.mp4.
    """
    clip = corpus_clip(name)
    if not clip.is_file():
        pytest.skip(f"{clip} not present")
    rect = detect_active_rect(str(clip))
    assert rect is not None, f"cropdetect found no crop line for {name}"
    assert (rect.width, rect.height, rect.x, rect.y) == SPLIT_ACTIVE_RECT


@pytest.mark.parametrize("name", VERTICAL_FAMILY)
def test_vertical_family_is_not_letterboxed(corpus_dir, name):
    """The 9:16 deliveries carry no bars -- the pack measured
    letterbox.vertical_social_family.applied == false, and README.md section 5
    records `crop=1080:1920:0:0` for instagram_reel_test.mp4. Guards against a
    detector that "finds" letterbox everywhere.
    """
    clip = corpus_clip(name)
    if not clip.is_file():
        pytest.skip(f"{clip} not present")
    rect = detect_active_rect(str(clip))
    assert rect is not None
    assert (rect.width, rect.height, rect.x, rect.y) == VERTICAL_ACTIVE_RECT
    assert rect.is_full_frame


def test_letterbox_is_excluded_from_exposure_scoring(split_clip, tmp_path):
    """Scoring a letterboxed file must match scoring it pre-cropped.

    Before the 2026-07-28 fix, no scorer cropped, and the gap was exactly the
    pack's measured content_cost of 24.4%: exposure 0.7556 letterboxed vs
    1.0000 pre-cropped. The bars code as luma 16 in a color_range=tv stream,
    decode to 0, and fall at or below LOW_CLIP_THRESHOLD == 5, so every bar
    pixel counted as under-exposed.
    """
    rect = detect_active_rect(str(split_clip))
    assert rect is not None

    pre_cropped = tmp_path / "cropped.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(split_clip),
         "-vf", f"crop={rect.width}:{rect.height}:{rect.x}:{rect.y}",
         "-c:v", "libx264", "-crf", "12", str(pre_cropped)],
        check=True,
    )

    letterboxed = compute_raw_exposure(str(split_clip), 0.0, 8.0, active_rect=rect)
    cropped = compute_raw_exposure(str(pre_cropped), 0.0, 8.0)
    assert abs(letterboxed - cropped) < 0.05, (
        f"letterbox not excluded: {letterboxed:.4f} vs {cropped:.4f}"
    )


def test_corpus_file_is_single_shot_with_no_scene_cuts(split_clip, tmp_path):
    """The pack's single most consequential finding, re-tested from the code.

    editorial_style.json -> shot_structure.hard_cut_count_total_corpus == 0 and
    .shot_count_per_file == 1, both measured, via ffmpeg `scdet`. This asserts
    the same conclusion through an INDEPENDENT tool -- PySceneDetect's
    AdaptiveDetector inside the real pipeline -- so agreement is corroboration
    rather than restatement.
    """
    manifest = _run(split_clip, tmp_path / "m.json")
    assert manifest["summary"]["scenes_detected"] == 0
    assert manifest["candidate_boundaries"]["scene_boundaries"] == []


def test_single_segment_yields_null_rank_but_real_raw_measurement(split_clip, tmp_path):
    """A within-file rank is undefined for a lone segment; the absolute
    measurement is not.

    Before the 2026-07-28 fix, min_max_normalize returned [1.0] for ANY single
    value -- [0.02] and [123.4] were indistinguishable -- and 20 of 20
    sharpness/motion values across the 8-file corpus were saturated at 0.0 or
    1.0. Since the pack measured every corpus file to be a single continuous
    shot, that degenerate case is the NORM here, not an edge case.

    The n=1 condition is FORCED here rather than inherited (review-tests P1-T1).
    Under the default profile this clip yields one segment only because
    max_duration == 15.0 exceeds its 8.3 s -- which is audit finding 0,
    "segmentation is inert on 6 of 8 corpus files", an OPEN defect. Measured
    2026-08-01 on split_003_s66.mp4: max_duration 15.0/8.0/5.0/3.0 -> 1/2/2/4
    segments. So inheriting the default made this test fail the moment finding 0
    was fixed, and the failure read as a regression in bc3a499 (the null-rank
    fix) when it was the correct behaviour finally appearing. A duration window
    no boundary set from an 8.3 s clip can satisfy forces the whole file into
    one segment under any boundary-selection strategy, so this test now depends
    on the null-rank contract alone.
    """
    manifest = _run(
        split_clip,
        tmp_path / "m.json",
        PipelineConfig(min_duration=600.0, max_duration=999.0),
    )
    segments = manifest["segments"]
    assert len(segments) == 1, "the forced duration window admits no interior cut"

    scores = segments[0]["scores"]
    assert scores["sharpness"] is None, "rank must be null, not a fabricated 1.0"
    assert scores["motion_smoothness"] is None

    # ...and the absolute measurements survive, so the null costs no information.
    assert scores["sharpness_raw"] is not None and scores["sharpness_raw"] > 0.0
    assert scores["motion_smoothness_raw"] is not None

    # exposure and composition are absolute [0,1] by construction, so they are
    # never nulled by segment count.
    assert isinstance(scores["exposure"], float)
    assert isinstance(scores["composition"], float)


def test_multiple_segments_yield_a_real_rank(split_clip, tmp_path):
    """The companion to the null-rank test: when the file DOES split, the rank
    must be a real number spanning the full [0,1] range.

    This is the n >= 2 path's first integration coverage (review-tests P1-T1).
    Without it the suite only ever exercises the degenerate branch, so a
    regression to "always return None" -- the mirror image of the bug bc3a499
    fixed -- would pass every footage-gated test in this file.

    max_duration is forced small for the same reason the sibling test forces it
    large: the segment count must be a property of this test, not of the default
    profile. Measured 2026-08-01 on split_003_s66.mp4 (8.3 s): a 2-3 s window
    yields 4 segments.
    """
    manifest = _run(
        split_clip,
        tmp_path / "m.json",
        PipelineConfig(min_duration=2.0, max_duration=3.0),
    )
    segments = manifest["segments"]
    assert len(segments) >= 2, "a 2-3s window must split an 8.3s clip"

    for field in ("sharpness", "motion_smoothness"):
        ranks = [s["scores"][field] for s in segments]
        assert all(r is not None for r in ranks), f"{field} rank is null at n>=2: {ranks}"
        assert min(ranks) == 0.0 and max(ranks) == 1.0, (
            f"{field} min-max rank must span [0,1] exactly: {ranks}"
        )


def test_pipeline_is_deterministic(split_clip, tmp_path):
    """Two independent runs must produce byte-identical manifests.

    Guards the whole chain -- cropdetect, sparse optical flow, frame sampling,
    scoring, normalisation -- against any accidental nondeterminism (unseeded
    RNG, dict-ordering, wall-clock in output).
    """
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    _run(split_clip, a)
    _run(split_clip, b)
    sha_a = hashlib.sha256(a.read_bytes()).hexdigest()
    sha_b = hashlib.sha256(b.read_bytes()).hexdigest()
    assert sha_a == sha_b, f"pipeline is nondeterministic: {sha_a} != {sha_b}"
