# Test Review — integration suite + two rewritten unit tests

STATUS: COMPLETE. Skeleton written 2026-07-29 07:35; the agent stalled before writing
findings. Completed 2026-08-01 in-session by the orchestrator, not re-dispatched.

Scope:
- `tests/integration/conftest.py`
- `tests/integration/test_corpus_footage.py`
- `tests/highlight_extraction/test_scoring_sharpness.py` (changed in `bc3a499`)
- `tests/highlight_extraction/test_scoring_motion_smoothness.py` (changed in `bc3a499`)

## Verdict in one line

The integration suite is **not vacuous** — both fixes it claims to guard were reverted at
runtime and both were caught — but it is **fragile in one specific way that matters**: its
central test hard-codes an *unfixed* defect as a precondition, so fixing audit finding 0
will make it fail, and a half-copied footage mirror reports green.

## Answers to the four questions asked

### (a) Do the integration tests fail if the fixes are reverted, or pass vacuously? — **THEY FAIL. Not vacuous.**

Tested by mutation, not by reading. Each fix was reverted at *runtime* via a pytest plugin
(`pytest_configure` monkeypatch), leaving `src/` untouched, and the suite re-run:

| Mutant | What it reverts | Result |
|---|---|---|
| `letterbox` | `ActiveRect.crop` → identity, i.e. the exact pre-`0644fb7` state (detection works, no scorer crops) | **1 failed, 9 passed** |
| `rank` | `min_max_normalize` / `invert_and_normalize` → return `1.0` in both degenerate branches (pre-`bc3a499`) | **1 failed, 9 passed** |

The `letterbox` mutant failed with:

```
AssertionError: letterbox not excluded: 0.7556 vs 1.0000
assert 0.24444315933124017 < 0.05
```

`0.24444` reproduces the pack's measured `content_cost` of 24.4% to five decimal places,
from a completely different direction — the test recovers the pack's own number when the
fix is removed. That is the strongest possible evidence the guard is real.

The `rank` mutant failed with `assert 1.0 is None` at `test_corpus_footage.py:135`.

**Caveat that limits this result:** each fix is guarded by *exactly one* test. There is no
redundancy — one deleted or `xfail`ed test silently removes the entire guard for that fix.

### (b) Is the skip-when-footage-absent path correct? Does it mask failure? — **CORRECT for a fresh clone; MASKS FAILURE for a partial mirror.**

Both paths were exercised by repointing `CORPUS_DIR` via a plugin.

**Fresh clone (directory absent) — correct.** `10 skipped, 93 deselected in 0.29s`, exit 0,
every skip carrying the actionable message `re-copy from 00-assets/drone-video-examples/`.
This is the right design: `data/raw/` is gitignored, and failing here would redden CI for a
reason unrelated to the code. No complaint.

**Partial mirror — masks failure.** With only `split_003_s66.mp4` present:

```
5 passed, 5 skipped, 93 deselected in 51.23s     (exit 0)
```

Green. And the five that skipped include **both** `test_vertical_family_is_not_letterboxed`
cases — the suite's only guard against "a detector that finds letterbox everywhere", in that
test's own words. The false-positive guard vanished and nothing said so.

The cause is a state gap: `conftest.py:59` checks only that the *directory* exists, and
`conftest.py:70` / `test_corpus_footage.py:56,71` then skip file-by-file. "Absent" and
"present but incomplete" are different conditions and only the first is handled.

### (c) Were the two rewritten unit tests defensible, or did they destroy a contract? — **DEFENSIBLE. No contract destroyed.**

Both changed tests asserted the fabricating behaviour (`[1.0, 1.0, 1.0]` and `[1.0, 1.0]`)
in the `max == min` branch. They encoded the bug, so changing them was correct, and both
carry an in-body comment explaining why — the right idiom for a test whose expectation
legitimately inverts.

The surviving contract was checked explicitly, not assumed. The real ranking behaviour is
still guarded by `test_scoring_sharpness.py:25-29` (`[10,50,100]` → `0.0 < mid < 1.0`, ends
exactly `0.0`/`1.0`) and `test_scoring_motion_smoothness.py:43-45` (n=2 → `1.0`/`0.0`). A
regression to "always return `None`" would fail both. The empty-list contract is still held
at `:41` and `:54`. Nothing was weakened.

**But the rewrite covered the wrong degenerate branch.** See P2-T3 — the branch these tests
now exercise (`max == min`) is not the one `bc3a499` was written for.

### (d) Assertions that break on legitimately different footage — **ONE SERIOUS, and it breaks on a *fix*, not on footage.**

The serious one is P1-T1 below: the test breaks the moment someone fixes an open finding in
this same repo. The remainder are intentional pack-regression assertions (exact
`SPLIT_ACTIVE_RECT` equality etc.) that are *supposed* to be footage-specific — they are the
point of the suite, not a defect, and the suite skips rather than fails when the footage is
absent.

One assertion I expected to be marginal is not: `abs(letterboxed - cropped) < 0.05`
(`:101`) compares an in-place crop against a **lossy libx264 CRF-12 re-encode**, which
sounds tolerance-sensitive. Measured:

