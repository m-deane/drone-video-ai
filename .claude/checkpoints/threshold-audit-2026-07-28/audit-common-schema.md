# Threshold Audit — `common/` group (ffprobe.py, manifest.py, schema.py)

Date: 2026-07-28 · Static audit only (src/ never executed, imported, or installed).
Scope: the shared substrate — the ffprobe wrapper, the highlight-manifest dataclasses,
and the structural validators for the highlight manifest + edit manifest.

Files read in full this session:
- `/Users/mac/.../src/drone_video_ai/common/ffprobe.py` (190 L)
- `/Users/mac/.../src/drone_video_ai/common/manifest.py` (311 L)
- `/Users/mac/.../src/drone_video_ai/common/schema.py` (300 L)
Ground truth read this session:
- `data/reference_pack/editorial_style.json` (all ~110 confidence-labelled leaves enumerated)
- `data/reference_pack/exemplars/bbc-earth-aerial.json`
- `data/reference_pack/probe/*.json` (all 8 corpus + 6 archive masters re-queried directly)
- `.claude/specs/drone-video-pipeline/spec.md` (94 L), `plan.md` (425 L), `tasks.md` (361 L)
- corroborating reads outside the group (cited, not audited): `reference_pack/schema.py`,
  `highlight_extraction/scoring_composition.py`, `reel_stitching/render.py`,
  and the 8 real legacy `manifest.json` files under `data/raw/` + `00-assets/`.

---

## 0. Counting rule (disclosed, so the distribution can be re-derived)

A "constant" here = a value the code asserts that could have been chosen differently:
numeric literals, string sentinels, tool-flag values, and the **required-key sets** the
schema asserts (this group's whole product is *what a manifest may assert*, so the key
sets are its primary constants, not incidental).

Excluded from the count, listed as notes instead: docstring *illustrative* examples,
re-use sites of an already-counted value, and `from_dict` default-fill *policies*
(these appear under Interaction Bugs, where their consequence lives).

Classification tie-breaks used:
- A value is **INVENTED** when it is a bare, unexplained value that silently substitutes
  for data the code failed to obtain and then propagates into output as if it were real.
- A structural selector with one obvious correct answer (`streams[0]`) is
  **DEFENSIBLE_DEFAULT**, not INVENTED, even when unexplained.
- An ffmpeg/ffprobe flag value (`-v error`, `csv=p=0`, `v:0`) is **LIBRARY_DEFAULT**.

---

## 1. Distribution

| Class | Count | Share |
|---|---:|---:|
| MEASURED | **0** | 0% |
| SPEC | 28 | 54% |
| LIBRARY_DEFAULT | 6 | 12% |
| DEFENSIBLE_DEFAULT | 10 | 19% |
| INVENTED | 8 | 15% |
| **Total** | **52** | |

Per file: ffprobe.py 17 · manifest.py 12 · schema.py 23.

**MEASURED = 0 is the honest headline and it is only half a criticism.** This is an I/O and
schema layer, not a thresholding layer; there is no threshold here that *should* have been
calibrated on footage. But it also means the shared contract encodes **zero knowledge of the
corpus it was built for** — see §4.1 (no active-picture field) and §4.5.

---

## 2. Full inventory — `common/ffprobe.py`

| # | Constant / value | Line | Class | Derivation found? |
|---|---|---:|---|---|
| F1 | `ffprobe_bin: str = "ffprobe"` | 84, 145 | LIBRARY_DEFAULT | PATH-resolved binary name; plan.md L112–114 fixes ffprobe as an external subprocess binary, not a pip dep. |
| F2 | `-v error` | 93, 159 | LIBRARY_DEFAULT | ffmpeg loglevel enum member. |
| F3 | `-of json` | 96 | LIBRARY_DEFAULT | ffprobe writer name. |
| F4 | `-of csv=p=0` | 163 | LIBRARY_DEFAULT | ffprobe csv writer, `p=0` = suppress section prefix. |
| F5 | `-select_streams v:0` | 160 | LIBRARY_DEFAULT | ffmpeg stream-specifier syntax. |
| F6 | `-skip_frame nokey` | 161 | LIBRARY_DEFAULT | ffmpeg AVDiscard enum member (keyframes only). |
| F7 | `_parse_fps` → `0.0` when `rate_str` falsy | 67 | **INVENTED** | none stated. Silent substitution — see IB-1. |
| F8 | `_parse_fps` → `0.0` on ValueError/ZeroDivisionError | 71 | **INVENTED** | none stated. |
| F9 | `duration = 0.0` when no duration tag | 123 | **INVENTED** | none stated. |
| F10 | `duration = 0.0` on ValueError | 125 | **INVENTED** | none stated. |
| F11 | `width` default `0` | 131 | **INVENTED** | none stated. |
| F12 | `height` default `0` | 132 | **INVENTED** | none stated. |
| F13 | `codec` default `""` | 134 | **INVENTED** | none stated. |
| F14 | `pix_fmt` default `""` | 135 | **INVENTED** | none stated. |
| F15 | `video_streams[0]` — pick first video stream | 118 | DEFENSIBLE_DEFAULT | unexplained in code, but single obvious choice; **and empirically safe on this project's material — see §3.2**. |
| F16 | `line.split(",")[0]` — first CSV token | 183 | DEFENSIBLE_DEFAULT | explained in-line: ffprobe `csv=p=0` emits a trailing empty field on the first row. Genuine, documented derivation. |
| F17 | `time_base: Optional[str] = None` field default | 49 | DEFENSIBLE_DEFAULT | explained in-line: "Optional/defaulted so existing Capability 1 call sites and tests are unaffected." Honest additive-field note. |

