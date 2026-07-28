# Census 2 — Slice A: the two BENCHMARK documents

**Agent:** census2-bench-a · **Date:** 2026-07-28 · **Status:** COMPLETE (re-verified pass 3)

> **Pass-2 note.** Both source files were re-read end to end and every mechanical claim in
> this document was re-checked with `grep`. Six errors in the pass-1 text were found and
> corrected; three contradictions were **downgraded** because the adversarial re-check did not
> sustain them at pass-1 strength. All corrections are logged in **§7 Correction log**. Where a
> contradiction was weakened, the weakened form is what now appears in §3 — do not cite the
> pass-1 strength.
>
> <sub>**Dangling reference, flagged pass 3 (defect P3-7): §7 does not exist in this file.**
> `grep -nE "^#+ *7\."` returns nothing; the headings run …§6 Method note → §8 Pass-3 correction
> log. Pass 2 asserted six corrections and pointed at an audit trail it never wrote, so **the
> pass-2 corrections are unverifiable and their claimed count of six is unsupported.** Pass-3's
> own log (§8) is written and complete. Left in place rather than deleted because the broken
> promise is itself evidence about how much weight this checkpoint's self-reports carry.</sub>
>
> **Pass-3 note (2026-07-28, this session).** Both files re-read end to end a third time by an independent
> agent with no inherited context. Every URL count, absence grep and attribution sweep in §0
> **re-verified and confirmed exact**. **Six defects** were found in the pass-2 text and are
> fixed in place; all are logged in **§8 Pass-3 correction log**. The three most important:
> **(a) two citations were off by one line** (A27 `:143`→`:142`, A68 `:429`→`:428`) and the
> error had propagated into §3's C4, C5 and C6; **(b) §0's claim that "there is no fifth
> attribution construction in 1035 lines" is false** — `viral_drone_benchmark_2026.md:504`
> ("Research methodology: Web search analysis…") is a fifth, and the pass-2 grep could not have
> found it; **(c) eight claim rows were missed** (A77, B79–B85), which materially understated
> C9 — file B states a hook window **nine** times across **five** different values, two of them
> in the same sentence. Revised totals: **A 77 · B 85 · 162 total · 0 sourced**. The headline
> findings — zero point-of-use attribution, zero reference videos — are unchanged and now
> triple-verified.

## Scope and handling

Two files, read **end to end** (529 + 506 = 1035 lines, no sampling, no pruning):

| Key | Path | Dated (self-declared) | Lines |
|---|---|---|---|
| **A** | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/viral_drone_benchmark.md` | 2026-02-02 | 529 |
| **B** | `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/viral_drone_benchmark_2026.md` | 2026-02-08 | 506 |

Both are LLM-generated planning documents from the **archived** `_p-ai-drone-video` project.
They are **untrusted input**. Nothing below is asserted as true. Every row records what the
document *says* and what the document *credits it to* — the second column is the point of the
exercise. Read-only access; nothing under `_archive/` was written, moved, or deleted. No
network requests were made; URL liveness was not checked and is explicitly out of scope.

**Switch variables assumed:** `corpus-scope` = these 2 files only (not the wider archive);
`archive-write-mode` = read-only, reference by absolute path.

---

## 0. Provenance verdict (read this before any table)

**The sibling agents' corpus-wide pattern holds for these two files without a single
exception.**

Verified mechanically (`grep -n "http"`):

- **File A**: **12** distinct URLs (24 raw `http` occurrences — each is a markdown link whose
  label and target are both the URL), *all* on lines 490–514, *all* inside a trailing
  `## Research Sources` section (heading at :486) split into "Primary Sources" (6) and
  "Supporting Sources" (6). **Zero URLs appear anywhere in lines 1–489** — i.e. zero in the
  entire body that states the numbers.
- **File B**: **32** distinct URLs on 32 lines, *all* on lines 452–499, *all* inside a trailing
  `## Sources` section (heading at :449) split into **9** topical sub-headings (:451, :457,
  :463, :469, :475, :480, :485, :491, :496). **Zero URLs in lines 1–451.**

  <sub>Pass-1 stated "33 URLs" and "8 sub-headings". Both were wrong. Verified pass 2:
  `grep -oE "https?://[^ )\]]+" … | sort -u | wc -l` → 32; `grep -n "^### " … | awk -F: '$1>449'`
  → 9 headings.</sub>

**Not one number in either document is attached to a source at its point of use.** There is
no footnote marker, no superscript, no inline link, no "(source: …)" parenthetical, no
per-section source list. The topical grouping in B's source list (e.g. a "Color Grading &
Visual Trends" heading above four LUT-vendor blog URLs) creates the *appearance* of linkage
but binds no individual figure to any individual URL — a reader cannot determine which of the
four blogs, if any, produced "40-70%". Per the task's rule, that is **NONE**, and I record it
as NONE throughout.

The only **five** attribution-shaped strings in either document are (pass-1 said three and
omitted B:5; pass-2 said four and omitted B:504 — see §8):

| Cite | Text | Assessment |
|---|---|---|
| `viral_drone_benchmark.md:4` | "**Analysis Basis**: Analysis of viral drone content patterns, engagement metrics from **500+ viral reels**, and professional cinematography standards" | Vague. Names no analyst, no dataset, no date range. Grammatically it claims *first-party* analysis. |
| `viral_drone_benchmark.md:10` | "Based on comprehensive research of viral Instagram drone content in 2024-2025" | Vague. "Comprehensive research" credits nobody. |
| `viral_drone_benchmark_2026.md:5` | "**Sources:** **20+** articles, creator guides, and platform specifications" | A *count* of sources, in the front matter, with no mapping from any source to any claim. |
| `viral_drone_benchmark_2026.md:23` | "**Data:** Analysis of 500+ viral reels shows 7-15 second content achieves highest completion and shareability rates." | Vague. The "**Data:**" label is the strongest evidentiary signal in either file and it still names nobody. |
| `viral_drone_benchmark_2026.md:504` | "**Research methodology:** Web search analysis, platform documentation review, viral content pattern extraction" | **Added pass 3.** The only *methodology* statement in either file. It credits the entire document to "web search analysis" — i.e. it concedes there is no primary measurement behind any number, while naming no search, no query, no date, and no result. It is an anti-citation: it tells you the provenance floor without raising it. |

