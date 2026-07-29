# Review: commit bc3a499 — "stop fabricating quality scores where the within-file rank is undefined"

Reviewer: normalization-review agent. Date 2026-07-29. Read-only review; nothing modified.

Files reviewed (all absolute paths under
`/Users/mac/Documents/photography-WORKFLOW-local/04-drone-video-editing-ai/`):

- `src/drone_video_ai/highlight_extraction/scoring_sharpness.py`
- `src/drone_video_ai/highlight_extraction/scoring_motion_smoothness.py`
- `src/drone_video_ai/common/manifest.py`
- `src/drone_video_ai/highlight_extraction/gates.py`
- `src/drone_video_ai/highlight_extraction/pipeline.py`
- `src/drone_video_ai/highlight_extraction/composite.py`
- `src/drone_video_ai/common/schema.py`
- `src/drone_video_ai/highlight_extraction/cli.py`, `weights.py`, `motion.py`
- `src/drone_video_ai/reel_stitching/edit_manifest.py`, `src/drone_video_ai/reference_pack/schema.py`
- `tests/highlight_extraction/*`, `tests/integration/test_corpus_footage.py`, `tests/common/test_manifest_schema.py`

---

## Verdict in one line

The core change is **correct and an unambiguous improvement** — it removes a real
fabrication, the two changed tests genuinely encoded the bug, and no None-crash path
exists anywhere in `src/`. But the fix stops one layer short: the fabrication it
removed from `scores.sharpness` reappears, in a different form, in
`composite_score`; one of the two new raw fields carries **inverted polarity relative
to its own name**; and the schema version was not bumped despite the same file's
docstring stating the rule that requires it.

**7 issues: 2 × P1, 4 × P2, 3 × P3.** (P3 count includes one test-coverage item.)

---

## Answers to the four questions asked

### (a) Every consumer of these scores — does any path break on `None`? — **NO. Clean.**

Grepped all of `src/` for `sharpness`, `motion_smoothness`, `composite_score`,
`composition`, `sharpness_raw`, `motion_smoothness_raw`. Complete consumer list:

| Consumer | Line | None-safe? |
|---|---|---|
| `gates.py::evaluate_gates` | `gates.py:130`, `:133` | YES — explicit `is not None` guard added by this commit |
| `composite.py::compute_composite_score` | `composite.py:45` | YES — `or score is None: continue` |
| `manifest.py::SegmentScores.to_dict` | `manifest.py:152-160` | YES — `json.dumps` emits `null` |
| `manifest.py::SegmentScores.from_dict` | `manifest.py:162-171` | YES — see (c) |
| `common/schema.py::validate_highlight_manifest` | `common/schema.py:172-176` | YES — presence-only check, never reads the value |
| `pipeline.py` assembly | `pipeline.py:141-166` | YES — indexes and passes through only |

Nothing in `src/` sorts, compares, thresholds, or does arithmetic on
`scores.sharpness` / `scores.motion_smoothness` outside those two guarded sites.
Specifically verified as NOT consumers:

- `reel_stitching/` — fully decoupled; `edit_manifest.py:5` states it does not read
  `HighlightManifest`. Grep confirms: zero references to any score field.
- `reference_pack/schema.py:146-173` — `ExemplarScores` is a separate,
  independently-populated dataclass; its `sharpness` was already `Optional[float]`
  and it is never fed from a highlight manifest.
- Nothing outside `src/` and `tests/` reads these fields (grepped the repo excluding
  `.venv/`).

`Segment.composite_score` and `ManifestSummary.avg_composite_score` are always
concrete floats (`composite.py:55-57` returns `0.0` rather than `None`), so
`pipeline.py:204`'s `sum(...) / len(...)` cannot see a `None`. Confirmed safe.

**This part of the change is complete and correct.** No P-level issue.

### (b) `composite.py`'s None-handling and renormalisation — **P1-A below. Not the intended semantic, or at least not a stated one.**

`composite.py:45` skips a null signal *and* omits its weight from `total_weight`
(`:53`), so the remaining signals are renormalised to sum to 1.0. Measured on the
actual default profile (`.venv/bin/python`, `weights.default_weights()` →
`default-v2`, four × 0.25):

