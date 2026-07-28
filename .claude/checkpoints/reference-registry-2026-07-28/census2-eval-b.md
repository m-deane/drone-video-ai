# Census 2 — Slice B: Qualitative / Visual Scoring Docs

**Agent:** census2-eval-b · **Date:** 2026-07-28 · **Status:** COMPLETE

**Corpus under audit** (READ-ONLY, `_archive/_p-ai-drone-video/.claude_plans/`, 788 lines total):

| # | File | Lines | Date it self-reports |
|---|---|---|---|
| 1 | `v21_visual_analysis.md` | 218 | 2026-02-20 |
| 2 | `v2_vs_viral_comparison.md` | 418 | (none stated) |
| 3 | `reel_review_vs_viral.md` | 152 | 2026-02-08 |

**Trust posture:** these are LLM-generated planning documents from an archived project. Nothing
below is asserted as true. Every row records what the document *says* and what the document
*credits it to*. `NONE` is the overwhelmingly common — and correct — provenance verdict.

---

## 0. Headline findings

1. **Zero URLs. Zero named sources. Zero citations of any kind.** `grep -niE 'http|www\.|\.com|@[a-z]|source:|according|study|research|cite|reference'` across all three files returns **no** external reference. Unlike the sibling agents' files, these three do **not even have a bulk topical URL list at the end** — the attribution floor here is lower still. See §5.
2. **Zero reference videos. Zero named exemplar creators.** Not one specific third-party video, channel, account, or creator is named anywhere in 788 lines. The "viral benchmark" is a disembodied, unattributed authority voice.
3. **No rubric in any of the three files defines its scale anchors.** One (`v21` §3) declares the *range* ("each out of 10") and its aggregate is arithmetically reconstructible; the other two scales (`45/100`, `Viral Score x/10`, `Hook score x/100`) are neither anchored nor reconstructible. See §1 — this is the core deliverable of this unit.
4. **The range→point→code-default failure pattern the parent flagged is present, and worse than described**: the LUT range `40-70%` collapses to **two different** point values in two different documents (`0.5` and `60%`), and a third document prescribes an entirely different quantity for the same job (`1.3-1.5x saturation`). The clip-length range `1.5-3s` acquires a `target_avg=2.5` code default that has **no prose antecedent anywhere**.
5. **A range was copied across a duration change without recomputation** (`8-15 clips`, correct for 22.9 s at line 43, arithmetically impossible at its 8-clip lower bound for 30 s at line 329). See §4 C4.
6. **`v21` scores categories its own stated method admits it cannot observe** — line 167 says transitions are "Hard to evaluate from stills" and assigns `4/10` on the same line.

---

## 1. Rubric scale definitions — THE CORE QUESTION

Verdict: **NO rubric in this slice defines anchors, weights, rater, or method.** Four distinct
invented numeric scales are used across three files; none is operationalised.

| Scale | Where | Range declared? | Anchors defined? | Weights stated? | Method/rater stated? | Aggregate reconstructible? |
|---|---|---|---|---|---|---|
| **A. Category score /10** | `v21:155-168` | YES — "Scoring Criteria (each out of 10)" | **NO** — no description of what a 2, 5 or 8 means for any category | **NO** | **NO** | — |
| **B. Overall score /10** | `v21:174-175` | implied by A | **NO** | **NO** | **NO** | **YES** — `(2+4+3+6+5+5+8+8+4+5)/10 = 50/10 = 5.0`. The doc never states this is an unweighted mean; it is reconstructible only by inspection. |
| **C. "Viral Score" /10 (per segment)** | `v2:24-30` | **NO** — column header only | **NO** | n/a | **NO** | n/a |
| **D. "V2 Score" /100** | `v2:5` ("45/100") | **NO** | **NO** | **NO** | **NO** | **NO** — 45 is not derivable from any table, sum, or weighting in the file. It appears once and is never decomposed. |
| **E. "Hook score" /100** | `v2:389` (20/100 → 80/100, standard 85+) | **NO** | **NO** | n/a | **NO** | **NO** — and `20/100` is the same judgement as `2/10` at `v2:26` / `v21:159`, silently rescaled. |
| **F. Ordinal verdicts** | `reel_review:36-46` (`PERFECT`/`GOOD`/`OPTIMAL`) | n/a | **NO** — `OPTIMAL` is applied at :41 to 2.7 s while :390 of the sibling doc sets the target at 2.5 s and :80 sets the exemplar at 3.0 s | n/a | **NO** | n/a |

