# census2-eval-a — Reference & Claim Registry

**Agent slice:** `v21_viral_benchmark_review.md` + `v21_technical_analysis.md`
**Date:** 2026-07-28
**Status:** COMPLETE

## 0. Standing caveats

- Both source files are **untrusted, LLM-generated planning documents** from the archived
  `_p-ai-drone-video` project (dated 2026-02-20). Nothing below is asserted as true. Every row
  records **what the document claims** and **what the document credits it to**.
- Read-only: `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video` was
  never written to. No network requests were made. No image/frame file was written.
- URL liveness was NOT checked (out of scope, reserved for the user) — and is moot here: see §3.

---

## 1. Files read

| Path | Lines | Read |
|---|---|---|
| `/Users/mac/.../_archive/_p-ai-drone-video/.claude_plans/v21_viral_benchmark_review.md` | 275 | full, 1–275 |
| `/Users/mac/.../_archive/_p-ai-drone-video/.claude_plans/v21_technical_analysis.md` | 199 | full, 1–199 |

**Total lines read: 474.**

### 1.1 What each file is

- **`v21_technical_analysis.md`** — an `ffprobe`-based measurement report on **two of the
  project's own rendered outputs**, `reel_30s_4k_adaptive_stab.mp4` and
  `reel_30s_4k_full_stab.mp4`. Line 9 states: *"Analysis performed via ffprobe on 2026-02-20."*
  That single line is the **only tool attribution in either file**, and it is the strongest
  provenance statement in this slice. §1–§3 and §6 are genuine self-measurement. §5 (platform
  spec matrix) and §7 (recommendations) are **not** measurement — they are asserted external
  facts with no source at all.
- **`v21_viral_benchmark_review.md`** — a consolidation/roadmap. Line 4 declares its
  **Inputs**: *"Visual Analysis, Viral Research, Technical Quality Analysis, Opus Codebase
  Review."* These are **four sibling files inside the same archived corpus**, verified present
  by `ls`: `v21_visual_analysis.md`, `v21_viral_research.md`, `v21_technical_analysis.md`,
  `opus_codebase_review.md`. They are therefore **internal LLM-generated documents, not
  external sources**. A citation of the form *"Viral research: …"* in this file resolves to
  another unsourced document in the same corpus — it is **not** an external citation and is
  recorded as `source_kind = internal_sibling_doc`, which for external-provenance purposes is
  **NONE**.

### 1.2 Source-kind legend

| Kind | Meaning |
|---|---|
| `self_measurement` | Document measured its own rendered output (ffprobe/frame stats). Highest-trust tier in this slice. |
| `self_derived` | Arithmetic derived from a self_measurement in the same file. |
| `self_code` | A value read out of the archived project's own source (e.g. a default in `video_processor.py`). |
| `internal_sibling_doc` | Credited to "Visual analysis" / "Viral research" / "Technical analysis" — another unsourced file in the same corpus. **Not an external citation.** |
| `NONE` | Stated bare. No source of any kind, internal or external. |

---

## 2. Numeric editorial claims — FULL TABLE

Abbreviations: `TA` = `v21_technical_analysis.md`, `VB` = `v21_viral_benchmark_review.md`.
Excluded per scope: the old project's own source line numbers, function/class names, Impact
(x/10) and Complexity (S/M/L) priority ratings, phase/week numbering, test counts (`951 tests,
76% coverage`, VB:275).

### 2.A Self-measurement of the project's own render — `v21_technical_analysis.md`

These are the **only claims in this slice with a stated measurement method** (ffprobe, TA:9).