```
single-shot file (both ranks null), exposure=1.0, composition=0.40 -> 0.7000
multi-segment BEST  (sharp 1.0, motion 1.0), exposure=1.0, comp=0.40 -> 0.8500
multi-segment WORST (sharp 0.0, motion 0.0), exposure=1.0, comp=0.40 -> 0.3500
```

Full detail in P1-A. Short form: for a single-shot file the composite collapses to
`mean(exposure, composition)`, and since exposure is measured at ≈1.0 on 28/28
working clips, that is `0.5 + 0.5 × composition` — a **monotone rescaling of
composition alone with a hard floor of 0.5**. The corpus is 100% single-shot, so
this is the normal case, not an edge case.

### (c) `SegmentScores.from_dict` backward-compatibility — **SOUND. No defect.**

`manifest.py:166-167` uses `d.get("sharpness_raw")` / `d.get("motion_smoothness_raw")`,
so a legacy v2 or pre-bc3a499 v3 manifest deserialises without `KeyError`.
`sharpness=d["sharpness"]` and `motion_smoothness=d["motion_smoothness"]` remain hard
lookups, which is correct — both keys have always existed in every version of this
schema and `common/schema.py:174` requires them.

Discrimination also works in practice, which is the non-obvious part and it holds:

- legacy single-segment record → `sharpness=1.0` (fabricated), `sharpness_raw=None`
- new single-segment record → `sharpness=None`, `sharpness_raw=920.12`

These are distinguishable, so a consumer *can* tell a fabricated legacy rank from a
genuine new one. The discriminator is `sharpness_raw is None`.

The caveat, which is what makes P2-D matter: that discriminator is **implicit**. It
works only because the new pipeline always populates the raw fields and
`common/schema.py` never required them (P2-E), so nothing enforces it. A version bump
would have made the discriminator explicit and declared rather than inferred.

### (d) Was the schema version bumped, and should it have been? — **NOT BUMPED. It should have been. See P2-D.**

`manifest.py:30` is unchanged at `MANIFEST_VERSION = 3`. By the rule stated in this
file's own docstring at `manifest.py:17-22`, it should be 4.

---

## Issues

### P1-A — `composite_score` silently changes estimator when a rank is null, and nothing in the manifest records it

**Where:** `src/drone_video_ai/highlight_extraction/composite.py:41-57` (the
`total_weight` accumulation), reached from
`src/drone_video_ai/highlight_extraction/pipeline.py:183-189`.

**What breaks.** When `sharpness` and `motion_smoothness` are both `None`,
`total_weight` is 0.5 instead of 1.0 and the surviving two signals are renormalised.
Measured against the real default weight profile:

| Case | scores | composite |
|---|---|---|
| single-shot file (ranks null) | exp 1.0, comp 0.40 | **0.7000** |
| multi-segment file, best segment | sharp 1.0, motion 1.0, exp 1.0, comp 0.40 | **0.8500** |
| multi-segment file, worst segment | sharp 0.0, motion 0.0, exp 1.0, comp 0.40 | **0.3500** |

Two files whose footage is identical by every *absolute* measure they share end up
0.15 apart purely because one happened to segment into one shot and the other into
several. Reduced further: with exposure pinned at ≈1.0 (measured: exactly 1.0 on
19/28 working clips, within 0.7% on all 28),

- null-rank segment: `composite = 0.5 + 0.5 × composition`, range **[0.50, 1.00]**
- ranked segment: `composite = 0.25 + 0.25 × (sharpness + motion + composition)`,
  range **[0.25, 1.00]**

Different estimators, different floors, both written to a field named
`composite_score` in an interchange format whose stated purpose (`manifest.py:4-5`)
is to be Capability 2's input for selecting **across files**. The manifest carries no
`total_weight`, no `contributing_signals`, no marker of any kind. A consumer cannot
detect which estimator produced a given number, and
`summary.avg_composite_score` (`pipeline.py:203-205`) averages the two kinds together.

