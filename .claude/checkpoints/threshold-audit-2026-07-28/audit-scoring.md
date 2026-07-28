# Threshold Audit — Scoring Group (4 per-signal scorers)

STATUS: COMPLETE
Date: 2026-07-28
Mode: **STATIC audit only.** `src/` was never executed, imported, or installed. Every claim
below is either (a) read directly out of source text, (b) read directly out of
`data/reference_pack/`, or (c) an explicitly-labelled inference marked LIKELY /
NEEDS_EXECUTION. No runtime behaviour is asserted as fact.

Files audited (all read in full this session):
- `/Users/mac/.../src/drone_video_ai/highlight_extraction/scoring_sharpness.py` (75 lines)
- `/Users/mac/.../src/drone_video_ai/highlight_extraction/scoring_exposure.py` (75 lines)
- `/Users/mac/.../src/drone_video_ai/highlight_extraction/scoring_motion_smoothness.py` (50 lines)
- `/Users/mac/.../src/drone_video_ai/highlight_extraction/scoring_composition.py` (306 lines)

Also read (for grounding / interaction analysis, not audited for constants — other agents own them):
- `data/reference_pack/editorial_style.json` (all value/unit/confidence leaves enumerated)
- `data/reference_pack/REVIEW.md` (§ lines 719-780 luma/letterbox, 925-975 grade controls, 1139 open question I)
- `.claude/specs/drone-video-pipeline/{spec.md,plan.md,tasks.md}`
- `src/.../highlight_extraction/{motion.py,gates.py,pipeline.py,segmentation.py}` + `weights.py` (grep only)

---

## 0. Headline

**Zero of the 33 constants in these four files trace to `data/reference_pack/`.**
Not one cites a measured value, a probe file, an `editorial_style.json` key path, or any number
someone actually measured over this project's own footage. The reference pack and the scoring
code were built in complete isolation from each other.

That is the finding. It is *not* the same as saying the code is careless — the opposite is
visibly true. 10 constants are genuinely well-documented DEFENSIBLE_DEFAULTs with explicit,
honest reasoning (`scoring_composition`'s 0.5/0.5 sub-weighting and its closed-form
normalisation denominator are model examples). The problem is narrower and sharper: the
codebase documents its constants **against itself** (docstrings, internal cross-references,
synthetic-fixture tests) and never once against the corpus it will run on.

Two constants are individually reasonable and **measurably inert or wrong** on this corpus.
Four scorers share one systemic blind spot: **none of them crops the letterbox**, which the
pack measured as baked into 4 of the 8 corpus files.

---

## 1. Constant inventory

Classification key (per audit brief):
`MEASURED` traces to a measured leaf in the pack · `SPEC` traces to a spec/plan/tasks line ·
`LIBRARY_DEFAULT` is the documented default of ffmpeg/OpenCV/PySceneDetect ·
`DEFENSIBLE_DEFAULT` is arbitrary AND the code says so and explains ·
`INVENTED` is a bare number with no derivation locatable anywhere.

Note on the rubric applied: a comment asserting a value is "conservative", "standard", or
"documented" is **not** a derivation. `scoring_exposure.py` L18-20 literally says its
thresholds are "conservative, documented thresholds -- not invented magic numbers buried
inline; see highlight_extraction/weights.py". I checked. `weights.py` contains scoring
*weights* and duration profiles; it says nothing about luma clipping thresholds. The
cross-reference is a redirect to a file that does not contain the claimed documentation. The
comment asserts a derivation exists rather than providing one, so both values classify
INVENTED.

### 1.1 `scoring_sharpness.py` — 5 constants

