# Census: URL + Creator-Attribution Sweep of Archived Research Corpus

**Agent**: census-url-attribution-sweep
**Date**: 2026-07-28
**Status**: COMPLETE — INDEPENDENTLY RE-VERIFIED (second pass, 2026-07-28)

> **Verification pass.** A first pass wrote this file but stalled before returning its
> structured result. A second pass re-ran the entire mechanical sweep from scratch with
> independently-written scripts and reproduced every load-bearing figure exactly:
> 210 files / 134 images / 76 text files, 221 raw tokens, 12 malformed, **233 occurrences,
> 174 distinct**, 12 files carrying URLs with identical per-file counts, and identical
> handle counts. Bucket classification was re-derived from an explicitly-listed domain
> ruleset (`classify.py`) rather than inherited. **Six of eight buckets reproduced exactly**
> — `creator_video` 1, `creator_profile` 3, `other` 4, `academic_or_standards` 4,
> `platform_official_spec` 11/13, `code_or_docs_reference` 19. See §3 note on the one
> boundary that moved.
>
> The decisive claim was additionally verified by direct grep, independent of the URL
> pipeline:
> `grep -rnIE "youtube\.com|youtu\.be|vimeo|/video/|/reel/|instagram\.com/p/|tiktok\.com|watch\?v=|/shorts/"`
> over both roots returns **exactly 3 lines**, one of which is an Adobe guide URL containing
> the substring `/video/`. Net: **one specific third-party video URL in the entire corpus.**

## Scope

- `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_research/`
- `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.claude_plans/` (incl. `highlight_splitter/`, `reel_analysis/`)

Corpus is LLM-generated planning/research from an earlier archived project (Dec 2025 – Mar 2026).
**NOT trusted source material.** Numeric assertions inside it are of unknown veracity and are
recorded here with provenance only, never adopted as fact. Archive treated strictly read-only;
the dead symlink `_p-ai-drone-video/_p-ai-drone-video` was not followed (`os.walk(..., followlinks=False)`
+ `os.path.islink` skip). **No network verification was performed** — URL liveness is explicitly
out of scope and reserved for the user. Every "this is a blog" judgement below is made from the
URL string, slug, and the citing sentence in the corpus, not from fetching the page.

## Method (reproducible)

Scripts (scratchpad, not in-repo):
- `census_urlsweep_A.py` — URL extraction, normalisation, malformed detection
- `census_handles_A.py` — `@handle` extraction with decorator exclusion
- `classify_B.py` — bucket classification (explicit overrides + domain rules)

Regex: `(?:https?://|www\.)[^\s<>"'`\\|]+`
Normalisation: strip trailing `. , ; : ! ? ) ] } > * _ " '` (balanced-paren aware), then strip trailing `/`.
Malformed test: token contains `](`, `[`, `]`, or more than one `http`.
Image files (`.jpg/.png/...`) excluded from text scan — 134 `.jpg` frames live under
`.claude_plans/reel_analysis/*frames*/` and are not text. **No image file was read, written, or created.**

## 1. File inventory

| Metric | Count |
|---|---|
| Files total under both roots (excl. symlink) | 210 |
| Text files scanned (`.md` 69, `.txt` 3, `.json` 2, `.gitkeep` 2) | 76 |
| Image files skipped (`.jpg`) | 134 |
| **Text files containing at least one URL** | **12** |
| Text files containing zero URLs | 64 |

All of `.claude_plans/highlight_splitter/` (5 files) and all of `.claude_plans/reel_analysis/`
(7 `.md` files) contain **zero URLs and zero creator attributions**.

Files that carry every URL in the corpus:

| Occurrences | File |
|---:|---|
| 37 | `.claude_research/viral_drone_editing_patterns.md` |
| 32 | `.claude_plans/viral_drone_benchmark_2026.md` |
| 28 | `.claude_research/viral_drone_video_research.md` |
| 24 | `.claude_plans/viral_drone_benchmark.md` |
| 20 | `.claude_plans/research_pro_software.md` |
| 19 | `.claude_plans/v21_viral_research.md` |
| 16 | `.claude_research/RESEARCH_SUMMARY.md` |
| 15 | `.claude_plans/research_color_science.md` |
| 15 | `.claude_plans/research_viral_trends.md` |
| 12 | `.claude_plans/research_transitions.md` |
| 10 | `.claude_research/ai-video-stitching-research.md` |
| 5 | `.claude_research/professional_drone_editing_software_analysis.json` |

## 2. URL counts

