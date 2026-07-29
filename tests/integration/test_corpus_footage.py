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
from drone_video_ai.highlight_extraction.pipeline import run_pipeline
from drone_video_ai.highlight_extraction.scoring_exposure import compute_raw_exposure

from .conftest import (
    SPLIT_ACTIVE_RECT,
    SPLIT_FAMILY,
    VERTICAL_ACTIVE_RECT,
    VERTICAL_FAMILY,
    corpus_clip,
)

pytestmark = pytest.mark.integration


def _run(clip: Path, out: Path | None = None) -> dict:
    """Run the real pipeline and return its manifest as a plain dict.

    ``run_pipeline`` returns a ``HighlightManifest`` rather than writing a file,
    so serialisation happens here. ``sort_keys=True`` makes the determinism
    comparison depend on manifest CONTENT, not on dict insertion order.
    """
    manifest = run_pipeline(str(clip))
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
    """
    manifest = _run(split_clip, tmp_path / "m.json")
    segments = manifest["segments"]
    assert len(segments) == 1, "pack measured this file as one continuous shot"

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
