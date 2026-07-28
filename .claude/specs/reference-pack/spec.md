# Spec: reference-pack
Status: DRAFT

> This document is DRAFT and is **not** signed off. Producing it does not authorise
> implementation. Per the repo's Spec-Driven Workflow, Plan → Tasks may not begin until
> the user explicitly signs off, and any divergence found during implementation must be
> resolved by amending this spec first.

## Problem Statement

`pyproject.toml` names three capabilities in its `description`: "highlight extraction,
reel stitching, and **reference-pack curation**". The first two have surviving surface —
`[project.scripts]` declares `drone-highlights = "drone_video_ai.highlight_extraction.cli:main"`
and `drone-stitch = "drone_video_ai.reel_stitching.cli:main"`, the `readme` field pins
Capability 1 to Milestone 1, and the dependency comments pin Capability 2's `.otio` /
CMX3600 EDL export to Milestone 2 via `opentimelineio>=0.16` + `otio-cmx3600-adapter>=1.0`.
Reference-pack curation has **no** entry point, **no** milestone marker, and **no**
surviving spec — yet `.gitignore` already legislates its on-disk layout
(`/data/reference_pack/media/*` ignored, `!/data/reference_pack/media/.gitkeep` re-included)
and already legislates its central prohibition (frame-capture PNGs "exactly the kind of
footage-adjacent artifact this project's reference pack must never persist (spec Scope-out)").

So the layout and the prohibition survive as binding constraints while their justification
does not. This spec reconstructs the capability's requirements from the two surviving
artifacts plus measurement, and does not invent the rest.

**What the pack is for.** Capability 1 scores highlights and Capability 2 stitches reels.
Both need thresholds. A threshold invented from intuition is exactly the "invented constant"
the repo Constitution prohibits, and the anti-hallucination rules forbid asserting a value
that was not measured this session. The reference pack exists so that every threshold in
`src/` can trace to a measurement over this corpus, and so that the corpus's *actual*
statistical shape governs the design instead of an assumption about what drone footage
looks like.

**What measurement already established, and why it reframes the problem.** The corpus is
9 entries in the read-only directory `/Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples`
— 8 `.mp4` deliverables plus `manifest.json`. Across all 8 files and all 4,099 scored
frames, **zero** frames reach a scene-change score of 5.0 on ffmpeg `scdet`'s 0–100 scale
(per-file maxima 0.516 / 1.547 / 1.776 / 1.799 / 2.104 / 2.435 / 2.668 / 3.537), where a
calibrated synthetic positive control put genuine hard cuts at 31.42 and 42.19. Every file
is a **single continuous shot**; the corpus contains no cuts at all, and no audio stream on
any file.

This is a positive finding, not a detection failure, and it is load-bearing for scope: a
corpus with no shot boundaries cannot validate a shot-boundary detector, which independently
corroborates `pyproject.toml`'s licence-driven exclusion of "any TransNetV2/PyTorch/TensorFlow
shot-boundary dependency". The tuning problem here is *within-shot* quality and motion
scoring, not boundary detection.

**Toolchain constraint that shapes the deliverable.** The declared runtime dependencies
(`opencv-contrib-python`, `scenedetect[opencv]`, `numpy`, `opentimelineio`) are **not
installed** — `.venv/` is an empty husk with only `pyvenv.cfg` and no `bin/`, and system
`python3` has none of them. Every measurement in this pack was therefore produced with
ffprobe/ffmpeg 8.1 plus the Python 3 standard library. That is sufficient for container,
timing, framing, luma/chroma and frame-difference facts, and provably insufficient for
optical-flow facts. The pack must state which is which rather than closing the gap by guessing.

## Scope (in)

1. **Per-file technical probe.** One ffprobe JSON per probed `.mp4` (full `-show_format
   -show_streams`), at `data/reference_pack/probe/{basename}.json`. **9 files** — the 8
   corpus files plus the out-of-corpus source master `DJI_0355_proxy.mp4` (located in
   `_archive/`, probed so the split-family provenance measurements are reproducible from
   retained raw output) — each validating under `python3 -m json.tool`. *(Amended
   2026-07-27: originally "8 files"; the proxy pair was added during verification and the
   spec amended per this repo's divergence-amends-spec-first rule.)*
2. **Per-frame scene-change score series.** One CSV per probed `.mp4` at
   `data/reference_pack/probe/{basename}.scd.csv`, two columns (`pts_time`, `lavfi.scd.score`),
   one row per frame, produced by `scdet=threshold=0` so that thresholding is done offline
   and is auditable rather than baked into the capture. **9 files**, same set as item 1.
3. **Identity anchors.** A `sha256` per source file, so any later measurement can prove it
   examined the same bytes.
4. **Distribution summaries with derived, not assumed, thresholds.** min / p50 / p90 / p99 /
   max / mean / stdev per file, plus the hard-cut count and the *stated justification* for
   the threshold used to produce that count. Thresholds must be derived from each file's own
   distribution; a magic constant is not acceptable.
5. **`manifest.json` reconciliation.** Every claim in the sidecar checked against measurement
   and classed agrees / disagrees / unverifiable, with the numeric delta where it disagrees.
6. **Topology and provenance map.** Per file: role (master / derivative / rendition), whether
   provenance is *known* (documented and verified) or *inferred* (measured only), and the
   evidence.
7. **Edit grammar characterisation.** Shot structure, cut rhythm, letterbox geometry and
   mechanism, colour treatment and tagging, speed handling, audio, and delivery surfaces.
8. **`data/reference_pack/README.md`** — the pack's own regeneration and interpretation
   contract, including the never-contain prohibition.
9. **This spec.**
10. **A negative-control requirement.** Any similarity claim in the pack must be reported
    against a calibrated null measured from this same corpus. This is in scope because the
    null here is large enough to invalidate naive matching: time-reversed `split_003` scores
    r=+0.9421 against `instagram_reel_test` versus a forward r=+0.7497, and known-disjoint
    split pairs reach r=+0.8831. An unanchored correlation is not evidence.
11. **`data/manifests/` as the trackable home** for any derived manifest the pack emits —
    `.gitignore` deliberately does not ignore it ("data/manifests/ (small JSON) is
    intentionally NOT ignored — safe to commit selectively").
12. **Cross-validation against archived footage the corpus itself does not contain.**
    *(Added 2026-07-27.)* `_archive/_p-ai-drone-video/.drone_clips/` holds 6 raw
    camera-original drone masters and 7 more `manifest.json` sidecars (39 derivative
    clips between them, run with different `split_params` than the corpus's own
    `manifest.json`, 3 against a raw camera master rather than the transcoded proxy).
    Probing and reconciling these is IN SCOPE as **cross-validation, not corpus
    expansion**: it tests whether item 5's reconciliation findings and item 7's edit-grammar
    characterisation generalize beyond the one manifest/one source-file case the original 9
    entries allow, or were parameter-specific. It does not change what "the corpus" means
    (item 1's 8 `.mp4` deliverables are unchanged) — this material stays clearly
    distinguished in every artifact (REVIEW.md §2.5/§2.6/§8, `README.md`'s "Also measured"
    note, `reference_pack.json → archive_expansion`) rather than merged into corpus-scoped
    counts and tables.

## Scope (out)

Licence-driven exclusions, verbatim from `pyproject.toml` lines 12–14 and binding on this
capability as much as on the others:

- **`ultralytics` / YOLOv8** — AGPL-3.0.
- **`pyiqa` / IQA-PyTorch** — non-commercial licence.
- **Any TransNetV2 / PyTorch / TensorFlow shot-boundary dependency.** Independently
  corroborated as unnecessary here: the corpus has no shot boundaries to detect.

Prohibition-driven exclusions, from `.gitignore` lines 41–49:

- **Persisted frame captures, stills, thumbnails, contact sheets, or any rasterised
  single-frame artifact**, anywhere in the repo. `.gitignore` names `/seek*.png`,
  `/short*.png`, `/shot-initial.png`, `/.playwright-mcp/` and calls a frame-capture PNG of
  an all-rights-reserved source video "exactly the kind of footage-adjacent artifact this
  project's reference pack must never persist". Frames may be *decoded* in a pipe; they may
  not be *written*.
- **Media payload under `data/reference_pack/media/`.** The directory is tracked (via
  `.gitkeep`); its contents are ignored. The pack is measurements about footage, never
  footage.

Boundary-driven exclusions:

- **`src/drone_video_ai/`, any CLI, and `tests/`.** Not this spec's artifact. Note these
  paths are *referenced* by surviving config — `[tool.setuptools.packages.find] where =
  ["src"]`, `[tool.pytest.ini_options] testpaths = ["tests"]` — and are absent from disk
  (verified this session).
- **`data/interim/` and `data/output/`.** `.gitignore` classes both as "regenerable from
  manifests + raw footage".
- **Optical-flow-derived measures.** Verifying `manifest.json`'s `motion_type` **direction**
  labels (`REVEAL` vs `ORBIT_CW`) requires per-pixel motion-vector direction and rotation
  estimation, i.e. `cv2`, which is unavailable and which this spec forbids installing.
  `scdet`'s MAFD gives motion *magnitude* only and is direction-blind. Out of scope as
  **UNVERIFIABLE IN-SESSION**, not deferred pending a guess. *(Narrowed 2026-07-27, matching
  `README.md` and `editorial_style.json`, both fixed in the first remediation pass — this
  bullet was missed then: the **`STATIC`** label specifically is *partly* testable without
  `cv2`. A null-controlled 128-bin row-profile cross-correlation showed `split_004` — declared
  `STATIC` — drifting ~2.7 px/frame. Single-run, unreplicated, and row-profile drift cannot
  separate camera pan from subject motion, so this is a caveat, not a finding — it does not
  bring `STATIC` in scope, but it means "no ffmpeg path exists" is too strong a claim for the
  `STATIC`/non-`STATIC` distinction specifically. See `REVIEW.md` §5.1 group G.)*
- **Re-encoding, moving, renaming, or modifying anything in the read-only source directory,
  or in `/Users/mac/Documents/photography-WORKFLOW-local/_archive/`** where the source proxy
  was located. Read-only.

## Acceptance Criteria

Criteria 1–4, 10 and 12 are checkable with a command as stated. Criteria 5–9 and 11 are
**review criteria**: they bind on human/agent review of the artifacts, and where a partial
mechanical check exists it is named inline. *(Amended 2026-07-27: the original preamble
claimed every criterion was command-checkable, which criteria 5–9 never were.)*

1. **Coverage.** `data/reference_pack/probe/` contains exactly one `.json` and one `.scd.csv`
   per probed `.mp4` — the 8 corpus files plus the out-of-corpus source master
   `DJI_0355_proxy` (see Scope (in) item 1) — **9 of each, 18 files**.
   Check: `ls data/reference_pack/probe/*.json | wc -l` = 9; same for `*.scd.csv`.
   *(Amended 2026-07-27: originally "8 of each, 16 files", written before the proxy pair was
   added; the check as previously stated failed against the delivered pack.)*
2. **JSON validity.** Every probe JSON parses and contains both a `streams` array and a
   `format` object.
   Check: `for f in data/reference_pack/probe/*.json; do python3 -m json.tool "$f" >/dev/null; done`
3. **CSV score integrity — the pack's highest-risk failure mode.** Every CSV row carries a
   numeric score in column 2, and the row count equals the file's `nb_frames`. This criterion
   exists because the malformed comma form of the `scdet` recipe (see Open Question 5) exits
   0 and silently emits a score-less CSV; a row-count check alone passes on a broken file.
   Check: row/score counts must be 813/813, 813/813, 450/450, 450/450, 249/249, 450/450,
   437/437, 437/437, and **1909/1909** for `DJI_0355_proxy.scd.csv`.
   *(Amended 2026-07-27: proxy row added, same reason as criterion 1.)*
4. **Identity.** Each recorded `sha256` reproduces against the source file.
   Check: `shasum -a 256` per file. Two were re-verified this session:
   `split_003_s66.mp4` = `33dd47b0a2980a7033c639a95087059104bfe445258bd56793e3785fe26e396c`,
   `instagram_reel_test.mp4` = `e1fb91b6b99eaaff69711f6617b38d4c7c07cbf4fc384c25a4d83ad7f02a4eb8`.
5. **No invented constants.** Every threshold reported alongside a cut count is accompanied
   by its derivation from the measured distribution, and the derivation reproduces from the
   delivered CSV.
6. **Two independent methods per cut claim.** Each hard-cut count is corroborated by both the
   offline `scdet` threshold and the `select='gt(scene,...)'` filter, and the two agree.
   The `select` cross-check must use `metadata=print:file=-` (see Open Question 5).
7. **Unverifiability is declared, not filled.** Every `manifest.json` field with no
   ffprobe/ffmpeg observable appears in an explicit unverifiable list. Nothing is guessed.
   The list must at minimum cover `motion_type`, `score`, `motion_energy`, `scene_threshold`,
   `enhanced`, and `quality`'s label→bitrate mapping.
8. **Provenance is labelled by confidence.** Each file is marked `known` or `inferred`. The
   four `split_*` files may be `known` (documented in `manifest.json` *and* verified by
   pixel measurement); the four vertical files must be `inferred`, because no surviving
   artifact documents them.
9. **Similarity claims are anchored.** Every correlation or PSNR claim cites a corpus-derived
   negative control (a matched-geometry unrelated pair, with the pairing, crop and scaler
   named) or a time-reversed null. Unanchored similarity claims fail review.
   *(Amended 2026-07-27: the previous text mandated the figure "12.481161 dB" without naming
   its pairing, crop or frame alignment, making the criterion uncheckable — and a skeptic's
   matched-geometry control with a stated pairing (split_001 vs split_003 picture areas, both
   cropped 1280:544:0:88) measured 18.844898 dB, which does not reproduce it. The anchor is
   now the *method*, not an unattributed constant.)*
10. **Zero persisted frames.** No image file exists anywhere under the repo.
    Check: `find . -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.bmp' -o -iname '*.ppm'`
    returns nothing outside the gitignored inherited `assets/`, `docs/`, `site/` trees that
    belong to the other project.
11. **Regeneration is executable as written.** Every command in
    `data/reference_pack/README.md` runs as pasted and produces the documented artifact.
    Verified at authoring time for the probe, `scdet`, `select`-cross-check, `cropdetect`,
    and audio-absence recipes. **This criterion is environment-dependent and known to have
    broken once already**: on 2026-07-27 a homebrew x265 upgrade (4.1→4.2) removed
    `libx265.215.dylib` and every ffmpeg/ffprobe recipe aborted at load until
    `brew reinstall ffmpeg` relinked it (README "Toolchain" note). Re-run one recipe before
    trusting this criterion in a new session.
12. **Layout conforms to `.gitignore`.** `data/reference_pack/media/` contains `.gitkeep` and
    no media.
13. **Archive cross-validation coverage.** *(Added 2026-07-27.)* Every raw master and
    derivative clip named in scope item 12 has a retained ffprobe JSON + scdet CSV pair in
    `probe/`, and every one of the 7 archive `manifest.json` files has a reconciliation
    recorded in REVIEW.md §8. State each check as a live command, not a hardcoded count —
    this pack's counts have drifted from hardcoded values twice already:
    Check: `ls data/reference_pack/probe/*.json | wc -l` must equal
    `ls data/reference_pack/probe/*.scd.csv | wc -l` (both counts, whatever they are,
    must match each other exactly — currently 54).
    Check: every basename under `find _archive/_p-ai-drone-video/.drone_clips -iname
    'DJI_*.MP4' -o -iname 'DJI_*.mov'` and every `split_*.mp4` under
    `_archive/_p-ai-drone-video/.drone_clips/.advanced/*/` has a matching
    `data/reference_pack/probe/{name}.json`.
    **Known partial gap, stated honestly rather than hidden**: 6 of the 7 archive manifest
    reconciliations (all except `highlights_long`) were produced by a run interrupted by an
    infrastructure failure before an independent adversarial verification pass could run —
    see REVIEW.md §8.4. This criterion checks *coverage* (was it measured and recorded), not
    *adversarial confirmation* (was it independently attacked and survived) — those are
    different bars, and only the corpus-proper claims (item 1–11) currently clear the second
    one. A future session should run that verification pass before treating §8's findings
    with the same weight as the rest of this pack.

## Open Questions

None of these may be resolved unilaterally. Each is a live ambiguity, and where an assumption
is currently in force it is labelled as an assumption.

1. **May `media/` hold derived artifacts from the user's OWN footage?**
   `.gitignore` grounds the exclusion in licensing — "a frame-capture PNG of an
   **all-rights-reserved source video**". But the four `split_*` clips descend from
   `DJI_0355_proxy.mp4`, a DJI drone file in the user's own `_archive/`, which appears to be
   the user's own footage. Two readings are live and the surviving artifacts cannot choose
   between them: (a) the prohibition is *licence-scoped*, so derived artifacts from the user's
   own footage are permissible in `media/` while any third-party reference frame is
   categorically excluded; (b) the prohibition is *categorical*, and `media/*` is ignored
   regardless of who owns the footage. **The pack currently operates under the strictest
   reading — reading (b), zero persisted frames from any source — and that is an ASSUMPTION,
   not a verified rule.** Note the two readings are not equally reversible: adopting (a)
   later is cheap, whereas retracting persisted frames is not. Escalate to the user; do not
   resolve.

2. **What authority does this spec surface actually carry, given how little survived?**
   `src/`, `tests/`, `plan.md`, and the prior `spec.md` are all **absent from disk** (verified
   this session); `.git` is corrupt with no objects, refs, or index, so nothing is recoverable
   from history and no git command can run. `pyproject.toml` and `.gitignore` are the only
   surviving **project-specific authority documents**.

   > **CORRECTED 2026-07-27 — C43 killed 2/3.** This paragraph previously read "Only
   > `pyproject.toml` and `.gitignore` survived", which is a universal a one-line `ls`
   > falsifies. Two counter-examples, both re-verified this session: (a) `.pytest_cache/`
   > (mtime 2026-07-24) also survived at the repo root — it holds `CACHEDIR.TAG`, `README.md`
   > and `.gitignore` but **no** `nodeids` and **no** `lastfailed`, so it attests that a test
   > run once happened and nothing about what was tested; (b) `.claude/specs/reference-pack/`
   > is **present** — this very file, mtime 2026-07-26 09:42:53, predates the claim's own
   > recording at 11:18, so the cited "ABSENT" probe for `spec.md` was already stale when
   > written. The repo root additionally carries `CLAUDE.md`, `README.md`, `CHANGELOG.md`,
   > `TODO.md`, `REVIEW.md`, `PROMPTLAB-READINESS.md`, `mkdocs.yml`,
   > `sync-claude-template.sh`, `requirements-promptlab.txt`, plus `docs/`, `promptlab/`,
   > `assets/`, `dist/`, `site/` and `.claude/` — all inherited `claude-template` content
   > that `.gitignore` lines 3-19 explicitly disclaims, which is why they do not count as
   > authority here. **The paragraph's conclusion is unaffected**: nothing that survived
   > carries the reasoning behind the pinned decisions.

   Both surviving files actively cite the vanished documents as authority: `.gitignore` cites "spec Open
   Questions #7", "spec Open Question #2", and "spec Scope-out"; `pyproject.toml` says
   `otio-cmx3600-adapter` is "what plan.md names". Implications that need a user decision:
   - The prior spec had **at least 7 open questions**. Their content is unknown and is **not**
     reconstructed here. The numbering in *this* section is fresh and deliberately does **not**
     continue theirs — do not read question 2 here as the old "#2".
   - The two surviving files are *derived* authority: they encode decisions whose reasoning is
     gone. They are strong evidence of *what* was decided (a dependency pin, an ignore rule)
     and no evidence of *why*, so they cannot be safely amended or relaxed.
   - `pyproject.toml`'s Milestone 1 / Milestone 2 markers imply a milestone plan that no
     longer exists. Reference-pack curation is named in `description` but assigned to no
     milestone, so its sequencing relative to Capabilities 1 and 2 is unknown.
   - Question for the user: should this spec be treated as a **reconstruction** subordinate to
     the lost original if it resurfaces, or as the **new** authoritative spec superseding it?

3. **`manifest.json` records processing that measurably did not happen. Is the manifest wrong,
   or is the tool's vocabulary different from its plain meaning?** Unsettled by the
   reconciliation and unsettleable from the artifact, which carries `"version": 1` and no
   schema:
   - `auto_speed: true` is a measurable **no-op**. Clip frame N maps to source frame offset+N
     for all 1,599 frames with SSIM flat across every clip and no progressive drift; net speed
     factor 1.000.
   - `color: "drone_aerial"` at `color_intensity: 0.65` produced a **luma-only** change
     (YAVG −8.25%, YMAX −6.58%) with chroma at or within noise (UAVG +0.11%, VAVG −0.23%,
     SATAVG +2.2%, HUEAVG +0.03%). A parameter named "color" measurably changed no colour.
     *(Control stated 2026-07-27: these percentages are vs an 8-bit-reduction-only baseline
     of the proxy — no matrix conversion — over `crop=1280:544:0:88`, first 450 frames,
     per-frame `signalstats` means, both sides 8-bit. The control is load-bearing: measured
     natively (10-bit vs 8-bit) every statistic shifts −75 to −77% as a pure scale artifact,
     and uncropped letterboxed frames shift YAVG materially. See `REVIEW.md` MAT-2.)*
   - `filtered: false` **directly contradicts** `summary.scenes_filtered: 3` in the same
     document.
   - `scenes_detected: 7` / `scene_threshold: 7.0` do not describe what produced these clips.
     4 of 5 clip boundaries sit at frames ranking 464th, 897th, 1571st and 1752nd of 1909 by
     **`scdet` score** (`|mafd − prev_mafd|`, a *derivative* of frame difference, not frame
     difference itself — mislabelled here until 2026-07-27) — at or below the median, the
     opposite of a scene boundary — while 3 of
     4 clips are exactly `max_duration` (15.000000 s) long. The `7 − 3 = 4` arithmetic matching
     `total_clips` appears to be coincidence, not mechanism. And `7.0` is on an undocumented
     scale: zero of 1,909 source frames exceed even 2.0 on `scdet`'s scale.
   - An **8.633333 s** source region was excluded despite exceeding `min_duration: 7.0` by
     1.63 s, with `min_score: 0.0` unable to explain it; and 3 claimed filtered scenes must fit
     into only **2** disjoint unaccounted regions.
   Resolving these requires the generating tool's source, which is not in scope here. Question:
   is that tool available to inspect, and should the pack treat `manifest.json`'s processing
   semantics as **unreliable** (the current working assumption) while treating its geometry and
   timing as reliable?

4. **Is the source proxy's `bt2020nc` tag correct — and was a colour conversion owed?**
   `DJI_0355_proxy.mp4` declares `color_space=bt2020nc` with `color_primaries=bt2020` and
   `color_transfer=arib-std-b67` (HLG) at 10-bit; the four splits are 8-bit and tagged
   `bt709`, with chroma pixel values measurably carried across **unconverted**. Either the
   splits have a colour-management defect, or the source tag is spurious and no conversion was
   owed. Both branches remain open and no artifact settles it. Neither the bit-depth reduction
   (10→8) nor the matrix retag is recorded anywhere in `manifest.json`.

5. **Should the pack ship an executable regeneration script rather than documented commands?**
   Two recipe defects were confirmed this session, and **both fail silently with exit 0** —
   the most dangerous shape a reproducibility bug can take:
   - `-show_entries frame=pts_time,frame_tags=lavfi.scd.score` uses a **comma** where ffprobe
     requires a **colon** between section specifiers, and drops the score column entirely.
     Reproduced directly: the comma form emitted bare timestamps, the colon form emitted
     `0.033333,2.104`.
   - `select='gt(scene,...)',metadata=print` under `-loglevel error` is **inert**, because
     `metadata=print` writes at INFO level. Proven with a positive control: at
     `gt(scene,0.01)`, which genuinely matches frames, the documented form printed nothing
     while `metadata=print:file=-` printed `lavfi.scene_score=0.053851`. Its silence therefore
     carries **no** information and must never be cited as evidence of "no cuts".
   Documented-but-mistyped commands already produced score-less CSVs once in this pack's
   history. Question: accept prose commands plus Acceptance Criterion 3 as the guard, or
   require a checked-in script? A script would need a home outside the paths this task may
   write to, so it needs a user decision.

6. **Where does raw footage actually live, and is `_archive/` stable?**
   `.gitignore` lines 21–23 ignore `/_01_examples/instagram_reel_v34_all_kb_full.mp4` and
   `/_01_examples/viral_test_v2_4k.mp4` — but `/_01_examples/` **does not exist** (verified),
   and those files now live in the read-only `00-assets/drone-video-examples/`. Separately,
   `manifest.json`'s recorded source path
   `/Users/matthewdeane/Documents/Data Science/python/_projects/...` is unresolvable
   (`/Users/matthewdeane` does not exist); the proxy was located at
   `/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4`
   (92,905,225 bytes). So two of the pack's three footage locations are stale in surviving
   config. Question: which path is canonical going forward, should the `_01_examples` rules be
   retired, and is `_archive/` a durable location or a staging area? This matters because
   locating the proxy is what allowed the split family's provenance, letterbox mechanism,
   `auto_speed` and colour claims to be *verified* rather than marked unverifiable — if
   `_archive/` is transient, that verification is not repeatable.

7. **What is the source of the four vertical files?**
   `DJI_0355_proxy.mp4` was **ruled out** by measurement against a calibrated null
   (best lagged r = +0.5228 for `instagram_reel_test`, below its own time-reversed null of
   +0.7748; MPEG-7 signature `detectmode=full` returned "no matching of video 0 and 1"). No
   parent for them exists in the searched tree, and `manifest.json` documents nothing about
   them. They are also the *earlier* family by roughly five weeks (mtimes 2026-02-04 → 02-08
   versus **03-16 only** for all four splits — corrected 2026-07-27; 03-15 belongs to
   `DJI_0355_proxy.mp4`, not any split file, confirmed by `stat`), so the splits cannot be
   their intermediates. Question: does that project
   still exist anywhere, and should the pack's coverage claim be narrowed to say the vertical
   family's provenance is unrecoverable rather than merely uninvestigated?

8. **Which member of each rendition pair is authoritative?**
   Not determinable from pixels — PSNR is near-symmetric for the viral pair: **34.640697 dB**
   (4K→1080, bicubic) vs **34.404432 dB** (1080→4K, bicubic), a 0.24 dB gap. *(Corrected
   2026-07-27 — adversarial verification killed claim C57, 3/3 unanimous: the original "31.80
   dB" counterpart does not reproduce under any of five scalers swept (33.467–34.714 dB), and
   scaler choice alone moves the figure further than the asymmetry it was cited to prove — so
   the conclusion that neither file is identifiable as the render source is *stronger* than
   originally stated, not weaker. No PSNR figure in this pack is meaningful without naming its
   scaler. See `REVIEW.md` §5.1 group K.)* For the reel pair the naming and the chronology
   actively **conflict**:
   `instagram_reel_v34_all_kb_full.mp4` is the *earlier* render (2026-02-04 14:32) and
   `instagram_reel_test.mp4` the *later* (2026-02-08 17:42), so "v34" is not a later revision
   of "test". Question: which is the master for tuning purposes? They differ in grade
   (YAVG mean 121.83 vs 117.34), so the choice changes any luma-derived threshold.

9. **Is there a dissolve in `instagram_reel_v34_all_kb_full.mp4` at t≈0.77–1.40 s?**
   The corpus's single unexplained structural feature: a 19-frame run above 5× its own median
   frame difference, where the other 7 files max out at 2–5 frames. Its frame-locked 1080p
   twin cannot settle it, since a dissolve in the shared cut would appear identically in both
   and so would not disturb their PSNR. If it is a transition, the "zero transitions
   internally" characterisation needs qualification.

10. **Are there burned-in captions, logos, or graphic overlays?**
    **Unmeasured, but not unmeasurable** — *identifying* an overlay's content needs a rendered
    frame, forbidden here (Open Question 1). *Detecting the presence* of a static or animated
    overlay region does not: region-wise MAFD, `signalstats`, or `freezedetect` on crops all run
    entirely in-pipe. That measurement was not attempted in this pass (a coarse 3×6 spatial-grid
    check found no zero-variance region on the two 1080p verticals, but this is partial, not a
    clearance). *(Corrected 2026-07-27 — adversarial verification killed claim C59, 3/3
    unanimous.)* Separately, overlays are **no longer** a live candidate explanation for a
    "front-loaded motion envelope" — that claim itself was killed on independent verification
    (C56, 3/3 unanimous): the per-second maximum for two of the four verticals falls mid-file,
    not in the opening seconds, and the "13–61×" figure was undefined and did not survive on an
    alternative metric. The residual, narrower finding is only that two of the four verticals
    show elevated frame-difference *range* in their first ~4s — see `REVIEW.md` §3.7 and §5.1
    group E/F. Question: is a *transient*, never-persisted inspection acceptable, or does the
    prohibition bind even in-memory viewing? This is the one open question whose resolution
    would unlock the overlay-presence question specifically.

11. **What tolerance applies to `manifest.json`'s cosmetic defects?**
    `start_time` / `end_time` are recorded at 2 dp, **coarser than one frame period**
    (0.033333 s), and this is not merely cosmetic — it is the demonstrated *cause* of
    `split_003_s66.mp4`'s 1-frame shortfall (25.0 − 16.67 = 8.33; 8.33 × 30 = 249.9;
    floor → 249 frames, versus the true 250-frame span). Any consumer recomputing frame ranges
    from those fields reproduces the same off-by-one. Also unresolved: `total_size_mb: 95.4` is
    correct only read as **mebibytes** (95.3939 MiB vs 100.0278 SI MB, a 4.85% error under the
    stated unit); `avg_score: 68.1` against a computed 68.05; and `clips[]` is **score-sorted,
    not timeline order**, which the manifest never states, so a consumer iterating it in order
    gets reverse-chronological footage. Question: does the pack normalise these on read, or
    report and preserve them?

12. **Mixed HDR/SDR transfer curves across six raw masters from one source tree — is this
    normal capture, or an anomaly?** *(Added 2026-07-27.)* 4 of the 6 raw masters declare
    HLG (`arib-std-b67`); `DJI_20241030011801_0346_D.MP4` declares SDR `bt709`;
    `DJI_20241029174916_0356_D_383181722.mov` declares PQ (`smpte2084`) — a third transfer
    curve, on a different codec (`h264` vs the others' `hevc`) and pixel format (`yuvj420p`
    vs `yuv420p10le`). No file in reach states whether this is a deliberate mixed-format
    capture policy, a firmware/settings change between flights, or an operator error. Any
    downstream pipeline assuming uniform camera colour handling across this footage tree
    would be wrong for at least 2 of 6 files measured.

13. **Are two archive `manifest.json` sidecars themselves the stale artefact, not the
    files?** *(Added 2026-07-27.)* This pack has treated `manifest.json` as ground truth to
    reconcile measurement *against* throughout (item 5, Open Question 3). Two archive
    directories invert that: `highlights_graded_25s`'s manifest documents 3 clips against 10
    files physically present, and `highlights_long`'s documents 3 against 5 present (2 of
    which are byte-identical duplicates under different filenames). Is the manifest in each
    case the authoritative record of what that directory *should* contain, with the extra
    files being stale leftovers from an earlier run — or is the manifest itself the outdated
    artefact? Nothing in either directory states which.

14. **Why does `scenes_detected` vs `total_clips` bookkeeping run in opposite directions
    across manifests from the same tool?** *(Added 2026-07-27.)* `highlights_best`:
    `scenes_detected`(15) − `scenes_filtered`(0) = 15 against `total_clips` 5 — a 200%
    over-count, the widest gap measured anywhere in this pack. `highlights_graded` and
    `highlights_graded_25s`: `scenes_detected` exactly equals `total_clips` (7 and 3
    respectively), `scenes_filtered` 0 both times — no gap at all, for the opposite reason
    (§8.2: `scenes_detected` there tracks output-clip count, not real segmentation). The
    original corpus manifest sits between these (7 − 3 = 4, matching `total_clips` by what
    §4's MAT-5 already showed is coincidence, not mechanism). Three manifests from the same
    splitting tool, three different relationships between these two fields. No file in reach
    explains the tool's actual scene-counting logic well enough to predict which regime a
    new run would land in.
