# Plan: drone-video-pipeline

Status: DRAFT
Spec: `.claude/specs/drone-video-pipeline/spec.md`

This plan resolves the spec's Open Questions to the extent already decided, fixes a concrete
src-layout project structure, and defines the exact JSON manifest schema shared between
Capability 1's output and Capability 2's input. It does not contain application code.

Grounding notes from this session (verified, not assumed):
- Repo is already a git repo (`git log` shows 2 prior commits: initial publish, then
  "chore: relocate sample footage to data/raw/ convention"). `.gitignore` already excludes
  the inherited `claude-template` maintainer content and the two raw files over 100MB
  (`instagram_reel_v34_all_kb_full.mp4`, `viral_test_v2_4k.mp4`).
- `data/raw/` exists and contains `DJI_0355/` (with the legacy `manifest.json` + 4 split clips)
  and 4 additional sample mp4s (`instagram_reel_test.mp4`, `instagram_reel_v34_all_kb_full.mp4`,
  `viral_test_v2.mp4`, `viral_test_v2_4k.mp4`). All 4 top-level sample mp4s probe as
  h264/yuv420p/30fps, but **`color_range`/`color_space`/`color_transfer`/`color_primaries`
  all read `unknown` via `ffprobe`** on every sample file — this is a real constraint the
  Capability 2 color-metadata-pinning code and tests must handle (pin-through-if-present,
  don't assume the tag exists; the AC2 "exactly matches source" check must still pass when
  source and output both read `unknown`/unset for the same tag).
- No `pyproject.toml` or `src/` exists yet — this is a greenfield package layout decision, not
  a refactor.
- Toolchain confirmed present in this environment: Python 3.10.13, `ffmpeg` 8.0.1 (built with
  `--enable-gpl`, has `xfade`/`blackdetect`/`freezedetect`/`signalstats` filters), `ffprobe`
  8.0.1, OpenCV (`cv2`) 4.13.0, PySceneDetect (`scenedetect`) 0.6.7.1, pytest 8.4.2.
- The legacy `data/raw/DJI_0355/manifest.json` (`"version": 1`) confirms the precedent schema
  shape: `score` (0–100 float), `motion_energy` (0–100 float), `motion_type` (enum string),
  per-clip `start_time`/`end_time`/`duration`, and a `post_processing` block
  (`color`, `stabilized`, `letterbox`, `auto_speed`) that this pipeline must NOT reproduce.

## Directory Layout

