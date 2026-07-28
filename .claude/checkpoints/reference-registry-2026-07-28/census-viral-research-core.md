# Census: viral-research-core slice

**Agent slice:** `census-viral-research-core`
**Date:** 2026-07-28
**Corpus status:** UNTRUSTED. All five files are LLM-generated research/planning output from the
archived `_p-ai-drone-video` project (documents self-date 2026-01-25 / 2026-01-27). Nothing below
is endorsed as fact. Every row records what the document *asserts* and what it *credits*.

## Files read (end to end)

| Key | Absolute path | Lines |
|---|---|---|
| R | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/viral_drone_video_research.md` | 674 |
| P | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/viral_drone_editing_patterns.md` | 626 |
| J | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/viral_insights_structured.json` | 394 |
| S | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/RESEARCH_SUMMARY.md` | 456 |
| I | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/implementation_priorities.md` | 432 |

---

## 0. THE SINGLE MOST IMPORTANT PROVENANCE FACT

**Not one numeric claim in this slice carries an inline citation.**

Verified mechanically:

```
awk '/https?:\/\// {print FILENAME":"FNR}' R P S I   # -> every hit falls inside the
                                                     #    trailing Sources section
```

Result: **zero URL-bearing lines outside the trailing `## SOURCES` / `## RESEARCH SOURCES` /
`## Resources & References` blocks** in any of the four markdown files. `viral_insights_structured.json`
contains **no URL at all** and no sources field beyond `"sources_analyzed": 45`.

So the attribution structure of this whole corpus is:

- claims are stated bare in the body;
- a topical bulk URL list sits at the end (R: 28 unique URLs; P: 37; S: 16; I: **0**; J: **0**);
- nothing maps a number to a source.

The only exceptions — the only places a document credits a number to anything at all — are four
inline verbal credits, none of them resolvable:

| File:line | Verbal credit | Resolvable? |
|---|---|---|
| R:293 | "**Facebook Study:** 65% who watch first 3 seconds continue for 10+ seconds" | No study named, no year, no URL. No Facebook/Meta URL anywhere in R's source list. |
| P:366 | "27% boost in online video engagement (2025 automotive case study)" | Unnamed case study. |
| P:425 | "41% increase in virtual tour engagement (2025 hospitality case study)" | Unnamed case study. |
| S:52 | "Analysis of top 100 viral Shorts: 2.5s average clip length = **35% higher completion**" | Unnamed analysis. Also a platform mismatch — "Shorts" is YouTube; the doc's stated scope is Instagram Reels + TikTok. |

Everything else is `NONE`.

One near-miss worth naming explicitly so nobody upgrades it later: P:581 and S:379 both list
`https://www.creatorsjet.com/blog/best-instagram-reel-length-for-engagement-based-on-500-viral-videos`
in their bulk topical lists. That URL *title* contains "based on 500 viral videos" and sits in the
"Cut Frequency & Pacing" / "Platform Best Practices" grouping. It is **tempting but unsupported** to
treat it as the source of the 7-15s or 1.5-3s numbers. The documents never make that link. Recorded
as NONE.

---

## 1. NUMERIC EDITORIAL CLAIMS — FULL TABLE

Subject codes: DUR=total_duration, SHOT=shot_length, CUT=cut_rate, TRANS=transition_duration,
GRADE=colour_grade, ASP=letterbox_aspect, RES=resolution, FPS=framerate, BR=bitrate,
BPM=audio_bpm, HOOK=hook_timing, RET=retention, RAMP=speed_ramp, TEXT=text_overlay, OTH=other.

### 1.1 File R — viral_drone_video_research.md (self-dated 2026-01-25)

