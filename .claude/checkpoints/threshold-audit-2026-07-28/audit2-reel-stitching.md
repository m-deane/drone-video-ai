# Audit 2 — reel_stitching unit: pacing.py, color_pinning.py, verify.py

STATUS: COMPLETE
Date: 2026-07-28
Auditor: subagent, no inherited context. Read-only outside this file. No git, no pip, no network,
no image files written, pipeline NOT run. One in-pipe `ffmpeg -f framemd5 -` measurement was taken
against read-only corpus footage (stdout only, no file written) — see H5.

Files audited (absolute):
- /Users/mac/.../src/drone_video_ai/reel_stitching/pacing.py        (121 lines)
- /Users/mac/.../src/drone_video_ai/reel_stitching/color_pinning.py (153 lines)
- /Users/mac/.../src/drone_video_ai/reel_stitching/verify.py        ( 74 lines)

Read for interaction analysis but NOT audited for constants (outside assigned unit):
edit_manifest.py, render.py, cli.py, otio_export.py (docstring + `_entry_shrink` only),
common/ffprobe.py, tests/reel_stitching/test_pacing_tolerance.py.

Classification: MEASURED | SPEC | LIBRARY_DEFAULT | DEFENSIBLE_DEFAULT | INVENTED.
Only `confidence == "measured"` leaves of `data/reference_pack/editorial_style.json` support MEASURED.

Counting rule (stated so the totals are reproducible): a "constant" is a value that could have been
chosen differently without changing the code's meaning. Mathematical/structural identities
(`current_total <= 0`, `ratio > 1.0`, `returncode != 0`, `len(a) != len(b)`, `:.3f`/`:.4f` format
precision) are NOT counted; they are listed separately in §1.4.

---

## 1. Constant tables

### 1.1 pacing.py — 2 counted constants

| # | Line | Constant | Value | Class | Trace |
|---|------|----------|-------|-------|-------|
| P1 | 23 | `DEFAULT_TOLERANCE` | 0.5 s | **SPEC** | `spec.md:68` — "Duration/pacing parameters … are honored within a defined tolerance (e.g. ±0.5s)"; `tasks.md:191` — "configurable tolerance (default ±0.5s per spec)"; `tasks.md:245` — "within ±0.5s (or the configured tolerance)". Code comment says "per spec's stated default (+/-0.5s)" and is accurate. |
| P2 | 28 | `MIN_ENTRY_DURATION` | 0.04 s | **INVENTED** | Comment: "seconds (~1 frame at 25fps)". 25 fps appears nowhere in this project's measurements. Corpus is **30/1, strictly CFR, all 8 files** (`editorial_style.json` → `/corpus_wide_invariants/frame_rate` = "30/1", `/corpus_wide_invariants/constant_frame_rate` = true, both `confidence: measured`). One real frame here is 0.033333 s, not 0.04. No spec/plan/tasks line mentions a minimum entry duration at all (grepped). |

Notes on P1: `spec.md:68` hedges with "e.g.", so the spec authorises the *concept* of a tolerance and
offers 0.5 s as the illustration; `tasks.md:191` hardens it to "default ±0.5s per spec". SPEC is the
right class. Scale check against the corpus, for the record: 0.5 s = 15 frames at the measured 30/1,
i.e. 6.0% of the shortest corpus clip (8.3 s / 249 frames). Nothing in the pack supports or
contradicts that figure — there is no measured pacing tolerance to compare it to.

Notes on P2: this is the mildest INVENTED finding in the audit and should not be inflated. The value
is *safe* in effect — 0.04 > 1/30, so it never admits a sub-one-frame entry; it is merely over-strict
by 0.0067 s. The defect is the citation, not the number: a general-knowledge PAL frame rate stands in
for a frame rate this project has measured. The fix is one line — `MIN_ENTRY_DURATION = 1.0 / 30.0`
with a citation to `/corpus_wide_invariants/frame_rate`, or better, derive it per-clip from
`SourceFileInfo.fps`, which `pacing.py` already has access to via `probe_source_file` (it currently
reads only `.duration` from it). See H6 for why this constant is inert anyway.

### 1.2 color_pinning.py — 11 counted constants, ZERO numeric

`color_pinning.py` contains **no numeric literal of any kind** outside its docstrings. Every counted
value is a string sentinel or an external tool's option name.