Established by exhaustive sweep, not by reading impression:
`grep -niE "research show\|studies\|according to\|source\|analysis of\|data:\|cited\|based on\|identified in\|survey"`
over both files returns 12 hits in A and 12 in B (**re-run and confirmed exact, pass 3**); every
hit outside the rows above is either a source-section heading, a URL in the bulk list, or an
unrelated use of "based on" (e.g. `A:303` "based on storytelling", `A:525` "based on real-world
results", `B:304` "based on shake scores").

<sub>**Pass-3 correction.** Pass 2 concluded from that sweep that "there is no fifth attribution
construction in 1035 lines." That conclusion was wrong, and wrong in an instructive way: the
sweep regex contains `research show`, which does **not** match `Research methodology` at B:504.
The sweep was treated as exhaustive when it was only exhaustive *over its own pattern list*.
B:504 was recovered by reading, not by grep. Recorded here because it is the same class of error
this registry exists to catch — a mechanical check mistaken for a complete one.</sub>

**Provenance inflation — the most important finding in this slice.** The "500+ viral reels"
figure is the sole quantitative evidence base cited for the single most consequential number
in both documents (7-15s optimal duration). It appears in both files (A:4, B:23) phrased as
the documents' own analysis. Both bulk source lists contain **CreatorsJet, "Best Reel Length
for Engagement (Based on 500 Viral Videos)"** (`A:494`, `B:467`) — a marketing blog post about
Instagram reel length *in general*, not drone content, and not a study. The near-certain
reading is that "500+ viral reels" is a restatement of that one blog's title, laundered into
first-party language at point of use. **Neither document says so.** Treating A:4/B:23 as
independent corroboration of B:23 would be double-counting one SEO blog post.

**Second-order provenance problem: B is not independent of A.** B was written 6 days after A,
in the same project, and reuses two of A's exact sources (socialpilot at A:506/B:452;
finchley at A:492/B:458; vloglikepro at A:490/B:459; creatorsjet at A:494/B:467). Where B
agrees with A, that agreement is **not** confirmation — it is very likely inheritance. Where B
*disagrees* with A (§3 below), the disagreement is the informative signal, and no reason for
any change is given anywhere in B.

**Confidence theatre.** `viral_drone_benchmark_2026.md:505` self-certifies
"**Confidence level:** High (20+ authoritative sources, consistent patterns across sources)".
This is asserted by the document about itself, is contradicted by §3 below (the sources are
not internally consistent, and B is not consistent with A six days earlier), and "authoritative"
is doing unearned work for a list containing four blog posts from a single LUT-preset vendor
(`aaapresets.com`, B:470–473) that has a commercial interest in the "apply LUTs at 40-70%"
claim those same lines are the only plausible support for.

**One genuine credit.** `viral_drone_benchmark_2026.md:31` — "**No specific BPM range
identified** in research" — is the only place in either document where a gap is *declared*
rather than filled with a plausible number. It is the correct behaviour and it is worth
noting precisely because it is unique across 1035 lines.

---

## 1. Numeric editorial claims — FILE A (`viral_drone_benchmark.md`, 2026-02-02)

Source column: what *the document itself* credits the number to at the point it is stated.

| # | Subject | Claim (verbatim value) | Cite | Credited to |
|---|---|---|---|---|
| A1 | other (evidence base) | "engagement metrics from 500+ viral reels" | :4 | NONE (self-described "Analysis Basis"; no analyst named) |
| A2 | hook_timing | hook = "jaw-dropping movement in first **1-2 seconds**" | :12 | NONE |
| A3 | total_duration | "**7-15 second** optimal length (highest completion rates)" | :13 | NONE |
| A4 | resolution | "**4K** resolution with cinematic color grading" | :15 | NONE |
| A5 | other (target score) | "Target Viral Benchmark: **85/100**" | :25 | NONE |
| A6 | retention | 85/100 "represents **top 10%** of performing drone content" | :25 | NONE — calibration claim with no stated method |
| A7 | other (rubric weight) | Hook Effectiveness weight **20/100** | :31 | NONE |
| A8 | hook_timing | "critical first **1-2 seconds**" | :33 | NONE |
| A9 | hook_timing | 60/100 tier: "movement visible in first **2 seconds**" | :46 | NONE |
| A10 | hook_timing | 80/100 tier: "Dramatic camera movement in first **1-2 seconds**" | :52 | NONE |
| A11 | detection_threshold | "First clip sharpness score **> 0.7**" | :67 | NONE |
| A12 | detection_threshold | "First clip motion energy **> 0.6**" | :68 | NONE |
| A13 | shot_length | "First clip duration **< 3 seconds**" | :69 | NONE |
| A14 | other (rubric weight) | Visual Sharpness weight **15/100** | :74 | NONE |
| A15 | resolution | "**4K** resolution standard (higher engagement/completion than **1080p**)" | :79 | NONE |
| A16 | other (quality) | 60/100: "soft focus or minor blur in **20-30%** of shots" | :89 | NONE |
| A17 | resolution | 60/100: "**1080p** quality level or soft 4K" | :90 | NONE |
| A18 | other (quality) | 80/100: "sharp focus across **90%+** of reel" | :96 | NONE |
| A19 | resolution | 80/100: "**4K** resolution with visible detail" | :97 | NONE |
| A20 | resolution | 100/100: "Crystal clear **4K** throughout entire reel" | :104 | NONE |
| A21 | framerate | "Cinematic motion blur … (**2x framerate** shutter rule)" | :108 | NONE |
| A22 | detection_threshold | "Average scene sharpness score **> 0.6** for 80/100" | :112 | NONE |
| A23 | detection_threshold | "Average scene sharpness score **> 0.75** for 100/100" | :113 | NONE |
| A24 | detection_threshold | "No clips with sharpness **< 0.4**" | :114 | NONE |
| A25 | detection_threshold | "Brightness variance within acceptable range (**0.3-0.7**)" | :115 | NONE |
| A26 | other (rubric weight) | Transition Quality weight **15/100** | :119 | NONE |
| A27 | other (beat align rate) | 80/100: "**70-80%** of transitions aligned with musical beats" | **:142** | NONE — *pass-3 fix: pass 2 cited :143, which is "Smooth execution with minimal jarring moments". Verified `grep -n "70-80%"` → 142.* |
| A28 | other (beat align rate) | 100/100: "Perfect beat sync (**95%+** cuts aligned)" | :149 | NONE |
| A29 | **transition_duration** | "Transition duration varies (**0.2s - 0.5s** range)" | :157 | NONE |
| A30 | other (variety) | "Transition types include **3+** varieties" | :158 | NONE |
| A31 | other (beat tolerance) | "Beat alignment accuracy **> 80%** (timing within **0.1s** of beat)" | :159 | NONE |
| A32 | transition_duration | "No transitions longer than **0.6s** unless intentional slow fade" | :160 | NONE |
| A33 | other (rubric weight) | Dynamic Movement weight **15/100** | :164 | NONE |
| A34 | other (variety) | 60/100: "**1-2** movement types dominate" | :180 | NONE |
| A35 | other (variety) | 80/100: "Mix of **3+** movement types" | :186 | NONE |
| A36 | other (motion coverage) | 80/100: "movement in **80%+** of reel" | :189 | NONE |
| A37 | other (variety) | 100/100: "**5+** movement types" | :194 | NONE |
| A38 | detection_threshold | "Average motion energy score **> 0.5** for 80/100" | :202 | NONE |
| A39 | detection_threshold | "Average motion energy score **> 0.7** for 100/100" | :203 | NONE |
| A40 | detection_threshold | "Motion energy variance **> 0.15**" | :204 | NONE |
| A41 | detection_threshold | "No clips with motion energy **< 0.3**" | :205 | NONE |
| A42 | other (rubric weight) | Clip Pacing weight **15/100** | :209 | NONE |
| A43 | total_duration | "Optimal reel length: **7-15 seconds** (highest completion rates)" | :214 | NONE |
| A44 | **shot_length** | "Clip duration: **1.5-4 seconds** per clip" | :215 | NONE |
| A45 | total_duration | 60/100: "Total reel length appropriate (**10-20 seconds**)" | :223 | NONE |
| A46 | shot_length | 60/100: "**3-5 second** average clip length (slightly slow)" | :225 | NONE |
| A47 | total_duration | 80/100: "**7-15 seconds** ideal range" | :231 | NONE |
| A48 | **shot_length** | 80/100: "clip duration variety (**1.5s - 4.5s** range)" | :232 | NONE |
| A49 | shot_length | 80/100: "Average clip length **2-3 seconds**" | :233 | NONE |
| A50 | shot_length | 80/100 ex.: "quick cuts (**1.5-2s**) and medium holds (**3-4s**)" | :236 | NONE |
| A51 | **total_duration** | 100/100: "Perfect total length (**7-12 seconds** for max completion)" | :239 | NONE |
| A52 | **shot_length** | 100/100: "clip variety (**1-5 second** range)" | :240 | NONE |
| A53 | shot_length | 100/100: "Rapid cuts during high-energy (**1-1.5s** clips on drops)" | :241 | NONE |
| A54 | shot_length | 100/100: "longer clips for impact (**3-4s** for money shot)" | :242 | NONE |
| A55 | total_duration | Impl. signal: "Total reel duration: **7-15 seconds**" | :248 | NONE |
| A56 | detection_threshold | "Clip duration standard deviation **> 0.5**" | :249 | NONE |
| A57 | shot_length | Impl. signal: "Average clip length: **2-3 seconds**" | :250 | NONE |
| A58 | other (rubric weight) | Color/Mood weight **10/100** | :255 | NONE |
| A59 | colour_grade | "Brightness balance appropriate (**0.4-0.6** for most scenes)" | :295 | NONE |
| A60 | other (rubric weight) | Overall Engagement weight **10/100** | :301 | NONE |
| A61 | retention | 80/100: "Good rewatchability (worth watching **2-3 times**)" | :327 | NONE |
| A62 | other (target breakdown) | 17/20, 12/15, 13/15, 13/15, 13/15, 9/10, 8/10 → **85/100** | :352-360 | NONE (arithmetic checks out: 17+12+13+13+13+9+8 = 85) |
| A63 | retention | Tier 1 (85-100): "Completion rate: **70-90%**" | :375 | NONE |
| A64 | retention | Tier 2 (70-84): "Completion rate: **50-70%**" | :388 | NONE |
| A65 | retention | Tier 3 (60-69): "Completion rate: **30-50%**" | :400 | NONE |
| A66 | retention | Tier 4 (<60): "Completion rate: **<30%**" | :411 | NONE |
| A67 | hook_timing | "Target **1-2 second** opening with dramatic movement" | :423 | NONE |
| A68 | other (beat align rate) | "Align **90%+** of transitions within **0.1s** of beat" | **:428** | NONE — *pass-3 fix: pass 2 cited :429, which is "Match cut energy to music energy". Verified `grep -n "90%+"` → 96, 428.* |
| A69 | total_duration | "Target **7-15 second** total duration" | :434 | NONE |
| A70 | total_duration | "Avoid reels longer than **20 seconds**" | :435 | NONE |
| A71 | shot_length | "Aim for **2-3 second** average clip length" | :436 | NONE |
| A72 | detection_threshold | "Reject clips with sharpness score **< 0.5**" | :439 | NONE |
| A73 | resolution | "Prioritize **4K** source footage" | :441 | NONE |
| A74 | detection_threshold | "Ensure **80%+** of clips have motion energy **> 0.5**" | :445 | NONE |
| A75 | other (variety) | "no more than **40%** same movement style" | :446 | NONE |
| A76 | other (code default) | `'viral_ready': total_score >= 85` | :480 | NONE — the score threshold, hardcoded |
| **A77** | retention (calibration) | Tier 1 characteristics: "**Top 10%** of drone content, high completion rates" | **:367** | NONE — **added pass 3.** Second, independent statement of the top-10% calibration (A6 is the first, at :25). Missed by passes 1–2. Matters because C18 turns on this claim and pass 2 anchored C18 to a single line; it is stated twice. |