| # | Subject | Value | Unit | Cite | Source credited | Kind |
|---|---|---|---|---|---|---|
| 1 | resolution | 2160x3840 (portrait 4K), both renders | px | TA:21 | ffprobe (TA:9) | self_measurement |
| 2 | framerate | 30 (constant) | fps | TA:22 | ffprobe (TA:9) | self_measurement |
| 3 | resolution/profile | H.264 High / Level 5.1 | — | TA:19 | ffprobe (TA:9) | self_measurement |
| 4 | other (bit depth) | 8 | bits | TA:24 | ffprobe (TA:9) | self_measurement |
| 5 | colour_grade (metadata) | colour space NOT tagged (BT.601 assumed) | — | TA:25 | ffprobe (TA:9) | self_measurement |
| 6 | other (B-frames) | 0 | frames | TA:27 | ffprobe (TA:9) | self_measurement |
| 7 | other (ref frames) | 1 | frames | TA:28 | ffprobe (TA:9) | self_measurement |
| 8 | total_duration | 30.567 | s | TA:29 | ffprobe (TA:9) | self_measurement |
| 9 | other (frame count) | 917 | frames | TA:30 | ffprobe (TA:9) | self_measurement |
| 10 | other (file size) | 294 MB — 307,857,135 B (adaptive) / 308,238,382 B (full) | bytes | TA:31 | ffprobe (TA:9) | self_measurement |
| 11 | other (audio streams) | 0 / NONE, both renders | streams | TA:32, TA:108 | ffprobe (TA:9) | self_measurement |
| 12 | bitrate | stream 80,571 / 80,671 | kbps | TA:42 | ffprobe (TA:9) | self_measurement |
| 13 | bitrate | container 80,573 / 80,673 | kbps | TA:43 | ffprobe (TA:9) | self_measurement |
| 14 | bitrate | calculated avg from frame sizes 77,583 / 77,679 | kbps | TA:44 | frame-size sum | self_derived |
| 15 | other (avg frame size) | 327.8 / 328.3 | KB | TA:50 | frame stats | self_measurement |
| 16 | other (max frame size) | 1,118.5 / 1,014.8 | KB | TA:51 | frame stats | self_measurement |
| 17 | other (max/avg ratio) | 3.41x / 3.09x | ratio | TA:52 | derived | self_derived |
| 18 | bitrate | adaptive min 39,731 (sec 27), max 97,985 (sec 23), avg 77,583 | kbps | TA:57 | per-second analysis | self_measurement |
| 19 | bitrate | adaptive range ratio 2.47x | ratio | TA:58 | derived | self_derived |
| 20 | bitrate | adaptive spike 92–98 at sec 21–25 | Mbps | TA:59 | per-second analysis | self_measurement |
| 21 | bitrate | adaptive drop 40 at sec 27 | Mbps | TA:60 | per-second analysis | self_measurement |
| 22 | bitrate | full min 26,535 (sec 27), max 99,094 (sec 23), avg 77,679 | kbps | TA:63 | per-second analysis | self_measurement |
| 23 | bitrate | full range ratio 3.73x | ratio | TA:64 | derived | self_derived |
| 24 | bitrate | full spike 94–99 at sec 21–25 | Mbps | TA:65 | per-second analysis | self_measurement |
| 25 | bitrate | full trough 27 at sec 27 | Mbps | TA:66 | per-second analysis | self_measurement |
| 26 | bitrate | "approximately 80 Mbps" both | Mbps | TA:70 | derived | self_derived |
| 27 | other (file size) | ~294 MB per 30 s | MB/30s | TA:74 | derived | self_derived |
| 28 | other (keyframes) | 76 total, both | keyframes | TA:82 | ffprobe (TA:9) | self_measurement |
| 29 | cut_rate (GOP) | 12-frame GOP, consistent | frames | TA:83 | ffprobe (TA:9) | self_measurement |
| 30 | cut_rate (GOP) | 0.4 GOP / keyframe interval | s | TA:84 | derived (12/30) | self_derived |
| 31 | bitrate | variance 2.5–3.7x; sec-27 dip to 27–40 Mbps | ratio/Mbps | TA:114 | derived from TA:57/63 | self_derived |
| 32 | letterbox_aspect | 2160:3840 = 9:16, both | ratio | TA:141 | derived | self_derived |
| 33 | other (file size delta) | adaptive 381 KB smaller than full | KB | TA:156 | derived | self_derived |

**Arithmetic re-check of the self-measurements (performed this session, by hand):** they are
internally coherent. 307,857,135 B ÷ 30.567 s ≈ 80,574 kbps ✔ (matches TA:43). 307,857,135 ÷
917 = 335,722 B = 327.9 KiB ✔ (matches TA:50). 1,118.5 ÷ 327.8 = 3.412 ✔. 97,985 ÷ 39,731 =
2.466 ✔. 99,094 ÷ 26,535 = 3.734 ✔. 917 ÷ 12 = 76.4 → 76 keyframes ✔. 12 ÷ 30 = 0.4 s ✔.
294 MB × 2 = 588 MB ✔. **Verdict: the §1–§3/§6 measurement layer of `TA` is self-consistent
and is the one part of this slice that behaves like real measurement.** Note the unit
convention is MiB (307,857,135 B = 293.6 MiB = 307.9 MB decimal) and is never declared.

### 2.B External platform / delivery specs — asserted, no source

