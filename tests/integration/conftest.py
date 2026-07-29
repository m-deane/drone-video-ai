"""Fixtures for the `integration` suite -- the only tests in this repo that run
against REAL drone footage rather than synthetic ffmpeg/cv2 fixtures.

`pyproject.toml` has declared the `integration` marker since Milestone 1
("slower tests that use real `data/raw/` sample footage") and, until
2026-07-28, **no test used it**. Every one of the 93 tests was a unit test over
synthetic fixtures, so the pipeline had never been exercised against the footage
this project actually measures.

`data/raw/` is gitignored (`.gitignore`: a convenience mirror of the read-only
`00-assets/drone-video-examples/` tree, ~3.7 GB, never committed). A clean
checkout therefore does NOT have it, and every test here must skip rather than
fail in that case -- otherwise CI on a fresh clone goes red for a reason that
has nothing to do with the code.

These tests are the regression guard for facts established by
`data/reference_pack/`, which measured this same footage independently with
ffprobe/ffmpeg + stdlib Python only. Where a test asserts a number, that number
comes from the pack, and the citation is in the test body. If one of these
fails, either the code regressed or the pack is wrong -- both worth knowing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "data" / "raw" / "corpus"

# The four members of what data/reference_pack/ calls the "horizontal split
# family": derivative clips carrying BAKED-IN letterbox bars. Measured active
# picture 1280x544 inside a 1280x720 coded frame, bars at rows 0-87 and 632-719.
SPLIT_FAMILY = ["split_001_s70", "split_002_s69", "split_003_s66", "split_004_s65"]

# The "vertical social family": 9:16 deliveries with NO letterbox.
VERTICAL_FAMILY = ["instagram_reel_test", "viral_test_v2"]

# Measured active-picture geometry, from editorial_style.json ->
# letterbox.horizontal_split_family.{active_picture_px, coded_frame_px},
# both confidence == "measured".
SPLIT_ACTIVE_RECT = (1280, 544, 0, 88)
VERTICAL_ACTIVE_RECT = (1080, 1920, 0, 0)

# The shortest split, used wherever a test needs a full pipeline run and does
# not care which file: 8.3 s, versus 15.0 s for the other three.
FASTEST_SPLIT = "split_003_s66"


def corpus_clip(name: str) -> Path:
    return CORPUS_DIR / f"{name}.mp4"


@pytest.fixture(scope="session")
def corpus_dir() -> Path:
    """Skip the whole integration suite when the gitignored footage mirror is
    absent, which is the normal state of a fresh clone."""
    if not CORPUS_DIR.is_dir():
        pytest.skip(
            f"real corpus footage not present at {CORPUS_DIR} "
            "(data/raw/ is gitignored; re-copy from 00-assets/drone-video-examples/)"
        )
    return CORPUS_DIR


@pytest.fixture(scope="session")
def split_clip(corpus_dir: Path) -> Path:
    p = corpus_clip(FASTEST_SPLIT)
    if not p.is_file():
        pytest.skip(f"{p} not present")
    return p