| # | Constant | Value | Line | Class | Derivation found? |
|---|---|---|---|---|---|
| S1 | `max_samples` default | `10` | 29 | INVENTED | None. Not in spec.md, plan.md, or tasks.md (1.7 specifies "sampled frames per segment" with no count). Bare number. |
| S2 | fps fallback | `30.0` | 42 | INVENTED | None stated. **Coincidentally exactly right**: `corpus_wide_invariants.frame_rate = "30/1"`, confidence=measured, true on all 8 files. Right answer, no citation. |
| S3 | degenerate-range epsilon | `1e-9` | 72 | DEFENSIBLE_DEFAULT | Purpose explained inline ("rather than dividing by zero"). Standard float-equality guard. |
| S4 | degenerate normalize return | `1.0` | 73 | DEFENSIBLE_DEFAULT | Explicitly explained: "there is no 'worse' segment to compare against". Honest, reasoned policy choice. |
| S5 | no-decodable-frame sentinel | `0.0` | 57 | INVENTED | Undocumented. Semantically means "worst segment in the video" after min-max — an I/O failure is indistinguishable from genuinely soft footage. |

Non-constants deliberately excluded: `max(1, ...)`, `n_samples <= 1`, `cv2.CV_64F`,
`COLOR_BGR2GRAY` — structural/enum, not tunable magnitudes.

### 1.2 `scoring_exposure.py` — 6 constants

| # | Constant | Value | Line | Class | Derivation found? |
|---|---|---|---|---|---|
| E1 | `LOW_CLIP_THRESHOLD` | `5` | 21 | INVENTED | Comment claims "conservative, documented"; the pointer (weights.py) does not document it. Absent from spec/plan/tasks. See §3.1 — **provably inert on this corpus**. |
| E2 | `HIGH_CLIP_THRESHOLD` | `250` | 22 | INVENTED | Same. See §3.2 — near-inert on the one file where the pack measured YMAX. |
| E3 | `max_samples` default | `10` | 44 | INVENTED | Same as S1. |
| E4 | fps fallback | `30.0` | 56 | INVENTED | Same as S2. |
| E5 | histogram bins / range | `[256]`, `[0,256]` | 35 | LIBRARY_DEFAULT | `cv2.calcHist` canonical 8-bit parameterisation. Correct against measured `corpus_wide_invariants.codec = "h264, profile High, pix_fmt yuv420p, 8-bit"` (measured). |
| E6 | no-decodable-frame sentinel | `0.0` | 71 | INVENTED | Undocumented. Means "every pixel clipped" — the worst possible exposure — for what is actually a decode failure. |

Correctness note (positive): the two tails are symmetric — `hist[:LOW+1]` is bins 0-5 (6 levels)
and `hist[HIGH:]` is bins 250-255 (6 levels). The docstring's "at or below / at or above"
wording matches the slicing exactly. No off-by-one.

### 1.3 `scoring_motion_smoothness.py` — 3 constants

| # | Constant | Value | Line | Class | Derivation found? |
|---|---|---|---|---|---|
| M1 | empty-samples / empty-mask sentinel | `0.0` | 26, 30, 33 | INVENTED | Undocumented, and **direction-inverted** relative to S5/E6: raw jerk `0.0` is the *best possible* value (perfectly smooth). After `invert_and_normalize`, a segment with no motion samples becomes the smoothest segment in the video. See §3.6. |
| M2 | degenerate-range epsilon | `1e-9` | 48 | DEFENSIBLE_DEFAULT | Mirrors S3. |
| M3 | degenerate normalize return | `1.0` | 49 | DEFENSIBLE_DEFAULT | Explicitly explained: "there is no 'shakier' segment to compare against". |

Correctness check performed (positive result): `compute_raw_jerk_magnitude` builds `mask` over
`samples` and indexes `jerk` with it. I read `motion.py:149-164` — `compute_jerk_series`
returns `np.zeros(len(samples))` with `jerk[2:] = accel`, i.e. **same length as `samples`**.
The boolean-mask index is length-safe. No IndexError. This was a hypothesis I actively tried
to falsify and it did not hold.

### 1.4 `scoring_composition.py` — 19 constants