| # | Subject | Value | Unit | Cite | Source credited | Kind |
|---|---|---|---|---|---|---|
| 34 | bitrate | Instagram caps re-encoding at ~3.5 Mbps for Reels | Mbps | TA:71 | — | NONE |
| 35 | bitrate | YouTube recommended 53–68 for 4K HDR uploads | Mbps | TA:73 | — | NONE |
| 36 | cut_rate (keyframe) | "1–2 second recommendation for social platforms" | s | TA:90 | — | NONE |
| 37 | bitrate | current encode "10–20x higher than platform delivery bitrate" | x | TA:110 | — | NONE |
| 38 | bitrate | "15–25 Mbps for 4K or 8–12 Mbps for 1080p would be optimal" | Mbps | TA:110 | — | NONE |
| 39 | other (compression) | B-frames: +10–20% efficiency with 2–3 B-frames | % | TA:111 | — | NONE |
| 40 | other (upload limit) | Instagram 650 MB/60 s; TikTok 287 MB | MB | TA:112 | — | NONE |
| 41 | other (file size) | 60 s render would be ~588 MB | MB | TA:112 | derived from TA:31 | self_derived |
| 42 | resolution | Instagram/TikTok deliver at 1080x1920 max | px | TA:113 | — | NONE |
| 43 | resolution/bitrate | Instagram Reels: 1080x1920, 30 fps, H.264, 3,500+ kbps, AAC 128 kbps, 650 MB, 90 s | mixed | TA:124 | — | NONE |
| 44 | resolution/bitrate | TikTok: 1080x1920, 30 fps, H.264/HEVC, 2,500+ kbps, AAC 128 kbps, 287 MB*, 10 min | mixed | TA:125 | "*limits vary by account/region" (TA:129) | NONE |
| 45 | resolution/bitrate | YouTube Shorts: 1080x1920, 30–60 fps, H.264, 8,000+ kbps, AAC 128 kbps, 256 MB, 60 s | mixed | TA:126 | — | NONE |
| 46 | resolution/bitrate | YouTube (4K): 2160x3840, 30 fps, H.264/VP9, 35,000–68,000 kbps, AAC 384 kbps, 128 GB, 12 hr | mixed | TA:127 | — | NONE |
| 47 | bitrate | target 15–20 Mbps for 4K master; 1080x1920 at 8–12 Mbps for social | Mbps | TA:170 | — | NONE |
| 48 | bitrate | `--export instagram`: 1080x1920, 8 Mbps | Mbps | TA:176 | — | NONE |
| 49 | bitrate | `--export youtube`: 2160x3840, 40 Mbps | Mbps | TA:176 | — | NONE |
| 50 | other (compression) | `-bf 3` for **~15%** bitrate savings | % | TA:180 | — | NONE (range→point, see §4.C) |
| 51 | other (compression) | HEVC: 30–50% better compression at equivalent quality | % | TA:185 | — | NONE |
| 52 | framerate | 24 fps cinematic option; 60 fps for action/FPV | fps | TA:186 | — | NONE |
| 53 | bitrate | reducing to 15–20 Mbps would speed encoding "significantly" | Mbps | TA:187 | — | NONE |
| 54 | bitrate | "80 Mbps / 294 MB for a 30 s clip is 10x more than needed" | x | TA:196 | — | NONE |

### 2.C Output-quality scores — `v21_viral_benchmark_review.md`

| # | Subject | Value | Unit | Cite | Source credited | Kind |
|---|---|---|---|---|---|---|
| 55 | other (overall quality) | both test renders scored **5.0/10** overall | /10 | VB:11 | "The visual analysis" | internal_sibling_doc |
| 56 | hook_timing (quality) | opening hook 2/10 | /10 | VB:11, VB:196 | visual analysis | internal_sibling_doc |
| 57 | other (scene variety) | 4/10 | /10 | VB:11, VB:197 | visual analysis | internal_sibling_doc |
| 58 | cut_rate (pacing/energy) | 3/10 | /10 | VB:11, VB:198 | visual analysis | internal_sibling_doc |
| 59 | other (composition) | 6/10 | /10 | VB:199 | visual analysis | internal_sibling_doc |
| 60 | colour_grade | 5/10 | /10 | VB:200, VB:65 | visual analysis | internal_sibling_doc |
| 61 | other (exposure/DR) | 5/10 | /10 | VB:201 | visual analysis | internal_sibling_doc |
| 62 | resolution (sharpness) | 8/10 | /10 | VB:202, VB:266 | visual analysis | internal_sibling_doc |
| 63 | other (stabilization) | 8/10 | /10 | VB:203, VB:267 | visual analysis | internal_sibling_doc |
| 64 | transition_duration (transitions) | 4/10 | /10 | VB:204, VB:118 | visual analysis | internal_sibling_doc |
| 65 | other (audio/platform fit) | 1/10 | /10 | VB:205 | visual analysis | internal_sibling_doc |
| 66 | other (subject interest) | 5/10 | /10 | VB:206 | visual analysis | internal_sibling_doc |
| 67 | other (category weights) | 15/12/12/10/10/8/5/5/8/10/5 % | % | VB:196–206 | "visual analysis framework, calibrated against viral research benchmarks" (VB:192) | NONE (calibration never shown) |
| 68 | other (viral readiness) | Current **38/100** | /100 | VB:212 | — | NONE (and see §4.A) |
| 69 | other (viral readiness) | After Critical Fixes **55/100** | /100 | VB:213 | — | NONE |
| 70 | other (viral readiness) | After Quick Wins **70/100** | /100 | VB:214 | — | NONE |
| 71 | other (viral readiness) | After Major Upgrades **84/100** | /100 | VB:215 | — | NONE |
| 72 | other (projected per-category) | full 4-stage projection grid (44 forward-looking cell values) | /10 | VB:196–206 | — | NONE (pure forecast) |