| Line | Subj | Value | Unit | Claim | Credited to |
|---|---|---|---|---|---|
| 8 | DUR | 15-30 | s | "15-30 second optimal length" (exec summary) | NONE |
| 8 | HOOK | 3 | s | "strong opening hooks in the first 3 seconds" | NONE |
| 47 | HOOK | 3 | s | FPV "instant attention-grabbing for first 3 seconds" | NONE |
| 55 | RET | 22 | % | "Videos with varied speeds see 22% longer watch times on TikTok" | NONE |
| 63 | RET | 40 | % | "Beat-synced videos increase engagement by up to 40%" | NONE |
| 72 | SHOT | 1-2 | s | "Fast-Paced: 1-2 second cuts for high-energy content" | NONE |
| 73 | SHOT | 3-5 | s | "Cinematic: 3-5 second cuts for landscape/scenic content" | NONE |
| 74 | HOOK | 3 | s | "Faster cuts in first 3 seconds, then settle into rhythm" | NONE |
| 133 | DUR | 90 / 1200 | s | IG max "extended to 20 minutes (as of 2025: 90 seconds)" — self-contradictory in one line | platform_spec (uncited) |
| 134 | DUR | 15-30 | s | "Optimal for Engagement: 15-30 seconds (shorter is better)" | NONE |
| 138 | DUR | 15-3600 | s | TikTok "15 seconds to 60 minutes (10 minutes recording max)" | platform_spec (uncited) |
| 139 | DUR | 30 | s | TikTok "Strongest Engagement: 30 seconds or less" | NONE |
| 140 | DUR | 15-30 | s | "Sweet Spot: 15-30 seconds for viral potential" | NONE |
| 143 | DUR | 30 | s | "videos under 30 seconds generate highest engagement and completion rates" | NONE |
| 148 | ASP | 9:16 | ratio | "Aspect Ratio: 9:16 (vertical)" | platform_spec, bulk URLs at R:600-603 |
| 149 | RES | 1080x1920 | px | "Resolution: 1080 × 1920 pixels" | platform_spec, bulk URLs at R:600-603 |
| 159 | FPS | 30 | fps | Export "Frame Rate: 30 FPS" | NONE |
| 160 | BR | high | none | "High bitrate to reduce upload blur" (no number given) | NONE |
| 161 | RES | 1080p | px | "Resolution: 1080p minimum" | NONE |
| 166 | FPS | 30 | fps | "Both Instagram and TikTok optimize for 30 FPS" | NONE |
| 168 | FPS | 30 | fps | "Instagram Behavior: Forces 30 FPS anyway" | NONE |
| 173-175 | FPS | 24 | fps | 24 FPS "can cause stuttering"; "Avoid for social media" | NONE |
| 180 | FPS/RES | 60 / 4K | fps | "TikTok: 4K at 60 FPS can improve video performance" | NONE |
| 184 | FPS | 30 | fps | "Shoot at 30 FPS or 60 FPS → Export at 30 FPS" | NONE |
| 189 | RET | 40 | % | "Up to 40% increase in engagement vs non-synced" | NONE |
| 240 | OTH | 30-60 | min | Golden hour "30-60 mins after sunrise/before sunset" | NONE |
| 250 | OTH | 20 | min | "Be ready 20 minutes before sunrise" | NONE |
| 293 | RET | 65 | % | "65% who watch first 3 seconds continue for 10+ seconds" | **"Facebook Study"** (unnamed) |
| 294 | RET | 45 | % | "Conversion Rate: 45% will watch for 30+ seconds" | adjacent to the Facebook Study line; attribution ambiguous |
| 295 | HOOK | 2 | s | "Users decide within 2 seconds to keep watching or swipe" | NONE |
| 332 | TEXT | 3 | s | "Subtitles and bold colors in first 3 seconds" | NONE |
| 339 | RET | 1200 | % | "Videos with strong hooks in first 1-3 seconds generate 1,200% more shares" | NONE |
| 416 | RET | 40 | % | Self-projection: "Expected Impact: 40% engagement increase" | derived from R:63 |
| 426 | RET | 65 | % | Self-projection: "Expected Impact: 65% retention past 3 seconds" | derived from R:293 |
| 436 | RET | 22 | % | Self-projection: "Expected Impact: 22% longer watch times" | derived from R:55 |
| 461 | DUR | 15-30 | s | "Target: 15-30 seconds total" | NONE |
| 473 | RES/FPS | 1080x1920 / 30 | px / fps | "Export: 1080x1920, 30 FPS, H.265, high bitrate" | NONE |
| 501 | TEXT | 3 | s | "First 3 Seconds: Add attention-grabbing text" | NONE |
| 513-515 | DUR/ASP/FPS | 15-30 / 9:16 / 30 | mixed | Tier 1 priority list | NONE |
| 551 | GRADE | 50-70 | % | "Apply creative LUT at 50-70% intensity" | NONE |
| 553 | SAT | — | none | "Slight saturation boost for social media" — **no number given** | NONE |
| 644-651 | mixed | 3 / 40 / 30 / 9:16 / 15-30 / 22 | mixed | "Key Takeaways" restating the above as imperatives ("30 FPS export is mandatory", "9:16 is non-negotiable") | NONE |

Excluded from R as non-editorial: R:583 "Complete edit in under 5 minutes" (tool speed),
R:656 "80% of users shouldn't need to adjust settings" (UX target),
R:349-370 follower counts (creator metadata, captured in §2).

### 1.2 File P — viral_drone_editing_patterns.md (self-dated 2026-01-27)

