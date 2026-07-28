# Census — Craft / Colour / Transitions Research Slice

Agent: census-craft-research
Date: 2026-07-28
Status: COMPLETE — all 5 assigned files read end to end

**Framing reminder:** every number below is an extracted assertion from an LLM-generated
document in an archived, unrelated project (`_p-ai-drone-video`, Dec 2025 – Feb 2026).
Nothing here is verified. Nothing here should be copied into `data/reference_pack/` or
`editorial_style.json` as fact. This is a provenance census, not a findings document.

## Assigned files (all read in full)
| # | Path | Lines | Has a sources section? |
|---|---|---|---|
| F1 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/drone_visual_design_principles.md` | 1322 | **NO — zero URLs, zero citations in the entire file** (verified: `grep -n "http"` returns nothing) |
| F2 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/research_color_science.md` | 700 | Yes — §6 RESEARCH SOURCES, 15 URLs, lines 685–699. **Bulk list only; not one claim is individually cited.** |
| F3 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/research_transitions.md` | 867 | Yes — References, 12 URLs, lines 855–866. Bulk list; one item (TikTok) is cross-referenced inline at L72/L627. |
| F4 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/research_pro_software.md` | 750 | Yes — Sources Consulted, 20 URLs, lines 730–749. Bulk list; no per-claim citation. |
| F5 | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/professional_drone_editing_software_analysis.json` | 1008 | Partial — each of 5 `professional_software` entries carries a `citation` field with a URL. Everything under `technical_insights`, `community_insights`, `implementation_recommendations`, `instagram_reels_specifications` is uncited. |

## Headline provenance result

**F1 — the single densest source of editorial constants in this slice (clip durations,
retention targets, energy curve, platform presets, "35% of top-performing travel reels") —
contains no citation of any kind.** Not a URL, not a publication, not a dataset. Its
"Research-Based Duration Thresholds" (L197) and "Research Insight" (L591) headers are
free-floating assertions. This is the document that most directly supplies the parameter
class `editorial_style.json` marks UNSUPPORTED, and it is the least sourced document here.

F2/F3/F4 all follow the same pattern: a plausible-looking bulk URL list at the bottom, with
zero linkage between any individual number and any listed source. A reader cannot determine
which of the 15/12/20 URLs (if any) produced "contrast +20 to +30".

F5 is the only file with per-item citations, and only for the 5 vendor product descriptions.
Its *editorial* claims (LUT intensity, clip duration, bitrate) are uncited assertions in
`expert_opinions` / `workflow_best_practices` arrays.

---

## 1. Numeric editorial claims

### F1 — drone_visual_design_principles.md (attributed_source = NONE for every row)

| Line | Claim | Subject | Value | Unit |
|---|---|---|---|---|
| 92 | "hero moment" is a 2-4 second segment | shot_length | 2-4 | s |
| 94-96 | Opening hook = first 3s; climax 60-70% through; final payoff last 2s | hook_timing | 3 / 60-70 / 2 | s / % / s |
| 103 | Hero criterion: colour saturation >60% mean | saturation | >60 | % |
| 106 | Hero criterion: audio sync within 0.5s of beat/downbeat | audio_bpm | 0.5 | s |
| 156-157 | Top 15% of scenes are hero candidates (code uses `len//7` ≈ 14.3%) | other | 15 | % |
| 199-203 | **Platform table**: TikTok clip 2.5-4.5s, drop after 5s, total 15-30s; IG Reels 3-5s, after 6s, 30-60s; YT Shorts 3-6s, after 7s, 30-60s. Header L197 "Research-Based Duration Thresholds" | shot_length / total_duration | see cell | s |
| 208 | CLI default reel duration 45.0s | total_duration | 45 | s |
| 231-233 | platform_params: tiktok 2.5/3.5/4.5; instagram 3.0/4.0/5.0; youtube 3.5/4.5/6.0 (min/ideal/max) | shot_length | 2.5-6.0 | s |
| 260-276 | 45s arc: 0-3 hook, 3-12 establish (4-5s clips), 12-30 build (alternate 2.5s/4s), 30-40 climax, 40-45 resolve | cut_rate | see cell | s |
| 304-333 | Sequencer literals: hook 3.0, establish 4.5×2, build alternate 2.5/4.0, climax 5.0, resolve 5.0 | shot_length | 2.5-5.0 | s |
| 374-378 | Energy keypoints: hook 8%, establish 25%, build 70%, climax 85% of duration | other | 8/25/70/85 | % |
| 380-396 | Energy values 0.7 → 0.5 → 0.5-0.8 → 1.0 → 0.3 | other | 0.3-1.0 | ratio |
| 403 | Blend energy curve 70% / music 30% | other | 70/30 | % |
| 456-463 | Preset saturation table: drone_aerial 60%, warm_sunset 75%, cool_blue 55%, teal_orange 70%, vibrant 85%, muted 35% | saturation | 35-85 | % |
| 568-573 | Alternate ±5% brightness between adjacent clips | colour_grade | ±5 | % |
| 597 | Teal shadows + orange highlights = **35% of top-performing travel reels** | colour_grade | 35 | % |
| 602 | Desaturated greens + warm skin = **22% of adventure content** | colour_grade | 22 | % |
| 607 | Deep blues + gold = **18% of luxury travel** | colour_grade | 18 | % |
| 617-623 | WANDERLUST: shadows_teal +15, highlights_orange +10, midtone_sat 0.85, contrast 1.15, blacks_lift 0.05 | colour_grade | see cell | unitless |
| 649-651 | Text safe zones by altitude: >100m top 40%; 30-100m top 25%; <30m bottom 15% | text_overlay | 15-40 | % of frame |
| 660-664 | Stroke ≥3px @50% opacity; scrim rgba(0,0,0,0.4); font 72-96 / 48-64 / 36-48 px at 1080×1920 | text_overlay | see cell | px |
| 667-669 | Fade in 0.3s; min 1.5s on-screen per word; fade out 0.2s | text_overlay | 0.2-1.5 | s |
| 691 | Caption min duration = words × 0.5s + 1.0s | text_overlay | 0.5/1.0 | s |
| 715-725, 730 | Watermark opacities 25/30/20%; logo ≤150×150px = 7% of frame width | text_overlay | 20-30 / 7 | % |
| 845 | Visual-hit-to-beat alignment tolerance 0.15s | audio_bpm | 0.15 | s |
| 884-890 | **Genre table**: EDM 128-140 BPM → 16-24 cuts/min; Hip-Hop 80-110 → 8-12; Indie/Pop 100-120 → 12-16; Ambient 60-90 → 4-8; Rock 120-140 → 14-20 | cut_rate | 4-24 | cuts/min |
| 902-929 | Tempo→pacing: ≥128 BPM → 20 cuts/min, clips 2.0-3.5s; ≥110 → 14, 3.0-4.5s; ≥90 → 10, 3.5-5.5s; else 6, 4.0-7.0s | cut_rate | 6-20 | cuts/min |
| 939 | Documentary/ambient mode: 6-8s per clip | shot_length | 6-8 | s |
| 944 | ASMR/relaxation: 8-12s per clip | shot_length | 8-12 | s |
| 948 | Before/after: silence 2-3s then music | other | 2-3 | s |
| 967-969 | `--no-music` mode: min clip 6.0s, max 12.0s, transition 0.8s | transition_duration | 0.8 | s |
| 1005 | **Retention targets: >80% at 3s, >60% at 15s, >40% at 30s** | retention | 80/60/40 | % |
| 1010 | Engagement rate target >5% | retention | >5 | % |
| 1015 | Avg watch time target >60% of total duration | retention | >60 | % |
| 1020 | Rewatch rate target >15% | retention | >15 | % |
| 1027 | Hypothesis: auto colour selection +10-15% engagement | retention | 10-15 | % |
| 1031 | Hypothesis: energy curve +12-18% retention | retention | 12-18 | % |
| 1035 | Hypothesis: highest-score hook +20% 3s retention | retention | 20 | % |
| 1039 | Hypothesis: energy-matched transitions +8-12% watch time | retention | 8-12 | % |
| 1049-1059 | INSTAGRAM_PRESET: 9:16, 1080×1920, 30fps, 15-60s, ideal 30s, bitrate 5000k | bitrate/resolution/framerate | 5000 | kbps |
| 1064-1065 | Text avoid top 10% / bottom 20%; boost saturation +10% for feed visibility | saturation | +10 | % |
| 1071-1081 | TIKTOK_PRESET: ideal 21s ("sweet spot for algorithm"), bitrate 4500k | total_duration/bitrate | 21 / 4500 | s / kbps |
| 1085 | TikTok pacing 2-3s clips | shot_length | 2-3 | s |
| 1087 | **Text overlays expected (80% of top content)** | text_overlay | 80 | % |
| 1093-1103 | YOUTUBE_PRESET: ideal 45s, bitrate 6000k | total_duration/bitrate | 45 / 6000 | s / kbps |
| 1107 | YouTube pacing 4-6s clips | shot_length | 4-6 | s |
| 1133-1142 | Motion-safe mode: min clip 4.5s, transition 0.8s, max motion score 70 | shot_length/transition_duration | 4.5 / 0.8 | s |
| 1178-1179 | Text contrast ≥4.5:1 (AA), 7:1 (AAA) — **the only claim in F1 traceable to a named external standard (WCAG), and even that is named without a URL** | text_overlay | 4.5 / 7 | ratio |
| 1262-1265 | Cheat sheet: high motion 2.5-3.5s, medium 3.5-4.5s, low 4.5-6s | shot_length | 2.5-6 | s |
| 1291-1293 | Cheat sheet platform targets: TikTok 21s, IG 30s, YT 45s | total_duration | 21/30/45 | s |

