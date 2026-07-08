# Tasks: drone-video-pipeline

Status: DRAFT
Spec: `.claude/specs/drone-video-pipeline/spec.md`
Plan: `.claude/specs/drone-video-pipeline/plan.md`

Every task cites the Acceptance Criteria (AC) it satisfies, using the spec's numbering:
`C1.N` = Capability 1 AC N, `C2.N` = Capability 2 AC N, `C3.N` = Capability 3 AC N.
Tasks are ordered; later tasks depend on earlier ones within the same section unless noted.
Per Constitution rule 4, each task's diff must be independently reviewable — do not batch
unrelated tasks into one commit.

---

## 0. Project scaffolding (prerequisite for all three capabilities)

0.1. Create `pyproject.toml` at repo root: package name `drone_video_ai`, src-layout
     (`src/drone_video_ai`), build backend, runtime deps (`opencv-python`, `scenedetect[opencv]`,
     `numpy`), dev deps (`pytest`), console-script entry points `drone-highlights` and
     `drone-stitch` per plan.md's "Package / CLI naming" section. *(Supports all AC — no code
     runs without this.)*

0.2. Create the `src/drone_video_ai/` package tree with empty `__init__.py` files for
     `common/`, `highlight_extraction/`, `reel_stitching/`, `reference_pack/` matching the
     plan.md directory layout exactly (file names, not just directories).

