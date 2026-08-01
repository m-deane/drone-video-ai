# Post-move verification + P1-T1/P1-T2/P2-T3 fixes — 2026-08-01 (evening)

Continuation of `SESSION-SUMMARY.md` (same day, earlier). Two things happened at once, and
the order matters for reading the numbers below.

## 0. The move happened mid-session, unannounced from this side

Work started against `/Users/mac/Documents/photography-WORKFLOW-local/04-drone-video-editing-ai`.
Three test-file edits (the P1-T1/P1-T2/P2-T3 fixes) were written there, and a `pytest -m
integration` run was in flight when the run died with:

```
FileNotFoundError: [Errno 2] No such file or directory:
  '/Users/mac/Documents/photography-WORKFLOW-local/04-drone-video-editing-ai'
```

The directory had been moved out from under the running process. Located immediately at
`/Volumes/Phone SSD/photography-WORKFLOW-local/04-drone-video-editing-ai`; not in `~/.Trash`.
The **whole `photography-WORKFLOW-local/` tree** moved, siblings included — the lowest-risk
option `MOVE-READINESS.md` §3 recommends.

The in-flight edits did **not** travel: the SSD copy was clean at `7bc7019` with the
pre-edit files. They were re-applied to the SSD tree from the session transcript and are the
basis of everything below. Worth internalising: **an editor or agent holding uncommitted
work in a tree that is being moved loses it silently** — the destination looks clean and
consistent, which is exactly what makes it easy to miss.

## 1. Post-move verification, in `MOVE-READINESS.md`'s prescribed order

| Step | Result |
|---|---|
| `ffprobe -version` | 8.1.2, healthy — no `dyld` breakage |
| Payloads present | `00-WORKING` 112 G, `data/raw` 3.7 G (8/8 clips), `data/output` 167 M, `.claude/transcripts` 6.9 M |
| Siblings present | `00-assets/drone-video-examples/` and `_archive/` both moved too |
| `.venv/` shebang | **broke exactly as predicted** — `#!/Users/mac/Documents/…/.venv/bin/python3` |
| venv rebuild | `uv venv --python 3.12 --clear .venv && VIRTUAL_ENV=.venv uv pip install -e ".[dev]"` → CPython 3.12.13, clean |
| opencv conflict | **reproduced again** — the project install pulled `opencv-python` 5.0.0.93 alongside `opencv-contrib-python` 5.0.0.93 |
| `cv2.saliency.StaticSaliencySpectralResidual_create()` | OK **before** the fix (install order happened to favour contrib) and OK after |
| Full suite | **`106 passed in 115.02s`** |
| `git status` | clean at `7bc7019` before the fixes below |

Two notes on that table.

**The opencv fix was applied anyway, deliberately.** The concrete factory already worked, so
this was not remediation — it was to leave the environment in the *deterministic* state
`pyproject.toml` pins (contrib only, `uv pip uninstall opencv-python opencv-contrib-python`
then `uv pip install --reinstall --no-deps "opencv-contrib-python>=4.8"`), rather than in a
state that happens to work because of install ordering this project does not control. Factory
re-verified after; `numpy` 2.5.1 survived, per CLAUDE.md's warning about `--no-deps`.

**The SSD is measurably slower and it changes what "cheap" means here.** The integration
suite ran 39.25 s on the internal disk this morning and **114.60 s** on the SSD tonight
(11 tests vs 10). The `letterbox` mutant run — which disables cropping, so every scorer sees
full frames — took **408.94 s**. Not a controlled benchmark (fresh venv, cold cache), but the
direction is not in doubt, and CLAUDE.md's 3.7–8.1x-realtime 4K figure should be treated as a
floor from now on, not a bound.

## 2. Fixes applied — review-tests P1-T1, P1-T2, P2-T3

All three are test-only. **`src/` was not modified.**

### P1-T1 — the null-rank test no longer depends on an open defect