```
p-drone-video-editing-ai/
├── pyproject.toml
├── src/
│   └── drone_video_ai/
│       ├── __init__.py
│       ├── common/
│       │   ├── __init__.py
│       │   ├── manifest.py            # Segment/HighlightManifest dataclasses + versioned (de)serialization
│       │   ├── schema.py              # JSON-schema dicts for highlight manifest, edit manifest, exemplar record
│       │   └── ffprobe.py             # ffprobe subprocess wrapper: codec/resolution/pix_fmt/timebase/color-metadata probe
│       ├── highlight_extraction/
│       │   ├── __init__.py
│       │   ├── cli.py                 # `drone-highlights` entrypoint (argparse)
│       │   ├── segmentation.py        # PySceneDetect AdaptiveDetector scene boundaries + union with motion minima
│       │   ├── motion.py              # optical-flow (goodFeaturesToTrack + calcOpticalFlowPyrLK) per-frame motion transform series + derivative-minima detector
│       │   ├── scoring_sharpness.py   # cv2.Laplacian(...).var() per sampled frame + in-video min-max normalization to 0-1
│       │   ├── scoring_exposure.py    # histogram-based over/under-exposure clipping fraction -> 0-1
│       │   ├── scoring_motion_smoothness.py  # jerk/acceleration of the motion.py transform series -> 0-1 (inverse-normalized)
│       │   ├── gates.py               # ffmpeg blackdetect/freezedetect wrappers + configurable min-sharpness/min-exposure floors
│       │   ├── weights.py             # versioned, documented scoring-weight config (dataclass + default weight set with a `weights_version` string)
│       │   ├── composite.py           # weighted composite score from per-signal scores + weights.py config
│       │   └── pipeline.py            # orchestrates segmentation -> scoring -> gating -> manifest emission (+ optional clip rendering)
│       ├── reel_stitching/
│       │   ├── __init__.py
│       │   ├── cli.py                 # `drone-stitch` entrypoint (argparse)
│       │   ├── edit_manifest.py       # EditManifest/EditEntry dataclasses + versioned (de)serialization
│       │   ├── pacing.py              # target-total-duration / per-clip-trim / ordering step, prior to rendering
│       │   ├── color_pinning.py       # ffprobe-sourced color metadata extraction + xfade encode arg construction (pins colorspace/primaries/trc/range from source, tolerates `unknown`/unset tags)
│       │   ├── render.py              # concat-demuxer (`-c copy`) hard-cut rendering + xfade transition-window rendering
│       │   └── verify.py              # `ffmpeg -f framemd5` byte-exact verification between source and output frame ranges
│       └── reference_pack/
│           ├── __init__.py
│           ├── schema.py              # ExemplarRecord dataclass + JSON schema (per spec AC 71-74 fields)
│           └── storage.py             # storage-layout validator: no locally-stored file for any all-rights-reserved record
├── tests/
│   ├── conftest.py                    # shared fixtures: synthetic test clips generated via ffmpeg `lavfi` sources (color bars, black frames, frozen frames) — no large binaries checked in
│   ├── common/
│   │   └── test_manifest_schema.py
│   ├── highlight_extraction/
│   │   ├── test_segmentation_boundaries.py      # AC1.3 — asserts every emitted start/end is boundary-set member
│   │   ├── test_scoring_sharpness.py            # AC1.6 — high-Laplacian-variance clip scores above low-variance clip
│   │   ├── test_scoring_exposure.py
│   │   ├── test_scoring_motion_smoothness.py
│   │   ├── test_gates.py                        # AC1.2 — black-frame clip must hard-gate-fail
│   │   └── test_pipeline_manifest_output.py      # AC1.1, AC1.4, AC1.5 — schema shape, duration bounds, version + no post_processing fields
│   ├── reel_stitching/
│   │   ├── test_concat_demuxer_framemd5.py       # AC2.1
│   │   ├── test_xfade_color_metadata.py          # AC2.2
│   │   ├── test_forbidden_filters_lint.py        # AC2.3 — greps render.py/color_pinning.py source for forbidden filter names
│   │   └── test_pacing_tolerance.py              # AC2.5
│   └── reference_pack/
│       ├── test_schema_validation.py             # AC3.1
│       └── test_storage_layout_no_arr_files.py   # AC3.2
├── data/
│   ├── raw/                           # existing — source footage (already relocated; unchanged by this plan)
│   ├── interim/                       # NEW — rendered highlight-extraction output clips (gitignored; regenerable from manifest + raw)
│   ├── output/                        # NEW — stitched reel renders (gitignored; regenerable from edit manifest + interim/raw)
│   ├── manifests/                     # NEW — emitted highlight manifests + edit manifests (small JSON; may be committed selectively)
│   └── reference_pack/
│       ├── exemplars/                 # NEW — one JSON record per exemplar (metadata + derived analysis); safe to commit, no video bytes
│       └── media/                     # NEW — reserved for individually-verified CC BY/CC0/public-domain/owned footage only; empty in this pass
└── .claude/specs/drone-video-pipeline/{spec.md, plan.md, tasks.md}
```

`data/interim/`, `data/output/` and any non-JSON contents of `data/reference_pack/media/` must be
added to `.gitignore` when created (Tasks list item), consistent with the existing pattern of
excluding large raw files >100MB.

## Package / CLI naming

- Distribution + import name: `drone_video_ai` (src-layout: `src/drone_video_ai/`).
- `pyproject.toml` build backend: `setuptools` (or `hatchling` — either is acceptable; Tasks
  will pin one during scaffolding). Console scripts:
  - `drone-highlights` → `drone_video_ai.highlight_extraction.cli:main`
  - `drone-stitch` → `drone_video_ai.reel_stitching.cli:main`
- Runtime dependencies (Milestone 1 scope only): `opencv-python`, `scenedetect[opencv]`,
  `numpy`. `ffmpeg`/`ffprobe` are external binaries invoked via subprocess, not pip
  dependencies — document a minimum-version note (this session confirms 8.0.1 works; no
  known minimum floor has been tested below that).
- Dev/test dependency: `pytest`.
- Explicitly excluded (per spec Scope-out): `ultralytics`/YOLOv8 (AGPL-3.0), `pyiqa`/IQA-PyTorch
  (non-commercial licenses), any TransNetV2/PyTorch/TensorFlow shot-boundary dependency.
