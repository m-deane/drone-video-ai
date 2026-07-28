# Census 2 — Eval C: source_footage_analysis.md + detection_tuning_params.md

STATUS: COMPLETE
Agent: census2-eval-c
Date: 2026-07-28
Slice: 2 files under `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/`

**Standing caveat for every row below: these are UNTRUSTED, LLM-generated planning
documents from an archived project. Nothing in this file is asserted as true. Every
number is recorded as "the document claims X at line N", never as a fact about the
footage. drone_video_ai must not inherit any of these values without its own
measurement.**

---

## 1. Files read

| # | File (abs) | Lines | Read end-to-end |
|---|---|---|---|
| 1 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/source_footage_analysis.md` | 505 | YES (1–505) |
| 2 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/highlight_splitter/detection_tuning_params.md` | 419 | YES (1–419) |

**Total lines read: 924.**

Shorthand used below: `SFA` = source_footage_analysis.md, `DTP` = detection_tuning_params.md.

### 1.1 Attribution grep — result

```
grep -n -i -E 'http|www\.|\.com|@[a-z]|research|study|studies|source|cite|citation|
according to|reference|benchmark|industry|standard|best practice|shows that|data from|
per the|survey|report' SFA DTP
```

Hits, in full — there are only five, and **none is a citation**:

| Hit | What it actually is |
|---|---|
| `DTP:3  "## Research Summary"` | A section heading. Summarises the doc's own reasoning. Cites nothing. |
| `DTP:157 "@dataclass"` | A Python decorator. Matched the `@[a-z]` handle pattern. Not a handle. |
| `DTP:352 "...user control over scene quality preferences"` | Matched "preferences". Prose. |
| `SFA:1   "# Source Footage Analysis"` | Title. Matched "Source". |
| `SFA:315 "BT.709 (standard)"` | Matched "standard". A colour-space name. |

**ZERO URLs. ZERO named publications. ZERO named people. ZERO external references of any
kind in either file.** Not even a bulk list at the end — see §5.

---

## 2. Numeric editorial claims, with provenance

Provenance column records what the *document itself* credits the number to. `NONE` means
the document supplies no attribution whatsoever. `CODE-LOC` means the document points at a
source-code location (e.g. `config.py:27`) — this is recorded as a distinct, weaker
category because **a code location says where a constant lives, not how it was chosen**;
it is not a derivation and must not be read as one.

### 2.1 SFA — corpus-level claims

| # | Claim | Value | Cite | Doc's credited source |
|---|---|---|---|---|
| 1 | Clip count | 5 drone clips | SFA:5 | NONE |
| 2 | Camera | DJI Mavic 3 Pro (all 5) | SFA:5 | NONE (contradicted for Clip 3 — see §4.14) |
| 3 | Location | "likely Baja California, Mexico based on terrain and wildlife" | SFA:5 | NONE — explicit speculation |
| 4 | Total raw duration | ~96 s (1 min 36 s) | SFA:7 | NONE (arithmetically consistent w/ clips: 16.23+3.80+26.53+25.54+24.04 = 96.14) |
| 5 | Total file size | ~1.46 GB | SFA:8 | NONE (consistent: 255+61+372+401+377 = 1466 MB) |
| 6 | Recording dates | October 29–30, 2024 | SFA:9 | NONE (consistent with filenames) |

### 2.2 SFA — per-clip technical specs (container/format numbers)