**File A subtotal: 77 claims (76 at pass 2, +A77 at pass 3). Credited to a named source: 0.**

**Counting caveat (added pass 2).** 10 of A's 77 rows are rubric-scheme numbers rather than
properties of the output video: the seven category weights (A7, A14, A26, A33, A42, A58, A60),
the 85/100 target (A5), its arithmetic breakdown (A62), and the `>= 85` code threshold (A76).
A strict reading of the task's exclusion list ("task priority or complexity scores") would drop
these, giving **A = 67 strictly-editorial claims**. They are retained in the table because they
are inheritable constants that a scoring module would lift verbatim, and because A5/A6/A76 form
the calibration claim examined in C18. **Either way the sourced count is 0.**

File A states **no aspect ratio, no framerate target, no bitrate, no BPM, no LUT/grade
intensity, and no saturation/contrast delta anywhere.** Verified pass 2 by targeted absence
greps: `9:16|aspect|vertical|1080x1920|portrait` → **0 hits**; `bitrate|kbps|mbps|codec|h\.264`
→ **0 hits**; `bpm|tempo` → **0 hits**; `fps|frame ?rate` → **exactly 1 hit**, A:108's "2x
framerate shutter rule" (a shooting rule, not an output spec); `lut|intensity|saturat` → 9 hits,
**none carrying a number** (A:282 "LUT applied consistently", A:297 "Saturation boost applied",
A:288 "not oversaturated"). Its colour section (:255–298) is entirely qualitative with the
single exception of the brightness-balance range A59. **These absences are load-bearing for §3
(C7, C11, C12, C13) and are now confirmed by exhaustive grep, not by reading impression.**

---

## 2. Numeric editorial claims — FILE B (`viral_drone_benchmark_2026.md`, 2026-02-08)