| Metric | Count |
|---|---|
| Raw regex tokens matched | 221 |
| URL instances after splitting the 12 malformed swallowed-link tokens into their two constituents | **233** |
| **Distinct URLs after normalisation** | **174** |
| Malformed URL forms | 12 (all in one file) |

`total_url_occurrences = 233` is the post-split figure used everywhere below; 221 is the raw-token figure.

## 3. Bucket classification

| Bucket | Distinct | Occurrences |
|---|---:|---:|
| `vendor_tool_marketing` | 84 | 108 |
| `seo_blog_or_guide` | 48 | 81 |
| `code_or_docs_reference` | 19 | 19 |
| `platform_official_spec` | 11 | 13 |
| `academic_or_standards` | 4 | 4 |
| `other` | 4 | 4 |
| `creator_profile` | 3 | 3 |
| **`creator_video`** | **1** | **1** |
| **TOTAL** | **174** | **233** |

**Boundary sensitivity, stated honestly.** The `vendor_tool_marketing` / `seo_blog_or_guide`
split is the one judgement call in this classification, and it moved between the two passes
(pass 1: 76/56 distinct; pass 2: 84/48). The difference is entirely about whether a given
content-marketing blog belongs to a company that also sells a video tool
(`studiobinder.com`, `spotlightfx.com`, `streamingmedia.com`, `getacademy.blog`, and similar
borderline domains). **This has zero bearing on the census's conclusion**: both buckets are
"not a video", and the six buckets that determine the verdict — `creator_video`,
`creator_profile`, `other`, `academic_or_standards`, `platform_official_spec`,
`code_or_docs_reference` — reproduced identically across both independent passes. The
combined non-video editorial figure is **132 distinct / 189 occurrences** either way.

Bucket definitions used:
- `creator_video` — URL resolves to one specific third-party video.
- `creator_profile` — URL resolves to a named human creator's channel/profile/own site.
- `vendor_tool_marketing` — page on a commercial tool/preset/SaaS/retail vendor's own domain (incl. its content-marketing blog).
- `seo_blog_or_guide` — general editorial/agency/how-to content site, not the vendor of a named tool.
- `platform_official_spec` — first-party product/help documentation from the software vendor it documents (Adobe, Apple, Blackmagic, DJI, CapCut, Canva, Google Play).
- `academic_or_standards` — camera-maker colour-science references (ARRI, RED) and explanation thereof.
- `code_or_docs_reference` — GitHub/PyPI/library docs/technical code tutorials.
- `other` — aggregator/festival/forum/contest-announcement pages that are neither a video nor an article making a claim.

**Notable structural absence:** there is **not one first-party Instagram, TikTok, or YouTube
platform-specification URL** in the corpus. Every one of the ~40 platform-spec claims
(aspect ratio, max duration, bitrate, feed cutoffs) is sourced to a third-party SEO page
(`postfa.st`, `socialsizes.io`, `zeely.ai`, `socialrails.com`, `litcommerce.com`,
`clickanalytic.com`, `kapwing.com`, …). Those numbers should be treated as unverified.

### `creator_video` (n=1)
| URL | File:line | Citing text |
|---|---|---|
| `https://www.tiktok.com/@thedronecreative/video/7380822378483338528` | `.claude_plans/research_transitions.md:862` | `- [Drone Orbit + Speed Ramp Technique (TikTok)](...)` |

### `creator_profile` (n=3)
| URL | File:line |
|---|---|
| `https://www.instagram.com/thedronecreative` | `.claude_research/viral_drone_video_research.md:636` |
| `https://www.tiktok.com/@thedronecreative` | `.claude_research/viral_drone_video_research.md:637` |
| `https://www.koldercreative.com` | `.claude_plans/research_viral_trends.md:291` (Sam Kolder masterclass/network site) |

### `other` (n=4)
| URL | File:line | Why not a reference video |
|---|---|---|
| `https://www.nycdronefilmfestival.com/winners` | `.claude_plans/v21_viral_research.md:361` | winners index page; no specific film named or linked in the corpus |
| `https://www.dji.com/media-center/announcements/skypixel-10th-annual-contest-winners-announced-en` | `.claude_plans/v21_viral_research.md:351` | contest press release |
| `https://influencers.feedspot.com/drone_instagram_influencers` | `.claude_research/viral_drone_video_research.md:635` | "Top 35 Drone Influencers" aggregator listicle |
| `https://forum.dji.com/thread-209598-1-1.html` | `.claude_research/professional_drone_editing_software_analysis.json:12` | product forum thread |