All six rows below: **credited source NONE.** No `ffprobe` invocation, no tool name, no
command, no probe output is shown anywhere in the document. The values are the shape
`ffprobe` emits and are internally self-consistent (see #4, #5 above), which is the only
positive evidence they were read off real files rather than invented — see §6.

| Clip | File | Duration | Resolution | FPS | Codec | Bitrate | Colour | Size | Cite |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DJI_20241029173912_0350_D.MP4 | 16.23 s | 3840x2160 | 59.94 | HEVC Main 10 | 120 Mbps | BT.2020/HLG | 255 MB | SFA:18–26 |
| 2 | DJI_20241029174007_0351_D.MP4 | 3.80 s | 3840x2160 | 59.94 | HEVC Main 10 | 121 Mbps | BT.2020/HLG | 61 MB | SFA:87–95 |
| 3 | DJI_20241029174916_0356_D_383181722.mov | 26.53 s | 3840x2160 | 59.94 | H.264 High | 112 Mbps | BT.2020/HDR (PQ) | 372 MB | SFA:148–156 |
| 4 | DJI_20241030011347_0341_D.MP4 | 25.54 s | 3840x2160 | 59.94 | HEVC Main 10 | 120 Mbps | BT.2020/HLG | 401 MB | SFA:234–242 |
| 5 | DJI_20241030011801_0346_D.MP4 | 24.04 s | 3840x2160 | 59.94 | HEVC Main 10 | 120 Mbps | BT.709 | 377 MB | SFA:309–317 |

Additional numeric spec claim: Clip 3 **"Stabilized (smoothness 90), Enhanced (Topaz AI)"**
— SFA:156. Source: NONE. This is a Topaz Video AI parameter value, presented without
saying who set it or why.

### 2.3 SFA — timestamp notation hazard (read before using ANY window below)

**The document uses a colon as a DECIMAL POINT, not as a minutes separator.** Proof from
the document's own text: Clip 2 has duration `3.80 seconds` (SFA:88) and its content
inventory row reads `0:00-3:80` (SFA:101) — `3:80` is not a valid MM:SS value. Clip 1's
final scene boundary is `16:23` (SFA:78) against a stated duration of `16.23 seconds`.

**Consequence for drone_video_ai: every window in SFA §Clip 1–5 must be read as
SECONDS.SECONDS-HUNDREDTHS. A downstream consumer parsing `5:00-7:00` as minutes gets a
value 60x wrong.** This is a live inheritance hazard, not a cosmetic one — the hero-clip
hook `5:00-7:00` is a 2-second window inside a 26.53-second clip.

### 2.4 SFA — content-inventory windows (all source NONE)

| Clip | Windows | Cite |
|---|---|---|
| 1 | 0:00–5:00 / 5:00–10:00 / 10:00–16:00 (3 rows) | SFA:32–34 |
| 2 | 0:00–3:80 (1 row, whole clip) | SFA:101 |
| 3 | 0:00–3:00 / 3:00–7:00 / 7:00–12:00 / 12:00–17:00 / 17:00–22:00 / 22:00–26:53 (6 rows) | SFA:164–169 |
| 4 | 0:00–5:00 / 5:00–10:00 / 10:00–15:00 / 15:00–20:00 / 20:00–25:54 (5 rows) | SFA:248–252 |
| 5 | 0:00–5:00 / 5:00–10:00 / 10:00–15:00 / 15:00–20:00 / 20:00–24:04 (5 rows) | SFA:325–329 |

Clip 3 additionally carries a **whale-count** column — 4-5, 6-8, 8-10, 7-9, 8-10, 10-12
visible (SFA:164–169). Source: NONE. No counting method stated. These are the only
"subject count" numbers in either document and they are the numbers the whole
`wildlife_present: 2.0` weight (SFA:453) rests on.

Clip 3 also carries a point event: **"splash visible at 13s"** (SFA:167). Source NONE.

### 2.5 SFA — quality ratings (subjective /10 scores, source NONE for all 20)

| Clip | Sharpness | Stability | Exposure | Colour | Cite |
|---|---|---|---|---|---|
| 1 | 8/10 | 9/10 | 7/10 | 6/10 | SFA:54–57 |
| 2 | 9/10 | 9/10 | 8/10 | 7/10 | SFA:120–123 |
| 3 | 8/10 | 10/10 | 8/10 | 8/10 | SFA:191–194 |
| 4 | 8/10 | 9/10 | 6/10 | 7/10 | SFA:274–277 |
| 5 | 7/10 | 9/10 | 9/10 | 9/10 | SFA:351–354 |

No rubric, no anchor, no measurement is given for any of the 20 ratings. There is no
statement of what 8/10 sharpness means in Laplacian-variance terms or any other unit.

### 2.6 SFA — peak moments and best-quality segments (source NONE)

| Clip | Peak moments | Best-quality segment | Cite |
|---|---|---|---|
| 1 | 0:00–3:00, 10:00–16:00 | 5:00–10:00 | SFA:47–48, 64 |
| 2 | 0:00–2:00 | "entire clip" | SFA:114, 127 |
| 3 | 5:00–7:00, 20:00–22:00, 10:00–12:00, 25:00–26:53 (ranked 1–4) | 5:00–12:00 | SFA:182–185, 200 |
| 4 | 10:00–15:00, 20:00–25:00 | 10:00–20:00 | SFA:267–268, 284 |
| 5 | 10:00–15:00, 20:00–24:00 | 10:00–24:00 | SFA:344–345, 360 |

### 2.7 SFA — hook scores and hook windows (VIEWER-BEHAVIOUR claims; source NONE for all)

| Clip | Rank | Window | Hook type | Score | Cite |
|---|---|---|---|---|---|
| 1 | 1 | 0:00–2:00 | Establishing shot | 6/10 | SFA:70 |
| 1 | 2 | 10:00–14:00 | Mountain reveal | 6/10 | SFA:71 |
| 2 | 1 | 0:00–2:00 | Action/movement | 8/10 | SFA:133 |
| 3 | 1 | 5:00–7:00 | Wildlife reveal / tight pod | **10/10** | SFA:206 |
| 3 | 2 | 20:00–22:00 | Scale reveal | 9/10 | SFA:207 |
| 3 | 3 | 25:00–26:53 | Diagonal formation | 9/10 | SFA:208 |
| 3 | 4 | 10:00–12:00 | Surface activity/splash | 8/10 | SFA:209 |
| 3 | 5 | 0:00–2:00 | Mystery intro | 7/10 | SFA:210 |
| 4 | 1 | 20:00–25:00 | Epic reveal | 8/10 | SFA:290 |
| 4 | 2 | 10:00–15:00 | Dramatic peak | 7/10 | SFA:291 |
| 4 | 3 | 0:00–5:00 | Intimate detail | 6/10 | SFA:292 |
| 5 | 1 | 20:00–24:04 | Epic sunset reveal | 9/10 | SFA:366 |
| 5 | 2 | 10:00–15:00 | Golden hour peak | 8/10 | SFA:367 |
| 5 | 3 | 0:00–5:00 | Silhouette intro | 7/10 | SFA:368 |

Overall per-clip hook verdicts (SFA:73, 135, 212, 294, 370): Clip 1 **LOW**, Clip 2
**HIGH**, Clip 3 **MAXIMUM**, Clip 4 **MEDIUM-HIGH**, Clip 5 **HIGH**. Source NONE. See
§4.4 — these verdicts are inconsistent with DTP's own numeric tier boundaries.

The Global Hook Ranking table (SFA:387–396) restates 10 of the above as a cross-clip
top-10. Values agree with the per-clip tables; no new numbers, no source.

### 2.8 SFA — scene-boundary suggestions (source NONE; 20 boundaries)

| Clip | Suggested boundaries | Cite |
|---|---|---|
| 1 | 0:00, 8:00, 16:23 | SFA:76–78 |
| 2 | 0:00, 3:80 — "continuous shot, no internal scene changes" | SFA:138–139 |
| 3 | 0:00, 5:00, 12:00, 17:00, 22:00, 26:53 | SFA:215–220 |
| 4 | 0:00, 7:00, 15:00, 25:54 | SFA:297–300 |
| 5 | 0:00, 8:00, 15:00, 20:00, 24:04 | SFA:373–377 |

**These are labelled "Suggestions" and are explicitly editorial, not detected.** Note
SFA:139 states outright that Clip 2 has *no internal scene changes* — the document's own
only direct statement about cut structure, and it agrees with drone_video_ai's
independent finding of zero hard cuts. No equivalent statement is made for clips 1, 3–5;
their boundaries are described as "subtle shift", "scene intensifies", "colour shift
intensifies" — i.e. content-interest markers, not cuts.

### 2.9 SFA — recommended cuts (OUTPUT-SHOT-LENGTH claims; source NONE)

| # | Window | Stated length | Actual length | Cite |
|---|---|---|---|---|
| 1 | Clip 3 @ 5:00–8:00 | "3s hook" | 3.00 s ✓ | SFA:223 |
| 2 | Clip 3 @ 20:00–24:00 | "4s establishing" | 4.00 s ✓ | SFA:224 |
| 3 | Clip 3 @ 25:00–26:53 | "2s dramatic" | **1.53 s ✗** | SFA:225 |

### 2.10 SFA — content category durations (source NONE)

| Category | Clips | Stated total | Cite |
|---|---|---|---|
| Wildlife (whales) | 3 | 26.5 s | SFA:405 |
| Ocean/water | 1, 2 | 20.0 s | SFA:406 |
| Mountains/landscape | 4, 5 | 49.6 s | SFA:407 |
| Coastal | 4, 5 | 49.6 s | SFA:408 |

Arithmetic check: 16.23+3.80 = 20.03 ✓; 25.54+24.04 = 49.58 ✓. But the four category
totals sum to 145.7 s against a 96 s corpus — clips 4 and 5 are counted twice. Not a
contradiction (categories are declared overlapping) but a **double-count trap** for any
downstream consumer summing this column.

### 2.11 SFA — algorithm recommendations (the invented-constant block)

| # | Claim | Value | Cite | Source |
|---|---|---|---|---|
| 1 | **"Opening 3 seconds rule"** — always select highest-scoring hook segment first | 3 s | SFA:435 | **NONE** |
| 2 | `wildlife_present` weight | 2.0 | SFA:453 | NONE |
| 3 | `human_activity` weight | 1.5 | SFA:454 | NONE |
| 4 | `movement_detected` weight | 1.3 | SFA:455 | NONE |
| 5 | `golden_hour` weight | 1.4 | SFA:456 | NONE |
| 6 | `subject_count` weight | 1.2 | SFA:457 | NONE |
| 7 | `composition_score` weight | 1.1 | SFA:458 | NONE |
| 8 | `sharpness` weight | 1.0 | SFA:459 | NONE |
| 9 | `color_variance` weight | 0.9 | SFA:460 | NONE |

The `SCENE_WEIGHTS` block (SFA:452–461) is presented as a Python dict, i.e. in
copy-paste-ready form, with **no derivation, no fit, no experiment, and no comparison
against the pipeline's existing weights**. The values form a smooth descending ladder of
round numbers (2.0, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9) — the signature of an authored
preference ordering rather than a measured one. The "Opening 3 seconds rule" (SFA:435) is
the single most inheritance-prone claim in this file: it is a hook-timing constant about
viewer behaviour, stated as a *rule*, with zero attribution.

Clip-priority assignments (SFA:468–472), source NONE: Clip 1 "Low priority — use only for
transitions"; Clip 2 "High priority"; Clip 3 "MAXIMUM priority"; Clip 4 "Medium-high";
Clip 5 "High".

### 2.12 SFA — suggested reel structures (OUTPUT DURATION + SHOT LENGTH; source NONE)

**Option A — "Wildlife Focus (30s)"** (SFA:478–486)

| Beat | Source | Window | Stated | Actual |
|---|---|---|---|---|
| Hook | Clip 3 | 5:00–7:00 | 2 s | 2.00 ✓ |
| Establish | Clip 1 | 0:00–3:00 | 3 s | 3.00 ✓ |
| Build | Clip 3 | 10:00–15:00 | 5 s | 5.00 ✓ |
| Peak | Clip 3 | 20:00–24:00 | 4 s | 4.00 ✓ |
| Transition | Clip 2 | 0:00–3:00 | 3 s | 3.00 ✓ |
| Landscape | Clip 4 | 15:00–20:00 | 5 s | 5.00 ✓ |
| Finale | Clip 5 | 18:00–24:00 | 6 s | 6.00 ✓ |
| End | Clip 3 | 25:00–26:53 | 2 s | **1.53 ✗** |
| | | **Total** | **30 s** | **29.53 s** |

Implied cut rate: 8 shots / 30 s = **3.75 s mean shot length, 0.267 cuts/s**. (Derived by
me from the document's own numbers; the document never states a cut rate.)

**Option B — "Cinematic Journey (45s)"** (SFA:488–496)

| Beat | Source | Window | Stated | Actual |
|---|---|---|---|---|
| Hook | Clip 5 | 10:00–13:00 | 3 s | 3.00 ✓ |
| Reveal | Clip 4 | 0:00–8:00 | 8 s | 8.00 ✓ |
| Ocean | Clip 1 | 5:00–12:00 | 7 s | 7.00 ✓ |
| Wildlife intro | Clip 3 | 0:00–3:00 | 3 s | 3.00 ✓ |
| Wildlife peak | Clip 3 | 5:00–12:00 | 7 s | 7.00 ✓ |
| Action | Clip 2 | 0:00–3:80 | 4 s | **3.80 ✗** |
| Return | Clip 4 | 18:00–25:00 | 7 s | 7.00 ✓ |
| Finale | Clip 5 | 18:00–24:04 | 6 s | 6.04 (rounds ✓) |
| | | **Total** | **45 s** | **44.84 s** |

Implied cut rate: 8 shots / 45 s = **5.63 s mean shot length, 0.178 cuts/s**. Again
derived by me, not stated.

**No transition durations, no LUT/grade intensities, no saturation/contrast deltas, no
aspect ratio for the output, no BPM/beat-alignment, no text-overlay timing, no
retention/drop-off percentages, and no speed-ramp factors appear anywhere in SFA.** The
only output-format target named at all is "Instagram Reels" (SFA:383), with no
accompanying spec.

---

### 2.13 DTP — detector constructor parameters (§1.1, DTP:13–18)

| # | Parameter | Default | Stated range | Cite | Doc's credited source |
|---|---|---|---|---|---|
| 1 | `threshold` (scene_threshold) | **27.0** | 15.0–50.0 | DTP:15 | **CODE-LOC only** (`config.py:27`). No derivation. |
| 2 | `min_scene_length` | **1.0 s** | 0.5–5.0 s | DTP:16 | CODE-LOC only (`config.py:28`) |
| 3 | `max_scene_length` | **8.0 s** (create) / **10.0 s** (detector init) | 5.0–20.0 s | DTP:17 | CODE-LOC only (`config.py:29`) |
| 4 | `analysis_scale` | **0.5** | 0.25–1.0 | DTP:18 | CODE-LOC only (`scene_detector.py:212`), "NO – hardcoded" |

DTP:22 attributes the *mechanism* to PySceneDetect ("Controls ContentDetector sensitivity
via PySceneDetect") — **27.0 is PySceneDetect's own ContentDetector default value.** The
document therefore inherits a library default and re-presents it as this project's
threshold. It never claims to have chosen 27.0, and never claims to have tested it.

### 2.14 DTP — the single observational claim

| # | Claim | Cite | Source |
|---|---|---|---|
| 1 | "The DJI video case produced **7 scenes** with similar scores (**55–64 range**)" | DTP:5 | NONE — no filename, no duration, no command, no per-scene table, no date |

Restated at DTP:65 ("All 7 DJI scenes likely scored in 55-64 range" — note the hedge
"likely" applied to what DTP:5 asserted as an observed run result), DTP:271, DTP:301,
DTP:413.

### 2.15 DTP — basic scoring weights (§2.1, DTP:53–62)

| # | Component | Weight | Cite | Source |
|---|---|---|---|---|
| 1 | motion_score | 0.30 | DTP:54 | NONE |
| 2 | composition_score | 0.20 | DTP:55 | NONE |
| 3 | color_score | 0.20 | DTP:56 | NONE |
| 4 | sharpness | 0.15 | DTP:57 | NONE |
| 5 | brightness_score | 0.15 (distance from ideal 127/255) | DTP:58 | NONE |
| 6 | Peak scoring | `overall = 0.6*max(frame_scores) + 0.4*mean(frame_scores)` | DTP:62 | NONE |

Weights sum to 1.00 ✓.

### 2.16 DTP — enhanced scoring weights + hook tiers (§2.2, DTP:75–85)

| # | Component | Weight | Cite | Source |
|---|---|---|---|---|
| 1 | subject_score | 0.25 | DTP:76 | NONE |
| 2 | motion_score | 0.25 (reduced from 0.30) | DTP:77 | NONE |
| 3 | composition_score | 0.15 (from 0.20) | DTP:78 | NONE |
| 4 | color_score | 0.15 (from 0.20) | DTP:79 | NONE |
| 5 | sharpness | 0.10 (from 0.15) | DTP:80 | NONE |
| 6 | brightness_score | 0.10 (from 0.15) | DTP:81 | NONE |

Weights sum to 1.00 ✓. No rationale is given for any of the six reallocations.

**Hook potential tiers (DTP:85) — source NONE:**
MAXIMUM ≥ 80 · HIGH ≥ 65 · MEDIUM ≥ 45 · LOW ≥ 25 · POOR < 25.

These four boundary values are the most directly reusable "viewer-engagement" constants in
either file and carry no attribution of any kind.

### 2.17 DTP — component score formulas (§2.3, source NONE for every constant)

| # | Metric | Formula / constant | Cite |
|---|---|---|---|
| 1 | Motion amount | `min(mean_magnitude / 3.0 * 100, 100.0)` — normalisation divisor **3.0**, cap **100** | DTP:99 |
| 2 | Motion quality | `1.0 - min(std/mean, 1.0)` | DTP:100 |
| 3 | Motion score mix | `0.7*amount + 0.3*quality` | DTP:101 |
| 4 | Composition: rule of thirds | 40% of composition | DTP:113 |
| 5 | Composition: horizon level | 30% | DTP:114 |
| 6 | Composition: leading lines | 30% | DTP:115 |
| 7 | Saturation score | `(mean_sat/255.0*50) + (std_sat/128.0*50)` — divisors **255**, **128**, scalars **50/50** | DTP:124 |
| 8 | Sharpness | `min(Laplacian_variance / 500.0 * 100, 100.0)` — divisor **500.0** | DTP:135 |
| 9 | Brightness ideal | **127** (of 255); `score = max(0, 100 - deviation*100)` | DTP:143–145 |

The divisors 3.0, 500.0, 255/128 and the ideal 127 are the load-bearing normalisation
constants of the whole scoring system. **Not one of them is justified, cited, or tied to
any measurement of this footage or any other.** 127 is simply the midpoint of an 8-bit
range; 500.0 and 3.0 have no stated basis at all.

### 2.18 DTP — filter thresholds (§3.1, DTP:159–164)

| # | Field | Value | Cite | Source |
|---|---|---|---|---|
| 1 | `min_motion_energy` | 25.0 | DTP:159 | NONE |
| 2 | `ideal_motion_energy` | 45.0 | DTP:160 | NONE |
| 3 | `min_brightness` | 30.0 | DTP:161 | NONE |
| 4 | `max_brightness` | 245.0 | DTP:162 | NONE |
| 5 | `max_shake_score` | 40.0 | DTP:163 | NONE |
| 6 | `subject_score_threshold` | 0.6 | DTP:164 | NONE |

Tier logic restating these (DTP:170–174): High Subject ≥0.6 · High Motion ≥45.0 · Medium
Motion ≥25.0 · Low Motion <25.0 · Filtered if brightness out of range or shake >40.0.
(Line citations in this subsection re-verified by grep on 2026-07-28; an earlier draft of
this checkpoint was off by one here.)

Note `max_shake_score` filters on a **"shake score" that is never defined anywhere in the
document** — §2.3 defines motion, composition, colour, sharpness and brightness only.

### 2.19 DTP — predicted / hypothesised score ranges (all hedged, source NONE)

| # | Metric | Stated range | Cite | Hedge word used |
|---|---|---|---|---|
| 1 | motion_score | "converge to **40–60** range" | DTP:104 | "so ... converge" |
| 2 | composition | "likely score **50–70**" | DTP:117 | "likely" |
| 3 | motion_energy | "in **35–50** range" | DTP:178 | "If all 7 scenes have ... (likely ...)" |
| 4 | motion_score | "**35–55** across all scenes" | DTP:275 | "Given a sequence of..." |
| 5 | composition | "**45–65** across all scenes" | DTP:281 | same |
| 6 | mean brightness | "**90–110** (all pass balance check)" | DTP:285 | same |
| 7 | colour | "**40–60** across all scenes" | DTP:290 | same |
| 8 | sharpness | "**60–80** across all scenes" | DTP:294 | same |
| 9 | Combined | `0.6*max(55-65) + 0.4*mean(55-65) = 0.6*65 + 0.4*58 = 63.2` | DTP:298 | — |

Rows 1–8 are the closest thing in either document to per-metric measurements of this
footage. **Every one is grammatically hypothetical** ("likely", "If all 7 scenes have",
"Given a sequence of 7 landscape drone shots"). No per-scene values are ever printed. Row
9's arithmetic is wrong — see §4.5.

### 2.20 DTP — proposed CLI flag defaults and recommendations (§4, source NONE)

| # | Flag | Default | Range | Recommendation in text | Cite |
|---|---|---|---|---|---|
| 1 | `--scene-threshold` | 27.0 | 15.0–50.0 | "Lowering to **20–22**" | DTP:204–207 |
| 2 | `--enhanced` | off | bool | "2–3x slower (~**30 sec** per video instead of **10–15 sec**)" | DTP:210–214 |
| 3 | `--motion-weight` | 0.30 | 0.0–1.0 | "Reduce to **0.15–0.20**" | DTP:217–220 |
| 4 | `--min-subject-score` | **0.3** | 0.0–1.0 | example uses **0.5** | DTP:225–229 |
| 5 | `--golden-hour-boost` | 1.0 | 0.5–2.0 | §9 test uses **1.5** | DTP:231–235 |
| 6 | `--depth-threshold` | 0.0 (no filter) | 0.0–100.0 | — | DTP:237–241 |
| 7 | `--analysis-scale` | 0.5 | 0.25–1.0 | 1.0 max quality / 0.25 quick | DTP:243–247 |
| 8 | `--motion-variety` | — | — | "Orbit/Flyover/Reveal scenes get **+10** to final score" | DTP:258 |

### 2.21 DTP — predicted outcomes of the proposed values (§6, source NONE)

| # | Claim | Cite |
|---|---|---|
| 1 | threshold 20 vs 27 "**Would detect 10–12 scenes instead of 7**" | DTP:309 |
| 2 | subject_score illustrative values: **0.2** empty landscape, **0.7** wildlife, **0.5** interesting rock formation | DTP:312 |
| 3 | TIER 1 subject_score **≥0.5**; TIER 2 **0.4–0.5**; TIER 3 **<0.4** (filtered) | DTP:316–318 |

Row 1 is stated in the indicative ("Would detect 10-12") but is a pure prediction; §9 makes
clear the run had not been done. Row 2's three values are openly illustrative. Row 3
introduces a **third** subject-score threshold scheme — see §4.3.

### 2.22 DTP — performance estimates (§7, DTP:328–334; source NONE)

`--enhanced` 2–3x slower · `--golden-hour-boost` ~10% slower · `--depth-threshold`
~5–10% slower · others "None"/"Variable". Not editorial claims about the output video;
recorded for completeness only.

### 2.23 DTP — testing-plan values (§9, DTP:367–391; source NONE — these are *proposed*
test inputs, not results)

Test 1: `--scene-threshold 20 --min-score 40`. Test 2: `--min-subject-score 0.4`.
Test 3: `--scene-threshold 22 --min-subject-score 0.35 --golden-hour-boost 1.5
--min-score 45`. Test 4: `--min-subject-score 0.6 --min-score 60 --count 5`.
The `--min-score` values (40, 45, 60) appear **only** here and are never defined or
justified anywhere else in the document.

### 2.24 DTP — §10 impact table (DTP:399–407)

Restates: threshold "current value (27) ... lowering to 20-22" (DTP:402);
**"reducing 30% → 15%"** for motion weight (DTP:404). See §4.2 — this is a
range-to-point-value collapse.

---

### 2.25 CLAIM TALLY

Counted as distinct number-bearing claims (not table rows — a spec row carrying six values
counts six). Derivation of the count is shown so it can be audited.

| Section | Contents | SFA | DTP |
|---|---|---|---|
| §2.1 | corpus-level (clip count, total duration, total size, dates) | 4 | — |
| §2.2 | 5 clips x 6 spec fields (duration/res/fps/bitrate/colour-std/size) + Topaz smoothness 90 | 31 | — |
| §2.4 | 20 content windows + 6 whale counts + 1 splash-at-13s | 27 | — |
| §2.5 | 5 clips x 4 quality ratings | 20 | — |
| §2.6 | 11 peak-moment windows + 5 best-quality segments | 16 | — |
| §2.7 | 14 hook rows (window + /10 score) | 14 | — |
| §2.8 | scene-boundary suggestions | 20 | — |
| §2.9 | recommended cuts | 3 | — |
| §2.10 | category durations | 4 | — |
| §2.11 | "opening 3 seconds rule" + 8 SCENE_WEIGHTS | 9 | — |
| §2.12 | 2 reel structures x (8 segments + total) | 18 | — |
| §2.13 | 4 defaults + 4 ranges + alt max_scene_length | — | 9 |
| §2.14 | "7 scenes", "55-64" | — | 2 |
| §2.15 | 5 basic weights + peak formula + ideal 127 | — | 7 |
| §2.16 | 6 enhanced weights + 4 hook-tier boundaries | — | 10 |
| §2.17 | 9 component-score formulas/constants | — | 9 |
| §2.18 | 6 FilterThresholds fields | — | 6 |
| §2.19 | 8 predicted ranges + 1 combined calculation | — | 9 |
| §2.20 | 8 proposed CLI flag defaults/recommendations | — | 8 |
| §2.21 | 3 predicted outcomes | — | 3 |
| §2.22 | 3 performance estimates | — | 3 |
| §2.23 | 4 testing-plan configurations | — | 4 |
| §2.24 | motion weight 30% -> 15% | — | 1 |
| | **Subtotal** | **166** | **71** |

| Bucket | Count |
|---|---|
| Catalogued numeric claims, both files | **237** |
| ... carrying a resolvable NAMED source (URL or named publication) for that number | **0** |
| ... carrying a code-location pointer only (`CODE-LOC` — where the constant lives, not why) | 4 |
| ... carrying NOTHING at all | 233 |

**Claims with a named source: 0 of 237.**

---

## 3. Reference videos and exemplar creators

**COUNT: 0.**

Applying the strict test (a specific identifiable third-party video, or a named creator
held up as an exemplar):

| Candidate found in text | Cite | Verdict |
|---|---|---|
| "DJI Mavic 3 Pro" | SFA:26 etc. | Camera hardware. NOT a creator. |
| "Topaz Video AI" | SFA:158 | Software tool. NOT a creator. |
| "PySceneDetect" | DTP:22 | Library. NOT a creator. |
| "Instagram Reels" | SFA:383 | Distribution platform named as a target format. No account, no video, no creator. |
| "drone-reel" | DTP:369 etc. | The archived project's own CLI. Not third-party. |

No Instagram handles, no TikTok links, no YouTube references, no named editors,
colourists, or channels appear in either file. **Consistent with the sibling agents'
corpus-wide finding: the single specific third-party video in the entire archived corpus
is the TikTok link in research_transitions.md:862, and it is not in this slice. Neither
is any of the four Instagram handles.**

---

## 4. Internal contradictions (hunted actively)

Ordered by consequence to drone_video_ai.

### 4.1 The same metric is given THREE different ranges for the SAME 7 scenes

| Metric | Value A | Value B | Value C |
|---|---|---|---|
| motion | "converge to **40–60**" DTP:104 | "**35–50** range" DTP:178 | "**35–55** across all scenes" DTP:275 |
| composition | "likely score **50–70**" DTP:117 | — | "**45–65** across all scenes" DTP:281 |

These are not different metrics or different runs — §2.3.1, §3.3 and §5 all describe the
same 7 scenes of the same video. **Real recorded measurements do not drift between three
sections of one document.** This is the strongest single piece of evidence that these
ranges were authored, not observed. It also matters materially: whether motion is 35–50 or
40–60 flips how many scenes clear the `ideal_motion_energy = 45.0` gate (DTP:160), which is
the document's own tiering boundary.

### 4.2 RANGE → POINT VALUE collapse (the pattern the parent flagged), twice

| Instance | Range stated | Collapsed to | Cite |
|---|---|---|---|
| motion weight | "Reduce to **0.15–0.20**" | "reducing 30% → **15%**" | DTP:220 → DTP:404 |
| scene threshold | "Lowering to **20–22**" | `--scene-threshold **20**` in the §6 worked scenario and §9 Test 1 | DTP:207 → DTP:307, DTP:369 |

The motion-weight case is the clean instance: a two-endpoint range is restated 184 lines
later as a single value, the *lower* endpoint, with **no reason given for choosing it**.
This is structurally identical to the documented LUT `50-70% → 60% → intensity=0.6` and
transition `0.3-0.5s → 0.3s → duration=0.3` failures. One more hop and `0.15` becomes a
code default whose only remaining justification is that a planning doc once said
"0.15-0.20".

The threshold case is milder — 22 does survive into §9 Test 3 (DTP:377) — but the primary
worked example and the first test both take 20.

### 4.3 THREE mutually inconsistent subject-score threshold schemes in one document

| Scheme | Value(s) | Cite |
|---|---|---|
| `FilterThresholds.subject_score_threshold` dataclass | **0.6** | DTP:164 |
| §3.2 tier rule "High Subject" | **≥ 0.6** | DTP:170 |
| `--min-subject-score` CLI default | **0.3** | DTP:225 |
| §4.2 worked example | 0.5 | DTP:229 |
| §6 tiering: TIER 1 / TIER 2 / TIER 3 | **≥0.5 / 0.4–0.5 / <0.4** | DTP:316–318 |
| §9 test values | 0.4, 0.35, 0.6 | DTP:372, 378, 386 |

A CLI default of 0.3 alongside a dataclass gate of 0.6 means the flag's default is
*below* the filter it is supposed to drive. Six different subject thresholds appear across
one 419-line document with no statement of which governs.

### 4.4 The two documents' hook tiers disagree for 3 of 5 clips

DTP:85 defines tiers numerically on 0–100: MAXIMUM ≥80, HIGH ≥65, MEDIUM ≥45, LOW ≥25,
POOR <25. SFA assigns verbal tiers per clip from /10 scores. Scaling SFA's scores ×10:

| Clip | SFA verdict | SFA top hook score | ×10 | DTP tier that implies | Agree? |
|---|---|---|---|---|---|
| 1 | LOW (SFA:73) | 6/10 | 60 | MEDIUM | **NO** |
| 2 | HIGH (SFA:135) | 8/10 | 80 | MAXIMUM | **NO** |
| 3 | MAXIMUM (SFA:212) | 10/10 | 100 | MAXIMUM | yes |
| 4 | MEDIUM-HIGH (SFA:294) | 8/10 | 80 | MAXIMUM | **NO** (and "MEDIUM-HIGH" is not a defined tier) |
| 5 | HIGH (SFA:370) | 9/10 | 90 | MAXIMUM | **NO** |

Either the ×10 mapping is wrong (in which case no mapping is stated anywhere and SFA's
tier words are meaningless against the code) or the tier boundaries are wrong. The
documents never reconcile them. Under DTP's boundaries, 4 of 5 clips are MAXIMUM — which
would make the tier system useless for exactly this footage, the same "no differentiation"
complaint the whole DTP document exists to solve.

### 4.5 Arithmetic error in the document's flagship calculation

DTP:298: `0.6*max(55-65) + 0.4*mean(55-65) = 0.6*65 + 0.4*58 = 63.2`.

**0.6 × 65 = 39.0; 0.4 × 58 = 23.2; 39.0 + 23.2 = 62.2, not 63.2.**

Two further problems in the same line: (a) the input range is written **55–65** here but
the document's headline observation is **55–64** (DTP:5, 271, 301) — the max is
inconsistent by one point; (b) the "mean" is given as **58**, which is not the midpoint of
55–65 (that would be 60) and is unexplained. A number copied out of a real run does not
fail its own arithmetic.

### 4.6 Does this footage contain golden hour? The two documents say opposite things

- SFA:421 — "Dusk/Golden Hour | Clips **4, 5** | Warm, dramatic"; SFA:5 "during golden
  hour"; SFA:327 "Golden hour glow intensifying"; SFA:354 rates Clip 5 colour 9/10 for
  "Beautiful warm gradient".
- DTP:288 — "Same lighting conditions (**daytime, no dramatic golden hour**)".
- DTP:405 — `--golden-hour-boost` "Would boost sunset shots **if present** in footage".

One document says two of five clips are sunset/golden-hour hero material; the other says
there is no dramatic golden hour and is not sure whether sunset shots exist at all. This
directly undermines the proposed `--golden-hour-boost` flag *and* SFA's
`'golden_hour': 1.4` weight (SFA:456) — the two documents cannot both be describing the
same footage correctly.

### 4.7 Two incompatible weighting schemes for the same pipeline

| SFA:452–461 (`SCENE_WEIGHTS`) | DTP:54–58 (`_score_scene`) |
|---|---|
| Multipliers 2.0 / 1.5 / 1.4 / 1.3 / 1.2 / 1.1 / 1.0 / 0.9 | Fractions 0.30 / 0.20 / 0.20 / 0.15 / 0.15, summing to 1.00 |
| composition 1.1 > sharpness 1.0 > colour 0.9 | colour 0.20 = composition 0.20 > sharpness 0.15 |

Different mechanism (boost multipliers vs. a convex combination) **and** an inverted
relative ordering of colour vs. sharpness. Neither document acknowledges the other's
scheme.

### 4.8 Opposed advice on motion

SFA:455 boosts `movement_detected` (1.3x). DTP:220/404 argues motion must be *de-weighted*
(0.30 → 0.15) precisely because drone motion is uniform and therefore non-discriminating.
Both are unsourced; they point in opposite directions.

### 4.9 Clip 3: the hero hook window contradicts the document's own content inventory

- Content inventory SFA:165 — `3:00-7:00` = "Pod **spreading out**, multiple surfacing
  events", 6–8 whales visible.
- Content inventory SFA:166 — `7:00-12:00` = "**Peak activity - tight formation**", 8–10
  visible.
- Peak Moments SFA:182 — `5:00-7:00` = "Maximum whale visibility, **tight formation**".
- Hook rank 1 SFA:206 — `5:00-7:00` = "Wildlife reveal - **tight pod formation**",
  **10/10**.

The window the document scores 10/10 — the highest score in either file, the value that
makes Clip 3 "HERO FOOTAGE" and drives `wildlife_present: 2.0` — falls inside the
inventory row the same document labels "pod spreading out", while the row labelled "tight
formation" is 7:00–12:00. The document's own maximum whale count (10–12) is at
22:00–26:53 (SFA:169), not at 5:00–7:00. **The single highest-consequence editorial
judgement in this slice contradicts the evidence table printed 40 lines above it.**

### 4.10 Clip 3: "any segment from 5–27 seconds" exceeds the clip

SFA:212 says "Any segment from 5-**27** seconds works as a powerful hook" against a stated
duration of 26.53 s (SFA:149).

### 4.11 Shot length mislabelled in three places

`25:00-26:53` is 1.53 s but is called "2s" at SFA:225 and SFA:486. `0:00-3:80` is 3.80 s but
is called "4s" at SFA:494. Consequently Option A totals 29.53 s not the stated 30 s
(SFA:478) and Option B totals 44.84 s not 45 s (SFA:488). Small individually; material if
a stitcher inherits "2s" as a shot-length default.

### 4.12 Clip 1 exposure: "needs grading" vs "no exposure problems"

SFA:56 rates exposure 7/10, "Slightly flat/hazy, HLG footage needs grading". SFA:62, six
lines later under Quality Issues, states "**No exposure problems**". Same clip, same
section.

### 4.13 Clip 1 is simultaneously panning and static

SFA:42 — camera movement "Slow horizontal pan/orbit". SFA:414 lists Clip 1 under
**Orbit/Pan**. SFA:415 also lists Clip 1 under **Static/Slow**. The clip is placed in two
mutually exclusive movement categories, one of which the per-clip section refutes.

### 4.14 Clip 3 is presented as a camera original but is demonstrably a derivative

SFA:5 — "5 drone clips **captured with a DJI Mavic 3 Pro**". But Clip 3 (SFA:148–158) is a
`.mov`, H.264 High Profile (all others HEVC Main 10), BT.2020 PQ (all others HLG or 709),
carries a `_383181722` suffix, is the only clip with **no `Camera` row in its spec table**,
and is explicitly described as "pre-processed through Topaz Video AI with stabilization and
enhancement", with acknowledged "compression artifacts from re-encoding" (SFA:198).

**This matters more than it looks.** The document's hero footage — the source of the 10/10
hook, the whale counts, and the `wildlife_present: 2.0` weight — is a re-encoded,
AI-stabilised, AI-enhanced derivative being treated as source material. Any measurement of
"what this footage looks like" taken from Clip 3 measures Topaz, not the drone. This is
precisely the genealogy question drone_video_ai's own pack resolved by pixel-matching for
`DJI_0355_proxy.mp4`; the archived doc does not even pose it.

### 4.15 Clip 5's "different from others" note is wrong

SFA:319 — "This clip uses BT.709 colour space (not HLG), **different from others**". But
Clip 3 is BT.2020/PQ HDR (SFA:154), also not HLG. Two clips differ, not one.

### 4.16 Geography: Baja California vs fynbos

SFA:5 places the shoot in "likely Baja California, Mexico based on terrain and wildlife".
SFA:255 describes Clip 4's vegetation as "**fynbos**/chaparral type" — fynbos is endemic to
the South African Cape. The document's own vegetation identification points at a different
hemisphere from its own location guess. Both are unsourced speculation; recorded because
SFA:5's guess is stated in the Overview where it is most likely to be inherited as fact.

### 4.17 Filename timestamps vs "dusk"

Clips 4 and 5 are `DJI_20241030**011347**` and `DJI_20241030**011801**` — 01:13 and 01:18
by the DJI naming convention — yet are described throughout as dusk/sunset/golden hour
(SFA:248, 251, 327). Reconcilable via a UTC offset, but the document never notes or
resolves the discrepancy, and it is the only cross-check available on its "golden hour"
framing (which DTP:288 disputes anyway — see §4.6).

### 4.18 Corpus mismatch between the two documents — never reconciled

SFA documents **5 clips, ~96 s total, each an unbroken shot** (SFA:139 says so explicitly
for Clip 2). DTP is entirely about "**the DJI video**" that "produced **7 scenes**"
(DTP:5). Neither document names the file DTP analysed, states its duration, or explains
whether it is one of the five, a concatenation of them, or something else. Every tuning
recommendation in DTP is anchored to those 7 scenes, and there is no way to tell what they
were scenes *of*.

### 4.19 DTP's own bug report invalidates any claim that 27.0 was validated

DTP:22 and DTP:27–34 state that `split` and `extract_clips` **do not wire
`config.scene_threshold`** — both instantiate `SceneDetector()` with defaults. So whatever
run produced "7 scenes, 55-64" used the hardcoded default and **could not have been a test
of any tuned threshold**. The document simultaneously (a) reports an outcome, (b) reports
that the parameter under discussion was not connected during that outcome, and (c)
recommends changing that parameter based on the outcome.

### 4.20 A filter threshold exists for a metric that is never defined

`max_shake_score: float = 40.0` (DTP:163) and the tier rule "Filtered: ... shake > 40.0"
(DTP:174). No "shake score" is defined in §2.3 or anywhere else in the document. SFA
meanwhile rates every clip 9/10 or 10/10 for stability (SFA:55, 121, 192, 275, 352) — i.e.
the filter is inert against this footage regardless of its value.

### 4.21 The brightness argument is refuted by the document's own formula

DTP:285 asserts "Daytime footage: mean brightness 90-110 (all pass balance check) ... All
scenes near ideal, so **minimal brightness differentiation**". Apply the document's own
formula (DTP:143–145, ideal 127):

- mean 90 → deviation 37/127 = 0.291 → score **70.9**
- mean 110 → deviation 17/127 = 0.134 → score **86.6**

That is a **15.7-point spread** on a 0–100 scale — comparable to the spread the document
claims for motion or composition, and larger than the 9-point spread of the final scores
it is trying to explain (55–64). The document's stated cause of convergence is contradicted
by its own arithmetic.

---

## 5. Provenance verdict

**The corpus-wide pattern the sibling agents described — bare claims in the body, a bulk
topical URL list at the end, nothing linking any number to any source — holds for this
slice with ONE notable variation: there is no bulk URL list at the end either. These two
files contain zero URLs.**

Confirmed by grep (§1.1): the only matches for `http|www|.com|@|research|study|source|
according to|reference|cite` are a section heading ("## Research Summary", DTP:3), a Python
decorator (`@dataclass`, DTP:157), and three incidental word matches. Neither file has a
References section, a Sources section, a footnote, or a link of any kind.

So the attribution structure here is **weaker** than the rest of the corpus, not stronger.
Elsewhere a reader could at least see a pile of URLs at the end and understand that
*something* was consulted. Here, 237 numeric claims stand entirely alone.

The one partial exception is DTP's four `CODE-LOC` pointers (`config.py:27`,
`config.py:28`, `config.py:29`, `scene_detector.py:212`). These are **not citations for the
values** — they say where the constant is stored, which is a fact about the repository, not
evidence about the footage. Recording them as sources would be exactly the "upgrade a
vague pointer into a named source" error. Under the schema's definition (resolvable named
source — URL or named publication — *for that specific number*), the count of claims with a
named source is **0 of 237**.