`tests/integration/test_corpus_footage.py`. The test asserted `len(segments) == 1`, which
held only because `max_duration = 15.0` exceeds the clip's 8.3 s — audit finding 0, still
open. Fixing finding 0 would have broken three assertions and read as a regression in
`bc3a499`.

`_run` now takes a `PipelineConfig`, and the test forces its own condition with
`min_duration=600.0, max_duration=999.0`. That is stronger than the review's recommended
`max_duration=999.0` alone: a large max only guarantees one segment under the *current*
greedy "farthest boundary within max" rule in `segmentation.py:135` — the rule finding 0 is
most likely to change — whereas a window no boundary set from an 8.3 s clip can satisfy
forces the whole file into one segment under any selection rule. `split_segments` reaches it
via its documented `meets_min` fallback, and no gate filters on duration, so the segment
survives into the manifest.

New companion `test_multiple_segments_yield_a_real_rank` gives the n≥2 path its first
integration coverage: a 2–3 s window on the same clip, asserting both ranks are non-null and
that `min == 0.0` and `max == 1.0` exactly. That last assertion is the one that would catch
the mirror-image regression — "always return `None`" — which every other footage-gated test
in the file would pass.

### P1-T2 — a partial footage mirror no longer reports green

`tests/integration/conftest.py`. `corpus_dir` now requires every member of `SPLIT_FAMILY +
VERTICAL_FAMILY` when the directory exists, and skips the whole suite naming what is missing.
The fresh-clone path is untouched. Re-measured with the preserved harness:

| `FOOTAGE` | Before | After |
|---|---|---|
| `absent` | 10 skipped, exit 0 | 11 skipped, exit 0 — unchanged behaviour |
| `partial` (1 of 6) | **5 passed, 5 skipped, exit 0** | **11 skipped, exit 0**, naming all 5 missing clips |

This was the finding most directly relevant to the move, and it is now fixed on the far side
of one.

### P2-T3 — the `n < 2` branch has unit coverage

`tests/highlight_extraction/test_scoring_sharpness.py`,
`tests/highlight_extraction/test_scoring_motion_smoothness.py`. The branch `bc3a499` exists
for had no unit test — only integration coverage, which skips without the gitignored mirror,
so a fresh clone was green with the headline behaviour never executed. Each new test asserts
two different magnitudes (`[0.02]`/`[123.4]`, `[3.0]`/`[987.6]`) rather than one, because the
point is that the old code made them *indistinguishable*, not that any particular value maps
to `None`.

## 3. The guards were re-proved, not assumed

The preserved mutation harness (`harness/mutants.py`, committed in `7bc7019` precisely so
these findings stay re-checkable) was re-run after the changes:

| `MUTANT` | Result | Failure |
|---|---|---|
| `letterbox` | 1 failed, 10 passed | `letterbox not excluded: 0.7556 vs 1.0000`, delta `0.24444315933124017` |
| `rank` | 1 failed, 10 passed | `assert 1.0 is None` at `test_corpus_footage.py:156` |

Both still fail **exactly one** test — so P2-T5's "no redundancy" finding stands unchanged —
and the letterbox delta still reproduces the pack's measured 24.4% `content_cost` to five
decimals. The `rank` mutant's line moved `:135` → `:156`, which `harness/README.md` predicted
in writing before the fix existed.

## 3a. Audit finding 0 — fixed, in a second commit

With P1-T1 out of the way, finding 0 was fixed the same session. Full record in `CLAUDE.md` →
"Finding 0, closed (2026-08-01)"; the short version:

`split_segments` now takes the **nearest** boundary at least `min_duration` away instead of
the farthest one within `max_duration`, plus a tail-fold for a sub-`min_duration` remainder.
`DEFAULT_DURATION_PROFILE` is untouched — spec AC1.4's 2–15 s window was never the problem,
the selection rule was.