### Most-cited URLs (all buckets)
| Occ | URL | Bucket |
|---:|---|---|
| 8 | `https://vloglikepro.com/what-makes-a-great-drone-reel-go-viral-on-tiktok-and-instagram` | seo_blog_or_guide |
| 8 | `https://www.finchley.co.uk/finchley-learning/short-video-success-using-drone-videography-for-tiktok-and-instagram-reels` | seo_blog_or_guide |
| 5 | `https://oscarliang.com/color-grade-fpv-videos` | seo_blog_or_guide |
| 5 | `https://www.creatorsjet.com/blog/best-instagram-reel-length-for-engagement-based-on-500-viral-videos` | vendor_tool_marketing |
| 5 | `https://www.opus.pro/blog/best-ai-beat-sync` | vendor_tool_marketing |

The "500+ viral reels" figure that props up the corpus's headline pacing claims
(`viral_drone_benchmark.md:4`, `viral_drone_benchmark_2026.md:23`) traces to exactly one
commercial-vendor blog post (`creatorsjet.com`, a video-tool vendor). It is a single
second-hand citation, not an independent measurement, and the corpus never reproduces
its dataset or method.

## 4. Malformed URLs (n=12, all in one file)

Every malformed form is the same defect: a markdown reference-list entry whose link text is
itself the URL, so the closing `]` and opening `(` were swallowed —
`https://X](https://X)`. **All 12 are in `.claude_plans/viral_drone_benchmark.md`, References
section, lines 490–514** (odd-numbered entries 1–12). No other file in the corpus has a
malformed URL.

| # | File:line | Malformed form (truncated) |
|---|---|---|
| 1 | `viral_drone_benchmark.md:490` | `https://vloglikepro.com/what-makes-a-great-drone-reel-go-viral-on-tiktok-and-instagram](https://vloglikepro.com/...)` |
| 2 | `viral_drone_benchmark.md:492` | `https://www.finchley.co.uk/finchley-learning/short-video-success-...](https://www.finchley.co.uk/...)` |
| 3 | `viral_drone_benchmark.md:494` | `https://www.creatorsjet.com/blog/best-instagram-reel-length-...](https://www.creatorsjet.com/...)` |
| 4 | `viral_drone_benchmark.md:496` | `https://pixflow.net/blog/mastering-cinematic-drone-filmmaking/](https://pixflow.net/...)` |
| 5 | `viral_drone_benchmark.md:498` | `https://oscarliang.com/color-grade-fpv-videos/](https://oscarliang.com/...)` |
| 6 | `viral_drone_benchmark.md:500` | `https://www.dronegenuity.com/pilot-guide-to-color-correcting-drone-footage/](https://www.dronegenuity.com/...)` |
| 7 | `viral_drone_benchmark.md:504` | `https://www.autelpilot.com/blogs/faq/how-to-create-a-hit-on-social-media-with-a-drone](https://www.autelpilot.com/...)` |
| 8 | `viral_drone_benchmark.md:506` | `https://www.socialpilot.co/blog/instagram-reels-trends](https://www.socialpilot.co/...)` |
| 9 | `viral_drone_benchmark.md:508` | `https://cropink.com/instagram-reels-statistics](https://cropink.com/...)` |
| 10 | `viral_drone_benchmark.md:510` | `https://www.heyorca.com/blog/best-tiktok-hooks](https://www.heyorca.com/...)` |
| 11 | `viral_drone_benchmark.md:512` | `https://blog.studiovity.com/drone-cinematography-secrets-.../](https://blog.studiovity.com/...)` |
| 12 | `viral_drone_benchmark.md:514` | `https://www.thedroneu.com/blog/drone-cinematography-guide/](https://www.thedroneu.com/...)` |

Note the citation-hygiene signal: the corpus's most assertive numeric document
(`viral_drone_benchmark.md`, source of "7–15s optimal", "1.5–3s per clip", "85/100 target")
is also the one whose entire reference list is structurally broken. That is evidence the
reference list was generated rather than transcribed from pages actually opened.

## 5. Creator handles