| Line | Subj | Value | Unit | Claim | Credited to |
|---|---|---|---|---|---|
| 11 | DUR | 7-15 | s | "Optimal length: 7-15 seconds for highest completion rate and shareability" | NONE |
| 12 | DUR | 15-30 | s | "Sweet spot: 15-30 seconds balances impact with engagement" | NONE |
| 13 | DUR | 30 | s | "Maximum recommended: 30 seconds before noticeable drop-off" | NONE |
| 14 | DUR | 60-90 | s | "Extended format: 60-90 seconds can work for narrative-driven content" | NONE |
| 17 | SHOT | 1.5 | s | "Minimum viable: 1.5 seconds (shorter shots are too fast for viewers to process)" | NONE |
| 18 | SHOT | 4 | s | "Maximum before drag: 4 seconds" | NONE |
| 19 | SHOT | 1.5-2 / 3-4 | s | "Action sports benchmark: quick cuts (1.5-2s) with contemplative shots (3-4s)" | NONE |
| 24 | RET | 50 | % | "50% of viewers drop off in first 3 seconds" | NONE |
| 25 | RET | 3 | s | "Average watch time: Just 3 seconds on Instagram Reels" | NONE |
| 27 | OTH | 1-2 | shots | "1-2 shots maximum in hook window" | NONE |
| 30 | HOOK | 3-15 | s | Build section defined as 3-15 s | NONE |
| 32 | SHOT | 1.5-3 | s | Build section "Shot duration: 1.5-3 seconds per clip" | NONE |
| 36 | DUR | 15-25 | s | Climax Section (15-25 seconds) | NONE |
| 41-42 | DUR/SHOT | 25-30 / 3-4 | s | Resolve Section 25-30 s, shots "can extend to 3-4 seconds" | NONE |
| 47 | CUT | 15-25 | cuts/min | "Estimated cuts per minute: 15-25 cuts (based on 1.5-4 second shot durations)" | self-derived, and **arithmetically wrong** (see §3) |
| 48 | CUT | 40 | cuts/min | "Up to 40 cuts per minute in action peaks" | NONE |
| 49 | CUT | 70-90 | % | "70-90% of cuts should align with musical beats or downbeats" | NONE |
| 78 | TRANS | 0.3-0.5 | s | "Duration: 0.3-0.5 seconds (10-15 frames at 30fps)" — **frame maths wrong** (see §3) | NONE |
| 96 | TRANS | 5 | frames | Whip pan: "5 frames before cut (0% blur) → cut point (100% blur) → 5 frames after" | NONE |
| 162 | FPS | 60 | fps | "Shoot at 60fps minimum for quality slow-motion" | NONE |
| 163 | RAMP | 10-50 | % | "Limit speed decrease to 10-50% to avoid artifacts" — ambiguous (of original? or reduction by?) | NONE |
| 176 | RAMP | 150-300 | % | "150-300% for subtle acceleration" | NONE |
| 177 | RAMP | 400-800 | % | "400-800% for dramatic time compression" | NONE |
| 193 | RAMP | 15-20 | frames | "Gradual deceleration: 1x → 0.5x over 15-20 frames" | NONE |
| 194,196 | RAMP | 1x→2x→4x | multiplier | Stepped acceleration / smooth cycle patterns | NONE |
| 208-210 | RAMP | 10-15 / 20-30 / 10-15 | frames | ramp in / slow-mo hold / ramp out | NONE |
| 231 | HOOK | 2-3 | s | "reveal happens in first 2-3 seconds" | NONE |
| 255 | HOOK | 2 | s | "Slow-motion impact moment in first 2 seconds" | NONE |
| 278 | ASP | 9:16 | ratio | "9:16 aspect ratio fills mobile screen" | NONE |
| 279 | RES | 4K | px | "4K resolution: Critical for screen presence on small displays" | NONE |
| 280 | FPS | 30 / 60 | fps | "30fps standard, 60fps if slow-motion in hook" | NONE |
| 303 | OTH | 3-5 | s | "3-5 second duration per Ken Burns movement" | NONE |
| 311 | OTH | 110-130 | % | Zoom end keyframe "scale 110-130%" | NONE |
| 323 | OTH | 5-10 | frames | "Quick zoom-in (5-10 frames) on subject entry" | NONE |
| 324 | BPM | every 4th | beat | "Punch zoom on every 4th beat or downbeat" | NONE |
| 366 | RET | 27 | % | Orbit: "27% boost in online video engagement" | **"2025 automotive case study"** (unnamed) |
| 391 | SHOT | 2-5 | s | Reveal shots: "2-5 seconds for reels (faster = more impact)" | NONE |
| 425 | RET | 41 | % | FPV: "41% increase in virtual tour engagement" | **"2025 hospitality case study"** (unnamed) |
| 484 | TRANS | 1-3 | s | J-cuts: "1-3 seconds of audio overlap typical" | NONE |
| 496 | CUT | 70-90 | % | "70-90% of cuts should align with musical structure" | NONE |
| 516 | SHOT | 1.5-3 | s | Must-have: "Fast-paced beat-synced cutting (1.5-3 second shots)" | NONE |
| 517 | HOOK | 2 | s | Must-have: "Dynamic hook in first 2 seconds" | NONE |
| 525 | RAMP | 50 | % speed | "Strategic slow-motion at peak moments (50% speed)" | NONE |
| 541 | DUR | 7-15 / 30 | s | "Speed matters: 7-15 seconds optimal, 30 seconds maximum" | NONE |
| 542 | RET | 50 | % | "Hook is everything: 50% drop-off in first 3 seconds" | NONE |
| 543 | CUT | 70-90 | % | "Beat sync critical: 70-90% of cuts align with music" | NONE |
| 549-552 | mixed | 0-3 / 3-15 / 15-25 / 25-30 | s | **Editing Rhythm Formula** code block (see §3 contradiction C7) | NONE |
| 556 | FPS | 30 / 60 | fps | "30fps standard, 60fps for slow-motion" | NONE |
| 557 | RES | 4K | px | "Resolution: 4K for quality on mobile screens" | NONE |
| 559 | SHOT | 1.5-4 (2-3) | s | "Shot duration: 1.5-4 seconds (sweet spot: 2-3s)" | NONE |
| 560 | TRANS | 0.3-0.5 | s | "Transition duration: 0.3-0.5 seconds" | NONE |
| 561 | RAMP | 10-20 | frames | "Speed ramp curve: 10-20 frames for smooth transition" | NONE |