### F2 — research_color_science.md (per-claim attribution = NONE; doc-level bulk list §6 L685-699)

| Line | Claim | Subject | Value |
|---|---|---|---|
| 15-26 | golden_hour: temp +200 to +500K, exposure +0.2-0.5 stops, highlights -40 to -60, shadows +30 to +50, contrast +15 to +25, vibrance +20 to +40, saturation +10 to +15, grain 15-25% | colour_grade | see cell |
| 55-65 | blue_hour: temp -300 to -500K, blue sat +25 to +40, exposure -0.3 to 0, LAB b -8 to -15, vignette 30-50% | colour_grade | see cell |
| 91-101 | harsh_midday: highlights -80 to -100, whites -50, shadows +60 to +80, blacks +30, vibrance +40 to +60, contrast **-10** | contrast | -10 |
| 114-124 | overcast: temp -50 to -100K, contrast +5 to +10, clarity +20 to +30, saturation -5 to -10, dehaze +10 to +20 | contrast/saturation | see cell |
| 137-148 | night_city: exposure -0.5 to -1.0, contrast +30 to +50, vignette 40-60%, halation blend 10-15% | contrast | +30 to +50 |
| 163-171 | ocean_coastal: cyan sat +20, blue sat +15, orange sat +25, highlights -30, contrast +15, dehaze +15-25 | saturation | see cell |
| 195-203 | forest_jungle: green sat -10 to -15, shadows +40, clarity +25, vibrance +15, temp +100K | saturation | -10 to -15 |
| 216-225 | urban_city: orange sat +20, blue sat +15, contrast +25 to +35, blacks -20, vignette 20-30% | contrast | +25 to +35 |
| 238-248 | desert_arid: orange sat -10 to -15, highlights -50 to -70, blue sat +20, temp +200K, contrast +20, dehaze +20 | contrast | +20 |
| 263-272 | snow_mountain: WB 5600K (+50-100K), highlights -60 to -80, blue sat -20 to -30, vibrance +20, contrast +10 to +20 | contrast | +10 to +20 |
| 285-294 | autumn_foliage: orange sat +25 to +35, red sat +20, green sat -20, temp +100-200K, contrast +20 to +25 | saturation | +25 to +35 |
| 489-494 | **teal_orange**: shadows teal HSL H185-195° S40-60%; highlights orange H25-35° S30-50%; global saturation **-10 to -15**; contrast **+20 to +30** | saturation/contrast | see cell |
| 520-526 | desaturated_moody: global saturation -30 to -40, blacks -40 to -60, contrast +30 to +40, vignette 40-60% | saturation | -30 to -40 |
| 550-558 | warm_pastel: lift +30 to +50, whites -20 to -30, contrast -20 to -30, saturation -15 to -25, temp +100-200K | contrast | -20 to -30 |
| 571-579 | dark_moody_neon: exposure -0.8 to -1.2, blacks -60 to -80, contrast +40 to +60, cyan sat +50, global sat -15, vignette 50-70% | contrast | +40 to +60 |
| 592-596 | hyper_realistic_natural: contrast +5 to +10, saturation 0 to +5, vibrance +5 to +10 | contrast | +5 to +10 |
| 617-671 | Concrete preset JSON: golden_hour contrast 20 / sat 12; blue_hour contrast 15 / sat 10; teal_orange contrast 25 / sat -10; dark_moody contrast 35 / sat -30 / vignette 0.5; warm_pastel contrast -25 / sat -20 / lift 40 | contrast/saturation | see cell |
| 353 | ARRI LogC4: middle gray = 28% | colour_grade | 28% |
| 381 | RED Log3G10: 10 stops above middle gray | colour_grade | 10 stops |
| 361-367 | LogC3 decode constants 0.385537 / 0.2471896 / 0.00937677; Rec709 encode 1.099 / 0.45 / 0.099 / 0.018 / 4.5 | colour_grade | see cell |