### 2.D Claims about the project's own render, restated in `VB`

| # | Subject | Value | Unit | Cite | Source credited | Kind |
|---|---|---|---|---|---|---|
| 73 | shot_length | featureless ocean occupies "the first 7 seconds" | s | VB:11 | — | NONE (restating visual analysis) |
| 74 | shot_length | ocean clip ≈ 0–7 s = **23% of the 30-second reel** | s / % | VB:35–36 | — | NONE |
| 75 | shot_length | "5 seconds of nearly identical ocean surface is far too long" | s | VB:38 | "Visual analysis" | internal_sibling_doc |
| 76 | shot_length | 3 distinct scenes in 30 s; "3 clips averaging 10 s each" | count / s | VB:36, VB:40, VB:70, VB:104 | visual analysis | internal_sibling_doc |
| 77 | hook_timing | strongest content ("mountain dusk panorama") at 15 s; "marine life overhead" at 22 s | s | VB:29 | visual analysis | internal_sibling_doc |
| 78 | colour_grade | sunset sky at 15 s under-saturated | s | VB:61, VB:63 | "Visual analysis" | internal_sibling_doc |
| 79 | other (exposure) | mountain shots at 15–20 s have underexposed foreground | s | VB:121, VB:178 | "Visual analysis" | internal_sibling_doc |
| 80 | bitrate | output ~80 Mbps, 294 MB for 30 s; Instagram re-encodes ~3.5 Mbps; 60 s ≈ 588 MB vs TikTok 287 MB limit | Mbps/MB | VB:43 | "Technical analysis" | internal_sibling_doc → traces to TA (self_measurement for the 80/294; NONE for 3.5/287) |
| 81 | bitrate | `VideoProcessor.__init__` defaults `video_bitrate` to `"15M"` | Mbps | VB:44 | archived source code | self_code |
| 82 | bitrate | export presets: Instagram **8M**, TikTok **10M**, YouTube Shorts **12M** | Mbps | VB:47 | archived `export_presets.py` | self_code |
| 83 | framerate | "Constant 30 fps" listed as already-correct | fps | VB:269 | — | self_measurement (via TA:22) |
| 84 | letterbox_aspect | 9:16 portrait, correct for all short-form | ratio | VB:270 | — | self_measurement (via TA:141) |

### 2.E Prescriptive editorial targets in `VB` — the high-consequence rows

These are the numbers most likely to be inherited as code defaults. **Every one is NONE or
internal_sibling_doc.**

