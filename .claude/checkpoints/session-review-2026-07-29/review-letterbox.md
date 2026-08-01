# Review: letterbox exclusion (commit 0644fb7)

Reviewer: subagent, 2026-07-29. Read-only; nothing under `src/` or `tests/` was modified.

**Unit suite re-run this session:** `.venv/bin/python -m pytest -q -m "not integration"` →
**93 passed, 10 deselected in 178.55s**. The integration suite was NOT run (it re-encodes corpus
footage; out of scope for this review and the 4K members would breach the no-4K constraint).

**Verdict:** the fix is real, the mechanism is correctly identified, and the threading of
`active_rect` through the four scorers and `motion.py` is complete and consistent. The defects
below are (1) an unconditional new per-file cost that is measured-prohibitive on this project's
actual working footage, (2) an aggregation rule whose stated rationale is inverted with respect to
`cropdetect`'s own accumulate semantics, and (3) three measurement paths the crop was not extended
to. Nothing here is a crash; every defect is silent, which is what makes them worth fixing.

---

## Direct answers to the four questions asked

**(a) `ActiveRect.crop` raw slice, no bounds check — reachable?**
Not through any call path that exists today. Demonstrated silent behaviour (run this session):

```
ActiveRect(1280,544,0,88).crop(np.zeros((240,320)))  -> shape (152, 320)   no exception
ActiveRect(1280,544,0,88).crop(np.zeros((88,1280)))  -> shape (0, 1280)    no exception
```

NumPy clips out-of-range slices rather than raising, so a mismatch produces a wrong region or a
zero-pixel frame, never an error. Reachability: within `run_pipeline` the rect and every cropped
frame derive from the same `video_path`; there is no resize/scale step in `motion.py` or any
`scoring_*.py`; and no file in `data/raw/corpus/` carries a rotation side-data entry (checked with
`ffprobe -show_entries stream_side_data=rotation` this session), so the one plausible mechanism —
ffmpeg auto-rotating where OpenCV does not — is not reachable on this material. Filed P3 (silent,
2-line guard), not dropped, because the failure mode is invisible rather than loud. See P3-1.

**(b) 5-second probe + modal value on a fade or dark opening — sound?**
No, and the docstring's stated reason is backwards. `reset=0` makes `cropdetect` report a *running
maximum* (largest non-black area seen so far), so its per-frame output is a monotone accumulator,
not a set of independent estimates. An early dark period is therefore *persistent*, not transient,
and the mode locks onto it. Measured this session on a synthetic lavfi source (3 s of a small
bright region on black, then the true 1280x544 picture):

```
73 crop=80:80:600:300      <- modal winner; what detect_active_rect would return
50 crop=1280:544:0:88      <- the true active picture
```

Every scorer plus the optical-flow pass would then measure an 80x80 patch of a 1280x720 video, for
the whole file, silently. See P2-1 — including the counter-argument, which is real.

**(c) Is the crop applied consistently to every scorer?**
Yes for all four scorers and for optical flow — identical placement (after `cvtColor` to gray,
before any measurement): `scoring_sharpness.py:55-56`, `scoring_exposure.py:69-70`,
`scoring_composition.py:296-297`, `motion.py:78-79`. `scoring_motion_smoothness` needs no crop; it
consumes the already-cropped motion series. **Three other frame-measuring paths were not extended**:
`gates.py` blackdetect/freezedetect (P2-2, measured effect below), PySceneDetect in
`segmentation.py` (P3-5), and — by design — nothing else in the package decodes frames (grepped:
the only other `subprocess.run`/`VideoCapture` sites are `common/ffprobe.py` and
`reel_stitching/{render,verify}.py`, none of which score).

**(d) Per-video vs per-segment rect?**
Correct as written. `detect_active_rect` is called exactly once, at `pipeline.py:86`, before the
segment loop, and the resulting rect is reused for the whole-video optical-flow pass and for all N
segments. No recomputation, no cache, no staleness bug. The gap is that the rect is never
*recorded* (P2-5).

---

## Findings

### P1-1 — Unconditional 5 s `cropdetect` probe: minutes per file on the real working footage, for a measured no-op, with no way to disable it
`pipeline.py:86`, `letterbox.py:55` (`DEFAULT_PROBE_SECONDS = 5.0`), `letterbox.py:93-102`.

`data/reference_pack/WORKING_FOOTAGE.md` §4 records, measured 2026-07-29: "`cropdetect` over 2 s of
one clip … exceeded a 2-minute wall clock" on this project's real 4K hevc material, and these
"do not complete on this material at native resolution." `detect_active_rect` asks for **5 s** of
the same decode, at native resolution, on every `run_pipeline` call. Linear extrapolation from the
pack's own number: >5 minutes per clip, >12 h added across the 153-clip working set, on top of the
measured 6.9–15.0 h full pass.