| # | Subject | Claim (verbatim value) | Cite | Credited to |
|---|---|---|---|---|
| B1 | other (evidence base) | "Sources: **20+** articles, creator guides, and platform specifications" | :5 | NONE (count only; no mapping) |
| B2 | total_duration | "**7-15 second** clips" (exec summary) | :11 | NONE |
| B3 | hook_timing | "jaw-dropping hooks in the first **2-3 seconds**" | :11 | NONE |
| B4 | letterbox_aspect + resolution | "**9:16** vertical framing at **1080x1920px**" | :11 | NONE |
| B5 | **colour_grade** | colour trends "at **40-70% intensity**" | :11 | NONE |
| B6 | total_duration | "Optimal total duration: **7-15 seconds** (highest completion rate)" | :18 | NONE |
| B7 | total_duration | "Maximum for viral potential: **30 seconds**" | :19 | NONE |
| B8 | **shot_length** | "Individual shot duration: **1.5-3 seconds** per clip" | :20 | NONE |
| B9 | total_duration | "Up to **3 minutes** allowed, but **>90 seconds** excluded from Discovery" | :21 | NONE (platform spec, stated bare) |
| B10 | total_duration | "Analysis of **500+** viral reels shows **7-15 second** content achieves highest completion" | :23 | NONE — "**Data:**" label, no analyst. See §0. |
| B11 | total_duration | "Beauty/fashion … best at **6-12 seconds**; lifestyle peaks at **15-25 seconds**" | :23 | NONE — and neither vertical is drone content |
| B12 | **cut_rate** | "Target: **4-8 clips** in a **15-second** reel (**1.9-3.8s** average)" | :28 | NONE |
| B13 | audio_bpm | "**No specific BPM range identified** in research" | :31 | NONE — declared gap (see §0, the one honest line) |
| B14 | other (engagement) | "Trending audio (**42%** higher engagement)" | :32 | NONE |
| B15 | **transition_duration** | "Use **0.3-0.5 second** transition durations" | :44 | NONE ("**Technical note:**" label, no source) |
| B16 | **colour_grade** | "Apply LUTs at **40-70% intensity**" | :58 | NONE |
| B17 | speed_ramp | "**60fps** source for smooth slow-motion (**2x** slowdown max without optical flow)" | :71 | NONE |
| B18 | speed_ramp | "Optical flow for **3-4x** slowdown" | :72 | NONE |
| B19 | **letterbox_aspect** | "Aspect ratio: **9:16** (**1080x1920px**) mandatory" | :81 | NONE |
| B20 | text_overlay | "Frame subject in upper **2/3** for caption space" | :82 | NONE |
| B21 | letterbox_aspect | "**9:16** primary, **4:5** feed preview, **1:1** grid" | :84 | NONE |
| B22 | **retention** | "First **2 seconds**: **50%** viewer drop-off point" | :91 | NONE |
| B23 | hook_timing | "First **3 seconds**: Algorithm evaluation window" | :92 | NONE |
| B24 | hook_timing | "First **5 seconds**: **30%** more algorithmic weight in 2026" | :93 | NONE |
| B25 | **retention** | "Reels with strong hooks: **45%** higher watch-through rate" | :113 | NONE ("**Benchmarks:**" label, no source) |
| B26 | cut_rate | "First **3-second** jump cuts: **72%** more likely to go viral" | :114 | NONE |
| B27 | **other (beat tolerance)** | "Cuts must align within **100-200ms** of beat" | :128 | NONE |
| B28 | other (beat tolerance) | "Align clip boundaries to beat times **±0.15s**" | :141 | NONE |
| B29 | other (musical structure) | "Respect **4-bar** and **8-bar** musical structure" | :143 | NONE |
| B30 | other (shot mix) | "Long shots: **20-30%**" | :175 | NONE — labelled "Classical Grammar" |
| B31 | other (shot mix) | "Medium shots: **40-50%**" | :176 | NONE |
| B32 | other (shot mix) | "Close-ups: **20-30%**" | :177 | NONE |
| B33 | resolution + framerate | "Minimum: **720p @ 30fps**" | :196 | NONE |
| B34 | **resolution** | "Recommended: **1080x1920px @ 30fps**" | :197 | NONE |
| B35 | resolution | "Premium: **4K** source downscaled to **1080p**" | :198 | NONE |
| B36 | framerate | "High action: **60fps**" | :199 | NONE |
| B37 | letterbox_aspect | "Primary **9:16** / Feed **4:5** / Grid **1:1**" | :202-204 | NONE |
| B38 | **bitrate** | "**High bitrate** (reduce upload blur)" | :212 | NONE — **and no number given** |
| B39 | bitrate (audio) | "**128 kbps** minimum", "**44.1kHz or 48kHz**" | :219-220 | NONE |
| B40 | framerate | "**30fps** standard / **60fps** action / **24fps** cinematic" | :223-225 | NONE |
| B41 | total_duration | "Max duration: **3 minutes** (**90s** for Discovery eligibility)" | :228 | NONE |
| B42 | text_overlay | "captions (up to **2,200** characters)" | :234 | NONE |
| B43 | other (posting) | "**3-5** Reels per week (sweet spot)" | :249 | NONE |
| B44 | other (growth) | "Regular posting (**25%** faster follower growth)" | :251 | NONE |
| B45 | other (posting time) | "**7-9 AM**", "**11 AM-1 PM**" | :255-256 | NONE |
| B46 | other (engagement) | "Trending audio: **42%**" / hooks: **45%** / jump cuts: **72%** | :259-261 | NONE — verbatim restatement of B14/B25/B26 |
| B47 | total_duration | "Reels **>90s** excluded from Discovery" | :267 | NONE |
| B48 | total_duration | Comparison table: current **15-60s** vs benchmark **7-15s** | :278 | NONE |
| B49 | **shot_length** | Comparison table: current **2-4s** vs benchmark **1.5-3s** — marked "✅ ALIGNED" | :279 | NONE |
| B50 | **transition_duration** | Comparison table: current **0.3s default** vs **0.3-0.5s** — marked "✅ **OPTIMAL**" | :280 | NONE |
| B51 | letterbox_aspect | Comparison table: **9:16** vs **9:16** required — "✅ CORRECT" | :281 | NONE |
| B52 | **resolution** | Comparison table: current **1080p default, 4K option** vs benchmark "**1080p standard**" — "✅ CORRECT" | :282 | NONE |
| B53 | framerate | Comparison table: **30fps** vs **30fps** — "✅ CORRECT" | :283 | NONE |
| B54 | hook_timing | Comparison table: "First **2-3s** critical" | :285 | NONE |
| B55 | **colour_grade** | Gap: "Tool applies full-strength grading; viral content uses **40-70%**" | :293 | NONE |
| B56 | **colour_grade** | `--color-intensity 0.5  # Apply grading at 50% (viral sweet spot: 40-70%)` | :317 | NONE — **range → point collapse, in code** |
| B57 | speed_ramp | `--ramp-intensity 0.7  # Control ramp aggression` | :331 | NONE — number appears here and nowhere else |
| B58 | total_duration | `--preset viral-short  # 7-15s` | :352 | NONE |
| B59 | total_duration | `--preset viral-medium  # 15-30s` | :353 | NONE |
| B60 | transition_duration | `--transition-mix "zoom:0.4,blur:0.3,flare:0.2,cut:0.1"` | :368 | NONE — weights sum to 1.0; otherwise unmotivated |
| B61 | **retention** | "Completion rate (aim **>60%**)" | :391 | NONE |
| B62 | other (engagement) | "Engagement rate (likes/views **>5%**)" | :392 | NONE |
| B63 | retention | "Watch time (aim **80%+** of duration)" | :393 | NONE |
| B64 | total_duration | A/B test: "**7-15s** vs **30s** duration" | :395 | NONE |
| B65 | colour_grade | A/B test: "Color intensity **50%** vs **100%**" | :397 | NONE |
| B66 | other (beat tolerance) | "Beat sync precision (**±150ms** tolerance)" | :402 | NONE |
| B67 | total_duration | Recap: optimal **7-15s** / max **30s** / cutoff **90s** | :412-414 | NONE |
| B68 | shot_length | Recap: "Clip duration: **1.5-3 seconds**" | :415 | NONE |
| B69 | transition_duration | Recap: "Transition duration: **0.3-0.5 seconds**" | :416 | NONE |
| B70 | retention | Recap: "Completion rate target: **60%+**"; "First 3s retention: **50%+**" | :419-420 | NONE |
| B71 | other (engagement) | Recap: **+42%**, **+45%**, **+72%** | :421-423 | NONE |
| B72 | resolution + framerate | Recap: "**1080x1920px (9:16)**", "**30fps** standard, **60fps** action" | :426-427 | NONE |
| B73 | **bitrate** | Recap: "Bitrate: **High** (minimize compression)" | :428 | NONE — again no number |
| B74 | **colour_grade** | Recap: "LUT intensity: **40-70%** (not 100%)" | :432 | NONE |
| B75 | **saturation** | Recap: "Saturation boost: **Moderate**" | :433 | NONE — no number |
| B76 | **contrast** | Recap: "Contrast: **High** for cinematic look" | :434 | NONE — no number |
| B77 | other (beat tolerance) | Recap: "Sync tolerance: **±100-200ms**" | :437 | NONE |
| B78 | other (posting) | Recap: **3-5**/week; **7-9 AM**, **11 AM-1 PM**; **+25%** growth | :443-445 | NONE |