**Docstring examples (not counted, noted for grounding hygiene):** `"1/12800"` (L46) and
`"30000/1001"` (L65) are offered as illustrative values. Neither occurs anywhere in this
project's measured material: all 8 corpus files probe `time_base=1/15360, r_frame_rate=30/1`;
the 6 archive masters probe `1/60000, 60000/1001`. Zero consequence (they are `e.g.`), but in
a repo whose constitution forbids carrying over "what drone footage usually looks like", an
illustrative constant that matches nothing measured is worth replacing with a real one.

### What ffprobe.py gets *right* against the pack (verified, not assumed)

Re-ran the extraction logic by hand against `data/reference_pack/probe/*.json`:

| corpus file | streams v/a | w×h | r_frame_rate | avg_frame_rate | stream dur | format dur |
|---|---|---|---|---|---|---|
| split_001_s70 | 1/0 | 1280×720 | 30/1 | 30/1 | 15.000000 | 15.000000 |
| split_002_s69 | 1/0 | 1280×720 | 30/1 | 30/1 | 15.000000 | 15.000000 |
| split_003_s66 | 1/0 | 1280×720 | 30/1 | 30/1 | 8.300000 | 8.300000 |
| split_004_s65 | 1/0 | 1280×720 | 30/1 | 30/1 | 15.000000 | 15.000000 |
| instagram_reel_test | 1/0 | 1080×1920 | 30/1 | 30/1 | 27.100000 | 27.100000 |
| viral_test_v2 | 1/0 | 1080×1920 | 30/1 | 30/1 | 14.566667 | 14.566667 |
| instagram_reel_v34_all_kb_full | 1/0 | 2160×3840 | 30/1 | 30/1 | 27.100000 | 27.100000 |
| viral_test_v2_4k | 1/0 | 2160×3840 | 30/1 | 30/1 | 14.566667 | 14.566667 |

- Every corpus file exposes a stream-level `duration`, so the `vstream.get("duration") or
  fmt.get("duration")` precedence never falls back, and both agree to 6 dp anyway.
- `r_frame_rate == avg_frame_rate` on all 8 — consistent with the pack's measured strict CFR
  (`editorial_style.delivery_surfaces[*].cfr = true`, confidence `measured`), so choosing
  `r_frame_rate` over `avg_frame_rate` is correct here and produces exactly `30.0`.
- Durations produced would be `[15.0, 15.0, 8.3, 15.0, 27.1, 14.566667, 27.1, 14.566667]`,
  matching `editorial_style.shot_length_distribution.all_files.values_s` (`measured`) exactly.
- The module docstring's colour-tag claim is **confirmed against the pack**: it says the tags
  read `"unknown"` or are absent. Pack: `colour_treatment.colour_tagging.vertical_social_family`
  = all four `null`; `horizontal_split_family` = `bt709`/`tv` with primaries+transfer `null`
  (both `measured`). The pass-through-never-default policy is exactly right for that reality.

**On balance ffprobe.py's happy path is measurement-faithful for this corpus.** Its defect is
entirely in the failure path (§4, IB-1).

---

## 3. Hypothesis tests (stated as hypotheses, tested, reported either way)

### 3.1 Does the `letterbox` omission in `FORBIDDEN_POST_PROCESSING_KEYS` matter? — **YES, CONFIRMED**
See IB-2. Tested against the 8 real legacy manifests on disk.

