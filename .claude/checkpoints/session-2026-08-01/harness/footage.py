"""Pytest plugin: repoint the integration suite's CORPUS_DIR to test its
skip-when-footage-absent behaviour (review-tests question (b)).

FOOTAGE=absent  -- CORPUS_DIR points at a nonexistent path (fresh-clone state).
FOOTAGE=partial -- CORPUS_DIR points at a dir holding ONLY split_003_s66.mp4,
                   simulating a half-copied mirror.
"""

import os
from pathlib import Path


def pytest_configure(config):
    mode = os.environ.get("FOOTAGE", "full")
    if mode == "full":
        return

    from tests.integration import conftest as ic

    if mode == "absent":
        ic.CORPUS_DIR = Path("/nonexistent/data/raw/corpus")
    elif mode == "partial":
        ic.CORPUS_DIR = Path(os.environ["PARTIAL_DIR"])
    else:
        raise SystemExit(f"unknown FOOTAGE={mode!r}")

    print(f"\n[footage] CORPUS_DIR -> {ic.CORPUS_DIR} (mode={mode})")
