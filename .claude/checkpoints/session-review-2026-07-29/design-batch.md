# Batch / Proxy Architecture — Design Proposal + Reviewer Assessment

Agent: `design-batch`. Date: 2026-07-29. **DESIGN ONLY — no code was written, no tracked file modified.**
All measurements below labelled "measured in-session" were taken by this agent today on this machine
with `.venv/bin/python` (cv2 5.0.0) and `ffmpeg`/`ffprobe` 8.1.2. Everything else is cited to a file.

---

## 0. Assumptions (state-before-act, per CLAUDE.md Critical Patterns)

| # | Assumption | If wrong |
|---|---|---|
| A1 | `corpus-scope` = the 8-file `00-assets/drone-video-examples/` corpus, mirrored at `data/raw/corpus/`. "Working footage" = `00-WORKING/Videos/`, 153 clips, 112 GB on disk (`du -sh`, in-session). | Counts and cost projections shift. |
| A2 | The design target is the working footage, not the corpus. The corpus is calibration material only. | If the corpus is the target, none of this is needed — a full corpus pass is minutes. |
| A3 | `data/reference_pack/WORKING_FOOTAGE.md` (read in full, in-session) is authoritative for working-footage facts. I did not re-derive its numbers. | — |
| A4 | Proxies are **derived media**, and this repo's licence constraint forbids media under `data/`. I therefore assume proxies live **outside the repo**. This is my assumption, not a stated rule — the stated rule covers frames/images. **Reviewer must confirm.** | If proxies may live in-repo, §5 simplifies. |
| A5 | `.git` stays untouched; `git-repair-mode` default. No git command was run. | — |
| A6 | Single machine, no cluster, no cloud. Apple Silicon (VideoToolbox present and functional — verified in-session). | §4 scheduling changes entirely. |
| A7 | Output contract is unchanged: one `HighlightManifest` JSON per source clip. Batch adds orchestration, not a new output schema. | — |

**Switch variables not named by the task, defaulted per CLAUDE.md:** `archive-write-mode` (read-only,
reference by absolute path), `spec-status` (the reference-pack spec is DRAFT; **this design has no spec
at all and must not be implemented until one is written and signed off**), `verification-completeness`
(PARTIAL — see §9).

---

## 1. Problem statement, in measured numbers

### 1.1 What the pack already established

- 111.4 min of 4K, no batch mode, one full pass = **6.9–15.0 h** (`WORKING_FOOTAGE.md:162-163`).
- `signalstats` over 3 s and `cropdetect` over 2 s of one 4K clip **both exceeded a 2-minute wall
  clock** (`WORKING_FOOTAGE.md:167-170`).
- **Never run two 4K decode jobs concurrently** — they contend and both crawl
  (`WORKING_FOOTAGE.md:174-175`).
- Working footage is **not** letterboxed; the full 3840×2160 raster is picture
  (`WORKING_FOOTAGE.md:149-154`).
- `exposure` returns exactly 1.0 on 19/28 clips and within 0.7% of 1.0 on all 28, at 0.25 weight
  (`WORKING_FOOTAGE.md:129-131`).
- 150 of 153 clips carry `.SRT` telemetry sidecars at 59.94 Hz with GPS + altitude
  (`WORKING_FOOTAGE.md:53-69`). **This is a decode-free motion signal and the design's biggest lever.**

### 1.2 What I measured in-session (new)

Clip: `00-WORKING/Videos/2026-07-12_04h-06h_Khorog/DJI_20260712054120_0200_D.MP4`
(3840×2160, 59.94 fps, hevc 10-bit, 3460 frames).

| Operation | Measured | Derived rate |
|---|---:|---|
| `cv2.VideoCapture` open + first frame | 3.14 s | — |
| `cv2` sequential decode, 120 frames | 25.81 s | **4.6 fps = 0.08× realtime** |
| `cv2` `set(POS_FRAMES, 600)` + read | 11.15 s | — |
| `cv2` `set(POS_FRAMES, 1200)` + read | 9.74 s | — |
| `ffmpeg` software decode, 120 frames, no filter | 18.95 / 26.23 / 22.54 s (3 passes) | **~5.3 fps = 0.09× realtime** |
| `ffmpeg -hwaccel videotoolbox`, 120 frames, no filter | 2.34 / 3.71 / 3.52 s (3 passes) | **~34 fps = 0.57× realtime** |

Two consequences, both decisive:

**(a) A random seek costs ~45–50× a sequential frame read.** 9.74–11.15 s per `cap.set(POS_FRAMES)` +
`read()` versus 0.217 s per sequential frame. Every scorer in this package samples by seeking
(`scoring_sharpness.py:50`, `scoring_exposure.py:64`, `scoring_composition.py:291`), 10 samples per
segment (`pipeline.py:53`), in three separate `VideoCapture` sessions per segment
(`pipeline.py:114,117,121`).

**(b) VideoToolbox hardware decode is 6–8× software and is real.** I verified it emits actual frames,
not a silent no-op: `-hwaccel videotoolbox … -frames:v 120 -pix_fmt yuv420p -f rawvideo -` produced
**exactly 1,492,992,000 bytes = 120 × 3840 × 2160 × 1.5**. The speedup is stable across three passes,
so it is not a page-cache artefact (the software runs did not get faster on repeat; they got slower).

### 1.3 Cost projection for the current code, unmodified, on one 161 s working clip

161.2 s is the pack's measured max clip duration (`WORKING_FOOTAGE.md:39`) = 9,662 frames.
`max_duration` default 15.0 s (`weights.py:105`) ⇒ ≥11 segments.