### F3 — research_transitions.md (per-claim attribution = NONE; bulk References L855-866)

| Line | Claim | Subject | Value | Unit |
|---|---|---|---|---|
| 34 | Whip pan if \|mean_dx\| > 8.0 px/frame and dx/dy ratio > 3.0 | other | 8.0 / 3.0 | px/frame |
| 57 | Orbital continuation cut if flow magnitudes within 30% | other | 30 | % |
| 103, 109-113 | **Whoosh cut: last 0.5s of A ramps 1.0x→2.5x; first 0.5s of B ramps 2.5x→1.0x** | speed_ramp | 1.0-2.5 | ×speed |
| 127 | Slow-mo peak freeze: 0.1x held for 0.3s | speed_ramp | 0.1 / 0.3 | × / s |
| 162-163 | Iris wipe feather 4px | transition_duration | 4 | px |
| 242 | Parallax slide: background 0.5x rate, foreground 1.0x | speed_ramp | 0.5 / 1.0 | × |
| 325 | RGB channel split lasts 3-5 frames | transition_duration | 3-5 | frames |
| 348, 357 | Glitch cut duration 0.15s; channel shift ramps 0→12→0 px | transition_duration | 0.15 | s |
| 384 | Scan line flash 3-6 frames | transition_duration | 3-6 | frames |
| 416 | Pixel sort applied over a 0.1-0.2s window | transition_duration | 0.1-0.2 | s |
| 445, 462 | Datamosh: blocks persist 5-10 frames; 30% of blocks persist | transition_duration | 5-10 / 30 | frames / % |
| 482 | Whiteout flash: 2-4 frames to pure white | transition_duration | 2-4 | frames |
| 526 | Light leak max opacity 60% | transition_duration | 60 | % |
| 543 | Anamorphic streak typically 2-4 frames | transition_duration | 2-4 | frames |
| 584 | **Hyperlapse zoom-through accelerates 2x → 8x** | speed_ramp | 2-8 | × |
| 588, 596-618 | **Same technique's implementation ramps 1.0x → 3.0x over 0.8s** | speed_ramp | 1.0-3.0 | × |
| 632, 658 | Cloud/fog pass duration 0.3-0.8s (implementation default 0.6s) | transition_duration | 0.3-0.8 | s |
| 636 | Fog opacity 0.85 | transition_duration | 0.85 | ratio |
| 696 | Radial zoom blur intensity 0.3 (recommend 0.1-0.4) | other | 0.1-0.4 | ratio |
| 790-796 | Auto-selection durations: GLITCH_RGB 0.15s, IRIS_IN 0.4s, LIGHT_LEAK 0.5s, HYPERLAPSE_ZOOM 0.6s | transition_duration | 0.15-0.6 | s |
| 849 | Transitions "typically 0.2-0.8s = 6-24 frames at 30fps" | transition_duration | 0.2-0.8 | s |
| 839-847 | Per-frame cost table (RGB glitch <1ms … pixel sort ~100ms/frame at 1080p) | other | see cell | ms/frame |