And §3b of the same file measures that this footage **is not letterboxed** (row means 46.6–175.9,
nothing under the luma-24 limit), so the result of that decode is a whole-frame no-op.

There is no escape hatch: `PipelineConfig` (`pipeline.py:45-60`) has no probe-seconds or
enable/disable field, `cli.py` exposes no flag, the ffmpeg command has no downscale, and
`subprocess.run` at `letterbox.py:103` has no timeout — an ffmpeg that never returns hangs
`run_pipeline` indefinitely with no output.

*Concrete failure:* `drone-highlights <4K clip> -o out.json` blocks for minutes before the first
frame is scored, and the user cannot turn it off or bound it.

*Fix, already proven in this repo:* WORKING_FOOTAGE.md §4 records that decoding one frame and
measuring row means in NumPy answered the same letterbox question "in milliseconds after
`cropdetect` had timed out entirely." That is a like-for-like replacement for the probe. Cheaper
interim: add `letterbox_probe_seconds` / `detect_letterbox: bool` to `PipelineConfig` + a CLI flag,
and pass `timeout=` to `subprocess.run`.

*Caveat, stated for fairness:* the >5-minute figure is extrapolated from the pack's 2 s
measurement, not measured directly — I am forbidden from running the pipeline on 4K this session,
which is itself the point.

### P2-1 — Modal aggregation over a monotone accumulator can silently lock in a partial rect
`letterbox.py:108` (`Counter(matches).most_common(1)[0]`), rationale at `letterbox.py:88-92`.

The docstring says the mode is chosen so that "a single transient reading (a dark frame early in a
fade, for instance) should not decide the geometry." With `reset=0` that is exactly the case it
cannot protect against: ffmpeg documents `reset=0` as "never reset … returns the largest area
encountered during playback," so the printed sequence is non-decreasing in area and an early dark
stretch produces a *long run* of identical under-estimates, which is what the mode selects.
Measured demonstration above (73 votes for an 80x80 rect vs 50 for the true 1280x544). Because the
sequence is monotone, the error is always in the direction of **cropping away real picture**, which
is worse than the bug being fixed: an 80x80 crop destroys Laplacian-variance sharpness, puts the
rule-of-thirds grid on a postage stamp, and leaves optical flow almost no features.

*Counter-argument, which is genuinely strong:* under `reset=0` a single above-limit pixel anywhere
in a bar (compression noise; the pack measured worst-case bar YMAX 21 against a limit of 24)
permanently expands the accumulated rect to full frame from that frame onward — so taking the last
or maximal reading is fragile in the opposite direction, and the mode does protect against it. The
pack's own recipe (`data/reference_pack/README.md:378-386`) reports the same modal statistic and
records that 2 of ~250 readings deviate, so this module is **consistent with the pack**, not
divergent from it. That consistency was an explicit design goal and should not be given up lightly.

*Fix that keeps both protections:* use a nonzero `reset` (e.g. one reset per second) so each
printed value is an independent per-window estimate and the mode becomes a meaningful statistic —
but note this diverges from the pack's recorded parameters, so it needs recording as such.
Cheapest defensible alternative: keep `reset=0` and the mode, but compare the modal rect against
the maximal observed rect and surface/reject a modal rect materially smaller in area.

*Why P2 and not P1:* no evidence any real clip triggers it. The pack measured a single stable crop
over the **full** duration of all four splits, and the working footage never dips under luma 24.
The mechanism is proven; the incidence in this project's own material is zero-so-far and unmeasured
for the 153-clip set.

### P2-2 — `gates.py` still measures the uncropped frame, and the effect is measurable
`pipeline.py:146-154` (no `active_rect` passed) → `gates.py:110-121`, filters built at
`gates.py:73` and `gates.py:89`.

The commit message says the fix covers "all frame scoring." The gates are the frame-measuring path
that decides **inclusion or exclusion**, and they were not covered. Two concrete consequences on
the four letterboxed corpus files:

*freezedetect — measured this session, not inferred.* Sweeping a moving box against an otherwise
static frame, at the pipeline's own defaults (`n=0.001`, `d=0.5`):

```
frame 1280x720 (letterboxed)      box 36x36 -> freeze_start REPORTED
frame 1280x544 (active picture)   box 36x36 -> no freeze
                                  (flip point: 36-42 px at h=720, 30-36 px at h=544)
```

The static bars contribute exactly zero inter-frame difference over 24.4% of the frame, so the
measured difference is ~0.756x the active-picture value and the gate is correspondingly more
trigger-happy. A segment that is not frozen is reported frozen and dropped from `segments`
entirely — a false exclusion, i.e. a lost highlight, not merely a shifted score.