| Stage | Code | Projected |
|---|---|---:|
| `detect_active_rect`, 5 s of 4K cropdetect | `letterbox.py:55`, `pipeline.py:86` | **> 5 min** (pack: >2 min for 2 s) |
| `compute_motion_series`, full sequential decode + LK flow at 3840×2160 | `motion.py:71-105`, `pipeline.py:88` | ≥ 35 min (decode alone) |
| PySceneDetect, a **second** full decode pass | `segmentation.py:38` | ≥ 35 min |
| 3 scorers × 11 segments × (1 open + 10 seeks) | `pipeline.py:114,117,121` | ≈ 57 min |
| gates: 2 ffmpeg passes over every segment = 2× the whole clip decoded again | `gates.py:110,117` | ≈ 61 min |
| **Total** | | **≈ 3.2 h for one 161 s clip ≈ 71× video duration** |

**This projection disagrees with the pack's 3.7–8.1× by roughly an order of magnitude, and I did not
run an end-to-end 4K pass to settle it** (the task forbids it, and it would take hours). Both numbers
are on the record; §9 lists the one measurement that would reconcile them. Do not size a schedule on
either until that measurement exists. What is *not* in doubt is the shape: the clip is decoded
end-to-end **at least 4 times** (motion, scenedetect, blackdetect, freezedetect) plus 30 random seeks
per segment, and every one of those passes is at native 4K.

---

## 2. Proxy generation

### 2.1 Recommended spec

```
resolution : 1280x720   (exactly 3840/3 x 2160/3)
codec      : h264, yuv420p 8-bit, CRF 18, preset veryfast
frame rate : UNCHANGED (59.94 fps) — do not decimate; see 2.3
colour     : tag-preserving passthrough; NO tonemap (see 2.4)
audio      : none (measured: zero audio streams on all 153, WORKING_FOOTAGE.md:27)
container  : .mp4, faststart
naming     : <sha-or-fingerprint>.<spec-hash>.mp4 under an out-of-repo cache root
```

### 2.2 Why 1280×720 and why an exact integer divisor

Two independent arguments, one measured, one structural:

