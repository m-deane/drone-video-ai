"""Pytest plugin that reverts one 2026-07-28 fix at RUNTIME, without touching src/.

Purpose: answer review-tests question (a) -- do the integration tests actually
fail when the fix they claim to guard is reverted, or do they pass vacuously?

Select with MUTANT=letterbox | rank | none.

  letterbox -- ActiveRect.crop becomes a no-op. Detection still works, but no
               scorer sees the cropped frame. This is the exact pre-0644fb7
               state: "every pack measurement used crop=1280:544:0:88; no
               scorer cropped at all."
  rank      -- min_max_normalize / invert_and_normalize return 1.0 in both
               degenerate branches (n < 2, max == min), i.e. the pre-bc3a499
               fabricating behaviour. Patched on the pipeline module too,
               because pipeline.py imports the names directly.
"""

import os


def pytest_configure(config):
    mutant = os.environ.get("MUTANT", "none")
    if mutant == "none":
        return

    if mutant == "letterbox":
        from drone_video_ai.highlight_extraction import letterbox

        letterbox.ActiveRect.crop = lambda self, frame: frame

    elif mutant == "rank":
        from drone_video_ai.highlight_extraction import pipeline
        from drone_video_ai.highlight_extraction import scoring_sharpness as ss
        from drone_video_ai.highlight_extraction import scoring_motion_smoothness as sm

        def old_min_max_normalize(raw_values):
            if not raw_values:
                return []
            lo, hi = min(raw_values), max(raw_values)
            if hi - lo <= 0.0:
                return [1.0] * len(raw_values)
            return [(v - lo) / (hi - lo) for v in raw_values]

        def old_invert_and_normalize(raw_jerk_values):
            if not raw_jerk_values:
                return []
            inverted = [-v for v in raw_jerk_values]
            lo, hi = min(inverted), max(inverted)
            if hi - lo < 1e-9:
                return [1.0] * len(inverted)
            return [(v - lo) / (hi - lo) for v in inverted]

        ss.min_max_normalize = old_min_max_normalize
        sm.invert_and_normalize = old_invert_and_normalize
        pipeline.min_max_normalize = old_min_max_normalize
        pipeline.invert_and_normalize = old_invert_and_normalize

    else:
        raise SystemExit(f"unknown MUTANT={mutant!r}")

    print(f"\n[mutants] ACTIVE MUTANT: {mutant}")