| # | Line | Constant | Class | Trace |
|---|------|----------|-------|-------|
| C1 | 37 | `None` in `_UNKNOWN_TAG_VALUES` | **LIBRARY_DEFAULT** | ffprobe omits an unset colour key entirely from its JSON; `common/ffprobe.py:_normalize_tag` propagates that absence as `None`. Measured: all four tags absent on 4 of 8 corpus files (§2.3). |
| C2 | 37 | `"unknown"` | **LIBRARY_DEFAULT** | FFmpeg's own sentinel — `libavutil/pixdesc.c` colour-name tables render `AVCOL_*_UNSPECIFIED` as the string `unknown` (also `color_range` values are `{unknown, tv, pc}`). |
| C3 | 37 | `"unspecified"` | **INVENTED** | No ffmpeg/ffprobe build emits `"unspecified"` for any of these four tags. Measured: **0 of 60** probe JSONs under `data/reference_pack/probe/` contain the literal string `"unknown"` *or* `"unspecified"` for any key (`grep -l '"unknown"' *.json` → 0 files). Dead branch, zero risk, but unsourced. |
| C4 | 41 | `"-color_range"` | **SPEC** | `spec.md:30` names all four flags verbatim; `plan.md:260`; `tasks.md:197`. |
| C5 | 42 | `"-color_primaries"` | **SPEC** | same. |
| C6 | 43 | `"-color_trc"` | **SPEC** | same. |
| C7 | 44 | `"-colorspace"` | **SPEC** | same. |
| C8 | 90 | `"colorprim="` | **LIBRARY_DEFAULT** | x264 `--colorprim`, reachable through ffmpeg's `-x264-params`. |
| C9 | 92 | `"transfer="` | **LIBRARY_DEFAULT** | x264 `--transfer`. |
| C10 | 94 | `"colormatrix="` | **LIBRARY_DEFAULT** | x264 `--colormatrix`. |
| C11 | 96-99 | `"tv"→fullrange=off`, `"pc"→fullrange=on` | **LIBRARY_DEFAULT** | ffmpeg `color_range` vocabulary `{unknown,tv,pc}` mapped onto x264 `--fullrange off|on`. Semantics correct (tv = limited = fullrange off). |

One latent edge in C11: the `if/elif` at 96-99 silently drops any *known-but-unmapped* `color_range`
value while `parts` may still be non-empty, producing a silent partial pin. Unreachable today —
ffprobe's `color_range` vocabulary has exactly three members and two are mapped, the third is in
`_UNKNOWN_TAG_VALUES`. Noted for completeness, not counted as a defect.

### 1.3 verify.py — 3 counted constants, ZERO numeric

`verify.py` contains **no numeric threshold, tolerance, or epsilon of any kind**. This is correct by
construction: byte-exactness is not a threshold, and introducing one would defeat spec AC2.1.

| # | Line | Constant | Class | Trace |
|---|------|----------|-------|-------|
| V1 | 33 | `"-v", "error"` | **LIBRARY_DEFAULT** | ffmpeg loglevel. |
| V2 | 35 | `"0:v:0"` | **LIBRARY_DEFAULT** | ffmpeg `-map` stream specifier, first video stream — consistent with `common/ffprobe.py`'s `video_streams[0]`. |
| V3 | 42 | `"#"` comment prefix | **LIBRARY_DEFAULT** | framemd5 muxer header prefix. Confirmed by direct measurement this session: 8 header lines emitted, every one begins `#` (`#format`, `#version`, `#hash`, `#software`, `#tb 0: 1/30`, `#media_type`, `#codec_id`, `#dimensions`). |

### 1.4 Excluded structural identities (not counted)

`pacing.py:85` `current_total <= 0`; `pacing.py:90` `ratio > 1.0` (the extension/shrink discriminant —
mathematically forced, not a tunable); `pacing.py:96,115` comparisons against parameters;
`verify.py:38` `returncode != 0`; `verify.py:53` `len(src) != len(out)`; format precisions
`:.3f`/`:.4f`. None of these could have been another value.

### 1.5 Distribution