**Rows B79–B85 added pass 3** — all missed by passes 1 and 2, all in the hook/text-timing
cluster. Recovered by re-reading plus `grep -niE "first [0-9]|first frame|in first"`. Their
omission mattered: pass 2's C9 (hook-window drift) was argued from four B cites when B in fact
states a hook or early-retention window **nine** times, across five different values.

| # | Subject | Claim (verbatim value) | Cite | Credited to |
|---|---|---|---|---|
| **B79** | hook_timing | "**early engagement** (first **3-5 seconds** critical)" | :11 | NONE — a *fifth* hook window, in the same sentence as B3's "first 2-3 seconds". Two different windows, one sentence. |
| **B80** | text_overlay | "**On-screen text** in **first frame** (combined with voiceover)" | :106 | NONE — ordinal, not numeric; logged because text-overlay timing is in scope and this is the only placement rule B gives. |
| **B81** | hook_timing | "**Hook first** (most dramatic shot in first **2 seconds**)" | :150 | NONE |
| **B82** | hook_timing | "First **3 seconds:** Algorithm evaluation window" (restated) | :244 | NONE — verbatim duplicate of B23 (:92). |
| **B83** | other (engagement timing) | "Early engagement: Likes/comments in **first hour** critical" | :246 | NONE — viewer-behaviour timing claim; the only one on an hours scale in either file. |
| **B84** | hook_timing / retention | "Hook effectiveness (retention in first **3s**)" | :401 | NONE |
| **B85** | text_overlay / thumbnail | "**Thumbnail:** **First frame** serves as preview in grid" | :236 | NONE — ordinal, not numeric; logged for the same reason as B80. |

**File B subtotal: 85 claims (78 at pass 2, +7 at pass 3). Credited to a named source: 0.**

**Combined: 162 numeric editorial claims (154 at pass 2, +8 at pass 3). 0 with a resolvable
named source at point of use.** The sourced count did not move, and has not moved across three
independent passes.

---

## 3. A-vs-B contradictions — the line-by-line hunt

The two files were written **6 days apart** on the **same subject** by the same project. Any
divergence is a change of position with **no stated reason anywhere in either document**. B
never mentions A, never says it supersedes A, and never explains a single revised number.

**Strength labels (added pass 2).** Each contradiction now carries a label, because pass 1
stated several at a strength the evidence does not support:
- **HARD** — the two texts cannot both be followed. 8 of 18.
- **TIERED** — the values differ but are scoped to different quality tiers, so differing is
  *intended*; the defect is only where a tier-scoped number collides with an unscoped
  directive. 2 of 18.
- **SOFT / DOWNGRADED** — pass 1 overstated this; the weakened form is what stands. 3 of 18
  (**C4, C6, C10**).
- **ABSENCE** — one file is silent where the other is prescriptive. 3 of 18.
- **INTERNAL** — a file contradicts itself. 2 of 18.

### C1 — Delivery resolution: 4K (A) vs 1080p (B). Highest consequence.
- **A** makes 4K the viral-quality bar for the *finished reel*: ":15 4K resolution with
  cinematic color grading"; ":79 4K resolution standard (higher engagement/completion than
  1080p)"; ":104 **Crystal clear 4K throughout entire reel**" is literally the 100/100
  criterion; ":90 1080p quality level" is scored **60/100 — Acceptable**; ":441 Prioritize 4K
  source footage".
- **B** makes 1080p the *correct* delivery spec and 4K merely a source format: ":197
  Recommended: 1080x1920px"; ":198 Premium: 4K source **downscaled to 1080p**"; ":282
  Resolution — current "1080p default, 4K option" vs viral benchmark "**1080p standard**" —
  **✅ CORRECT**".
- **The collision:** B stamps "✅ CORRECT" on exactly the configuration A scores at 60/100.
  A pipeline built from A renders 4K; a pipeline built from B renders 1080p and reports
  compliance. Both cite nothing.

### C2 — Per-shot duration: eight different ranges across two files. **[TIERED + HARD]**
| Value | Where | Context |
|---|---|---|
| 1.5–4s | A:215 | "Clip duration … per clip" (the headline pacing rule) |
| 3–5s avg | A:225 | 60/100 tier |
| 1.5–4.5s | A:232 | 80/100 tier |
| 2–3s avg | A:233, A:250, A:436 | 80/100 tier + impl. signal + recommendation |
| 1–5s | A:240 | 100/100 tier |
| 1–1.5s | A:241 | high-energy cuts |
| **1.5–3s** | **B:20, B:68/415, B:279** | B's headline rule |
| **1.9–3.8s** | **B:28** | derived from "4-8 clips in a 15-second reel" |
**Corrected pass 2 — pass 1 called all eight "mutually incompatible"; that is not fair to three
of them.** A:225 (3-5s), A:232 (1.5-4.5s) and A:240 (1-5s) are scoped to the 60 / 80 / 100 tiers
respectively, so they are *supposed* to differ. Strip those and the genuine defect is sharper,
not weaker:

- **HARD, within A:** the unscoped headline rule **A:215 "1.5-4 seconds per clip"** vs the
  unscoped Implementation Signal **A:250 "Average clip length: 2-3 seconds"** vs the unscoped
  recommendation **A:436 "Aim for 2-3 second average"**. A pipeline author has two different
  unscoped answers in one file. (2-3 sits inside 1.5-4, so this is a narrowing without notice
  rather than a flat collision — but it is the number that gets coded.)
- **HARD, across files:** A's unscoped **1.5-4s** vs B's unscoped **1.5-3s** (B:20, B:68/415,
  B:279). The ceiling moves 4 → 3 in six days, unexplained.
- **HARD, within B:** B:20's 1.5s floor vs B:28's 1.9s floor, derived on the same page.
- **The verdict column is decorative — this part stands unchanged.** **B:279 marks the tool's
  existing 2-4s setting "✅ ALIGNED" against B's own 1.5-3s benchmark, and 4s is outside
  1.5-3s.** B stamps a pass on a setting that fails its own stated range. Same failure as C3
  and C16.

### C3 — Transition duration: 0.2-0.5s (A) vs 0.3-0.5s (B), then collapsed to 0.3s.
- **A:157** "Transition duration varies (**0.2s - 0.5s** range)"; **A:160** "No transitions
  longer than **0.6s**".