| # | Subject | Value | Unit | Cite | Source credited | Kind |
|---|---|---|---|---|---|---|
| 85 | retention | "the critical first 1–3 seconds where **50% of viewers** decide to stay or scroll" | s / % | VB:29 | — | NONE (hedge already stripped, see §4.D) |
| 86 | retention | "The average viewer decides to swipe within **1–2 seconds**. **Up to 50%** drop off in the first **3 seconds**." | s / % | VB:31 | "Viral research" | internal_sibling_doc |
| 87 | shot_length | "Viral drone reels use **1–3 second clips** with **8–12 distinct scenes** in 30 seconds" | s / count | VB:36 | — | NONE |
| 88 | shot_length | "TikTok: Faster cuts, **~1–3 seconds per clip**" | s | VB:38, VB:72 | "Viral research" | internal_sibling_doc |
| 89 | shot_length | interest-adaptive: high-hook **3–4 s**, medium **2–3 s**, low **1.5–2 s max** | s | VB:39, VB:100 | — | NONE |
| 90 | shot_length | 30 s reel → target **8–10 clips at 2.5–3.5 s each**; 15 s reel → **5–7 clips at 2–2.5 s each** | count / s | VB:71 | — | NONE |
| 91 | shot_length | total clip count target **8–12** for a 30 s reel; hook position **2–3 s max** | count / s | VB:100 | — | NONE |
| 92 | shot_length | "Viral benchmark shows **8–12 clips at 1–3 s each**" | count / s | VB:104 | "Viral benchmark" (unnamed) | NONE |
| 93 | other (scene count) | minimum **6 scenes for 30 s**, **10 for 60 s** | count | VB:68 | — | NONE |
| 94 | other (scene count) | "**8–12 distinct locations/angles** in 30 seconds" | count | VB:70 | "Visual analysis" | internal_sibling_doc |
| 95 | colour_grade | "default or viral preset should use **0.6–0.7** intensity, not lower" (`--color-intensity` scale 0.0–1.0) | scalar | VB:62 | — | NONE |
| 96 | colour_grade | "Adjust default `--color-intensity` to **0.6** when a platform is selected" | scalar | VB:64 | — | NONE (range→point, see §4.C) |
| 97 | colour_grade | add shadow-lift of **~10–15 units** in the LAB path | LAB units | VB:64 | — | NONE |
| 98 | detection threshold | apply shadow lift "for frames with **mean luminance below 80**" | luma (0–255) | VB:64 | — | NONE — bare invented constant |
| 99 | detection threshold | lift shadows when "the **bottom 30%** of the histogram is underrepresented" | % | VB:122 | — | NONE — bare invented constant |
| 100 | saturation | "Instagram/TikTok: Slightly more saturated than cinema" (no number) | — | VB:65 | "Viral research" | internal_sibling_doc |
| 101 | cut_rate / hook_timing | narrative arc by percentage: Hook **0–15%**, Build **15–50%**, Climax **50–85%**, Resolution **85–100%** | % of runtime | VB:76 | — | NONE |
| 102 | cut_rate / hook_timing | arc by seconds: Hook (**0–5 s**): **1–2 cuts**; Build (**5–15 s**): cuts every **1.5–3 s**; Climax (**15–25 s**): fastest; Resolution (**25–30 s**) | s | VB:79 | "Viral research" | internal_sibling_doc |
| 103 | shot_length | closing: "Resolution (**25–30 s**): Slower cuts, **2–4 s** each, land on wide/epic shot" | s | VB:185 | "Viral research" | internal_sibling_doc |
| 104 | speed_ramp | "**1.5x** acceleration into drop, **0.3–0.5x** slow-mo on drop" | x | VB:107 | — | NONE |
| 105 | speed_ramp | speed ramping is "one of the TOP trending effects for drone content in **2025**" / "#1 trending drone editing effect" | rank | VB:109, VB:111 | "Viral research" | internal_sibling_doc |
| 106 | total_duration | per-platform optima: TikTok **15–25 s**; Instagram **60–90 s**; YouTube Shorts **30–60 s** | s | VB:132 | "Viral research shows" | internal_sibling_doc |
| 107 | other (compression) | B-frames would reduce file size **10–20%** | % | VB:139, VB:143 | "Technical analysis" | internal_sibling_doc → TA:91 (itself NONE) |
| 108 | framerate | `--fps 60` option; "currently fixed at 30 fps" | fps | VB:146 | — | self_code |
| 109 | framerate | "60 fps adds perceived quality for drone footage" | fps | VB:148, VB:150 | "YouTube Shorts research" / "Technical analysis and viral research both" | **MISATTRIBUTED — see §4.E** |
| 110 | other (compression) | HEVC **30–50%** better compression | % | VB:160, VB:164 | "Technical analysis" | internal_sibling_doc → TA:185 (itself NONE) |
| 111 | other (audio mix) | ambient environmental audio mixed at **-20 dB** under music | dB | VB:168 | — | NONE |
| 112 | bitrate | "excessive bitrate (**80 Mbps vs 8–15 Mbps recommended**)" | Mbps | VB:11 | "The technical analysis found" | **MISATTRIBUTED — see §4.E** |

**Totals:** 112 catalogued numeric editorial claims.
**With a resolvable named source (URL or named publication) for that specific number: 0.**
The only resolvable *method* attribution is `ffprobe` (TA:9), which covers rows 1–33 (33 rows)
plus the derived subset. `ffprobe` is a tool, not a named publication, so the strict
"named source" count remains **0**; the honest tool-grounded count is 33.

---

## 3. Reference videos and exemplar creators

**Count: 0. Neither category appears anywhere in either file.**

Verified by grep across both files (`grep -nE 'https?://|www\.|@[A-Za-z0-9_.]+|\.com|\.org|\.net'`)
— **exit status 1, zero matches**. A second grep for
`creator|channel|influenc|account|viral video|example video|reel by|film|award|festival|winner`
returned only four false positives, all unrelated:

| Match | Line | Why it is not a reference |
|---|---|---|
| "TikTok: 287 MB for some **account**s" | TA:112 | upload-limit prose |
| "*TikTok limits vary by **account**/region" | TA:129 | footnote |
| "\| Metric \| Adaptive \| Full \| **Winner** \|" | TA:154 | table header comparing the project's own two renders |
| "**film**" — no match; `duration_adjuster` hit was on "en**film**"-free substring | VB:37 | substring artefact of the grep, not a film reference |

- **Zero URLs.** These two files contain no bulk URL list at all — not even the end-of-file
  topical dump the sibling agents found elsewhere in the corpus.
- **Zero Instagram/TikTok handles.** None of `@thedronecreative`, `@beverlyhillsaerials`,
  `@basso2012`, `@simeonpratt` appear here.
- **Zero named third-party videos.** The single corpus-wide reference video the sibling agents
  located (`research_transitions.md:862`) does **not** appear in this slice.