| Class | Count | Share |
|---|---|---|
| MEASURED | **0** | 0% |
| SPEC | 5 | 31% |
| LIBRARY_DEFAULT | 9 | 56% |
| DEFENSIBLE_DEFAULT | 0 | 0% |
| INVENTED | 2 | 13% |
| **Total counted** | **16** | |

**How to read the zero.** This is not the scoring group's result wearing different clothes. A
byte-exact remux plus a metadata pass-through *should* have almost no footage-derived thresholds, and
this unit correctly has almost no thresholds at all: 2 in `pacing.py`, 0 in the other two files. The
finding is not "these constants are wrong" — 14 of 16 trace cleanly to the spec or to a documented
tool default. The finding is an **omission**: there is exactly one place in this unit where a
`confidence: measured` value from the pack was needed and is absent — the 30/1 frame grid — and that
omission is what produces the top bug (§2.1).

---

## 2. Interaction bugs vs the measured corpus

Corpus identified by matching `/shot_length_distribution/all_files/values_s`
(`[8.3, 14.566667, 14.566667, 15.0, 15.0, 15.0, 27.1, 27.1]`) against
`data/reference_pack/probe/*.json`; all 8 files confirmed present at
`/Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples/`.

| File | W×H | dur s | frames | color_range | color_space | prim | trc |
|---|---|---|---|---|---|---|---|
| split_001_s70 | 1280×720 | 15.000000 | 450 | tv | bt709 | absent | absent |
| split_002_s69 | 1280×720 | 15.000000 | 450 | tv | bt709 | absent | absent |
| split_003_s66 | 1280×720 | 8.300000 | 249 | tv | bt709 | absent | absent |
| split_004_s65 | 1280×720 | 15.000000 | 450 | tv | bt709 | absent | absent |
| viral_test_v2 | 1080×1920 | 14.566667 | 437 | absent | absent | absent | absent |
| viral_test_v2_4k | 2160×3840 | 14.566667 | 437 | absent | absent | absent | absent |
| instagram_reel_test | 1080×1920 | 27.100000 | 813 | absent | absent | absent | absent |
| instagram_reel_v34_all_kb_full | 2160×3840 | 27.100000 | 813 | absent | absent | absent | absent |

All 8: h264 High, yuv420p, 8-bit, `r_frame_rate` 30/1, `time_base` 1/15360, zero audio streams.
Matches `editorial_style.json` `/colour_treatment/colour_tagging/*` and
`/corpus_wide_invariants/*` exactly (both `confidence: measured`).

### 2.1 TOP BUG — framemd5 verification is not invariant to sub-frame seek phase, and pacing.py guarantees the phase will differ

**Anchor: `verify.py:60` (whole-line comparison). Trigger: `pacing.py:102`.**

Measured this session, in-pipe, on `split_001_s70.mp4` (read-only source, stdout only, nothing
written to disk):

```
ffmpeg -v error -ss <SS> -i split_001_s70.mp4 -t 0.134 -map 0:v:0 -f framemd5 -
```

| `-ss` | lines | pts column | first hash |
|---|---|---|---|
| 0.0 (on-grid) | 5 | 0,1,2,3,4 | a0ad2f7b… |
| 5.0 (on-grid) | 5 | 0,1,2,3,4 | df217629… |
| 5.0166 (off-grid) | **4** | **1,2,3,4** | b84f73d5… |
| 5.02 (off-grid) | 5 | 0,1,2,3,4 | b84f73d5… |

Two facts follow, both measured, neither hypothetical:

1. **framemd5 lines carry timestamps.** The emitted format is
   `stream, dts, pts, duration, size, hash`. `verify.py:42` strips only `#` header lines and returns
   the full data lines; `verify.py:60-66` compares them with `if s != o`. So `dts` and `pts`
   participate in the equality test even though the docstring calls them "per-frame MD5 hash lines".
2. **The pts column is a function of sub-frame seek phase, not of content.** `-ss 5.0166` and
   `-ss 5.02` return the *same pixels* — hash `b84f73d5…` is the first line of both — but numbered
   `pts=1` in one and `pts=0` in the other, and the frame count for an identical `-t` differs (4 vs
   5). ffmpeg offsets output timestamps by the requested `-ss` and rounds the residual into the
   1/30 timebase; the residual's sign decides 0 vs 1.