**Method transparency in `v21`.** The document states its evidence base is **still frames sampled
at 0, 3, 5, 7, 10, 12, 15, 17, 20, 22, 25 s** — 11 samples of a self-declared ~30.6 s video, with
**no sample after 25 s**. It nonetheless issues whole-reel scores for `Pacing/Energy` (`3/10`),
`Transitions` (`4/10`) and `Stabilization` (`8/10`) — three properties not observable in a still.
Line 167 makes the contradiction explicit in the same cell as the score:
> "Hard to evaluate from stills but scene changes appear abrupt ... | 4/10"

This is the textbook shape of the failure this project guards against: an undefined 0-10 score,
produced by an unstated method that the document itself concedes cannot see the property being
scored, presented in a bolded summary table as evidence.

---

## 2. Numeric editorial claims — FULL TABLE

Legend for **Source**: `NONE` = document credits it to nothing. `SELF-MEAS(untooled)` = a
measurement of the project's own output, but with **no tool, command, or log named** — not a
citation, and not reproducible from the document. `"viral benchmark"` = the document's own
unattributed authority phrase, which is **not** a named source.

### 2A. `v21_visual_analysis.md` (34 claims)

| # | Cite | Subject | Value | Source the doc credits |
|---|---|---|---|---|
| 1 | v21:8 | resolution | 2160x3840 | SELF-MEAS(untooled) |
| 2 | v21:8 | letterbox_aspect | 9:16 | SELF-MEAS(untooled) |
| 3 | v21:8 | framerate | 30 fps | SELF-MEAS(untooled) |
| 4 | v21:8 | bitrate | ~80 Mbps (H.264 yuv420p) | SELF-MEAS(untooled) |
| 5 | v21:8 | total_duration | ~30.6 s | SELF-MEAS(untooled) |
| 6 | v21:24 | hook_timing | attention-grabbing first frame required **within 0.5 s** | NONE |
| 7 | v21:33 | retention | "most viewers decide to stay or scroll **within 1-2 seconds**" | NONE |
| 8 | v21:42 | shot_length | 5 s of one clip "far too long ... in a 30s reel" | NONE |
| 9 | v21:64 | shot_length | "A **5+ second** hold ... too long for viral pacing" | NONE |
| 10 | v21:73 | shot_length | opening ocean scene = **0-6 s** | SELF-MEAS(untooled) |
| 11 | v21:73 | shot_length | ocean+mountains = **7-12 s** | SELF-MEAS(untooled) |
| 12 | v21:138 | shot_length | "Ocean scenes (**0-12s**)" | SELF-MEAS(untooled) |
| 13 | v21:139 | shot_length | "Mountain scenes (**15-20s**)" | SELF-MEAS(untooled) |
| 14 | v21:140 | shot_length | "Marine life scenes (**22-25s**)" | SELF-MEAS(untooled) |
| 15 | v21:159 | other (rubric) | Opening Hook **2/10** | NONE (scale undefined) |
| 16 | v21:160 | other (rubric) | Scene Variety **4/10**; "only **3 distinct scenes in 30s**" | NONE |
| 17 | v21:161 | other (rubric) | Pacing/Energy **3/10** | NONE |
| 18 | v21:162 | other (rubric) | Composition Quality **6/10** | NONE |
| 19 | v21:163 | colour_grade | Color Grading **5/10** | NONE |
| 20 | v21:164 | other (rubric) | Exposure/Dynamic Range **5/10** | NONE |
| 21 | v21:165 | resolution | Sharpness/Detail **8/10** | NONE |
| 22 | v21:166 | other (rubric) | Stabilization **8/10** | NONE |
| 23 | v21:167 | transition_duration | Transitions **4/10** — same cell admits "Hard to evaluate from stills" | NONE |
| 24 | v21:168 | other (rubric) | Subject Interest **5/10** | NONE |
| 25 | v21:174 | other (rubric) | Adaptive Stabilization overall **5.0/10** | NONE (= unweighted mean of #15-24, undeclared) |
| 26 | v21:175 | other (rubric) | Full Stabilization overall **5.0/10** | NONE (same) |
| 27 | v21:185 | shot_length | ocean clip "runs **~7 seconds** (0-7s)" | SELF-MEAS(untooled) |
| 28 | v21:185 | shot_length | "= **23%** of the entire reel" | derived (7/30.6 = 22.9% — arithmetic checks out) |
| 29 | v21:185 | shot_length | "Maximum clip duration for a 30s reel should be **3-4 seconds**" | NONE |
| 30 | v21:187 | cut_rate | "Viral drone reels typically show **8-12 distinct locations/angles in 30 seconds**" | NONE ("typically") |
| 31 | v21:191 | saturation | "Recommend **1.3-1.5x saturation boost**" | NONE |
| 32 | v21:195 | transition_duration | "smooth crossfades (**0.3-0.5s**)" | NONE |
| 33 | v21:205 | letterbox_aspect | "**9:16** vertical reframe appears to be using center-crop" | SELF-MEAS(untooled) |
| 34 | v21:213 | resolution | source "Native **4K**, clean and sharp" | SELF-MEAS(untooled) |

### 2B. `v2_vs_viral_comparison.md` (41 claims)

| # | Cite | Subject | Value | Source the doc credits |
|---|---|---|---|---|
| 35 | v2:5 | other (rubric) | "**Current V2 Score: 45/100**" | NONE — scale undefined, value not derivable |
| 36 | v2:11 | cut_rate | V2 **4.6s avg** vs Viral Standard **1.5-3s avg** | NONE for the standard |
| 37 | v2:15 | total_duration | V2 **22.9s** vs Viral Standard **15-30s** → graded ✅ Good | NONE for the standard |
| 38 | v2:22 | total_duration | "V2 Timeline (**22.9 seconds, 5 clips**)" | SELF-MEAS(untooled) |
| 39 | v2:26 | other (rubric) | 0-4s ocean texture — **2/10** | NONE (scale undefined) |
| 40 | v2:27 | other (rubric) | 4-8s golden hour mountains — **7/10** | NONE |
| 41 | v2:28 | other (rubric) | 8-13s ocean horizon — **4/10** | NONE |
| 42 | v2:29 | other (rubric) | 13-18s mountain peak — **6/10** | NONE |
| 43 | v2:30 | other (rubric) | 18-23s boats/marina — **5/10** | NONE |
| 44 | v2:39 | retention | "**65% of viewers lost in first 3 seconds**" | NONE |
| 45 | v2:42 | cut_rate | "5 clips / 22.9s = **4.58s** average" | derived (arithmetic checks out) |
| 46 | v2:43 | shot_length | Needed: **1.5-3s per clip (8-15 clips** for 22.9s) | NONE |
| 47 | v2:44 | retention | "**35% lower completion**" | NONE |
| 48 | v2:49 | other (engagement) | "**40% less engagement**, no algorithm boost" | NONE |
| 49 | v2:54 | speed_ramp | "**22% less watch time**" (from missing speed ramps) | NONE |
| 50 | v2:68-77 | cut_rate | "Typical Viral Drone Reel Structure (30s)" — 10 blocks of 3 s; HOOK 0-3s, CLIMAX **12-15s**, Resolve 18-24s, END 27-30s | NONE ("typical") |
| 51 | v2:80 | cut_rate | "**Clip Count: 10 clips in 30s = 3s average**" | NONE |
| 52 | v2:92 | cut_rate | "5 clips in 22.9s = **4.6s average (TOO SLOW)**" | derived |
| 53 | v2:114-129 | other (threshold) | Hook scoring weights: FPV/REVEAL/APPROACH **+40**, ORBIT **+30**, PAN **+20**, STATIC **+5**; moving subject **+30**; `color_score * 0.15`; `sharpness_score * 0.15` | NONE — invented constants, no derivation, no prose antecedent |
| 54 | v2:137 | shot_length | current impl: "Clips can be any length **up to 5s**" | SELF-MEAS(untooled) |
| 55 | v2:142 | shot_length | `min_clip=1.5, max_clip=3.0, **target_avg=2.5**` | NONE — `2.5` has **no prose antecedent anywhere in the corpus** |
| 56 | v2:213-218 | speed_ramp | REVEAL ramp: start_speed **1.0** → end_speed **0.5**, margins **0.5 s** each end, `ease_in_out` | NONE |
| 57 | v2:225-230 | speed_ramp | drop ramp: start_speed **1.5** → end_speed **0.6**, window **drop ±0.5 s** | NONE |
| 58 | v2:255 | audio_bpm (audio) | `audio_fadein(**0.5**)` / `audio_fadeout(**1.0**)` seconds | NONE |
| 59 | v2:264 | other | "**4/8 frames** in v2 are similar blue ocean shots" | NONE — denominator 8 contradicts the file's own "5 clips" |
| 60 | v2:270 | other (threshold) | `diversity_score = **100**` base | NONE |
| 61 | v2:279-280 | other (threshold) | `color_sim > **0.8**` → **-10** | NONE |
| 62 | v2:283-284 | other (threshold) | same motion type → **-15** | NONE |
| 63 | v2:287-288 | other (threshold) | same source file → **-5** | NONE |
| 64 | v2:328 | shot_length | "Enforce **1.5-3s** per clip" | NONE |
| 65 | v2:329 | cut_rate | "Target **8-15 clips for 30s reel**" | NONE — see contradiction C4 |
| 66 | v2:335-338 | hook_timing | Hook **0-3s** / Build **3-15s** / Climax **15-22s** / Resolve **22-30s** | NONE — contradicts #50 in same file |
| 67 | v2:347 | colour_grade | "Color grading (**teal-orange @ 60%**)" | NONE — point collapse of the 40-70% range |
| 68 | v2:370 | text_overlay | "Location tag (**1-3s** in)" | NONE |
| 69 | v2:378 | resolution | export **1080x1920 @ 30fps** | NONE |
| 70 | v2:379 | bitrate | export **H.265, 10-12 Mbps** | NONE |
| 71 | v2:389 | other (rubric) | Hook score: V2 **20/100** → V3 target **80/100** → Viral Standard **85+** | NONE — scale undefined |
| 72 | v2:390 | cut_rate | Clip frequency: **4.6s** → target **2.5s** → standard **1.5-3s** | NONE |
| 73 | v2:392 | speed_ramp | Speed ramps: None → **3-5 per reel** → "Throughout" | NONE |
| 74 | v2:393 | retention | 3s retention: **~35%** → **65%+** → viral standard **65%** | NONE |
| 75 | v2:394 | retention | Completion rate: **~40%** → **70%+** → viral standard **72%** | NONE |

### 2C. `reel_review_vs_viral.md` (21 claims)

| # | Cite | Subject | Value | Source the doc credits |
|---|---|---|---|---|
| 76 | reel:13 | total_duration | **27.10 s** | SELF-MEAS(untooled) |
| 77 | reel:14 | resolution | **1080x1920 (9:16)** | SELF-MEAS(untooled) |
| 78 | reel:15 | framerate | **30** fps | SELF-MEAS(untooled) |
| 79 | reel:16 | other | file size **46 MB** | SELF-MEAS(untooled) |
| 80 | reel:17 | cut_rate | **10 clips** used from **14 detected scenes** | SELF-MEAS(untooled) |
| 81 | reel:21 | other | Stabilization Adaptive (**7 stabilized, 3 skipped**) | SELF-MEAS(untooled) |
| 82 | reel:40 | cut_rate | Viral target "**4-8 clips for 15s**"; ours "10 clips for 27s (**~2.7s avg**)" → GOOD | NONE for the target |
| 83 | reel:41 | shot_length | Viral target avg clip length "**1.5-3s**"; ours ~2.7 s → **OPTIMAL** | NONE |
| 84 | reel:51 | other (engagement) | "Music is mandatory; **trending audio = +42% engagement**" | NONE — labelled only "Viral benchmark" |
| 85 | reel:57 | total_duration | "**7-15s** achieves highest completion rates; **max 30s** for drone content" | NONE |
| 86 | reel:60 | total_duration | "Default to **15s** for maximum viral potential" | NONE |
| 87 | reel:63 | speed_ramp | "Speed ramps are a **top-5** transition technique for drone reels" | NONE — ranking with no ranked list anywhere |
| 88 | reel:69 | other (viewer) | "**80% of Instagram users watch on mute**; captions essential" | NONE |
| 89 | reel:75 | colour_grade | "Apply LUTs at **40-70% intensity**" | NONE |
| 90 | reel:76 | colour_grade | ours: "Full **100%** drone_aerial grade" | SELF-MEAS(untooled) |
| 91 | reel:78 | colour_grade | Fix: "`--color-intensity **0.5**`" | NONE — point collapse, see C1 |
| 92 | reel:88 | hook_timing | "First **2-3 seconds** need 'jaw-dropping' moment" | NONE |
| 93 | reel:106 | colour_grade | "`--color-intensity **0.5**` (**40-70%** range)" — point and range stated side by side, 0.5 is the low edge, not the 0.55 midpoint | NONE |
| 94 | reel:116 | total_duration | presets: viral-short **7-15s**, viral-medium **15-30s** | NONE |
| 95 | reel:143 | total_duration | recommended `--duration **15**` | NONE |
| 96 | reel:146 | resolution | recommended `--resolution **4k**` | NONE — contradicts v2:378 |

**Excluded as out of scope** (pipeline performance, not output/viewer): `reel:24-28` scene
analysis 52m50s / motion 13m7s / stitching 7m49s / grading 2m58s / total ~77 min; `reel:84`
52-min bottleneck. `reel:80`'s "77 min for **30s** reel" is retained only as contradiction C11.

**TOTALS: 96 numeric editorial claims. 0 carry a resolvable named source.**
Breakdown of provenance: `NONE` = 74 · `SELF-MEAS(untooled)` = 19 · `derived arithmetic` = 3.
Even the 19 self-measurements name no tool, command, or log, so none is reproducible from the
document; they are not citations and were **not** counted as sourced.

---

## 3. Reference videos and exemplar creators

**COUNT: 0.** Strict test applied (a specific identifiable third-party video, or a named creator
held up as an exemplar).

Exhaustive check of every candidate:

| Candidate | Cite | Verdict |
|---|---|---|
| "Typical Viral Drone Reel Structure (30s)" | v2:65-78 | **NOT a reference video** — a synthesised generic template. No title, creator, platform, or link. |
| "Viral benchmark:" ×8 | reel:51,57,63,69,75,81,88,94 | **NOT a source** — an unattributed authority label. No named benchmark set, no sample, no n. |
| "Viral Standard" column | v2:7-16, 387-394 | **NOT a source** — column header only. |
| "Viral drone reels typically show 8-12 ..." | v21:187 | **NOT a source** — "typically", no corpus named. |
| "Instagram/TikTok" | v21:24 | Platform names, not videos or creators. |
| "top-5 transition technique" | reel:63 | A ranking with no ranked list, no ranker, no source. |
| Named modules (`SpeedRamper`, `DiversitySelector`, `TextOverlay`, `BeatSynchronizer`, `SaliencyReframer`) | v2 & reel throughout | The archived project's **own** code. Not third-party. |
| `moviepy`, `cv2` | v2:177, 247 | Libraries, not exemplars. |

No Instagram/TikTok/YouTube handle, no follower count, no creator name appears in this slice —
**consistent with, but not a duplicate of, the sibling agents' finding**: the four handles
(@thedronecreative, @beverlyhillsaerials, @basso2012, @simeonpratt) and the single TikTok URL they
located are **absent from all three of my files**.

---

## 4. Internal contradictions

Ordered by consequence. `[X-FILE]` = across files in this slice; `[SAME-FILE]` = within one file.

### C1 — Colour-grade intensity: one range, two different point collapses, plus a third incompatible prescription `[X-FILE]`
- **Range:** "Apply LUTs at **40-70%** intensity" — `reel:75`, `reel:106`
- **Point A:** `--color-intensity **0.5**` — `reel:78`, `reel:106` (stated *beside* the range, on the low edge; the range midpoint is 0.55)
- **Point B:** "teal-orange @ **60%**" — `v2:347` (baked into the recommended V3 pipeline diagram)
- **Prescription C:** "**1.3-1.5x saturation boost**" — `v21:191` — a *multiplier on saturation*, not a LUT-blend fraction; not commensurable with either point value
- **Direction flip:** `reel:74` files "Color Grade Intensity **Too Strong**" as GAP 5 (output at 100%), while `v2:13` grades the colour grade "**✅ Applied / Good**" and `v21:163` scores it **5/10** with the opposite complaint — "**too subtle** for social media ... lacks punch" (`v21:191`). The same subsystem is simultaneously too strong, fine, and too weak.
- **This is the parent's documented failure pattern, instantiated twice from one range.** Neither point value is justified anywhere.

### C2 — Optimal total duration: three incompatible answers `[X-FILE]`
- `reel:57` — "**7-15s** achieves highest completion rates; max 30s"; `reel:60` "Default to **15s**"; `reel:116` viral-short = 7-15s
- `v2:15` — Viral Standard "**15-30s**"; the 22.9 s output is graded **✅ Good** on that basis
- `v21` — analyses a **~30.6 s** reel across 218 lines and never once flags duration as a problem; §4 P0/P1/P2 (lines 181-205) list ten improvements, none about length
- The lower bound moves 7 → 15 and the whole window shifts by more than 2× depending on which file you read.

### C3 — Hook window: four values, two of them nine lines apart in the same file `[SAME-FILE] + [X-FILE]`
- "attention-grabbing first frame **within 0.5s**" — `v21:24`
- "most viewers decide to stay or scroll **within 1-2 seconds**" — `v21:33` (same file, 9 lines later)
- "First **2-3 seconds** need a 'jaw-dropping' moment" — `reel:88`
- "Hook (**0-3s**)" — `v2:9`, `v2:36`, `v2:68`, `v2:335`
- A 6× spread on the single most consequential timing constant in the whole design.

### C4 — "8-15 clips for a 30s reel" is arithmetically impossible at its own lower bound `[SAME-FILE]`
- `v2:43` states "**1.5-3s** per clip (**8-15 clips** for same duration)" — for the **22.9 s** V2 reel this is sound (8 × 3 s = 24 s ≥ 22.9 s ✓).
- `v2:328-329` restates "Enforce **1.5-3s** per clip / Target **8-15 clips** for a **30s** reel" — but 8 clips × 3.0 s max = **24 s**, and 9 × 3.0 = 27 s. **No clip count below 10 can fill 30 s** under the stated 3.0 s cap.
- The range was transplanted from a 22.9 s context to a 30 s context without recomputation. Anyone inheriting `8` as a minimum clip count for a 30 s reel inherits an impossibility.

### C5 — `target_avg=2.5` is a code default with no prose antecedent anywhere `[SAME-FILE]`
- `v2:142`: `def __init__(self, min_clip=1.5, max_clip=3.0, **target_avg=2.5**)`
- `min_clip`/`max_clip` trace to the prose range "1.5-3s". **`2.5` traces to nothing** — it appears in no prose sentence in any of the three files before this line.
- It is then laundered into an *objective*: `v2:390` "Clip frequency | 4.6s avg | **V3 Target 2.5s** avg". An invented constructor default has become a success metric within the same document.
- Meanwhile `v2:80` sets the exemplar average at **3.0 s** and `reel:41` calls **2.7 s** "OPTIMAL". Three different "right answers" inside one 1.5-3 s band.

### C6 — Export spec: ~7× bitrate disagreement and a resolution disagreement `[X-FILE]`
- `v2:378-379` — "1080x1920 @ 30fps / **H.265, 10-12 Mbps**"
- `v21:8` — the actually-produced reel is "2160x3840 ... **H.264** ... **~80 Mbps**"
- `reel:146` — recommends `--resolution **4k**` "for maximum sharpness"; `reel:14` reports the tested output at 1080x1920
- No document acknowledges the other's figure. Nothing states which is the target.

### C7 — Two different narrative structures for a 30 s reel, in one file `[SAME-FILE]`
- `v2:68-77`: HOOK 0-3s · Build 3-12s · **CLIMAX 12-15s** · Peak 15-18s · Resolve 18-24s · Close 24-27s · END 27-30s
- `v2:335-338`: Hook 0-3s · Build 3-15s · **Climax 15-22s** · Resolve 22-30s
- The climax moves by 3-7 s between the "viral example" section and the "recommended V3 pipeline" section of the same document.

### C8 — Maximum clip duration: 3-4 s vs 3.0 s `[X-FILE]`
- `v21:185` — "**Maximum** clip duration for a 30s reel should be **3-4 seconds**"
- `v2:11`, `v2:43`, `v2:328`, `v2:390`, `reel:41` — target band tops out at **3.0 s**; `v2:142` hard-codes `max_clip=3.0`
- v21's ceiling is up to 33% higher than the other two files' ceiling, with no acknowledgement.

### C9 — Audio engagement effect: +42% vs −40%, near-identical magnitude, opposite framing, no source for either `[X-FILE]`
- `reel:51` — "trending audio = **+42% engagement**"
- `v2:49` — no audio ⇒ "**40% less engagement**"
- These are not reconcilable as the same statistic (a +42% gain from a base is not a 40% loss from a base), and neither is attributed. The proximity of the magnitudes suggests one number was reproduced from memory of the other.

### C10 — Clip-count denominator contradicts the file's own clip count `[SAME-FILE]`
- `v2:22` and `v2:92` — the V2 reel is "**5 clips**"
- `v2:264` — "**4/8 frames** in v2 are similar blue ocean shots"
- The denominator **8** is never explained; if these are sampled frames, the sampling scheme is never stated, and the "4/8 = half the reel is blue ocean" inference is used to justify the diversity-scoring penalties at `v2:279-288`.

### C11 — A 27.10 s output is called a "30s reel" twice `[SAME-FILE]`
- `reel:13` — Duration **27.10s**; `reel:80` "Processing Time (77 min for a **30s** reel)"; `reel:82` "77 minutes for a single **30s** reel"

### C12 — `v21`'s own scene timeline does not cover the reel `[SAME-FILE]`
- `v21:138-140` label the reel as Ocean **0-12s** / Mountain **15-20s** / Marine **22-25s**.
- **12-15 s, 20-22 s, and 25-30.6 s are unaccounted for** — 8.6 s of a ~30.6 s reel, i.e. ~28%, including the entire ending.
- Yet `v21:160` scores "Scene Variety 4/10 — only **3 distinct scenes in 30s**", a count that depends on the unexamined 28% containing nothing new. The doc also never scores the close, while `v21:197` asserts a viral reel should "close with a memorable moment".

### C13 — Ocean clip length stated twice, differently `[SAME-FILE]`
- `v21:73` — "featureless ocean (**0-6s**)"
- `v21:185` — "The ocean surface clip runs **~7 seconds (0-7s)**", from which the headline "**23%** of the entire reel" is computed. The percentage would be 20% on the other figure.

### C14 — Hook score silently rescaled between /10 and /100 `[SAME-FILE] + [X-FILE]`
- `v2:26` "0-4s ... **2/10**"; `v21:159` "Opening Hook **2/10**"; `v2:389` "Hook score **20/100**"
- Same judgement, two undeclared scales, and the /100 version acquires a "Viral Standard **85+**" that has no counterpart on the /10 scale and no anchor on either.

### C15 — Retention figures are internally consistent but numerically self-referential `[SAME-FILE]`
- `v2:39` "**65%** of viewers lost in first 3 seconds" and `v2:393` "3s retention | ~**35%**" are consistent (100 − 65 = 35). **Noted as a consistency, not a contradiction.**
- However `v2:393` also sets the *viral standard* for 3 s retention at exactly **65%** — the same number as the loss figure, now with the opposite meaning. And `v2:44`'s "**35% lower completion**" does not reconcile with `v2:394`'s V2 ~40% vs standard 72% (a 32 pp / 44% relative gap). The three retention numbers 65 / 35 / 65 appear to be one number reused rather than three measurements.

### C16 — `v21` scores properties its stated method cannot observe `[SAME-FILE]`
- Evidence base is 11 still frames (`v21:14-128`), none after 25 s.
- `v21:167` assigns Transitions **4/10** while stating in the same cell "**Hard to evaluate from stills**".
- `v21:161` assigns Pacing/Energy **3/10** and `v21:166` Stabilization **8/10** — neither observable in a still frame. `v21:147` even concedes the stabilization comparison is "extremely subtle **in still frame analysis**" and then scores both 8/10 and declares a winner.
- These three scores contribute 15 of the 50 points behind the headline **5.0/10**.

---

## 5. Provenance verdict

**The sibling agents' corpus-wide pattern holds for my three files in its "bare body" half, and is
strictly worse in its "bulk list" half.**

- **Bare claims in the body: CONFIRMED.** All 96 numeric claims are stated flat, in prose, tables,
  or code, with no inline attribution. Not one number is followed by a parenthetical, footnote,
  superscript, or link.
- **Bulk topical URL list at the end: ABSENT — this is an exception to the corpus pattern.** None
  of the three files has a references, sources, or links section. `grep -niE 'http|www\.|\.com'`
  returns zero matches across all 788 lines. Where the sibling agents' files at least gestured at a
  reading list, these files have **no external reference of any kind** — the attribution floor here
  is lower.
- **Nothing maps any number to any source: CONFIRMED**, trivially, since no sources exist.
- **The substitute for citation is a stock phrase.** `reel_review_vs_viral.md` uses the bolded
  label "**Viral benchmark:**" eight times (lines 51, 57, 63, 69, 75, 81, 88, 94) to introduce its
  most specific quantitative claims (+42% engagement, 80% watch on mute, 40-70% LUT intensity,
  7-15 s duration). `v2_vs_viral_comparison.md` uses a "**Viral Standard**" table column the same
  way. These are **not** sources — no benchmark set, corpus, sample size, date, or measurer is
  named — but they are formatted to read like ones. That formatting is the specific hazard here:
  a downstream reader skimming `reel:75` sees a labelled benchmark, not an unsourced assertion.
- **Self-measurements are not exempt.** The 19 `SELF-MEAS(untooled)` rows describe the archived
  project's own output, which is the one thing these documents could legitimately have measured —
  yet none names `ffprobe`, a command, a log, or a file hash. `v21:8`'s "~80 Mbps" and `reel:16`'s
  "46MB" are as unreproducible from the document as "+42% engagement" is.

**Consequence for `drone_video_ai`.** Nothing in this slice is usable as grounding for a threshold.
The four scoring scales (§1) are unanchored, and the three highest-traffic constants — clip length
`1.5-3.0 s`, LUT intensity `40-70% / 0.5 / 60%`, hook window `0.5 / 1-2 / 2-3 / 0-3 s` — each
disagree with themselves across the slice. Any number lifted from here would be exactly the
"invented constant" the project Constitution prohibits.

---

## 6. Method note

Read all 3 files end to end (788 lines, Read tool, full range, no truncation). Provenance search
was a single `grep -niE 'http|www\.|\.com|@[a-z]|source[s]?:|according|study|studies|research|cite|
citation|reference|instagram\.com|tiktok|youtube|per |benchmark'` over all three files —
23 hits, all of them either prose using the word "benchmark"/"reference" generically, layout
terms ("upper third", "two-thirds"), or Python identifiers. Zero URLs. Arithmetic checks
(#28, #45, #52, C4, C15, and the 5.0/10 mean in §1) were done by hand and are stated with their
working so a reviewer can re-derive them. No network access was used; no file under `_archive/`
was written, moved, or modified; no image or frame file was created.