**Measured — non-integer scale factors damage the sharpness statistic disproportionately.**
Scale sweep on `data/raw/corpus/split_001_s70.mp4`, active picture 1280×544 (the pack's measured crop),
5 frames, `INTER_AREA`, in-session:

| frame | lapvar @1.0 | @0.75 | @0.5 | @0.25 |
|---:|---:|---:|---:|---:|
| 30 | 1100.8 | 662.4 | 1026.6 | 728.7 |
| 100 | 1006.4 | 575.3 | 856.8 | 591.1 |
| 200 | 791.9 | 440.6 | 649.2 | 427.0 |
| 300 | 659.3 | 423.9 | 621.9 | 414.6 |
| 400 | 836.5 | 480.3 | 730.1 | 483.3 |

Retention vs native: **0.5 → 0.82–0.94**, but **0.75 → 0.56–0.64** — *worse than 0.25* (0.54–0.66).
The behaviour is non-monotonic in scale. The clean 2:1 box-filter path (0.5) preserves far more
high-frequency energy than the resampled 0.75 path. Conclusion: use an exact integer divisor.

**Structural — 1280×720 is the resolution every constant in `src/` was chosen against.** The corpus
is 1280×720 (`editorial_style.json` → `letterbox.coded_frame_px`), and 3840/3 = 1280, 2160/3 = 720
exactly. Proxying to 1280×720 makes the working footage geometrically identical to the only
calibration material this project has. That is worth more than the marginal resampler-quality
advantage of 1920×1080 (÷2).

**Honest counter-argument, unresolved:** ÷3 is not a power of two, so it is not a clean box filter
either. I measured ÷2, ÷4 and ×0.75 — **I did not measure ÷3.** If the reviewer prefers, 1920×1080
(÷2) is the measured-safe choice and 960×540 (÷4) is the measured-safe cheap choice. §9 lists the
÷3 measurement as required before adoption.

### 2.3 Do not decimate frame rate in the proxy

`motion.py`'s magnitude series is per-frame displacement and `compute_jerk_series` differentiates
**with respect to frame index**, not time (`motion.py:164-166`). Halving the frame rate rescales the
index axis and changes every jerk value non-linearly. Separately, `DEFAULT_MIN_SCENE_LEN_FRAMES = 15`
(`segmentation.py:22`) is frame-denominated. A proxy at a different fps from the master silently
changes the meaning of both. Keep 59.94.

### 2.4 Do not tonemap in the proxy

77% of the footage is HLG/bt2020 (`WORKING_FOOTAGE.md:36`). Tonemapping would be the *right* thing
for a human-facing proxy and the *wrong* thing here: the pack measured what `cv2` actually hands the
scorers from these sources (`WORKING_FOOTAGE.md:95-108`) and the fix for exposure is to replace the
metric, not to pre-correct the pixels (`WORKING_FOOTAGE.md:138-141`). Also, this ffmpeg build has no
`zscale` filter (`WORKING_FOOTAGE.md:144-145`), so the tonemap chain cannot be built here anyway.
A proxy that silently changes the transfer curve would invalidate every comparison against the pack.

### 2.5 Generation command shape, with a mandatory verification step

```
ffmpeg -v error -hwaccel videotoolbox -i "$SRC" \
       -vf scale=1280:720 -c:v libx264 -crf 18 -preset veryfast \
       -pix_fmt yuv420p -an -movflags +faststart "$DST"
```

**This command must be byte-verified before adoption, not trusted.** Measured in-session today:
`-hwaccel videotoolbox -hwaccel_output_format nv12 -i … -vf scale=960:540 -f rawvideo -` **exited 0
in 0.50 s and produced 0 bytes.** So did `-hwaccel videotoolbox … -vf "hwdownload,format=nv12,scale=…"`.
Both look like a 40× speedup and are in fact a silent total failure. This is the same
exit-0-with-wrong-output trap `data/reference_pack/README.md` documents for the `scdet` recipe.
The batch tool must assert `ffprobe nb_read_frames(proxy) == nb_read_frames(master)` after every
proxy generation and fail loudly otherwise.

---

## 3. Signal-by-signal resolution invariance — the core of the design

All figures measured in-session on `split_001_s70.mp4`, 5 frames × 4 scales, using the project's own
functions (`_rule_of_thirds_score`, `_horizon_levelness_score`, `_clipped_fraction`) imported directly.

| Signal | Code | Scale-invariant? | Evidence | Consequence for proxying |
|---|---|---|---|---|
| **Sharpness — absolute** (`sharpness_raw`) | `scoring_sharpness.py:57` | **NO — strongly** | 1006.4 → 856.8 → 591.1 across ÷1/÷2/÷4; upscaled 3× to 3840×1632 it collapses to **23.4** (43× drop). A native 4K working frame measured **27.4** vs ~1000 on the 720p corpus. | `sharpness_raw` is meaningless across resolutions. See P1-5. |
| **Sharpness — within-file rank** (`scores.sharpness`) | `scoring_sharpness.py:66-94` | **YES, in this sample** | Rank order 30 > 100 > 400 > 200 > 300 was **identical at all four scales — zero inversions in 5 frames × 4 scales.** | Safe to compute on the proxy. This is the load-bearing result. |
| **Exposure** | `scoring_exposure.py:34-40` | Untestable from this data | `_clipped_fraction` was **0.000000 at every scale** on the corpus frame. That is not evidence of invariance — the signal is saturated (cf. `WORKING_FOOTAGE.md:129`). | In principle a pixel *fraction* is scale-invariant in expectation, but downscaling averages extremes toward the mean and can only *reduce* measured clipping. Direction is known, magnitude is not. |
| **Composition — rule-of-thirds** | `scoring_composition.py:184-217` | **YES** | Max deviation 0.077 across a 4× downscale; rank order preserved at all scales. Mechanism verified: `StaticSaliencySpectralResidual` resizes internally to **64×64** (`getImageWidth()/getImageHeight()` = 64) and resizes the map back to input size (checked at 720p, 544p and 2160p — output shape always equals input shape, so the centroid coordinate space is correct). | Safe on the proxy. |
| **Composition — horizon levelness** | `scoring_composition.py:220-258` | **NO — catastrophically** | Native = 1.000 on all 5 frames. Downscaled, it disagreed on **6 of 15** evaluations. Worst: frame 100, 1.000 → **0.158** at ÷4 (Δ 0.842). At ÷2, frame 300 → 0.444. | **Not portable.** See P1-4. |
| **Motion magnitude / jerk** (`motion_smoothness_raw`) | `motion.py:97-98`, `164-166` | **NO** | Units are *pixels per frame*. 4K gives 3× the pixel displacement of 720p for the same physical pan, and jerk is a second difference w.r.t. frame index, so frame rate rescales it again. | See P2-4. Fix is unit change, not a correction factor. |

### 3.1 What follows for sharpness scoring — stated plainly, because the task asks

Laplacian variance is **not** scale-invariant, and the measured behaviour is worse than "not
invariant": it is **not even monotonic in scale** (÷0.75 retains less than ÷0.25 on 4 of 5 frames),
and the retention ratio varies by frame at a fixed scale (0.82–0.94 at ÷2). **There is therefore no
correction constant, and no per-file correction factor either.** Anyone tempted to write
`lapvar_4k ≈ k · lapvar_proxy` should read that table again.

Three things follow, in order of importance:

1. **Score sharpness on the proxy and use only the rank.** `min_max_normalize` (`scoring_sharpness.py:66`)
   is a within-file rank and the rank survived every scale I tested with zero inversions. This is the
   design's licence to proxy at all.
2. **`sharpness_raw` must be either dropped or qualified.** It is currently documented as the
   cross-file-comparable value (`manifest.py:147-148`, `pipeline.py:162-165`) and it is not — not
   between proxy and master, and not between the 720p corpus and the 4K working footage *today*,
   before any proxy exists. If it is kept, it must carry the analysis resolution beside it and the
   manifest must forbid comparing values with differing resolutions. See P1-5.
3. **The rank result is 5 frames from 1 file at 720p.** It is exactly the near-tie case where a rank
   inversion would occur, and near-ties are already handled by the `max == min → None` branch. Confirm
   on the working footage before relying on it (§9).

---

## 4. Work scheduling

### 4.1 Two stages with opposite parallelism rules

```
STAGE A  proxy generation      4K-decode-bound   → STRICTLY SERIAL, 1 job
STAGE B  analysis over proxies not 4K-bound      → PARALLEL, N workers
```

Stage A is serial because the pack measured concurrent 4K decode contention directly
(`WORKING_FOOTAGE.md:174-175`) — "one job at a time finishes sooner than two in parallel". This is a
measured constraint, not a heuristic, and the batch runner must enforce it structurally (a semaphore
of capacity 1 around every job that touches a master), not merely default to it.

**Stage A cost, from in-session measurement.** 111.4 min at 59.94 fps = 400,638 frames.

| Path | Rate | Stage A wall clock |
|---|---:|---:|
| Software decode | 5.3 fps | **≈ 21 h** |
| VideoToolbox decode | 34 fps | **≈ 3.3 h** |

Hardware decode is the difference between "run it overnight" and "run it over a weekend". It is the
single highest-value item in this design. It is also the one with a verified silent-failure mode
(§2.5), so it must ship with the frame-count assertion or not at all.

Stage A is one-time and cacheable (§5). Stage B then runs against 1280×720 h264 8-bit material — the
class the pack measured at **0.4–1.2× realtime** (`WORKING_FOOTAGE.md:162`), i.e. hours not days, and
parallelisable because it is no longer contending on the 4K decoder.

**I have not measured proxy decode throughput** — the 0.4–1.2× figure is the pack's, for 720p/1080p
material generally. §9.

### 4.2 Worker count

`os.cpu_count()` on Apple Silicon counts efficiency cores, which will drag a decode pool. Recommend
`min(4, performance_cores - 1)`, defaulting to 4, **configurable and defaulting low**. I have no
in-session measurement of the parallel scaling curve for 720p decode on this machine, so this number
is a starting point to be measured, not a claim. Do not increase it without measuring — the one
concurrency fact this project actually has says contention is worse than expected.

### 4.3 Ordering and failure isolation

- Order Stage A by **ascending duration**, so the run produces usable output early and a stall on the
  161 s clip does not block 152 others.
- One clip's failure must not abort the batch. Per-clip status persisted to the cache (§5) as
  `pending | proxied | analysed | failed:<reason>`, so a re-run resumes rather than restarts. This
  mirrors the `/resume` checkpoint discipline CLAUDE.md already mandates for agents, applied to media.
- Run detached (`WORKING_FOOTAGE.md:180`) with progress to a log file, never to a TTY the session owns.

### 4.4 The telemetry shortcut — the biggest available win, and it is free

150 of 153 clips carry `.SRT` sidecars at 59.94 Hz with GPS and altitude
(`WORKING_FOOTAGE.md:53-69`), from which the pack already derived ground speed, vertical speed and a
motion classification **with zero video decode**.

`motion.py`'s entire purpose is to produce a camera-motion magnitude series, at a measured cost of a
full sequential 4K decode plus Lucas-Kanade optical flow per frame — the largest single item in §1.3.
Telemetry gives a motion series that is:

- free (text parse, milliseconds),
- **resolution-invariant** (m/s, not pixels/frame),
- **frame-rate-invariant** (per second, not per frame),
- physically interpretable, so a threshold on it can be justified in units a human can argue with.

**Recommendation:** in Stage B, derive `motion_minima_boundaries` from telemetry where a sidecar
exists, and fall back to optical flow only for the 3 clips without one. Keep optical flow available
behind a flag for cross-validation. This is the change that most reduces cost and most improves
groundedness at the same time — the resulting boundaries trace to a measured GPS track rather than to
`FEATURE_PARAMS`/`LK_PARAMS`, which the audit found trace to nothing.

**Caveat the pack itself raises:** the telemetry classifier's thresholds "are stated so they can be
challenged, not because they are validated", and nothing has been cross-checked against visual review
(`WORKING_FOOTAGE.md:91-93`). Also: no gimbal angles in this DJI variant (`WORKING_FOOTAGE.md:59`),
so telemetry gives platform motion, **not** camera pointing. A gimbal-only pan is invisible to it.
That is a real limitation, and it is the argument for keeping optical flow as a cross-check rather
than deleting it.

---

## 5. Cache design

### 5.1 Identity keys

**Source identity** — `sha256` is correct but 112 GB at ~1 GB/s is ~2 min of pure I/O per full scan.
Use a two-tier scheme:

- *fast key* = `(realpath, st_size, st_mtime_ns, ffprobe fingerprint: codec, w, h, r_frame_rate,
  nb_frames, duration, bit_rate)`. Cheap, and the ffprobe part catches the case where a file was
  replaced with a same-size different file.
- *strong key* = `sha256`, computed lazily and only in `--verify` mode, matching the pack's existing
  sha256 baseline discipline (`CLAUDE.md` Commands).

**Params identity** — a stable hash over exactly the constants that affect each artifact. Not a hash
of the whole module (comment edits would invalidate everything); an explicit, enumerated tuple.

### 5.2 What is cached, keyed on what

| Artifact | Key | Invalidated by |
|---|---|---|
| `probe.json` | source fast-key | source change |
| `proxy.mp4` | source fast-key + proxy spec (w, h, codec, crf, fps policy) | source or proxy spec |
| `telemetry.json` (parsed SRT series) | sidecar fast-key | sidecar change |
| `active_rect.json` | **analysis-target** key (i.e. the proxy) + `CROPDETECT_FILTER` + `probe_seconds` | proxy or cropdetect params |
| `motion_series.json` | analysis-target key + hash(`FEATURE_PARAMS`, `LK_PARAMS`, `MIN_TRACKED_POINTS`, `max_frames`) **or** telemetry key when telemetry-derived | proxy or flow params |
| `scene_boundaries.json` | analysis-target key + (`scene_threshold`, `min_scene_len_frames`) + fps | proxy or detector params |
| `segment_scores.json` | analysis-target key + segment `(start, end)` rounded to the frame + per-scorer params hash + `active_rect` | any of those |
| `gates.json` | analysis-target key + segment + `GateConfig` | ditto |

**The point of separating these keys** is that the expensive things are keyed on the cheap-to-stabilise
inputs. Concretely: editing `weights.py` invalidates **nothing** — only the composite is recomputed,
from cached per-signal scores, in milliseconds across all 153 clips. Editing `scene_threshold`
invalidates boundaries, segments, scores and gates but **not** the proxy and **not** the motion series.
Editing the proxy spec invalidates everything below it. That gradient is the whole design.

`active_rect` **must** be keyed on the proxy, not the master. See P2-3: an `ActiveRect` detected at one
resolution and applied at another mis-crops silently.

### 5.3 Layout and provenance

Mirror `data/reference_pack/probe/`'s convention — flat, per-clip, plain JSON, one file per artifact,
regenerable from a documented recipe. Cache root **outside the repo** (A4), default
`~/.cache/drone_video_ai/`, overridable by `--cache-root`.

Every cached artifact records: the recipe that produced it, the tool version (`ffmpeg -version`,
`cv2.__version__`), the key inputs, and a UTC timestamp. Two reasons: the pack's own convention, and
the fact that a `brew upgrade` has already silently broken this toolchain once (`CLAUDE.md`).

**The emitted manifest must record both paths.** `source_file` stays the master (that is what a
downstream edit references), and a new `analysis_source` block records the proxy path, its resolution,
and its spec hash. Without this, a manifest is a set of numbers with no way to know what they were
measured on — and given §3, resolution is not an incidental detail, it is part of the measurement.

---

## 6. Where this belongs

**Recommendation: a new module `src/drone_video_ai/batch/` and a new console script `drone-batch`.
Do not change `drone-highlights`' one-file contract.**

| Option | Verdict |
|---|---|
| Extend `drone-highlights` to accept a directory | **No.** `cli.py:30` takes one positional `input` and `cli.py:32` one required `-o`. Making it variadic changes the meaning of `-o` and every existing invocation's contract, for a feature that is orchestration, not extraction. |
| A shell script over the existing CLI | **No.** Caching, key management and the serial-4K constraint are real logic. A script cannot express "invalidate scores but not the proxy". |
| **New `batch/` module + `drone-batch` script** | **Yes.** Orchestration is a separate concern. `pyproject.toml` already establishes one console script per capability. |

**One change to existing code is unavoidable, and it should be exactly one:**

```python
def run_pipeline(video_path, config=None, analysis_path=None) -> HighlightManifest
```

`analysis_path` defaults to `video_path` (so every current caller and all 93 unit tests are unaffected).
When supplied, all decode-and-measure work targets `analysis_path` (the proxy) while `probe_source_file`
targets `video_path` (the master), so `source_file` in the manifest describes the real footage and
timecodes stay in master time. Frame-rate parity between master and proxy (§2.3) is what makes that
safe; the batch layer must assert it.

`PipelineConfig` also needs `letterbox_probe_seconds` and `skip_letterbox_detection` (see P1-1), and
must actually pass `ffmpeg_bin` through (P1-2).

**What `batch/` should contain and nothing more:** `discovery.py` (walk a root, match extensions, pair
`.SRT` sidecars), `proxy.py` (generate + verify), `cache.py` (keys, read/write, invalidate),
`schedule.py` (serial Stage A, parallel Stage B, resume), `cli.py`. No scoring logic. If a scorer needs
to change, it changes in `highlight_extraction/`.

---

## 7. What this must NOT do

Absolute (violating any of these is a defect, not a trade-off):

1. **Never write a frame or image file anywhere in the repo.** Licence constraint, stated in
   `CLAUDE.md` and restated as a hard Scope-out in the reference-pack spec. All measurement stays
   in-pipe (`-f null -`) or in NumPy. A proxy `.mp4` is not a frame — but see (2).
2. **Never write proxies inside the repo** (A4 — reviewer to confirm). Default the cache root outside
   the repo so the answer does not depend on `.gitignore` being correct.
3. **Never copy, move or modify anything under `00-assets/`, `_archive/`, or `00-WORKING/`.** Masters
   are read-only and referenced by absolute path. The batch tool opens them for reading only, and
   never writes a sidecar next to one.
4. **Never run two 4K decode jobs concurrently** (measured, `WORKING_FOOTAGE.md:174-175`).
5. **Never treat an ffmpeg exit code as evidence the filter chain produced output.** Measured today:
   two plausible hwaccel+scale chains exited 0 and produced zero bytes. Assert frame counts.
6. **Never apply an `ActiveRect` across resolutions** (P2-3 — NumPy clamps silently).
7. **Never compare `sharpness_raw` or `motion_smoothness_raw` across differing resolutions or frame
   rates** (§3, P1-5, P2-4).
8. **Never invent a constant to close a measurement gap.** Where this design needs a number it does not
   have, §9 says so instead. That includes the tempting ones: worker count, proxy CRF, and the
   sharpness-rank stability claim on 4K.
9. **Never delete or overwrite a cache entry as a side effect of reading it.** Invalidate by writing a
   new key, so a bad run cannot destroy a good one — with `.git` corrupt there is no undo.
10. **Never implement this before a spec is written and signed off.** `spec-status` default: the one
    spec in this repo is DRAFT, and this capability has none.

---

## 8. Issues found in existing code

Every item cites `file:line`, states the input that triggers it and what breaks. Items I could not make
concrete were dropped rather than padded. Line numbers verified by reading the files in-session.

### P1 — must fix

**P1-1 · `letterbox.py:55` + `pipeline.py:86` — mandatory 5 s of 4K `cropdetect` per clip, unconfigurable,
buying a guaranteed no-op.**
`DEFAULT_PROBE_SECONDS = 5.0`; `pipeline.py:86` calls `detect_active_rect(video_path)` with no override,
and `PipelineConfig` (`pipeline.py:46-56`) exposes no field for it.
*Input:* any clip in `00-WORKING/Videos/`.
*Breaks:* the pack measured `cropdetect` over **2 s** of one 4K clip exceeding a **2-minute** wall clock
(`WORKING_FOOTAGE.md:167-170`). Five seconds projects to **>5 min per clip, >12.75 h across 153 clips**
— before a single frame is scored. And the pack separately measured that this footage **is not
letterboxed** (`WORKING_FOOTAGE.md:149-154`), so the entire cost buys a full-frame no-op.
*Fix:* `PipelineConfig.letterbox_probe_seconds` and `skip_letterbox_detection`; batch layer detects on
the proxy, once, cached.

**P1-2 · `pipeline.py:86` — `PipelineConfig.ffmpeg_bin` is silently ignored by letterbox detection.**
`ffmpeg_bin` (`pipeline.py:55`) is threaded to gates (`pipeline.py:153`) but `detect_active_rect` is
called with no `ffmpeg_bin`, taking the default `"ffmpeg"` (`letterbox.py:84`).
*Input:* `run_pipeline(p, PipelineConfig(ffmpeg_bin="/opt/homebrew/bin/ffmpeg"))` in an environment
where `ffmpeg` is not on `PATH`.
*Breaks:* `subprocess.run` at `letterbox.py:103` raises `FileNotFoundError`. `check=False` suppresses
`CalledProcessError`, not `FileNotFoundError`, and nothing catches it — the whole pipeline dies despite
a valid binary having been supplied. A batch runner pinning an absolute ffmpeg path (exactly what
`CLAUDE.md`'s documented `brew upgrade` breakage argues for) hits this on clip 1.
*Fix:* pass `ffmpeg_bin=cfg.ffmpeg_bin` at `pipeline.py:86`.

**P1-3 · `scoring_exposure.py:17-22` — a false provenance comment on a signal measured to be inert.**
The comment reads "conservative, documented thresholds -- not invented magic numbers buried inline; see
highlight_extraction/weights.py for the scoring-weight configuration these values feed into."
`weights.py` (all 135 lines, read in-session) contains **no exposure threshold** — only weight and
duration profiles. The cross-reference is dangling, and no measurement in `data/reference_pack/`
grounds 5 or 250.
*Input:* any two working clips, one well-exposed and one badly exposed by any human standard.
*Breaks:* the pack measured `exposure` at exactly 1.0 on 19/28 clips and within 0.7% of 1.0 on all 28
(`WORKING_FOOTAGE.md:129`), at 0.25 weight (`weights.py:80`). The two clips' exposure scores differ by
<0.007, contributing <0.002 to the composite difference. A quarter of the weight budget is a constant.
The comment's damage is separate from the numbers': it instructs a future reader not to question them,
in a repo whose Constitution names invented constants as the primary failure mode.
*Fix:* delete the dangling cross-reference and state the thresholds are unvalidated on this footage,
citing `WORKING_FOOTAGE.md:138-141`. Replacing the metric is a separate, spec-level decision.

**P1-4 · `scoring_composition.py:225-232` — horizon levelness mixes scaled and absolute parameters, so it
is not resolution-portable.**
`cv2.Canny(gray, 50, 150)` (line 225) uses absolute gradient thresholds; `maxLineGap=10` (line 232) is
absolute pixels; `threshold=60` (line 230) is an absolute accumulator vote count — while
`minLineLength=max(1, width // 3)` (line 231) *is* scaled. The operating point therefore moves with
resolution.
*Input:* the same clip scored at two resolutions. Measured in-session on `split_001_s70.mp4`:
`_horizon_levelness_score` = 1.000 on all 5 native frames; downscaled it disagreed on **6 of 15**
evaluations, worst case frame 100 at ÷4: **1.000 → 0.158 (Δ 0.842)**; at ÷2, frame 300 → 0.444.
*Breaks:* horizon is half of `composition` (`scoring_composition.py:165-166,306`) and composition carries
0.25 (`weights.py:82`), so a 0.842 sub-score swing moves the composite by **0.105** with no content
change. Two consequences: (a) composition cannot be computed on a proxy and compared to a master; (b)
**independently of proxies, composition scores measured on the 1280×720 corpus do not transfer to the
3840×2160 working footage** — a 3× linear difference, larger than the ÷2 step that already broke it here.
*Not measured:* behaviour at 3840×2160. I measured only downscales from 720p. The direction at 4K is
genuinely uncertain — `minLineLength` scales up (harder) while vote counts scale up (easier).
*Fix:* express all four parameters as fractions of frame dimension, or normalise every frame to a fixed
analysis resolution before this scorer runs. Then re-derive `MAX_HORIZON_TILT_DEGREES` (line 161), whose
docstring justification ("a professionally-composed aerial shot with an intentional tilt rarely exceeds
this") is precisely the general-knowledge-about-drone-footage reasoning the Constitution prohibits.

**P1-5 · `manifest.py:147-150` + `pipeline.py:162-165` — `sharpness_raw`/`motion_smoothness_raw` are
documented as cross-file-comparable and are not.**
The comment states they are "Absolute, cross-file-comparable measurements … so Capability 2 has something
cross-file-comparable to select on."
*Input:* one corpus clip (1280×720) and one working clip (3840×2160), both scored today.
*Breaks:* measured in-session, `cv2.Laplacian(...).var()` on a 4K working frame = **27.4**; on a 720p
corpus frame = **~1000**. That is a **36× gap driven by resolution, not by sharpness.** Capability 2
selecting the sharpest clips across a mixed library by `sharpness_raw` would rank every 720p clip above
every 4K clip, unconditionally. The same applies to `motion_smoothness_raw` (see P2-4). This is not a
future proxy problem — it is live today, because the corpus and the working footage are both in scope
and differ by 3× linear.
*Fix:* record the analysis resolution and frame rate alongside each raw value and make comparison across
differing values an explicit error, or drop the "cross-file-comparable" claim. Note that this defect
does **not** invalidate the change in `bc3a499` — carrying a raw value is still better than fabricating
a 1.0. It invalidates the justification written beside it.

**P1-6 · `composite.py:45` + `manifest.py:82-87` — the manifest reports weights that were not applied.**
`composite.py:45` skips any signal whose score is `None`, and `composite.py:57` renormalises by
`total_weight`. `scoring_weights.weights` is serialised unconditionally from the configured profile.
*Input:* any single-shot file — which is **every file in the corpus** (measured, zero hard cuts) and, for
the working footage, unknown because `scdet` has not been run there (`WORKING_FOOTAGE.md:190-192`).
*Breaks:* with one segment, `min_max_normalize` and `invert_and_normalize` both return `None`
(`scoring_sharpness.py:90`, `scoring_motion_smoothness.py:49`), so composite =
`(0.25·exposure + 0.25·composition) / 0.5` — a two-signal score. The manifest nonetheless reports
`{"sharpness": 0.25, "exposure": 0.25, "motion_smoothness": 0.25, "composition": 0.25}`. Two harms:
(a) the document asserts a false fact about its own computation, and a consumer cannot recompute
`composite_score` from the fields provided; (b) across files, a multi-segment file's best segment can
collect up to 0.25 of within-file sharpness rank that a single-segment file structurally cannot, so
Capability 2 ranking clips by `composite_score` **systematically prefers multi-segment files**.
*Counter-argument, stated fairly:* `scoring_weights` can be read as configuration rather than as applied
weights, and within any single manifest the denominator is uniform (both normalisers return all-`None`
or all-numeric), so intra-file ranking is sound. The defect is cross-file, and it is exactly where
Capability 2 operates.
*Fix:* emit `applied_weights` per segment, or a per-segment `signals_applied` list. One extra field.

### P2 — should fix

**P2-1 · `manifest.py:128` — stale `normalization.motion_smoothness` description.**
`bc3a499` updated the `sharpness` description (line 126) to "null when undefined (n<2, or all segments
equal). NOT comparable across files -- use sharpness_raw for that", but left line 128 as
`"in-video min-max over inverse jerk magnitude -> [0,1]"` — despite `invert_and_normalize`
(`scoring_motion_smoothness.py:49,54`) having the *identical* null contract and
`motion_smoothness_raw` now existing.
*Input:* a consumer reading `normalization.motion_smoothness`, then
`float(seg["scores"]["motion_smoothness"])`.
*Breaks:* `TypeError: float() argument must be … not 'NoneType'` on every single-shot file — all 8
corpus files. The block that exists specifically to tell consumers the range lies about it.
*This is the sibling-artifact drift failure mode `CLAUDE.md` warns about, occurring inside one dict
literal, four lines apart.* Grep the pack's five artifacts for the same claim before closing it.

**P2-2 · `letterbox.py:73-78` (`ActiveRect.crop`) — silent mis-crop on any resolution mismatch.**
The docstring warns callers, but nothing enforces it and NumPy does not raise.
*Input:* an `ActiveRect(1280, 544, 0, 88)` detected on the master, applied to a 640×272 proxy frame.
*Breaks:* verified in-session — returns a **(184, 640)** array. Not the whole frame, not the intended
crop: a wrong region, silently, with no exception. Every scorer would then measure a wrong sub-rectangle
and the manifest would look entirely normal. This is the single most dangerous interaction between the
existing code and the proposed proxy layer.
*Fix:* add `source_width`/`source_height` to `ActiveRect` and raise in `crop()` on mismatch. Cheap,
and it converts a silent wrong answer into a loud failure.

**P2-3 · `motion.py:30-35` + `segmentation.py:22` — pixel- and frame-denominated constants change meaning
across the two footage classes.**
`FEATURE_PARAMS` (`minDistance=8`, `blockSize=7`) and `LK_PARAMS` (`winSize=(21,21)`) are absolute pixels;
`DEFAULT_MIN_SCENE_LEN_FRAMES = 15` is absolute frames.
*Input:* the corpus (1280×720, 30 fps) versus the working footage (3840×2160, 59.94 fps).
*Breaks:* a 21×21 LK window covers 1/9 the fractional frame area at 4K that it covers at 720p, so the
tracker follows a different spatial scale of motion on the two classes. `min_scene_len` of 15 frames is
0.50 s on the corpus and **0.25 s** on the working footage — the same nominal setting is a 2× different
minimum scene length. The comment at `motion.py:28-29` ("tuned for general handheld/aerial footage; not
footage-specific") is honest that these are not grounded, which makes it worse, not better: they are
also not dimensionless.
*Fix:* express spatial parameters as fractions of frame width and temporal ones in seconds; convert at
call time using the probed fps.

**P2-4 · `motion.py:97-98,164-166` — `motion_smoothness_raw` has resolution- and frame-rate-dependent
units.**
`magnitude` is the mean Euclidean displacement of tracked points **in pixels between adjacent frames**;
`compute_jerk_series` takes a second difference **with respect to frame index**.
*Input:* the same physical camera movement filmed at 1280×720/30 and 3840×2160/59.94.
*Breaks:* pixels-per-degree is 3× at 4K, and the frame interval is half, so the per-frame displacement
series is on a different scale, and the second difference w.r.t. index rescales it again. The value
stored in `scores.motion_smoothness_raw` and advertised as absolute (`manifest.py:147-150`) is therefore
not comparable across the two footage classes — the P1-5 problem, second instance.
*I did not derive the exact combined exponent* and will not invent one; the resolution factor (3× linear)
is measurable directly and should be, before any cross-file use.
*Fix:* express magnitude as **fraction of frame width per second**. Then it is dimensionless and
frame-rate-independent, and it becomes directly comparable with the telemetry-derived m/s series (§4.4).

**P2-5 · `scoring_motion_smoothness.py:27-31` — the full-video jerk series is recomputed per segment.**
`compute_jerk_series(samples)` is called inside `compute_raw_jerk_magnitude`, which `pipeline.py:119`
calls once per segment. Line 28 additionally builds a full-length Python `list` of booleans per segment.
*Input:* a 161 s working clip = 9,662 samples, ≥11 segments.
*Breaks:* O(n_segments × n_frames) where O(n_frames) suffices — 11 full `np.diff` passes plus 11 × 9,662
Python-level attribute accesses, and a fresh n-float array allocated each call.
*Honest weighting:* this is **not** the dominant cost today — decode is, by orders of magnitude. It is
P2 because the design in §4–§5 removes the decode cost, at which point this becomes the visible one, and
because it grows with both factors on this footage.
*Fix:* compute the jerk series once in `pipeline.py` and pass slices; use `np.searchsorted` on the times
array instead of a Python list comprehension.

### P3 — polish

**P3-1 · `pipeline.py:203-205` — `avg_composite_score` is fabricated as 0.0 when there are no segments.**
`avg_composite = … if segments else 0.0`. A file where every segment fails a gate emits
`avg_composite_score: 0.0`, indistinguishable from a file whose segments genuinely scored zero. This is
the same fabrication `bc3a499` removed from the normalisers, surviving three lines from the code that
implements the new principle. A consumer can defend itself by checking `total_segments == 0`, hence P3.
*Fix:* `None`, consistent with the rest of the change.

**P3-2 · `common/schema.py:174` + `manifest.py:125-135` — the null-rank mitigation is neither validated
nor documented.**
`validate_highlight_manifest` requires only `["sharpness", "exposure", "motion_smoothness",
"composition"]` in `scores`, so a manifest omitting `sharpness_raw`/`motion_smoothness_raw` validates
clean — and `SegmentScores.from_dict` (`manifest.py:166-167`) defaults them to `None` via `.get()`, so a
legacy v2 manifest round-trips into a v3-shaped object with silent nulls in the two fields that are the
entire mitigation for null ranks. Neither field appears in `DEFAULT_NORMALIZATION`.
*Fix:* require both keys for `version >= 3` and add their descriptions to the normalization block.

**P3-3 · `gates.py:130,133` — the new `None` branches have no unit-test coverage.**
The `sharpness_score is not None` / `exposure_score is not None` guards added by `bc3a499` are exercised
only by `tests/integration/test_corpus_footage.py:120`
(`test_single_segment_yields_null_rank_but_real_raw_measurement`), which is `@pytest.mark.integration`
and requires `data/raw/` footage. `tests/highlight_extraction/test_gates.py` contains no occurrence of
`None` (grepped in-session). The always-runnable 93-test unit suite does not cover the branch.
*Fix:* two unit tests calling `evaluate_gates(..., sharpness_score=None, exposure_score=None)` with a
nonzero floor, asserting no failure is appended.

**P3-4 · `tests/integration/` covers only 720p corpus material.** All five integration tests parametrise
over `SPLIT_FAMILY`/`VERTICAL_FAMILY` (`test_corpus_footage.py:46,63`). Nothing covers the working-footage
class (hevc / 3840×2160 / 59.94 / 10-bit / HLG), which is where every finding in `WORKING_FOOTAGE.md`
lives. A decode-based test there would time out (§1), so the honest addition is a **metadata-only**
conformance test asserting the `corpus_wide_invariants` deltas the pack already measured — cheap,
`ffprobe`-only, and it would fail loudly the day someone assumes corpus properties hold.

### Deliberately not raised

- `motion.py:166` assigns `accel` (centred at index i+1) to `jerk[2:]`, a one-frame lag. At 59.94 fps
  that is 16.7 ms against a mean over a ≥2 s segment. Real, immaterial, not worth a reviewer's time.
- `letterbox.py:99` places `-t` before `-i`. That is a correct and *more* efficient input-side duration
  limit, not a bug.
- `scoring_composition.py:190` constructs a new saliency object per frame. Measured at 0.48 ms/frame per
  the module's own docstring benchmark; construction is not the cost.

---

## 9. Open questions requiring measurement before implementation

Numbers this design needs and does **not** have. None of them are guessed at above.

1. **End-to-end wall clock for one 4K clip through the unmodified pipeline.** My component-derived
   projection (~71× video duration, §1.3) and the pack's 3.7–8.1× (`WORKING_FOOTAGE.md:162`) disagree by
   ~10×. One detached run on the shortest working clip settles it. **Nothing should be scheduled until
   this exists.**
2. **Laplacian variance and rank stability at ÷3 (3840×2160 → 1280×720) on real working footage.** I
   measured ÷2, ÷4 and ×0.75 on 720p corpus material only. The recommended proxy scale is the one scale
   I did not test.
3. **Proxy decode throughput** at 1280×720 h264 8-bit on this machine. The 0.4–1.2× realtime figure is
   the pack's, for 720p/1080p generally, not for these proxies.
4. **A working VideoToolbox decode-and-scale filter chain, byte-verified.** Two candidates produced zero
   bytes at exit 0 today (§2.5). Without one, Stage A must download full 4K frames to the CPU and the
   3.3 h estimate is optimistic.
5. **Parallel scaling curve for Stage B** at 1 / 2 / 4 / 8 workers. The worker count in §4.2 is a
   starting point, not a measurement.
6. **Horizon-levelness behaviour at 3840×2160.** P1-4 measured downscales only; the direction at 4K is
   uncertain.
7. **`scdet` on the working footage.** The zero-hard-cuts finding is a corpus property and is explicitly
   *not* established here (`WORKING_FOOTAGE.md:190-192`). P1-6's severity depends on it: if working clips
   are multi-shot, the single-segment degenerate case may be rare there.
8. **Telemetry-derived motion versus optical-flow motion, on the same clips.** Required before §4.4's
   substitution can be trusted, and the pack already flags the classifier's thresholds as unvalidated
   (`WORKING_FOOTAGE.md:91-93`).

---

## 10. Verdict

The two commits under review are **directionally right and carefully reasoned**, and the letterbox fix
in particular is exactly the kind of measurement-grounded change this repo's Constitution asks for — it
cites a measured delta (0.2444) that matches a measured cause (24.4% content cost) to four decimal
places. `bc3a499`'s refusal to fabricate a 1.0 is likewise correct in principle.

Both, however, were designed against the 8-file 720p corpus, and **six of the eleven issues above are
instances of one root cause: constants and comparability claims that are silently resolution- or
frame-rate-denominated.** The proxy architecture does not create that problem — it makes an existing
one unavoidable, because it forces the question "what resolution was this measured at?" onto every
value in the manifest. That question currently has no answer recorded anywhere in the output.

The highest-value single change is not in this design at all: it is §4.4, using the 150 telemetry
sidecars the pack found, which replaces the most expensive stage of the pipeline with a free one and
grounds it in metres per second instead of pixels per frame.