One further provenance signal worth recording: SFA:502–505 ends with a cleanup note,
`rm -rf .drone_clips/analysis_frames/`. This is the **only** methodological trace in either
file, and it reveals that the per-clip content descriptions rest on **frames extracted to
disk and looked at** — i.e. vision-model inspection of stills, not measurement. It also
means the archived project routinely wrote frame files to disk, which drone_video_ai's
licence constraint absolutely forbids. Do not reproduce that method.

---

## 6. Were the thresholds derived from measuring the footage?

**Verdict: NO. On the balance of the evidence in these two documents, every threshold in
DTP appears chosen a priori — inherited from a library default, from a round-number
preference ordering, or from the 0–100/0–1 shape of its own scale — and none is shown to
have been derived from measuring this footage.** Presenting both sides, as required:

### 6.1 The evidence FOR footage-derived thresholds (stated at its strongest)

1. **DTP:5 reports an actual outcome**: "The DJI video case produced 7 scenes with similar
   scores (55-64 range)." This is phrased as a result, not a prediction. If true, it is one
   genuine observation of the pipeline's output on this footage.
2. **DTP §2.3/§5 supply per-metric ranges** (motion, composition, brightness, colour,
   sharpness) that are the *shape* of run output and are individually plausible.
3. **SFA's technical spec tables are internally consistent** — the five durations sum to
   the stated ~96 s and the five file sizes sum to the stated ~1.46 GB. Invented numbers
   rarely reconcile to two independent totals. These specs were very likely read off real
   files with a probe tool.
