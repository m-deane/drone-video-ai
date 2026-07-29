# Working footage — measured characterisation

**Subject:** `00-WORKING/Videos/` — 153 clips, 111.4 minutes, July 2026 Pamir shoot.
**Measured:** 2026-07-29, `ffprobe` 8.1.2 + Python 3 stdlib. Same toolchain and discipline as the
rest of this pack.
**Status:** container/timing/colour facts measured on all 153. Per-frame luma/chroma and
scene-change measurement NOT yet run (see "Not yet measured").

> **Why this file exists.** Everything in `data/reference_pack/` characterises the 8-file
> `00-assets/drone-video-examples/` corpus, and every threshold in `src/drone_video_ai/` is
> calibrated against it. This footage is what the project is actually for, and **it does not
> resemble that corpus.** Three of the four `corpus_wide_invariants` fail here.

---

## 1. The pack's invariants, tested against this footage

`editorial_style.json` → `corpus_wide_invariants` describes itself as "the only style values a
generator can take as given". Tested on all 153 clips:

| Invariant | Pack value (measured on corpus) | This footage | Holds? |
|---|---|---|---|
| `codec` | `h264` | `hevc` ×150, `h264` ×3 | **NO** |
| `frame_rate` | `30/1` | `60000/1001` ×150, `25/1` ×3 | **NO** |
| `pix_fmt` (bit depth) | `yuv420p` (8-bit) | `yuv420p10le` (**10-bit**) ×150, `yuv420p` ×3 | **NO** |
| `color_range` | `tv` | `tv` ×153 | yes |
| `audio_streams` | `0` | `0` ×153 | yes |

**Three of five fail.** The two that hold are the two that were never load-bearing.

## 2. What this footage actually is

| Property | Value |
|---|---|
| Resolution | 3840×2160 on all 153 |
| Transfer / primaries | `arib-std-b67` + `bt2020` ×118 (**HLG, HDR**); `bt709` ×35 (SDR) |
| Camera colour mode (from telemetry) | `hlg` ×117, `dlog_m` ×32 |
| Bit rate | 125 Mbps median, 376 Mbps max |
| Duration | 0.1 s min, 35.7 s median, 161.2 s max; **111.4 min total** |
| Audio | none, on all 153 |

**77% of this footage is 10-bit HDR (HLG/bt2020).** The pipeline has never processed 10-bit or HDR
material — the corpus is uniformly 8-bit bt709 SDR.

That is not cosmetic. `scoring_exposure.py` defines `LOW_CLIP_THRESHOLD = 5` and
`HIGH_CLIP_THRESHOLD = 250` on an implied 0–255 8-bit SDR scale. Against a 10-bit HLG source those
numbers describe a different part of the signal than intended, and the audit already established
the low threshold is unreachable even on the SDR corpus (measured YMIN ≥ 14). **Do not assume the
exposure scorer means anything on this footage until it is re-checked.**

## 3. Telemetry — a measured source for camera motion

150 `.SRT` sidecars accompany the 153 clips (98% coverage). Schema is **identical in all 150**:

```
[iso] [shutter] [fnum] [ev] [color_md] [focal_len] [latitude] [longitude] [rel_alt abs_alt] [ct]
```

Per-frame, at 59.94 Hz. **No gimbal angles** in this DJI variant, so yaw/pitch/roll are not
directly available — but position and altitude are.

149 clips carry enough GPS to derive flight dynamics (1 too short):

| Derived quantity | min | median | max |
|---|---:|---:|---:|
| Ground speed | 0.00 | **12.96** | 20.61 m/s |
| Vertical speed | −6.09 | +0.00 | +7.30 m/s |
| Altitude range within a clip | — | 54.9 | 441.7 m |
| Absolute altitude | 2235 | 3916 | 5067 m |

### Why this matters more than any other finding here

`editorial_style.json` → `toolchain.unavailable` records that this project has **"no optical-flow
capability"** and the README lists camera-motion direction and rotation under "Not verifiable with
this toolchain". That limitation is why the corpus `manifest.json`'s `REVEAL` / `ORBIT_CW` /
`STATIC` labels have stood unverified since the pack was built.

GPS position over time answers that question directly, without optical flow. Classified from
telemetry alone, sampling at 0.5 s to suppress GPS quantisation:

| Class | Clips | Share |
|---|---:|---:|
| TRANSLATE | 82 | 55% |
| ASCEND/DESCEND | 58 | 39% |
| STATIC/HOVER | 8 | 5% |
| ORBIT | 1 | 1% |

**The ORBIT rate is the interesting number, and it cuts against expectation.** The corpus
`manifest.json` labels 1 of its 4 clips `ORBIT_CW` — 25%. Here it is 1 in 149. Either orbits are far
rarer in real shooting than the archived material implies, or this classifier's thresholds
(>2.0°/s sustained turn, >0.7 directional consistency) are too strict. **Both readings are live; the
thresholds below are stated so they can be challenged, not because they are validated.** Nothing
here has been cross-checked against visual review of the clips.