### F4 — research_pro_software.md (per-claim attribution = NONE; bulk Sources L730-749; each feature names a *source tool*, not a source *document*)

| Line | Claim | Subject | Value |
|---|---|---|---|
| 79-80 | Vignette defaults: strength 0.5, radius 0.75, softness 0.5 | colour_grade | 0.5/0.75/0.5 |
| 109 | Chromatic aberration default strength 3.0 px | colour_grade | 3.0 px |
| 138-139, 145 | Halation strength 0.3, blur radius 21px, highlight threshold r>200 | colour_grade | 0.3 / 21 |
| 169 | Lens distortion default k1 -0.3, k2 0.1 | other | -0.3 / 0.1 |
| 219 | **Reels music should fade out in the final 2-3 seconds** | other | 2-3 s |
| 227-234 | duck_duration 2.0s, target -20.0 dB, auto_duck_outro 2.5s | other | 2.0-2.5 s |
| 256-257 | Film grain strength 0.3, grain_size 2 | colour_grade | 0.3 / 2 |
| 287-288 | Atmospheric haze horizon_y 0.4, haze_strength 0.2 | colour_grade | 0.4 / 0.2 |
| 325 | Log-footage detector: contrast (std) < 40 and 80 < mean < 160 | colour_grade | <40, 80-160 |
| 333-335 | D-Log M decode constants 0.14 / 0.584 / 0.36 / 4.6 / 0.0208 / 3.5 | colour_grade | see cell |
| 349, 357 | Drone shutters 1/2000s+; blend 2-4 adjacent frames (default 3) to simulate 180° shutter | other | 2-4 frames |
| 389, 395 | Sky mask HSV (90,20,150)-(140,255,255); sky saturation boost ×1.2 | saturation | ×1.2 |
| 417, 424, 429 | **Whip pan 0.2s; spin 0.3s; warp zoom 0.25s** | transition_duration | 0.2-0.3 s |
| 481-486 | GND filter: sky_fraction 0.4, exposure -1.5 stops (= 0.354× factor) | colour_grade | -1.5 stops |
| 510-511 | Lens flare defaults: sun at (0.5, 0.2), strength 0.4 | colour_grade | 0.4 |
| 536, 543 | **Letterbox 2.35:1 or 2.39:1 anamorphic bars; implementation default 2.35** | letterbox_aspect | 2.35 / 2.39 |
| 572-578 | Denoise: bilateral d = 5 + strength×10, sigma = strength×75; NLM h = strength×10 | other | see cell |

