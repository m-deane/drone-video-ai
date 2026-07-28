# CLAUDE.md

## Role

You are an expert media-pipeline engineer working on `drone_video_ai` — a licence-clean,
measurement-grounded drone video processing project. Your default stance is
implementation-ready, grounded, and reviewer-accountable: every threshold, claim, or
provenance statement you produce in this repo must trace to a measurement taken in-session,
never to an invented constant or an assumption carried over from general knowledge of "what
drone footage usually looks like."

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## Project Overview

**`drone_video_ai`** — per `pyproject.toml`: "Drone video editing AI pipeline: highlight
extraction, reel stitching, and reference-pack curation." Three capabilities:

1. **Highlight extraction** (Milestone 1) — `drone-highlights` console script →
   `drone_video_ai.highlight_extraction.cli:main`.
2. **Reel stitching** (Milestone 2, `.otio`/CMX3600 EDL export) — `drone-stitch` console
   script → `drone_video_ai.reel_stitching.cli:main`.
3. **Reference-pack curation** — no console script, no milestone marker in `pyproject.toml`.
   This is the only capability with a built deliverable right now (see below).

**Current implementation state, verified 2026-07-28 — read before assuming otherwise:**

> **CORRECTED 2026-07-28. The previous version of this section said the implementation was lost.
> It was not.** `.git` was corrupt (config only, no objects/refs), which made the configured
> remote unreachable and the working tree look like all that survived. Repairing `.git` recovered
> 7 commits from `https://github.com/m-deane/drone-video-ai.git`. Do not re-derive the
> "implementation was lost" conclusion from a bare `ls` — it was wrong for three sessions.