```
exposure  cropped-in-place=0.999999  pre-cropped-reencode=0.999998  |delta|=0.000001
```

The tolerance has **~49,700x headroom** on the passing side and sits 2.4x below the failing
value (0.2444). Well chosen; leave it alone.

## 1. Findings

### P1-T1 — `test_single_segment_yields_null_rank_but_real_raw_measurement` hard-codes an OPEN defect as its precondition

`tests/integration/test_corpus_footage.py:132,135,136`

```python
assert len(segments) == 1, "pack measured this file as one continuous shot"
...
assert scores["sharpness"] is None, "rank must be null, not a fabricated 1.0"
assert scores["motion_smoothness"] is None
```

`len(segments) == 1` is true *only* because `DEFAULT_DURATION_PROFILE.max_duration = 15.0`
exceeds this clip's 8.3 s, which is audit **finding 0 — "segmentation is inert on 6 of 8
corpus files"**, still open. Measured on `split_003_s66.mp4` via `PipelineConfig`:

| `max_duration` | segments | `sharpness` | `motion_smoothness` |
|---|---|---|---|
| 15.0 (default) | 1 | `None` | `None` |
| 8.0 | 2 | 1.0 | 1.0 |
| 5.0 | 2 | 1.0 | 1.0 |
| 3.0 | 4 | 1.0 | 1.0 |

So lowering the cap — the natural fix for finding 0 — breaks all three assertions at once,
and the failure *reads* like a regression in `bc3a499` when it is in fact the correct
behaviour finally appearing. The test conflates two independent facts: "the pack measured
this file as one continuous shot" (a footage fact, true) and "the pipeline emits one
segment" (a configuration artefact, an open defect).

**Fix:** force the n=1 condition explicitly rather than inheriting it —
`run_pipeline(clip, PipelineConfig(max_duration=999.0))` — and add a companion case with a
small cap asserting a *real* rank appears (`sharpness is not None`), which would also give
the n≥2 path its first integration coverage.

### P1-T2 — a partially-populated `data/raw/corpus/` reports green

`tests/integration/conftest.py:55-72`, `test_corpus_footage.py:56-57,71-72`

Measured above: 5 passed / 5 skipped / exit 0 with 1 of 6 clips present, silently dropping
the vertical-family false-positive guard. `data/raw/` is a hand-maintained gitignored mirror
("regenerate/re-copy" per CLAUDE.md), so partial population is a realistic state, not a
contrived one.

**Fix:** in the `corpus_dir` fixture, when the directory exists, require every member of
`SPLIT_FAMILY + VERTICAL_FAMILY`; skip the whole suite with an explicit "incomplete mirror"
message otherwise. Keep the fresh-clone path exactly as it is.

### P2-T3 — the `n < 2` branch — the case `bc3a499` exists for — has NO unit test

`tests/highlight_extraction/test_scoring_sharpness.py`,
`tests/highlight_extraction/test_scoring_motion_smoothness.py`

`min_max_normalize` has two degenerate branches (`scoring_sharpness.py:89` `n < 2`, and
`:92` `max == min`). Grep of every call site in the unit suite:

```
min_max_normalize([10.0, 50.0, 100.0])   n=3, non-degenerate
min_max_normalize([5.0, 5.0, 5.0])       n=3, max == min
min_max_normalize([])                     n=0
invert_and_normalize([smooth, jitter])    n=2, non-degenerate
invert_and_normalize([3.0, 3.0])          n=2, max == min
invert_and_normalize([])                  n=0
```