Consequence: `verify_frame_range` compares a source-side seek to `check.src_start` against an
output-side seek to `check.out_start`. It is sound only while **both** land within ±1/60 s of a frame
boundary in their respective files. `pacing.py:102` —

```python
new_duration = e.duration * ratio
new_out_tc = e.in_tc + new_duration
```

— applies a real-valued `ratio` (`pacing.py:87`) with no quantisation to any frame grid. The resulting
off-grid durations flow into `render.py:282-288`, where `cursor` accumulates them as raw floats and
becomes `FrameRangeCheck.out_start`. `in_tc` is never moved by pacing, so the source side stays
on-grid while the output side does not. The pts columns then diverge and every line mismatches —
`VerificationError` at frame 0 of a byte-perfect render — or the frame counts differ and the
`len(src_hashes) != len(out_hashes)` guard at `verify.py:53` fires first.

**Why this is corpus-specific, not generic.** With untrimmed entries every corpus duration is an
exact multiple of the measured 30/1 frame period (15.0 = 450 f, 8.3 = 249 f, 27.1 = 813 f,
14.566667 ≈ 437 f), so `cursor` stays on-grid and verification passes. It is precisely
`--target-duration` — `pacing.py`'s entire reason to exist, and spec AC2.5 — that puts the pipeline
into the failing regime. The one corpus property that makes the bug reachable (a fine, exact, strictly
constant frame grid) is a `confidence: measured` fact the module never consults.

**The project already solved this one module over, and did not carry it across.**
`otio_export.py:179` rounds every `RationalTime` to the whole-frame grid at `EDIT_MANIFEST_RATE =
30.0`, and its docstring at `otio_export.py:169-178` records the discovery in the author's own words:
a fractional-frame duration "arises routinely from `_entry_shrink`'s half-transition-duration math on
ordinary, non-adversarial transition durations", and rounding is "required, not cosmetic". So the
*paper* edit (the .otio/.edl) is quantised to the frame grid; the *rendered* edit is not. Same
project, same session, same measured 30 fps — one path fixed, the sibling path untouched.

**Fix shape** (not applied — read-only audit): quantise in `pacing.py` at the moment of trim, e.g.
`new_out_tc = e.in_tc + round(new_duration * fps) / fps` with `fps` taken from `probe_source_file`
(already imported at `pacing.py:20`, currently used only for `.duration`), and cite
`/corpus_wide_invariants/frame_rate`. Quantising at the source removes the drift from `render.py`'s
cursor and from `verify.py` simultaneously.

### 2.2 SECOND BUG — verify.py passes vacuously on two empty hash lists

`verify.py:53` compares `len(src_hashes) != len(out_hashes)`, then `verify.py:60` zips them. If both
ffmpeg calls exit 0 having emitted no data lines — which is what a seek past EOF produces — the
lengths are equal (`0 == 0`), the `zip` is empty, and `verify_frame_range` **returns success having
compared nothing**. That is reachable by the same drift as §2.1: `cursor` accumulating past the real
end of a run's output file. A verifier whose failure mode is silent success is the one thing spec
AC2.1 (`spec.md:64`, "not a manual/visual spot check") exists to prevent. One line fixes it: raise if
`not src_hashes`.

### 2.3 THIRD FINDING — the delivered file is never verified

`verify_render_result` (`verify.py:69-74`) iterates `result.run_outputs` only. It never touches
`result.output_path` — the final assembled reel the user is handed — and never touches
`result.transition_outputs` at all. The final assembly is a *second* `-c copy` concat pass
(`render.py:359-366`) over the intermediates, and any defect it introduces (timestamp rewriting, edit
lists, segment ordering) is outside everything verify.py inspects.