4. **SFA:502–505 proves frames were actually extracted** from the clips, so the content
   descriptions rest on something real being looked at.
5. **SFA:139 makes a correct, checkable structural claim** — Clip 2 is a "continuous shot,
   no internal scene changes" — which agrees with drone_video_ai's independent finding of
   zero hard cuts.

### 6.2 The evidence AGAINST — decisive

1. **Every per-metric range is grammatically hypothetical.** DTP:65 "likely scored";
   DTP:117 "likely score 50-70"; DTP:178 "**If** all 7 scenes have motion_energy in 35-50
   range (**likely** for consistent drone motion)"; DTP:271 "**Given** a sequence of 7
   landscape drone shots". Not one range is presented as recorded. No per-scene table, no
   timecodes, no scene IDs, no filename, no command, no date appears anywhere.
2. **The same metric drifts across three sections** (§4.1: motion 40-60 / 35-50 / 35-55).
   Measurements do not do this. Authored estimates do.
3. **The flagship calculation fails its own arithmetic** (§4.5: 62.2 written as 63.2, with
   an input range that shifts 55-64 → 55-65 and an unexplained "mean 58"). A number pasted
   from a run does not miscompute.
4. **Every constructor threshold is credited to a code location, never to a derivation**
   (DTP:15–18). The document is meticulous about *where* 27.0 lives and completely silent
   on *why* it is 27.0.