### 1.3 File J — viral_insights_structured.json (self-dated 2026-01-25)

Machine-readable. **This is the highest-risk file in the slice** — it is the one a future pipeline
could `json.load()` and consume as config without a human ever seeing that the numbers are uncited.

| Line | Subj | Value | Key | Credited to |
|---|---|---|---|---|
| 5 | OTH | 45 | `sources_analyzed: 45` | self-assertion; J itself contains 0 URLs |
| 10-11 | ASP/RES | 9:16 / 1080x1920 | `aspect_ratio` | NONE |
| 15 | DUR | [15, 30] | `optimal_range_seconds` | NONE |
| 16 | DUR | 90 | `instagram_max_seconds` | NONE |
| 17 | DUR | 600 | `tiktok_max_seconds` | NONE |
| 18 | DUR | 30 | `engagement_drop_after_seconds` | NONE |
| 21-23 | FPS | 30 / [30,60] / 24 | `recommended_export` / `shooting_options` / `avoid` | NONE |
| 30 | RES | 1080p | `resolution: "1080p minimum"` | NONE |
| 78 | RET | 22 | `speed_ramps.engagement_impact_percent` | NONE |
| 141 | GRADE | 50-70 | `"Apply creative LUT at low intensity (50-70%)"` | NONE |
| 148 | HOOK | 3 | `critical_window_seconds` | NONE |
| 150 | RET | 65 | `watch_3_seconds_continue_10_seconds_percent` | NONE (the "Facebook Study" credit at R:293 did **not** survive into J) |
| 151 | RET | 45 | `watch_3_seconds_continue_30_seconds_percent` | NONE |
| 152 | HOOK | 2 | `decision_time_seconds` | NONE |
| 175 | RET | 1200 | `share_amplification_percent` | NONE |
| 179 | RET | 40 | `music_sync.engagement_increase_percent` | NONE |
| 204 | OTH | 30-60 | golden hour `timing` | NONE |
| 214 | OTH | 20 | "Be ready 20 minutes before sunrise" | NONE |
| 289 | DUR | 15-30 | tier_1 `Optimal Length Enforcement.target` | NONE |
| 303 | mixed | 30 fps / 1080x1920 / H.265 | tier_1 `Export Settings.specs` | NONE |
| 322 | RET | 40 | `engagement_increase_percent` | NONE |
| 330 | RET | 22 | `watch_time_increase_percent` | NONE |
| 354 | RET | 65 | `retention_increase_percent` | NONE |
| 367-374 | mixed | 65 / 40 / 22 / [15,30] / 1200 / 30 / 9:16 / 1080x1920 | **`key_metrics` block** — the whole editorial constant set in one object | NONE |

### 1.4 File S — RESEARCH_SUMMARY.md (self-dated 2026-01-27)

**S introduces numbers that appear in neither R nor P nor J.** Specifically `72%`/`46%` completion,
`+45%` golden hour, `+30%` top-down, `35%` higher completion / "top 100 viral Shorts", `85%+`
sound-off, and the `60-80% / 40-60% / 30%` retention bands. A summary document is inventing data
its own sources do not contain.

