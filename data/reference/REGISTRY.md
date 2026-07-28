# reference registry

**Status: FINDINGS DOCUMENT — not a curated catalogue, because there is nothing to curate.**
Built 2026-07-28. Supersedes nothing; this is the first content ever written to `data/reference/`.

---

## Why this file exists, and what it was supposed to be

`.gitignore` lines 38–44 (written 2026-07-27) promise this file:

> ```
> # Third-party best-in-class REFERENCE videos (targets to aim at, not source material).
> # Never committed — these are all-rights-reserved works by other creators, held locally for
> # study only. data/reference/REGISTRY.md (the curated catalogue) and data/reference/probe/
> # (measurements about them) ARE tracked; the video files themselves never are.
> /data/reference/videos/*
> !/data/reference/videos/.gitkeep
> ```

That rule is the **only** place in this repository that has ever mentioned `data/reference/` or
`REGISTRY.md`. Verified 2026-07-28 by grep across `CLAUDE.md`, `.claude/CLAUDE.md`,
`.claude/specs/`, `pyproject.toml`, and every `.md`/`.json` under `data/`: zero other hits. The
capability has no spec, no milestone, and no mention in the architecture map.

The intended source material was the archived research corpus at
`_archive/_p-ai-drone-video/{.claude_research,.claude_plans}/` — the surviving planning layer of a
different, earlier project. The session of 2026-07-27 was mid-census of that corpus when it stopped.
This file completes that census.

**The census answered the question in the negative.** The corpus does not contain a catalogue of
best-in-class reference videos. It contains one.

---

## 1. The catalogue

Strict inclusion test, applied by five independent agents: *a specific, identifiable third-party
video, or a named creator held up as an exemplar.* An SEO blog post about drone videography is not a
reference video. A film-festival winners index page with no film named is not a reference video.

### 1.1 Specific videos — complete list

| # | Video | Platform | URL | Cited at | Cited for |
|---|---|---|---|---|---|
| 1 | "Drone Orbit + Speed Ramp Technique", id `7380822378483338528` | TikTok | `https://www.tiktok.com/@thedronecreative/video/7380822378483338528` | `research_transitions.md:862`, cross-referenced at `:72` and `:627` | Justifies two MUST-HAVE features: Orbital Continuation Cut ("highly viral technique") and Hyperlapse Zoom-Through ("viral drone technique per TikTok @TheDroneCreative analysis") |

That is the entire list. **One video, across 21 documents and ~11,100 lines.**

Note the wording at `research_transitions.md:627` — "per TikTok @TheDroneCreative **analysis**". No
such analysis appears in the document. The word implies a study of the video that was never written
down, and the two features it justifies are specified in frames and speed multipliers that appear
nowhere in the citation.

### 1.2 Creators named without any linked work

| Handle / name | Platform | Stated credentials | Cited at | Work linked? |
|---|---|---|---|---|
| `@thedronecreative` (Matthew Brennan) | Instagram + TikTok | 136K followers, Dubai; "Orbit transitions with speed ramps and motion blur" | `viral_drone_video_research.md:347–354`, `viral_insights_structured.json:255–263` | Profile links only |
| `@beverlyhillsaerials` | Instagram | 179.4K followers, "3× Emmy Award Winner" | `viral_drone_video_research.md:356–360` | No |
| `@basso2012` | Instagram | 54.2K followers, "DGCA Authorized UAV Pilot" | `viral_drone_video_research.md:362–365` | No |
| `@simeonpratt` | Instagram | 25.6K followers, Director/Cinematographer | `viral_drone_video_research.md:367–370` | No |
| Sam Kolder | — | "Most Studied/Replicated" style | `research_viral_trends.md:107` | No — only a masterclass site and a third-party tutorial *about* his transition |
| Peter McKinnon | — | Named as a style heading | `research_viral_trends.md:115` | No |
| Casey Neistat | — | "speed ramps, dynamic pacing" | `viral_drone_video_research.md:54, 375` | No — and not a drone creator |