- The only "exemplars" invoked are the abstract, unnamed collectives *"Viral drone reels"*
  (VB:36, VB:70) and *"Viral benchmark"* (VB:104). Under the strict test these are **not**
  reference videos or exemplar creators — no video, channel, or person is identifiable.

**Consistency with sibling agents:** confirmed and consistent. My slice contributes 0 URLs to
the corpus-wide 233 occurrences / 174 distinct, and 0 to the single-reference-video count.

---

## 4. Internal contradictions — hunted for actively

### 4.A The headline score does not reconcile three ways *(highest severity)*

`VB:11` says the visual analysis scored both renders at **5.0/10 overall**.
`VB:212` says Current viral readiness is **38/100**.
Recomputing `VB:196–206` by hand with the stated weights (which do sum to exactly 100%):

```
0.15·2 + 0.12·4 + 0.12·3 + 0.10·6 + 0.10·5 + 0.08·5
      + 0.05·8 + 0.05·8 + 0.08·4 + 0.10·1 + 0.05·5  =  4.11/10  =  41.1/100
```

So three mutually incompatible "current quality" figures coexist: **5.0/10 (VB:11)**,
**38/100 (VB:212)**, and **41.1/100 (computed from VB:196–206)**.

Critically, the *other three* stages reconcile almost exactly under the same method —
After Quick Wins computes to **70.1** vs stated 70 ✔; After Major Upgrades computes to
**83.4** vs stated 84 ✔; After Critical Fixes computes to **56.3** vs stated 55 (≈1.3 off).
Only the **Current** row is off by 3.1 points. The projections are arithmetically sound; the
baseline they are measured against is not. Any "we improved the score by N points" claim
inherits this error.

### 4.B "10 categories" that are actually 11

`VB:192`: *"Scores are weighted across **10 categories** from the visual analysis framework."*
The table immediately below (`VB:196–206`) has **11 rows**. Subject Interest (VB:206, weight
5%) appears to be an eleventh category bolted onto a framework described as ten. This is
consistent with 4.A: an 11th category added after the 38/100 figure was computed would explain
the 38 vs 41.1 gap almost exactly (41.1 − 0.05·5 = 38.6 ≈ 38).

### 4.C Range → point-value collapse — the documented failure pattern, twice, in this slice

The sibling agents flagged this pattern (LUT "50-70%" → "60%" → `intensity=0.6`). **It occurs
in my files too, and one instance is the very same `--color-intensity` parameter:**

| Instance | Range stated | Point value adopted | Reason given |
|---|---|---|---|
| Colour grade intensity | "should use **0.6–0.7** intensity, not lower" (VB:62) | "Adjust default `--color-intensity` to **0.6**" (VB:64) | **none** — collapses to the range's *floor*, three lines after being told "not lower" |
| B-frame compression saving | "**10–20%**" (TA:91, TA:111; echoed VB:139, VB:143) | "`-bf 3` for **~15%** bitrate savings" (TA:180) | **none** — midpoint taken silently |