0.3. Create `tests/` tree (`conftest.py` + the four subpackages' test directories) per
     plan.md, with `conftest.py` implementing the synthetic-clip fixture generators
     (black-frame clip, frozen-frame clip, high-variance clip, low-variance clip, a
     multi-scene clip with known cut points) via `ffmpeg -f lavfi`, written to `tmp_path`.
     *(Supports C1.6, C2.1, C2.2, C2.5, C3.1, C3.2 — all rely on hermetic fixtures.)*

0.4. Update `.gitignore`: add `/data/interim/`, `/data/output/`, and
     `/data/reference_pack/media/*` (keep `.gitkeep` or similar so the directory itself is
     tracked) per plan.md's retention convention. Do not touch the existing inherited-content
     or >100MB-raw-file entries.

0.5. Run `pip install -e .[dev]` (or equivalent) in this environment and confirm
     `pytest --collect-only` succeeds with zero collection errors before writing any real
     test bodies — this is the scaffolding checkpoint, verified with a tool (pytest), not
     self-assessment, per Constitution rule 6.

---

## 1. Capability 1 — Highlight extraction

### Milestone 1 (this pass)

1.1. Implement `common/ffprobe.py`: subprocess wrapper around `ffprobe -show_streams
     -show_format -of json`, returning duration/width/height/fps/codec/pix_fmt and the four
     color-metadata tags (tolerating `unknown`/absent values — confirmed to occur on this
     repo's own sample footage per plan.md's grounding notes). *(Supports C1.1's `source_file`
     block and is reused by Capability 2.)*

1.2. Implement `common/manifest.py`: `HighlightManifest`/`Segment`/`ExcludedSegment`
     dataclasses matching the exact schema in plan.md section "1. Highlight manifest", with
     `to_json()`/`from_json()` round-trip methods. *(C1.1, C1.5.)*

1.3. Implement `common/schema.py`'s highlight-manifest JSON-schema dict and a
     `validate_highlight_manifest(doc: dict) -> None` (raises on invalid) function.
     *(C1.1, C1.5 — machine-checkable schema, not just a docstring.)*

1.4. Implement `highlight_extraction/segmentation.py`: PySceneDetect `AdaptiveDetector`
     integration producing `scene_boundaries`, honoring a configurable `scene_threshold`.
     *(C1.3 — half of the candidate boundary set.)*

1.5. Implement `highlight_extraction/motion.py`: per-frame camera-motion transform time
     series via `cv2.goodFeaturesToTrack` + `cv2.calcOpticalFlowPyrLK`, plus a
     derivative-minima detector over that series producing `motion_minima_boundaries`.
     *(C1.3 — other half of the candidate boundary set; this is the GPL-avoidance path
     resolved in plan.md Open Question 5 — no `vid.stab`/`vidstabdetect` dependency.)*

1.6. Implement the boundary-union step (in `segmentation.py` or a small
     `candidate_boundaries.py`, implementer's choice) combining 1.4 + 1.5 into
     `union_boundaries`, and the segment-splitting logic that only cuts at
     `union_boundaries` members while enforcing configurable `min_duration`/`max_duration`
     (default 2–15s per plan.md, with the legacy 7–15s documented as an alternate named
     profile, not hardcoded). *(C1.3 — the boundary-membership invariant; C1.4 — duration
     bounds.)*

1.7. Implement `highlight_extraction/scoring_sharpness.py`: `cv2.Laplacian(...).var()` over
     sampled frames per segment, in-video min-max normalized to `[0,1]`. *(C1.1, C1.6.)*

1.8. Implement `highlight_extraction/scoring_exposure.py`: histogram-based over/under-exposed
     clipping-fraction score, normalized to `[0,1]` (`1 - clipped_fraction`). *(C1.1, C1.6.)*

1.9. Implement `highlight_extraction/scoring_motion_smoothness.py`: jerk/acceleration
     magnitude derived from the `motion.py` transform series, in-video min-max normalized
     (inverted so smoother = higher score) to `[0,1]`. *(C1.1, C1.6.)*

1.10. Implement `highlight_extraction/gates.py`: `ffmpeg blackdetect`/`freezedetect` wrappers
      (subprocess, parsing stderr log lines) plus configurable `min_sharpness_floor` /
      `min_exposure_floor` threshold checks, returning a `gate_failures: list[str]` per
      segment. *(C1.2.)*

1.11. Implement `highlight_extraction/weights.py`: a documented, versioned default weight
      config (`weights_version: "default-v1"`, `composition: 0.0` fixed for Milestone 1) as
      a dataclass/dict loaded from a plain Python module (or a small YAML/JSON file if
      preferred — implementer's choice, but must not be a hardcoded literal buried inside
      `composite.py`). *(C1.1's "documented, versioned scoring-weight configuration"
      requirement, spec line 23.)*

1.12. Implement `highlight_extraction/composite.py`: weighted composite score from
      sharpness/exposure/motion_smoothness using `weights.py`'s config (composition weight
      is 0.0, so its `null` score never enters the sum). *(C1.1.)*

1.13. Implement `highlight_extraction/pipeline.py`: orchestrates 1.4–1.12 end-to-end for one
      input video, applies gates (segments failing gates go to `excluded_segments`, not
      `segments`, per plan.md's schema), and emits a `HighlightManifest` via `common/manifest.py`.
      Optional flag to also render each accepted segment to a clip file (stream-copy via
      ffmpeg, no re-encode, no pixel modification — this pipeline never modifies pixels
      either). *(C1.1, C1.2, C1.5.)*

1.14. Implement `highlight_extraction/cli.py`: argparse entrypoint wiring input file path,
      `min_duration`/`max_duration`/`scene_threshold`/gate-floor CLI flags, output manifest
      path, and the optional clip-rendering flag, to `pipeline.py`. *(C1.1–C1.5, end-to-end.)*

1.15. Write `tests/highlight_extraction/test_segmentation_boundaries.py`: assert every emitted
      segment's `start_time`/`end_time` is a member of `union_boundaries` on a synthetic
      multi-scene fixture. *(C1.3.)*

1.16. Write `tests/highlight_extraction/test_scoring_sharpness.py`: assert a synthetic
      high-Laplacian-variance clip scores strictly above a low-variance (blurred/flat) clip.
      *(C1.6.)*

1.17. Write `tests/highlight_extraction/test_scoring_exposure.py`: assert a synthetic
      correctly-exposed clip scores above an over/under-exposed (clipped-histogram) clip.
      *(C1.6.)*

1.18. Write `tests/highlight_extraction/test_scoring_motion_smoothness.py`: assert a
      synthetic smooth-pan clip scores above a synthetic jittery/shaky-motion clip.
      *(C1.6.)*

1.19. Write `tests/highlight_extraction/test_gates.py`: assert a synthetic black-frame clip
      and a synthetic frozen-frame clip both produce `gate_status: "failed"` with the correct
      `gate_failures` entry and land in `excluded_segments`, not `segments`. *(C1.2, C1.6.)*

1.20. Write `tests/highlight_extraction/test_pipeline_manifest_output.py`: run the full
      pipeline against a synthetic multi-segment fixture and assert: (a) manifest validates
      against `common/schema.py`'s schema; (b) `version == 2`; (c) no `post_processing` key
      anywhere in the output; (d) every emitted segment's duration is within the configured
      min/max bounds; (e) `normalization` block is present and non-empty for all three scored
      signals. *(C1.1, C1.4, C1.5.)*

### Milestone 2 (built)

1.21. **[done]** Implemented composition scoring: OpenCV `saliency`-module (`StaticSaliencySpectralResidual`)
      rule-of-thirds distance scorer, in `scoring_composition.py`. *(Satisfies the `composition`
      portion of C1.1.)*

1.22. **[done]** Implemented a vendored (not pip-installed) Hough-line horizon-tilt scorer
      for aerial-specific framing (`cv2.Canny` + `cv2.HoughLinesP`), combined into the
      composition score from 1.21 via an unweighted 0.5/0.5 average — see
      `scoring_composition.py` module docstring for the full derivation and the
      SpectralResidual-vs-FineGrained benchmark that motivated the algorithm choice.

1.23. **[done]** Evaluated MediaPipe's object detector for subject-centroid detection;
      **decision: not integrated** — the saliency-map centroid already supplies sufficient
      spatial weighting for the rule-of-thirds sub-score without needing to identify *what*
      the salient region is, so an added dependency was not justified (see
      `scoring_composition.py`'s "MediaPipe evaluation" section). YOLOv8/Ultralytics remains
      excluded per spec Scope-out, unchanged.

1.24. **[done]** Bumped `scoring_weights.weights.composition` to a nonzero default: `weights.py`
      now has two named, immutable profiles — `"default-v1"` (legacy, composition=0.0,
      preserved unchanged) and `"default-v2"` (new module-wide default, equal 0.25 quarters
      across all four signals). `scores.composition` and `normalization.composition` are
      populated for real in the manifest, and `MANIFEST_VERSION` bumped from 2 to 3 per
      plan.md's "Milestone 2 (composition scoring) changes to this schema" note.

1.25. **[done]** Added `tests/highlight_extraction/test_scoring_composition.py` (via new
      `make_bright_region_clip`/`make_horizon_clip` fixtures in `tests/conftest.py`) validating
      the rule-of-thirds and horizon-tilt sub-scorers against synthetic well-composed vs.
      poorly-composed / tilted-horizon fixtures.

---

## 2. Capability 2 — Reel stitching

### Milestone 1 (this pass)

2.1. Implement `reel_stitching/edit_manifest.py`: `EditManifest`/`EditEntry` dataclasses
     matching plan.md's edit-manifest schema, with `to_json()`/`from_json()`. *(C2.1, C2.5 —
     the manifest is the pre-render source of truth the spec requires, spec line 28.)*

2.2. Extend `common/schema.py` with the edit-manifest JSON schema and a
     `validate_edit_manifest(doc: dict) -> None` function.

2.3. Implement `reel_stitching/pacing.py`: given an `EditManifest` and a
     `target_duration`, compute per-clip trims/ordering to hit the target within a
     configurable tolerance (default ±0.5s per spec), producing an updated `EditManifest`
     as an explicit, inspectable intermediate artifact (not applied silently during
     render). *(C2.5.)*

2.4. Implement `reel_stitching/color_pinning.py`: for each transition-window pair in an
     `EditManifest`, call `common/ffprobe.py` on the source clip(s) and derive the
     `-colorspace`/`-color_primaries`/`-color_trc`/`-color_range` ffmpeg args to pin onto the
     `xfade` encode, passing through `unknown`/absent values rather than substituting
     defaults (per plan.md's grounding note that this repo's own sample footage reports
     `unknown` color tags). Assert (raise, don't silently pick) if the two clips in a
     transition pair disagree on any of these four tags. *(C2.2.)*

2.5. Implement `reel_stitching/render.py`:
     - Hard-cut path: build an ffmpeg concat-demuxer file list from consecutive
       `type: "cut"` entries sharing codec/profile/resolution/pix_fmt/timebase, render via
       `-c copy`. *(C2.1, and Scope-out's "never concat filter/MoviePy for final render".)*
     - Transition path: for each `type != "cut"` entry pair, render only the overlapping
       transition window via ffmpeg `xfade`, lossless (`-crf 0`, FFV1, or ProRes 4444 —
       implementer's choice, document which), using `color_pinning.py`'s args. *(C2.2.)*
     - Concatenate the hard-cut segments and rendered transition windows into the final
       output file.
     - Hard constraint enforced by construction, not a flag: no color/exposure/white-balance/
       sharpen/stabilize/letterbox/speed-ramp filter is ever invocable through this module's
       public API. *(C2.3 — the code-shape half of this AC; 2.7 below is the test half.)*

2.6. Implement `reel_stitching/verify.py`: for every stream-copied (non-transition) region,
     run `ffmpeg -f framemd5` on the corresponding source frame range and on the output frame
     range, and assert equality. *(C2.1.)*

2.7. Implement `reel_stitching/cli.py`: argparse entrypoint wiring an edit-manifest path,
     optional `--target-duration`, output file path, to `pacing.py` → `render.py` →
     `verify.py`. *(C2.1, C2.2, C2.5, end-to-end.)*

2.8. Write `tests/reel_stitching/test_concat_demuxer_framemd5.py`: build a synthetic
     multi-segment edit manifest of all-`"cut"` transitions from a single-source synthetic
     clip, render, and assert `framemd5` equality between source and output for every
     region. *(C2.1.)*

2.9. Write `tests/reel_stitching/test_xfade_color_metadata.py`: build a synthetic 2-clip
     edit manifest with one `xfade` transition, render, and assert (via `ffprobe` on the
     output) that `color_primaries`/`color_trc`/`color_range`/colorspace exactly match the
     source clip for the transition-window region — including the case where the source
     reports `unknown`/unset (must not fail merely because the tag is unset, must fail if
     output diverges from source's unset-ness or from a differing explicit value).
     *(C2.2.)*

2.10. Write `tests/reel_stitching/test_forbidden_filters_lint.py`: statically read
      `reel_stitching/render.py` and `reel_stitching/color_pinning.py` source text and assert
      none of `eq=`, `curves=`, `colorbalance=`, `unsharp=`, `vidstabtransform=`, or a
      speed-changing `setpts=` usage appears as a constructed ffmpeg filter argument.
      *(C2.3.)*

2.11. Write `tests/reel_stitching/test_pacing_tolerance.py`: given a target duration and a
      synthetic multi-clip edit manifest, assert the paced manifest's total duration is
      within ±0.5s (or the configured tolerance) of the target. *(C2.5.)*

### Milestone 2 (built)

2.12. **[done]** Added `opentimelineio>=0.16` + `otio-cmx3600-adapter>=1.0` to `pyproject.toml`
      dependencies; implemented `otio_export.py`'s `edit_manifest_to_otio`/`export_otio`:
      `EditManifest` → `.otio` timeline exporter. *(Satisfies the `.otio` half of C2.4.)*

2.13. **[done]** Implemented `.otio` → CMX3600 EDL export (`export_edl`, via the installed
      `otio-cmx3600-adapter`), plus `validate_export`'s schema/structural validation check
      (clip-count + total-duration-within-tolerance, read back via `otio.adapters.read_from_file`)
      runnable in CI with no NLE involved. *(Satisfies the EDL-export half of C2.4; actual NLE
      round-trip remains a manual acceptance step per the spec's own text, spec line 67.)*

2.14. **[done]** Added `tests/reel_stitching/test_otio_export.py` covering the
      schema/structural validation from 2.13, plus the transition half-shrink accounting,
      all-cut plain-adjacency case, and `OTIOExportError` propagation for
      transition-too-long-for-entry inputs.

---

## 3. Capability 3 — Reference pack (build now, full spec scope)

3.1. Implement `reference_pack/schema.py`: `ExemplarRecord` dataclass and JSON schema exactly
     matching plan.md's exemplar-record schema, including all fields listed in spec AC 71:
     `source_url`, `platform`, `license_category`, `title`, `creator`, `duration`,
     `retrieval_date`, per-signal + composite scores, `award_or_showcase_provenance`
     (nullable). *(C3.1.)*

3.2. Implement `reference_pack/storage.py`: a validator that, given the
     `data/reference_pack/exemplars/` and `data/reference_pack/media/` directories, asserts
     no exemplar record with `license_category == "all-rights-reserved"` has a non-null
     `local_media_path` or a matching file present under `media/`. *(C3.2.)*

3.3. Write a short, versioned refresh/expiry process note (a markdown doc alongside
     `reference_pack/`, e.g. `src/drone_video_ai/reference_pack/README.md`, or a docstring in
     `schema.py` — implementer's choice) describing: metadata retrieved via the YouTube Data
     API must be refreshed or deleted within 30 calendar days of `retrieval_date`; this is a
     manual/documented process for now, not automated. *(C3.3 — the field already exists per
     3.1; this task is the "documented process" half of the AC.)*

3.4. **Manual research task (human- or agent-verified, not automated):** identify exactly one
     real, currently public, correctly-attributable drone landscape or wildlife video (e.g. a
     known SkyPixel Awards / Drone Awards showcase entry, or a reputable creator's published
     upload) and record its true `source_url`, `platform`, actual observed
     `license_category` (default expectation: `all-rights-reserved` for a typical YouTube
     upload, unless the uploader has explicitly marked the video Creative Commons — verify by
     inspecting the actual video's license setting, do not assume), `title`, `creator`,
     `duration`, and today's date as `retrieval_date`. **No URL may be invented** — if no
     verifiable public example can be confirmed in the implementation session, stop and flag
     this task as blocked rather than fabricating one. If `license_category` is anything
     other than one of `cc-by`/`cc-by-sa`/`cc-by-nd`/`cc0`/`public-domain`/`owned`, do not
     download or persist the video file — `local_media_path` stays `null`. *(C3.4.)*

3.5. Run the Milestone-1 Capability-1 scoring functions (1.7–1.9) against the worked
     example's video — either a legally retrievable short clip if license permits local
     analysis, or a manual/transient stream-and-discard pass that never writes the source
     file to disk if it does not — to populate the exemplar's `sharpness`/`exposure`/
     `motion_smoothness`/`composite_score` fields (`composition` stays `null`, matching
     Capability 1 Milestone 1's convention). Save the resulting single JSON record under
     `data/reference_pack/exemplars/`. *(C3.4 — "demonstrates the full metadata-plus-
     derived-analysis record end-to-end".)*

3.6. Write `tests/reference_pack/test_schema_validation.py`: assert the worked example from
     3.5 validates against `schema.py`'s JSON schema and contains all required fields from
     spec AC 71. *(C3.1.)*

3.7. Write `tests/reference_pack/test_storage_layout_no_arr_files.py`: assert `storage.py`'s
     validator passes against the current `data/reference_pack/` contents, and add a second
     synthetic-fixture case (a fake all-rights-reserved record paired with a deliberately
     placed stray file under `media/`) asserting the validator correctly *fails* that case.
     *(C3.2 — tests both the true-positive and the true-negative path.)*

3.8. **[done, post-Milestone-1 addition]** Added `editorial_style` (an `EditorialStyle`
     dataclass: `format`, `estimated_cut_count`, `avg_shot_length_seconds`,
     `transition_styles_observed`, `pacing_notes`, `review_method`) to `schema.py` and its
     validator — this closes a gap versus spec Scope-in line 37 ("this project's own derived
     analysis ... plus shot-length/cut/transition-style notes"), which had no schema field for
     it until now. Optional field, not part of AC71's required minimum; honesty-tagged via
     `review_method` (`"not_reviewed"` / `"text_provenance_only"` / `"live_playback_review"`)
     following the same provenance-honesty convention as `scores_provenance`. *(Extends C3.1.)*

3.9. **[done, post-Milestone-1 addition, repo-owner-directed]** Expanded the reference pack
     from the single AC3.4 worked example to 39 individually-researched exemplars (see
     `data/reference_pack/exemplars/` and `reference_pack/README.md`'s "Scope reminder" section
     for the per-batch rationale). Each record was sourced and verified individually (no bulk
     scraping/downloading — every `all-rights-reserved` record has `local_media_path: null` and
     no matching file under `media/`, mechanically enforced by `storage.py` and re-confirmed by
     `tests/reference_pack/test_storage_layout_no_arr_files.py`), so this stays within the
     spec's Scope-out boundary on **bulk automation**. It does NOT itself constitute the
     Tier C legal/licensing sign-off items (a)-(e) in spec Open Question 6 (CC-BY-NC commercial
     use, direct creator outreach) — those remain open and are only triggered if either scenario
     is actually encountered, per plan.md Open Question 6's original resolution.

No further Milestone 2 tasks tracked for Capability 3 beyond 3.8/3.9 above — per plan.md,
scaling past manually-researched individual exemplars into an *automated/unattended* bulk
pipeline still requires separate Tier C legal sign-off (spec Open Question 6) before any further
implementation, and is intentionally not tracked here.

---

## 4. Cross-cutting verification (Constitution rule 3)

4.1. Run `python3 -m pytest` for the full suite (all three capabilities) and confirm 100%
     pass with zero skips due to missing fixtures/tools.

4.2. Run `bash -n` on any new shell snippets introduced (if any); this milestone is Python +
     subprocess-invoked `ffmpeg`/`ffprobe`, so this step may be a no-op — confirm and note
     that explicitly rather than skipping silently.

4.3. Confirm no forbidden dependency (`ultralytics`, `pyiqa`/`IQA-PyTorch`, any
     TransNetV2/PyTorch/TensorFlow package) appears in the final `pyproject.toml`.

4.4. Confirm `data/interim/`, `data/output/`, and `data/reference_pack/media/*` are
     git-ignored (task 0.4) and that no large rendered artifact from running the test suite
     or CLIs locally has been accidentally staged (`git status --short` review) before any
     commit.