The four Instagram handles and their follower counts most plausibly derive from a Feedspot listicle
(`influencers.feedspot.com/drone_instagram_influencers`, in the bulk source list at
`viral_drone_video_research.md:635`), but no document says so. Recorded as unattributed.

### 1.3 What the URLs actually are

Exhaustive mechanical sweep of both archived directories: **233 URL occurrences, 174 distinct.**

| Bucket | Count | Share |
|---|---:|---:|
| Vendor / tool marketing | 84 | 48.3% |
| SEO blog or guide | 48 | 27.6% |
| Code or docs reference (GitHub, PyPI, OpenCV) | 19 | 10.9% |
| Platform official spec (Adobe, Apple, Blackmagic, CapCut) | 11 | 6.3% |
| Academic or standards (ARRI, RED colour science) | 4 | 2.3% |
| Other (festival/contest index pages, DJI forum) | 4 | 2.3% |
| Creator profile | 3 | 1.7% |
| **Creator video** | **1** | **0.6%** |

The sweep also found a class of malformed URLs — markdown links that swallowed a second copy of
themselves, e.g. `https://vloglikepro.com/...](https://vloglikepro.com/...)`. Citation hygiene in the
corpus is poor enough to corrupt its own links.

---

## 2. Provenance of the claim corpus

The corpus's value was never really its video catalogue — it was the ~980 numeric editorial claims
it asserts about how drone video should be cut, graded, paced and delivered. Those are what a future
`src/drone_video_ai/` threshold would be tempted to inherit. So the census catalogued them all.

### 2.1 Coverage

| Unit | Files | Lines | Numeric claims | With an external named source |
|---|---:|---:|---:|---:|
| viral-research-core | 5 | 2,582 | ~150 | 0 (4 unresolvable verbal credits) |
| craft-research | 5 | 4,647 | ~127 | 5 (vendor marketing figures only) |
| benchmark-plans A | 2 | 1,035 | 162 | 0 |
| benchmark-plans B | 2 | 666 | 94 | 0 |
| evaluation A | 2 | 474 | 112 | 0 external — but see §2.3 |
| evaluation B | 3 | 788 | 96 | 0 |
| evaluation C | 2 | 924 | 237 | 0 |
| **Total** | **21** | **~11,116** | **~978** | **5** |

### 2.2 The uniform attribution pattern

Every unit independently reported the same structure, with no exceptions found:

> Claims are stated bare in the document body. A bulk topical URL list sits at the end of the file.
> **Nothing maps any individual number to any source.**

Density varies but the pattern does not. `drone_visual_design_principles.md` — 1,322 lines, the
single densest source of editorial constants in the corpus, and the origin of the preset discussed
in §4 — contains **zero URLs of any kind**. `source_footage_analysis.md` and
`detection_tuning_params.md` likewise have no bulk list at all: all 237 of their claims stand alone.
`v21_viral_benchmark_review.md` and `v21_technical_analysis.md` have no URLs either.

The only inline credits that exist anywhere are four unresolvable verbal ones:

| Where | Credit | Resolvable? |
|---|---|---|
| `viral_drone_video_research.md:293` | "**Facebook Study:** 65% who watch first 3 seconds continue for 10+ seconds" | No study, year, or URL named; no Meta URL anywhere in the corpus |
| `viral_drone_editing_patterns.md:366` | "27% boost … (2025 automotive case study)" | Unnamed |
| `viral_drone_editing_patterns.md:425` | "41% increase … (2025 hospitality case study)" | Unnamed |
| `RESEARCH_SUMMARY.md:52` | "Analysis of top 100 viral Shorts: 2.5s average clip length = 35% higher completion" | Unnamed; also a platform mismatch (Shorts is YouTube; stated scope is Reels + TikTok) |

`viral_drone_benchmark_2026.md:504` concedes its own method outright: "web search analysis".