*blackdetect — direction certain, exact threshold not verified in-session.* `picture_black_ratio_th`
defaults to 0.98 (verified: `ffmpeg -h filter=blackdetect`) and the bars at luma 16 sit below the
pixel-black threshold under either plausible range mapping (0.10 → 25.5 full-range, or 37.9 for
limited range). So the bars always count as black and the active picture only needs to be
(0.98 − 0.244)/0.756 = **97.35%** black to trip the gate instead of 98%.

*Fix:* one line each — prepend `crop={w}:{h}:{x}:{y},` to `filter_str` in
`_run_ffmpeg_filter_stderr`, and thread `active_rect` into `evaluate_gates`.

*Counter-argument:* one could argue a gate should judge the delivered frame as delivered — a black
or frozen deliverable is black or frozen whether or not it has bars. That is a defensible position;
it is just not the position the code takes anywhere, and it contradicts the commit's own premise.
Decide it explicitly and write it down either way.

### P2-3 — `pipeline.py:86` ignores `cfg.ffmpeg_bin`
`pipeline.py:86` calls `detect_active_rect(video_path)` with no `ffmpeg_bin`, so it uses
`letterbox.py:84`'s hardcoded `"ffmpeg"`, while the very next ffmpeg consumer in the same function
(`evaluate_gates`, `pipeline.py:153`) is correctly given `ffmpeg_bin=cfg.ffmpeg_bin`.

*Concrete failure, verified:* with an ffmpeg that is not on `PATH`,
`detect_active_rect(..., ffmpeg_bin="ffmpeg-not-installed")` raises an **uncaught**
`FileNotFoundError` — the whole run dies at line 86, before a single frame is scored, even though
the caller supplied a valid interpreter path in `PipelineConfig`. This repo's `CLAUDE.md` documents
a real ffmpeg-breakage failure mode (`brew upgrade` → `dyld: Library not loaded`), which is exactly
when someone would reach for an explicit binary path.

*Fix:* `detect_active_rect(video_path, ffmpeg_bin=cfg.ffmpeg_bin)`.

### P2-4 — `letterbox.py` has zero unit-test coverage
`ls tests/highlight_extraction/` → no `test_letterbox.py`. The only coverage is
`tests/integration/test_corpus_footage.py:47/64/79`, all `pytest.mark.integration`, i.e. among the
**10 deselected** in the unit run I executed. So the 93-test suite that the commit message cites as
still passing does not exercise this module at all.

Untested and all testable without footage: `ActiveRect.crop` on a matching frame, on a mismatched
frame, and on a full-frame rect; the `matches`-empty → `None` path; the `w <= 0 or h <= 0` guard;
and the modal-selection rule (feedable directly by monkeypatching `subprocess.run` with a canned
stderr string). *Concretely:* a regression that made `crop()` a no-op, or that swapped the mode for
the last reading, would be invisible to `pytest -m "not integration"`.

### P2-5 — The detected rect is not recorded anywhere, so a silent reversion is undetectable
`pipeline.py:86` (result used, never stored), `pipeline.py:69-78` / `222-229` (manifest carries no
letterbox field).

`detect_active_rect` returns `None` whenever ffmpeg emits no parsable `crop=` line — verified:
`detect_active_rect('/nonexistent.mp4')` returns `None`, no exception. On `None`, `run_pipeline`
proceeds and scores **every frame uncropped**, i.e. exactly the pre-fix behaviour, and the emitted
manifest contains no evidence of which happened. The parse is log-scraping against an unversioned
format, and the pack itself warns (`README.md:216`) that "`scdet`/`cropdetect`/`signalstats`
behaviour is version-dependent."

*Concrete failure:* an ffmpeg upgrade that alters the cropdetect log line silently reverts the fix.
Two manifests for the same letterboxed file, one before and one after, differ by 0.2444 in exposure
and are indistinguishable from the manifest alone — the exact "invented vs measured provenance"
problem this repo's Constitution exists to prevent.

*Fix:* record the rect (or an explicit `null`) in the manifest's source-file/provenance block. I
found no `additionalProperties: false` in the schema module, but this is still a schema-version
question — flagging for the human rather than prescribing.

### P3-1 — `ActiveRect.crop` cannot fail loudly
`letterbox.py:73-78`. Demonstrated above: NumPy clips, so a mismatched rect yields a wrong region
and a fully out-of-range rect yields a zero-pixel frame. Note the downstream consequence of the
empty case: `scoring_exposure.py:37-38` returns a clipped fraction of 0.0 for a zero-size frame, so
the segment scores a **perfect exposure of 1.0 from zero pixels**. The docstring
(`letterbox.py:75-77`) states the hazard honestly and puts the burden on callers, and today every
caller honours it — hence P3, not higher. The guard is two lines:
`if frame.shape[0] < self.y + self.height or frame.shape[1] < self.x + self.width: raise ValueError(...)`.