- **B:44** "Use **0.3-0.5 second** transition durations"; restated **B:416**.
- **B:280** the tool's "**0.3s default**" is compared to "0.3-0.5s recommended" and stamped
  "**✅ OPTIMAL**".
- **This is the documented failure pattern, caught mid-flight.** The floor silently moves
  0.2 → 0.3 between files with no reason. Then a *point value sitting exactly on the bottom
  edge of the range* is declared "OPTIMAL" — not "acceptable", not "in range". A reader
  inheriting this reads "0.3s is the optimum", which neither file's range actually says. A's
  0.2s floor and 0.6s ceiling are erased entirely.

### C4 — Beat-sync philosophy: A optimises for what B calls a defect.
- **A** rewards maximal beat alignment: ":142 70-80% aligned" = 80/100; ":149 "**Perfect beat
  synchronization (95%+ cuts aligned)**" = 100/100; ":428 "Align **90%+** of transitions".
  *(pass-3 fix: both cites were off by one — :143 → :142, :429 → :428. Values unchanged; the
  contradiction stands at full strength.)*
- **B** explicitly rejects it: ":124 "**Avoid:** Cutting on every single beat (creates
  frenetic, exhausting pacing)"; ":122 sync to downbeats only; ":297 lists "**Beat sync to
  all beats**" as a **critical gap** requiring a "downbeat-only mode"; ":344 proposes
  `--beat-sync downbeat` to replace the "all" default.
- **The collision:** A's 100/100 score is B's P2 bug ticket. Six days, no explanation.

### C5 — Beat-sync tolerance: A is 2x stricter, and B collapses a range to a point.
- **A:159** "within **0.1s** of beat"; **A:428** "within **0.1s**" (=100ms). *(pass-3 fix: :429 → :428)*
- **B:128** "**100-200ms**"; **B:141** "**±0.15s**"; **B:402** "**±150ms**"; **B:437**
  "**±100-200ms**".
- Within B alone, "100-200ms" becomes "±0.15s" becomes "±150ms" — **a range collapsing to its
  midpoint with no reason given**, the same failure shape as C3 and C7. Across files, A's
  100ms is the *tightest edge* of B's range presented as B's whole answer would be 150ms —
  a 50% loosening.

### C6 — Beat-alignment *rate*: four different numbers inside file A alone.
70-80% (A:142) · 95%+ (A:149) · >80% (A:159) · 90%+ (A:428). *(pass-3 fix: :143 → :142,
:429 → :428.)* A:159 is the stated "Implementation Signal" for the section (>80%) yet A:428's
"Immediate Priorities … (Critical)" says 90%+. A pipeline author reading A top-to-bottom gets a
different constant depending on which section they stop at. B states no rate at all.

### C7 — LUT / grade intensity: A has no number; B invents 40-70% and ships 0.5.
- **A** quantifies nothing about grading strength. Its colour section is qualitative
  throughout (":288 Vibrant but natural (not oversaturated/HDR-look)"; ":297 Saturation boost
  applied"; ":443 Apply consistent color grading preset"). The **only** colour number in A is
  ":295 Brightness balance … 0.4-0.6".
- **B** introduces "**40-70%**" **five** times — :11, :58, :293, :432, and inside the code
  comment at :317 — and at that same :317 writes
  **`--color-intensity 0.5  # Apply grading at 50% (viral sweet spot: 40-70%)`**.
  *(pass-3 fix: pass 2 said "three times" while listing four cites and omitting the :317
  occurrence. Verified `grep -n "40-70%"` → 11, 58, 293, 317, 432.)*
- **Range → point → code default, in a single file, with the range still visible in the
  comment.** 0.5 is not the midpoint of 40-70% (55% is); nothing explains the choice of 0.5.
  :397 then hardens it further into an A/B plan ("Color intensity 50% vs 100%"), treating 50%
  as *the* candidate.
- **Cross-check against the sibling agents' finding:** they recorded a "50-70% → 60% →
  intensity=0.6" chain elsewhere in the corpus. **This file gives a different range (40-70%)
  and a different point value (0.5) for the same parameter.** So the corpus contains at least
  two incompatible LUT-intensity lineages, each sourceless, each already collapsed to a
  different code default. Any downstream consumer inherits whichever file it read.

### C8 — Total duration: A caps at 20s, B allows 30s; and A's own optimum is unstable.
- **A**: 7-15s (:13, :214, :231, :248, :434) but **7-12s** for the 100/100 tier (:239), and
  **10-20s** described as "appropriate" at 60/100 (:223), with ":435 Avoid reels longer than
  **20 seconds**".
- **B**: 7-15s optimal (:18) but "**Maximum for viral potential: 30 seconds**" (:19),
  `--preset viral-medium # 15-30s` (:353), and the A/B plan "7-15s vs **30s**" (:397).
- A's hard ceiling (20s) is 10s below B's (30s). A's viral-quality optimum (7-12s) is
  narrower than the 7-15s figure both files headline. **The 7-15s number is the single most
  repeated figure across both documents — 13 occurrences (A: :13, :214, :231, :248, :434; B:
  :11, :18, :23, :278, :352, :395, :412, :419) — and A's own top-tier criterion contradicts
  it.** *(pass-3 fix: pass 2 said 9; `grep -c "7-15"` → 5 in A, 8 in B.)*

### C9 — Hook window: A says 1-2s; B says five different things, twice in one sentence. **[HARD + INTERNAL]**
- **A**: "first **1-2 seconds**" (:12, :33, :52, :423); "first **2 seconds**" (:31 heading,
  :46); first clip "< **3 seconds**" (:69).
- **B** (list corrected and extended pass 3 — B states a hook / early-retention window **nine**
  times, not four): "first **2-3 seconds**" (:11) **and "first 3-5 seconds critical" in the same
  sentence** (:11, B79); section titled "First **1-3** Seconds" (:88); "First **2 seconds**: 50%
  drop-off" (:91); "First **3 seconds**: Algorithm evaluation window" (:92); "First **5
  seconds**: **30%** more algorithmic weight" (:93); "first **2 seconds**" (:150, B81); "First
  **3 seconds**" restated (:244, B82); "First **2-3s** critical" (:285); "retention in first
  **3s**" (:401, B84); "First **3s** retention" (:420).
- **Five distinct values — 1-3, 2, 2-3, 3, 3-5, 5 — and the widest and one of the narrowest sit
  in the same sentence at :11.** The window widens across the 6 days from A's 1-2s, with no
  reason given, and B does not converge internally either. B's :93 "30% more algorithmic weight
  in 2026" is a precise-sounding percentage attached to an unfalsifiable mechanism, credited to
  nothing.

### C10 — Completion rate: B's "viral" target is A's second tier.
- **A:375** Tier 1 "Viral-Ready" (85-100) expects **70-90%** completion. **A:388** Tier 2
  "Strong Performer" expects **50-70%**.
- **B:391/419** "Completion rate target: **60%+**"; **B:393** "Watch time (aim **80%+** of
  duration)".