5. **27.0 is PySceneDetect's own ContentDetector default.** DTP:22 frames the parameter as
   "Controls ContentDetector sensitivity via PySceneDetect". This is a library default
   carried through unexamined — the textbook a-priori constant.
6. **DTP §9 is titled "Testing Plan ... Once parameters are implemented" (DTP:363–365).**
   The document states on its face that the validating runs had not been performed. The
   recommended 20–22 rests on a prediction ("Would detect 10-12 scenes instead of 7",
   DTP:309) that the document never checked.
7. **DTP's own bug report forecloses the strongest FOR argument.** Per DTP:22 and 27–34,
   `split`/`extract_clips` never wired `config.scene_threshold` — so the one real
   observation (7 scenes / 55-64) was produced with the parameter disconnected. It cannot
   be evidence that 27.0 suits this footage; it is only evidence of what the default did
   once.
8. **The normalisation constants have no possible footage origin.** Ideal brightness = 127
   is the midpoint of an 8-bit range. The motion divisor 3.0 (DTP:99) and sharpness divisor
   500.0 (DTP:135) are bare round numbers. The saturation scalars 50/50 over divisors
   255/128 (DTP:124) exist to make the output land in 0–100. These are scale-shaping
   choices, not measurements.
9. **The weight sets are preference ladders.** SFA:452–461 descends 2.0 → 0.9 in even
   steps. DTP:54–58 and DTP:75–81 are round fractions that each happen to total exactly
   1.00. Both are designed, and DTP's §2.2 reallocation of six weights is given without a
   single word of rationale.