### F5 — professional_drone_editing_software_analysis.json

| Line | Claim | Subject | Value | Attributed source |
|---|---|---|---|---|
| 22 | DJI Fly needs minimum 5 clips for optimal auto-edit | other | 5 | `citation` L12 → forum.dji.com/thread-209598 |
| 51-53 | Dronie distance 10-120m (controller) / 10-60m (wifi), default 40m | other | 10-120 m | same DJI citation L12 |
| 59-61 | Rocket heights 40/60/80/100/120 ft | other | 40-120 ft | same DJI citation L12 |
| 71 | DJI Fly "~40% faster than manual editing (reported)" | other | 40% | same DJI citation L12; the parenthetical "(reported)" is the document's own hedge |
| 105 | DJI Mimo cuts editing time "approximately 40%" | other | 40% | `citation` L84 → dji-retail.co.uk blog |
| 251 | Aspect ratios 9:16 / 1:1 / 16:9 | letterbox_aspect | — | CapCut citation L197 → filmora.wondershare.com |
| 381 | ShotCoL self-supervised "13% improvement in average precision" | other | 13% | NONE (no paper cited) |
| 393 | librosa beat detection accurate "within 50ms of actual beats for most music" | audio_bpm | 50 ms | NONE |
| 458 | **"Apply LUT at low intensity (50-70%), then fine-tune"** | colour_grade | 50-70% | NONE |
| 866 | **"Apply LUTs at 50-70% intensity, then fine-tune manually"** (restated in `expert_opinions`) | colour_grade | 50-70% | NONE — "expert_opinions" names no expert |
| 870 | **"1.5-2 second clip duration optimal for beat-synced montages"** | shot_length | 1.5-2 s | NONE |
| 751 | Reels export: 1080×1920, H.264, 30fps, 5-10 Mbps | bitrate | 5-10 Mbps | NONE |
| 834, 842 | 15-second reel = top 4-6 clips totalling ~13s | shot_length/total_duration | 15 / 13 s | NONE |
| 886-899 | Reels spec: 9:16, 1080×1920, MP4, H.264/AAC, 30fps, video 5000-10000 kbps, audio 128 kbps, 44.1/48 kHz, max 90s, optimal 15-30s | platform_spec block | see cell | NONE — presented as a spec but no Instagram/Meta doc is cited |
| 905 | **"Stay within 5-15 Mbps bitrate range"** | bitrate | 5-15 Mbps | NONE |
| 952 | PySceneDetect processes 1080p at ~60fps (perf, not editorial — logged for completeness) | other | 60 fps | NONE |
| 755, 846 | 5-min 4K in 3-5 min; 30-min video in 5-10 min (perf, not editorial) | other | — | NONE |