- Deferred-milestone-only dependencies (do NOT add to Milestone 1 `pyproject.toml`):
  `opentimelineio` + `otio-cmx3600-adapter` (Capability 2 Milestone 2).

## Shared Manifest Schema (Capability 1 output == Capability 2 input contract)

Two distinct JSON documents exist. The **highlight manifest** is Capability 1's output. The
**edit manifest** is Capability 2's input; it MAY be authored by hand, by a future selection
tool, or by copying `segments[].start_time/end_time` + chosen `clip_path`s out of one or more
highlight manifests — Capability 2's `edit_manifest.py` only needs to parse the edit-manifest
shape below, decoupling the two capabilities per the spec's stitching-input/output contract
(spec line 24, Scope-out line 44).

### 1. Highlight manifest (`drone_video_ai.common.manifest.HighlightManifest`)

```jsonc
{
  "version": 2,                          // int; bumped from legacy precedent's 1 because this
                                          // schema drops post_processing and adds per-signal scores
  "source_file": {
    "path": "string",                    // absolute or repo-relative path as provided at CLI invocation
    "name": "string",
    "duration": 0.0,                     // float seconds, from ffprobe
    "width": 0,                          // int, from ffprobe
    "height": 0,                         // int, from ffprobe
    "fps": 0.0,                          // float, from ffprobe r_frame_rate
    "codec": "string",                   // from ffprobe codec_name
    "pix_fmt": "string"                  // from ffprobe pix_fmt
  },
  "scoring_weights": {
    "weights_version": "string",         // e.g. "default-v1"; resolves AC1's "documented,
                                          // versioned scoring-weight configuration" requirement
    "weights": {
      "sharpness": 0.0,
      "exposure": 0.0,
      "motion_smoothness": 0.0,
      "composition": 0.0                 // MUST be 0.0 in Milestone 1 (composition not scored yet
                                          // — see Milestone 2); kept as an explicit field so
                                          // enabling composition later is a weights-config change,
                                          // not a schema change
    }
  },
  "candidate_boundaries": {
    "scene_boundaries": [0.0],           // float seconds; PySceneDetect AdaptiveDetector output
    "motion_minima_boundaries": [0.0],   // float seconds; motion-derivative local minima
    "union_boundaries": [0.0]            // sorted union of the two sets above — this is the
                                          // Stage-1 candidate boundary set that AC1.3's test
                                          // asserts every emitted segment start/end is a member of
  },
  "normalization": {
    "sharpness": "in-video min-max over sampled frames -> [0,1]",
    "exposure": "1 - (clipped-pixel fraction from histogram) -> [0,1]",
    "motion_smoothness": "in-video min-max over inverse jerk magnitude -> [0,1]",
    "composition": "not scored in this schema version (Milestone 2, deferred)"
  },
  "segments": [
    {
      "segment_id": "string",            // e.g. "seg_0001", stable within one manifest
      "start_time": 0.0,
      "end_time": 0.0,
      "duration": 0.0,
      "scores": {
        "sharpness": 0.0,                // 0-1
        "exposure": 0.0,                 // 0-1
        "motion_smoothness": 0.0,        // 0-1
        "composition": null              // always null in Milestone 1 output
      },
      "composite_score": 0.0,            // 0-1; weighted sum over sharpness/exposure/motion_smoothness
                                          // only (composition weight is 0.0 per scoring_weights above)
      "gate_status": "passed"            // "passed" | "failed"
    }
  ],
  "excluded_segments": [
    {
      "segment_id": "string",
      "start_time": 0.0,
      "end_time": 0.0,
      "duration": 0.0,
      "scores": { "sharpness": 0.0, "exposure": 0.0, "motion_smoothness": 0.0, "composition": null },
      "gate_status": "failed",
      "gate_failures": ["blackdetect"]   // non-empty list of: "blackdetect" | "freezedetect" |
                                          // "min_sharpness_floor" | "min_exposure_floor"
    }
  ],
  "summary": {
    "total_segments": 0,
    "total_duration": 0.0,
    "avg_composite_score": 0.0,
    "scenes_detected": 0,
    "motion_minima_detected": 0,
    "segments_excluded": 0
  }
}
```

Field-by-field rationale tying back to Acceptance Criteria:
- AC1.1 (per-segment fields + normalized scores + stated normalization method) → `segments[]`
  + top-level `normalization` block.
- AC1.2 (hard-gate exclusions distinguishable from low scores) → `excluded_segments[]` is a
  structurally separate array from `segments[]`, carrying `gate_failures`; a low-scoring but
  passing segment stays in `segments[]` with `gate_status: "passed"`.