Because `data/reference_pack/` measured every corpus file as a single continuous
shot, the 2-signal estimator is the *default* path for this project's own footage,
not a rare branch.

**Why this is the sharpest point in the review.** The commit's own thesis is: do not
emit a value where the inputs do not define one. It applied that to `scores.sharpness`
and then let `composite_score` quietly absorb the missing rank instead. The
internally consistent fix is one of:

1. emit `composite_score: null` when any nonzero-weighted signal is null (mirrors the
   commit's own principle exactly), or
2. keep the renormalisation but persist the applied basis — e.g. a per-segment
   `composite_weight_basis: 0.5` or `contributing_signals: ["exposure","composition"]`.

Either is a small change. Doing neither leaves the fabrication moved rather than
removed.

**Fairness note:** this is *not a regression*. Pre-commit, a null rank became 1.0 and
the composite was `0.75 + 0.25 × composition`, floor 0.75 — strictly worse. This is an
incomplete fix, not a new bug. It is still P1 because the field is the primary output
and the defect is invisible to every downstream consumer.

**No test covers it.** There is no `tests/highlight_extraction/test_composite.py` at
all (directory listing confirms: `test_gates.py`, `test_pipeline_manifest_output.py`,
`test_scoring_composition.py`, `test_scoring_exposure.py`,
`test_scoring_motion_smoothness.py`, `test_scoring_sharpness.py`,
`test_segmentation_boundaries.py`). The only call site of `compute_composite_score` in
the suite is `tests/reference_pack/test_schema_validation.py:188`, with all-float
inputs.

---

### P1-B — `motion_smoothness_raw` holds **jerk**, whose polarity is the inverse of the field name

**Where:** `src/drone_video_ai/highlight_extraction/pipeline.py:165`
(`motion_smoothness_raw=raw_jerk[i]`), declared at
`src/drone_video_ai/common/manifest.py:150`.

**What breaks.** `compute_raw_jerk_magnitude` documents itself at
`scoring_motion_smoothness.py:23-24` as *"Higher = less smooth (more erratic camera
motion)"*, and `invert_and_normalize:50` negates it precisely because of that. The
raw value is stored into the manifest **un-inverted** under a field named
`motion_smoothness_raw`. Higher `motion_smoothness_raw` therefore means **worse**
motion smoothness, while higher `sharpness_raw` means **better** sharpness — the two
sibling fields, added in the same commit and documented in the same comment block
(`manifest.py:146-150`) as "absolute, cross-file-comparable measurements", have
opposite polarity conventions.