| # | Constant | Value | Line | Class | Derivation found? |
|---|---|---|---|---|---|
| C1 | `ROT_POINT_FRACTIONS` | `1/3, 2/3` × 4 | 152-157 | SPEC | spec.md:21 "saliency-to-rule-of-thirds distance via OpenCV's `saliency` module"; tasks.md:147 (1.21). The 1/3 and 2/3 fractions *are* the definition of the named technique. |
| C2 | `MAX_HORIZON_TILT_DEGREES` | `20.0` | 161 | **INVENTED** | Rationale given (docstring §2) is "a professionally-composed aerial shot with an intentional tilt rarely exceeds this". That is precisely the prohibited class of derivation — general knowledge of what drone footage usually looks like. **No measured horizon-tilt distribution exists in the pack**, and the pack states the toolchain cannot produce one (`schema.toolchain.unavailable`, measured). Highest-consequence INVENTED value in the group. |
| C3 | `ROT_SUBSCORE_WEIGHT` | `0.5` | 165 | DEFENSIBLE_DEFAULT | Docstring §3: "the spec calls out with no stated priority between them, so an even split is the simplest defensible default." Textbook honest labelling. |
| C4 | `HORIZON_SUBSCORE_WEIGHT` | `0.5` | 166 | DEFENSIBLE_DEFAULT | Same. |
| C5 | Canny `threshold1` | `50` | 225 | INVENTED | No derivation anywhere. Not an OpenCV default (both Canny thresholds are required positional args). |
| C6 | Canny `threshold2` | `150` | 225 | INVENTED | Same. (1:3 ratio is a common convention, but the code never says so.) |
| C7 | Hough `rho` | `1` | 228 | LIBRARY_DEFAULT | Canonical OpenCV-documented 1-pixel accumulator resolution. Caveat: required arg, so not literally an API default. |
| C8 | Hough `theta` | `np.pi/180` | 229 | LIBRARY_DEFAULT | Canonical OpenCV-documented 1-degree resolution. Same caveat. |
| C9 | Hough `threshold` | `60` | 230 | INVENTED | Bare vote count. No derivation. |
| C10 | `minLineLength` divisor | `width // 3` | 231 | INVENTED | The `//3` divisor is undeclared. Possibly meant to echo the rule-of-thirds grid; the code never says. See §3.4 — this is the constant that makes the letterbox bug bite. |
| C11 | `maxLineGap` | `10` | 232 | INVENTED | Bare number, no derivation. |
| C12 | ROT normalisation denominator | `sqrt((w/3)²+(h/3)²)` | 212 | DEFENSIBLE_DEFAULT | **The best-documented constant in the group.** Docstring §1 states the closed form and why it is exact (max nearest-ROT-point distance is attained at a frame corner). I verified this analytically this session: corner (0,0)→(w/3,h/3) gives sqrt((w/3)²+(h/3)²); centre gives sqrt((w/6)²+(h/6)²); edge midpoints give strictly less. **Claim confirmed.** But see §3.3 — the *w,h* it is fed are wrong for 4 of 8 files. |
| C13 | near-horizontal candidate filter | `45.0` deg | 246 | DEFENSIBLE_DEFAULT | Explained in docstring §2 as the horizontal-vs-vertical discriminator; 45° is the exact bisector of that dichotomy, so it is derived rather than picked. |
| C14 | no-line-detected neutral score | `1.0` | 235, 253 | DEFENSIBLE_DEFAULT | Extensively and well reasoned (docstring §2): absence of a detectable horizon is not evidence of a tilted one; nadir aerials should not be penalised for a signal this scorer cannot evaluate. Genuinely good engineering. |
| C15 | saliency-degenerate guard | `1e-9` + geometric-centre fallback | 197, 213 | DEFENSIBLE_DEFAULT | Explained inline ("a perfectly uniform frame produces essentially no saliency signal"). |
| C16 | `computeSaliency` failure sentinel | `0.0` | 193 | INVENTED | Undocumented — and **internally inconsistent** with C14 forty lines below, which adopts the opposite policy (missing signal → neutral 1.0) for the sibling sub-score. Two failure paths in one function, opposite conventions, one of them argued for at length and one silent. |
| C17 | no-decodable-frame sentinel | `0.0` | 299 | INVENTED | Same family as S5/E6. |
| C18 | `max_samples` default | `10` | 262 | INVENTED | Same as S1. |
| C19 | fps fallback | `30.0` | 282 | INVENTED | Same as S2. |