`src/` and `tests/` **exist and are populated**: 28 Python files / ~4,079 LOC across
`common/`, `highlight_extraction/`, `reel_stitching/`, `reference_pack/`, and 22 test files /
~2,060 LOC. Recovered 2026-07-28 from `origin/main` (commit `8163d4b`, "implement Milestone 1
of all three drone-video-ai capabilities").

**`src/` IS NOW RUNNABLE AND ITS TESTS PASS** (2026-07-28, user-authorised relaxation of the
no-`pip install` rule, scoped to a project-local `.venv` only).

- **Interpreter trap:** system `python3` is **3.9.6**, but `pyproject.toml` requires `>=3.10`, so
  `pip install -e .` fails with "requires a different Python". The venv must be built on 3.10+.
  Working recipe: `uv venv --python 3.12 --clear .venv && VIRTUAL_ENV=.venv uv pip install -e ".[dev]"`.
- **The opencv conflict `pyproject.toml` documents is real and reproduces every time.** Installing
  the project pulls BOTH `opencv-python` (via `scenedetect`) and `opencv-contrib-python`. Apply
  that file's own documented fix afterwards, and check the CONCRETE FACTORY
  (`cv2.saliency.StaticSaliencySpectralResidual_create`), not just `hasattr(cv2, "saliency")`.
  Do NOT `--no-deps` reinstall before the project install has succeeded — that strips `numpy`.
- **`93 passed in 20.31s`.** Both console scripts run.

**But green tests do NOT mean validated against this footage.** `pyproject.toml` declares an
`integration` marker for "tests that use real `data/raw/` sample footage"; **zero tests use it**
and none reference real footage. All 93 are unit tests over synthetic fixtures. The pipeline was
first run against real corpus footage on 2026-07-28 — see "Audit findings" below.

**What does exist and is real, working, and verified:**

- **`data/reference_pack/`** — a measured, adversarially-verified characterisation of this
  project's example footage (`README.md`, `REVIEW.md`, `editorial_style.json`, `probe/`).
  Built entirely with `ffprobe`/`ffmpeg` CLI + Python 3 stdlib (no `cv2`/`numpy`/
  `scenedetect` — see "Toolchain constraint" below). Read `data/reference_pack/README.md`
  first in any session touching footage, thresholds, or house style — it is the single
  source of truth for what this footage actually measures as, not what it might be assumed
  to be.
- **`data/manifests/reference_pack.json`** — the machine-readable index behind the pack:
  per-file `ffprobe` fingerprints, provenance, and (as of 2026-07-27) an `archive_expansion`
  section covering 6 raw camera-original drone masters and 39 derivative clips used to
  cross-validate the pack's findings, kept clearly distinguished from the corpus proper.
- **`data/reference_pack/exemplars/`** — 58 curated third-party reference videos (recovered
  2026-07-28). **Metadata-only by design**: every entry carries `license_category:
  "all-rights-reserved"` as a conservative default and `local_media_path: null`; no media file is
  ever downloaded or persisted. Entries record source URL, creator, platform, retrieval date,
  award/showcase provenance, scores, and — critically — a `scores_provenance` flag distinguishing
  measured values from `manually_estimated` ones. This is the project's answer to "what should we
  aim at", and it is the model for how provenance should be recorded anywhere in this repo.
- **`.claude/specs/`** — **two** specs, not one:
  - `drone-video-pipeline/` — `spec.md` + `plan.md` + `tasks.md`, the chain behind the
    implemented Capabilities 1 and 2. Recovered 2026-07-28.
  - `reference-pack/spec.md` — **Status: DRAFT, not signed off.** Per the Spec-Driven Workflow
    below, no Plan/Tasks/Implement phase may begin against *this one* until the user signs off.
- **`.claude/`** — a full Claude Code scaffold (73 skills, 73 hookify rules, 17 agents,
  recipes, router, settings) synced from `claude-template` on 2026-07-25/26. `.claude/CLAUDE.md`
  (behavioural directives) and `.claude/settings.json` are project-owned per that template's
  own convention and are not overwritten by future syncs.

**Toolchain constraint that shapes everything in this repo right now.** Every measurement in
`data/reference_pack/` was produced with `ffprobe`/`ffmpeg` (currently 8.1.2 at
`/opt/homebrew/bin`) plus the Python 3 standard library only. **Do not `pip install`
anything** to work in this repo — there is no working venv to install into, and the pack's
own spec forbids adding a dependency to close a measurement gap. This toolchain is sufficient
for container, timing, framing, luma/chroma, and frame-difference facts, and is **provably
insufficient** for optical-flow facts (camera-motion direction/rotation classification). The
pack states which is which rather than guessing; new work in this repo must do the same.

**The toolchain is also fragile — verified failure, not theoretical.** A routine `brew
upgrade` (x265 4.1→4.2) once broke every `ffmpeg`/`ffprobe` command in this repo mid-session
(`dyld: Library not loaded`). First command in any new session that will run `ffprobe`/
`ffmpeg`: `ffprobe -version`. If it dies with a `dyld` error, run `brew reinstall ffmpeg`
before anything else — do not assume the toolchain works because it worked last session.

**Source footage — three locations, do not conflate them:**

| Location | Role | Constraint |
|---|---|---|
| `00-assets/drone-video-examples/` (sibling folder, outside this repo) | The 9-entry example **corpus** — 8 `.mp4` + `manifest.json` | Read-only. This is what "the corpus" means everywhere in `data/reference_pack/` unless stated otherwise. |
| `_archive/_p-ai-drone-video/.drone_clips/` (sibling folder) | 6 raw camera-original masters + 7 more `manifest.json` sidecars (39 derivative clips), used for **cross-validation**, not corpus expansion | Read-only, ~3.3 GB. Never copy into this repo — reference by absolute path. One dead symlink inside it (`_p-ai-drone-video/_p-ai-drone-video` → a nonexistent `/Users/matthewdeane/...` path on this machine) — do not follow it. |
| `data/raw/` (this repo, if present) | A local, gitignored **consolidated copy** of footage for convenience — see below | Gitignored; regenerate/re-copy, never treat as authoritative provenance. The two locations above remain the source of truth. |

## Commands

```bash
# Verify the toolchain before doing anything ffprobe/ffmpeg-dependent
ffprobe -version   # if this dies with a dyld error: brew reinstall ffmpeg

# Validate the reference pack's two JSON artifacts
python3 -m json.tool data/reference_pack/editorial_style.json > /dev/null
python3 -m json.tool data/manifests/reference_pack.json > /dev/null

# Reference-pack coverage check (probe/ must hold matched .json + .scd.csv pairs)
ls data/reference_pack/probe/*.json | wc -l
ls data/reference_pack/probe/*.scd.csv | wc -l   # must match the line above exactly

# Re-verify source corpus integrity (sha256 — see data/reference_pack/README.md for the
# full baseline table; never modify anything under 00-assets/ or _archive/)
shasum -a 256 /Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples/*.mp4

# Full regeneration recipes for every probe/ artifact (ffprobe/scdet/cropdetect commands,
# with the two documented silent-failure traps) live in data/reference_pack/README.md —
# copy from there, not from memory; two broken forms of the scdet recipe exit 0 while
# producing wrong output and have already shipped bad artifacts in this pack's history.
```

`pyproject.toml` declares `pytest>=8.0` as the sole dev dependency and a `testpaths =
["tests"]` / `integration` marker convention ("slower tests that use real `data/raw/` sample
footage") — but `tests/` does not exist, so there is currently nothing to run `pytest`
against. The `data/raw/` marker text is itself the grounding for where consolidated local
footage should live if you set that up (see the source-footage table above).

There is **no build, lint, or CI command** in this repo yet — `src/` doesn't exist. The
Quality Gates in `.claude/CLAUDE.md` (bash -n, hookify cross-reference checks,
`sync-claude-template.sh` dry-run, hookify routing tests) are inherited from `claude-template`
and apply to `.claude/` scaffold edits, not to this project's own (currently nonexistent)
code.

## Architecture

```
src/drone_video_ai/            # RECOVERED 2026-07-28 from origin/main — 28 files, ~4,079 LOC
├── common/                    # ffprobe.py, manifest.py, schema.py
├── highlight_extraction/      # segmentation, motion, gates, weights, composite, 4x scoring_*, cli
├── reel_stitching/            # otio_export, pacing, color_pinning, render, verify, edit_manifest, cli
└── reference_pack/            # schema.py, storage.py
tests/                         # RECOVERED — 22 files, ~2,060 LOC. NOT RUNNABLE HERE (no pytest)

data/
├── reference_pack/          # the built deliverable — see "What each artifact means" in its own README
│   ├── README.md             # regeneration recipes, directory layout, failure traps — read first
│   ├── REVIEW.md              # full per-file review, manifest reconciliation, verification log
│   ├── editorial_style.json  # machine-readable house style, confidence-labeled per value
│   ├── probe/                 # raw ffprobe JSON + scdet CSV — the primary source, everything else derives from this
│   ├── exemplars/             # 58 third-party reference videos, METADATA ONLY (local_media_path: null)
│   └── media/                 # .gitkeep only — NEVER holds actual media (licence constraint, see below)
├── manifests/
│   └── reference_pack.json    # machine-readable file index + archive_expansion cross-validation index
├── reference/                  # REGISTRY.md — provenance census of the archived _p-ai-drone-video corpus
└── raw/                        # (if present) gitignored local consolidated footage copy — convenience only

.claude/
├── specs/drone-video-pipeline/    # spec.md + plan.md + tasks.md — the chain behind Capabilities 1 & 2
├── specs/reference-pack/spec.md   # Status: DRAFT, not signed off.
├── CLAUDE.md                       # behavioural directives — project-owned, not overwritten by sync
├── settings.json                   # permissions + hooks — project-owned, not overwritten by sync
├── skills/, hookify.*.local.md, recipes/, router.md, agents/   # synced scaffold from claude-template
└── (agents/ and rules/ are the two paths claude-template's sync script never overwrites automatically)

CLAUDE.md, README.md, CHANGELOG.md, TODO.md, REVIEW.md, PROMPTLAB-READINESS.md, docs/,
promptlab/, assets/, dist/, site/, mkdocs.yml, sync-claude-template.sh,
requirements-promptlab.txt   # INHERITED claude-template maintainer content — .gitignore
                              # explicitly excludes these from this project. They describe
                              # claude-template itself, not drone_video_ai. Do not treat their
                              # content as authoritative for this project; do not delete them
                              # without asking (disposition is an open question, not decided).

.git/    # REPAIRED 2026-07-28 — was corrupt (HEAD/config/COMMIT_EDITMSG/description only, no
         # objects/refs/index), which made the CONFIGURED REMOTE unreachable and made the working
         # tree look like all that survived. Re-initialised, fetched origin, reset --mixed to
         # origin/main (working tree untouched), restored only deleted paths. 8 commits now.
         # Remote: https://github.com/m-deane/drone-video-ai (public). Local main is 1 commit
         # AHEAD of origin/main — the reconciliation commit has NOT been pushed.
```

## Audit findings — `src/` vs the measured pack (2026-07-28, first ever comparison)

`src/` and `data/reference_pack/` were built independently and **had never been compared**. When
they were, the headline is blunt: **of 85 constants audited across the scoring and `common/`
groups, ZERO trace to a measurement in `data/reference_pack/`.** The scoring group's verdict:
"pack and scorers were built as if the other did not exist."

This is an orientation failure, not a sloppiness failure — the code is careful, heavily commented,
and several constants are honestly labelled as arbitrary-but-defensible. But the cost is concrete
and was **confirmed by execution**, not inferred:

0. **THE BIG ONE — segmentation is inert on 6 of 8 corpus files.** `split_segments`
   (`segmentation.py:135`) is greedy on `chosen = max(within_max)`: it takes the FARTHEST
   boundary that still fits inside `max_duration`. So whenever the whole file fits inside
   `max_duration`, it returns exactly one segment spanning the file and **discards every interior
   boundary it just computed**. Verified on `split_001_s70.mp4`: the pipeline discovers 12 interior
   boundaries, then emits 1 segment `(0.0, 15.0)`. Lowering the cap recovers them —
   `max_duration=8.0 -> 2 segments`, `5.0 -> 4`, `3.0 -> 6` — so the machinery works; the default
   is wrong for this footage. `DEFAULT_DURATION_PROFILE.max_duration = 15.0` traces to spec AC1.4,
   and the pack's measured shot lengths are `[8.3, 14.567, 14.567, 15.0, 15.0, 15.0, 27.1, 27.1]`
   — **6 of 8 are ≤ 15.0**, and the mean is 17.08. Only the two 27.1 s files ever split.
   This compounds with finding 2: one segment forces `n=1`, which pins `sharpness` and
   `motion_smoothness` to 1.0. **Net effect on this corpus: the highlight extractor emits one
   whole-file segment with half its quality signals saturated, so it cannot rank highlights
   because it never produces more than one.** Nothing is broken in the code; the default cap and
   the measured footage were simply never compared.
1. **No scorer crops the letterbox.** Every pack measurement uses `crop=1280:544:0:88`; no scorer
   crops at all (grep: zero crop logic in `highlight_extraction/`). Measured effect on
   `split_001_s70.mp4`: cropping the bars off moves **exposure +0.2444** — the pack's measured
   letterbox `content_cost` is **24.4%**. Letterboxed exposure is exactly `1 − 0.2444 = 0.7556`:
   the bars (measured luma 16) are counted as clipped pixels, so exposure scores the mask, not the
   picture. Composition moves +0.0336. Constant ≈ −0.061 composite penalty on the 4 split-family
   files versus the vertical family.
2. **Scores are rank, not quality.** `min_max_normalize` (`scoring_sharpness.py:63`) returns
   `[1.0]` for ANY single-element input — verified: `[0.02] -> [1.0]` and `[123.4] -> [1.0]`. At
   n=2 it forces `{1.0, 0.0}`. The pack proved every corpus file is single-shot, and the live run
   produced `total_segments = 1` on 4 of 5 files, so `sharpness` and `motion_smoothness` are `1.0`
   by construction and carry no quality information. `exposure` and `composition` are absolutely
   normalised and therefore unaffected.
3. **Under-exposure detection is structurally unreachable.** `LOW_CLIP_THRESHOLD = 5`
   (`scoring_exposure.py:21`) against a corpus whose measured YMIN is ≥14 everywhere. Half the
   exposure scorer cannot fire on this footage.
4. **`MAX_HORIZON_TILT_DEGREES = 20.0`** is justified in-code as "a professionally-composed aerial
   rarely exceeds this" — precisely the general-knowledge-of-drone-footage derivation the
   Constitution prohibits. No measured tilt distribution exists in the pack.
5. **The highlight manifest cannot distinguish a fabricated value from a measured one.**
   `ffprobe.py` silently substitutes `0` on its failure path, and `from_dict` default-fills a
   `normalization` method description for work that never ran. This project solved this problem
   twice already — `editorial_style.json`'s `confidence` field and
   `reference_pack/schema.py`'s `scores_provenance` — and the pipeline's own output schema is the
   one artifact that does not.

**A positive result worth keeping:** PySceneDetect's `ContentDetector`, running inside the real
pipeline, reported `scenes_detected = 0` on every corpus file — independently reproducing the
pack's zero-hard-cuts finding with a completely different tool from the `ffmpeg scdet` the pack
used. That is the strongest confirmation the pack's central claim has.

**Scope correction to the toolchain constraint below.** That section says this project has "no
optical-flow capability". That is true of the **reference pack's** measurement layer
(ffprobe/ffmpeg + stdlib) and remains the reason pack claims about camera-motion direction are
OUT OF REACH. It is **not** true of `src/`: `motion.py` runs genuine sparse optical flow
(`cv2.goodFeaturesToTrack` + `calcOpticalFlowPyrLK`), deliberately avoiding ffmpeg's GPL
`vid.stab` per plan.md's resolution of spec Open Question 5. It computes **magnitude only** —
mean Euclidean feature displacement — not direction or rotation, so the corpus manifest's
`REVEAL`/`ORBIT_CW`/`STATIC` labels stay unverified. But the capability gap is narrower than a
plain reading of the toolchain section suggests: the pipeline could reach direction; it chose
not to.

Capability 2 is in materially better shape than Capability 1: 16 constants, 0 MEASURED but 5 SPEC
and 9 LIBRARY_DEFAULT, only 2 INVENTED and both inert. `pacing.py` correctly invents no cut
rhythm where the pack found none. Its real defect is a verification bug — `verify.py:60` compares
whole framemd5 lines including pts, but pts/frame-count depend on sub-frame `-ss` phase, while
`pacing.py:102` puts `out_tc` off the measured 30/1 CFR grid that `otio_export.py:179` already
quantises to. So `verify` can fail on byte-perfect paced renders, and passes vacuously on empty
input.

Full per-constant tables: `.claude/checkpoints/threshold-audit-2026-07-28/`.
**None of these findings has been fixed.** Each fix is a design decision, not a cleanup.

**Why the reference pack exists.** Capability 1 scores highlights, Capability 2 stitches
reels; both need thresholds. An invented threshold is exactly the "invented constant" the
Constitution below prohibits. `data/reference_pack/` exists so that any future threshold in
`src/drone_video_ai/` can cite a number someone actually measured over this project's own
footage — read it before writing any pipeline code that scores or thresholds anything.

**The pack's single most consequential finding, stated so it is not accidentally re-litigated
from scratch:** the 8-file example corpus contains **zero hard cuts** — every file is one
continuous shot. This generalizes to the much larger archive cross-validation set too (45
more files, 2026-07-27). Any future shot-boundary-detection work must not assume this corpus
can validate a cut detector; it cannot, by construction.

**Licence constraint, absolute:** no frame/image file may ever be written anywhere in this
repo. `.gitignore` names this explicitly for one already-encountered failure mode
(`/.playwright-mcp/`, `seek*.png`, etc.) and the reference-pack spec restates it as a hard
Scope-out. All measurement must stay in-pipe (`ffmpeg ... -f null -`); this has never once
required a persisted frame in this pack's construction and should not start now.

**A documented, recurring failure mode in this pack's own history, worth internalising
before extending it further:** a fix or new fact landing in one artifact (say,
`REVIEW.md`) while an identical stale claim survives in a sibling artifact, a sibling JSON
field, or even a second table row in the *same* file. This has shipped at least twice.
Before treating any correction or addition to `data/reference_pack/` or
`data/manifests/reference_pack.json` as complete, grep all five artifacts
(`REVIEW.md`, `README.md`, `editorial_style.json`, `reference_pack.json`, `spec.md`) for
every related existing claim, not just the one you are directly editing.

## Constitution

Non-negotiable rules that govern every phase — spec, plan, tasks, and implementation:

1. **Grounding**: never reference a file path, function name, or export without having
   verified it in this session
2. **No placeholders**: no mocks, stubs, TODOs, or partial implementations in production
   artifacts
3. **Verification**: always verify changes — for JSON: `python3 -m json.tool`; for
   ffprobe/ffmpeg recipes: run them and check the output against the documented failure
   traps in `data/reference_pack/README.md`; for shell scripts: `bash -n`
4. **Human review**: every diff must be reviewable — vibe-coding (unreviewed acceptance) is
   prohibited in production scope
5. **Reversibility**: confirm before any irreversible action (push, delete, external API
   call) — and note that with `.git` corrupt, "push" is not currently possible and "delete"
   has no undo via version control either
6. **Tool-grounded verification**: verification must use external tools (ffprobe, python3
   `json.tool`, `shasum`, a second independent measurement). Self-critique without tool
   output is not verification
7. **Epistemic balance**: for qualitative or research questions, present evidence both for
   and against the user's implied position

## Verifiability Tiers

Classify every task before acting — tier determines confirmation requirements:

- **Tier A (autonomous-safe)**: re-running an already-documented `ffprobe`/`ffmpeg` recipe
  from `data/reference_pack/README.md` verbatim, JSON validity checks, sha256 re-verification
  against a recorded baseline.
- **Tier B (assisted, default)**: extending `data/reference_pack/` with new measurements or
  findings, editing `.claude/specs/reference-pack/spec.md`, skill/hookify edits. Confirm plan
  before dispatch.
- **Tier C (supervised)**: repairing `.git` (`git init` or any git command), deleting or
  moving anything under `00-assets/drone-video-examples/` or `_archive/`, writing to
  `src/`/`tests/` for the first time (this would be starting real implementation against a
  DRAFT, unsigned spec), any action affecting the inherited claude-template root files'
  disposition. Confirm every action; do not batch.

## Critical Patterns

Switch variables — named assumptions where choosing the wrong value produces meaningfully
different output. State the assumed value before any task that produces an artifact:

| Variable | Default assumption | Wrong value → consequence |
|----------|--------------------|---------------------------|
| `corpus-scope` | "the corpus" = the original 9-entry `00-assets/drone-video-examples/` directory only; the `_archive/` cross-validation material (6 raw masters, 39 derivatives) is explicitly separate | conflating archive-expansion counts with corpus counts → the exact drift bug that has already broken this pack's own acceptance criteria twice |
| `spec-status` | `.claude/specs/reference-pack/spec.md` is DRAFT, not signed off; any divergence found while extending the pack amends the spec first, never diverges silently | treating the spec as authorising implementation → building `src/` against an unapproved design |
| `archive-write-mode` | `_archive/` and `00-assets/` are read-only; footage is referenced by absolute path, never copied into this repo (only measurement output — small JSON/CSV — is written to `data/reference_pack/probe/`) | copying multi-GB footage into git-tracked space, or modifying a file under either read-only tree |
| `git-repair-mode` | RESOLVED 2026-07-28 — `.git` is repaired and healthy, 8 commits, remote `origin` = `github.com/m-deane/drone-video-ai`. Local `main` is 1 commit AHEAD of `origin/main` and has never been pushed | assuming `.git` is still corrupt → refusing to commit, or re-running `git init` over a working repository |
| `verification-completeness` | assume PARTIAL — some claims in `data/reference_pack/` are adversarially verified (independent skeptics, majority-refute), others (notably 6 of 7 archive-manifest reconciliations as of 2026-07-27) are single-pass and explicitly flagged as not yet independently confirmed | treating every claim in the pack as equally certain — REVIEW.md §7/§8 record which is which; check before citing a number as settled |

When a task does not name its switch values, assume the defaults above and state the
assumption explicitly before proceeding.

## Grounding Rules (Anti-Hallucination)

- When verification is not possible in the current session, state uncertainty explicitly:
  "I have not verified this in the current session — treat as unconfirmed."
- Never assume dispatched agents inherit context from this session — every condition that
  must govern an agent's work must be written explicitly into that agent's prompt
- Never reference a file path without having read it or verified it with `ls`/`find` in this
  session — this applies with extra force to `src/`/`tests/`, which do not exist despite
  being declared in `pyproject.toml`
- Never state a function, type, or export exists without having grepped for it
- Never confirm a package name or dependency without having checked whether it is actually
  installed (`python3 -c "import X"`) — `pyproject.toml`'s declared dependencies are
  currently **aspirational**, not installed
- Never summarise file contents without reading the file first in this session
- Never confirm a user's assumption about the codebase without independently verifying it

## Qualitative Grounding Rules

- Never agree with a qualitative claim about this footage's "style," "quality," or
  "usability" without checking whether `data/reference_pack/` measures it — the pack exists
  specifically to replace impressionistic footage assessment with measurement
- Never search for only confirming evidence when a claim about this footage embeds a
  hypothesis — the pack's own construction found its most valuable results (byte-identical
  duplicate clips, a manifest contradicting itself, a mislabeled metric) by actively hunting
  for disagreement, not by confirming what a manifest or filename implied
- When the user's question contains a superlative or absolute about this footage or pipeline
  ("clearly a hard cut," "definitely the camera original"), treat it as testable, not
  established — the pack's genealogy resolution for `DJI_0355_proxy.mp4` is a worked example
  of exactly this: a plausible filename/duration coincidence, confirmed only after actual
  pixel-match measurement

## Conversational Conventions

- **"proceed" / "go ahead" / "yes" / "ok" / "retry"**: Execute the action most recently
  proposed. Apply the reversibility gate — if the action involves `git`, deleting or moving
  anything under `00-assets/`/`_archive/`, or writing outside `data/`/`.claude/specs/`, state
  what you are about to do in one sentence and confirm. For everything else, execute
  immediately without preamble.
- **"give me a prompt [to do X]"**: Generate a standalone, copy-paste-ready prompt for X. Do
  not execute X — output the prompt text only.
- **"run the prompt"**: Execute the prompt most recently generated.
- **"launch an agent team [for X]" / "ultracode"**: Decompose X and dispatch via the Workflow
  tool. **Known infrastructure fragility in this environment, worth planning around**:
  long-running or heavily-parallel workflow agents have repeatedly stalled mid-stream this
  session, and any `await agent()` call *not* wrapped in `parallel()`/`pipeline()` will crash
  the entire workflow script if it stalls — always wrap every agent call, even a single one.
- **"commit"**: `.git` works (repaired 2026-07-28). Commit normally. Local `main` is ahead of
  `origin/main` and unpushed — say so, and treat `push` as a separate, outward-facing action
  requiring its own confirmation. The remote is **public**.
- **"anything else?" / "what's left?"**: Scan for open items — as of 2026-07-28 the standing ones
  are: the unpushed commit, whether `src/` should be made runnable (needs a venv + deps, currently
  blocked by the no-`pip install` rule), the inherited-file disposition decision, `data/reference/`'s
  redundancy against `exemplars/` (see `data/reference/REGISTRY.md` §7), and `REVIEW.md`/`spec.md`'s
  own recorded Open Questions.
- **"no" / "no thank you"**: Decline acknowledged. Stop. Do not re-propose.

## Skill Routing

This repo has the full three-layer routing model from `claude-template`:

1. **Layer 1 — Hookify keyword match**: `.claude/hookify.detect-*.local.md` files (73,
   synced).
2. **Layer 2 — Router document**: `.claude/router.md` — cluster-based disambiguation.
3. **Layer 3 — Semantic matching**: skill descriptions in the system-reminder list.

## Long-Running Agent Work

- Use `/sprint [goal]` to orchestrate parallel agents with automatic checkpointing
- Use `/resume` to recover from stream timeouts without re-doing completed work
- Dispatch max 4-5 agents per wave — beyond this, combined agent output floods the
  orchestrating context window; for 6+ agent tasks use sequential waves with `/resume`
  between waves, or the `Workflow` tool with small, narrowly-scoped agents (see the
  stall-avoidance note under Conversational Conventions above — this project has hit that
  failure mode repeatedly and recovering from it by hand, using data agents had already
  written to disk before stalling, has worked reliably every time it's been tried)

## Stream Idle Timeout — Prevention and Recovery

Stream idle timeouts (`API Error: Stream idle timeout - partial response received`) are the
primary cause of lost agent work in this repo's own history.

**Prevention:** Embed in every agent prompt: "Write ALL code and detail to your checkpoint
file. Inline return: ≤150 words. Write checkpoint FIRST — even a skeleton. Stop immediately
after your inline summary." Keep individual agent scope narrow — this repo's own experience
is that giant "write everything" agents stall; several small, focused agents each writing one
file do not.

**Recovery:** Check whether Write/Edit tool calls landed on disk before the agent's final
structured response stalled — they usually did, even when the harness reports the agent as
"failed." Read `journal.jsonl` for the workflow run (path given in the failure notification)
before assuming a stalled agent produced nothing; extract and reuse whatever it actually
returned. Re-dispatch only the genuinely missing pieces with narrower scope.

## Hooks

Hooks live in `.claude/hooks/` (Python, synced: `log-activity.py`, `turn-boundary.py`) and
are wired from `.claude/settings.json` (project-owned, merged not overwritten by sync). They
write to the gitignored `.claude/activity.md`.

## Eval & Prompt Versioning

Available via the synced `.claude/` scaffold (`/eval-harness`, `/stability-test`,
`/rubric-eval`, `/version-prompt`, etc.) but **not yet used in this project** — there is no
prompt or skill of this project's own to version yet, since `src/` doesn't exist. Relevant
once pipeline code (and its prompts, if any) exist.

## Git Remotes

**`origin` = `https://github.com/m-deane/drone-video-ai` — and it is PUBLIC.** Corrected
2026-07-28: this section previously said there was no remote. There always was one; `.git` was
corrupt, so `git remote -v` failed and the remote's existence was invisible. That single stale
sentence is why three sessions believed the implementation had been lost.

Run `git remote -v` before any push, same as any repo. Because the remote is public, treat every
push as publishing: check that no absolute local path, credential, or user-identifying detail is
being added that should not be. Local `main` is currently 1 commit ahead and unpushed.

## File Safety

- **Jupyter notebooks (.ipynb)**: none exist in this repo currently; if added, use `nbformat`
  for programmatic edits, never raw string/regex manipulation
- **Generated files**: `data/reference_pack/probe/*.json` and `*.scd.csv` are generated —
  regenerate via the recipes in `data/reference_pack/README.md` rather than hand-editing

## File Safety Rules

- Never modify `.env` files, `node_modules/`, or `.git/`
- Never modify anything under `00-assets/drone-video-examples/` or `_archive/` — both are
  read-only source material this project measures but does not own

## Spec-Driven Workflow

Phase order: **Spec → Plan → Tasks → Implement**. Each phase produces a named artifact; the
user must explicitly sign off before the next phase begins.

There are **two** spec trees, and they are at different phases:

- `.claude/specs/drone-video-pipeline/` — `spec.md` + `plan.md` + `tasks.md`, complete through
  Implement. Capabilities 1 and 2 were **built against this chain** (commit `8163d4b`). Corrected
  2026-07-28: this file previously said Capabilities 1 and 2 had "no spec at all", which was wrong
  — the spec existed on `origin/main` and was unreachable only because `.git` was corrupt.
- `.claude/specs/reference-pack/spec.md` — **Status: DRAFT, not signed off.** No Plan/Tasks/
  Implement phase may begin against *this* spec without explicit user sign-off.

Before implementing against either, re-read it. Do not infer a spec's phase from the presence of
code — infer it from the spec's own recorded status.

When something is ambiguous during implementation, return to the spec. Amend the spec, then
code. Never improvise divergence from a signed-off spec — and never treat a DRAFT spec as
signed off.

## Personal Overrides

Create `CLAUDE.local.md` in the project root for personal, machine-specific overrides. This
file should be gitignored and never committed.
