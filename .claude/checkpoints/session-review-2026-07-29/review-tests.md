# Test Review — integration suite + two rewritten unit tests

STATUS: IN PROGRESS (skeleton written first per anti-stall protocol)

Scope:
- tests/integration/conftest.py
- tests/integration/test_corpus_footage.py
- tests/highlight_extraction/test_scoring_sharpness.py (changed)
- tests/highlight_extraction/test_scoring_motion_smoothness.py (changed)

Questions:
(a) do integration tests fail if fixes reverted, or pass vacuously?
(b) skip-when-footage-absent path — correct? does it mask failure?
(c) were the two rewritten unit tests defensible, or did they destroy a contract?
(d) assertions that break on legitimately different footage

## 1. Findings
TBD

## 2. Per-test regression-guard analysis
TBD

## 3. Verdict
TBD