**Concrete failure.** Capability 2 selects the best clips across files by
`max(scores.motion_smoothness_raw)` — the obvious reading of the field name, and the
one the `manifest.py:146-148` comment invites ("so that Capability 2 has something
cross-file-comparable to select on"). It gets the **jerkiest** segment in the library.
Nothing corrects this: `DEFAULT_NORMALIZATION["motion_smoothness"]`
(`manifest.py:128`) does not mention the raw field at all (see P2-C), and there is no
units or polarity annotation anywhere in the emitted document.

**Fix:** either store the negated/inverted value, or rename the field to
`jerk_magnitude_raw` (accurate, and the polarity trap disappears with the name), and
state the polarity in the `normalization` block. Renaming is the cleaner option and is
free right now, before any consumer exists.

This is the "mislabeled metric" failure class that `CLAUDE.md` records as already
having occurred once in this project's own history.

---

### P2-C — `DEFAULT_NORMALIZATION["motion_smoothness"]` was not updated while `["sharpness"]` was — stale claim in a sibling field, shipped in every manifest

**Where:** `src/drone_video_ai/common/manifest.py:126` vs `:128`.

Line 126 (updated by this commit):

```
"sharpness": "WITHIN-FILE RANK: in-video min-max over sampled frames -> [0,1]; null when undefined (n<2, or all segments equal). NOT comparable across files -- use sharpness_raw for that.",
```

Line 128 (untouched):

```
"motion_smoothness": "in-video min-max over inverse jerk magnitude -> [0,1]",
```

`motion_smoothness` acquired **exactly the same three properties** in this commit — it
is a within-file rank, it is now null when undefined, it is not comparable across
files — and its description states none of them, nor points at
`motion_smoothness_raw`. This is not a code comment: `DEFAULT_NORMALIZATION` is
serialised into the `normalization` block of every emitted manifest
(`manifest.py:281`, `:290`) and is a required key
(`common/schema.py:57`, `:157`). It is shipped, consumer-facing data that is now
factually incomplete.

This is the precise failure mode `CLAUDE.md` warns about: *"a fix landing in one
artifact while an identical stale claim survives in a sibling artifact, a sibling JSON
field, or even a second table row in the same file."* Here it is two entries of the
same dict, four lines apart.

**Concrete:** a consumer reading `normalization.motion_smoothness` from a v3 manifest
is told the value is in `[0,1]`, and then finds `null`.

---

### P2-D — schema version not bumped, contrary to the rule stated in this same file

**Where:** `src/drone_video_ai/common/manifest.py:30` (`MANIFEST_VERSION = 3`,
unchanged) and the module docstring at `manifest.py:11-22` (also unchanged).

That docstring sets the project's own bump criterion, verbatim:

> "Per plan.md's 'Milestone 2 (composition scoring) changes to this schema' note, this
> composite-score-affecting change bumps `MANIFEST_VERSION` from 2 to 3 — **not a
> silent, purely-additive change to version 2, since consumers reading
> `composite_score` now see a value computed over four signals instead of three.**"

bc3a499 does two things that meet that criterion at least as strongly:

1. `composite_score` is now, for single-shot files, computed over **two** signals
   instead of four (P1-A) — the identical class of change, in the identical field, one
   step further.
2. `scores.sharpness` and `scores.motion_smoothness` change **type**, `number` →
   `number | null`. That is not additive at all; it is a breaking type change for any
   consumer doing `seg["scores"]["sharpness"] > 0.5`, which raises
   `TypeError: '>' not supported between instances of 'NoneType' and 'float'`.

The two genuinely new fields (`sharpness_raw`, `motion_smoothness_raw`) are additive
and would not on their own justify a bump. The type change and the estimator change
do.

**Concrete consequence:** a manifest written on 2026-07-27 and one written on
2026-07-29 both say `"version": 3`, and they are not interchangeable. The only way to
tell them apart is the implicit `sharpness_raw is None` heuristic from (c), which
nothing declares or enforces.

`tests/highlight_extraction/test_pipeline_manifest_output.py:81-84` hard-asserts
`doc["version"] == 3`, so bumping is a two-line change plus that assertion.

---

### P2-E — `common/schema.py` was not updated; the new raw fields are not part of the validated contract

**Where:** `src/drone_video_ai/common/schema.py:172-176` (and the mirrored
`HIGHLIGHT_MANIFEST_SCHEMA` literal at `:47`, `:57`).

`validate_highlight_manifest` still requires only
`["sharpness", "exposure", "motion_smoothness", "composition"]` inside
`segments[i].scores`. The pipeline now always emits `sharpness_raw` and
`motion_smoothness_raw`, and the entire justification for allowing a null rank is that
*"a null rank now costs no information"* — which is true only if the raw value is
present.

**Concrete:** a manifest with `sharpness: null` and no `sharpness_raw` key passes
`validate_highlight_manifest` cleanly and is written by `cli.py:96-101` with exit code
0, carrying literally no sharpness information at all. Nothing in the codebase
prevents or detects that document.

This is also the enforcement gap that makes the (c) legacy-discriminator implicit
rather than guaranteed.

**Fix:** add both keys to the required list (gated on `version >= 4` if legacy
manifests must keep validating).

---

### P2-F — `--min-sharpness-floor` silently no-ops on single-shot files, and its help text now describes the wrong quantity

**Where:** `src/drone_video_ai/highlight_extraction/gates.py:130` (the skip),
`src/drone_video_ai/highlight_extraction/cli.py:58-63` (the flag and its help),
`src/drone_video_ai/highlight_extraction/gates.py:23` (the constant's comment).

Two distinct problems, same flag:

1. **Silent no-op.** `drone-highlights clip.mp4 -o m.json --min-sharpness-floor 0.9`
   against any of the 8 corpus files (all measured single-shot → `sharpness = None`)
   produces zero exclusions, exits 0, prints no warning, and records nothing in the
   manifest indicating the gate was not evaluated. The operator asked for a hard
   quality floor and got no gate at all. The skip itself is the *right* behaviour —
   `gates.py:124-129` argues it well — but silence about it is not. Either warn on
   stderr or record a `gates_skipped: ["min_sharpness_floor"]` entry alongside
   `gate_failures`.

2. **Wrong quantity.** `cli.py:62` reads *"minimum normalized [0,1] sharpness score to
   pass"* and `gates.py:23` reads *"normalized [0,1]"*. This commit re-characterised
   that value as a **within-file rank**, not a quality score
   (`scoring_sharpness.py:68-72`, emphatically). On a multi-segment file
   `--min-sharpness-floor 0.5` therefore excludes roughly the bottom half of *every*
   file by construction, however sharp the file is in absolute terms — it is a
   percentile cut, not a floor. The help text now actively misleads. If a real
   sharpness floor is wanted, it should be applied to `sharpness_raw`.

Problem 2 is arguably pre-existing, but bc3a499 is the commit that made the
distinction explicit and is where the docs should have followed.

---

### P3-G — three type annotations now lie about `None`

- `src/drone_video_ai/highlight_extraction/gates.py:98` — `sharpness_score: float`,
  but `pipeline.py:150` passes `normalized_sharpness[i]`, which is
  `Optional[float]`. (`exposure_score: float` at `:99` is genuinely always a float —
  correct as annotated, and the `is not None` guard at `:133` is harmless defensive
  symmetry.) `gates.py` does not currently import `Optional`.
- `src/drone_video_ai/highlight_extraction/composite.py:19` — `sharpness: float`,
  and `:21` — `motion_smoothness: float`. Both receive `None` from
  `pipeline.py:184`/`:186` on every single-shot file. `Optional` is already imported
  at `composite.py:13` and already used correctly for `composition` at `:22`, so this
  is a two-word fix.

Behaviour is correct in all three cases; only the declared contract is wrong. No
type-checker runs in this repo today, so this is documentation accuracy, not a
runtime risk.

---

### P3-H — the two normalisers use different degeneracy tests while the docstring claims they are identical

**Where:** `scoring_sharpness.py:92` uses `if hi - lo <= 0.0`;
`scoring_motion_smoothness.py:53` uses `if hi - lo < 1e-9`.
`scoring_motion_smoothness.py:41-42` states *"Mirrors
`scoring_sharpness.min_max_normalize`'s contract exactly."*

**Honest assessment:** I could **not** construct a reachable input where the two
diverge, and I am not going to invent one. Laplacian variances are of order 10^1–10^3,
so a nonzero difference below 1e-9 requires ~1e-12 relative precision, which realistic
identical content produces as exactly 0.0 (caught by both). In the other direction,
mean |jerk| over sub-pixel optical flow is of order 1e-3 or larger, far above the 1e-9
absolute epsilon. **This is a docstring-accuracy defect, not a behavioural one** — the
claim "exactly" is false as written. Either align the tests or soften the claim.

(One asymmetry that *is* fine and I checked specifically: `min_max_normalize([])`
returns `[]` via `[None] * 0`, matching `invert_and_normalize`'s explicit
`if not raw_jerk_values: return []`. Both correct.)

---

### P3-I — the two behavioural changes with real consequences are untested

The commit reports "93 tests pass" and updated two tests correctly (both genuinely
encoded the old fabricating behaviour; the changes are legitimate, well-commented, and
I would have made the same ones). But:

1. **`gates.py`'s None-skip has no test that can fail.**
   `tests/highlight_extraction/test_gates.py:54`
   (`test_evaluate_gates_reports_min_sharpness_and_exposure_floor_failures`) passes
   float scores. The integration test
   `tests/integration/test_corpus_footage.py:125-146` reaches `sharpness = None` but
   only under the **default floor of 0.0**, where "skipped" and "passed" are
   indistinguishable (`0.0 < 0.0` is False either way). Nothing anywhere asserts that a
   **nonzero** floor is skipped rather than fired. Pre-commit, that same input would
   have raised `TypeError`; post-commit it silently passes; no test distinguishes
   those outcomes.

2. **`composite.py` has no test file at all** — so P1-A's renormalisation is
   completely uncovered.

Per `.claude/CLAUDE.md`'s Tests-as-Truth principle ("if you believe a scenario is
untested, add a test — hedging without adding a test is prohibited"), these two
branches' behaviour is not currently established by the suite. Two tests, roughly ten
lines total:

```
evaluate_gates(..., sharpness_score=None, ..., config=GateConfig(min_sharpness_floor=0.9))
    -> "min_sharpness_floor" not in failures
compute_composite_score(None, 1.0, None, 0.4, default_weights()) -> 0.70   # documents the basis switch
```

---

## What is right, and should not be changed

Stated because a review that only lists defects misrepresents this commit.

- **The core diagnosis is correct and the evidence is real.** `min_max_normalize([0.02])`
  and `min_max_normalize([123.4])` both returning `[1.0]` is a genuine fabrication, and
  "20 of 20 values saturated at exactly 0.0 or 1.0 across the corpus" is a measurement,
  not an intuition. The fix targets the actual defect.
- **`None` is the right sentinel**, not 0.5 or 0.0. Both alternatives would have been
  new invented constants — exactly what the Constitution prohibits.
- **Carrying the raw values alongside is the right design.** It is what makes the null
  free rather than lossy, and it follows this project's own established provenance
  idiom (`editorial_style.json`'s measured|inferred|assumed labels), rather than
  inventing a new one.
- **The `gates.py` skip is the right call**, and the seven-line comment at
  `gates.py:124-129` justifies it from a measurement rather than from taste. Firing the
  gate would have excluded the only segment of every file in the corpus.
- **Both changed tests genuinely encoded the bug.** Changing them was correct, not
  test-fitting, and both carry a dated comment explaining why — which is the right way
  to do it.
- **Backward compatibility in `from_dict` is sound** (see (c)) and the legacy-vs-new
  discrimination actually works.
- **No None-crash path exists anywhere in `src/`** (see (a)). The guard coverage is
  complete.

---

## Recommended order of work

1. **P1-A** — decide the composite semantic (null the composite, or persist the weight
   basis). Everything else is smaller.
2. **P1-B** — rename `motion_smoothness_raw` → `jerk_magnitude_raw` (or invert the
   stored value). Free now; expensive once a manifest is in anyone's hands.
3. **P2-D** — bump `MANIFEST_VERSION` to 4 with 1 and 2 folded in, so there is one
   version boundary rather than three.
4. **P2-C**, **P2-E**, **P2-F** — the documentation/contract catch-up. Per `CLAUDE.md`'s
   standing instruction, grep all sibling artifacts before calling any of these done.
5. **P3-G/H/I** — polish plus the two missing tests.

---

## Verification performed

- Read every file listed at the top of this document, in this session.
- `grep -rn --include='*.py' -E "sharpness|motion_smoothness|composite_score|composition" src/`
  — full consumer enumeration for (a).
- Repo-wide grep excluding `.venv/` for consumers outside `src/` and `tests/` — none found.
- `git show --stat bc3a499` and `git show bc3a499 -- tests/` — confirmed the exact
  diff, the two changed tests, and the seven touched files. (Read-only git inspection;
  nothing written, no repo state changed.)
- Executed `compute_composite_score` under `.venv/bin/python` against the real
  `default_weights()` profile to produce the P1-A table — the numbers there are
  measured in-session, not derived by hand.
- Unit suite: launched `.venv/bin/python -m pytest -q`; it exceeded the 120s foreground
  budget (it includes the `integration` marker suite, which decodes real footage) and
  was still running when this review was written. **I did not confirm the 93-test pass
  count myself — treat the commit's "93 tests pass" claim as unverified in this
  session.** No finding in this review depends on it.
