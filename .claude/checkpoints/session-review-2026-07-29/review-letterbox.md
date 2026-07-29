# Review: letterbox exclusion (commit 0644fb7) — IN PROGRESS

Status: skeleton written, review underway.

## Scope
- src/drone_video_ai/highlight_extraction/letterbox.py
- pipeline.py threading of active_rect into motion.py + scoring_*.py

## Questions
(a) ActiveRect.crop bounds check
(b) detect_active_rect 5s modal sampling
(c) crop applied to every scorer?
(d) per-video vs per-segment rect

## Findings
TBD

## Test run
TBD