The module docstring justifies checking the isolated per-run files ("it removes any ambiguity from
seeking across a codec-parameter boundary inside the final, possibly transition-containing, merged
output") and that reasoning is sound. But spec AC2.1 (`spec.md:64`) is written about "the rendered
output's stream-copied regions", and the rendered output is the merged file. The gap is real, it is
argued rather than hidden, and closing it needs a check that the final file's segments are the
intermediates — not a relaxation of the framemd5 comparison.

### 2.4 FOURTH FINDING — pacing.py has no knowledge of the transition budget render.py will demand

`pacing.py` scales entry durations but holds every `transition_to_next.duration` fixed
(`pacing.py:78-83` computes `overlap` from the *original* manifest and never revises it). Its only
floor is `MIN_ENTRY_DURATION = 0.04 s`. The floor that actually binds is `render.py:192`
(`eff_out <= eff_in` → `RenderError`), and `render.py:188-189` removes the **full** transition
duration from each side, so an interior entry must exceed `dur_prev + dur_next`.

Worked against the measured corpus (8 entries, content total 136.633334 s, shortest 8.3 s, 1.0 s
crossfade on all 7 joins): an interior entry must survive a 2.0 s bite, so
`8.3 × ratio > 2.0` → `ratio > 0.241` → `target + 7.0 > 32.93` → **target > ≈25.9 s**. Ask for a 25 s
reel from the eight corpus clips with one-second crossfades and `pacing.py` certifies it within
±0.5 s, writes the paced manifest, and `render.py` then refuses to render it. `MIN_ENTRY_DURATION`
never gets a look in — see H6 for the arithmetic showing it binds only below a ~0.66 s target.

### 2.5 FIFTH FINDING — the AC2.5 tolerance test is a tautology (the one the brief was hunting for, one module over)

`tests/reel_stitching/test_pacing_tolerance.py:34`:

```python
paced = apply_target_duration(manifest, target, tolerance=DEFAULT_TOLERANCE)
assert abs(paced.content_duration - target) <= DEFAULT_TOLERANCE
```

`apply_target_duration` raises `PacingError` at `pacing.py:115-120` when exactly that predicate is
false. Any manifest it *returns* satisfies the assertion by construction; the assertion can only be
reached in the passing state. The test never renders, never probes the output, and never measures a
file. Its fixture uses `fps=10` clips with a 12 s → 6 s halving, so every duration in it lands on the
frame grid by luck of the numbers and the §2.1 regime is never entered.

So AC2.5's guarantee, as currently tested, is a property of float arithmetic over a dataclass, not a
property of a reel. `spec.md:68` asks for the target to be honoured "in test runs" — which reads as a
claim about rendered output. Note this cuts against the repo's own Tests-as-Truth principle: the test
passes, but the scenario it appears to cover is not the scenario it covers.

### 2.6 SIXTH FINDING (cross-module, flagged not asserted) — two different transition models

`render.py:188-189` takes the **full** transition duration from the tail of A and from the head of B.
`otio_export.py:_entry_shrink` (lines 185-199) takes **half** from each side. Both preserve the same
total timeline length, and half-each-side is the normal OTIO `Transition` in_offset/out_offset
convention, so this may be deliberate. Two consequences are real regardless: the exported EDL places
the cut point `D/2` away from where the render places it, and the two modules' feasibility thresholds
differ by exactly 2× (`OTIOExportError` at `duration <= D/2 + D/2`, `RenderError` at
`duration <= D + D`), so a manifest can export a valid EDL and fail to render. `otio_export.py` is
outside my assigned unit and I read only its docstring and `_entry_shrink`; treat this as a pointer
for whoever audits that file, not as a confirmed defect.

---

## 3. Hypotheses tested — result reported either way

**H1 — "pacing.py is where a shot-length or cut-rhythm constant would live, and the pack found no cut
rhythm to derive one from, so pacing.py probably invented one."**
**REFUTED. pacing.py contains no shot-length, cut-rate, or rhythm constant at all.** It is purely
proportional: one global scale factor across every entry (`pacing.py:87`), applied from each entry's
tail, with the docstring stating why ("Milestone 1 has no per-clip priority signal to weight
unevenly"). None of `/shot_length_distribution/mean_s` (17.079167), `/median_s` (15.0),
`/cut_rhythm/cuts_per_minute` (0.0), or `/cut_rhythm/hypothetical_assembly_shot_length_s` (13.325)
appears anywhere in the file — and none *should*, because the pack measured
`cuts_per_minute = 0.0` and there was no rhythm to derive. The brief anticipated a risk here; the
code does not take it. This is the cleanest positive result in the audit and it should be recorded as
such rather than buried.

**H2 — "color_pinning.py encodes something about the chroma-inert drone_aerial grade or the
2.352941 baked-in letterbox."**
**REFUTED.** `color_pinning.py` contains zero numeric constants, zero geometry, zero pixel
operations, and no reference to grading, saturation, crop, aspect, or the legacy `post_processing`
block. `/colour_treatment/declared_grade` (drone_aerial @ 0.65, "PARTIALLY FALSIFIED — luma-only,
chroma untouched") and `/letterbox/horizontal_split_family/*` (active 1280×544 in coded 1280×720,
bars at 88/631, bar_luma 16, ratio 2.352941, content_cost 24.4%) are correctly absent: the letterbox
is baked into source *pixels*, `spec.md:44` forbids removing it, and stream copy preserves it byte for
byte. Contrast with the confirmed scoring-group defect (24.4% of every scored frame being synthetic
black on 4 of 8 files): in *this* unit the letterbox is genuinely inert, and inert for the right
reason. `/speed_ramp_policy/measured_effect` ("NO-OP") is likewise irrelevant here — no `setpts`
speed usage exists in the unit, which `tests/reel_stitching/test_forbidden_filters_lint.py` enforces
mechanically over `render.py` and `color_pinning.py` source text.

**H3 — "the module docstrings' stated grounding about colour tags is accurate."**
**REFUTED BY MEASUREMENT.** `color_pinning.py:9-11` claims, "confirmed in this repo's own sample
footage … these tags frequently read the literal string `\"unknown\"` or are entirely absent";
`common/ffprobe.py:5-8` goes further — "real sample footage in this repo reports … as the literal
string `\"unknown\"` … on **every** sample clip"; `plan.md:18-20` is the origin of the claim.
Measured: **zero** of the 60 probe JSONs in `data/reference_pack/probe/` contain the literal string
`"unknown"` for any key, for the 8-file corpus or the archive cross-validation set. The corpus's real
state (`/colour_treatment/colour_tagging/*`, `confidence: measured`) is bt709/tv with primaries and
transfer *absent* on the four splits, and all four *absent* on the four verticals. The code's
**behaviour** is correct anyway — `None` and `"unknown"` are handled identically at
`color_pinning.py:68` — so this is a documentation/grounding defect, not a behavioural one, and it is
the reason C3 (`"unspecified"`) exists as dead code. Worth correcting because the false claim is
currently load-bearing for a reader deciding whether the module was validated against real footage.

**H4 — "verify.py is a tautology that cannot fail."**
**REFUTED as stated, but two real gaps found.** Not vacuous: `render.py:283-288` emits one
`FrameRangeCheck` per entry, so every run carries ≥1 check and `verify_render_result` always compares
independently-produced hash lists. It is a genuine external, tool-grounded check (Constitution rule
6). The gaps are §2.2 (empty-vs-empty passes silently) and §2.3 (the delivered file is never
verified). The tautology the brief was hunting for does exist — it is in
`test_pacing_tolerance.py:34`, see §2.5.

**H5 — "verify.py's line comparison is invariant to sub-frame seek placement."**
**REFUTED BY MEASUREMENT.** See §2.1 for the measurement table and reasoning. This is the top bug.

**H6 — "MIN_ENTRY_DURATION is the floor that binds when pacing shrinks aggressively."**
**REFUTED.** On the measured corpus (8 entries, 136.633334 s total, shortest 8.3 s), the 0.04 s floor
binds only when `8.3 × ratio < 0.04` → `ratio < 0.00482` → target below ≈0.66 s. No user asks for a
0.66-second reel. The floor that actually binds is `render.py:192`'s effective-duration check (§2.4),
which pacing.py cannot see. `MIN_ENTRY_DURATION` is an inert guard — which is also why P2's
25-fps-derived value has never caused visible harm, and why it survived unexamined.
(`test_pacing_tolerance.py:74` reaches it only with a deliberately absurd `target=0.05`.)

**H7 — "color_pinning's tag-agreement check is satisfiable across this corpus."**
**PARTIALLY REFUTED, with a mitigation that matters.** The corpus splits into two disjoint colour-tag
classes — 4 splits (`tv` / `bt709` / absent / absent) and 4 verticals (all absent) —
so `_assert_tags_agree` (`color_pinning.py:105-115`) raises on every cross-family pair: **16 of the
28** unordered clip pairs (57%) cannot carry a transition. Mitigation, established by measurement in
§2.2's table: those same 16 pairs also differ in coded resolution (1280×720 vs 1080×1920 vs
2160×3840), and ffmpeg `xfade` requires identical dimensions, so they were unrenderable regardless —
the colour check merely fails first, and with a clearer message than ffmpeg would give. **Not a
defect in effect.** Within each family the check passes and the pin round-trips correctly: the splits
yield `colormatrix=bt709:fullrange=off` (primaries/transfer stay unsignalled, so ffprobe on the output
omits them exactly as it does on the source), and the verticals yield `to_x264_params() → None`, so no
`-x264-params` is passed and libx264 writes no colour VUI — output absent, source absent, AC2.2
satisfied. The `to_x264_params` mechanism and its empirical justification
(`color_pinning.py:80-86`, "this build's libx264 wrapper does not reliably propagate the generic
`-color_primaries`/`-color_trc` output flags into the encoded VUI") is the single best-grounded piece
of engineering in this unit: a claim about tool behaviour, tested in-environment, with the workaround
documented at the point of use.

**H8 — "hard cuts enforce the same colour-tag agreement that transitions do."**
**REFUTED.** `_check_stream_copy_compatible` (`render.py:142-152`) checks codec/width/height/pix_fmt/
time_base and **not** the four colour tags, so a hard-cut run may freely mix the two measured colour
classes while a transition between the identical pair hard-fails. Whether the merged output then
carries the first segment's tags, or each segment's own in-band VUI, depends on ffmpeg's MP4 `colr`
box handling on `-c copy` concat — **I did not test this** (it needs a render, which is out of scope
here) and I will not assert either branch. Flagged as an open question for whoever audits `render.py`.

---

## 4. Verdict

`pacing.py` / `color_pinning.py` / `verify.py` are 16 counted constants: **0 MEASURED, 5 SPEC,
9 LIBRARY_DEFAULT, 0 DEFENSIBLE_DEFAULT, 2 INVENTED** (`MIN_ENTRY_DURATION = 0.04` derived from a
25 fps that this project has never measured; `"unspecified"`, a colour sentinel no ffprobe emits —
0 hits in 60 probe JSONs). Both INVENTED values are currently inert, and I am not going to dress them
up: this is a carefully written, heavily and honestly commented unit, and it is **not** a second
instance of the scoring group's "built as if the pack did not exist". `color_pinning.py` and
`verify.py` correctly contain no footage-derived thresholds at all, `pacing.py` invents no cut rhythm
where the pack found none (H1), and the letterbox and the chroma-inert grade are correctly absent
from all three files (H2).

The failure is a single **omission**, not a set of bad numbers. The corpus's frame grid — 30/1,
strictly CFR, all 8 files, `confidence: measured` — is the one measured value this unit needed and
never consulted. `pacing.py:102` produces off-grid cut points; `render.py`'s float cursor carries the
drift; `verify.py:60` compares framemd5 lines whose `dts`/`pts` columns I measured to be a function of
sub-frame seek phase rather than of content. The result is that the pipeline's own byte-exactness
check fails on correct renders in exactly the configuration `pacing.py` exists to produce, while the
AC2.5 test that is supposed to cover pacing asserts something `apply_target_duration` guarantees by
construction (§2.5) and never renders anything. The project already learned this lesson at
`otio_export.py:179` and wrote it down in that file's docstring; the fix was applied to the exported
EDL and not to the rendered reel.

Consistency with the sibling audits: same root pattern, different surface. The common/ group found a
fabricated value and a measured value are indistinguishable once written to the manifest; here, a
verified render and an unverified one are indistinguishable once §2.2's empty-vs-empty path is taken,
and a paced manifest's certified duration is indistinguishable from a measured one because nothing
ever measures it.

Highest-value fixes, in order: (1) quantise `new_out_tc` to the source's real fps in `pacing.py:102`,
citing `/corpus_wide_invariants/frame_rate`; (2) `raise` on empty hash lists in `verify.py:53`;
(3) make `test_pacing_tolerance.py` assert against a rendered file rather than against
`content_duration`; (4) give `pacing.py` the transition budget `render.py:192` will demand (§2.4);
(5) correct the `"unknown"` grounding claim in `color_pinning.py:9-11` and `common/ffprobe.py:5-8`,
and delete `"unspecified"`.