Excluded as structural: the ±90/180 angle-wrap arithmetic (L242-245), `np.clip(...,0,1)` bounds.

---

## 2. Distribution

**Per-site count (each literal at each site counted once): 33 constants.**

| Class | Count | % |
|---|---|---|
| MEASURED | **0** | 0% |
| SPEC | 1 | 3% |
| LIBRARY_DEFAULT | 3 | 9% |
| DEFENSIBLE_DEFAULT | 10 | 30% |
| INVENTED | 19 | 58% |

**Deduplicated by distinct engineering decision** — because three patterns (`max_samples=10`,
`fps or 30.0`, `return 0.0` on decode failure) are the same decision copy-pasted across 3-4
files, the per-site count overstates how many independent unjustified choices were made. The
honest second view:

| Class | Distinct decisions |
|---|---|
| MEASURED | **0** |
| SPEC | 1 |
| LIBRARY_DEFAULT | 3 |
| DEFENSIBLE_DEFAULT | 8 |
| INVENTED | **12** |

The 12 distinct INVENTED decisions: `max_samples=10`; `fps or 30.0`; `return 0.0` decode
sentinel; `LOW_CLIP_THRESHOLD=5`; `HIGH_CLIP_THRESHOLD=250`; `MAX_HORIZON_TILT_DEGREES=20.0`;
Canny `50`; Canny `150`; Hough `threshold=60`; `minLineLength=width//3`; `maxLineGap=10`;
saliency-failure `0.0` sentinel.

Both views are reported because either alone misleads: 58% is technically true but reads as
sloppier than the code is; 12 distinct is fairer but hides that the sentinel-direction problem
recurs in every file.

---

## 3. Interaction bugs — constants that are individually defensible but wrong against THIS footage

### 3.1 `LOW_CLIP_THRESHOLD = 5` is provably inert on the measured corpus — CONFIRMED

Code: `scoring_exposure.py:21,39` — pixels with gray ≤ 5 count as under-exposed.

Pack, all confidence=measured:
- `colour_treatment.measured_tonal_signature.horizontal_split_family_active_area.YMIN_floor` =
  `{split_001: 31, split_002: 41, split_003: 38, split_004: 36}`
- `...vertical_social_family_full_frame.YMIN_floor` = `{instagram_reel_test: 30, viral_test_v2: 14}`
- `corpus_wide_invariants.lifted_blacks = true`
- REVIEW.md:766 — "blacks are lifted, **there is no true black in the picture**"

The darkest single pixel measured anywhere in the corpus is Y=14. The threshold is 5. On the
raw luma plane, the fraction of pixels at or below 5 is **exactly zero in all 8 files**.

I actively tried to falsify this with the one candidate that could produce near-black: the
vertical family's terminal fade. REVIEW.md:719-720 — the fades are **truncated**, last frame
YAVG 23.68-34.71, YMAX 30-51. Even the darkest frame in the corpus has its *brightest* pixel
at 30, i.e. 6× the threshold. The fade does not rescue this threshold either.

**Consequence:** the under-exposure half of the exposure scorer contributes identically zero on
every file of this corpus. It is not "rarely triggered" — it is structurally unreachable.

### 3.2 `HIGH_CLIP_THRESHOLD = 250` is near-inert on the one file the pack measured YMAX for — LIKELY

REVIEW.md:953 (grade-control table, `crop=1280:544:0:88`, first 450 frames, per-frame
`signalstats`): `split_004_s65` active region **YMAX 238.22**, versus 254.99 for the 8-bit
baseline reduction and 243.00 for a true BT.2020→BT.709 conversion.

238.22 is 11.8 levels below the 250 threshold. The measured `drone_aerial` grade is described
in the same section as "a highlight-weighted downward compression" (YMAX −16.77, −6.58 %) —
i.e. the grade actively pushes the corpus's highlights *away* from the clip threshold.