---

## 2. Reference videos / creators

Strict test applied: a specific identifiable third-party video, or a named creator held up as
an exemplar. SEO blog posts, vendor documentation, GitHub repos, and PyPI pages were all
**rejected** — that removes ~55 of the ~60 URLs across these five files.

| File:line | Identifier | Platform | URL | Specificity | Why cited |
|---|---|---|---|---|---|
| F3:862 (cross-ref F3:72, F3:627) | `@thedronecreative` — video id 7380822378483338528, "Drone Orbit + Speed Ramp Technique" | TikTok | https://www.tiktok.com/@thedronecreative/video/7380822378483338528 | **specific_video** | Sole named exemplar in this slice. Used twice to justify a MUST-HAVE priority: L72 (Orbital Continuation Cut — "highly viral technique") and L627 (Hyperlapse Zoom-Through — "viral drone technique per TikTok @TheDroneCreative analysis"). The word "analysis" implies a study of the video; no such analysis appears in the document. |

**Near-misses, deliberately excluded:**
- F5:264 `"nemo_integration": "TikTok link analysis for template extraction"` — names a tool, no video.
- F5:262 `"Extract cut maps from viral videos"` — generic, no identifier.
- F1:597/602/607 "35% of top-performing travel reels" / "22% of adventure content" — aggregate populations with no video, creator, or dataset named.
- F2 sources 1/2/10/11, F3 source "Top 5 Video Transitions for Reels/TikTok 2025", F4 sources 1/20 (Oscar Liang) — blog articles. Oscar Liang is a named person, but cited as a written tutorial author, not held up as a video exemplar; excluded per the strict test.

---

## 3. Internal contradictions