## 3a. What OpenCV actually hands the scorers (measured 2026-07-29)

`cv2.VideoCapture` decodes these 10-bit sources to **`uint8`** — no 10-bit precision reaches any
scorer. That much is expected. What matters is *how* the transfer curve survives:

| Sample | cv2 luma min | max | mean | `_clipped_fraction` |
|---|---:|---:|---:|---:|
| HLG (`arib-std-b67`/bt2020) | 0–2 | **255** | ~88 | 0.0011 – 0.0018 |
| SDR (`bt709`) | 5–8 | 202–233 | 77–99 | **0.000000** |

The HLG samples reach 255 and register clipping; the SDR samples never approach
`HIGH_CLIP_THRESHOLD = 250` at all. This is consistent with HLG being decoded as though it were
bt709 — HLG's highlight roll-off encodes a much wider range, and reading it flat pushes highlights
to white.

### The bias hypothesis, tested at scale — and largely REFUTED

The three-frame samples above suggested `exposure` might be systematically biased against HLG.
Tested across 28 clips (14 HLG, 14 SDR), two frames each:

| | clips with ANY clipping | median | mean | max |
|---|---:|---:|---:|---:|
| HLG | **8 / 14** | 0.000000 | 0.000533 | 0.006681 |
| SDR | **1 / 14** | 0.000000 | 0.000000 | 0.000000 |

**The direction is real; the magnitude is negligible.** HLG clips do clip more often — 8 of 14
versus 1 of 14 — but the worst clipped fraction seen anywhere is 0.0067, i.e. an exposure score of
0.9933, which at the 0.25 composite weight moves a composite score by **0.00167**. That is not a
systematic bias worth acting on. The initial three-frame sample happened to catch clipping frames
and overstated the effect; the median HLG clip clips exactly as much as the median SDR clip, which
is to say not at all.

### The finding that replaces it, and it is worse

**`exposure` returns exactly 1.0 on 19 of 28 clips (68%), and is within 0.7% of 1.0 on all 28.**

A signal carrying **25% of the composite weight** discriminates essentially nothing on this
footage. This is not new behaviour — the audit recorded the same pattern on the 8-file corpus
("exposure is a near-constant signal holding 25% of the composite weight") — but it now generalises
to the real library, for a different reason. On the corpus the *low* threshold was unreachable
(measured YMIN ≥ 14). Here both tails are effectively unreachable: aerial footage at altitude,
correctly exposed, simply does not put pixels at ≤5 or ≥250.

So the actionable defect is not the HLG transfer curve. It is that `LOW_CLIP_THRESHOLD = 5` /
`HIGH_CLIP_THRESHOLD = 250` measure *sensor clipping*, an failure mode this footage does not
exhibit, while contributing a quarter of every score. A discriminating exposure signal would need
to measure something else entirely — histogram spread, mid-tone placement, or dynamic-range usage.

A residual caveat, unresolved: the clean control (decode with a proper HLG→bt709 tonemap and
re-measure) still could not be run — this ffmpeg build has no `zscale` filter, so the
`zscale,tonemap,zscale` chain fails with "No such filter". That control would settle whether the
small HLG excess is a decode artifact or real. Given the measured magnitude, it is no longer
urgent.

## 3b. Letterbox — absent here

Measured from decoded mid-clip frames on both an HLG and an SDR sample: zero rows above or below
the picture fall under the luma-24 limit the pack's `cropdetect` recipe uses. Row means span
59.3–175.9 (HLG) and 46.6–163.3 (SDR). **This footage is not letterboxed; the full 3840×2160 frame
is picture.**

So `letterbox.py`'s crop correctly degrades to a whole-frame no-op here. The fix matters for the
corpus's split family and is harmless on this material — which is the intended behaviour, and is
already guarded by the `test_vertical_family_is_not_letterboxed` integration test.

## 3c. Which signals actually discriminate on this footage (2026-07-29)

Measured on 15 720p 3-second proxy segments sampled across the library, 3 frames each. The question
is not whether a signal is principled but whether it **separates clips at all** — a signal returning
the same value everywhere carries no information however sound its derivation.

**The signal that reaches the composite today:**

| | min | max | span | exactly 1.0 |
|---|---:|---:|---:|---:|
| `exposure` (= 1 − clipped_fraction) | 0.9824 | 1.0000 | **0.0176** | 5 / 15 |

**`exposure` occupies 1.8% of the [0,1] scale it is weighted 25% on.**

**Candidates, by raw spread (p90/p10):**