- **60% falls inside A's Tier-2 band (50-70%), not Tier 1.** B labels as the viral target what
  A classifies as a non-viral strong performer. Separately, B's own two numbers (60%+
  completion, 80%+ watch time) are in tension with each other for a 7-15s reel.

### C11 — Aspect ratio: A is completely silent; B calls 9:16 "mandatory".
A never states an aspect ratio in 529 lines. B states 9:16 / 1080x1920 as mandatory five
times (:11, :81, :84, :202, :281). Not a numeric contradiction — an **absence** contradiction,
and the more dangerous kind: a consumer reading only A has no framing constraint at all.

### C12 — Framerate: A gives none; B gives 30/60/24.
A's only framerate-adjacent statement is the "**2x framerate** shutter rule" (:108), which is
a shooting rule, not an output spec. B specifies 30fps standard / 60fps action / 24fps
cinematic (:196-199, :223-225, :283, :428).

### C13 — Bitrate: the one spec B refuses to quantify.
**B:212** "**High bitrate** (reduce upload blur)" and **B:428** "Bitrate: **High** (minimize
compression)". In a section (`## 6. Technical Specifications`) and a recap
(`### Technical Specs`) that put exact numbers on resolution, fps, audio kbps and sample rate,
bitrate alone gets an adjective. A states no bitrate at all. **There is no inheritable bitrate
number anywhere in either benchmark document** — anyone implementing from these files must
invent one, which is precisely the "invented constant" failure this registry exists to
prevent. Same applies to **B:433 Saturation boost: "Moderate"** and **B:434 Contrast: "High"**
— named as benchmark parameters, quantified nowhere.

### C14 — Internal to A: sharpness reject floor is 0.4 in one section, 0.5 in another.
**A:114** "No clips with sharpness **< 0.4**" (Implementation Signals, §2) vs **A:439**
"**Reject** clips with sharpness score **< 0.5**" (Implementation Recommendations). Both are
directives to the same filter. 25% apart.

### C15 — Internal to B: shot-count arithmetic contradicts the shot-duration rule.
**B:28** "4-8 clips in a 15-second reel (1.9-3.8s average)" vs **B:20** "1.5-3 seconds per
clip". At 1.5s/clip a 15s reel holds 10 clips, not 8; at 3s/clip it holds 5. The stated
"4-8 clips" band and the stated "1.5-3s" band are inconsistent, and the parenthetical
"1.9-3.8s" is a *third* range derived from the first without reconciling the second.

### C16 — Internal to B: "8 types" of transition, 5 listed.
**B:288** "Transitions | **8 types** (CUT, CROSSFADE, FADE, ZOOM, SLIDE)" — five names in a
list labelled eight, in a table row stamped "✅ ALIGNED". Not an editorial number, logged
because it demonstrates the comparison table's verdict column is not checked against its own
cells (see also C2, C3).

### C17 — Unsupported classical-grammar shot mix applied to aerial footage.
**B:175-177** "Long shots 20-30% / Medium shots 40-50% / Close-ups 20-30%", labelled
"(Classical Grammar)". These categories are defined by *subject scale relative to a human
figure* and have no established meaning for aerial drone footage, which is long-shot by
construction. The document neither justifies the transfer nor sources the percentages, and A
has no analogue. Worth flagging because the percentages sum to a tidy 100% at their midpoints
(25/45/25 ≈ 95%) and look computed.

### C18 — A's "top 10%" calibration.
**A:25** "Target Viral Benchmark: **85/100** (represents **top 10%** of performing drone
content)", restated at **A:367** "Top 10% of drone content" (row A77, added pass 3 — the claim
is made **twice**, not once). For either to be true, the 85-point rubric — which A itself
invented on the same page — would need to have been scored against a distribution of real drone
content. **A:520-526 admits the opposite**: "This rubric **should be validated against actual
output reels**" and "Next Review: After **10+ test reels** scored". The calibration claim is
made in the executive summary, repeated in the performance-tier table, and retracted in the
appendix of the same file.

---

## 4. Reference videos and exemplar creators

**Count: 0.** Applying the strict test, neither file contains a single specific identifiable
third-party video, and neither holds up a named creator as an exemplar.

**Mechanically confirmed pass 3** — not merely by reading impression:

- `grep -niE "tiktok\.com|youtube|youtu\.be|instagram\.com|vimeo"` over both files → **0 hits.**
  There is no link to a video-hosting platform anywhere in 1035 lines. Every one of the 44 URLs
  (12 in A, 32 in B) points to a written article.
- `grep -n "@"` over both files, excluding the three resolution/framerate strings (`720p @ 30fps`,
  `1080x1920px @ 30fps`, `4K source`) → **0 hits.** No social handle of any kind appears. The
  four handles the sibling agents found corpus-wide (@thedronecreative, @beverlyhillsaerials,
  @basso2012, @simeonpratt) are **not** in these files.

Everything that superficially resembles a reference video, and why it fails:

| Candidate | Cite | Why it does not count |
|---|---|---|
| "7 Stunning Drone Videos to Inspire Your Next Adventure in 2026" | `viral_drone_benchmark_2026.md:460` | SEO listicle on a commercial drone-services site. **No video is named** in the benchmark document; the doc never says which 7, never links one, never describes one. Exactly the excluded case. |
| "51 Viral Reel Hooks To Stop The Scroll (with 2026 Examples)" | `viral_drone_benchmark_2026.md:465` | **Added pass 3.** Second title in B promising "examples". Same failure as the row above: the benchmark document names, links and describes **none** of them. Two of B's 32 sources advertise examples in their titles and B inherits zero. |
| Oscar Liang | `viral_drone_benchmark.md:498` | The only named individual in either file. Appears **as the author of a cited colour-grading tutorial**, in the bulk source list, not as a creator whose *work* is held up as a target. No video of his is referenced. Fails the exemplar test. |
| VlogLikePro, Finchley Studio, CreatorsJet, Pixflow, Dronegenuity, Autelpilot, Social Pilot, Cropink, HeyOrca, Studiovity, Drone U | `viral_drone_benchmark.md:490-514` | Blog/brand publishers of written articles. Not creators presented as exemplars; not videos. |
| DJI Mini / DJI Air / DJI Inspire / GoPro | `viral_drone_benchmark.md:101, :109` | **Equipment**, cited as a quality proxy ("Cinema-grade drone (DJI Inspire, FPV with GoPro 4K)"). Not creators, not videos. |
| CapCut, OpusClip, Librosa, Premiere Pro | `viral_drone_benchmark_2026.md:129, :140, :483` | Tools. |
| aaapresets.com (4 LUT articles) | `viral_drone_benchmark_2026.md:470-473` | Vendor blog posts. Also a **conflict-of-interest flag**: the only plausible support for the 40-70% LUT-intensity claim (C7) is four articles by a company that sells LUTs. |

**Consistent with the sibling agents' corpus-wide result (exactly one specific third-party
video across 233 URL occurrences, in `research_transitions.md:862`).** Neither of these two
files contains it, and neither contains any other. Note the significance: these are the
corpus's *benchmark* documents — the ones whose entire purpose is to state what "good" looks
like — and they benchmark against **zero examples of good**. Every target number is asserted
against written prose about video, never against video.