| Line | Subj | Value | Claim | Credited to |
|---|---|---|---|---|
| 14 | RET | 65 / 1200 | "65% retention if hook is strong \| +1200% shares" | NONE — and note the semantic drift from R:293's conditional continuation rate |
| 15 | RET | 40 | "+40% engagement" | NONE |
| 16 | RET | 22 | "+22% watch time" | NONE |
| 17 | DUR/RET | 15-30 / 72 | "15-30 seconds optimal \| 72% completion rate" | NONE — contradicted by S:144/S:148 |
| 18 | ASP | 9:16 | "9:16 vertical mandatory" | NONE |
| 19 | FPS | 30 | "30 FPS export" | NONE |
| 20 | SHOT | 1.5-3 | "Every 1.5-3 seconds" | NONE |
| 21 | RET | 45 | "Golden Hour ... +45% engagement" | NONE — **appears nowhere in R, P, or J** |
| 22 | RET | 30 | "Top-Down Shots ... +30% likes" | NONE — **appears nowhere in R, P, or J** |
| 32-34 | RET/HOOK | 65 / 45 / 2 | restates R:293-295 | NONE (Facebook Study credit dropped) |
| 50 | SHOT | 1.5-3 (2.5) | "Cut every 1.5-3 seconds (average 2.5s)" | NONE |
| 51 | SHOT | 4 | "Static shots > 4 seconds = viewer dropout" | NONE |
| 52 | SHOT/RET | 2.5 / 35 | "top 100 viral Shorts: 2.5s average clip length = 35% higher completion" | **"Analysis of top 100 viral Shorts"** (unnamed; YouTube-platform mismatch) |
| 57 | RET | 40 | "40% engagement increase when beat-synced" | NONE |
| 59 | SHOT | 4 | "Enforce maximum 4-second clip length" | NONE |
| 68 | RET | 30 | "Top-Down: Overhead perspective (+30% likes in 2024)" | NONE |
| 87 | RET | 22 | "+22% watch time increase" | NONE |
| 93 | TRANS | 0.3 | "Crossfade on beat (0.3s duration)" — P's 0.3-0.5 range hardened to its floor | NONE |
| 97 | GRADE | 50-70 | "Apply LUTs at 50-70% intensity (not 100%)" | NONE |
| 107-108 | OTH | — | Trending audio named: "Purple Rain, Heroes"; "Espresso, Dramamine" | NONE |
| 112 | RET | 85 | "85%+ of videos watched without sound" | NONE |
| 113 | RET | 40 | "Beat-synced videos: +40% engagement" | NONE |
| 130 | TEXT | 2/3 | "Safe zone compliance (center 2/3 of frame)" | NONE |
| 143 | DUR/RET | 7-15 / 60-80 | "7-15 seconds: 60-80% retention (highest)" | NONE |
| 144 | DUR/RET | 15-30 / 40-60 | "15-30 seconds: 40-60% retention (recommended)" | NONE |
| 145 | DUR/RET | 45+ / 30 | "45+ seconds: Rarely above 30% retention" | NONE |
| 148 | DUR/RET | 15 / 72 | "≤15 seconds: 72% completion" | NONE |
| 149 | RET | 46 | "Longer videos: 46% completion" | NONE |
| 152-154 | ASP/RES/FPS | 9:16 / 1080x1920 / 30 | Format requirements | NONE |
| 164 | DUR | 15-30 | "Enforce 15-30 second total output" | NONE |
| 167 | GRADE | 60 | "Teal-orange LUT at 60% intensity" — range hardened to a point value | NONE |
| 176 | SHOT/RET | 1.5-3 / 40 | "Cut every 1.5-3s aligned to beats (+40% engagement)" | NONE |
| 177 | RET | 22 | "+22% watch time" | NONE |
| 178 | RET | 45 | "Golden Hour Detection ... (+45% engagement)" | NONE |
| 188 | RET | 65 | "Ensure first 3s are most engaging (+65% retention)" — **"65% retention" has now become a projected *gain*** | NONE |
| 294 | DUR | 15-30 | Success metric | NONE |
| 305 | RET | 65 | "65% retention past first 3 seconds" | NONE |

### 1.5 File I — implementation_priorities.md (undated header; body says "2024-2025")

I is where the numbers become **default config values** — the shortest path from uncited research to
a shipped constant. I contains **zero URLs**; its only "Research Sources" (I:411-412) are two absolute
paths on a machine that no longer exists (`/Users/matthewdeane/...`).

| Line | Subj | Value | Claim | Credited to |
|---|---|---|---|---|
| 10 | RET/HOOK | 65 / 3 | "First 3 seconds determine 65% retention rate" — strongest causal restatement of R:293 yet | NONE |
| 11 | RET | 40 | "Beat-synced cuts increase engagement by 40%" | NONE |
| 12 | RET | 22 | "Speed ramps add 22% watch time" | NONE |
| 13 | DUR | 15-30 | "Optimal length: 15-30 seconds (not longer)" | NONE |
| 24 | DUR | 15-20 (max 30) | "Target total output: 15-20 seconds (configurable, max 30s)" | NONE |
| 27 | DUR | 20 / 30 | "Default config: `target_duration: 20`, `max_duration: 30`" | NONE |
| 32 | DUR | 20 / 30 | `def select_clips_for_duration(scenes, target_duration=20, max_duration=30)` | NONE |
| 53,59-60 | HOOK | 3 | hook scoring window = first 3 seconds | NONE |
| 72 | SHOT | 1.5-3 (2.5) | "Enforce cuts every 1.5-3 seconds (average 2.5s)" | NONE |
| 73 | SHOT | 4 | "Never allow static shots > 4 seconds" | NONE |
| 81 | SHOT | 1.5 / 3.0 | `generate_cut_points_with_frequency(..., min_gap=1.5, max_gap=3.0)` | NONE |
| 106 | RES | 1080x1920 | "Export at exactly 1080x1920" | NONE |
| 112-115 | ASP/RES/FPS | 9:16 / [1080,1920] / 30 / h265 | `output_format` JSON block | NONE |
| 125 | RET | 22 | "+22% watch time" | NONE |
| 138 | RAMP | 1.0 → 0.5 | `apply_ramp(..., start_speed=1.0, end_speed=0.5, ...)` | NONE |
| 163 | RET | 30 | "Favor top-down shots (proven +30% engagement in 2024)" — note "**proven**", and note "likes"→"engagement" drift from S:22/S:68 | NONE |
| 199 | GRADE | 50-70 | "Apply LUTs at 50-70% intensity (not 100%)" | NONE |
| 212 | GRADE | 0.6 | `def apply_lut_with_blend(self, frame, lut_name, intensity=0.6)` | NONE |
| 243 | TRANS | 0.3 | `self._create_crossfade(clip1, clip2, duration=0.3)` | NONE |
| 261 | RET | 85 | "85% watch without sound" | NONE |
| 297 | OTH | 60-70 | "60-70% mark: Climax clip (second-best hook)" | NONE |
| 345 | RET | 65 | "3-second retention rate (target: 65%+)" | NONE |
| 346 | RET | 60 | "Completion rate (target: 60%+ for 15-20s videos)" | NONE |
| 351 | SHOT | 2.5 | "Average clip length (target: 2.5s)" | NONE |
| 352 | CUT | 0.33-0.67 | "Cuts per second (target: 0.33-0.67)" — **the one place the arithmetic checks out** (1/3s .. 1/1.5s) | NONE |
| 353 | BPM | 95 | "Beat alignment accuracy (target: 95%+)" | NONE |
| 354 | DUR | 15-20 | "Total video duration (target: 15-20s)" | NONE |
| 367 | DUR | 15/20/30 | A/B test: "15s vs 20s vs 30s (hypothesis: 20s optimal)" — the only place the corpus admits a number is a hypothesis | NONE |
| 368 | SHOT | 2/2.5/3 | A/B test: "2s avg vs 2.5s avg vs 3s avg" | NONE |
| 374 | RET | 20 | "Implementation increases completion rate by 20%+" | NONE |