- AC1.3 (no boundary strictly inside a scene/maneuver) → `candidate_boundaries.union_boundaries`
  is the exact set the test asserts membership against.
- AC1.4 (min/max duration bounds) → enforced in `pipeline.py`; no schema field needed beyond
  `duration`, but `weights.py`/CLI carries the configured `min_duration`/`max_duration` bounds
  (default 2–15s per spec; the legacy 7–15s stays as a documented default profile, not a
  hardcoded constant).
- AC1.5 (`"version": N`, no `post_processing`) → `"version": 2`; no `post_processing` key
  anywhere in this schema.
- AC1.6 (test suite against synthetic/sample inputs) → `tests/highlight_extraction/`.

Milestone 2 (composition scoring) changes to this schema, when built, will be additive only:
populate `scores.composition` with a real 0-1 value, give `scoring_weights.weights.composition`
a nonzero default, and update `normalization.composition`. `version` bumps to 3 at that point
since the composite-score computation changes (not purely additive to consumers who read
`composite_score`).

### 2. Edit manifest (`drone_video_ai.reel_stitching.edit_manifest.EditManifest`)

```jsonc
{
  "version": 1,
  "target_duration": null,               // float seconds, or null for "use full entries as-is"
  "entries": [
    {
      "clip_path": "string",             // path to a source clip (raw footage or a rendered
                                          // highlight-extraction clip) — never modified in place
      "in_tc": 0.0,                      // float seconds, in-point within clip_path
      "out_tc": 0.0,                     // float seconds, out-point within clip_path
      "transition_to_next": {
        "type": "cut",                   // "cut" | "xfade" | "wipeleft" | "wiperight" | ... (any
                                          // ffmpeg xfade transition name; "cut" means concat-demuxer
                                          // hard cut, no xfade filter invoked)
        "duration": 0.0                  // float seconds; must be 0.0 when type == "cut"
      }
    }
  ]
}
```

- `render.py` reads consecutive `entries` and decides per-adjacent-pair whether the concat
  demuxer stream-copy path applies (matching codec/profile/resolution/pix_fmt/timebase,
  `type == "cut"`) or the `xfade` lossless-transition path applies (`type != "cut"`).