**No unit test anywhere passes a single-element list.** Yet `n < 2` is the branch the commit
message is entirely about ("`min_max_normalize([0.02])` and `min_max_normalize([123.4])`
both returned `[1.0]`"), and the pack measured it to be the norm on this corpus, not an edge
case. It is covered *only* by the integration test — which skips without footage. On a fresh
clone `pytest` is green with the headline behaviour of `bc3a499` never executed.

Corroborates review-normalization P3-I and localises it: add `min_max_normalize([5.0]) ==
[None]` and `invert_and_normalize([3.0]) == [None]`. Two lines, no footage required.

### P2-T4 — `letterbox.py` has zero unit coverage; the module is footage-gated entirely

Grep for `letterbox|ActiveRect|active_rect` across `tests/` excluding `tests/integration/`
returns **nothing**. Confirms review-letterbox P2-4 by measurement. The consequence worth
naming: `ActiveRect.crop` (`letterbox.py:73-78`) is pure slice arithmetic that its own
docstring warns "would silently mis-slice" on a mismatched frame — testable with a 3-line
NumPy array and no video at all — and it is exercised only when the gitignored mirror exists.

### P2-T5 — the letterbox fix's effect on `composition` is unguarded

`letterbox.py:23` records that the fix moved composition by **+0.0336** ("the bar edge is a
full-width, high-contrast horizontal line — a perfect false horizon"), but no test in the
repo asserts a composition value against the pack. Only exposure is guarded
(`test_corpus_footage.py:99-103`). Measured now on `split_003_s66`:

```
composition  cropped-in-place=0.851340  pre-cropped-reencode=0.851166  |delta|=0.000174
```

A regression that reintroduced the bars into composition scoring only — e.g. dropping
`active_rect` from the `compute_raw_composition` call at `pipeline.py:121` — passes the
entire suite. The `letterbox` mutant above demonstrates this: it failed exactly one test,
via exposure, despite disabling cropping for *every* scorer.

### P3-T6 — the corpus mirror is an unverified copy

The suite asserts pack-measured numbers against `data/raw/corpus/`, a convenience copy,
while the authoritative tree is the read-only `00-assets/drone-video-examples/`. Nothing
checks they agree. Verified today — all six clips are byte-identical by sha256, so this is
currently clean, not a live bug. But a re-encoded or drifted mirror would move every
measured number with no test noticing, and CLAUDE.md already maintains the sha256 baseline
the fixture would need.

### P3-T7 — `"ffmpeg"` hard-coded in the test body

`test_corpus_footage.py:93` calls bare `"ffmpeg"`. Same defect class as review-letterbox
P2-3 (`pipeline.py:86` ignoring `cfg.ffmpeg_bin`). With ffmpeg off PATH this errors rather
than skipping — and CLAUDE.md documents a real `dyld` breakage of exactly this toolchain.

### P3-T8 — the `integration` marker is declared but never deselected

`pyproject.toml [tool.pytest.ini_options]` sets `testpaths` and the marker but no `addopts`,
so a plain `pytest` runs the integration suite too. Cheap here (39.25 s) but the design doc
targets 4 K masters at 3.7–8.1x realtime. There is no CI, so this suite fires only when
someone remembers `-m integration`. Worth one documented command rather than a code change.

## 2. Per-test regression-guard analysis

| Test | Guards | Proven non-vacuous | Note |
|---|---|---|---|
| `test_letterbox_detection_matches_pack_measured_geometry` (×4) | pack's `1280x544+0+88` | not mutation-tested (asserts detection, which neither mutant breaks) | exact-equality by design |
| `test_vertical_family_is_not_letterboxed` (×2) | detector false positives | — | **silently skipped on a partial mirror** (P1-T2) |
| `test_letterbox_is_excluded_from_exposure_scoring` | `0644fb7` | **YES** — recovers 0.24444 | sole guard for the whole fix (P2-T5) |
| `test_corpus_file_is_single_shot_with_no_scene_cuts` | pack's zero-hard-cuts finding, via an independent tool | — | genuine corroboration, not restatement |
| `test_single_segment_yields_null_rank_but_real_raw_measurement` | `bc3a499` | **YES** — `assert 1.0 is None` | **breaks when finding 0 is fixed** (P1-T1) |
| `test_pipeline_is_deterministic` | whole chain | — | passes; 14.15 s, the slowest test |

## 3. Recommended order of work

1. **P1-T1** — decouple from `max_duration`. Do this *before* touching finding 0, or the
   segmentation fix will look like it broke the normalisation fix.
2. **P1-T2** — completeness check in `corpus_dir`.
3. **P2-T3** — two one-line unit tests. Cheapest real coverage gain in the repo.
4. **P2-T5**, **P2-T4**, then the P3s.

## 4. Verification performed

All results below are tool output from this session, not inspection.

- `pytest -q -m integration` baseline: **`10 passed, 93 deselected in 39.25s`**.
- Mutation runs via a `pytest_configure` plugin on `PYTHONPATH` (`src/` never modified):
  `MUTANT=letterbox` → 1 failed / 9 passed; `MUTANT=rank` → 1 failed / 9 passed.
- Skip-path runs via a plugin repointing `CORPUS_DIR`: `FOOTAGE=absent` → 10 skipped, exit 0,
  0.29 s; `FOOTAGE=partial` (1 of 6 clips) → 5 passed / 5 skipped, exit 0.
- Segmentation coupling: `run_pipeline` with `PipelineConfig(max_duration=…)` at 15.0 / 8.0 /
  5.0 / 3.0 → 1 / 2 / 2 / 4 segments, `sharpness` `None` / 1.0 / 1.0 / 1.0.
- Tolerance headroom: `compute_raw_exposure` in-place-crop vs pre-cropped re-encode,
  `|delta| = 0.000001` against a 0.05 tolerance; composition `|delta| = 0.000174`.
- `ffprobe` durations confirm `FASTEST_SPLIT = split_003_s66` at **8.300000 s** vs 15.0 for
  the other three — `conftest.py:47`'s comment is exactly right.
- `shasum -a 256`: all 6 clips in `data/raw/corpus/` byte-identical to
  `00-assets/drone-video-examples/`.
- Coverage greps over `tests/` excluding `tests/integration/`: no `letterbox|ActiveRect|
  active_rect` reference; no single-element normalize call; no `sharpness_raw` assertion.

**Limits of this review.** Mutation testing covered two mutants, both targeted at the two
2026-07-28 fixes; it is not a general mutation-coverage score. The unit suite outside the two
changed files was not reviewed — out of scope. No test was run against 4 K footage or against
`00-WORKING/` working footage; all timings are the 720p corpus.