### 3.2 Does `video_streams[0]` pick a thumbnail on the DJI masters? — **NO. Hypothesis refuted.**
Five of the six raw camera-original masters carry **two** video streams (an HEVC 3840×2160
main stream plus a 960×540 MJPEG cover-art stream with `disposition.attached_pic = 1`).
`probe_source_file` has no `attached_pic == 0` filter, so it is purely order-dependent.
Measured stream order in all five: main video at `index 0`, MJPEG cover art at `index 3`.
So `[0]` selects correctly on every file this project has. Reporting this as **LATENT
robustness debt, not a live bug** — a one-line `disposition.attached_pic != 1` filter would
make it order-independent, but nothing in the measured material currently breaks.

### 3.3 Is `avg_frame_rate` vs `r_frame_rate` a live divergence? — **NO.**
Identical on all 8 corpus files (table above). Consistent with pack `cfr = true` (`measured`).

---

## 4. Full inventory — `common/manifest.py`

| # | Constant | Line | Class | Derivation found |
|---|---|---:|---|---|
| M1 | `MANIFEST_VERSION = 3` | 30 | SPEC | plan.md L230 "`version` bumps to 3 at that point since the composite-score computation changes"; tasks.md 1.24 "`MANIFEST_VERSION` bumped from 2 to 3". |
| M2 | `ScoringWeights.composition: float = 0.0` | 76 | SPEC | plan.md L152 "MUST be 0.0 in Milestone 1". Retained as the `default-v1` value. |
| M3 | `SegmentScores.composition: Optional[float] = None` | 143 | SPEC | plan.md L181 `"composition": null // always null in Milestone 1 output`. |
| M4 | `Segment.gate_status = "passed"` | 173 | SPEC | plan.md L186 `"gate_status": "passed"`. |
| M5 | `ExcludedSegment.gate_status = "failed"` | 207 | SPEC | plan.md L195 `"gate_status": "failed"`. |
| M6 | normalization.sharpness = `"in-video min-max over sampled frames -> [0,1]"` | 126 | SPEC | plan.md L167 — **verbatim match**. |
| M7 | normalization.exposure = `"1 - (clipped-pixel fraction from histogram) -> [0,1]"` | 127 | SPEC | plan.md L168 — **verbatim match**. |
| M8 | normalization.motion_smoothness = `"in-video min-max over inverse jerk magnitude -> [0,1]"` | 128 | SPEC | plan.md L169 — **verbatim match**. |
| M9 | `0.5` / `0.5` blend inside the composition normalization prose | 129–133 | SPEC | tasks.md L153 "combined … via an unweighted 0.5/0.5 average". Matches `scoring_composition.py` L71. |
| M10 | `w/3`, `h/3` rule-of-thirds divisor in the prose | 131–132 | DEFENSIBLE_DEFAULT | geometric definition of "rule of thirds"; spec L21 names the technique. Matches `scoring_composition.py` L39. |
| M11 | `|tilt_deg|/20` cap in the prose | 132–133 | DEFENSIBLE_DEFAULT | traces to `scoring_composition.py:161 MAX_HORIZON_TILT_DEGREES = 20.0`, whose docstring (L51–54) *explains* the choice ("intentional aerial framing tilt rarely exceeds this") but cites **no measurement**. See §4.6 — this one can never be pack-grounded. |
| M12 | `to_json(indent=2)` | 287 | DEFENSIBLE_DEFAULT | unexplained, but purely cosmetic — no output semantics. (Note: repo's own `python3 -m json.tool` convention defaults to indent 4; harmless divergence.) |

### 4.1 Cross-artifact staleness check — ~~**PASSED**~~ **PARTIALLY REVERSED — see §9 C2**
(The composition-prose check below did pass. But a *same-file* stale version claim was missed
on the first pass and is recorded as IB-7.)
This repo's documented recurring failure mode is a fix landing in one artifact while a stale
twin survives elsewhere. Checked the composition prose in `manifest.py:129–133` against its
source of truth `scoring_composition.py` (0.5/0.5 at L71, `sqrt((w/3)**2+(h/3)**2)` at L39,
`MAX_HORIZON_TILT_DEGREES = 20.0` at L161): **all three restatements are accurate.** And the
composition string was correctly *updated* away from plan.md's Milestone-1 text
("not scored in this schema version") per tasks.md 1.24, rather than left stale. This is the
failure mode not happening — worth recording as a positive.

---

## 5. Full inventory — `common/schema.py`

| # | Constant | Line | Class | Derivation found |
|---|---|---:|---|---|
| S1 | `FORBIDDEN_POST_PROCESSING_KEYS = {"post_processing","color","stabilize","auto_speed"}` | 91 | SPEC (**incomplete — IB-2**) | spec L44 / L24 enumerate `color`, `stabilize`, **`letterbox`**, `auto_speed`. `letterbox` is absent from the set. |
| S2 | highlight top-level required: 8 keys | 23–32 | SPEC | plan.md L131–206 — exact key set. |
| S3 | `source_file` required: 8 keys | 37–39 | SPEC | plan.md L134–143 — exact key set. |
| S4 | `scoring_weights` required: `weights_version`, `weights` | 43 | SPEC | plan.md L145–148. |
| S5 | weights required: the 4 signal names | 47 | SPEC | plan.md L149–157. |
| S6 | `candidate_boundaries` required: 3 keys | 53 | SPEC | plan.md L159–164. |
| S7 | `normalization` required: 4 keys | 57 | SPEC | plan.md L166–171. |
| S8 | `segments[]` required: 7 keys | 63–67 | SPEC | plan.md L173–188. |
| S9 | `excluded_segments[]` required: 7 keys | 71–77 | SPEC | plan.md L190–198. |
| S10 | `summary` required: 6 keys | 80–84 | SPEC | plan.md L200–206. |
| S11 | `version` must be `int` | 132 | SPEC | plan.md L134 `"version": 2, // int`. |
| S12 | `segments[i].gate_status == "passed"` enforced | 177 | SPEC | plan.md L186 + AC1.2 (failing segments belong in `excluded_segments`). |
| S13 | `excluded_segments[i].gate_status == "failed"` enforced | 194 | SPEC | plan.md L195. |
| S14 | `gate_failures` must be non-empty | 198 | SPEC | plan.md L197 "non-empty list of: …". |
| S15 | edit-manifest required: `version`,`target_duration`,`entries` | 220 | SPEC | plan.md L237–239. |
| S16 | entry required: `clip_path`,`in_tc`,`out_tc`,`transition_to_next` | 228 | SPEC | plan.md L241–252. |
| S17 | transition required: `type`,`duration` | 234 | SPEC | plan.md L246–250. |
| S18 | `type == "cut"` ⇒ `duration != 0.0` is an error | 289 | SPEC | plan.md L250 "must be 0.0 when type == `cut`" — verbatim. |
| S19 | edit `version` must be `int` | 265 | SPEC | plan.md L238. |
| S20 | `duration < 0.0` rejected | 293 | DEFENSIBLE_DEFAULT | domain constraint on a duration; not spec-stated, but not arbitrary either. |
| S21 | `out_tc <= in_tc` rejected (strict increase) | 283 | DEFENSIBLE_DEFAULT | not spec-stated; a zero-length entry is meaningless. Docstring states the rule. |
| S22 | `entries` must be non-empty | 275 | DEFENSIBLE_DEFAULT (**over-attributed**) | docstring says "Per plan.md"; grepped plan.md + tasks.md for "non-empty" — the only hits are L197 (`gate_failures`) and tasks.md L142 (`normalization`). **The `entries` non-empty rule is not in plan.md.** Sound rule, mis-cited source. |
| S23 | final entry must be the `{"type":"cut","duration":0.0}` sentinel | 295–300 | DEFENSIBLE_DEFAULT (**over-attributed**) | same: docstring says "Per plan.md"; grepped for "final entry"/"last entry"/"sentinel" — **zero hits in plan.md or tasks.md**. The reasoning given in-code ("there is no clip after the last entry") is genuinely sound; the citation is not. |

**S22/S23 note.** These are good rules with a bad provenance label. In a repo whose
constitution forbids asserting a source you have not verified, a docstring that says
"Per plan.md:" and then lists four rules of which two are not in plan.md is exactly the
citation drift the constitution targets. Fix is one word ("Per plan.md, plus two additional
structural invariants:"), not a code change.

---

## 6. Interaction bugs — individually defensible, wrong or inert against THIS corpus

### IB-1 — ffprobe.py silently fabricates `0` measurements, violating the policy its own docstring states. CONFIRMED.
`ffprobe.py:1–12` states the module's governing principle explicitly: it "never substitutes a
default value" for colour tags, so consumers "can tell 'asserted unknown' apart from 'tag
absent'". The same function then does the opposite for six other fields: `fps→0.0` (L67, L71),
`duration→0.0` (L123, L125), `width→0` (L131), `height→0` (L132), `codec→""` (L134),
`pix_fmt→""` (L135). Each collapses "ffprobe did not tell me" into a value that is written to
`source_file` and read downstream as a measurement.

Why it bites *this* corpus specifically: every one of those zeros is a **measurably impossible**
value here. Pack (`measured`): fps `30/1` on all 8; dimensions 1280×720 / 1080×1920 / 2160×3840;
durations 8.3–27.1 s; codec `h264 High`; `yuv420p`. A `0` in any of those fields can only mean
probe failure — yet `schema.py:135–139` validates `source_file` by **key presence only**,
type- and range-checking nothing. A manifest asserting `{"fps": 0.0, "width": 0, "height": 0,
"duration": 0.0, "codec": "", "pix_fmt": ""}` passes `validate_highlight_manifest()` cleanly.
Downstream, `reel_stitching/otio_export.py:120` declares it assumes a fixed frame rate; a 0.0
fps reaching a RationalTime is not a value any timeline can represent.
Confidence: CONFIRMED (read both the producer and the validator).

### IB-2 — `letterbox` is missing from the forbidden-key set, and letterbox is the one legacy field this corpus provably carries. CONFIRMED.
`schema.py:91` forbids `{"post_processing", "color", "stabilize", "auto_speed"}`. Spec L44 and
L24 both enumerate **four** legacy pixel-editing fields: `color`, `stabilize`, **`letterbox`**,
`auto_speed`. I opened all 8 real legacy manifests on disk (`00-assets/drone-video-examples/
manifest.json` + the 7 `data/raw/archive/derivatives/*/manifest.json`) and read their actual
`post_processing` key sets:

| legacy manifest | actual post_processing keys |
|---|---|
| 00-assets corpus manifest | `color`, `stabilized`, `letterbox`, `auto_speed` |
| highlights_5_22s / _best / _graded / _graded_25s / _graded_varied / _long | `color`, `stabilized`, `letterbox` |
| highlights | (no post_processing block) |

Two concrete gaps, both measured, not inferred:
1. **`letterbox` appears in 7 of 8 legacy manifests and is not forbidden.** It is also the only
   one of the four that the pack proves was *actually applied* to this footage:
   `letterbox.horizontal_split_family.applied = true`, `active_picture_px [1280,544]`,
   `bar_height_px 88`, `bar_luma 16`, `content_cost 24.4` — all `measured`. By contrast the pack
   found `colour_treatment.declared_grade.verification_status = "PARTIALLY FALSIFIED"` (chroma
   untouched) and `speed_ramp_policy.measured_effect = "NO-OP"`. So the set forbids two fields
   whose declared effect the pack largely falsified, and permits the one whose effect it confirmed.
2. ~~**The spelling is wrong.** The real key is `stabilized`; the code forbids `stabilize`. No
   legacy manifest anywhere on disk contains the key `stabilize`. That guard is inert as written.~~
   **↑ REFUTED BY MEASUREMENT on re-verification — see §9 Correction C1.** Both spellings exist.
   The corrected finding: the guard misses **`letterbox` AND `stabilized`**, in 7 of 8 manifests.

Mitigation that keeps this from being catastrophic: the container key `post_processing` *is*
forbidden and the recursive walk catches it, so a wholesale legacy block is still rejected. The
gap opens when the fields are hoisted or flattened out of that container — which is precisely
the migration shape spec L24 contemplates ("Reuse of the existing schema shape … extended").
Confidence: CONFIRMED.
(Adjacent, belongs to the render group not this one: `reel_stitching/render.py:6–8`'s forbidden
filter list — `eq`, `curves`, `colorbalance`, `unsharp`, `vidstabtransform`, `setpts` — likewise
omits `pad`/`crop`, the actual mechanism the pack measured for this letterbox. Same blind spot,
second location. Flagging for whoever audits render.py; not verified further here.)

### IB-3 — the manifest cannot represent the active picture area, so 24.4% of 4 corpus files is scored as if it were image. CONFIRMED (schema side).
`SourceFile` (manifest.py:34–54) and `HIGHLIGHT_MANIFEST_SCHEMA.source_file` (schema.py:37–39)
carry exactly 8 fields: path, name, duration, width, height, fps, codec, pix_fmt. There is **no
field for the active-picture rectangle**. For the 4 `split_*` files the manifest therefore
asserts `1280×720` — true of the coded frame, but the pack measured (all `measured`) that the
picture is `1280×544` at offset y=88, with `bar_luma 16` bars occupying `24.4%` of rows, and
`mechanism = "vertical CENTRE-CROP at source row 88 then pad back to 1280x720 — NOT an
anamorphic…"`. Consequences that follow from the schema gap, not from any one scorer:
- No downstream consumer can learn it must crop; the contract does not carry the fact.
- Composition scoring's rule-of-thirds geometry (`sqrt((w/3)^2+(h/3)^2)`, restated in
  `manifest.py:131–132`) computes thirds lines over h=720 instead of h=544 — the horizontal
  thirds land ~26 px off the real picture's thirds, and a saliency centroid computed over the
  padded frame is pulled toward frame centre by two constant-luma-16 slabs.
- The `2.352941` measured active-picture ratio and the `2.35` label the pack reconciled are
  simply not expressible in this schema.
This is spec-conformant (plan.md L134–143 fixes the 8-field block), which is the point: the
spec fixed the block **before** the pack measured the letterbox. Confidence: CONFIRMED for the
schema gap; the composition-geometry consequence is LIKELY (I read `scoring_composition.py`'s
docstring but that file is another auditor's scope).

### IB-4 — `HighlightManifest.from_dict` silently stamps an unversioned document as version 3. CONFIRMED.
`manifest.py:295` `version=d.get("version", MANIFEST_VERSION)`. The module docstring (L14–22)
argues at length that 2→3 is *not* a silent additive bump, because "consumers reading
`composite_score` now see a value computed over four signals instead of three". Loading a
document with no `version` key then relabels it `3` — asserting exactly the semantic the
docstring says must never be assumed. Two sibling default-fills compound it:
`ScoringWeights.from_dict` (L98) fills `composition → 0.0` and `SegmentScores.from_dict`
(L161) fills `composition → None`. So a legacy-shaped document round-trips to a self-
contradictory artifact: `version: 3` (defined by a nonzero composition weight, tasks.md 1.24)
carrying `weights.composition: 0.0` and every `scores.composition: null` — and
`validate_highlight_manifest()` passes it, because it never cross-checks version against
weights. Confidence: CONFIRMED (read both `from_dict` and the validator).

### IB-5 — `normalization` default-fill fabricates a method description for work that never ran. CONFIRMED.
`manifest.py:299` `normalization=dict(d.get("normalization", DEFAULT_NORMALIZATION))`. A
document lacking the block acquires the current v3 prose, including a full description of the
saliency + Hough-tilt composition method — a paragraph asserting how a score was normalised for
a score that may not exist. In a repo where the reference pack labels every leaf
`measured|inferred|assumed`, silently supplying an unearned method description is the same
class of error as an invented constant. Confidence: CONFIRMED.

### IB-6 — `scores.composition = null` is overloaded across two incompatible meanings. LIKELY.
`SegmentScores.composition: Optional[float] = None` (L143) documents `None` as "backward
compatibility with legacy (version 2) manifests, which always had None here". But in a v3
manifest, `null` would also be the natural encoding for "the composition scorer ran and could
not produce a value" (e.g. Hough found no line). Nothing in the schema distinguishes them, and
`validate_highlight_manifest` requires only that the key exist. Against this corpus that matters:
the pack's measured horizon/motion facts are the *one* area where the pack's toolchain is
declared provably incapable, so composition is the signal most likely to legitimately fail.
Confidence: LIKELY — confirming "the scorer can return None" requires reading
`scoring_composition.py`'s return contract, which is another auditor's file.

---

## 7. The structural provenance gap (the question this group was assigned)

**Both reference-pack artifacts label the provenance of every value they assert. The pipeline's
own output schema labels none.**

Pack side, verified this session:
- `editorial_style.json` carries an explicit contract at `.schema.value_object_contract`:
  every asserted value is `{value, unit, confidence}` with `confidence ∈
  {measured, inferred, assumed}` — "'measured' = produced by a command run against the corpus.
  'inferred' = deduced from measurements without direct observation. 'assumed' = neither;
  carried from a declaration with no supporting observation." Every one of the ~110 leaves
  I enumerated carries it. The label does real work: `declared_grade.intensity 0.65` is
  `assumed`, `motion_type_vocabulary.assignments` is `assumed`, while
  `letterbox.*.bar_height_px 88` is `measured`.
- `exemplars/*.json` carry `scores_provenance` (e.g. `"manually_estimated"`), and the
  exemplar dataclass in `src/drone_video_ai/reference_pack/schema.py:96–98, 189` defines a
  second honesty enum `review_method ∈ {live_playback_review, text_provenance_only,
  not_reviewed}` with a docstring calling it exactly that: an "honesty tag".

Pipeline side (this group):
- `HighlightManifest` / `HIGHLIGHT_MANIFEST_SCHEMA` contain **no provenance field, no
  confidence field, and no measurement-context field** of any kind. `scores.sharpness`,
  `.exposure`, `.motion_smoothness`, `.composition` and `composite_score` are bare floats.
- Nothing records how many frames were sampled to produce a per-segment score, which
  ffprobe/ffmpeg build produced the numbers, or whether a value was computed vs. defaulted.
  Given IB-1 and IB-4/IB-5, a defaulted value is byte-identical to a measured one on the wire.
- The only method-provenance carrier is the free-form `normalization` prose dict, and the
  validator checks only that its four keys exist — never that the prose matches the code that
  actually ran. That is the same "stale twin" surface this repo has already shipped twice.
- `weights_version` (`"default-v1"` / `"default-v2"`) is the one genuine provenance handle in
  the manifest, and it is manifest-level, not per-score.

**The sharpest form of the gap: the project already solved this, one directory over.**
Capability 3's `reference_pack/schema.py` has `scores_provenance` and `review_method` enums
because its scores are admittedly estimates. Capability 1's manifest has neither — apparently
because its scores are *assumed* to be measurements. IB-1, IB-4 and IB-5 are three concrete
paths by which they are not. The minimal remedy is symmetry, not new machinery: a
`scores_provenance` on `SegmentScores` (`computed` / `defaulted` / `partial`) and a
`source_file_provenance` (`probed` / `partial`), enforced by the validator, would let a
consumer tell an asserted 30.0 fps from a fabricated 0.0 — the exact distinction ffprobe.py's
own docstring already argues for on the colour tags.

---

## 9. Independent verification pass (second agent, same day)

The first pass wrote §§1–8 but stalled before returning. A second agent re-read all three
source files in full and re-ran every load-bearing check with tools rather than relaying the
prior text. Result: **the distribution and all six original IBs survive; two factual claims
were wrong and are corrected below; one new finding (IB-7) was missed entirely.**

### Re-verified and CONFIRMED (tool output, this session)
| Claim | How re-verified | Result |
|---|---|---|
| `FORBIDDEN_POST_PROCESSING_KEYS` omits `letterbox` | read `schema.py:91` | CONFIRMED verbatim |
| `source_file` validated by key-presence only, no type/range check | read `schema.py:135–139` | CONFIRMED — a `{"fps":0.0,"width":0}` manifest validates clean |
| 8 zero-substitutions in ffprobe.py | read L67,71,123,125,131,132,134,135 | CONFIRMED, all 8 bare and unexplained |
| spec.md enumerates 4 legacy fields incl. `letterbox` | `grep -n` spec.md → **L24 and L44** both list `color`,`stabilize`,`letterbox`,`auto_speed` | CONFIRMED |
| `MANIFEST_VERSION = 3` is SPEC-grounded | plan.md **L230** "`version` bumps to 3 at that point"; tasks.md **L168** "`MANIFEST_VERSION` bumped from 2 to 3" | CONFIRMED |
| 0.5/0.5 composition blend is SPEC | tasks.md **L153** "unweighted 0.5/0.5 average" | CONFIRMED |
| S22/S23 over-attributed to plan.md | `grep -n "final\|last entry\|sentinel\|entries"` plan.md → only L239,240,257,269, none stating either rule | CONFIRMED — docstring's "Per plan.md" is wrong for both |
| Pack labels provenance, pipeline does not | `grep -c "provenance\|confidence"` → `common/manifest.py:0`, `common/schema.py:0`; vs `editorial_style.json.schema.value_object_contract` defining `confidence ∈ measured\|inferred\|assumed`, and `reference_pack/schema.py:96–98` `REVIEW_METHOD_VALUES` + `:189` `scores_provenance` | CONFIRMED — the §7 gap is real and stark |
| letterbox pack values | `editorial_style.letterbox.horizontal_split_family`: `applied True`, `active_picture_px [1280,544]`, `bar_height_px 88`, `bar_luma 16`, `content_cost 24.4` — all `measured`; `declared_ratio_label 2.35` is `assumed` | CONFIRMED |

### C1 — CORRECTION (refutes an original IB-2 sub-claim)
The first pass asserted the guard was **inert** because "no legacy manifest anywhere on disk
contains the key `stabilize`". That is **false**. The legacy schema carries the setting in
**two** places with **two** spellings:

- top-level `split_params.stabilize` (corpus manifest **line 20**: `"stabilize": false`)
- per-clip `post_processing.stabilized` (**lines 40, 56, 72, 88**: `"stabilized": false`)

Measured key sets across all 8 legacy manifests on disk:

| manifest | legacy pp-keys present | **missed by guard** |
|---|---|---|
| `00-assets/drone-video-examples` | post_processing, color, stabilize, stabilized, letterbox, auto_speed | **letterbox, stabilized** |
| `highlights` | (none) | — |
| `highlights_5_22s` / `_best` / `_graded` / `_graded_25s` / `_graded_varied` / `_long` | post_processing, color, stabilize, stabilized, letterbox | **letterbox, stabilized** |

So the `stabilize` guard **does fire** (7/8 manifests). The corrected finding is that the
forbidden set misses **two** keys that provably occur in this project's own material —
`letterbox` and `stabilized` — in 7 of 8 manifests. The original conclusion (letterbox is the
gap, and it is the one field the pack proved was actually applied) stands and is strengthened:
it is now a two-key gap, not a one-key gap plus a misspelling.

Severity nuance retained: `_check_no_post_processing` recurses, and `color` sits inside
`split_params` too, so a wholesale legacy document is still rejected via `color`/`post_processing`.
The gap is live only for a hoisted/flattened migration — the shape spec L24 explicitly contemplates.

### C2 / IB-7 — NEW FINDING the first pass missed: a stale version claim *inside the same docstring*
`manifest.py` line **6**: "Schema version is ``2`` -- bumped from the legacy … precedent's ``1``".
`manifest.py` line **19**: "…bumps ``MANIFEST_VERSION`` from 2 to 3".
`manifest.py` line **30**: `MANIFEST_VERSION = 3`.
`tests/highlight_extraction/test_pipeline_manifest_output.py:84`: `assert doc["version"] == 3`.

Line 6 is a stale sentence that survived the 2→3 bump and is contradicted 13 lines later by
the same docstring, by the constant, and by the test. This is *exactly* the failure mode root
`CLAUDE.md` names as this project's documented recurring defect — "an identical stale claim
survives in a sibling artifact … or even a second table row in the *same* file" — and the first
audit pass recorded §4.1 as PASSED. Zero runtime consequence (docstring only); high process
consequence, because it is the named failure mode recurring in the recovered code and being
missed by an audit whose job was to catch it. One-line fix: delete "Schema version is ``2`` -- ".

### C3 — scope note discovered during verification
Root `CLAUDE.md` states `tests/` does not exist. It **does** now (`tests/{common,highlight_extraction,reel_stitching,reference_pack}` + `conftest.py`), recovered with `src/`. Root `CLAUDE.md` is stale on this point. Not this group's finding to fix, but it invalidates the "nothing to run pytest against" line for whoever updates the project memory.

### C4 — cross-group lead (not this group's file, handed off)
`split_params` in the corpus manifest carries `"min_duration": 7.0, "max_duration": 15.0`
(lines 9–10) and `"letterbox": "2.35"`, `"color_intensity": 0.65`. The sibling group's
`weights.py DEFAULT_DURATION_PROFILE` max of **15.0** therefore has a plausible *provenance*
— the legacy tool's own split parameter — rather than being freely invented. That is not the
same as being measured: the pack's measured shot lengths reach **27.1 s** (mean 17.08 s), so
the 15.0 traces to a legacy tool's setting, not to this corpus's measured distribution. Whoever
owns `weights.py` should classify it against `split_params.max_duration`, not as a bare number.

---

## 8. Verdict

The `common/` group is a schema and I/O layer and it is, on the evidence, a careful one:
28 of 52 constants (54%) trace verbatim to `plan.md`'s fixed schema, 6 are ffmpeg flag
values, and the group's in-code explanations are real derivations rather than assertions
(`split(",")[0]`'s trailing-comma comment, the additive `time_base` field note, the
composition-prose restatements which I checked against `scoring_composition.py` and found
**accurate, not stale** — the failure mode this repo has shipped twice did not recur here).
The ffprobe happy path reproduces the pack's measured values exactly on all 8 corpus files.

Zero constants are MEASURED, which for a schema layer is mostly appropriate — there is no
threshold here that ought to have been calibrated. The real cost of that zero is different:
the contract encodes no knowledge of the footage it serves, so the pack's single most
consequential *structural* measurement — the baked-in 1280×544 active picture inside a
1280×720 coded frame — has nowhere to live (IB-3), and the one legacy field the pack proved
was actually applied, `letterbox`, is the one the forbidden-key guard omits (IB-2).

The 8 INVENTED values are all one pattern: silent zero-substitution in ffprobe.py's failure
path, in a file whose own docstring argues eloquently against exactly that for the colour
tags. Combined with a validator that checks key presence but never value sanity, and
`from_dict` default-fills that stamp version 3 and a full normalization method description
onto documents that earned neither, the group's weakness is not invented *thresholds* — it is
that **a fabricated value and a measured value are indistinguishable once written**. That is
the same problem `editorial_style.json`'s `confidence` field and `reference_pack/schema.py`'s
`scores_provenance` were built to solve, and the highlight manifest is the one artifact in
this project that does not solve it.