- `color_pinning.py` supplies the `-colorspace`/`-color_primaries`/`-color_trc`/`-color_range`
  args for any `xfade` encode, read via `ffprobe` from the **first** clip in the transition
  pair (documented, since two adjacent clips could in principle differ — Milestone 1 assumes
  they don't for xfade-eligible pairs and asserts this rather than silently picking one; see
  Tasks). Where `ffprobe` reports `unknown`/absent for a tag (confirmed to happen on this
  repo's own sample footage — see Grounding notes above), the pinning step passes through
  that same "unset" state rather than substituting a default, so AC2's "exactly matches
  source" check remains satisfiable.
- `verify.py`'s framemd5 check operates on the rendered output file against the same frame
  ranges from `clip_path` for every `entries[]` pair whose transition was `"cut"`.

### 3. Exemplar record (`drone_video_ai.reference_pack.schema.ExemplarRecord`)

```jsonc
{
  "version": 1,
  "source_url": "string",
  "platform": "youtube",                 // "youtube" | "vimeo" | "other"
  "license_category": "all-rights-reserved",  // "all-rights-reserved" | "cc-by" | "cc-by-nc" |
                                               // "cc-by-sa" | "cc-by-nd" | "cc0" | "public-domain" | "owned"
  "title": "string",
  "creator": "string",
  "duration": 0.0,
  "retrieval_date": "YYYY-MM-DD",
  "scores": {
    "sharpness": 0.0, "exposure": 0.0, "motion_smoothness": 0.0,
    "composition": null,                 // same Milestone-1-deferred convention as the highlight manifest
    "composite_score": 0.0
  },
  "award_or_showcase_provenance": null,   // nullable string, e.g. "SkyPixel Awards 2023 Finalist"
  "local_media_path": null                // MUST be null unless license_category is one of
                                           // cc-by/cc-by-sa/cc-by-nd/cc0/public-domain/owned
}
```

`storage.py`'s validator asserts: for every exemplar JSON in `data/reference_pack/exemplars/`,
if `license_category == "all-rights-reserved"` then `local_media_path` is `null` AND no file
exists under `data/reference_pack/media/` whose name matches that exemplar's id — this is the
mechanical AC3.2 check.

## Milestone Split

### Capability 1 — Highlight extraction

**Milestone 1 (this pass, build now):**
Scene-boundary segmentation (PySceneDetect `AdaptiveDetector`) unioned with motion-derivative
local minima; sharpness scoring (Laplacian variance); exposure scoring (histogram-based);
motion-smoothness scoring (optical-flow-based, pure OpenCV — no `vid.stab`, no GPL
entanglement risk); hard gates (`blackdetect`/`freezedetect` + min-sharpness/min-exposure
floors); composite scoring with `composition` weight fixed at 0.0; versioned JSON manifest
emission per the schema above; test suite.

**Milestone 2 (built — see tasks.md 1.21-1.25):**
Composition scoring — OpenCV `saliency`-module rule-of-thirds distance, vendored Hough-line
horizon-tilt scorer. MediaPipe object detection was evaluated and explicitly **not** integrated
(the saliency centroid already supplies sufficient spatial weighting; see
`scoring_composition.py` module docstring). Schema changes were additive as planned: `version`
bumped to 3, `composition` populated with a real `[0,1]` value, and its weight made nonzero via
a new `"default-v2"` named weight profile (`weights.py`) — the legacy `"default-v1"` profile is
preserved unchanged for callers that explicitly request it.

### Capability 2 — Reel stitching

**Milestone 1 (this pass, build now):**
JSON edit-manifest format (above); ffmpeg concat-demuxer hard-cut rendering with `-c copy`;
ffmpeg `xfade` transition rendering scoped to transition windows with `ffprobe`-sourced
color-metadata pinning; framemd5-based byte-exact verification test; forbidden-filter lint
test (AC2.3).

**Milestone 2 (built — see tasks.md 2.12-2.14):**
OpenTimelineIO (`.otio`) export and CMX3600 EDL export via `otio-cmx3600-adapter`, plus the
schema/structural validation check described in AC2.4, implemented in `otio_export.py`.
`opentimelineio`/`otio-cmx3600-adapter` are now real `pyproject.toml` dependencies (added only
at this milestone, not Milestone 1, per the original plan).

### Capability 3 — Reference pack

**Build now, full spec scope (single pass, no milestone split — already narrow per spec):**
Exemplar schema + storage-layout validator (above); exactly one manually-curated worked
example, sourced and attributed by hand during implementation (Tasks list requires the
implementer to locate and cite one real, currently-public drone landscape/wildlife video —
e.g. a known SkyPixel/Drone Awards showcase entry or a notable creator upload — record its
true observed `license_category` as found, which for a typical YouTube upload will be
`all-rights-reserved` unless the uploader has explicitly marked it Creative Commons; no
`source_url` may be invented, and no footage file may be persisted unless the true license
category permits it); `retrieval_date` field plus a documented (written, not automated)
30-day YouTube-API-metadata refresh/expiry process; schema + storage-layout tests.

**Post-Milestone-1 additions (repo-owner-directed, see tasks.md 3.8-3.9):** the pack has since
grown from the single AC3.4 worked example to 39 individually-researched exemplars, and gained
an `editorial_style` field (format/cut-count/shot-length/transition/pacing notes, honesty-tagged
via `review_method`) closing a gap versus the spec's own Scope-in text (spec line 37) that was
never given a schema slot in the original Milestone-1 pass. Both additions stay within the
spec's Scope-out boundary on bulk/automated scraping — every record was individually sourced and
verified, not bulk-downloaded — and do not themselves constitute the Tier C legal sign-off in
Open Question 6, which remains open and applies only if CC-BY-NC-commercial-use or
direct-creator-outreach scenarios actually arise.

No further follow-up milestone for Capability 3 beyond the above — automating this into an
*unattended* bulk pipeline stays out of scope per the spec's own Scope (out) section and is not
tracked as a deferred task here (it requires separate Tier C legal sign-off per Open Question 6,
not just implementation time).

## Open Questions — Resolution Status

1. **Spec granularity** — **Resolved (per explicit instruction): stays one combined spec.**
   Not split into three. Revisit only if a future capability's scope grows enough to warrant it.
2. **Footage storage location/volume** — **Resolved: `data/raw/` (done — confirmed present in
   this session).** This plan additionally fixes the retention convention for pipeline
   *outputs*: `data/interim/` (rendered highlight clips) and `data/output/` (stitched reels),
   both gitignored as regenerable artifacts; `data/manifests/` for the small JSON manifests
   themselves (safe to commit selectively). Adding these three paths to `.gitignore` (except
   manifests) is a Tasks-list item.
3. **Reference-pack footage: metadata-only vs. any local storage** — **Resolved for this plan:
   adopt the spec's stated default posture** (metadata + source link + derived analysis only;
   local footage storage reserved strictly for individually-verified CC BY/CC0/public-domain/
   owned content). The stricter zero-exception alternative the spec raises remains available
   for the user to choose later; this plan does not preclude tightening `storage.py`'s
   validator further if asked.