`@`-token sweep found 5 human handles and 10 distinct Python-decorator token families.
Decorators were excluded by two tests: token sits inside a ```python fence, or is
immediately followed by `(`.

**Kept (human):**

| Handle | Occ | Files | Specific video URL? |
|---|---:|---|---|
| `@thedronecreative` (7) / `@TheDroneCreative` (2) | 9 | `.claude_research/viral_drone_video_research.md` (347, 636, 637×2), `.claude_research/implementation_priorities.md:415`, `.claude_research/viral_insights_structured.json:256`, `.claude_plans/research_transitions.md` (72, 627, 862) | **Yes** — `research_transitions.md:862` |
| `@beverlyhillsaerials` | 3 | `viral_drone_video_research.md:356`, `implementation_priorities.md:416`, `viral_insights_structured.json:265` | No |
| `@basso2012` | 3 | `viral_drone_video_research.md:362`, `implementation_priorities.md:417`, `viral_insights_structured.json:272` | No |
| `@simeonpratt` | 2 | `viral_drone_video_research.md:367`, `viral_insights_structured.json:279` | No |

**Named creators without a handle:**

| Name | Occ | Files | URL? |
|---|---:|---|---|
| Sam Kolder | 9 | `.claude_plans/research_viral_trends.md` (56, 63, 107, 291, 293 …), `.claude_plans/visual_enhancements_roadmap.md:82` | Profile site + a tutorial *about* his transition; no video |
| Casey Neistat | 2 | `.claude_research/viral_drone_video_research.md` (54, 375) | No |
| Peter McKinnon | 1 | `.claude_plans/research_viral_trends.md:115` | No |
| Matthew Brennan (= `@thedronecreative`) | 4 | `viral_drone_video_research.md` ×2, `implementation_priorities.md`, `viral_insights_structured.json` | see above |

**Excluded (Python decorators, not creators):** `@patch` (59), `@click.option` (39),
`@dataclass` (10), `@main.command` (7), `@cli.command` (1), `@click.group` (1),
`@property` (1), `@pytest.fixture` (1), `@pytest.mark.skip` (1).

## 6. Reference-video candidates (strict)

Strict test applied: *is a specific third-party drone video identified precisely enough that a
reviewer could watch that exact video?* A blog article, a creator profile, a contest winners
index, and a listicle all fail this test.

| # | Identifier | Platform | Specificity | File:line |
|---|---|---|---|---|
| 1 | Drone Orbit + Speed Ramp Technique — `@thedronecreative` video `7380822378483338528` | TikTok | **specific_video** | `.claude_plans/research_transitions.md:862` |
| 2 | `@thedronecreative` / Matthew Brennan | Instagram + TikTok | creator_only | `.claude_research/viral_drone_video_research.md:347` |
| 3 | `@beverlyhillsaerials` | Instagram | creator_only | `.claude_research/viral_drone_video_research.md:356` |
| 4 | `@basso2012` | Instagram | creator_only | `.claude_research/viral_drone_video_research.md:362` |
| 5 | `@simeonpratt` | Instagram | creator_only | `.claude_research/viral_drone_video_research.md:367` |
| 6 | Sam Kolder | web (koldercreative.com) | creator_only | `.claude_plans/research_viral_trends.md:107` |
| 7 | Peter McKinnon | none given | creator_only | `.claude_plans/research_viral_trends.md:115` |
| 8 | Casey Neistat | none given | creator_only | `.claude_research/viral_drone_video_research.md:375` |
| 9 | Drone Film Guide (courses) | none given | generic | `.claude_research/viral_drone_video_research.md:377` |
| 10 | NYC Drone Film Festival winners | web index | generic | `.claude_plans/v21_viral_research.md:361` |
| 11 | SkyPixel 10th annual contest winners | web announcement | generic | `.claude_plans/v21_viral_research.md:351` |
| 12 | "These viral FPV drone videos will leave you speechless" (listicle) | web | generic | `.claude_plans/research_viral_trends.md:299` |
| 13 | Feedspot "Top 35 Drone Influencers in 2026" | web | generic | `.claude_research/viral_drone_video_research.md:635` |

**specific_video = 1. creator_only = 7. generic = 5.**

The four `@` handles are documented as *followers + credentials + a one-line specialty*
(`viral_drone_video_research.md:345–372`, mirrored in `viral_insights_structured.json:254–284`).
No individual work of theirs is named, timestamped, linked, or measured. Three of the four have
no URL anywhere in the corpus.

The corpus's own "case studies" (`viral_drone_video_research.md:384–401`) — "Speed Ramp Orbit
Technique", "FPV Indoor-Outdoor Transitions", "Golden Hour Landscape Reveals" — are technique
descriptions with no video attached. The "benchmark" documents
(`viral_drone_benchmark.md`, `viral_drone_benchmark_2026.md`, `v2_vs_viral_comparison.md`,
`reel_review_vs_viral.md`, `v21_viral_benchmark_review.md`) benchmark against an abstracted
"Viral Standard" column synthesised from the blog corpus, **never against a named video**.
`v2_vs_viral_comparison.md:1–20` is the clearest instance: a "V2 vs Viral Instagram Drone
Videos" comparison table whose "Viral Standard" column cites no video at all.

## 7. Verdict

**The archived corpus does NOT contain a curated catalogue of third-party reference videos.**

Evidence:
- 174 distinct URLs. Exactly **1** (0.57%) resolves to a specific third-party video.
- 3 more (1.7%) resolve to a creator profile/site. The remaining 170 (97.7%) are blog
  articles, vendor marketing, product docs, code repos, or aggregator pages.
- The single specific video (`tiktok.com/@thedronecreative/video/7380822378483338528`) appears
  **once**, in a reference list at the bottom of `research_transitions.md`, cited for one
  technique (orbit + speed ramp). It is not part of any catalogue, has no accompanying
  measurement, no duration, no shot list, no scoring, and is never referenced again anywhere
  in the corpus.
- The nearest thing to a catalogue is a 4-entry "Top Drone Videographers to Study" list
  (`viral_drone_video_research.md:345–372`) — creators, not videos, described by follower
  count. That is a list of accounts, not a catalogue of targets to aim at.
  Its machine-readable twin, the `top_creators` array at
  `viral_insights_structured.json:254–282` (verified by direct read, pass 2), is the single
  most registry-shaped structure in the corpus — and its four objects carry only
  `handle` / `name` / `platform` / `followers` / `credentials` / `specialty`.
  **There is no `url` field, no video field, and no named work on any of the four.**
  A registry schema with no artifact in it cannot seed a catalogue of artifacts.
- Zero YouTube, zero Vimeo, zero Instagram Reel/post permalinks anywhere in 76 text files.
- **The sharpest single piece of evidence** (verified by direct read, pass 2):
  `viral_drone_video_research.md:373–377` carries a section literally headed
  **"#### YouTube Tutorials on Drone Reel Editing"** whose three bullets are
  "Casey Neistat's vlog style", "DJI Official tutorials (LightCut features)", and
  "Drone Film Guide courses" — **containing not one YouTube URL, and not one video title**.
  A section named for a video platform, listing zero videos, is the corpus's own
  demonstration that it never collected reference videos in the first place.
- Verified by direct read (pass 2): `v2_vs_viral_comparison.md:7–17` is an 8-row
  "V2 Status vs **Viral Standard**" gap table whose entire "Viral Standard" column is
  adjectives and numbers ("Dynamic/Jaw-dropping", "1.5-3s avg", "Beat-synced",
  "Teal-orange") with **no video, creator, or URL cited for any row**. The corpus benchmarks
  against an abstraction, never against an artifact.
- Verified by direct read (pass 2): `v21_viral_research.md:340–361`, the "SOURCES" block of
  the most recent benchmark document, is **20 bullets, all 20 blog/vendor articles**. The two
  closest-to-video entries are SkyPixel and NYCDFF *contest-winner index pages* — no winning
  film is named, linked, or described anywhere in the corpus.

**Consequence for `data/reference/REGISTRY.md`** (promised by `.gitignore` lines 38–44 of
`04-drone-video-editing-ai` as a "curated catalogue" of "third-party best-in-class REFERENCE
videos"): the archive cannot seed it. Harvesting the archive yields **one** candidate row,
and even that row is unverified — its liveness, its content, and whether it actually
demonstrates what the corpus claims are all unchecked (and checking is out of scope here).
Writing a REGISTRY.md from this corpus would require either (a) shipping a one-row catalogue,
or (b) padding it with blog articles, which would misrepresent blog posts as reference videos
and violate the repo's measurement-grounding rule. Neither is a catalogue.

**Counter-position, stated fairly:** the corpus is not worthless for the registry's *sibling*
purpose. It contains 174 URLs and ~7 named creators that could seed a **bibliography** or a
**"creators to sample from" shortlist** — a legitimate, honestly-labelled artifact. What it
cannot honestly produce is a REFERENCE VIDEO registry, because the underlying reference videos
were never identified in the first place.

---
_Sweep complete and independently re-verified. No file under `_archive/` was written, moved,
or modified. No image file was read, written, or created. No network request was made
(URL liveness is out of scope and reserved for the user). No git command was run. No package
was installed. Scripts used live only in the session scratchpad, not in the repo._