Excluded from I as codebase-internal (per slice definition): I:67 hook score weights
(`motion*0.5 + color*0.3 + sharpness*0.2`), I:152 `3*t**2 - 2*t**3` easing, phase/week numbering.
**Flagged anyway** in §4 because the 0.5/0.3/0.2 weights are exactly the kind of invented constant
this project's Constitution prohibits, and they are one copy-paste away from `src/`.

---

## 2. REFERENCE VIDEOS / EXEMPLAR CREATORS

**Headline finding: the corpus cites ZERO specific viral drone videos.** Five documents whose entire
subject is "what makes a drone video go viral" do not identify a single video that went viral. There
is nothing here that could function as a visual benchmark, an A/B reference, or a target to measure
against.

What does exist is four Instagram handles and one YouTuber, listed with follower counts and
credentials but **no linked work**:

| Identifier | Platform | URL | Why cited | Where | Specificity |
|---|---|---|---|---|---|
| @thedronecreative (Matthew Brennan) | Instagram + TikTok | R:636 `https://www.instagram.com/thedronecreative/`, R:637 `https://www.tiktok.com/@thedronecreative` (profile links only, in the bulk source list) | "Top Drone Videographers to Study"; 136K followers; Dubai; "Notable Technique: Orbit transitions with speed ramps and motion blur" | R:347-354, J:255-263, I:415 | creator_only |
| @beverlyhillsaerials | Instagram | NONE | 179.4K followers; "3x Emmy Award Winner"; Film/TV/Commercial | R:356-360, J:264-270, I:416 | creator_only |
| @basso2012 | Instagram | NONE | 54.2K followers; "DGCA Authorized UAV Pilot" | R:362-365, J:271-277, I:417 | creator_only |
| @simeonpratt | Instagram | NONE | 25.6K followers; Director/Cinematographer | R:367-370, J:278-283 | creator_only |
| Casey Neistat | YouTube (implied) | NONE | Speed ramps "used by Casey Neistat and top vloggers" (R:54); "Casey Neistat's vlog style (speed ramps, dynamic pacing)" (R:375) | R:54, R:375 | creator_only — and not a drone creator |

The four handles and their follower counts most plausibly derive from the Feedspot listicle at
R:635 (`https://influencers.feedspot.com/drone_instagram_influencers/`), which sits in R's
"Influencers & Examples" source group — but the documents never say so. Recorded as unattributed.

**Explicitly NOT counted as reference videos** (applying the strict rule):
- SEO/tutorial blog URLs (all 64 unique URLs across the corpus) — articles, not videos.
- Courses: "Drone Film Guide courses" (R:377), "Drone Film Grades (Teachable)" (R:380).
- Tools: DJI LightCut, CapCut, Premiere, Filmora, InShot (R:66-69, S:314-317).
- Unnamed case studies: "2025 automotive case study" (P:366), "2025 hospitality case study" (P:425),
  "top 100 viral Shorts" (S:52), "500 viral videos" (URL title only, P:581/S:379).
- "Las Vegas campaigns" (R:25) — no identifiable work.
- Named *audio* tracks (S:107-108: Purple Rain, Heroes, Espresso, Dramamine) — songs, not videos or
  creators. Noted here because a future reader may mistake them for content exemplars.

---

## 3. INTERNAL CONTRADICTIONS

Ranked by consequence for anyone tempted to inherit a number.

### C1 — Optimal total duration: four incompatible targets
- P:11 `7-15 s` "for highest completion rate"
- R:134 / R:140 / P:12 / J:15 / S:164 `15-30 s`
- I:24 / I:354 `15-20 s`
- I:27 / I:32 default `target_duration: 20`