The colour-intensity case is the more dangerous: the range is stated as a *lower bound* ("not
lower") and the adopted default sits exactly *on* that lower bound, so the recommendation's own
emphasis is inverted by the value that would ship.

### 4.D Hedge stripping — a qualified claim restated as unqualified

| Original | Restatement | What was lost |
|---|---|---|
| VB:31 "**Up to** 50% drop off in the first 3 seconds" | VB:29 "the critical first **1–3 seconds** where **50% of viewers** decide" | "up to" dropped; a ceiling became a point estimate; "3 s" became "1–3 s" |
| TA:199 "VideoToolbox has **limited rate control** compared to libx264" | VB:44 "the h264_videotoolbox encoder that **ignores bitrate constraints**" | "limited" → "ignores" |
| TA:111 "The h264_videotoolbox encoder **may not** support B-frames" | VB:139 "Current h264_videotoolbox encoder **produces I/P-only streams**" (asserted) | uncertainty dropped (though TA:27 does measure 0 B-frames, so the *fact* holds; the *causal* claim does not) |
| TA:182 "-movflags +faststart … **(may already be set)**" | VB:93 quotes the sentence and drops the parenthetical | QW-6 is scoped as a fix for something the source says might not be broken |

### 4.E Misattribution — numbers credited to a document that does not contain them

Both files are in my slice, so I could check the quotes directly. Most quotations of the
technical analysis in `VB` are **verbatim and accurate** (VB:45↔TA:110, VB:58↔TA:109,
VB:86↔TA:110, VB:143↔TA:91, VB:157↔TA:181, VB:164↔TA:185). Two are not:

1. **VB:11 — "80 Mbps vs 8–15 Mbps recommended", credited to "The technical analysis found".**
   The string "8–15 Mbps" **appears nowhere** in `v21_technical_analysis.md`. TA offers
   *15–25* (4K, TA:110), *8–12* (1080p, TA:110), *15–20* (4K master, TA:170), and *40* (YouTube
   export, TA:176). "8–15" is a **new range synthesised in the executive summary** and
   back-attributed to a document that never states it. This is the single most quotable line in
   the file and it is the one with fabricated provenance.
2. **VB:148/150 — "60fps adds perceived quality for drone footage", credited to "YouTube
   Shorts research" and then to "Technical analysis and viral research both".** `TA` mentions
   60 fps exactly twice: TA:126 (YouTube Shorts accepts 30–60 fps — a spec, not a quality
   claim) and TA:186 ("60fps for action/FPV footage" — an option, not a quality claim). **`TA`
   never characterises 60 fps as a quality signal.** The attribution is an upgrade.

### 4.F Bitrate recommendation is irreconcilable across six statements

| Recommendation | Cite |
|---|---|
| 8–15 Mbps | VB:11 |
| Instagram 8M / TikTok 10M / Shorts 12M | VB:47 |
| 15–25 Mbps (4K) or 8–12 Mbps (1080p) | TA:110, VB:86 |
| 15–20 Mbps (4K master) or 8–12 Mbps (1080p) | TA:170, TA:187 |
| `--export youtube`: **40 Mbps** at 2160x3840 | TA:176 |
| YouTube (4K) platform spec: 35,000–68,000 kbps | TA:127 |

TA:170 ("target 15–20 Mbps for 4K master") and TA:176 (`--export youtube` at 40 Mbps, also 4K)
are **six lines apart and differ by 2x** for the same resolution. Neither cites anything.

### 4.G YouTube 4K recommended bitrate stated twice, differently, in one file

TA:73: *"Well above **YouTube's recommended 53–68 Mbps** for 4K HDR uploads."*
TA:127: YouTube (4K) bitrate = **35,000–68,000** kbps.
Same document, same platform; lower bound differs by 18 Mbps (53 vs 35). Neither sourced.

### 4.H The excess factor is stated as both 10–20x and 10x

TA:110: *"10–20x higher than platform delivery bitrate."* TA:196: *"10x more than needed."*
Against TA:71's own ~3.5 Mbps Instagram figure the true ratio is ~23x; against TA:110's own
15–25 Mbps optimum it is ~3.2–5.3x. **Neither stated factor is consistent with either of the
document's own reference points.**

### 4.I YouTube Shorts size limit contradicts its own footnote

TA:126 gives YouTube Shorts a **256 MB** max size. Footnote TA:130 states Shorts are *"uploaded
as regular video, flagged as Short by metadata"* — under which the YouTube (4K) row's **128 GB**
limit (TA:127) would apply. The two cannot both be right. Downstream, TA:145 tests file size
only against TikTok's 287 MB; the 294 MB render also exceeds the 256 MB Shorts figure, and that
failure is never surfaced.

### 4.J Ocean-clip duration: 7 s vs 5 s in adjacent lines

VB:11 and VB:35–36 assert the ocean clip runs **7+ seconds** (0–7 s, "23% of the reel").
VB:38, quoting the visual analysis directly, says *"**5 seconds** of nearly identical ocean
surface is far too long."* The 7 s figure — which drives the whole CF-3 headline, the 23%
figure, and the interest-adaptive-duration redesign (MU-1) — is **40% larger than the quoted
evidence for it**, with no reconciliation.

### 4.K Clip-count and clip-length targets are mutually inconsistent — four incompatible sets

| Target | Cite |
|---|---|
| 1–3 s clips, 8–12 scenes / 30 s | VB:36 |
| high-hook **3–4 s**, medium 2–3 s, low 1.5–2 s | VB:39, VB:100 |
| **minimum 6** scenes for 30 s, 10 for 60 s | VB:68 |
| 8–10 clips at **2.5–3.5 s** each (30 s) | VB:71 |
| **8–12** clips at **1–3 s** each | VB:92 (MU-1), VB:104 |

Three distinct failures: (i) VB:39/VB:71/VB:100 permit clips of **3–4 s** and **2.5–3.5 s**
while VB:36/VB:104 assert the viral benchmark is **1–3 s** — the prescription exceeds its own
benchmark's ceiling; (ii) QW-3's proposed floor of **6 scenes/30 s** (VB:68) is **below** the
8–12 benchmark quoted two lines later in the same section (VB:70) and below its own stated
target of 8–10 (VB:71) — an internal contradiction inside a five-line block; (iii) 8–10 clips ×
2.5–3.5 s = 20–35 s, which only sometimes fills the 30 s target.

### 4.L Narrative-arc percentages do not map onto the arc seconds

VB:76 defines Hook 0–15%, Build 15–50%, Climax 50–85%, Resolution 85–100%. On the actual
30.567 s render that is 0–4.6 s / 4.6–15.3 s / 15.3–26.0 s / 26.0–30.6 s. VB:79, the "Viral
research" quote the section claims to implement, says Hook **0–5 s**, Build **5–15 s**, Climax
**15–25 s**, Resolution **25–30 s**. The Climax and Resolution boundaries disagree by ~1 s.
Separately, VB:79's "Hook (0–5 s): 1–2 cuts" implies opening clips of ~2.5–5 s, contradicting
VB:100's "hook position gets **2–3 s max** (fast, punchy opener)".

### 4.M 4K resolution is simultaneously a strength and a defect

VB:266 lists *"4K resolution with clean detail (8/10 sharpness)"* under **"What's Already
Working Well … should not be regressed."** TA:113 lists *"Resolution (2160x3840)"* as an
**Issue Identified** ("Above most platform native resolution … doubles encode time and
storage"), and TA:143 marks it **WARN (oversized)**. TA:170 and VB:82/VB:129 then propose
rendering at 1080x1920 — i.e. regressing the exact item VB:266 says must not be regressed.

### 4.N "Exceeds" vs "approaching" the same limit

VB:43: a 60 s video (~588 MB) *"**would exceed** TikTok's 287 MB upload limit."*
TA:112: *"a 60 s video would be ~588 MB, **approaching limits**."*
588 MB vs 287 MB is 2.05x — "approaching" understates it, "exceed" is right, and the two
documents disagree while one cites the other.

### 4.O Nominal 30 s vs measured 30.567 s

Every percentage in `VB` (23% for 7 s, the 0–15%/15–50%/50–85%/85–100% arc) is computed against
a nominal **30 s**, while `TA:29` measures **30.567 s**. Small (1.9%), but it means no
percentage in `VB` is computed against the file that was actually measured.

### 4.P Stream bitrate vs frame-derived bitrate never reconciled

TA:42 (80,571 kbps) vs TA:44 (77,583 kbps) — a 3.9% gap between two measurements of the same
property in the same table. The document lists both without comment. (Container overhead is the
likely explanation, but the document does not say so, and the *narrative* thereafter switches
between "80 Mbps" and "77,583 avg" depending on which suits the sentence.)

---

## 5. Provenance verdict

**The sibling agents' corpus-wide pattern — bare claims in the body, a bulk topical URL list at
the end, nothing linking any number to any source — holds for my slice with one structural
exception: there is no bulk URL list at all.** These two files contain **zero URLs** (grep exit
1). So the pattern degrades to its worst form: bare claims in the body and **nothing at the end
either**. Every external-fact claim (platform bitrates, upload ceilings, retention statistics,
trend rankings) is asserted with no source of any kind.

The genuine exception, and the reason this unit matters, is **`v21_technical_analysis.md` §1–§3
and §6**: 33 claims measured off the project's own two renders with a stated tool
(`ffprobe`, TA:9) and a stated date. I re-derived nine of these by hand and they check out
(bytes÷duration→bitrate, bytes÷frames→avg frame size, max÷avg, max÷min, frames÷GOP→keyframes,
GOP÷fps→0.4 s, 294×2→588). **This is real self-measurement and should be treated as a different
evidential tier from everything else in the slice.**

The failure is at the seam. `v21_viral_benchmark_review.md` mixes that measured layer with an
unsourced layer and presents the result in one uniform voice — the executive summary (VB:11)
puts the measured "80 Mbps" and the fabricated "8–15 Mbps recommended" in the same sentence
under the same attribution ("The technical analysis found"). A reader cannot tell them apart
without opening both files. The four "Inputs" (VB:4) look like citations but resolve to sibling
LLM documents in the same corpus; "Viral research: …" is quotation, not attribution.

**Practical consequence for `drone_video_ai`:** rows 85–112 are the numbers most likely to be
lifted as pipeline defaults (`--color-intensity 0.6`, `mean luminance < 80`, `bottom 30% of
histogram`, `1.5x`/`0.3–0.5x` speed ramp, `8–12` clips, `1–3 s` shot length, `-20 dB` ambient
bed). **Not one of them has a source, and several are mutually contradictory (§4.K) or already
show the range→point collapse (§4.C).** Under this project's Constitution these are exactly
"invented constants" and none may be inherited without independent measurement.

## 6. Coverage note

Both files read in full, line 1 to EOF (275 + 199 = 474 lines); no sampling, no pruning.
112 numeric editorial claims catalogued across 5 sub-tables; 16 contradictions in §4.
Scope exclusions applied as instructed: Impact (x/10) and Complexity (S/M/L) priority ratings,
week/phase numbering, archived source line numbers, and the `951 tests / 76% coverage` figure
(VB:275) were logged as out-of-scope and are not counted. Nine self-measurement arithmetic
relationships independently re-derived by hand this session. Grep-verified: zero URLs, zero
handles, zero named creators, zero identifiable third-party videos. No network access; nothing
under `_archive/` was written, moved, or deleted; no image or frame file was written anywhere.
