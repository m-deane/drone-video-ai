# Reference-pack expansion — two launch prompts (deterministic vs. Bayesian)

Prepared for: `p-drone-video-editing-ai` (`drone_video_ai`), Capability 3 — Reference Pack
Grounded in this session against: `.claude/specs/drone-video-pipeline/{spec,plan,tasks}.md`, `src/drone_video_ai/reference_pack/{README.md,schema.py,storage.py}`, `docs/prompting-template.md` (this repo's own 13-section prompt scaffold), `docs/glossary.md`, `.claude/skills/goal/SKILL.md`, and ~45 existing records under `data/reference_pack/exemplars/`.

## Before you use these — what changed from the original ask, and why

You asked for prompts to build a comprehensive library of viral drone landscape videos scraped from YouTube, Instagram, and other platforms, with full processed/edited video files, to train an automation pipeline. I did not write that literally. Here's the grounded reason:

This repo already has that pipeline, and it already has an answer to "how do we source the library" — `.claude/specs/drone-video-pipeline/spec.md`'s Capability 3, which your own prior sessions worked through in detail. Its Scope-out section is explicit: **bulk-downloading and retaining full copies of all-rights-reserved videos "is an unambiguous ToS violation on both platforms with no private/internal-use carve-out, and is out of scope for any default/automated pipeline behavior."** Scaling past individually-researched, manually-verified exemplars into an unattended bulk pipeline is gated behind **Open Question 6 (Tier C legal sign-off)**, which `plan.md` confirms is **still open**. The pack today (~45 records, e.g. `pshepfpv-iceland-glaciers-fpv.json`, `chrisxgxc-the-last-dronie.json`) is built entirely on metadata + your own scoring functions' estimates, never on downloaded video files, with `local_media_path` left `null` for every all-rights-reserved record — mechanically enforced by `storage.py`.

So both prompts below do what you actually described — grow the library, target best-in-class/viral drone landscape content, cover places like Kyrgyzstan/Norway/Faroe Islands/Iceland, and feed your automation training loop — but by **extending the existing, already-legally-scoped reference-pack methodology** (individually sourced, independently re-verified, metadata + derived scores, footage never persisted unless a license is directly confirmed) rather than by launching a bulk YouTube/Instagram scrape-and-download job. If you actually want the Tier C conversation (bulk automation, or footage retention beyond CC/owned content), that's a separate, explicit decision — items (a)–(e) in spec Open Question 6 — not something either prompt below assumes on your behalf.

Two more things worth knowing before you run either prompt:

- **A parallel session is already live on this.** `.claude/activity.md` shows a local Claude Code session working this exact area in the last hour — it wrote `reference-pack-expand.workflow.js` to a scratchpad and added at least 4 new exemplars today (`chrisxgxc-the-last-dronie`, `acopian-guilfoyle-washed-up-reynisfjara-dronie` — Iceland's Reynisfjara — `captainvanover-fpv-cinematic-reel`, `rubencaser-fpv-dronie-railway-bridge`). Check current pack state before running either prompt below so you don't duplicate that work.
- **Kyrgyzstan and the Faroe Islands look like genuine gaps.** Scanning the ~45 existing filenames, Norway and Iceland already have entries (Lyngen Alps fjords, Iceland glaciers FPV, and now Reynisfjara), but nothing matches Kyrgyzstan or the Faroe Islands. Both prompts below prioritize those two.
- **The schema has no `location`/`geo_tag` or `platform_performance` (views/followers/engagement) field.** Geography today is only inferable from filenames/titles, and "viral" isn't captured structurally at all — only informally, in free-text `notes`. Both prompts flag this as a proposed schema addition rather than silently inventing new fields, the same way `editorial_style` was added in task 3.8. Worth a quick decision from you either way.

I could not fully verify `schema.py`'s exact field list and validator function names this session (I worked from `plan.md`'s documented schema plus real exemplar JSON records plus `README.md`, not a direct read of `schema.py`'s source) — both prompts tell the executing agent to confirm exact names against `schema.py` itself before writing anything, per this repo's own grounding rules.

---

## How the two prompts differ

Both target the same objective — grow the reference pack toward comprehensive, best-in-class coverage of elite drone-landscape content, prioritizing the Kyrgyzstan/Faroe Islands gap — under identical hard constraints (no bulk download, no Instagram media extraction, no fabricated fields). They diverge in the *decision procedure* for "is this candidate worth including," matching how this repo already uses each term elsewhere:

- **Deterministic** mirrors this repo's hookify Layer-1 routing and Capability 1's hard gates (`blackdetect`/`freezedetect`): fixed rules, an exact checklist, a fixed quota, binary include/exclude. Reproducible — two different agents running it should converge on the same candidates.
- **Bayesian** mirrors this repo's own `/goal` skill ("Bayesian entry→completion gates") and `docs/glossary.md`'s "Bayesian pipeline" ("weighing evidence as it goes"): a stated prior per location, evidence that shifts confidence up or down as each verification step completes, a diminishing-returns stopping rule instead of a fixed count, and low-confidence candidates surfaced for your sign-off instead of being silently included or excluded.

Run the deterministic one if you want a predictable, auditable batch fast. Run the Bayesian one if you want the agent to reason explicitly about uncertainty and tell you where coverage is genuinely thin versus just unfilled. They're safe to run back-to-back — both only add new files.

---

## Prompt 1 — Deterministic

```markdown
## Risk Tier
MEDIUM · Tier B (assisted)
Suggested execution mode: single-with-verify
Irreversible step(s): none — output is new JSON files under data/reference_pack/exemplars/ only.
Persisting any local_media_path (i.e. an actual video/image file) is a Tier C action → gate: confirm with the user before it happens, do not do it as part of this run even if a license appears to permit it.

## Role
You are a drone/travel videography researcher and metadata archivist maintaining the Capability-3 reference pack in this repo. Posture: implementation — apply a fixed, reproducible inclusion procedure identically to every candidate. This is not a creative/curatorial judgment call; it's a checklist.

## Objective (Definition of Done)
Done = data/reference_pack/exemplars/ contains up to 8 new ExemplarRecord JSON files (3 Kyrgyzstan, 3 Faroe Islands, 2 filling a Norway/Iceland subgenre not yet represented), each passing schema validation and storage.py's storage-layout validator, with zero fields that don't trace to a specific tool call made this session. A slot that cannot produce a verifiable real candidate is left unfilled and explicitly reported as such — never filled with an invented or unverified URL.

## Context (Stack & Jurisdiction)
Project: drone_video_ai, Capability 3 (Reference Pack) — a metadata-first exemplar dataset that gives Capability 1's quality-scoring pipeline a working definition of "award-winning" to measure against. Not a green-field scrape: this extends an existing, actively-maintained pack of ~45 records built the same way (see task 3.9 in tasks.md).
Stack: flat JSON files (one per exemplar) under data/reference_pack/exemplars/, validated against src/drone_video_ai/reference_pack/schema.py; storage-layout enforced by storage.py.

## Grounding Facts (read first)
- .claude/specs/drone-video-pipeline/spec.md — Capability 3 scope-in/scope-out and Acceptance Criteria (AC 71-74). Read the Scope-out section fully before doing anything else; it is the hard boundary for this task.
- .claude/specs/drone-video-pipeline/plan.md — the Exemplar Record schema section, and the "Open Questions — Resolution Status" section (#6, legal sign-off, is still open — do not act as though it's resolved).
- src/drone_video_ai/reference_pack/README.md — the "Scope reminder" and the YouTube Data API 30-day metadata refresh/expiry process (spec AC3.3); follow it for every YouTube-sourced field.
- src/drone_video_ai/reference_pack/schema.py + storage.py — the real, current ExemplarRecord fields and validator/storage-check function names. Confirm these directly; do not assume the field list below is exhaustive (this prompt was written from plan.md + real records, not a direct read of schema.py's source).
- data/reference_pack/exemplars/pshepfpv-iceland-glaciers-fpv.json and chrisxgxc-the-last-dronie.json — two fully worked examples of the expected rigor: real oEmbed/WebFetch verification quoted in `notes`, scores calibrated against named neighbors, composite_score computed via a real function call, honest nulls where something couldn't be verified. Match this shape exactly, not a lighter version of it.
- Read 3-5 more existing records before writing any new one, specifically to check whether Kyrgyzstan or Faroe Islands already have an entry (the pack may have grown since this was last checked) — do not duplicate an existing location/subgenre.

## Tools, Resources & Switch Variables
Tools: WebSearch and WebFetch for candidate discovery and primary-source verification; Bash + curl against YouTube's oEmbed endpoint (`https://www.youtube.com/oembed?url=...&format=json`) and, where needed, the watch-page HTML (grep for `licensedForReuse`, `lengthSeconds`, `dateText`) — use a realistic browser User-Agent string; Vimeo's oEmbed equivalent for vimeo.com sources; `python3 -c` invoking `drone_video_ai.highlight_extraction.composite.compute_composite_score` + `drone_video_ai.highlight_extraction.weights.default_weights()` to compute composite_score for real, never by hand. Gate command: `python3 -m pytest tests/reference_pack/ -q`.
Switch variables:
- location-quota: 3 Kyrgyzstan + 3 Faroe Islands + 2 Norway/Iceland-gap-filling = 8 total — wrong value → over/under-shoots the batch this prompt is scoped for.
- download-policy: never persist a video/image/audio file unless license_category is independently and directly confirmed (not inferred) as cc-by / cc-by-sa / cc-by-nd / cc0 / public-domain / owned — wrong value → violates storage.py's contract and spec Scope-out.
- instagram-policy: Instagram sources are metadata/caption/creator-reach research only — no media extraction or download of any kind — wrong value → crosses a line this pack has never crossed.
- autonomy-level: assisted — wrong value (autonomous) → records get written without the per-candidate verification checklist being visibly satisfied first.

## Task
For each of the 8 target slots, run this exact procedure in order. Do not move to the next slot until the current one either produces a valid record or is explicitly abandoned with a one-line stated reason.
1. Search (WebSearch: "[location] drone landscape video award", "[location] drone fpv viral", plus platform-scoped variants — YouTube, Instagram, Vimeo, SkyPixel, Drone Awards, AirVuz) for 3-5 real, currently-public candidate URLs.
2. For the strongest candidate, independently verify via oEmbed/WebFetch — do not trust a search-result snippet alone: title, creator/channel, platform, upload date, and any explicit Creative Commons marking. No explicit CC marking found = license_category "all-rights-reserved", full stop; never infer CC from "looks like it should be shareable."
3. Cross-check creator legitimacy/reach with one WebSearch (follower counts, prior awards, verified-account status). Record only what you actually find — do not state a follower count you didn't see in a result.
4. Estimate sharpness/exposure/motion_smoothness (0-1) by calibrating against at least 2 named existing exemplars already in the pack, cited by filename in `notes` — never assign a score with no calibration anchor.
5. Compute composite_score by actually invoking compute_composite_score()/default_weights() in this session's Python environment; paste the real invocation and result into `notes`.
6. Fill editorial_style (format / estimated_cut_count / avg_shot_length_seconds / transition_styles_observed / pacing_notes / review_method). Leave sub-fields null if not genuinely observed. `review_method` must accurately describe what you actually did — "live_playback_review" only if you actually loaded and inspected a `<video>` element.
7. Write the record to data/reference_pack/exemplars/{slug}.json. If step 2 cannot confirm a real, currently-public, attributable URL, abandon the slot with a one-line reason and move on — never invent a URL to hit the quota.

## Constraints (hard)
(1) No video, image, or audio file is ever downloaded or persisted for any all-rights-reserved record — local_media_path stays null. Fixed rule, not a judgment call.
(2) No Instagram media (reels, video, images) is ever extracted or downloaded — metadata and visible text only.
(3) Every non-null field traces to a specific tool call made this session, cited in `notes` — never filled from prior/background knowledge or plausible-sounding inference.
(4) Stay inside this session's 8-slot quota. Do not scale into an unattended/automated bulk pipeline — that is spec Open Question 6 (Tier C, still unresolved) and is explicitly out of scope here.
(5) If you hit a real schema gap (this session's read suggests there is currently no location/geo_tag field, and no field for platform-performance/view-follower signals) — stop and flag the proposed addition for the user's confirmation rather than silently inventing a new field, the way editorial_style was added in tasks.md 3.8. Do not block the rest of the batch on this — flag it once, keep going with the fields that do exist.

## Verification (tool-grounded — required before "done")
(1) `python3 -m pytest tests/reference_pack/ -q` passes green, including against the new records.
(2) Every new record validates against schema.py's real validator (confirm and use its actual name/import path — do not assume one).
(3) Grep-confirm `local_media_path` is null for 100% of new all-rights-reserved records — do not eyeball this.
(4) Re-open each new JSON file and confirm every tool call cited in `notes` actually appears in this session's own transcript. Self-assessment without this cross-check does not count as done.

## Examples (anchor the pattern)
Input/today: pshepfpv-iceland-glaciers-fpv.json and chrisxgxc-the-last-dronie.json — real oEmbed/WebFetch verification quoted in notes, scores calibrated against named pack neighbors, composite_score computed via the real function call, honest nulls where unverifiable (duration, cut count).
Expected output/target: up to 8 new files in the same directory, matching that shape and that rigor exactly — not a lighter-weight version.
Edge case: a strong-looking candidate that's actually a re-share/"best drone shots" compilation account with no traceable original creator — exclude it; constraint (3) can't be satisfied for a source with no verifiable original attribution.

## Deliverables (output shape)
Artifacts: up to 8 new data/reference_pack/exemplars/{slug}.json files, plus a short summary table at the end (slug | location | license_category | composite_score | verification method | included/abandoned-and-why).
Return format: the summary table as a markdown code fence; inline summary ≤150 words.

## Epistemic Balance
For every candidate you include, state the case FOR (why it's plausibly best-in-class — award, reach, technical craft) and the case AGAINST (what stayed unverifiable, what the notes field ultimately couldn't confirm) inside that record's `notes`, exactly as pshepfpv-iceland-glaciers-fpv.json and chrisxgxc-the-last-dronie.json already do. Do not write notes that only justify a decision you'd already made.

## Spec Anchor
This prompt executes the Implement phase (extending tasks.md §3, in the spirit of the already-completed 3.9 batch) against .claude/specs/drone-video-pipeline/spec.md, Capability 3. On any ambiguity (e.g. a candidate's license is genuinely unclear) — do not guess; leave the field null and flag it in the summary table. If the schema itself needs to change, amend plan.md's exemplar-record schema section first, then write code/data against the amended version — never improvise a new field silently.
```

---

## Prompt 2 — Bayesian

```markdown
## Risk Tier
MEDIUM · Tier B (assisted)
Suggested execution mode: single-with-verify, structured as an explicit entry-gate → evidence-gathering → completion-gate sequence (this repo's own /goal skill pattern — "Bayesian entry→completion gates" — applied here to content curation instead of code).
Irreversible step(s): none. Persisting any local_media_path remains a Tier C action → gate: confirm with the user before it happens, regardless of how confident you are in the license finding.

## Role
You are a drone/travel videography researcher applying probabilistic, evidence-weighted judgment to an inherently fuzzy question: whether the reference pack's coverage of elite, remote-landscape drone/FPV content is genuinely comprehensive. Posture: synthesis (accumulate and weigh uncertain evidence across candidates), with an assessment step at the end — did the evidence gathered actually raise your confidence, or just produce more files?

## Objective (Definition of Done)
Done = your own stated posterior confidence that "the pack's coverage of elite, remote-landscape drone/FPV content — the Kyrgyzstan/Faroe-Islands/Norway/Iceland genre — is comprehensive" has measurably increased from the prior you state before starting, with the new exemplar JSON files as the evidence trail for that shift. A batch that adds files without being able to articulate what confidence they bought you does not satisfy this objective, even if every file individually validates.
State the prior in one sentence before starting. State the posterior, and what moved it, when you finish.

## Context (Stack & Jurisdiction)
Project: drone_video_ai, Capability 3 (Reference Pack) — a metadata-first exemplar dataset giving Capability 1's quality-scoring pipeline a working definition of "award-winning" to measure against. Extends an existing, actively-maintained pack of ~45 records (see task 3.9 in tasks.md) — not a green-field scrape.
Stack: flat JSON files under data/reference_pack/exemplars/, validated against src/drone_video_ai/reference_pack/schema.py; storage-layout enforced by storage.py.

## Grounding Facts (read first)
- .claude/specs/drone-video-pipeline/spec.md — Capability 3 scope-in/scope-out and AC 71-74. The Scope-out section is a hard boundary, not evidence to be weighed — no amount of confidence overrides it.
- .claude/specs/drone-video-pipeline/plan.md — the Exemplar Record schema, and Open Question 6 (legal sign-off for anything beyond individually-verified exemplars) — confirmed still open. Treat "should we go beyond individual verification" as already answered "no" for this run, not as something your own confidence can unlock.
- src/drone_video_ai/reference_pack/README.md — the Scope reminder and the YouTube Data API 30-day refresh process (AC3.3).
- src/drone_video_ai/reference_pack/schema.py + storage.py — confirm the real, current field list and validator/storage-check function names directly; this prompt was written from plan.md + real records, not a direct read of schema.py's source.
- docs/glossary.md's "Bayesian pipeline" entry and .claude/skills/goal/SKILL.md — this repo's own established convention for entry-gate/evidence/completion-gate structure. This prompt follows that shape, applied to curation instead of implementation.
- data/reference_pack/exemplars/pshepfpv-iceland-glaciers-fpv.json — study its `notes` field closely: it already documents two independently-conflicting duration readings and chooses to leave the field null and record the uncertainty itself, rather than force a confident-looking number. That is the evidentiary honesty this prompt asks you to generalize, not a one-off.
- Read 3-5 more existing records before starting, specifically to check current Kyrgyzstan/Faroe Islands coverage — the pack may have grown since this was last checked, which would itself update your prior.

## Tools, Resources & Switch Variables
Tools: WebSearch and WebFetch for discovery and verification; Bash + curl against YouTube's oEmbed endpoint and (with a realistic User-Agent) watch-page HTML; Vimeo's oEmbed equivalent; `python3 -c` invoking compute_composite_score()/default_weights() for real, never by hand. Gate command: `python3 -m pytest tests/reference_pack/ -q`.
Switch variables:
- confidence-floor: do not silently include a candidate whose combined evidence (license verification + creator-reach corroboration + calibrated scores) leaves you below your own stated "would cite this as best-in-class" bar. Flag it as a low-confidence candidate for the user's sign-off instead of unilaterally including or excluding it — wrong value → either mediocre content quietly enters the pack, or good-but-uncertain content is quietly dropped and never surfaced.
- search-adaptivity: after every 2-3 candidates for a given location, reassess whether the search is surfacing genuinely distinct, strong material or re-finding the same creators/angles. If converging poorly, change the query strategy rather than repeating it — wrong value → a query gets rerun past the point of new evidence.
- stopping-rule: for each location, continue sourcing until two consecutive candidates fail to shift your stated confidence in that location's coverage (diminishing-returns stop) — not a fixed count. Wrong value → stops too early with a real gap left standing, or runs indefinitely with no exit condition.
- download-policy / instagram-policy / autonomy-level: identical to the deterministic prompt — never persist ARR media; Instagram is metadata-only; assisted, not autonomous.

## Task
Treat each location/subgenre gap as a hypothesis to test: "this pack can be brought to genuinely comprehensive coverage here." Start with Kyrgyzstan and the Faroe Islands (apparently zero current coverage — confirm this is still true first); only if time and evidence permit, move to deepening a Norway/Iceland subgenre not yet represented (e.g. a Faroe-style sea-stack/village angle distinct from the pack's existing fjord/glacier entries).
For each location:
1. State your PRIOR before searching: given the nearest existing pack neighbors (cite 1-2 by filename — e.g. abovehorizon-lyngen-alps-fjord as the nearest analog for a Faroe Islands fjord/sea-stack search) and general genre knowledge, how likely is it that 2-4 genuinely strong, independently-verifiable, distinct exemplars exist publicly for this location? One sentence.
2. Gather evidence using the same verification steps as a fixed checklist would (search → independent oEmbed/WebFetch check → creator-reach cross-check → calibrated scoring against named pack anchors → a real compute_composite_score() call) — but treat each step's result as evidence that shifts confidence, not a pass/fail gate. A candidate with strong technical scores but an unconfirmable license, or strong provenance but middling scores, is not automatically in or out — weigh both and say so.
3. After each candidate, restate your confidence in that location's coverage (increased / unchanged / decreased, and why) before deciding whether to keep searching or move on. This running log is what the completion gate checks against later.
4. Where genuine uncertainty remains after real effort (conflicting readings, unconfirmable duration, ambiguous license signals) — do not force a confident-looking value. Leave the field null and record the uncertainty itself as evidence, exactly as pshepfpv-iceland-glaciers-fpv.json already does.

## Constraints (hard)
(1) No video, image, or audio file is ever downloaded or persisted for any all-rights-reserved record — local_media_path stays null, no matter how high your confidence in the content's quality.
(2) No Instagram media is ever extracted or downloaded — metadata and visible text only.
(3) Every non-null field traces to a specific tool call made this session, cited in `notes`.
(4) Stay within individually-verified, single-session scope. High confidence in a location's coverage gap is not license to automate bulk sourcing — Open Question 6 (Tier C) is still open regardless of how justified automation might start to feel mid-task.
(5) If you hit a real schema gap (no location/geo_tag field; no platform-performance/view-follower field today) — flag the proposed addition once for the user's confirmation; do not block the rest of the task on it.
(6) A low-confidence candidate is never silently included to hit a target count — this prompt has no fixed count. Genuine under-coverage that remains after real effort is a valid, reportable outcome, not a failure to paper over.

## Verification (tool-grounded — required before "done")
(1) Same mechanical checks as the deterministic prompt: `python3 -m pytest tests/reference_pack/ -q` green; every new record validates against schema.py's real validator; local_media_path grep-confirmed null for every new all-rights-reserved record.
(2) Entry-gate check (before committing to the full location list): make one real oEmbed call against a known URL to confirm WebFetch/Bash-curl access actually works this session. Treat a failure here as a hard stop, not a soft assumption — consistent with how /goal's entry phase treats a missing precondition.
(3) Completion-gate check (before declaring done): for each location worked, does the stated posterior in the Objective section actually trace to specific evidence logged in Task step 3 — not to a general impression? This mirrors this repo's checkpoint-gate → synthesis-validator pattern (every conclusion must trace to a recorded checkpoint) applied to curation instead of code.
Self-assessment without both (1) and the trace-check in (3) does NOT count as done.

## Examples (anchor the pattern)
Input/today: pshepfpv-iceland-glaciers-fpv.json — two independently-conflicting duration readings (31.881s vs. 14.138s), resolved by leaving the field null and documenting the inconsistency as evidence of measurement uncertainty, not of the video's quality.
Expected output/target: new records that generalize this pattern — every genuinely uncertain field null with the uncertainty recorded as evidence, not smoothed over.
Edge case: a candidate with a clearly-genuine, large-following creator and strong footage, but where two independent verification attempts return inconsistent technical readings. Do not average or guess the inconsistent figure. Leave it null, note the inconsistency, and let the other converging evidence (creator reach, calibrated visual scores) still support inclusion if it's strong enough standing alone.

## Deliverables (output shape)
Artifacts: new exemplar JSON files (count determined by the stopping-rule switch variable, not fixed in advance) + one evidence log distinct from the per-record `notes` fields.
Return format: the evidence log as a markdown table (location | prior | candidates evaluated | included | posterior | what moved it); inline summary ≤150 words.

## Epistemic Balance
For each location, actively look for evidence AGAINST comprehensive coverage being achievable at all — e.g. "this location has very little published drone content because of airspace restrictions or low creator density" is a legitimate finding, not a failure to search harder. Do not let the desire to show progress bias evidence-gathering toward marginal candidates just to report a bigger batch.

## Spec Anchor
This prompt executes the Implement phase (extending tasks.md §3, in the spirit of the already-completed 3.9 batch) against .claude/specs/drone-video-pipeline/spec.md, Capability 3. On any ambiguity, amend the spec first, then act — including if your evidence-gathering starts to suggest the schema or the scope itself should change; never improvise divergence from what's signed off.
```

---

## Suggested next step

Both prompts are self-contained — paste either into a fresh session against this repo (or hand it to an agent) and it should run without needing this conversation's context. Given this repo already has `/prompt-engineering` (generate → critique-rewrite against 5 canonical failure modes → stability-test) and `/condition-audit`, you could formally test-drive these two before committing real search budget to either — that would also give you a principled, in-repo answer to "which actually performs better here" instead of just my judgment call.