| # | Topic | Claim A | Claim B | Note |
|---|---|---|---|---|
| C1 | **Optimal shot length for beat-synced editing** | "1.5-2 second clip duration optimal for beat-synced montages" — F5:870 | TikTok 2.5-4.5s / IG 3-5s / YT 3-6s, and the tempo table's fastest bucket is 2.0-3.5s — F1:199-203, F1:906 | Direct conflict. F5's floor (1.5s) sits below F1's *fastest possible* clip under any platform or any tempo. Both are uncited. Anything that averaged the corpus would land on a value neither document supports. |
| C2 | **Shot length inside F5 itself** | "1.5-2 second clip duration optimal" — F5:870 | 15s reel = "top 4-6 clips totalling ~13 seconds" ⇒ 2.2-3.3s per clip — F5:842 | Same file contradicts itself. The recipe cannot be built from the expert opinion. |
| C3 | **Reels bitrate** | video bitrate "5000-10000 kbps (5-10 Mbps)" — F5:893 | "Stay within 5-15 Mbps bitrate range for best quality/size balance" — F5:905 | Same `instagram_reels_specifications` object, 12 lines apart. Upper bound differs by 50%. Neither cites Instagram. |
| C4 | **Reels bitrate across files** | IG preset bitrate 5000k — F1:1058 | 5000-10000 kbps / 5-15 Mbps — F5:893/905 | F1 pins the bottom of F5's range as *the* value with no note that a range exists. |
| C5 | **Hyperlapse zoom-through speed factor** | "accelerates dramatically (2x → 8x speed)" — F3:584 | implementation ramps `start_speed=1.0, end_speed=3.0` — F3:596-603 | Prose and code in the same section, 15 lines apart, disagree by up to 2.7×. The 8x figure appears nowhere else in the file. |
| C6 | **Whip pan is/isn't already implemented, and is/isn't a cut** | "Priority: MUST-HAVE — already partially implemented via `select_motion_matched_transition()`"; whip pan = "pure cut with matching motion vectors", no duration — F3:25, F3:49 | Listed as MISSING feature #13 with `whip_pan_transition(..., duration=0.2)` — F4:405, F4:417 | Both files dated 2026-02-21. One says shipped-as-a-cut, the other says missing-and-needs-a-0.2s-blur. Directly contradictory on both existence and on whether the transition has a duration at all. |
| C7 | **Which transitions already exist** | Implemented: CUT, CROSSFADE, FADE_BLACK, FADE_WHITE, ZOOM_IN, ZOOM_OUT, SLIDE_LEFT, SLIDE_RIGHT (+2 unimplemented WIPEs) — F3:12-15 | "Transitions: cut, crossfade, fade_black, zoom_in" — F4:13 | Same date. F4's inventory is a strict subset of F3's, missing 4 transitions F3 says exist. Any "gap analysis" built on F4 overstates the gap. |
| C8 | **Colour preset count** | "`color_grader.py` has 11 presets" — F1:466 | 10 presets enumerated — F4:12 | Different dates (Jan 25 vs Feb 21) so drift is possible, but F4 claims *more* features exist overall while listing *fewer* presets. |
| C9 | **Transition duration for high-energy cuts** | Ambient/no-music and motion-safe modes both set transition_duration 0.8s — F1:969, F1:1141 | Auto-selection assigns 0.15s (glitch) to 0.6s (hyperlapse); "typically 0.2-0.8s" — F3:790-796, F3:849 | Not strictly contradictory, but F1 treats 0.8s as the *slow/safe* end while F3 treats 0.8s as the *outer maximum* for any transition. A pipeline reading both would find 0.8s labelled both "gentle default" and "longest we ever go". |
| C10 | **Contrast direction for bright daylight footage** | harsh_midday: contrast **-10** — F2:99 | Every other F2 preset and F1's platform advice push contrast up (+5 to +60); F1:1078 prescribes "punchy: high contrast + saturation" for TikTok generally | Not a numeric collision, but the sole negative-contrast recommendation in the slice, and it applies to the lighting condition drone footage is most often shot in. Flagged because an averaged "contrast delta" constant would erase it. |
| C11 | **Target total duration** | TikTok ideal 21s, IG 30s, YT 45s — F1:1076/1054/1098 | "optimal 15-30 seconds for engagement", max 90s — F5:899 | F1's YouTube target (45s) sits outside F5's optimal band entirely; F1 justifies it as "longer watch time = better algorithm" (F1:1098) while F5 gives no rationale. Opposite directional reasoning, both uncited. |

