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

## 4. Cost

Measured pipeline throughput: **0.4–1.2× realtime at 720p/1080p, 3.7–8.1× at 4K.** At 111.4 minutes
of 4K, a single full pass is **6.9–15.0 hours**, and there is no batch mode — the CLI takes one file.
Plan for downscaled analysis and parallelism before attempting a real run.

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