No Instagram handles appear in either file (the four handles the sibling agents found are
elsewhere in the corpus, not here).

---

## 5. Inheritance risk — what a downstream implementer would actually pick up

Ranked by consequence if silently adopted as a code default:

1. **`transition_duration = 0.3`** — B:280 stamps the point value "✅ OPTIMAL" against a
   0.3-0.5s range, while A:157 says the range starts at 0.2s. Already in code-comparison form;
   one copy-paste from being a constant.
2. **`color_intensity = 0.5`** — B:317, already written as a CLI flag with the range in the
   comment. A gives no intensity number at all. Corpus contains a rival 0.6 lineage.
3. **`resolution = 1080p` vs `4K`** — flatly contradictory between files (C1); B marks
   1080p "CORRECT", A scores it 60/100.
4. **`total_duration ∈ [7,15]`** — the most-repeated number in the slice (**13** occurrences,
   corrected pass 3) and contradicted by A's own 100/100 criterion (7-12s) and by B's 30s
   ceiling. Repetition is the *only* thing supporting it; it traces to no measurement, and its
   sole named evidence base ("500+ viral reels") is the title of one SEO blog post about
   Instagram reels in general — see §0.
5. **`shot_length`** — eight incompatible ranges (C2). No defensible single value exists in
   these files.
6. **`beat_tolerance = 150ms`** — B:402, a midpoint collapse of B:128's 100-200ms; A says
   100ms.
7. **Scene-filter thresholds** (A:11-12, A:22-25, A:38-41, A:56, A:72, A:74) — sharpness 0.4/
   0.5/0.6/0.7/0.75, motion energy 0.3/0.5/0.6/0.7, variance 0.15, brightness 0.3-0.7 and
   0.4-0.6. **Fifteen unit-interval thresholds, every one sourceless, and two of them (0.4 vs
   0.5 sharpness reject) mutually inconsistent.** These are the numbers most likely to be
   lifted wholesale into a scoring module because they already look like code.
8. **No inheritable bitrate, saturation delta or contrast delta exists** (C13) — anything a
   downstream doc states for these did not come from here.

---

## 6. Method note

- Both files read in full via `Read` (no offset/limit, no truncation) on **three** separate
  passes, the third by an agent with no inherited context.
- URL positions established mechanically: `grep -n "http"` plus
  `grep -oE "https?://[^ )\]]+" | sort -u | wc -l` on both — results in §0, re-run pass 3 and
  confirmed exact (A: 12 distinct / 24 raw occurrences / lines 490–514; B: 32 distinct / 32
  lines / lines 452–499 / 9 sub-headings).
- Attribution language swept with
  `grep -niE "research show|studies|according to|source|analysis of|data:|cited|based on|identified in|survey"`
  on both files (12 hits each). **The sweep is exhaustive over its own pattern list, not over the
  files** — B:504 was found by reading, not grep. Body-level attribution constructions: the
  **five** rows in §0.
- File A's absences re-confirmed pass 3 by targeted greps: aspect/9:16/vertical/portrait → **0
  hits**; bitrate/kbps/mbps/codec/h.264 → **0 hits**; bpm/tempo → **0 hits**; fps/framerate →
  **1 hit** (:108); lut/intensity/saturat → 9 hits, **none carrying a number**.
- Claim rows are line-anchored and spot-verified with `grep -n` against the literal value string.
  Two off-by-one errors were found this way (A27, A68) — line anchors in this file should be
  trusted only where such a check was run.
- Nothing under `_archive/` was modified, moved or deleted. No image or frame file was written
  anywhere. No network access of any kind; URL liveness unchecked and explicitly out of scope.
- Counts: File A **77** claims, File B **85** claims, **162 total, 0 sourced**.

---

## 8. Pass-3 correction log

Seven defects found in the pass-2 text. All are fixed or flagged in place above; **none changes
the headline findings** (0 sourced claims, 0 reference videos), and four *strengthen* the case
against these documents rather than weakening it.

| # | Defect | Where it was | Fix | Consequence |
|---|---|---|---|---|
| P3-1 | **Citation off by one.** A27 cited `:143` for "70-80% of transitions aligned"; :143 is "Smooth execution with minimal jarring moments". | §1 row A27, §3 C4, §3 C6 | → **`:142`** (`grep -n "70-80%"` → 142) | Cite-only. Value and contradiction unchanged. |
| P3-2 | **Citation off by one.** A68 cited `:429` for "Align 90%+ of transitions within 0.1s"; :429 is "Match cut energy to music energy". | §1 row A68, §3 C4, §3 C5, §3 C6 | → **`:428`** (`grep -n "90%+"` → 96, 428) | Cite-only. Value and contradiction unchanged. Note this error had propagated to **three** sections — the failure mode CLAUDE.md names (a stale claim surviving in a sibling artifact) reproduced inside a single file. |
| P3-3 | **False exhaustiveness claim.** §0 asserted "There is no fifth attribution construction in 1035 lines." `viral_drone_benchmark_2026.md:504` ("Research methodology: Web search analysis…") is a fifth. | §0 | Fifth row added to the attribution table; the over-claim replaced with a note on why the grep missed it (`research show` ≠ `Research methodology`) | **Strengthens the provenance verdict.** B:504 concedes the whole document rests on web search, naming no search and no result. |
| P3-4 | **Miscount.** C7 said "40-70%" appears "three times" while listing four cites, and omitted the :317 occurrence. | §3 C7 | → **five** (`grep -n "40-70%"` → 11, 58, 293, 317, 432) | Strengthens C7: the range and its collapsed point value sit on the *same line* (:317). |
| P3-6 | **Miscount.** "7-15s" was said to occur **9** times across both files. | §3 C8, §5 item 4 | → **13** (`grep -c "7-15"` → A 5, B 8) | Strengthens the point: the corpus's most-inherited number is also its most-repeated, and repetition is all that supports it. |
| P3-5 | **Eight claim rows missed.** A:367 (second "top 10%" statement) and B:11 / :106 / :150 / :236 / :244 / :246 / :401 (hook, text-overlay and engagement-timing claims). | §1, §2, §3 C9, §3 C18 | Rows A77 and B79–B85 added; C9 and C18 rewritten on the fuller evidence | **Strengthens C9 materially** — B states a hook window nine times across five values (1-3, 2, 2-3, 3, 3-5, 5), with the widest and a narrow one in the *same sentence* at :11. Pass 2 argued this from four cites. |

| P3-7 | **Dangling cross-reference / missing audit trail.** The pass-2 header promises "§7 Correction log". No §7 exists (`grep -nE "^#+ *7\."` → nothing; headings run §6 → §8). | Header note | Flagged in place, not silently deleted | **The pass-2 corrections have no audit trail and its claimed "six errors" is an unverifiable self-report.** Only §8 (pass 3) is a real log. Treat pass-2 provenance claims the way this checkpoint treats the source documents' — verified where re-checked, unsupported otherwise. |

**What pass 3 did *not* overturn.** Every URL count, every File-A absence, the four pass-2
attribution rows, all 154 pass-2 claim rows' values, the 0-sourced result, the 0-reference-video
result, and all 18 contradictions. Three independent passes have now failed to find a single
number in either file attached to a source at its point of use.