P states both 7-15 and 15-30 within two lines of each other (P:11, P:12) without reconciling them.
S:143-144 later tries to reconcile by demoting 15-30 to "recommended" while 7-15 gets "highest"
retention — which makes S:17's table row ("15-30 seconds optimal | 72% completion rate") wrong by
S's own §7.

### C2 — Shot length: R's guidance falls outside P's stated viable bounds
- R:72 `1-2 s` fast-paced cuts — **below** P:17's stated 1.5 s "minimum viable ... too fast for
  viewers to process".
- R:73 `3-5 s` cinematic cuts — **above** P:18's 4 s "maximum before drag" and directly contradicts
  S:51 "Static shots > 4 seconds = viewer dropout" and I:73 "Never allow static shots > 4 seconds".

Two research documents in the same directory, written two days apart, give shot-length guidance that
cannot both be followed.

### C3 — S:17 vs S:148 vs S:144: the 72% completion figure is attached to two different durations *in one file*
- S:17 (summary table): "**15-30 seconds** optimal | **72% completion rate**"
- S:148 (§7): "**≤15 seconds**: **72% completion**"
- S:144 (§7): "**15-30 seconds**: 40-60% retention"

The same document assigns 72% completion to 15-30 s in its headline table and to ≤15 s in its body,
while simultaneously giving 15-30 s a 40-60% retention band. Whichever is right, the table a reader
is most likely to skim is the one that is wrong.

### C4 — Delivery resolution: 1080p vs 4K
- R:149 `1080 × 1920`, R:161 "1080p minimum", J:11/J:374 `1080x1920`, I:106 "Export at **exactly**
  1080x1920", S:152 `1080x1920`
- P:279 "**4K resolution**: Critical for screen presence on small displays", P:557 "Resolution: **4K**
  for quality on mobile screens"

Flat contradiction on the deliverable spec. I:106's "exactly" makes it unresolvable by compromise.

### C5 — P:47 cuts-per-minute is arithmetically inconsistent with its own stated basis
P:47: "Estimated cuts per minute: **15-25** cuts (based on **1.5-4 second** shot durations)".
60/4 = 15 cuts/min; 60/1.5 = **40** cuts/min. The stated basis yields 15-40, not 15-25. P:48 then
independently states "Up to **40** cuts per minute" — i.e. the correct upper bound appears one line
later as if it were a separate, exceptional case.

### C6 — P:78 transition frame maths is wrong at the low end
P:78: "Duration: **0.3-0.5 seconds (10-15 frames at 30fps)**". At 30 fps, 0.3 s = **9** frames and
0.5 s = 15 frames. The stated frame range does not correspond to the stated second range.

### C7 — P's own Editing Rhythm Formula cannot fit inside P's own optimal duration
P:549-552 prescribes Hook 0-3 s → Build 3-15 s → Climax 15-25 s → Resolve 25-30 s, i.e. a **30-second**
structure. P:11 says optimal is **7-15 s** and P:13 says 30 s is the *maximum before drop-off*. The
document's flagship template can only be executed at the worst end of its own recommended range.

### C8 — Instagram maximum length: self-contradictory within a single line
R:133: "Maximum: Recently extended to **20 minutes** (as of 2025: **90 seconds**)". J:16 carries only
`instagram_max_seconds: 90`. The parenthetical contradicts the headline; the JSON silently picks one.

### C9 — TikTok maximum length: 60 minutes vs 600 seconds
R:138 "15 seconds to **60 minutes** (10 minutes recording max)" vs J:17 `tiktok_max_seconds: **600**`
(= 10 minutes). J encoded the parenthetical, not the stated range. Same failure mode as C8.

### C10 — "65% retention" changes meaning four times
- R:293 (with the only named credit): "65% **who watch first 3 seconds continue for 10+ seconds**" —
  a conditional continuation rate.
- S:14: "65% **retention if hook is strong**" — now conditioned on hook quality, not on having watched.
- I:10: "First 3 seconds **determine** 65% retention rate" — now causal.
- S:188 / J:354: "**+65% retention**" / `retention_increase_percent: 65` — now a projected *increase*.

A conditional observation became a causal constant and then a KPI gain, across four documents, with
the "Facebook Study" credit dropped at the first hop.

### C11 — Transition duration: a range collapses to its floor with no stated reason
P:78 / P:560 `0.3-0.5 s` → S:93 "(0.3s duration)" → I:243 `duration=0.3`. Same pattern as the LUT
value in C12. Nothing in any document explains the choice of endpoint.

### C12 — LUT intensity: "low intensity" vs 50-70% vs a hard 0.6
R:115 says "Apply creative LUT at **low intensity**"; R:551 / J:141 / S:97 / I:199 say
**50-70%** (J:141 even writes `"low intensity (50-70%)"` — 50-70% is not low); S:167 hardens to
**60%**; I:212 ships it as `intensity=0.6`. Qualitative → range → point value → code default, with
no measurement anywhere.

### C13 — Speed-ramp frame counts disagree within one file
P:193 "1x → 0.5x over **15-20** frames"; P:208-210 "**10-15** frames ramp in / 20-30 hold / 10-15 out";
P:561 summary "Speed ramp curve: **10-20** frames". Three different ramp lengths in one document.