Measured first, on all six corpus clips, by computing the real union-boundary sets and
evaluating both rules over them: old rule → **1 segment on 5 of 6 clips** (2 on the 27.1 s
one); new rule → 4–12 segments, every one inside `[2.0, 15.0]`. Zero scene boundaries in any
clip — every boundary is a motion minimum, which reproduces the pack's zero-hard-cuts finding a
third time through a third tool (`AdaptiveDetector`).

The rule is **policy, not measurement**, and both the docstring and CLAUDE.md say so: motion
minima are 1–1.5 s apart, so inside a 2–15 s window any rule picks a length the footage does
not determine. The pack measured no cut rhythm that would justify a target in between, and
inventing one is precisely what the Constitution forbids. Nearest-legal wins on the only
available ground — it is the one that lets the capability function.

`drone-highlights` on `split_003_s66.mp4` with stock defaults now emits 4 ranked segments,
composite `0.9521 / 0.7846 / 0.6363 / 0.4923`. That is the first real highlight ranking this
corpus has produced. `exposure` is 1.0000 on all four, so 3 of 4 signals discriminate —
the open question `d1013a8` raised, not a segmentation defect.

Verification: **109 passed** (98 unit + 11 integration). Three new unit tests guard the
defect itself — the collapse case, the tail fold, and the case where folding would break
`max_duration`. Both mutants re-run after the change and still fail **exactly one** test each
(`letterbox` 1F/10P, `rank` 1F/10P), so the guards survived a change to the code they guard.

**The P1-T1 fix paid for itself immediately**: fixing segmentation broke nothing, where before
it would have failed three assertions in the null-rank test and looked like a regression in
`bc3a499`.

## 4. Left open — unchanged from `SESSION-SUMMARY.md` §5 except where noted

1. ~~Push to the public `origin`~~ — **done, outside this session.** Verified against the
   real remote, not the tracking ref: `git ls-remote origin refs/heads/main` returns
   `7bc7019a1304cf600abae348ab68883e108d1be0`, identical to local `main`. So `d9e2730`,
   `329e268` and `7bc7019` are all public on `github.com/m-deane/drone-video-ai`. Note that a
   second remote, `old-origin`, now points at that same URL — a rename that left both names
   in place. This session's commit is again unpushed and again needs its own yes.
2. ~~P1-T1 before audit finding 0~~ — **done, and finding 0 itself is now fixed too.** See
   §3a above.
3. **Act on the three completed reviews** — unchanged. 9 findings in review-normalization
   (P1-A `composite_score` silently switching estimator, P1-B `motion_smoothness_raw` holding
   *jerk* with inverted polarity), 10 in review-letterbox, plus `design-batch.md`.
   review-tests P2-T4 (zero unit coverage of `letterbox.py`) and P2-T5 (composition effect
   unguarded) remain open.
4. **Audit findings 3, 4, 5** — unchanged, design decisions.
5. **`04a-drone-video-highlights-ai/`** — no longer merely a stray copy: as of 2026-08-01
   13:58 it has its own initial commit and its own **public** remote,
   `github.com/m-deane/04a-drone-video-highlights-ai`, already pushed. It still contains only
   the `.claude/` scaffold and a `CLAUDE.md` describing *this* repo — no `src/`, no `data/`.
   Whether it becomes a real split of Capability 1 is still undecided.
6. **Inherited claude-template root files** — unchanged, undecided.
7. **Memory** — orphaned by the move exactly as predicted, and now **reinstated**: this
   repo's two memory files were copied into the new path-derived slug
   `~/.claude/projects/-Volumes-Phone-SSD-photography-WORKFLOW-local-04-drone-video-editing-ai/memory/`,
   plus a new `repo-lives-on-phone-ssd.md` recording the move, the stale absolute paths, the
   SSD's speed cost, and the lost-uncommitted-work lesson from §0. **Transcripts** are still
   vendored at `.claude/transcripts/` and were not re-copied; the two sessions since that
   snapshot (`5c999851` post-13:49, and this one) are not in it.