| Candidate | ratio |
|---|---:|
| `sharpness_laplacian` (current) | **10.48×** |
| `edge_density` (Canny fraction) | 8.66× |
| `tenengrad` (Sobel energy) | 8.33× |
| `saturation_mean` (HSV S) | **4.78×** |
| `contrast_std` (luma σ) | 1.83× |
| `midtone_p50` | 1.76× |
| `dynamic_range_p1_p99` | 1.60× |

**Three of the four highest-spread candidates are the same signal wearing different hats.** Spearman
rank correlation across the 15 clips:

```
sharpness_laplacian ~ tenengrad      rho = +0.94
sharpness_laplacian ~ edge_density   rho = +0.93
tenengrad           ~ edge_density   rho = +0.94
```

Adding `tenengrad` or `edge_density` alongside `sharpness` would add weight, not information. No
other pair exceeded |rho| = 0.8, so `saturation_mean`, `contrast_std`, `midtone_p50` and
`dynamic_range_p1_p99` are mutually independent and independent of sharpness.

**What that suggests** — as a starting point for a spec, not a decision:

- Keep **one** detail signal. `sharpness_laplacian` already has the widest spread; its rivals are
  redundant with it.
- **`saturation_mean`** is the strongest genuinely independent addition: 4.78× spread, uncorrelated
  with detail.
- One tonal signal from `contrast_std` / `midtone_p50` / `dynamic_range_p1_p99`. All three are
  modest (1.6–1.8×) and mutually independent; nothing here says which.
- **Retire clipping-based exposure.** It measures sensor clipping, which this footage does not
  exhibit.
- **Telemetry** (§3) is the one signal with both large spread and a physical meaning: ground speed
  spans 0.00–20.61 m/s across 149 clips, and it measures the thing optical flow was reaching for.

### Caveats on this measurement, stated so it is not over-read

- **n = 15**, not the 24 intended: 9 proxy encodes failed silently and were not retried. The sample
  skews HLG (the queue was 18 HLG / 6 SDR before failures).
- **3 frames per clip** from one 3-second mid-clip window. This measures between-clip separation,
  and says nothing about within-clip variation, which is what segment scoring actually needs.
- **`sharpness_laplacian` is not scale-invariant.** These ratios come from 720p proxies; absolute
  values will differ at 4K, so the spread is comparable but the numbers are not transferable.
- Two discrimination metrics were tried and discarded first — IQR/median, then p90/p10 — because
  both divide by a near-zero quantity and reported the *most* inert signal as the most
  discriminating. Zero-inflated signals need the score-span framing used above, not a ratio.

## 4. Cost

Measured pipeline throughput: **0.4–1.2× realtime at 720p/1080p, 3.7–8.1× at 4K.** At 111.4 minutes
of 4K, a single full pass is **6.9–15.0 hours**, and there is no batch mode — the CLI takes one file.
Plan for downscaled analysis and parallelism before attempting a real run.

**4K hevc decode is the binding constraint, and it blocks measurement itself, not just the
pipeline.** Established the hard way on 2026-07-29: `ffmpeg signalstats` over 3 s of one clip, and
`cropdetect` over 2 s of one clip, both exceeded a 2-minute wall clock. These are the pack's own
standard recipes — the ones every existing measurement in `data/reference_pack/` was produced with.
They do not complete on this material at native resolution.

Practical consequences, all learned by hitting them:

- **Never run two 4K decode jobs concurrently.** They contend for the same cores and both slow to a
  crawl; one job at a time finishes sooner than two in parallel.
- **Decode a frame and measure it in NumPy** where an ffmpeg filter would otherwise walk the whole
  stream. The letterbox check in §3b took milliseconds this way after `cropdetect` had timed out
  entirely on the same question.
- **Any real characterisation of this footage needs downscaled proxies**, and the proxy step is
  itself a 4K decode, so it must be batched and run detached.

This is the single largest practical obstacle between the current pipeline and this footage.

## 5. Not yet measured

Deliberately absent rather than estimated:

- **Per-frame luma/chroma** (`signalstats`) — the pack's whole colour-treatment section has no
  counterpart here. Needed before any exposure or grade claim about this footage.
- **Scene-change scores** (`scdet`) — so **the zero-hard-cuts finding is NOT established for this
  footage.** It is a property of the 8-file corpus and its archive expansion, both of which were
  single-shot derivative clips. These are camera originals; assume nothing.
- **Letterbox geometry** (`cropdetect`) — untested here.
- Any cross-check of the telemetry classification against what the footage visually shows.

## 6. Reproduction

```bash
# Container / timing / colour facts (this file's sections 1-2)
ffprobe -v error -print_format json -show_format -show_streams "$CLIP"

# Telemetry schema check across all sidecars
grep -m1 -o '\[[a-z_]*:' "$SRT" | tr -d '[:' | paste -sd, -

# Telemetry parse: [latitude: X] [longitude: Y] [rel_alt: Z abs_alt: W] per frame,
# haversine between 0.5s-spaced samples for ground speed, bearing delta for turn rate.
```