### C14 — P:163 speed-decrease bound is ambiguous and inconsistent with P's own examples
"Limit speed decrease to **10-50%**" reads either as *slow to 10-50% of original* or *reduce speed by
10-50%*. P:193 (`1x → 0.5x`), P:525 ("50% speed") and I:138 (`end_speed=0.5`) all sit exactly on the
boundary, so the ambiguity is never resolved but is repeatedly relied on.

### C15 — Frame rate: "30 FPS is mandatory" vs "4K at 60 FPS improves performance"
R:184 / R:646 make 30 fps export mandatory; R:180 says "TikTok: 4K at 60 FPS can improve video
performance"; P:280 / P:556 allow 60 fps "if slow-motion in hook". No rule states which wins.

### C16 — Top-down uplift: metric drifts from "likes" to "engagement", and gains the word "proven"
S:22 "+30% **likes**" (no year) → S:68 "+30% **likes** in 2024" → I:163 "**proven** +30%
**engagement** in 2024". Neither the metric change nor the word "proven" is supported anywhere.

### C17 — S introduces six numbers absent from every document it claims to summarise
`72%`/`46%` completion (S:17,148,149), `+45%` golden hour (S:21,178), `+30%` top-down (S:22,68),
`35%` higher completion (S:52), `85%+` sound-off (S:112), and the `60-80% / 40-60% / 30%` retention
bands (S:143-145) appear in **none** of R, P, or J. A summary is the wrong place for new data.

### C18 — S misdescribes the very files it summarises
S:409 "viral_drone_video_research.md (**675** lines)" — actual **674**.
S:415 "viral_insights_structured.json (**395** lines)" — actual **394**.
S:421 "implementation_priorities.md (**433** lines)" — actual **432**.
S:410 "**12 major sections**" — R has **7** numbered sections (8 `##` headings including the
Executive Summary). Verified with `wc -l` and `grep -c "^## "`. Every count is wrong, uniformly by
one on the line counts. Evidence that self-descriptive numbers in this corpus were not checked.

### C19 — Source count is asserted, not demonstrated
S:5 "**45+** industry articles"; J:5 `sources_analyzed: **45**`. Actual unique URLs: R=28, P=37,
S=16, I=**0**, J=**0**; 64 unique across all four md files. The 45 figure matches no document's own
list. (Verified with `grep -oE "https?://[^)]+" | sort -u | wc -l`.)

### C20 — Corpus dating is internally inconsistent
R header "2026-01-25"; P header "2026-01-27"; S header "January 27, 2026"; I:3 bases itself on
"viral Instagram drone videos in **2024-2025**". P:610's own cited blog is dated 2025-11-01, and
multiple source titles say "2026". The research period the corpus claims to describe is not stable.

---

## 4. ASSESSMENT FOR drone_video_ai (this project's use)

1. **Nothing in this slice is measurement-grounded.** Zero inline citations; four unnamed verbal
   credits; two files (J, I) with no sources at all. Under this project's Constitution rule 1 and the
   "no invented constant" stance, **no number in this slice may be promoted to a threshold in
   `src/drone_video_ai/` as-is.**
2. **The highest-risk artifact is `viral_insights_structured.json`.** It is machine-readable, is the
   only file whose numbers are pre-shaped as config (`key_metrics`, `optimal_range_seconds`,
   `recommended_export`), and it dropped even the weak "Facebook Study" credit that the prose kept.
   A future `json.load()` would inherit ~24 uncited constants silently.
3. **The second-highest risk is `implementation_priorities.md`**, where numbers are already function
   defaults (`target_duration=20`, `min_gap=1.5, max_gap=3.0`, `intensity=0.6`, `duration=0.3`,
   `end_speed=0.5`). Copy-paste distance to `src/` is zero.
4. **Watch for the range→point-value collapse.** It has happened at least twice (C11, C12) and in
   both cases the point value is the one that reached code.
5. **Cross-check against `data/reference_pack/`.** The pack's headline finding is that the 8-file
   corpus contains **zero hard cuts** — every file is one continuous shot. Every cut-rate,
   shot-length and transition-duration claim in this slice (C1, C2, C5, C7, C11) is therefore
   **unvalidatable against this project's own footage**, not merely uncited. The archive
   cross-validation set (45 more files) does not change this.
6. **Also flagged though formally out of scope:** the hook-score weights at I:67
   (`motion*0.5 + color*0.3 + sharpness*0.2`, duplicated at S:264) are invented constants with no
   stated derivation, sitting inside ready-to-paste Python.

---

## 5. COVERAGE

All five assigned files read end to end (674 + 626 + 394 + 456 + 432 = 2582 lines). No file skipped,
no file truncated. Read-only throughout; nothing under `_archive/` was written, moved, or modified.
The dead symlink at `_archive/_p-ai-drone-video/_p-ai-drone-video` was not followed. No network
requests were made — **URL liveness is unverified by design and remains a user decision.** No image
or frame file was written.

Structured return carries the 60 highest-consequence numeric claims (of ~150 catalogued above),
prioritising first occurrences, hardened config values, and contradiction-bearing rows. The full
catalogue is this file.