### P3-2 — The `w <= 0 or h <= 0` guard is not the mechanism the code implies
`letterbox.py:110-111`, regex at `letterbox.py:57`. Measured this session: on an all-black input
`cropdetect` prints `crop=-1278:-718:1280:720` (73 of 123 lines in my lavfi run). The regex
`crop=(\d+):(\d+):(\d+):(\d+)` cannot match a leading `-`, so those degenerate lines are dropped
before the guard ever sees them. The outcome is right, but the documented mechanism is not the
operative one, and the real consequence is unstated: if the **entire** probe window is below
limit=24 (a >5 s fade from black, a night shot), `matches` is empty and the function returns
`None` → the file is scored uncropped, with no record (see P2-5). Fix: match `-?\d+`, keep the
guard, and make "degenerate" distinguishable from "no output".

### P3-3 — No `timeout` on `subprocess.run`
`letterbox.py:103`. `gates.py:58` has the same shape, so this is a package convention rather than a
new defect — but combined with P1-1 (a decode measured to exceed 2 minutes for 2 s of 4K input) it
means an unresponsive ffmpeg blocks `run_pipeline` forever.

### P3-4 — `Optional["ActiveRect"]` is a forward reference to a name never imported
`motion.py:51`, `scoring_sharpness.py:30`, `scoring_exposure.py:45`, `scoring_composition.py:263`.
Verified: `typing.get_type_hints(compute_motion_series)` raises
`NameError: name 'ActiveRect' is not defined`. Harmless at runtime under
`from __future__ import annotations`, but it breaks any introspection-based tooling. Fix:
`if TYPE_CHECKING: from drone_video_ai.highlight_extraction.letterbox import ActiveRect`.

### P3-5 — PySceneDetect never sees the rect
`pipeline.py:90-98` → `segmentation.py:33-38`; `open_video` decodes its own frames. Mostly benign:
`AdaptiveDetector`'s adaptive ratio is scale-invariant, so the uniform 24.4% dilution largely
cancels. The exception is `min_content_val` (verified default 15.0, scenedetect 0.7.1), applied to
the un-normalised content value: a real cut whose cropped content value falls in [15, 19.84) is
suppressed on a letterboxed file. Unobservable on this corpus — the pack measured zero hard cuts
across all 8 files (and 45 archive files) — which is precisely why this is P3.

---

## What is right, and worth not regressing

- **Once per video, before the segment loop** (`pipeline.py:86`). Question (d) has no defect.
- **Uniform application point.** All five consumers crop at the same place — after `cvtColor`,
  before any measurement — so no scorer sees a differently-prepared frame.
- **Cropping the optical-flow input** (`motion.py:78-79`) is the non-obvious right call: the
  bar/picture boundary is a full-width high-contrast edge, and features seeded along it are
  perfectly static, biasing every frame's mean displacement toward zero.
- **Parameters taken verbatim from the pack's own recipe** (`letterbox.py:50`), with the reasoning
  stated: a disagreement with the pack is then a real disagreement, not a parameter artefact. The
  modal statistic also matches how the pack itself reports (`README.md:378-386`).
- **The negative control exists**: `is_full_frame` plus
  `test_vertical_family_is_not_letterboxed` guard against a detector that finds letterbox
  everywhere — the failure mode a naive crop fix would have shipped.
- **The commit message retracts two of its own earlier claims by measurement** (the "bar edge acts
  as a false horizon" hypothesis, decomposed and refuted). That is the standard this repo asks for.

## Out of scope but noted in passing

The commit message's own retraction records that `_horizon_levelness_score`
(`scoring_composition.py:220-258`) takes only {0.0, 1.0} across 12 samples despite documenting a
graded `1 - |tilt|/20`. Reading the code, the "no line detected → 1.0" branches
(`scoring_composition.py:235, 253`) are neutral-by-design, so a measured 0.0 must come from
`tilt >= 20°`. Not investigated further — it belongs to a composition review, not this one.

## Method / limits of this review

- Read in full: `letterbox.py`, `pipeline.py`, `motion.py`, `gates.py`, all four `scoring_*.py`,
  `segmentation.py`, `composite.py`, `cli.py`, `tests/integration/test_corpus_footage.py:1-110`.
- Ran: the unit suite (93 passed); `ffprobe -version` (8.1.2, healthy); three lavfi-only ffmpeg
  experiments (cropdetect accumulate semantics; cropdetect on all-black; freezedetect sensitivity
  sweep) — none wrote any file; `ffmpeg -h filter=...` for blackdetect/freezedetect defaults;
  ffprobe dims/rotation over `data/raw/corpus/`; four in-process Python probes of `ActiveRect.crop`,
  `get_type_hints`, and `detect_active_rect` error paths.
- **Not** run: the integration suite, and anything touching 4K footage. The P1-1 magnitude is
  therefore extrapolated from the pack's recorded 2 s measurement, not measured directly.