---

## 4. Assessment of how well-founded these claims are

Ranked by how much epistemic weight the documents themselves actually support:

1. **Traceable to a vendor/primary source (weakest-but-real):** F5's 5 `professional_software`
   blocks (DJI Fly, DJI Mimo, LumaFusion, CapCut, Premiere Rush) each carry a URL. Even here
   the numbers are marketing figures — "~40% faster than manual editing (reported)" carries
   the document's own hedge, and the identical 40% appears for a *different* product 30 lines
   later, which reads more like one number reused than two measurements.
2. **Named external standard, no URL:** WCAG 4.5:1 / 7:1 (F1:1178). Real, checkable, but the
   document does not cite it.
3. **Camera-vendor colour math:** LogC3/Log3G10 decode constants (F2:361-367, F2:398) and
   D-Log M constants (F4:333-335). These are the kind of number that *does* have a primary
   source (ARRI/RED/DJI docs, two of which appear in F2's bulk list) — but the document never
   links constant to source, so they are unverified as transcribed.
4. **Free-floating engineering defaults:** the large majority — vignette 0.5, halation 0.3,
   grain 0.3, glitch 0.15s, iris 0.4s, every contrast/saturation delta in F2. These read as
   plausible starting values invented for the code, not measured. Presenting them in a
   "research" document gives them borrowed authority they never earned.
5. **Free-floating audience/behaviour claims — the least founded and the most dangerous:**
   F1:1005 retention curve (>80%/>60%/>40%), F1:1087 "80% of top content", F1:597/602/607
   ("35% of top-performing travel reels", 22%, 18%), F5:870 "1.5-2s optimal". These are
   population statistics stated to two significant figures with no dataset, no sample size,
   no date, and no source. F1 contains zero URLs, so there is no chain to follow even in
   principle. The four A/B "hypotheses" (F1:1027-1039, +10-15%, +12-18%, +20%, +8-12%) are at
   least *labelled* hypotheses by the document — which makes them more honest than the
   percentages above them, and they should not be silently promoted to findings.

**Bottom line for the registry:** in this slice, the parameters `editorial_style.json` marks
UNSUPPORTED (grade intensity, LUT strength, dissolve duration, letterbox ratio) map almost
exactly onto category 4 and 5 above. The corpus does not supply grounding for them. It
supplies confident-looking numbers that trace to nothing, plus one TikTok URL.

## 5. Coverage note

All 5 assigned files read end to end (1322 + 700 + 867 + 750 + 1008 = 4647 lines). No file
skipped, no file truncated. Read-only throughout; nothing under `_archive/` was written,
moved, or modified; the dead symlink was not followed. No network requests made — no URL in
any of these documents was fetched or checked for liveness, per scope. No image/frame file
written anywhere.

Deliberately excluded from the claims tables, per the task's exclusion list: old-project
source line numbers, function signatures, LOC estimates, feasibility scores (x/5), priority
tiers, impact/complexity ratings, est. dev-time hours, and per-frame performance costs
(the last logged in the F3/F5 tables only where they sat inside a row I was already
recording).

The claims table above is a superset of what fits in the 60-item structured return; the
structured return prioritises subjects named in the task (shot_length, total_duration,
cut_rate, transition_duration, colour_grade, saturation, contrast, letterbox_aspect,
resolution, framerate, bitrate, audio_bpm, hook_timing, retention, speed_ramp, text_overlay)
and drops the lowest-value engineering defaults. This file is the complete record.
