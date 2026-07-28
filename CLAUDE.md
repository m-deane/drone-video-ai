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

**Current implementation state, verified this session — read before assuming otherwise:**
`src/` and `tests/` **do not exist on disk**, despite `pyproject.toml` declaring both
(`[tool.setuptools.packages.find] where = ["src"]`, `[tool.pytest.ini_options] testpaths =
["tests"]`). `.venv/` is an empty husk (`pyvenv.cfg` only, no `bin/`); no declared runtime
dependency (`opencv-contrib-python`, `scenedetect[opencv]`, `numpy`, `opentimelineio`,
`otio-cmx3600-adapter`) is installed, and system `python3` has none of them either. The two
console scripts above are **not runnable**. This is not a partially-broken pipeline — it is a
project whose implementation was lost (most plausibly alongside a corrupted `.git`, see
below) while its planning/spec layer and one fully-built deliverable survived.

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
- **`.claude/specs/reference-pack/spec.md`** — the only capability with a spec.
  **Status: DRAFT — not signed off.** Per the Spec-Driven Workflow below, no Plan/Tasks/
  Implement phase may begin against it until the user explicitly signs off.
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
data/
├── reference_pack/          # the built deliverable — see "What each artifact means" in its own README
│   ├── README.md             # regeneration recipes, directory layout, failure traps — read first
│   ├── REVIEW.md              # full per-file review, manifest reconciliation, verification log
│   ├── editorial_style.json  # machine-readable house style, confidence-labeled per value
│   ├── probe/                 # raw ffprobe JSON + scdet CSV — the primary source, everything else derives from this
│   └── media/                 # .gitkeep only — NEVER holds actual media (licence constraint, see below)
├── manifests/
│   └── reference_pack.json    # machine-readable file index + archive_expansion cross-validation index
└── raw/                        # (if present) gitignored local consolidated footage copy — convenience only

.claude/
├── specs/reference-pack/spec.md   # the only spec in this repo. Status: DRAFT.
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

.git/    # CORRUPT — contains only HEAD/config/COMMIT_EDITMSG/description, no objects/refs/
         # index. Every git command fails with "fatal: not a git repository". Nothing in this
         # repo is currently under version control. Do not run `git init` or any git command
         # without the user's explicit authorization — this has been raised and deferred at
         # least once already; treat silence as "still deferred," not as permission.
```

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
| `git-repair-mode` | `.git` stays corrupt/untouched until the user explicitly authorizes repair; this has been raised and deferred already | running `git init` unprompted → silently starting version control on work the user hasn't decided how to handle yet |
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
- **"commit"**: `.git` is currently corrupt — there is nothing to commit to. Say so rather
  than attempting the action; do not silently no-op.
- **"anything else?" / "what's left?"**: Scan for open items — the git-repair decision, the
  inherited-file disposition decision, and `REVIEW.md`/`spec.md`'s own recorded Open
  Questions are the standing ones as of 2026-07-27.
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

`.git` is corrupt in this repo (see Architecture above) — there is currently no remote to
check. If `.git` is ever repaired, run `git remote -v` before any push, same as any repo.

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

`.claude/specs/reference-pack/spec.md` exists and is the only spec in this repo — **Status:
DRAFT**. No Plan/Tasks/Implement phase may begin against it without explicit user sign-off.
Capabilities 1 and 2 (highlight extraction, reel stitching) have **no spec at all** — if
asked to implement `src/drone_video_ai/highlight_extraction/` or `reel_stitching/`, a spec
must be written and approved first, per this section, not skipped because `pyproject.toml`
already names the console-script entry points.

When something is ambiguous during implementation, return to the spec. Amend the spec, then
code. Never improvise divergence from a signed-off spec — and never treat a DRAFT spec as
signed off.

## Personal Overrides

Create `CLAUDE.local.md` in the project root for personal, machine-specific overrides. This
file should be gitignored and never committed.