### 2.3 The one island of genuine measurement — and the seam beside it

For epistemic balance, the corpus is not uniformly ungrounded. **`v21_technical_analysis.md`
sections 1–3 and 6 are real self-measurement**: the file states its tool and date ("Analysis
performed via ffprobe on 2026-02-20", line 9) and reports 33 claims measured off the project's own
renders. An agent re-derived nine of them by hand and they check out. This is the only place in
~11,100 lines where a number is both stated and reproducible.

Which makes what happens next the most instructive finding in this census.

`v21_viral_benchmark_review.md:11` writes:

> "The technical analysis found the rendered files are **missing audio entirely**, use **excessive
> bitrate (80 Mbps vs 8-15 Mbps recommended)**, and lack **color space metadata**."

- **80 Mbps** is real. `v21_technical_analysis.md:42` measures 80,571 and 80,671 kbps via ffprobe.
- **"8-15 Mbps recommended"** appears **nowhere** in `v21_technical_analysis.md` (verified by grep,
  2026-07-28). What that file actually says, at line 110, is *"A 15-25 Mbps encode for 4K or 8-12
  Mbps for 1080p would be optimal"* — two separate bands for two different resolutions.

So "8–15" is a merge of the 4K band's floor with the 1080p band's ceiling, producing a number no
document states, presented in the same sentence as a genuine measurement, under a single
attribution to a source that does not contain it. A reader has no way to see the seam. This is not
carelessness at the margin — it is the exact mechanism by which an invented constant acquires the
authority of a measured one.

### 2.4 The range → point-value → code-default collapse

Documented in at least eight independent instances. A range is asserted, then silently hardened to a
single value with no stated reason, then appears as a function default:

| Parameter | Range asserted | Collapsed to | Reached code as |
|---|---|---|---|
| LUT / grade intensity | 50–70% (5 documents); also 40–70% | 60% (`RESEARCH_SUMMARY.md:167`), ~60% (`research_viral_trends.md:61`) | `intensity=0.6` (`implementation_priorities.md:212`); `--color-intensity 0.5` (`viral_drone_benchmark_2026.md:317`, whose own comment still reads 40–70%) |
| Transition duration | 0.3–0.5 s; also 0.2–0.5 s | 0.3 s, stamped "OPTIMAL" (`viral_drone_benchmark_2026.md:280`) | `duration=0.3` (`implementation_priorities.md:243`) |
| Speed-ramp opener | 50–70% speed | 0.7× (`v21_viral_research.md:71, 175`) | — |
| B-frame saving | 10–20% | "~15%" (`v21_technical_analysis.md:180`) | — |
| Colour intensity (review) | 0.6–0.7, "not lower" | "Adjust default to 0.6" (`v21_viral_benchmark_review.md:64`) | — |

In every case the point value, not the range, is what reached code.

### 2.5 Internal contradictions

Roughly 90 catalogued across the seven units; full tables in the checkpoint files. A representative
selection, chosen because each would change a threshold:

- **Optimal total duration** — four incompatible targets: 7–15 s, 15–30 s, 15–20 s, and a
  `target_duration: 20` default. `viral_drone_editing_patterns.md` states both 7–15 and 15–30 within
  two lines of each other.
- **Shot length** — `viral_drone_video_research.md:72` recommends 1–2 s, *below*
  `viral_drone_editing_patterns.md:17`'s stated 1.5 s "minimum viable"; `:73` recommends 3–5 s,
  *above* the same file's 4 s "maximum before drag".
- **Beat-sync philosophy inverted in six days** — `viral_drone_benchmark.md:149` (2026-02-02):
  95%+ of cuts aligned = "100/100 Viral-Quality". `viral_drone_benchmark_2026.md:124` (2026-02-08):
  cutting on every beat is listed as a critical gap needing a fix.
- **Delivery resolution** — 1080×1920 "exactly" vs "4K: Critical for screen presence". The same
  corpus scores 4K as both "Already Working Well" and "WARN (excessive)".
- **`RESEARCH_SUMMARY.md` introduces six statistics absent from every document it summarises**
  (72%/46% completion, +45% golden hour, +30% top-down, 35% higher completion, 85%+ sound-off, and
  the 60-80/40-60/30% retention bands), and misstates the line counts of the three files it
  summarises, each by exactly one.
- **Arithmetic that does not hold** — "15-25 cuts/min (based on 1.5-4 second shot durations)"; the
  stated basis yields 15–40. "0.3-0.5 seconds (10-15 frames at 30fps)"; 0.3 s is 9 frames.

### 2.6 Scores presented as evidence, with no scale defined

The three qualitative evaluation documents assign scores — "5.0/10 overall", "opening hook 2/10",
"45/100" — with **no rubric defining anchors, weights, or method anywhere**. Four separate invented
scales are in use. The "5.0/10" headline turns out to be the undeclared unweighted mean of ten
sub-scores (sum = 50, verified); the "45/100" is not derivable at all. One document writes "Hard to
evaluate from stills" and then assigns 4/10 to the thing it just said it could not evaluate, and
scores Pacing 3/10 from the same stills.

---

## 3. Collision with the measured pack

`data/reference_pack/` measured this project's own footage with ffprobe/ffmpeg and stdlib Python.
Where the archived corpus and that measurement address the same quantity, this is what happens.

Relation vocabulary: **CONFIRMED** — the pack measured it and agrees. **FALSIFIED** — the pack
measured it and disagrees. **UNVALIDATABLE** — the pack measured the relevant property and found a
corpus in which the claim cannot be tested even in principle. **UNMEASURED** — the pack does not
measure it. **OUT OF REACH** — the pack records this as beyond its toolchain.

| Archived claim | Pack measurement | Citation | Relation |
|---|---|---|---|
| Export at 30 fps | `30/1` on all 8 files, CFR exact | `editorial_style.json` → `corpus_wide_invariants.frame_rate` (measured) | **CONFIRMED** |
| Deliver 1080×1920 vertical | `[1080, 1920]` on the social-vertical surface | `delivery_surfaces[social_vertical_1080]` (measured) | **CONFIRMED** |
| Letterbox 2.35:1 | measured 2.352941 on active picture 1280×544 | `letterbox.horizontal_split_family.measured_ratio` (measured) | **CONFIRMED** — the 0.0029 delta is integer-pixel quantization, not error; the pack explicitly resolves the apparent 16:9-vs-2.35 contradiction as "both true simultaneously" |
| `drone_aerial` grade = Teal-Blue, saturation 60% | UAVG +0.11%, VAVG −0.23%, SATAVG +2.2%, HUEAVG +0.03% — all at or near noise. Only luma moved (YAVG −8.25%) | `colour_treatment.declared_grade.verification_status` (measured) | **FALSIFIED** — see §4 |
| `auto_speed: true` | "NO-OP — no speed change of any kind was applied to any clip"; clip frame N maps to source frame offset+N across all 1,599 frames | `speed_ramp_policy.measured_effect` (measured) | **FALSIFIED** |
| Bitrate 5–15 Mbps / 5000–10000 kbps | social-vertical 13.4–14.1 Mbps (in band); splits 15.0 Mbps (at ceiling); **4K masters 73.8–75.9 Mbps** | `delivery_surfaces[].video_bitrate_bps` (measured) | **FALSIFIED** for the 4K surface — and independently corroborated by the archived corpus's own ffprobe measurement of ~80 Mbps on its own renders |
| Cut every 1.5–3 s; 15–25 cuts/min; 8–12 scenes per 30 s | **0 hard cuts** across all 8 files; 1 shot per file; `cuts_per_minute = 0.0` over 136.6 s | `shot_structure.hard_cut_count_total_corpus` (measured) | **UNVALIDATABLE** — the pack records this as a positive finding, not a detection failure, and nulls `target_cut_interval_s`/`target_cuts_per_minute` rather than defaulting them. Generalises to 45 more archive files. |
| 70–90% of cuts aligned to beats; BPM 100–130; beat tolerance ±150 ms | **0 audio streams** on all 8 files | `audio.audio_stream_count` (measured) | **UNVALIDATABLE** — there is no audio track to which cuts could have been timed, and no cuts either |
| Retention figures: 65% at 3 s, +40% engagement, +22% watch time, +1200% shares, 50% drop-off, 72%/46% completion | no observable | — | **UNMEASURED** — nothing in a video file measures viewer behaviour. These are not weakly-sourced; they are unfalsifiable with any toolchain this project has |
| Camera-motion labels: `REVEAL`, `ORBIT_CW`, `STATIC`; orbit detection at \|mean_dx\| > 8.0 px/frame | no optical-flow capability (`cv2`/`numpy`/`scenedetect` absent) | `toolchain.unavailable`; README "Not verifiable with this toolchain" | **OUT OF REACH** — and the pack separately flags that `split_004_s65` is labelled `STATIC` yet measures mean MAFD 1.7130, 63.0% of the corpus high |
| Transition durations 0.15–0.8 s; dissolve/whip/glitch vocabularies | longest elevated scdet run is 2–5 frames on 7 of 8 files (19 on one) | `cut_rhythm.soft_transition_search` (measured) | **UNMEASURED** — `editorial_style.json.omitted_parameters` explicitly nulls `dissolve_duration_s`, `transition_type_vocabulary_beyond_fade_to_black`, `speed_ramp_curve`, `colour_grade_lut_or_curve`, `audio_bed_spec`, `text_overlay_or_caption_spec` and 13 others as unsupported by this corpus |

**The shape of the result:** the archived corpus is right about the things that are properties of a
file format (frame rate, resolution, aspect ratio) and wrong or untestable about everything that is
a property of *editing* — because the footage it was written to describe contains no editing to
measure. Zero cuts, zero audio, one shot per file.

---

## 4. Two confirmed lineages into this project's own footage

The archived corpus is not merely adjacent to this project. Two of its constants are provably
present in the footage `data/reference_pack/` measures.

### 4.1 `drone_aerial` — a colour preset that changes no colour

**Lineage: CONFIRMED.**

1. `drone_visual_design_principles.md:458` — a file containing **zero citations of any kind** —
   defines the preset — dominant hue Teal-Blue, saturation "Medium (60%)", contrast "Medium-High",
   use case "Default for landscapes". Line 467 makes it the default preset.
2. This project's corpus `manifest.json` declares `split_params.color = "drone_aerial"` and
   `color_intensity = 0.65`, applied to all four `split_*` clips.
3. `data/reference_pack/` measured what it actually did: **chroma untouched.** A true
   bt2020→bt709 conversion control would have moved SATAVG −36.6% and HUEAVG −14.66; the observed
   movement is +2.2% and +0.03%. Only a highlight-weighted luma compression occurred.
4. This generalises: 6 of 7 archive manifests declare a colour grade; **all** reproduce chroma-inert.

A preset whose entire published definition is a hue and a saturation level has never, in any of the
seven manifest regimes measured, produced a measurable hue or saturation change.

**Tested and NOT confirmed:** the value `0.65` itself. It is tempting to read it as inherited from
the corpus's "50–70%" band, but `0.65` appears **nowhere** in the archived corpus as an intensity
(its values cluster at 0.5, 0.6, 0.7 and the ranges 50–70% / 40–70%). Consistent with the band;
not traceable to it. Recorded as unresolved rather than asserted.

### 4.2 `scene_threshold: 7.0` — a parameter that was never wired

**Mechanism: CONFIRMED by the archived project's own documentation.**

The pack measured, from pixels alone, that clip boundaries are not content-derived and that the
declared `scene_threshold` is incommensurable with measured scene-change scores — a ~4× gap in this
corpus (7.0 against a measured scdet ceiling of 1.706), widening to ~36× worst-case across the
archive set. It recorded the mechanism as unknown.

`detection_tuning_params.md` supplies it, at lines 22 and 27–34:

> The `split` and `extract_clips` commands **do not wire `config.scene_threshold`** to SceneDetector.
> They instantiate with all defaults, ignoring user config.
> ```python
> scene_detector = SceneDetector()  # Uses defaults, ignores config
> ```

The `7.0` recorded in this project's `manifest.json` was never the operative value. The detector ran
at the PySceneDetect `ContentDetector` default of 27.0. A measurement and an archived source
document, produced independently and years apart, agree.

Note the same document contradicts itself on this: line 5 describes "the DJI video case" as having
"produced 7 scenes with similar scores (55-64 range)" as though a validated run occurred, while
lines 22–34 establish the parameter was disconnected.

**Tested and NOT resolved:** whether that "DJI video case" is this project's corpus run. The scene
count matches exactly (`manifest.json` `scenes_detected: 7`), but the document's stated 55–64 score
band excludes all four observable clip scores (65.6, 66.8, 69.8, 70.0). The three filtered scenes
are unobservable, so this cannot be settled. Recorded as unresolved.

Separately: the document's threshold recommendations are **not footage-derived**. 27.0 is the
library default; the proposed 20–22 is an untested prediction; the score ranges it reasons from
("likely 55-64", "likely 35-50 motion_energy") are hypotheticals, and the actual manifest values
(motion_energy 77.7–100.0) fall outside them. Its section 9 plans validation runs that were never
performed.

---

## 5. What this means for `src/drone_video_ai/`

1. **No number in the archived corpus may be promoted to a threshold as-is.** ~978 catalogued
   claims; five carry an external named source, and all five are vendor marketing figures. This is
   not a sourcing gap to be closed by more reading — the sources do not exist.
2. **The two highest-risk artifacts are machine-readable.** `viral_insights_structured.json` holds
   ~24 uncited constants pre-shaped as config (`key_metrics`, `optimal_range_seconds`,
   `recommended_export`) and a single `json.load()` inherits them silently — it even dropped the weak
   "Facebook Study" credit the prose retained. `implementation_priorities.md` has them already as
   function defaults (`target_duration=20`, `min_gap=1.5, max_gap=3.0`, `intensity=0.6`,
   `duration=0.3`, `end_speed=0.5`). Copy-paste distance to `src/` is zero.
3. **Watch the attribution seam, not just the number.** §2.3 shows a real ffprobe measurement and an
   invented band sharing one sentence and one attribution. Any future citation of this corpus must
   name a file *and line*, because file-level attribution is demonstrably not sufficient to separate
   the measured from the invented.
4. **This corpus cannot validate a cut detector, a beat-sync policy, or a grade.** Not because it is
   poorly sourced, but because the footage it describes has zero cuts, zero audio, and a grade that
   measurably does nothing. That is a property of the material, not of the documentation.
5. **The reusable part is the failure taxonomy, not the numbers.** The range→point→default collapse
   (§2.4), the undefined-scale score (§2.6), and the attribution seam (§2.3) are patterns worth
   testing future work against, including work produced in this repository.

---

## 6. Why `data/reference/probe/` is empty

`data/reference/videos/` holds only `.gitkeep`. Verified 2026-07-28: **no third-party reference
video exists anywhere on this machine** — not in the archived project (0 video files outside its own
DJI source tree), not in sibling projects. `probe/` is empty because there is nothing to probe, not
because the measurement step was skipped.

Populating it would mean downloading all-rights-reserved third-party works. That is an
outward-facing, licence-sensitive action and a user decision; it was not taken. Nor was any URL in
this document fetched or checked for liveness — **every URL here is recorded as it appears in the
archived corpus and is unverified.** Given the malformed-link rate found in §1.3, treat them as
citations to check, not as working links.

---

## 7. Open questions

1. **Should `data/reference/` exist at all?** It has no spec. `.gitignore` is its only authority,
   and the one spec in this repo (`reference-pack`) is still DRAFT. Per the Spec-Driven Workflow, a
   tracked deliverable here would normally need a spec first. This file is written as findings, not
   as the "curated catalogue" the ignore rule describes.
2. **Should reference videos be acquired?** If yes: which, under what licence reading, and does the
   no-persisted-frames rule extend to third-party video files held locally? Note `.gitignore`
   already anticipates the answer is yes (`/data/reference/videos/*`) while the reference-pack spec
   Open Question #1 leaves the licence scope of the prohibition undecided.
3. **Should the `.gitignore` comment be corrected?** It describes `REGISTRY.md` as "the curated
   catalogue". As of this file, that description is inaccurate.
4. **Should the archived corpus be retained?** Its measured content is one video URL, 33 reproducible
   ffprobe numbers, and two confirmed lineages into this project's own footage. Everything else is
   catalogued here.

---

## 8. Verification log

All checks run 2026-07-28 in-session.

| Check | Command / method | Result |
|---|---|---|
| Toolchain live | `ffprobe -version` | 8.1.2, no dyld fault |
| Pack JSON valid | `python3 -m json.tool` ×2 | both parse |
| Probe pairing | `ls probe/*.json`, `ls probe/*.scd.csv`, `comm -3` | 54/54, zero orphans |
| No persisted frames | `find` for image extensions outside inherited dirs | none |
| `data/raw/corpus` mirror | `shasum -a 256` vs read-only `00-assets/` | all 9 byte-identical |
| No reference videos on disk | `find` for video extensions across archived + sibling projects | 0 |
| `REGISTRY.md` referenced elsewhere | grep across CLAUDE.md, specs, pyproject, `data/` | only `.gitignore` |
| `0.65` in archived corpus | `grep -rnE 'intensity.*(0\.65\|65)'` | absent — lineage not confirmed |
| `drone_aerial` in archived corpus | `grep -rn "drone_aerial"` | present, `drone_visual_design_principles.md:458` — lineage confirmed |
| `8-15 Mbps` in `v21_technical_analysis.md` | `grep -n "8-15"` | **absent** — attribution at `review:11` does not hold |
| Corpus manifest params | `python3 -c` on `00-assets/.../manifest.json` | `scene_threshold 7.0`, `color drone_aerial`, `color_intensity 0.65`, `letterbox "2.35"`, `auto_speed true`, `scenes_detected 7` |

**Method.** Seven agents read 21 files end to end (~11,116 lines) under explicit instructions that
the corpus is untrusted, that `_archive/` is read-only, and that no network request was permitted.
Agent checkpoints — the full claim tables, all ~90 contradictions, and per-unit provenance verdicts —
are at `.claude/checkpoints/reference-registry-2026-07-28/`. The collision in §3 and every lineage
test in §4 were run directly against `data/reference_pack/` and the source manifests, not delegated.

**Not independently verified.** The per-claim tables in the agent checkpoints are single-pass. The
findings promoted into §3 and §4 of this document were re-derived directly from the pack and the
archived files; the wider catalogue behind them has not been adversarially re-checked. Treat the
headline counts (233 URLs, ~978 claims, ~90 contradictions) as one careful pass, not as settled.

**Switch variables in force.** `corpus-scope` = the 8-file `00-assets/drone-video-examples/` set;
the archive cross-validation material is kept distinct throughout. `archive-write-mode` = read-only,
honoured — nothing under `_archive/` or `00-assets/` was written, moved, or modified.
`git-repair-mode` = untouched; no git command was run. `spec-status` = DRAFT; nothing here treats
any spec as signed off.