10. **The filter thresholds are round numbers gating undefined or inert metrics** (§4.18,
    §4.20): 25.0 / 45.0 / 30.0 / 245.0 / 40.0 / 0.6, including a shake threshold for a
    metric the document never defines and which SFA's own 9–10/10 stability ratings make
    irrelevant to this footage.
11. **Zero external sources** (§5) — so the values are not from published practice either.
    They are from neither measurement nor literature.
12. **The footage cannot support the calibration in any case.** drone_video_ai's own
    reference pack independently measured this material and found **zero hard cuts**. A
    ContentDetector threshold is a cut-detection sensitivity; with no cuts present there
    are no true boundaries to calibrate against. Anything a threshold sweep produced on
    this footage would be false positives or `max_scene_length` forced splits — and note
    DTP:17's `max_scene_length` of 8.0 s (create) / 10.0 s (init), which is the far more
    likely explanation of "7 scenes" than any content detection. The reference pack further
    found the archived manifests' `scene_threshold` values sitting far above their own
    source's measured scdet scores (worst case ~36x), which is what a threshold picked
    without reference to the signal looks like.

### 6.3 Bottom line for drone_video_ai

Treat every value in §2.13–§2.24 as **an archived project's authored preference, not a
measurement**. Specifically, do not inherit:

- `scene_threshold = 27.0` or the proposed 20 / 20–22 (a PySceneDetect default and an
  untested prediction, against footage with no cuts to detect);
- `min_scene_length = 1.0` / `max_scene_length = 8.0`–`10.0` (unattributed; and the most
  probable actual cause of the "7 scenes" the whole document is reasoning about);
- the hook tiers 80 / 65 / 45 / 25 (unattributed viewer-engagement boundaries that, applied
  to SFA's own clip scores, tier 4 of 5 clips identically — §4.4);
- the weight sets 0.30/0.20/0.20/0.15/0.15 and 0.25/0.25/0.15/0.15/0.10/0.10, or SFA's
  2.0/1.5/1.4/1.3/1.2/1.1/1.0/0.9;
- `motion_weight = 0.15` (a range endpoint chosen for no stated reason — §4.2);
- the "Opening 3 seconds rule" (SFA:435), the single most portable and least supported
  editorial constant in this slice;
- `subject_score` 0.6 / 0.3 / 0.5 / 0.4 / 0.35 (six values, no governing one — §4.3);
- normalisation constants 3.0, 500.0, 127, 255/128×50 (§2.17).

---

## 7. Second-pass verification log (2026-07-28, independent re-read)

This checkpoint was written by a first dispatch of `census2-eval-c` that landed the file but
stalled before returning. A second dispatch re-read both source files end to end (924 lines)
without inheriting the first pass's conclusions, and re-checked its load-bearing assertions
with external tools. Recorded per the Constitution's tool-grounded-verification rule.

| # | Assertion re-tested | Method | Result |
|---|---|---|---|
| 1 | Zero URLs in either file | `grep -nEo 'https?://[^ )"]+'` over both | **CONFIRMED** — zero matches |
| 2 | Zero named creators / reference videos | grep for `@[a-z]`, instagram, tiktok, youtube, creator | **CONFIRMED** — only `@dataclass` (DTP:157) and "Instagram Reels" (SFA:383) |
| 3 | DTP:298 arithmetic is wrong | `python3` — `0.6*65+0.4*58` | **CONFIRMED** = 62.2, doc states 63.2 |
| 4 | Clip durations sum to stated ~96 s | `python3` — 16.23+3.80+26.53+25.54+24.04 | **CONFIRMED** = 96.14 |
| 5 | File sizes sum to stated ~1.46 GB | `python3` — 255+61+372+401+377 | **CONFIRMED** = 1466 MB |
| 6 | `25:00-26:53` is 1.53 s, not "2s" | `python3` — 26.53−25.00 | **CONFIRMED** = 1.53 |
| 7 | Option A totals 29.53 s, Option B 44.84 s | `python3` over the beat lists | **CONFIRMED** (stated 30 s / 45 s) |
| 8 | §4.21 brightness spread 70.9–86.6 | `python3` over DTP's own formula at mean 90 and 110 | **CONFIRMED**, 15.7-point spread |
| 9 | The 5 SFA files physically exist with matching sizes | `ls -la` on `_archive/.../.drone_clips/` (read-only, no writes) | **CONFIRMED** — all 5 present; e.g. `DJI_20241029173912_0350_D.MP4` = 255,015,141 bytes ≈ the doc's "255 MB" (decimal MB) |
| 10 | `analysis_frames/` (SFA:504 cleanup note) still exists | `ls -d` | **ABSENT** — the cleanup was carried out, or the directory was never retained. The frame-extraction method is attested only by the cleanup line itself. |
| 11 | Line citations in §2.17 (composition), §2.18 (FilterThresholds), §3.2 tier rules, and the two SFA cites for "Opening 3 seconds rule" / "fynbos" | `grep -n` on each literal string | **4 groups CORRECTED** — first pass was off by one (FilterThresholds block, tier rules, SFA:436→435, SFA:256→255) and off by two (composition sub-weights, DTP:112–114→113–115). All other spot-checked cites (SCENE_WEIGHTS 453–460, DTP:99–101, :124, :135, :143–145, :204–207, SFA:139, :156, :206, :212, :319, :414–415) verified correct as written. |

**No substantive finding changed.** Counts (237 claims / 0 named sources / 0 reference
videos), all 21 contradictions, and both verdicts (§5, §6) survive independent re-derivation.
The only defects found were citation line-number drift, now fixed.

**One caveat on the claim tally that a downstream reader must not lose:** the 237 figure is a
*counting convention*, not a measurement — it counts individual number-bearing values (a
5-column spec row counts 5), and §2.25 shows the derivation so it can be audited. A different
convention (per table row, or per distinct constant) would yield a materially different total.
What is robust regardless of convention is the ratio: **the numerator of "claims with a named
source" is zero under every convention**, because both files contain no external source of
any kind.

If any of these must be used, they must be re-derived by measurement against
`00-assets/drone-video-examples/` and recorded in `data/reference_pack/` with the
measurement that produced them — which is exactly what the pack exists for.