4. **GPU/CPU constraints** — **Resolved (per explicit instruction): CPU-only.** All Milestone 1
   scoring (Laplacian variance, histogram exposure, OpenCV optical flow) is classical CPU-only
   OpenCV; no GPU-dependent code path is planned. This also confirms the Milestone 2 saliency
   module choice (OpenCV `saliency`, CPU-friendly) over any GPU-accelerated alternative when
   that milestone is eventually built.
5. **Recommended tech stack** — **Resolved (per explicit instruction): the spec's proposed
   stack is accepted as-is**, with the GPL-vs-permissive motion-smoothness choice decided in
   favor of the pure-OpenCV optical-flow reimplementation (not ffmpeg `vid.stab`/`vidstabdetect`)
   specifically to avoid GPL entanglement, confirmed workable in this environment (`ffmpeg`
   here is in fact a `--enable-gpl` build, but the pipeline still avoids depending on that
   flag so it degrades gracefully on a non-GPL ffmpeg build elsewhere). PySceneDetect
   `AdaptiveDetector`, OpenCV Laplacian/histogram/optical-flow, ffmpeg concat-demuxer + `xfade`
   + `ffprobe` pinning, and the custom JSON manifest are all locked in for Milestone 1.
   Still **open/deferred** (not needed until their respective milestones): OpenCV `saliency` +
   vendored Hough-line horizon-tilt scorer + MediaPipe (Capability 1 Milestone 2);
   OpenTimelineIO + `otio-cmx3600-adapter` (Capability 2 Milestone 2); YouTube Data
   API/oEmbed + Vimeo API/oEmbed + `yt-dlp --skip-download` (Capability 3 — accepted in
   principle, but Milestone-1-scope Capability 3 work is a single manual worked example, so
   no live automated API-client code is built this pass; the one worked example may be
   populated by hand, or by one ad hoc manual API call, not a reusable pipeline component).
6. **Legal/licensing sign-off (Tier C)** — **Still open.** Not resolved by this plan; explicitly
   out of scope for this pass per the task's own constraint (capability 3 automation beyond
   the single worked example is excluded). Any future work scaling Capability 3 past one
   manual example requires the Tier C sign-off items (a)–(e) in spec Open Question 6 before
   proceeding.
7. **Prerequisite sequencing** — **Resolved: prerequisites are already satisfied.** `git init`
   has happened (2 existing commits), `.gitignore` already authored (excludes inherited
   template content + >100MB raw files), and `example-photos-videos/` → `data/raw/` relocation
   is done. The one remaining item from spec Open Question 7 — disposition of the inherited
   `claude-template` maintainer content (`docs/`, `promptlab/`, `copilot-studio/`, etc.) —
   stays explicitly out of scope for this spec/plan/tasks, exactly as the spec's own Scope
   (out) section states; it is not tracked as a task here.

## Test Strategy Notes

- No large binary fixtures are checked into `tests/fixtures/`. Synthetic clips (black frame,
  frozen frame, high/low Laplacian-variance patterns, known scene cuts) are generated at test
  time via `ffmpeg -f lavfi` source filters (`color`, `testsrc`, `noise`, etc.) into a pytest
  tmp_path, keeping the test suite hermetic and independent of `data/raw/` contents.
- `data/raw/` sample files MAY be used in a small number of slower, explicitly marked
  integration tests (e.g. `@pytest.mark.integration`) that are not part of the default fast
  test run, since they are real, large, and specific to this repo's footage.
- The AC2.3 forbidden-filter lint test reads the `reel_stitching` source files as text and
  asserts none of `eq`, `curves`, `colorbalance`, `unsharp`, `vidstabtransform`, or `setpts`
  (when used for speed, i.e. not `asetpts`/simple PTS-shift for concat) appear as ffmpeg
  filter-graph arguments — this is a grep-based static check per the spec's own suggested
  approach (spec line 66), not a runtime behavioral test.