Caveat stated honestly: 238.22 is a mean of per-frame YMAX over 450 frames, so individual
frames may exceed 250, and the pack measures YMAX for **only this one file**. This is weaker
evidence than §3.1 and is labelled LIKELY, not CONFIRMED.

**Combined consequence of §3.1 + §3.2:** on the split family's active picture, both tails of
the exposure scorer are at or near zero. `compute_raw_exposure` returns ≈ 1.0 for every
segment. Exposure carries a **0.25 weight** in the active profile (`weights.py:77-83`,
`default-v2`, which is `DEFAULT_WEIGHTS_VERSION`) and, unlike sharpness and motion-smoothness,
is **not** min-max renormalised (`pipeline.py:117-120` — "exposure and composition are already
normalized"). So 25% of the composite score is a near-constant on this corpus: it consumes a
quarter of the weight budget while ranking nothing.

### 3.3 No scorer crops the letterbox — the systemic finding — CONFIRMED (code side)

Pack, measured: `letterbox.horizontal_split_family` — `applied: true`,
`active_picture_px: [1280, 544]`, `coded_frame_px: [1280, 720]`, `bar_height_px: 88`,
`bar_luma: 16`, `mechanism: "vertical CENTRE-CROP at source row 88 then pad back to 1280x720
-- NOT an anamorphic squeeze"`, `content_cost: 24.4` percent. REVIEW.md:727-732 puts the
boundary exactly at rows 88 and 631 with a ~180-level luma step across 2-4 rows.
`editorial_style.json` records that every pack measurement of these files uses
`crop=1280:544:0:88` and explicitly labels it "active picture only, letterbox bars excluded".

All four scorers do `ret, frame = cap.read()` → `cv2.cvtColor(frame, COLOR_BGR2GRAY)` and
score the **full coded frame**. Verified at `scoring_sharpness.py:53`,
`scoring_exposure.py:67`, `scoring_composition.py:294`, and `motion.py:76` (which feeds
motion-smoothness). Not one of them crops, and not one mentions letterboxing. This applies to
**4 of the 8 corpus files** — 24.4% of every frame they score is a flat synthetic mask.

Per-scorer consequence:

- **Composition / rule-of-thirds (C1, C12):** the ROT grid is computed on the coded height
  720, putting the horizontal thirds at y = 240 and 480. The *visible picture* spans rows
  88-631, whose true thirds are y = 88 + 544/3 = **269.3** and 88 + 2·544/3 = **450.7**. The
  grid lines are misplaced by **29.3 px**, 5.4% of the active picture height, in opposite
  directions. The normalisation denominator C12 — the constant whose derivation I confirmed as
  mathematically exact in §1.4 — is fed h=720 instead of 544, so it is exact for a frame the
  viewer never sees. A correct constant applied to the wrong rectangle.
- **Sharpness (S-group):** Laplacian variance is taken over a frame that is 24.4% constant-
  valued. The bars contribute near-zero Laplacian response (except at the two boundary rows),
  systematically depressing the raw statistic. Because normalisation is in-video min-max and
  the dilution is constant within a file, **within-file ranking survives** — this one is a
  real distortion of the absolute value but not of the ordering. Stated so the finding is not
  overclaimed.
- **Exposure (E1):** see §3.5 — decoder-range-dependent.
- **Motion (M-group, via `motion.py`):** `goodFeaturesToTrack` gets 24.4% of the frame with no
  corner response; `maxCorners=200` is therefore spent on 75.6% of the raster. Low impact
  (features simply are not found in flat regions), noted for completeness rather than as a bug.

### 3.4 The letterbox bar edge is a perfect false horizon — pins composition's horizon sub-score to 1.0 — LIKELY

This is the highest-consequence interaction in the group.

`_horizon_levelness_score` (L220-258) runs `cv2.Canny(gray, 50, 150)` then `HoughLinesP(...,
threshold=60, minLineLength=max(1, width//3), maxLineGap=10)`, selects the **longest**
near-horizontal segment, and converts its angle to a levelness score.

On the 4 split-family files the pack measured (REVIEW.md:727-732):
- two perfectly horizontal boundaries at rows 88 and 631,
- spanning the full 1280 px width,
- with a luma step of roughly 180 levels (rows 84/86 read max Y 1-2; rows 88/90/92 read 182-184).

A ~180-level step edge will fire Canny at thresholds 50/150 with near-certainty.
`minLineLength = 1280 // 3 = 426` px is easily cleared by a 1280 px line, and `maxLineGap=10`
bridges any compression-noise dropouts. The bar edge is the **longest possible** horizontal
line in the raster, so `best_length` selects it over any real horizon, which can at best tie
it. Its angle is exactly 0.0°, so `tilt = 0.0` and the function returns **1.0**.

**Consequence:** for all 4 letterboxed corpus files, the horizon-levelness sub-score — 50% of
`scores.composition` per C4 — is pinned at its maximum on every frame of every segment, and
what it is actually measuring is the letterbox mask, not the horizon. The sub-scorer cannot
fail, cannot vary, and cannot detect the tilted horizon it exists to detect. `MAX_HORIZON_TILT_
DEGREES = 20.0` (C2) never enters the computation on these files at all.

Confidence: LIKELY not CONFIRMED. The measured edge geometry and the code path are both
confirmed by reading; that Canny/Hough actually fire is an inference I cannot execute. It is
falsifiable with one command against one split file once an interpreter exists.

### 3.5 `LOW_CLIP_THRESHOLD = 5` sits exactly astride the decoder-range boundary — NEEDS_EXECUTION

Measured `bar_luma = 16` ("limited-range video black, matching `color_range=tv`", REVIEW.md:730)
and measured `colour_tagging.horizontal_split_family.color_range = "tv"`.

`cv2.VideoCapture` decodes to BGR. If the decode path expands limited-range YUV to full-range
RGB (the standard swscale behaviour), Y=16 → RGB(0,0,0) → gray 0 → **counted as clipped**, and
24.4% of every frame of every split-family segment is scored as under-exposed. Exposure then
returns a constant ≈ 0.7556. If the decode path does not expand, Y=16 → gray 16 > 5 → not
counted, and exposure returns ≈ 1.0 per §3.1/§3.2.

The code pins neither behaviour and never mentions range. The pack measured the one value — 16
— that sits between the two outcomes for a threshold of 5. Either branch yields a **constant**
exposure score across all segments of a file, so the discriminative-power conclusion in §3.2
holds regardless; only the absolute level moves.

Does it cause a gate failure? **No, not by default.** `gates.py:24` sets
`DEFAULT_MIN_EXPOSURE_FLOOR = 0.0` ("no floor by default"), and `evaluate_gates` uses `<`, so
0.7556 passes. The damage is confined to the composite score: a constant −0.2444 × 0.25 ≈
**−0.061 composite penalty** applied to every split-family segment and to no vertical-family
segment. Per-file manifests are unaffected in ordering; any cross-file comparison (including
`summary.avg_composite_score`) is biased against the letterboxed family for a reason that has
nothing to do with quality. Worth flagging to whoever owns the min-exposure-floor CLI flag: a
user setting `--min-exposure-floor 0.8`, a value that looks conservative, would silently
exclude 100% of the split family under this branch.

### 3.6 Failure sentinels point in inconsistent directions — CONFIRMED

Three of the four scorers return `0.0` when they cannot read frames (S5, E6, C17), which after
normalisation means "worst segment". `scoring_motion_smoothness` returns `0.0` when it has no
samples (M1) — but there `0.0` is *raw jerk*, where lower is better. After
`invert_and_normalize` (L45: `inverted = [-v ...]`, then min-max), a segment with **zero motion
samples becomes the smoothest segment in the video**, scoring 1.0.

Same literal, same intent ("I have no data"), opposite outcomes: a data-starved segment is
maximally penalised on three signals and maximally rewarded on the fourth.

Within `scoring_composition` the inconsistency is internal: C16 returns 0.0 (max penalty) when
saliency computation fails, while C14 forty lines later returns 1.0 (neutral) when line
detection fails — and the docstring argues at length for *why* neutral is correct there. The
argument was never applied to its sibling.

Corpus relevance: `motion.py` samples every decoded frame, so an empty mask requires a segment
shorter than one frame or outside the series — unlikely with `min_duration = 2.0`. Rated a
robustness defect, not an active corpus bug.

### 3.7 In-video min-max normalisation on a zero-cut corpus — LIKELY

Pack, measured: `shot_structure.hard_cut_count_total_corpus = 0`;
`cut_rhythm.corpus_is_single_shot = true`; `corpus_wide_invariants.shots_per_file = 1`.
Every segment the pipeline produces from a corpus file therefore comes from **one continuous
shot**, not from different scenes.

`min_max_normalize` (sharpness) and `invert_and_normalize` (motion) stretch whatever spread
exists across segments to the full [0,1] range, so the best segment always scores exactly 1.0
and the worst exactly 0.0 **regardless of absolute quality**. When the segments are slices of a
single continuous take, that spread is small: the pack measured
`exposure_stability` = `split_001: [92.24, 98.61]` — YAVG varying by 6.4 levels across a whole
15 s take (measured), and REVIEW.md:766 calls exposure "extremely stable". The normalisation
converts near-noise into maximum score separation.

The degenerate branch is also reachable on real files: `DEFAULT_DURATION_PROFILE`
(`weights.py:105`) is min 2.0 / max 15.0 s, and **6 of the 8 measured durations are ≤ 15.0 s**
(8.3, 14.566667, 14.566667, 15.0, 15.0, 15.0). If the motion-minima detector yields no interior
boundary for such a file, it produces one segment, and both S4 and M3 fire: sharpness = 1.0 and
motion_smoothness = 1.0 by construction, exposure ≈ constant per §3.2 — a composite score of
roughly 0.75 + 0.25·composition carrying no information at all. This is conditional on
segmentation behaviour I did not audit (owned by another agent), so it is stated as a
conditional, not a conclusion.

### 3.8 Cross-check of the brief's hypothesis (a): `DEFAULT_BLACK_PIX_TH = 0.10` — LIKELY inert, but not for the stated reason

`gates.py` is not my file; recording this because it was posed as a hypothesis to test and the
exposure measurements bear directly on it.

The brief's reasoning ("lifted blacks YMIN 31-41, so blackdetect can never fire") is **not
quite right** and should not be repeated as stated. ffmpeg's `blackdetect` `pix_th` is scaled
into the luma range, so 0.10 on limited-range video corresponds to roughly Y ≤ 16 + 0.10·219 ≈
**37.9**, not Y ≤ 25. Measured active-area YMIN floors are 31-41 — i.e. some pixels *do* fall
below that. And the verticals' truncated terminal fade ends at YAVG 23.68-34.71 with YMAX 30-51
(REVIEW.md:719-720), meaning near the end of the fade a very large fraction of pixels — possibly
all of them, when YMAX is 30 — are below 37.9.

The gate is nonetheless inert here, for a different and better-grounded reason: `blackdetect`
also requires `picture_black_ratio_th` (default 0.98) **and** the code passes
`d=0.5` seconds (`DEFAULT_BLACK_MIN_DURATION`). The measured fade is 13-14 frames total
(0.433-0.467 s, `cut_rhythm.terminal_transition...length_s`, measured), and only its final
frames are dark enough to qualify. A 0.5 s minimum duration cannot be satisfied by a
0.47 s fade whose qualifying tail is a handful of frames. So: inert, but because of `d=0.5`
versus a measured 0.43-0.47 s truncated fade, not because of lifted blacks.

Flagged as LIKELY — the pix_th scaling formula is ffmpeg-documented behaviour I could not
execute to confirm, and the ownership of `gates.py` sits with another agent.

---

## 4. Things I checked that turned out to be fine

Recorded so this audit is not read as one-sided.

- `compute_jerk_series` length contract — safe (§1.3).
- Exposure histogram tail slicing — symmetric, no off-by-one (§1.2).
- C12's closed-form maximum-distance claim — independently verified analytically; the docstring
  is correct (§1.4). Its inputs are wrong on letterboxed files, but the constant is not.
- 8-bit histogram assumption — matches `corpus_wide_invariants.codec` (measured, yuv420p 8-bit).
- `fps or 30.0` — no derivation, but exactly matches the measured `30/1` CFR invariant on all
  8 files, so it will never actually fire wrong on this corpus.
- Rotation handling — no scorer reads rotation metadata; the pack measured
  `rotation_side_data = "absent on all 8"`. Correct by accident, but correct.
- C14 (no-line → neutral 1.0) and C3/C4 (0.5/0.5 split) are the two best-argued constants in
  the group and should be preserved as-is; they are exactly the honest DEFENSIBLE_DEFAULT the
  audit brief describes.

## 5. Observations outside the constant taxonomy

- `scoring_composition.py:136-149` raises `ImportError` **at module import time** if
  `cv2.saliency.StaticSaliencySpectralResidual_create` is missing. `pipeline.py:35` imports
  this module unconditionally, so a contrib/plain OpenCV clash kills the entire highlight CLI
  even in a Milestone-1 run where composition weight would be 0.0. Environmental, not corpus.
- The SpectralResidual-vs-FineGrained benchmark quoted in the docstring (0.48 ms vs 8.74 ms) is
  per **320×240** frame; the code passes the full decoded frame (1080×1920 for the verticals,
  2160×3840 for the mastering renditions per `delivery_surfaces[1].resolution_px`, measured).
  The quoted figure does not transfer to the corpus's actual resolutions.
- `max_samples = 10` against measured shot lengths: the two 27.1 s files at measured 30/1 CFR
  are 813 frames; 10 samples is one frame every 2.71 s, **1.2% of frames**. The pack measured
  within-file motion variation up to `range_ratio_max_over_min` = 5.5 (viral_test_v2,
  per-second MAFD, measured), so within-shot variation this sampling rate will not resolve is
  measured to exist.
- `cap.set(CAP_PROP_POS_FRAMES, idx)` is used for every sample in three scorers. The pack
  measured `has_b_frames 2` on both vertical families and `has_b_frames 0` on the splits
  (`delivery_surfaces[].codec`, measured), so seek precision is systematically different
  between the two families — the splits will seek exactly, the verticals may drift. Untestable
  without execution; recorded as a known asymmetry.

## 6. Verdict

The four scorers do not honour the measurement-grounding constitution, and the failure is one
of **orientation, not of care**. The code is unusually well commented, its degenerate-case
policies are argued rather than asserted, and its single most elaborate derivation (C12) is
mathematically correct — I checked it. But every one of its 33 constants is justified against
the code's own reasoning, a spec line, or an aesthetic prior; **not one is justified against
`data/reference_pack/`**, which exists specifically to supply those justifications. The pack
and the scorers were written as if the other did not exist.

The concrete cost is not hypothetical. Exposure spends a 25% weight on a signal whose
under-clip tail is provably unreachable on this corpus (measured YMIN ≥ 14 vs a threshold of
5) and whose over-clip tail sits below the one measured YMAX. Composition spends 50% of its
value on a horizon detector that, on half the corpus, will lock onto the letterbox bar edge the
pack measured at row 88 and return a perfect score forever. And no scorer crops that letterbox,
even though every measurement in the pack does.

Recommended next step, in priority order: (1) crop to the measured active picture before
scoring — one change, fixes §3.3 and §3.4 together; (2) recalibrate E1/E2 against the pack's
measured YMIN/YMAX rather than the 0-255 nominal range, or drop the under-clip tail and say
why; (3) either measure a horizon-tilt distribution or relabel C2 honestly as arbitrary; (4)
unify the failure sentinels. None of this requires a new dependency.
