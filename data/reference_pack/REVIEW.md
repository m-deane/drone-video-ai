# Reference Pack — Measurement Review

Adversarial technical review of the 8 media files in
`/Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples/`, their
sidecar `manifest.json`, and the located source proxy.

Everything below is either (a) a fact read out of a stored `ffprobe` JSON in
`data/reference_pack/probe/`, (b) a fact produced by a named `ffmpeg`/`ffprobe` command that
is quoted inline, or (c) explicitly marked **UNVERIFIABLE IN-SESSION**. No number in this
document was inferred, rounded to taste, or carried over from documentation without
measurement.

Source media is read-only. No file in `00-assets/` or `_archive/` was modified, moved or
re-encoded; all mtimes are unchanged.

---

## 0. Measurement basis — the commands behind every number

| # | Command | Produces |
|---|---------|----------|
| P1 | `ffprobe -v error -print_format json -show_format -show_streams FILE` | container, duration, resolution, fps, codec/profile/level, bitrate, pix_fmt, colour tags, stream count. Stored per file as `probe/<name>.json`. |
| P2 | `ffprobe -v error -f lavfi -i "movie=FILE,scdet=threshold=0" -show_entries "frame=pts_time:frame_tags=lavfi.scd.score" -of csv=p=0` | per-frame scene-change score on scdet's 0–100 scale. Stored as `probe/<name>.scd.csv`. **Note the COLON** between section specifiers — see §6. |
| P3 | `ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames FILE` | independent frame count, not read from the container header. |
| P4 | `ffprobe -v error -select_streams a -show_entries stream=index FILE` | audio stream presence (empty output = none). |
| C1 | `ffmpeg -nostats -loglevel info -i FILE -vf cropdetect=limit=24:round=2:reset=0 -f null -` | active-picture rectangle per frame (letterbox geometry). |
| S1 | `ffmpeg -nostats -i FILE -vf <crop>,signalstats -show_entries frame_tags=lavfi.signalstats.YAVG,... -f null -` | per-frame YMIN/YAVG/YMAX/UAVG/VAVG/SATAVG/HUEAVG. |
| S2 | `ffmpeg -i A -i B -lavfi "[0:v]scale=W:H[a];[a][1:v]ssim" -f null -` and the same with `psnr` | frame-for-frame similarity between two files. |
| M1 | `ffmpeg -i FILE -vf mpdecimate -f null -` | duplicate-frame count (slow-motion / frame-duplication detector). |
| X1 | `ffmpeg -i FILE -vf "select='gt(scene,0.3)',showinfo" -f null -` | independent hard-cut cross-check. **`showinfo`, not `metadata=print`** — see §6. |

Tool versions: `ffprobe -version` → **ffprobe version 8.1**; `ffmpeg` from the same build,
both at `/opt/homebrew/bin`.

---

## 1. Per-file measurements

### Facts common to all 8 files

Read from every `probe/*.json` (command **P1**):

- **Container**: `mov,mp4,m4a,3gp,3g2,mj2` — QuickTime/MOV. `major_brand=isom`,
  `minor_version=512`, `compatible_brands=isomiso2avc1mp41`. Muxer tag **`Lavf61.7.100`** on
  all eight — one FFmpeg build wrote every container in this set.
- **Stream count**: `format.nb_streams = 1`, and the sole stream is `codec_type=video`.
  **P4** returns empty for all eight. **There is no audio anywhere in this pack.**
- **Frame rate**: `r_frame_rate == avg_frame_rate == 30/1` on all eight, `time_base 1/15360`,
  `start_time 0.000000`, `start_pts 0`. **All eight are CFR 30 fps**, and in every case
  `format.duration == nb_frames / 30` exactly.
- **Pixel format**: `yuv420p`, `bits_per_raw_sample=8`, `chroma_location=left`,
  `field_order=progressive`. All eight are 8-bit 4:2:0 progressive.
- **Rotation**: no `side_data_list` key is present in any of the eight probe JSONs, so no
  display-matrix side data exists. **Rotation is 0 on every file.** The 9:16 files are
  natively tall-coded — they are not rotated 16:9 rasters.
- **Coded vs displayed aspect**: `coded_width == width` and `coded_height == height` on all
  eight, and both `sample_aspect_ratio` and `display_aspect_ratio` are **absent** from every
  stream. Pixels are therefore square by default and displayed aspect equals coded aspect.
  Caveat recorded honestly: absent SAR is an *unset tag*, and a downstream tool assuming 1:1
  is making the standard assumption, not reading a measurement.
- **Probe confidence**: `probe_score = 100` on all eight.

A reproducibility nit worth recording: the four `split_*.json` probes store `format.filename`
as a bare basename (`split_001_s70.mp4`) while the four vertical probes store the absolute
path. The probes are still valid — file identity was separately pinned by sha256 — but the
split JSONs alone do not tell a reader which directory they came from.

---

### 1.1 `instagram_reel_test.mp4`

| Property | Measured value (P1) |
|---|---|
| Container | QuickTime/MOV, `isom`, muxer `Lavf61.7.100` |
| Size | 47,761,652 bytes |
| Duration | `format.duration` 27.100000 s; `duration_ts` 416256 / `time_base` 15360 = 27.1 exactly |
| Frames | `nb_frames` 813; 813 / 30 = 27.100000 |
| Resolution | 1080 × 1920 (coded 1080 × 1920), portrait 9:16 |
| Frame rate | 30/1 CFR (`r_frame_rate == avg_frame_rate`) |
| Codec | h264, profile **High**, level **4.1**, `has_b_frames` 2 |
| Encoder | `Lavc61.19.100 libx264` |
| Bitrate | format 14,099,380 bps; stream 14,096,352 bps |
| pix_fmt | yuv420p, 8-bit |
| Colour | `color_range`, `color_space`, `color_transfer`, `color_primaries` — **all absent** |
| Rotation | none (no side data) |
| Audio | none (`nb_streams` 1) |
| Aspect | coded = displayed = 9:16; no SAR/DAR tags |
| Scene scores (P2, 813 rows) | max **1.547**, median 0.0350; frames ≥ 5.0: **0**; frames ≥ 10.0: **0** |

**Interpretation.** A finished 1080×1920 short-form upload master. It contains **one shot**:
across all 813 scored frames nothing comes within a factor of 20 of a hard cut (calibration
in §3). It carries **no colour tagging at all**, so any BT.709 reading of its pixels is a
downstream default, not a declaration. It is frame-locked to
`instagram_reel_v34_all_kb_full.mp4` (§2) and differs from it only in resolution and grade.
It ends on a 13-frame fade-to-black beginning at t = 26.633 s (S1: YAVG 106.5 → 34.7, ≈5.5
luma/frame) — a **truncated** fade, since the last frame is not black (YAVG 34.71).

### 1.2 `instagram_reel_v34_all_kb_full.mp4`

| Property | Measured value (P1) |
|---|---|
| Container | QuickTime/MOV, `isom`, muxer `Lavf61.7.100` |
| Size | 249,919,142 bytes |
| Duration | 27.100000 s; `duration_ts` 416256 / 15360 = 27.1 |
| Frames | 813; 813 / 30 = 27.100000 |
| Resolution | 2160 × 3840 (coded identical), portrait 9:16 |
| Frame rate | 30/1 CFR |
| Codec | h264, profile **High**, level **5.1**, `has_b_frames` 2 |
| Encoder | `Lavc61.19.100 libx264` |
| Bitrate | format 73,776,868 bps; stream 73,773,819 bps |
| pix_fmt | yuv420p, 8-bit |
| Colour | all four colour keys **absent** |
| Rotation | none |
| Audio | none |
| Scene scores (P2, 813 rows) | max **3.537**, median 0.0900; ≥5.0: **0**; ≥10.0: **0** |

**Interpretation.** The high-resolution sibling of §1.1 — exactly 2× linear resolution, the
same 813 frames, the same 27.100000 s. "4K" here means **3840 on the long (vertical) edge**;
the frame is only 2160 px wide. At ~74 Mbps this is a mastering/archival rendition, not an
upload target. It is the **brighter** grade of the pair (S1: frame-0 YAVG 137.6 vs 128.9;
whole-file YAVG mean 121.83 vs 117.34; YAVG max 146.98 vs 132.00). Its mtime is
**2026-02-04 14:32**, earlier than `instagram_reel_test.mp4` at **2026-02-08 17:42** — so
despite the `_v34` label this is the *earlier* render; naming and chronology point in
opposite directions. It also carries the set's single unexplained structural feature: a
**19-frame run** starting t = 0.77 s where frame difference exceeds 5× the file's own median
— the only dissolve-shaped signature anywhere in the pack (unresolved, §5 group B).

### 1.3 `viral_test_v2.mp4`

| Property | Measured value (P1) |
|---|---|
| Container | QuickTime/MOV, `isom`, muxer `Lavf61.7.100` |
| Size | 24,470,570 bytes |
| Duration | 14.566667 s; `duration_ts` 223744 / 15360 = 14.566667 |
| Frames | 437; 437 / 30 = 14.566667 |
| Resolution | 1080 × 1920, portrait 9:16 |
| Frame rate | 30/1 CFR |
| Codec | h264, profile **High**, level **4.1**, `has_b_frames` 2 |
| Encoder | `Lavc61.19.100 libx264` |
| Bitrate | format 13,439,214 bps; stream 13,435,909 bps |
| pix_fmt | yuv420p, 8-bit |
| Colour | all four colour keys **absent** |
| Rotation | none |
| Audio | none |
| Scene scores (P2, 437 rows) | max **1.799**, median 0.1180; ≥5.0: **0**; ≥10.0: **0** |

**Interpretation.** A second finished vertical upload master, one shot, no cuts. Its median
frame difference (0.1180) is the second-highest in the set — busier material than the splits.
*(A clause here formerly read "consistent with the front-loaded motion envelope described in
§3" — removed 2026-07-27: that envelope claim was killed 3/3 (C56, §3.7), and this file is
its counterexample — its per-second maximum falls at t = 14.100 s, the **last** second.)*
**M1** drops 2 of 437
frames as near-duplicates, the only non-zero duplicate count in the set and far too few to
indicate frame-duplicated slow motion. Terminal 14-frame fade-to-black from t = 14.067 s
(S1: YAVG 113.4 → 23.7, ≈6.4 luma/frame), also truncated — last frame YAVG 23.68.

### 1.4 `viral_test_v2_4k.mp4`

| Property | Measured value (P1) |
|---|---|
| Container | QuickTime/MOV, `isom`, muxer `Lavf61.7.100` |
| Size | 138,192,119 bytes |
| Duration | 14.566667 s; `duration_ts` 223744 / 15360 |
| Frames | 437 |
| Resolution | 2160 × 3840, portrait 9:16 |
| Frame rate | 30/1 CFR |
| Codec | h264, profile **High**, level **5.1**, `has_b_frames` 2 |
| Encoder | `Lavc61.19.100 libx264` |
| Bitrate | format 75,894,983 bps; stream 75,890,986 bps |
| pix_fmt | yuv420p, 8-bit |
| Colour | all four colour keys **absent** |
| Rotation | none |
| Audio | none |
| Scene scores (P2, 437 rows) | max **1.776**, median 0.1420; ≥5.0: **0**; ≥10.0: **0** |

**Interpretation.** Frame-locked high-resolution sibling of §1.3: identical frame count,
identical duration, exactly 2× linear resolution. **It is not a bicubic upscale of the
delivered 1080p** — mean Laplacian high-frequency energy over the first 180 frames measures
**3.2365** for this file versus **1.8853** for `viral_test_v2.mp4` bicubic-upscaled to
2160×3840, i.e. 1.72× more real detail than upscaling can manufacture.
> **Session re-measurement note (outside the claim set — never adversarially tested, §7.2
> finding 2).** The 1.72× ratio did not reproduce: a 61-frame re-measurement this session
> gives **3.2991 vs 2.0993 = 1.57×**. Direction holds, magnitude is unsettled; read it as a
> 1.57–1.72× range. *(This note formerly carried a "C57 killed" header by mistake — C57's
> verdict concerns only the PSNR figures below, not the Laplacian ratio.)*

> **CORRECTED 2026-07-27 — C57 killed 3/3.** PSNR is near-symmetric between the two
> directions — **34.640697 dB** (4K→1080, bicubic) and **34.404432 dB** (1080→4K, bicubic), a
> gap of **0.24 dB**. (The figure formerly printed here, 31.80 dB, is not reproducible in
> either direction under any of five scalers swept.) Neither file is a plain resample of the
> other; both read as independent exports of one composition.

### 1.5 `split_001_s70.mp4`

| Property | Measured value (P1) |
|---|---|
| Container | QuickTime/MOV, `isom`, muxer `Lavf61.7.100` |
| Size | 28,153,847 bytes |
| Duration | 15.000000 s; `duration_ts` 230400 / 15360 = 15.0 exactly |
| Frames | 450; 450 / 30 = 15.000000 |
| Resolution | 1280 × 720 (coded identical), landscape 16:9 |
| Frame rate | 30/1 CFR |
| Codec | h264, profile **High**, level **3.1**, `has_b_frames` **0** |
| Encoder | `Lavc61.19.100 **h264_videotoolbox**` |
| Bitrate | format 15,015,385 bps; stream 15,013,683 bps |
| pix_fmt | yuv420p, 8-bit |
| Colour | `color_space` **bt709**, `color_range` **tv**; `color_primaries` and `color_transfer` **absent** |
| Rotation | none |
| Audio | none |
| Active picture (C1) | `crop=1280:544:0:88` on **448 of 450 frames** — 88 px bars top and bottom, active 1280×544 = **2.352941:1** |
| Scene scores (P2, 450 rows) | max 2.668 — but that is the **scdet frame-1 warm-up artefact at t = 0.033333 s** (prev_mafd still 0). True content max **0.537**; median 0.0265; ≥5.0: **0**; ≥10.0: **0** |

**Interpretation.** A 2.35:1 letterboxed segment cut from `DJI_0355_proxy.mp4` at source
frames 1200–1649 (§2). Hardware-encoded (`h264_videotoolbox`) with zero B-frames, unlike the
libx264 verticals — a different encoder path entirely. Highest per-pixel bitrate in the pack:
15 Mbps at 720p, **28.6 % above** the 11,678,856 bps source it was cut from, which cannot
recover information and only enlarges the file. This is the clip that **discriminates the
letterbox mechanism**: correlated against the proxy's centre-crop at its declared offset,
r = **+0.95975**; against the proxy's *full frame*, r collapses to **+0.30494**. The 2.35
framing was made by **vertical centre crop, not anamorphic squeeze**.

### 1.6 `split_002_s69.mp4`

| Property | Measured value (P1) |
|---|---|
| Size | 28,140,059 bytes |
| Duration | 15.000000 s; `duration_ts` 230400 / 15360 |
| Frames | 450 |
| Resolution | 1280 × 720, 16:9 |
| Frame rate | 30/1 CFR |
| Codec | h264, High, level 3.1, `has_b_frames` 0, `h264_videotoolbox` |
| Bitrate | format 15,008,031 bps; stream 15,006,342 bps |
| Colour | `bt709` / `tv`; primaries and transfer absent |
| Active picture (C1) | `crop=1280:544:0:88` |
| Scene scores (P2, 450 rows) | max 2.435 (frame-1 warm-up); true content max **0.475**; median 0.0320; ≥5.0: **0** |

**Interpretation.** Source frames 750–1199 (25.000–40.000 s). This is the **strongest
provenance match in the set**: SSIM offset sweep gives 0.3515 at frame 749, **0.4777 at 750**,
0.3493 at 751 — a sharp single peak exactly on the manifest's declared `start_time`, and
correlation r = **+0.99948**. Frame-exact.

### 1.7 `split_003_s66.mp4`

| Property | Measured value (P1) |
|---|---|
| Size | 15,590,791 bytes |
| Duration | **8.300000 s**; `duration_ts` **127488** / 15360 = 8.3 **exactly** |
| Frames | **249** (`nb_frames` 249, and **P3** `-count_frames` independently returns 249); 249 / 30 = 8.300000 |
| Resolution | 1280 × 720, 16:9 |
| Frame rate | 30/1 CFR |
| Codec | h264, High, level 3.1, `has_b_frames` 0, `h264_videotoolbox` |
| Bitrate | format 15,027,268 bps; stream 15,025,257 bps |
| Colour | `bt709` / `tv`; primaries and transfer absent |
| Active picture (C1) | `crop=1280:544:0:88` (247 detections) |
| Scene scores (P2, 249 rows) | max 2.104 (frame-1 warm-up); true content max **0.174** — the quietest content in the pack; median 0.0170; ≥5.0: **0** |

**Interpretation.** The single most instructive file in the pack, because it is the one where
the manifest is **measurably wrong**. It covers source frames 500–748, i.e. it ends at
24.966667 s, **one frame short** of the declared 25.0. The duration is not a rounding of
8.33 — `duration_ts` 127488/15360 is 8.3 exactly and the frame count is 249, where 8.33 s
would be 249.9 frames. Full mechanism in §4.

### 1.8 `split_004_s65.mp4`

| Property | Measured value (P1) |
|---|---|
| Size | 28,143,093 bytes |
| Duration | 15.000000 s; `duration_ts` 230400 / 15360 |
| Frames | 450 |
| Resolution | 1280 × 720, 16:9 |
| Frame rate | 30/1 CFR |
| Codec | h264, High, level 3.1, `has_b_frames` 0, `h264_videotoolbox` |
| Bitrate | format 15,009,649 bps; stream 15,007,948 bps |
| Colour | `bt709` / `tv`; primaries and transfer absent |
| Active picture (C1) | `crop=1280:544:0:88` |
| Scene scores (P2, 450 rows) | max **0.516** — lowest maximum in the set, and low enough that even the frame-1 warm-up does not dominate; true content max 0.415; median 0.0150; ≥5.0: **0** |

**Interpretation.** Source frames 0–449 — the head of the proxy, at offset exactly 0. Mean
SSIM against the source at that offset is **0.9707** (n = 450, min 0.9587, max 0.9757), the
best of the four. Its own quintile SSIM means (0.9708 / 0.9734 / 0.9734 / 0.9705 / 0.9652)
are flat, which is the decisive evidence against any speed ramp (§4). It is also the clip
labelled `motion_type: STATIC` in the manifest while measuring mean mafd 1.9114 — 58.8 % of
the highest-motion clip. That tension is flagged, not resolved (§4, §5 group A).

---

## 2. Topology — masters, derivatives, renditions

Three tiers, plus one absent tier at the top.

```
DJI_20241029174803_0355_D.MP4          CAMERA ORIGINAL — identified 2026-07-27 by pixel
  3840x2160 HEVC Main10 HLG/BT.2020,   measurement, this session (§2.1a). Formerly shown
  59.94 fps, 63.580183 s, muxer tag    here as "ABSENT — not on this machine".
  "DJI Mavic3Pro", located at the same
  _archive/.../.advanced/ directory
            |
            v
  DJI_0355_proxy.mp4                   MASTER (for the split family)
  1280x720 10-bit HLG/BT.2020, 63.633333 s, 1909 frames, 11,678,856 bps
  located at _archive/_p-ai-drone-video/.drone_clips/.advanced/
            |
     +------+------+------+------+
     v             v      v      v
 split_004     split_003  split_002  split_001     DERIVATIVES (measured, frame-exact)
 f0-449        f500-748   f750-1199  f1200-1649

[ absent vertical parent timeline A ]  ABSENT
            |
     +------+------+
     v             v
 instagram_reel_test.mp4    instagram_reel_v34_all_kb_full.mp4    RENDITIONS (frame-locked)
 1080x1920                  2160x3840

[ absent vertical parent timeline B ]  ABSENT
            |
     +------+------+
     v             v
 viral_test_v2.mp4          viral_test_v2_4k.mp4                  RENDITIONS (frame-locked)
 1080x1920                  2160x3840
```

### 2.1 The master — `DJI_0355_proxy.mp4`, and its stale recorded path

`manifest.json` records `source_file.path` as:

```
/Users/matthewdeane/Documents/Data Science/python/_projects/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4
```

`ls` on that path returns *No such file or directory* — **`/Users/matthewdeane` does not
exist on this machine at all**. The file was located by name search at:

```
/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4
92,905,225 bytes, mtime 2026-03-15 17:00
```

The relative subpath below the project root is **identical**; only the home/root prefix
differs. So provenance is recoverable, but the recorded path breaks reproducibility exactly
as written.

This matters more than a broken-link nit: **locating this file is what turned five manifest
claims from UNVERIFIABLE into measured findings** — `start_time`, the letterbox mechanism,
`auto_speed`, `color`, and the scene-boundary narrative. An earlier pass in this run had all
five recorded as unverifiable for want of the source (§5, superseded group).

Probe of the proxy (**P1**): 1280×720, 30/1 CFR, `nb_frames` 1909, duration 63.633333 s,
11,678,856 bps, h264 **profile High 10**, `pix_fmt` **yuv420p10le** (10-bit),
`color_primaries` **bt2020**, `color_transfer` **arib-std-b67** (HLG), `color_space`
**bt2020nc**, `color_range` tv, `has_b_frames` 0, `nb_streams` 1 (no audio).

**It is not a camera original.** Its stream encoder tag is `Lavc62.11.100 libx264` and its
muxer is `Lavf62.3.100` — a re-encode. That, plus its filename and its 11.7 Mbps 720p rate,
mark it as a proxy.

> **RESOLVED 2026-07-27, this session — the sentence formerly ending this paragraph read "The
> true camera master is absent from this set and its codec, resolution and bit depth are
> unknown."** That is withdrawn. The camera original was located, in the same `.advanced/`
> directory as the proxy, and pixel-matched against it by direct measurement. See §2.1a.

### 2.1a The camera original, located and pixel-matched (2026-07-27, this session)

**File**: `DJI_20241029174803_0355_D.MP4`, same directory as the proxy
(`_archive/_p-ai-drone-video/.drone_clips/.advanced/`). 994,725,078 bytes, sha256
`fbf55068a6efe2baf6d2f2cc79421cf0726e76065ba2346606b859d5b67225e5`, mtime
2026-03-03T08:56:32.

**Probe (P1)**: HEVC (`hvc1`) Main 10, 3840×2160 coded, `r_frame_rate == avg_frame_rate ==
60000/1001` (59.94 fps), `duration_ts` 3814811/60000 = 63.580183 s exactly, `nb_frames` 3811,
`pix_fmt` yuv420p10le (10-bit), `has_b_frames` 1, bit_rate 125,161,650 bps (format) /
120,065,118 bps (video stream). **Colour**: `color_space=bt2020nc`, `color_primaries=bt2020`,
`color_transfer=arib-std-b67` (HLG), `color_range=tv` — identical to the proxy's own tag set
in every field. `format.tags.encoder = "DJI Mavic3Pro"` (a camera-firmware muxer signature,
not a software re-encoder tag), `creation_time = 2024-10-29T17:48:03Z` (matches the filename's
embedded timestamp exactly). Three additional streams beyond the HEVC video: a DJI `djmd`
metadata track, a DJI `dbgi` debug-info track, and an attached MJPEG thumbnail (960×540,
16:9) — the structure of an unmodified DJI camera file, not a re-encode. `cropdetect` returns
`crop=3840:2160:0:0` at both the start and end of the file (298 frames each window) — full
raster, no baked-in letterbox, matching the proxy's own unletterboxed full frame, so no crop
reconciliation was needed for the comparison below (unlike the split-vs-proxy comparison,
which required the proxy's 1280×544 centre-crop offset).

**Method**: because raw is 59.94 fps and the proxy is exact 30/1 CFR (a 2000:1001 ≈ 1.998:1
ratio, not a clean 2:1), frame-index correspondence cannot be assumed — each sampled proxy
timestamp was matched by extracting the proxy frame at nominal time *T*, then sweeping single
raw frames (scaled 3840×2160→1280×720, bicubic, no crop) across a window of raw times around
*T* in raw-frame steps (1001/60000 = 0.016683 s) and finding the PSNR/SSIM peak — the same
lag-sweep technique this pack already used to frame-lock the four `split_*` clips against the
proxy (§2.2).

**Result — sharp, well-defined peaks at 7 of 9 sampled proxy timestamps spanning the full
duration**, all far above a calibrated same-pair floor:

| Proxy *T* | Best-match raw *t* | Offset | PSNR y | SSIM Y |
|---|---|---|---|---|
| 1 s | 0.950 s | −0.050 s | 36.17 dB | — |
| 10 s | 9.950 s | −0.050 s | 37.81 dB | 0.936 |
| 20 s | 19.950 s | −0.050 s | 37.14 dB | 0.934 |
| 30 s | 29.950 s | −0.050 s | 33.88 dB | 0.785 |
| 50 s | 49.933 s | −0.067 s | 39.95 dB | 0.971 |
| 5 s | ≈4.933–4.950 s | −0.050 to −0.067 s | 29.3 dB (broader peak) | — |
| 40 s | ≈39.933 s | −0.067 s | 29.87 dB (weaker peak) | — |
| 58 s | ≈57.933–57.950 s | −0.050 to −0.067 s | ≈24.1 dB (weak, near-tail) | — |
| 62 s | ≈61.933–61.950 s | −0.050 to −0.067 s | ≈26.3–28.0 dB (weak, near-tail) | — |

**Calibration floor** (same two files, deliberately mismatched timestamps — the pack's own
"no unanchored similarity claim" convention, §README "Anchor every similarity claim"):
`raw 5s↔proxy 50s` 18.96 dB / SSIM Y 0.405; `raw 10s↔proxy 2s` 21.29 dB / SSIM Y 0.576;
`raw 30s↔proxy 62s` 17.23 dB / SSIM Y 0.279; `raw 45s↔proxy 5s` 19.19 dB. **Floor: PSNR y
15.5–19.6 dB, SSIM Y 0.28–0.58.** Even the weakest matched point (t=58s, ≈24.1 dB) clears the
floor's upper bound by 4.5 dB; the seven strongest clear it by 10–24 dB. This is the same
shape of result this pack already treats as conclusive for the split family (28.97 dB vs a
12.48 dB floor, §2.2) — here the gap is if anything wider.

**Verdict: CONFIRMED, high confidence.** `DJI_20241029174803_0355_D.MP4` is the camera
original behind `DJI_0355_proxy.mp4`. Two things are explicitly **not** resolved by this
measurement, and are not being smoothed over:

1. **A constant ~0.050–0.067 s (3–4 raw-frame) offset**, not zero, was needed at every sampled
   point from t=1s to t=50s — i.e. the raw frame that matches proxy time *T* sits at raw time
   *T* minus roughly 3–4 raw-frame periods, not at raw time *T* itself. This offset did **not**
   grow with elapsed time across the 1–50 s range tested, which argues against it being pure
   frame-rate-ratio drift (a clean "raw frame 2N ↔ proxy frame N" decimation aligned at t=0
   predicts an offset of only a few **milliseconds**, growing from ~0 at t=0 to a few ms by
   t=50s — far smaller than the observed constant 50–67 ms). The mechanism is not identified:
   candidates include a small head-trim during proxy creation, or a PTS/start-time convention
   difference between the HEVC and re-encoded H.264 muxers. **Unresolved.**
2. **The exact frame-index mapping** (clean every-other-raw-frame decimation vs. a genuine
   variable-rate resample) is not fully pinned down. The sharpness of the peaks at t=10/20/50s
   (8–13 dB drop to the immediately adjacent raw-frame step) favours **discrete nearest-frame
   selection** over motion-blended interpolation — a blended resample would smear the peak
   across neighbouring offsets rather than produce an isolated single-frame maximum — but the
   precise decimation formula was not derived.
3. **The two weakest windows (t=58s, t=62s)** — both in the last ~9% of the clip — showed
   softer peaks (≈24–28 dB) than the rest (29–40 dB). Still comfortably clear of the floor, but
   not explained: possibly faster motion/more motion blur late in the shot, possibly proximity
   to where the proxy's slightly longer nominal duration (63.633 s vs raw's 63.580 s, a 53 ms
   gap) runs out of exact raw-frame correspondence. **Unresolved.**

**Corroborating, independent evidence** (not part of the pixel measurement above):

- **Colour tags now settle REVIEW.md §5.1 group D's remaining open branch.** The raw file
  declares `color_space=bt2020nc` + `color_primaries=bt2020` + `color_transfer=arib-std-b67`
  + `color_range=tv` over 10-bit `yuv420p10le` — the **same complete HLG signalling set** as
  the proxy. Group D / claim C58's narrowed residual question — "whether the camera original
  behind the proxy was itself HLG/BT.2020, which no file in reach can answer" — is now
  answered: **yes, confirmed by direct measurement of that file.**
- **Sibling manifests in the same `.advanced/` directory.** Of the 7 `manifest.json` files
  under `.advanced/{highlights,highlights_5_22s,highlights_best,highlights_graded,
  highlights_graded_25s,highlights_graded_varied,highlights_long}/`, **5 name
  `DJI_20241029174803_0355_D.MP4` directly as `source_file`** (`highlights`,
  `highlights_5_22s`, `highlights_graded`, `highlights_graded_25s`, `highlights_graded_varied`)
  and the other 2 (`highlights_best`, `highlights_long`) name `DJI_0355_proxy.mp4` — the same
  two manifests already known to correspond to this pack's own split family. Internal
  consistency check: `highlights/manifest.json`'s last clip ends at `end_time: 63.58` —
  matching the **raw file's** own measured duration (63.580183 s) to 2 dp — while
  `highlights_best/manifest.json`'s last clip ends at `end_time: 63.63` — matching the
  **proxy's** own measured duration (63.633333 s) to 2 dp. Whatever tool produced these
  manifests genuinely read real per-file duration from whichever of the two files it was
  pointed at, and used both as inputs to the same clip-extraction pipeline (same
  `split_params` shape, same `h264_videotoolbox` encoder signature) for what this session's
  pixel measurement shows is the same underlying shot.
- A secondary cross-check using the derivative clips themselves (`highlights/split_006_s58.mp4`,
  raw-sourced, 3840×2160, t=0–10s vs this pack's own already-verified corpus file
  `split_004_s65.mp4`, proxy-sourced, t=0–15s, active-area cropped to match) gave a **weak,
  inconclusive** result — matched-time PSNR y only 22–26 dB against a mismatched-time floor of
  21.5 dB, a much smaller gap than the direct raw-master/proxy-master comparison above. This is
  most likely because both derivative clips are downstream of their own independent
  frame-rate-conversion passes (stacking two unknown sub-frame phase offsets rather than one),
  not evidence against the primary finding. Reported for completeness; not relied upon.

### 2.2 Derivatives — the four splits

Provenance verified by measurement, not by trusting the manifest. Active-area (1280×544)
per-frame YAVG correlated against the proxy's centre-crop YAVG over all 1460 candidate lags:

| Clip | Best-match lag | = time | r | Declared `start_time` |
|---|---|---|---|---|
| `split_004_s65` | 0 frames | 0.000 s | +0.99830 | 0.0 — **exact** |
| `split_003_s66` | **500** frames | **16.666667 s** | see note | 16.67 → frame 500 — **exact** |

> **CORRECTED 2026-07-27 — C24 killed 2/3.** This row previously read "501 frames / 16.700 s /
> one frame late", from a raw mean-luma correlation whose top five lags span only
> r = 0.99423–0.99706 — too narrow to resolve a single frame. Pixel PSNR resolves it cleanly:
> mean `psnr_avg` over 60 frames is **18.4002 dB at −ss 16.666667** (frame 500) against
> **17.4937 dB** at frame 499 and **17.4959 dB** at frame 501 — one sharp unique peak,
> reproduced independently by two skeptics. **All four splits are frame-exact** at
> floor(declared `start_time` × 30) = frames 0 / 500 / 750 / 1200. §4 row 7 already said this;
> this table and §2.4 were the stale copies.
| `split_002_s69` | 750 frames | 25.000 s | +0.99948 | 25.0 — **exact** |
| `split_001_s70` | 1200 frames | 40.000 s | +0.95975 | 40.0 — **exact** |

Direct pixel confirmation (**S2**): PSNR y = **28.97 dB** between the proxy
centre-cropped-and-padded and `split_004_s65` over 10 s, against a **12.48 dB** unrelated-pair
floor measured elsewhere in this same set. Mean SSIM at the claimed offsets: 0.9707
(split_004), 0.9605 (split_002), 0.9678 (split_003), 0.9537 (split_001).

The pipeline also performed an undocumented **10-bit HLG/BT.2020 → 8-bit SDR BT.709**
conversion (§4).

### 2.3 Renditions — the two vertical pairs

Neither pair is named anywhere in `manifest.json`, so their provenance is **inferred**, not
documented.

**`viral_test_v2` ↔ `viral_test_v2_4k`** — frame-locked: identical 437 frames / 14.566667 s /
30 fps CFR, exactly 2× linear resolution, YAVG Pearson **r = +0.99987** at lag 0,
mean |ΔYAVG| = **0.196** on a 0–255 scale, and PSNR y = **34.640697 dB** (u 46.21, v 45.48,
min 31.28, max 50.92) between the 4K downscaled to 1080×1920 and the native 1080p. Against a
12.48 dB unrelated-pair floor, conclusive.

**`instagram_reel_test` ↔ `instagram_reel_v34_all_kb_full`** — frame-locked: identical 813
frames / 27.100000 s, exactly 2× linear resolution, YAVG r = **+0.97211**, and per-frame PSNR
across all 813 frames stays well clear of the unrelated-pair floor throughout: min 19.08, p10
19.47, p50 23.53, max 44.11, **zero frames below 18 dB**. Never collapsing toward the ~12.5 dB
floor at any frame is the proof the two share one edit frame-for-frame — had the cuts diverged,
PSNR would drop toward that floor at the divergence point, and it never does. Their fade
geometry is identical to the frame (both begin at t = 26.633 s, both end at YAVG 34.7).
*(**CORRECTED 2026-07-27 — a residual "PSNR is uniform... a grade difference, not an edit
difference" characterisation formerly stood here, missed by the first remediation pass, which
fixed the same claim in `reference_pack.json:922` but not this file.** The per-frame PSNR is
**not** uniform: 40-frame windowed means rise from 19.42 to 34.08 dB with step changes near
frames 320, 520, 560, 600 and 720 — the divergence is concentrated in roughly the first 40% of
the timeline, consistent with a differing **opening treatment or overlay**, not a single
global grade applied evenly throughout. See `editorial_style.json` open_questions OQ15.)*

**Neither vertical family comes from `DJI_0355_proxy.mp4`** — ruled out by measurement, not
assumed:

- `instagram_reel_test` best lagged correlation against the proxy: **r = +0.5228** at 36.53 s,
  which is *below* its own time-reversed null of +0.7748 — worse than chance.
- `viral_test_v2` best: **r = +0.8787** at 45.70 s, against its own reversed null of +0.7798 —
  null-level.
- Genuine source matches in this set score **0.95975–0.99948**.
- MPEG-7 signature `detectmode=full` on `split_003` vs `viral_test_v2`: *"no matching of video
  0 and 1"*.

That null calibration is load-bearing and worth repeating, because naive luma matching is
badly misleading on this material: **time-reversed** `split_003` vs `instagram_reel_test`
scores r = +0.9421 while the *forward* pair scores +0.7497, and known-disjoint split pairs
reach +0.8831 (001 vs 003), +0.8753 (003 vs 004), +0.8006 (002 vs 003). Any correlation below
~0.95 on this corpus is noise.

**Which member of each pair was rendered first is not determinable from pixels** — PSNR is
near-symmetric in both directions. mtime is suggestive only, and for the reel pair it actively
conflicts with the naming (§1.2).

### 2.4 `manifest.json` itself

Not media — a 2,510-byte provenance sidecar (mtime 2026-03-16 19:23, the same minute as
`split_004`), validated with `python3 -m json.tool`. The media directory holds **9 entries**:
8 `.mp4` files plus this sidecar. It documents **only the split family** and says nothing
whatsoever about the four vertical files — which is precisely why their provenance is
inferred rather than known.

### 2.5 The five other newly-probed raw masters (2026-07-27, this session)

`DJI_20241029174803_0355_D.MP4` — the camera original behind `DJI_0355_proxy.mp4` — already
has its own writeup at §2.1a. This section covers the other five raw files discovered in
`_archive/_p-ai-drone-video/.drone_clips/`, none previously probed anywhere in this project.
All five are read-only, never copied into this repo; measurements are in-place.

| File | Duration | Codec / pix_fmt | `color_space` / `color_transfer` | scdet max |
|---|---|---|---|---|
| `DJI_20241029173912_0350_D.MP4` | 16.233 s | hevc, yuv420p10le | bt2020nc / arib-std-b67 (HLG) | 1.621 |
| `DJI_20241029174007_0351_D.MP4` | 3.804 s | hevc, yuv420p10le | bt2020nc / arib-std-b67 (HLG) | 1.377 |
| `DJI_20241030011347_0341_D.MP4` | 25.542 s | hevc, yuv420p10le | bt2020nc / arib-std-b67 (HLG) | 1.060 |
| `DJI_20241030011801_0346_D.MP4` | 24.041 s | hevc, yuv420p10le | **bt709 / bt709 (SDR)** | 0.131 |
| `DJI_20241029174916_0356_D_383181722.mov` | 26.526 s | h264, yuvj420p | bt2020nc / **smpte2084 (PQ)** | 0.355 |

All five are `3840×2160`, `~59.94fps` (`60000/1001`), and share the same DJI multi-stream
container structure as the confirmed camera original at §2.1a (a primary video stream plus
two `codec_type=unknown` telemetry/subtitle streams and an embedded `960×540` MJPEG proxy
stream) — consistent with all six being camera-original files from the same drone/firmware,
not re-encodes.

**Zero hard cuts extends to all five.** Every scdet max above sits far below this pack's
established 5.0/10.0 discard thresholds (§0, README "the one fact that matters most") — the
finding is not an artifact of the 8-file corpus or of transcoding; it holds on raw ~60fps 4K
camera masters too.

**Three different transfer curves in six raw files from one source tree is itself a
finding.** Four masters (including the confirmed camera original) declare HLG
(`arib-std-b67`); `DJI_20241030011801_0346_D.MP4` declares SDR `bt709`; the `.mov` file
declares PQ (`smpte2084`) — a third, distinct HDR transfer function, on a different codec
(`h264` vs the others' `hevc`) and a different pixel format (`yuvj420p`, JPEG-range, vs the
others' `yuv420p10le`). This is not a controlled, single-format capture set: whatever
generated these six files varied both HDR handling and codec across shots on the same
drone. Any downstream pipeline assuming a uniform camera transfer curve across this footage
tree would be wrong for at least 2 of the 6 files measured here.

### 2.6 The 39 archive derivative clips — summary (2026-07-27, this session)

Derived from 7 manifest.json files in `.drone_clips/.advanced/` (`highlights`,
`highlights_5_22s`, `highlights_best`, `highlights_graded`, `highlights_graded_25s`,
`highlights_graded_varied`, `highlights_long`), each run with different `split_params`
against either `DJI_0355_proxy.mp4` or the raw `DJI_20241029174803_0355_D.MP4`. Full
per-manifest claimed-vs-measured reconciliation is in §8. This section is the corpus-level
summary: all 39 probed (raw ffprobe JSON + scdet CSV retained for every one), read-only,
never copied into this repo.

| Manifest | Clips | Resolution(s) | Duration range | scdet max (excl. frame-1 artifact) |
|---|---|---|---|---|
| `highlights` | 7 | 3840×2160 | 3.567–10.000 s | 1.448 *(row max 7.828 is the frame-1 warm-up artifact, see below)* |
| `highlights_5_22s` | 3 | 3840×2160 | 9.967–22.000 s | 2.323 |
| `highlights_best` | 5 | 1280×720 | 5.600–10.600 s | 2.381 |
| `highlights_graded` | 7 | 3840×2160 | 3.567–10.000 s | 4.691 |
| `highlights_graded_25s` | 10 *(3 documented, 7 undocumented — §8)* | 3840×2160 | 3.567–25.000 s | 4.691 |
| `highlights_graded_varied` | 2 | 3840×2160 | 23.567–40.000 s | 1.784 |
| `highlights_long` | 5 *(3 documented, 2 undocumented — §8)* | 1280×720 | 15.500–22.000 s | 2.563 |

**Zero hard cuts extends to all 39.** Only one raw scdet value in the entire set —
`highlights__split_003_s61`, 7.828 at `pts_time` 0.033333 s — exceeds this pack's 5.0
discard threshold, and it is the corpus's own already-documented **frame-1 `scdet` warm-up
artifact** (§0/README: `prev_mafd` is still 0 at the first inter-frame comparison, so the
score equals the full MAFD, not a real discontinuity). Excluding row 1, this clip's true max
is 1.448 — the artifact reproduces correctly on new material and this pack's own documented
mitigation ("discard frame index 1 before computing any threshold") is what catches it. No
other clip in the 39 comes within 2× of the threshold. Global max across all scored frames
in the 39-clip set, frame-1 rows included: 7.828; excluded: 4.691 (`highlights_graded` and
`highlights_graded_25s`'s shared `split_003_s61`-derived clip, itself well below threshold).

---

## 3. Edit grammar

### 3.1 The finding that governs everything else

**There are ZERO hard cuts in this pack. Across all 4,099 scored frames in all 8 files, not
one frame reaches even 5.0 on scdet's 0–100 scale, let alone 10.0.**

Recounted directly from the eight stored `probe/*.scd.csv` files (command **P2**), row counts
813 + 813 + 450 + 450 + 249 + 450 + 437 + 437 = **4,099**:

| File | Rows | Max score | Max excl. frame-1 warm-up | Median | ≥ 5.0 | ≥ 10.0 |
|---|---|---|---|---|---|---|
| `instagram_reel_v34_all_kb_full` | 813 | 3.537 | 3.537 | 0.0900 | 0 | 0 |
| `split_001_s70` | 450 | 2.668 | **0.537** | 0.0265 | 0 | 0 |
| `split_002_s69` | 450 | 2.435 | **0.475** | 0.0320 | 0 | 0 |
| `split_003_s66` | 249 | 2.104 | **0.174** | 0.0170 | 0 | 0 |
| `viral_test_v2` | 437 | 1.799 | 1.799 | 0.1180 | 0 | 0 |
| `viral_test_v2_4k` | 437 | 1.776 | 1.776 | 0.1420 | 0 | 0 |
| `instagram_reel_test` | 813 | 1.547 | 1.547 | 0.0350 | 0 | 0 |
| `split_004_s65` | 450 | 0.516 | 0.415 | 0.0150 | 0 | 0 |

In `split_001/002/003` the **global maximum is an artefact, not content**: it lands on frame 1
at t = 0.033333 s, where scdet's `prev_mafd` is still 0. Excluding it, their true content
maxima are 0.537 / 0.475 / 0.174.

**This is a positive finding, not a detection failure.** It was calibrated against a synthetic
positive control (`testsrc2` → `black` → `smptebars`, built in `/tmp` and deleted after use)
whose two genuine hard cuts scored **31.42** and **42.19** — 10× to 80× above anything present
in this corpus. It was independently cross-checked with command **X1**: `select='gt(scene,0.3)'`
plus `showinfo` reports **0 frames** in every split file, and a `metadata=print:file=-` sweep
gives max `lavfi.scene_score` of **0.039609** (`instagram_reel_test`, 812 frames) and
**0.090538** (`instagram_reel_v34`) against a 0.3 cut gate — **0 frames above even 0.1**.

### 3.2 What that means for anyone using this pack as a style reference

Plainly: **this is not a fast-cut montage pack, and it cannot teach cutting rhythm.**

Every one of the eight files is a **single continuous graded long take**. Shot count is 1
everywhere, so mean shot length equals total duration by definition — splits 15.000 / 15.000 /
8.300 / 15.000 s (mean 13.325 s), verticals 27.100 / 27.100 / 14.567 / 14.567 s. If the four
splits were assembled in the manifest's order the average shot length would be 53.3 / 4 =
**13.325 s**.

The practical consequences:

1. **Any model, prompt, or heuristic trained on this pack to produce "cut timing" has no
   signal to learn from.** There are no cuts. A pack-derived "average shot length" of 13.325 s
   is an artefact of file boundaries, not an editorial decision.
2. **The house style this pack actually documents is: long take, letterbox or vertical crop,
   grade, terminal fade.** That is a *framing and grading* reference, not a *pacing*
   reference.
3. **There is no audio anywhere** (verified on all 8 files plus the proxy, command **P4**), so
   there is no music bed to which cuts could have been timed — consistent with, and reinforcing,
   the measured absence of cutting. Any sound design is added downstream on every surface.
4. **The only editorial transition measured anywhere in the pack is a terminal fade-to-black
   on the four verticals.** The four splits have *no* transition at either end — their
   terminal monotonically-decreasing luma run is **0 frames** and their opening frames sit at
   normal exposure (`split_001` Y = 76.4 at t = 0 against a file mean of 76.66). They are
   **hard-in / hard-out raw segments handed off for assembly**, not finished pieces.

### 3.3 Soft transitions — searched for, and near-absent

A cut is a single isolated spike; a dissolve is a *run* of consecutive frames elevated above
the file's own baseline. Searching for the longest run at ≥ 5× each file's own median frame
difference:

| File | Longest elevated run |
|---|---|
| `split_001_s70` | 2 frames |
| `split_002_s69` | 3 frames |
| `split_003_s66` | 2 frames |
| `split_004_s65` | 4 frames |
| `viral_test_v2` | 5 frames |
| `viral_test_v2_4k` | 3 frames |
| `instagram_reel_test` | 5 frames |
| **`instagram_reel_v34_all_kb_full`** | **19 frames, starting t = 0.77 s** |

Seven of eight are flat. The single 19-frame exception is the pack's one unexplained
structural feature and is **not resolved** — its frame-locked 1080p twin cannot settle it,
because a dissolve present in the shared cut would appear identically in both files and so
would not disturb their PSNR (§5 group B).

### 3.4 Terminal fades — measured

| File | Fade start | Length | YAVG trajectory | Rate |
|---|---|---|---|---|
| `instagram_reel_test` | t = 26.633 s | 13 frames (0.433 s) | 106.5 → 34.7 | ≈5.5 luma/frame |
| `instagram_reel_v34_all_kb_full` | t = 26.633 s | 13 frames (0.433 s) | 106.5 → 34.7 | ≈5.5 luma/frame |
| `viral_test_v2` | t = 14.067 s | 14 frames (0.467 s) | 113.4 → 23.7 | ≈6.4 luma/frame |
| `viral_test_v2_4k` | t = 14.067 s | 14 frames (0.467 s) | 113.4 → 23.7 | ≈6.4 luma/frame |
| all four `split_*` | — | **0 frames** | — | none |

Confirmed **multiplicative** — a true fade, not a luma dip: across `viral_test_v2`'s fade,
YMAX falls 184 → 30 and SATAVG falls 5.35 → 0.70 in step with YAVG. The fades are
**truncated**: the last frame of each is not black (YAVG 23.68–34.71, YMAX 30–51).

### 3.5 Letterbox — two different answers, and the apparent contradiction resolves

**Splits — 2.35 letterbox is real and baked in as black bars inside a genuinely 16:9 raster.**
Command **C1** returns one stable value on all four clips: `crop=1280:544:0:88`
(448/448/247/448 detections; an independent re-check of `split_001` gave that value on 448 of
450 frames). 88 + 544 + 88 = 720 exactly; 1280/544 = **2.352941:1**. Per-row `signalstats`
after `format=gray` puts the boundary exactly at rows 88 and 631: source rows 84/86 read max
Y 1–2 while rows 88/90/92 read 182–184, and rows 626–630 read 204–215 while rows 632/634 read
2–5. Bar luma is **Y = 16** (limited-range video black, matching `color_range=tv`):
YMIN = YMAX = 16 across all frames of `split_003`/`split_004` top bars, worst case
YMIN 13 / YMAX 21 in `split_001`'s bottom bar from compression noise.

So the manifest's `letterbox: "2.35"` and a 16:9 coded frame are **compatible, not
contradictory** — an earlier pass in this run flagged that pairing as a suspected defect and
it is now cleared.

The bars were **added by this pipeline**: **C1** on the source proxy returns
`crop=1280:720:0:0` for all frames — the source is not letterboxed.

**Mechanism: vertical centre crop, not anamorphic squeeze.** Two independent discriminators
agree. (a) SSIM of `split_004` against the source cropped at row 88 is **0.9707**, versus
**0.4399** for a scale-to-544 hypothesis; a vertical offset sweep gives 0.6806 / 0.7318 /
**0.9707** / 0.7318 / 0.6830 at y = 84/86/88/90/92 — a sharp peak at 88. (b) `split_001`
correlates at **+0.95975** against the proxy centre-crop but only **+0.30494** against the
proxy full frame.

**Verticals — no letterbox and no pillarbox.** **C1** returns the full frame:
`crop=1080:1920:0:0` (811 reports) and `crop=2160:3840:0:0` (298 reports over 10 s sampled),
and no vertical file's luma reaches legal black outside its tail fade.

Caveat kept explicit: `cropdetect` thresholds at luma 24, so it proves the bars sit *below*
that level. It does not prove they are mathematically pure or uniformly black (§5 group I).

### 3.6 Colour treatment

**Splits — a tagged SDR grade plus an undocumented HDR downconvert.** The manifest declares
`color: "drone_aerial"` at `color_intensity: 0.65`. Tagging on the outputs is *partial*:
`color_space=bt709` and `color_range=tv` are present, but `color_primaries` and
`color_transfer` are **absent**, so primaries and transfer are unspecified rather than
explicitly BT.709. Since the source proxy is 10-bit yuv420p10le / High 10 / bt2020 primaries /
arib-std-b67 (HLG) / bt2020nc, the render also performed an **HLG BT.2020 10-bit → SDR 8-bit
conversion that the manifest never mentions**.

Measured on the **active area only** (bars excluded, command **S1**): YAVG mean 88.39–96.29,
YMIN **31–41** — blacks are lifted, there is no true black in the picture — SATAVG mean
8.70–15.81. Exposure is extremely stable: `split_001`'s YAVG spans only 92.24–98.61 across a
whole 15 s take.

**Verticals — an untagged, brighter, more saturated grade.** `color_space`,
`color_primaries`, `color_transfer` and `color_range` are **all absent on all four**. Measured
YAVG mean 117.34–121.89 and SATAVG mean 12.82–15.58 with peaks 23.32–25.54 — materially
brighter and more saturated than the splits' active picture. Blacks lifted here too (global
YMIN 14–30). Within the reel pair, **grade is the version axis**: v34 is the hotter render
(frame-0 YAVG 137.6 vs 128.9; YAVG max 146.98 vs 132.00).

**Caveat that will not be papered over:** the family-to-family YAVG/SATAVG gap could partly
reflect **different content** rather than different grading, since the two families provably
share no source footage (§2.3).

### 3.7 Speed and motion envelopes

**No positive evidence of speed ramping in any file**, and in the one place it is documented
it left no measurable trace.

- Every declared span equals its output exactly: 40.0→55.0, 25.0→40.0 and 0.0→15.0 are
  15.000 s = 450 frames each, and that is precisely what the files contain. **No net retime.**
- `split_003`'s 8.300 s / 249 frames against a declared 8.33 s is **not** a 0.36 % speed
  change. **[Corrected 2026-07-27 — C24 killed 2/3.]** Its start is frame-exact at frame 500
  (16.666667 s); the one-frame deficit falls at the **end** of the range (it covers frames
  500–748, not 500–749), which is exactly what the sidecar's own 2 dp rounding yields:
  25.0 − 16.67 = 8.33 s → 8.33 × 30 = 249.9 → floor 249 (§4 row 7).
- **M1** drops **0** frames from `split_001/002/003/004` (450/450, 450/450, 249/249, 450/450)
  and **0** from `instagram_reel_test` (813/813); `viral_test_v2` drops just **2 of 437**. No
  frame-duplicated slow motion anywhere.
- All 8 files are CFR 30/1 with `r_frame_rate == avg_frame_rate` and `duration == frames/30`
  exactly.

**Motion envelopes**, measured as per-second mean frame difference:

- **Splits are FLAT with no trend** — range ratios only 3.2–5.6×, means 0.010–0.099. Steady
  continuous drone moves.
- **Verticals are strongly FRONT-LOADED and decay monotonically** — range ratios 33.3×
  (`instagram_reel_test`), 60.7× (v34), 13.1× (`viral_test_v2`), 6.3× (`viral_test_v2_4k`).

> **WITHDRAWN 2026-07-27 — C56 killed 3/3, unanimously.** Both halves fail. (a) **Not
> monotonic**: `instagram_reel_test`'s global per-second maximum is at **t ≈ 17.8 s**, above
> its opening second, and `viral_test_v2`'s global maximum is at **t = 14.100 s** — the last
> second of a 14.567 s file. Three of four files have a mid-file local maximum at or above the
> opening level. (b) **Not 13–61× as a decay rate**: those are whole-file max-second/min-second
> ratios, not per-second decay, and the three skeptics' reconstructions of the undefined metric
> gave 33.29/60.66/13.14/6.25, 59.4/84.0/11.8/9.0 and first-second÷last-second of
> **1.1× / 2.6× / 9.7× / 2.8×** — mutually irreconcilable, which is itself the finding: the
> metric was never defined. (c) **Metric-dependent**: on MAFD rather than scdet score the
> effect collapses to 4.89/6.02/5.23/5.29 and `viral_test_v2` runs slightly *back*-loaded.
> `editorial_style.json` already sets `front_loaded_motion_envelope: null` and
> `front_loaded_motion_parameter: null` — the JSON was right and this prose was the stale copy.
> Treat the paragraph below as superseded; the defensible residue is only that the verticals'
> first ~4 s carry elevated frame-difference *range*.
  `instagram_reel_test` runs 0.28 / 0.29 / 0.36 / 0.31 over its first four seconds then falls
  to 0.01–0.05 by t = 19–26 s; v34 runs 0.52 / 1.11 / 1.02 / 0.44 then falls to 0.02–0.05;
  `viral_test_v2` runs 0.41 / 0.40 / 0.35 then falls to 0.03. Their terminal rise coincides
  exactly with the fade-out, which itself generates frame difference.

**That front-loading is NOT called a speed ramp here.** It is equally consistent with a
decelerating camera move or with animated overlay graphics, and separating those requires
optical flow (§5 group F).

### 3.8 Delivery surfaces present in the pack

| Surface | Files | Spec | Read |
|---|---|---|---|
| Vertical 9:16 upload | `instagram_reel_test`, `viral_test_v2` | 1080×1920, 30 fps CFR, 13.4–14.1 Mbps, 14.567 s / 27.100 s, no audio, full frame no bars | Standard short-form upload spec (Reels / TikTok / Shorts); both durations sit inside common slots |
| Vertical 9:16 "4K" | `instagram_reel_v34_all_kb_full`, `viral_test_v2_4k` | 2160×3840, 30 fps CFR, 73.8–75.9 Mbps | Mastering/archival renditions, **not** upload targets; 3840 is the LONG edge |
| Horizontal 2.35-in-16:9 | `split_001..004` | 1280×720 raster with 1280×544 active, 30 fps CFR, ~15.0 Mbps, 8.3–15.0 s, no audio | **Proxy-resolution review / edit-assembly assets**, not a finished horizontal master — `split_params.resolution` is `"source"` and the source *is* the 720p proxy. Highest per-pixel rate in the set, consistent with an intermediate |

No surface in the set carries audio, and no surface carries a second shot.

---

## 4. `manifest.json` agreement table

`manifest.json`: 2,510 bytes, mtime 2026-03-16 19:23, validated with `python3 -m json.tool`.
It documents the four splits only.

### 4.1 All 37 reconciled claims

| # | Scope | Claimed | Measured | Agrees |
|---|---|---|---|---|
| 1 | all splits | `clips[].filename` — the four `split_*.mp4` | All four present in `00-assets/drone-video-examples/`; sha256 of each matches the probe phase byte-for-byte (`7f8928ef…`, `aebd54f0…`, `33dd47b0…`, `e5ceb9e4…`) | **yes** |
| 2 | all splits | `source_file.path = /Users/matthewdeane/…/DJI_0355_proxy.mp4` | Path does not resolve; `/Users/matthewdeane` does not exist. File found at `/Users/mac/…/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4`, 92,905,225 bytes | **NO** |
| 3 | all splits | `source_file.name = DJI_0355_proxy.mp4` — common source | **Confirmed by pixel comparison.** Mean SSIM 0.9707 / 0.9537 / 0.9605 / 0.9678 (split_004/001/002/003) at the claimed offsets | **yes** |
| 4 | split_004 | `start_time 0.0` | Source frame 0. SSIM peak at offset 0, mean 0.9707 (n=450, min 0.9587, max 0.9757). Frame-exact | **yes** (Δ 0 frames) |
| 5 | split_002 | `start_time 25.0` | Source frame 750. Sweep 0.3515 / **0.4777** / 0.3493 at frames 749/750/751 — sharp single peak. Frame-exact | **yes** (Δ 0 frames) |
| 6 | split_001 | `start_time 40.0` | Source frame 1200. Sweep 0.4738 / **0.6955** / 0.4697 at 1199/1200/1201. Frame-exact | **yes** (Δ 0 frames) |
| 7 | split_003 | `start_time 16.67` | Source frame 500 = 16.666667 s. Sweep 0.3498 / **0.4016** / 0.3491 at 499/500/501. Content frame-exact; the **written value** is a 2-dp rounding | **NO** (Δ +0.003333 s = 0.1 frame) |
| 8 | split_004 | `end_time 15.0` → source frame 450 exclusive | 450 frames from frame 0 = frames 0…449 | **yes** (Δ 0 frames) |
| 9 | split_002 | `end_time 40.0` → frame 1200 exclusive | 450 frames from 750 = frames 750…1199 | **yes** (Δ 0 frames) |
| 10 | split_001 | `end_time 55.0` → frame 1650 exclusive | 450 frames from 1200 = frames 1200…1649 | **yes** (Δ 0 frames) |
| 11 | split_003 | `end_time 25.0` → frame 750 exclusive, i.e. 250 frames | Only **249** frames (`nb_frames` 249, **P3** 249). Covers frames 500…748, ending at frame 749 = 24.966667 s | **NO** (Δ −1 frame / −0.033333 s) |
| 12 | split_001 | `duration 15.0` | `format.duration` 15.000000, `duration_ts` 230400/15360 = 15.0, 450 frames | **yes** (Δ 0.000000 s) |
| 13 | split_002 | `duration 15.0` | 15.000000, 230400/15360, 450 frames | **yes** (Δ 0.000000 s) |
| 14 | split_004 | `duration 15.0` | 15.000000, 230400/15360, 450 frames | **yes** (Δ 0.000000 s) |
| 15 | split_003 | `duration 8.33` | **8.300000**, `duration_ts` 127488/15360 = 8.3 exactly, 249 frames. Not a rounding of 8.33 (= 249.9 frames) | **NO** (Δ −0.033333 s, −0.40 %) |
| 16 | all splits | `score 70.0 / 69.8 / 66.8 / 65.6` | **Values UNVERIFIABLE** — undocumented metric, no ffprobe observable maps to it. Internal check: filename suffixes s70/s69/s66/s65 are `int()` **truncations**, not roundings (69.8→s69, 66.8→s66) | **yes**, self-consistent only |
| 17 | all splits | `motion_energy 100.0 / 96.1 / 79.9 / 77.7` (001/002/003/004) | **Rank order corroborated** — perfect Spearman match, confirmed three ways on two independent metrics. *(**Magnitudes WITHDRAWN 2026-07-27 — C54 killed 2/3.** The MAFD column formerly printed here — 3.2506/2.7098/2.5797/1.9114, max-normalised 100.00/83.36/79.36/58.80 — reproduced at neither refuting skeptic, and the single divergence figure "−24.3 %" is withdrawn: divergence is metric- and surface-dependent (−18.9 % on cropped-source scdet MAFD, 11.1 % on proxy full-frame 8-bit MAFD). See §7.1 C54 and MAT-6.)* | **NO** on being a linear normalisation of measured motion; **YES** on rank order |
| 18 | all splits | `motion_type REVEAL / ORBIT_CW / REVEAL / STATIC` | **UNVERIFIABLE IN-SESSION** — needs per-pixel motion-vector direction and rotation estimation (optical flow / cv2). scdet gives magnitude only | **NO** — not measurable, not guessed |
| 19 | all splits | `post_processing.letterbox "2.35"` | **Verified.** **C1** → `crop=1280:544:0:88` on all four (448/448/247/448); 88+544+88 = 720; 1280/544 = 2.352941; bars Y=16; source cropdetects `1280:720:0:0` so bars were added here; SSIM sweep peaks sharply at y=88 (0.9707 vs 0.6806/0.7318/0.7318/0.6830) | **yes** (Δ +0.002941, +0.125 %) |
| 20 | all splits | `post_processing.auto_speed true` | **No speed change of any kind.** Single packet `duration_time` 0.033333; pts deltas only {0.033333, 0.033334}; ratio 1.000000 on 3 of 4; **decisive** — 1:1 frame correspondence with flat SSIM quintiles (split_004 .9708/.9734/.9734/.9705/.9652; split_001 .9393/.9489/.9601/.9609/.9594; split_002 .9631/.9629/.9652/.9613/.9500; split_003 .9630/.9676/.9700/.9715/.9673) | **NO** — measurable **no-op** |
| 21 | all splits | `post_processing.color "drone_aerial"` @ `color_intensity 0.65` | **Luma-only change; chroma untouched.** Output tracks Baseline A (8-bit reduction, no matrix conversion) on chroma to ~2 % and diverges badly from Baseline B (true bt2020→bt709) | **NO** — no measurable colour change |
| 22 | all splits | `stabilized false` / `stabilize false`, tuning params all null | **Corroborated.** 1:1 SSIM correspondence at a single fixed crop rectangle, sweep peaking sharply at y=88 (0.73 at ±2 px), holds 0.95–0.97 for every frame. A stabiliser's per-frame warp would blur the peak | **yes** (rules out large warp, not sub-pixel) |
| 23 | split_params | `min_duration 7.0` | All four durations ≥ 7.0. **But** the excluded source tail (frames 1650–1908) is 8.633333 s, also > 7.0, and should have survived | **NO** — satisfied but does not explain the exclusion |
| 24 | split_params | `max_duration 15.0` | 3 of 4 clips are **exactly** 15.000000 s, and interior boundaries fall at exactly 25.0 s and 40.0 s — exactly 15.0 s apart | **yes** (Δ 0.000000 s) — the cap is the active mechanism |
| 25 | split_params | `scene_threshold 7.0`, `summary.scenes_detected 7` | **Not on the ffmpeg scale, and boundaries are not content-derived.** Full scdet over the source (1909 frames): min 0.000, p50 0.027, p90 0.101, p99 0.378, **max 1.706**, mean 0.0472, sd 0.0801 — zero frames above 7.0, zero above 2.0. Scores *at* the claimed boundaries: frame 450 (t=15.0) **0.004, rank 1752/1909**; frame 1650 (t=55.0) 0.009, rank 1571; frame 1200 (t=40.0) 0.030, rank 897; frame 750 (t=25.0) 0.055, rank 464; only frame 500 (t=16.666667) elevated at 0.165, rank 79 (neighbour 501 = 0.378 = source p99) | **NO** — 4 of 5 boundaries at or below median |
| 26 | split_params | `resolution "source"` | Source 1280×720; all four clips 1280×720, `coded_*` identical, no SAR/DAR. Raster preserved exactly. **But** the picture is a 1280×544 centre crop — **176 of 720 rows (24.4 %) discarded** | **yes** on raster (Δ 0 px) |
| 27 | split_params | `quality "high"` | Output bitrates 15,013,683 / 15,006,342 / 15,025,257 / 15,007,948 bps — spread 18,915 bps (**0.126 %**), a fixed ~15 Mbps target. Source is 11,678,856 bps → outputs are **28.6 % higher** than the source. Encoder changed libx264 → h264_videotoolbox | **yes**; label→bitrate mapping unverifiable |
| 28 | split_params | `sort "score"` | `clips[]` order is 70.0, 69.8, 66.8, 65.6 — strictly descending. **This is not source-timeline order** (timeline order is 004, 003, 002, 001) | **yes** |
| 29 | split_params | `min_score 0.0` | All four scores ≥ 0.0. Trivially satisfied; no discriminating power | **yes**, but vacuous |
| 30 | split_params | `filtered false` | **Directly contradicted by `summary.scenes_filtered = 3` in the same document.** Neither field's semantics is documented | **NO** — internal contradiction |
| 31 | split_params | `count null`, `enhanced false` | `count null` consistent with 4 clips against no target. `enhanced false` **UNVERIFIABLE** — no definition, no observable | **yes** / unverifiable |
| 32 | summary | `total_clips 4` | Exactly 4 `split_*.mp4` present | **yes** (Δ 0) |
| 33 | summary | `total_duration 53.3` | 15.000000 + 15.000000 + 8.300000 + 15.000000 = **53.300000** exactly. **But** the manifest's own `clips[].duration` values sum to **53.33** | **yes** vs reality (Δ 0.000000 s); −0.03 s vs the document's own figures |
| 34 | summary | `total_size_mb 95.4` | 28,153,847 + 28,140,059 + 15,590,791 + 28,143,093 = 100,027,790 bytes. ÷1,048,576 = **95.3939 MiB**; ÷1,000,000 = 100.0278 SI MB | **yes** under MiB (Δ −0.0061); **unit label wrong** |
| 35 | summary | `avg_score 68.1` | (70.0 + 69.8 + 66.8 + 65.6)/4 = 272.2/4 = **68.05** | **NO** (Δ +0.05) |
| 36 | summary | `scenes_detected 7`, `scenes_filtered 3` (7−3 = 4 clips) | Arithmetic works, **mechanism does not.** Clips occupy source frames 0–449, 500–748, 750–1199, 1200–1649 — splits 003/002/001 are **contiguous**, one unbroken 38.3 s span subdivided at exactly max_duration intervals. Coverage 1,599/1,909 frames (83.8 %), 55.0 s of 63.633333 s (86.4 %). Unaccounted: frames 450–499 (1.666667 s) and 1650–1908 (8.633333 s) — **only 2 disjoint regions for 3 claimed filtered scenes** | **NO** |
| 37 | all splits | *(omission)* no pixel-format, bit-depth or colour-matrix transformation is recorded | Source: yuv420p10le, High 10, level 31, bt2020nc, tv, libx264. Clips: yuv420p (8-bit), High, level 31, bt709, tv, h264_videotoolbox. **Bit depth halved; matrix tag changed — neither recorded**, and the chroma measurements show the tag changed *without* a pixel conversion | **NO** — two undocumented transformations |

**Score: 22 of 37 agree, 15 do not.**

### 4.2 The 15 discrepancies, grouped by severity

#### CONTRADICTION (2) — the document disagrees with itself or with a hard measurement

**CON-1. `split_003_s66` duration: manifest claims 8.33 s, file is 8.300000 s — a real 1-frame
shortfall, and the manifest contradicts itself about it.**

Quantified: `format.duration` 8.300000, `stream.duration` 8.300000, `duration_ts` 127488 /
`time_base` 15360 = 8.3 **exactly**, `nb_frames` 249 and **P3** `-count_frames` 249 —
249/30 = 8.300000. This is not a rounding of 8.33, which would be 249.9 frames. Frame-exact
SSIM alignment shows the clip covers source frames 500…748, whereas the claimed span
16.666667→25.0 is frames 500…749 = 250 frames.

**Mechanism, demonstrated:** the manifest stores `start_time` rounded to 2 dp as `16.67`;
25.0 − 16.67 = 8.33 s; 8.33 × 30 = 249.9 → `floor()` = **249**. *The document's own rounding
caused the frame loss.*

**Internal contradiction:** `summary.total_duration` is 53.3, which equals 15.0 + 15.0 + **8.3**
+ 15.0 — matching the measured sum of exactly 53.300000 — while `clips[2].duration` says
**8.33**. The two fields disagree by 0.03 s and **only the summary is correct**.

**CON-2. `split_params.filtered = false` directly contradicts `summary.scenes_filtered = 3`.**

Quantified: both fields are in the same 2,510-byte document. `split_params.filtered` is the
boolean `false`; `summary.scenes_filtered` is the integer `3`. `split_params.min_score` is
`0.0`, which cannot filter anything. If `min_duration 7.0` was the filter, the value of the
`filtered` flag still contradicts it. The manifest documents neither field's semantics, so
**the conflict cannot be resolved from the artifact**.

#### MATERIAL (8) — affects how the pack should be read or reused

**MAT-1. `auto_speed: true` is a measurable no-op — no speed change was applied to any clip.**

Decisive test is 1:1 frame correspondence, not frame timing. SSIM against the source at the
claimed offset holds flat for the whole clip with no progressive drift:

| Clip | SSIM quintile means |
|---|---|
| split_004 | 0.9708 / 0.9734 / 0.9734 / 0.9705 / 0.9652 |
| split_001 | 0.9393 / 0.9489 / 0.9601 / 0.9609 / 0.9594 |
| split_002 | 0.9631 / 0.9629 / 0.9652 / 0.9613 / 0.9500 |
| split_003 | 0.9630 / 0.9676 / 0.9700 / 0.9715 / 0.9673 |

Clip frame N = source frame offset+N for all **1,599 frames**. A speed ramp resamples time and
would make SSIM collapse or drift. Corroborating: output duration equals `end_time − start_time`
exactly on 3 of 4 clips (ratio 1.000000); every clip is strictly CFR (single packet
`duration_time` 0.033333; pts deltas only {0.033333, 0.033334}, the 1-tick alternation of a
1/15360 timebase; `r_frame_rate == avg_frame_rate == 30/1`).

**Important:** the CFR frame-timing evidence *alone proves nothing*, because re-encoding
normalises PTS regardless of any speed change applied upstream. Only the 1:1 pixel
correspondence turns this into a positive finding.

**MAT-2. `color: "drone_aerial"` @ `color_intensity 0.65` produced no measurable colour change —
only a luma change.**

Controls built from the located source over `crop=1280:544:0:88`, first 450 frames, per-frame
`signalstats` means (**S1**):

| Measure | Baseline A (8-bit reduction only) | Baseline B (true bt2020→bt709 via `colorspace=all=bt709:iall=bt2020`) | Measured `split_004_s65` active region |
|---|---|---|---|
| YMIN | 56.54 | 56.17 | **52.50** |
| YAVG | 100.11 | 98.83 | **91.85** |
| YMAX | 254.99 | 243.00 | **238.22** |
| UAVG | 139.90 | 141.96 | **140.06** |
| VAVG | 117.57 | 106.91 | **117.30** |
| SATAVG | 15.47 | 24.94 | **15.81** |
| HUEAVG | 308.47 | 323.22 | **308.56** |

Deltas vs **A**: luma YAVG **−8.26 (−8.25 %)**, YMAX −16.77 (−6.58 %), YMIN −4.04 (−7.15 %) —
a highlight-weighted downward compression. Chroma UAVG **+0.16 (+0.11 %)**, VAVG −0.27
(−0.23 %), SATAVG +0.34 (+2.2 %), HUEAVG +0.09 (+0.03 %) — all at or near noise.
Deltas vs **B**: VAVG +10.39 (+9.7 %), SATAVG −9.13 (−36.6 %), HUEAVG −14.66.

The output tracks A, not B. A parameter named "color" at 0.65 intensity is therefore a
**luma-only** operation as far as it is measurable, and the bt2020nc→bt709 tag change on the
clips was **not** accompanied by a chroma conversion of pixel data.

**MAT-3. `scenes_detected 7` / `scene_threshold 7.0` does not describe what produced these clips —
the boundaries are max_duration-driven, not content-driven.**

Frame-exact alignment shows splits 003, 002 and 001 are **contiguous** in the source (frames
500–748, 750–1199, 1200–1649): one unbroken 38.3 s span subdivided at exactly 25.0 s and
40.0 s — exactly `max_duration` (15.0 s) apart — with 3 of 4 clips exactly 15.000000 s long.

scdet over the full source (1909 frames; min 0.000, p50 0.027, p90 0.101, p99 0.378, max
1.706, mean 0.0472, sd 0.0801) gives these scores at the claimed boundaries:

| Source frame | Time | scdet score | Rank |
|---|---|---|---|
| 450 | 15.0 s | 0.004 | **1752 / 1909** (among the quietest frames in the file) |
| 1650 | 55.0 s | 0.009 | 1571 / 1909 |
| 1200 | 40.0 s | 0.030 | 897 / 1909 |
| 750 | 25.0 s | 0.055 | 464 / 1909 |
| 500 | 16.666667 s | **0.165** | **79 / 1909** (neighbour frame 501 = 0.378 = exactly p99) |

A genuine scene boundary is a **local maximum** of frame difference. Four of five sit at or
below the median. So 1 of 5 boundaries is plausibly content-derived and 4 are not; **4 clips
came from at most 2 content segments**. The 7 − 3 = 4 arithmetic matching `total_clips` is
coincidence, not mechanism. Separately, threshold 7.0 cannot be checked on the ffmpeg scale at
all — zero source frames exceed 7.0 and zero exceed even 2.0 — so 7.0 belongs to a different,
undocumented metric.

**MAT-4. `source_file.path` is stale and unresolvable, though the file exists locally elsewhere.**

Quantified in §2.1. Provenance is recoverable but the recorded path breaks reproducibility as
written. Locating the file is what allowed `start_time`, letterbox, `auto_speed`, `color` and
the scene-boundary claims to be verified rather than marked unverifiable.

**MAT-5. An 8.633333 s source region was excluded despite exceeding `min_duration 7.0`, and 3
filtered scenes must fit into only 2 unaccounted regions.**

Verified coverage: source frames 0–449, 500–748, 750–1199, 1200–1649 = **1,599 of 1,909 frames
(83.8 %)**, 55.0 s of 63.633333 s (86.4 %). Exactly **two** disjoint unaccounted regions:
frames 450–499 (50 frames, **1.666667 s**) and frames 1650–1908 (259 frames, **8.633333 s**),
totalling 10.30 s / 16.2 %.

The 8.633333 s tail is **1.633333 s above `min_duration 7.0`**, and `min_score` is 0.0, so no
stated parameter explains dropping it. And `scenes_filtered = 3` requires three filtered scenes
to occupy two regions, so at least one region must contain 2+ of them. Note also that the two
highest scdet scores in the entire source (**1.166** at t = 63.433333 and **1.706** at
t = 63.466667, ranks 2 and 1 of 1909) fall inside that excluded tail, in its final 0.2 s.

**MAT-6. `motion_energy` rank order is corroborated but its magnitudes are not a normalisation of
measured motion.**

| Clip | Mean scdet mafd (source active region) | Max-normalised measured | Claimed `motion_energy` | Δ |
|---|---|---|---|---|
| split_001 | 3.2506 | 100.00 | 100.0 | 0.00 |
| split_002 | 2.7098 | 83.36 | 96.1 | **−12.74 (−13.3 %)** |
| split_003 | 2.5797 | 79.36 | 79.9 | −0.54 (−0.7 %) |
| split_004 | 1.9114 | 58.80 | 77.7 | **−18.90 (−24.3 %)** |

> **MAGNITUDES WITHDRAWN 2026-07-27 — C54 killed 2/3.** The **rank order** survives and was
> reproduced twice independently, on two different metrics: mean scdet MAFD
> (2.0579 > 1.7497 > 1.6779 > 1.2971) and `tblend=all_mode=difference` → `signalstats` YAVG
> (7.2614 > 7.0357 > 6.4456 > 5.4642). Both are perfect Spearman matches to 100.0 / 96.1 /
> 79.9 / 77.7. The **magnitudes do not survive.** Neither skeptic reproduced the MAFD column
> above (one measured values 1.47–1.58× smaller — a *non-constant* ratio, so not a crop or
> units rescaling; the other ~2.2× smaller with a narrower spread), and their worst-divergence
> figures came out at **−18.9 %** and **11.1 %**, not −24.3 %. Because the two refutations
> disagree with each other as well as with this table, **no replacement number is asserted** —
> the honest statement is that the divergence is real, is largest at `split_004`, and is
> somewhere in the 11–24 % band depending on measurement surface. Root cause: no artifact ever
> recorded whether these MAFDs were taken on the proxy or the delivered clips, at 8 or 10 bit,
> cropped to the active region or full-frame. **Any MAFD figure must state its surface.**

Rank order is a **perfect Spearman match** (1/24 = 4.2 % by chance), so `motion_energy` does
track real motion. Two clips match closely and two are off by 13–24 %, so it is **monotonic in
motion but computed by a different, undocumented (probably flow-based) algorithm**.

**MAT-7. `start_time` / `end_time` are recorded at 2 decimal places, coarser than one frame
period.**

Frame period at 30 fps is 0.033333 s; 2 dp resolves only 0.01 s and rounds to values that are
not frame boundaries. `split_003_s66`'s true start is source frame 500 = 16.666667 s, written
as **16.67** — an error of **+0.003333 s (0.1 frame)**. This is **not merely cosmetic**: it is
the demonstrated cause of CON-1's 1-frame shortfall. Any consumer recomputing frame ranges from
these fields will reproduce the same off-by-one.

**MAT-8. Undocumented bit-depth reduction and colour-matrix retag.**

| | Source proxy | Split clips |
|---|---|---|
| pix_fmt | yuv420p10le (**10-bit**) | yuv420p (**8-bit**) |
| profile | High 10 | High |
| color_space | bt2020nc | bt709 |
| color_primaries / transfer | bt2020 / arib-std-b67 (HLG) | **absent / absent** |
| encoder | libx264 | h264_videotoolbox |
| bit_rate | 11,678,856 bps | 15,006,342 – 15,025,257 bps (**+28.6 %**) |

Neither the bit-depth halving nor the matrix retag is recorded in `split_params` or
`post_processing`, and MAT-2 shows the tag changed **without** a corresponding pixel conversion.

*(**CORRECTED 2026-07-27 — C58 killed 3/3, unanimous.** This paragraph formerly read: "the
source's own tagging is incomplete... the bt2020nc tag may itself be spurious. Both branches
are live and nothing in this pack settles it." That is withdrawn — missed by the first
remediation pass, which fixed the identical framing in `editorial_style.json` and `README.md`
but not here. The proxy's tag set is `color_space=bt2020nc` + `color_primaries=bt2020` +
`color_transfer=arib-std-b67` + `color_range=tv` over a **10-bit** `yuv420p10le` stream —
three agreeing fields over 10-bit, which is what a deliberate HLG encode looks like; a
spurious tag is normally a lone matrix field over 8-bit `yuv420p`. Absent mastering-display
metadata is expected on an HLG stream (that metadata is an HDR10/PQ container concept) and is
not corroborating weakness. So the spurious-tag horn is **weak**, not open on equal footing,
and the splits' `bt709` retag — which drops `color_primaries`/`color_transfer` entirely rather
than converting them — is correspondingly **more** plausibly a colour-management defect, not
less. The only genuinely open branch is whether the **camera original** behind this proxy
transcode was itself HLG/BT.2020. See `REVIEW.md` §5.1 group D for the fuller correction.)*
Encoding **28.6 % above** the source bitrate cannot recover information regardless.

#### COSMETIC (5) — real defects, but they do not change how the material reads

**COS-1. `motion_type: STATIC` on `split_004_s65` sits in tension with its measured frame-to-frame
change.** Its mean mafd over the source active region is **1.9114**, which is 58.8 % of the
highest-motion clip's 3.2506 — substantial change, not near zero. Stated with an explicit
caveat: the manifest nowhere defines STATIC, and it may mean "no dominant *directional* camera
motion" rather than "no change", in which case a high mafd is compatible with the label.
Direction requires optical flow, so this is **flagged as a tension to check against the tool's
source, not asserted as an error**.

**COS-2. `total_size_mb 95.4` is numerically right but the unit is mebibytes, not megabytes.**
100,027,790 bytes ÷ 1,048,576 = **95.3939 MiB** → rounds to 95.4 (Δ −0.0061, exact at the
stated precision). ÷ 1,000,000 = 100.0278 SI MB → Δ **+4.6278 (+4.85 %)**. The field agrees
only under a MiB reading, so the `mb` label is wrong by a factor of 1.048576.

**COS-3. `avg_score 68.1` versus a computed 68.05.** 272.2 / 4 = **68.05** exactly; manifest says
68.1, Δ **+0.05**. Consistent with half-up rounding — but note that Python's
`round(68.05, 1)` returns **68.0**, because 68.05 has no exact binary representation. So this
one value implies a rounding path different from whatever produced the rest of the document.

**COS-4. `resolution "source"` is true of the raster but conceals that 24.4 % of source rows were
discarded.** Raster delta is 0 px. But the letterbox is a centre crop — **C1** gives
`crop=1280:544:0:88` on every clip, the source cropdetects as `crop=1280:720:0:0`, and the SSIM
offset sweep peaks sharply at source row 88 (0.9707 vs 0.6806 / 0.7318 / 0.7318 / 0.6830 at
y = 84/86/90/92). **176 of 720 rows (24.4 %) of source picture were thrown away and replaced
with Y = 16 bars.**

**COS-5. `clips[]` array order is score-sorted, not timeline order, and the manifest never says
so.** `split_params.sort` is `"score"` and the array is strictly descending (70.0, 69.8, 66.8,
65.6) — internally consistent. But verified source order is split_004 (frame 0), split_003
(500), split_002 (750), split_001 (1200) — **exactly reversed**. A consumer iterating `clips[]`
in order gets reverse-chronological footage. Related trap: the filename suffixes s70/s69/s66/s65
are `int()` **truncations** of the scores, not roundings (69.8 → s69 would round to 70;
66.8 → s66 would round to 67) — self-consistent across all four, but anything parsing the score
back out of a filename will be wrong by up to 1.

---

## 5. Unverifiable in-session

57 raw entries were recorded across the run. Deduplicated and grouped, they reduce to **15
genuine knowledge gaps** (38 raw entries, grouped A-O below), **8 entries later resolved by
measurement**, **10 methodological notes** (which are not gaps at all), and **1 workflow
inference**. 38 + 8 + 10 + 1 = 57. *(Updated 2026-07-27, this session: one of group J's 2 raw
entries — "the camera original behind the proxy is absent" — moved from open to resolved; see
group J and §5.2. Formerly 39 + 7 + 10 + 1 = 57.)*

### 5.1 Genuine gaps — still open

| Group | What cannot be established | Raw entries | Tool that would be needed |
|---|---|---|---|
| **A. Camera-motion classification** | `motion_type` REVEAL / ORBIT_CW / STATIC for any clip. scdet's mafd gives motion **magnitude** only; separating a clockwise orbit from a reveal from a static hold needs per-pixel motion-vector direction and rotation estimation. No ffprobe/ffmpeg filter exposes flow direction. | 6 | **Optical flow** — `cv2` (Farnebäck / Lucas-Kanade) + `numpy`, or a dedicated camera-motion estimator |
| **B. Soft transitions inside a take** | Whether cross-dissolves, whip-pans or graphical wipes exist inside any single-shot file. A 0 hard-cut count cannot rule out gradual transitions, because a slow dissolve spreads its change across many frames and never trips a cut threshold. **Specifically unresolved: the 19-frame elevated run in `instagram_reel_v34_all_kb_full` at t = 0.77–1.40 s.** Its frame-locked twin cannot settle it, since a dissolve in the shared cut appears identically in both and does not disturb PSNR. | 3 | Sustained-elevation frame-differencing over a rolling window (buildable on ffmpeg output), or **frame inspection** (prohibited here) |
| **C. Colour interpretation of the untagged verticals** | What colour space, primaries and transfer the four vertical files' pixels actually are. All four declare **nothing** — the values are genuinely absent from bitstream and container, not merely unread. Any downstream BT.709 assumption is an inference. | 3 | The originating project/NLE, or camera metadata. ffprobe can only report absence |
| **D. Whether the proxy's `bt2020nc` tag is correct** | And therefore whether the splits' bt709 retag **without** chroma conversion is a colour-management defect or the correct handling of a spurious tag. Also whether the declared `drone_aerial` grade was applied *as specified* — with no ungraded SDR reference, the named grade cannot be separated from the HLG→SDR tone-mapping. *(**NARROWED 2026-07-27 — C58 killed 3/3.** The "spurious tag" horn is now much weaker. `probe/DJI_0355_proxy.json` — re-read this session — carries a **complete and mutually consistent HLG signalling set**, not one stray field: `color_space=bt2020nc`, `color_primaries=bt2020`, `color_transfer=arib-std-b67`, `color_range=tv`, `pix_fmt=yuv420p10le`. Three fields agreeing plus a 10-bit pixel format is what a deliberate HLG encode looks like; a spurious tag is normally a lone matrix field over an 8-bit `yuv420p` stream. The splits, by contrast, carry `color_space=bt709` with `color_primaries` and `color_transfer` **absent** — an incomplete set. So the **relative** tagging quality is settled on disk and favours the proxy. What remains genuinely open is narrower than the original framing: whether the camera original behind the proxy was itself HLG/BT.2020, which no file in reach can answer.)* *(**FURTHER RESOLVED 2026-07-27, this session, following C58 same day.** That narrowed residual question is now answered: the camera original was located — `DJI_20241029174803_0355_D.MP4`, pixel-matched against the proxy at 7 of 9 sampled timestamps (PSNR y 29–40 dB vs a same-pair floor of 15.5–19.6 dB, see §2.1a) — and it declares the identical HLG signalling set (`bt2020nc`/`bt2020`/`arib-std-b67`/`tv` over 10-bit `yuv420p10le`). Yes, confirmed by measurement: the camera original was itself HLG/BT.2020-tagged. What remains genuinely open, narrower still, is whether the `drone_aerial` grade was applied *as specified* — a separate question this new measurement does not touch. The "3" raw-entries count on this row was not recomputed for this narrowing, since the original three sub-questions do not map cleanly onto the post-C58 residual; treat that count as describing the pre-narrowing framing only.)* | 3 | The camera original behind the proxy, or the grading project |
| **E. Burned-in overlays, captions, logos** | Presence or absence in any file. **Unmeasured, but not unmeasurable.** *(**CORRECTED 2026-07-27 — C59 killed 3/3, unanimous.** The prohibition blocks frame *capture*, not frame *measurement*: region-wise MAFD/`signalstats`/`freezedetect` on crops can detect a static or animated overlay region entirely in-pipe. Not attempted here beyond a coarse 3×6 spatial-grid check on the two 1080p verticals, which found no zero-variance region — partial, not a clearance. What genuinely still needs a forbidden rendered frame is *identifying* an overlay's content, not detecting its presence. This is no longer linked to the verticals' motion envelope as "front-loaded" — that framing was itself killed, see group F.)* | 1 | **Region-wise in-pipe detection** — buildable now; **frame inspection** for identification — prohibited in this repo |
| **F. Cause of the verticals' elevated opening-second motion** | *(**CORRECTED 2026-07-27 — C56 killed 3/3, unanimous.** The original framing — "front-loaded envelope, decaying 6–61× from opening seconds to final third" — asserted a monotonic decay that isn't there: `instagram_reel_test`'s per-second maximum falls at t≈17.8s and `viral_test_v2`'s at t=14.1s, both outside the opening second, and the "6–61×" figure is undefined and metric-dependent (it collapses on MAFD; see §3.7). Only `instagram_reel_v34` and `viral_test_v2_4k` show any front-loading, and only as elevated frame-difference *range* in the first ~4s — not a decay rate.)* For those two files, whether that opening-seconds range is a decelerating camera move or animated overlay graphics remains open — **not** labelled a speed ramp. | 2 | **Optical flow** to separate global camera motion from local/overlay motion |
| **G. Every opaque manifest scalar** | `score` (70.0/69.8/66.8/65.6) and `motion_energy` exact magnitudes; `scene_threshold 7.0` as a *value* (incommensurable with scdet's 0–100 scale — plausibly a PySceneDetect `ContentDetector` threshold, but that is **not asserted**); `scenes_detected 7` / `scenes_filtered 3` as counts (the source's scene segmentation is not recoverable); `enhanced false`; `quality "high"` as a label→encoder-setting mapping; `min_score 0.0` (vacuous, nothing to verify against). *(**SCOPE CONFIRMED 2026-07-27 — C53 killed 2/3.** The killed claim listed `motion_energy` and `scene_threshold` **wholesale** as unverifiable. This row does not, and that difference is the whole kill: `motion_energy`'s **rank order** is reproducible with ffmpeg alone (MAT-6, perfect Spearman match, corroborated by all three skeptics on two independent metrics), and `scene_threshold`'s **scale** is measurably incommensurable with scdet's (MAT-7: max 1.706 over 1,909 frames, off-scale by 4×). Only the **exact magnitudes** and the **value** are opaque. One skeptic went further and showed the `STATIC` label on split_004 is partly testable without `cv2` — a 128-bin row-profile cross-correlation, null-controlled at exactly 0 net shift over 200 identical frames, drifts +0.626 bins/frame (~2.7 px/frame, net +281 bins over 449 frames). That result is **not** promoted into this table: it was produced once, is unreplicated, and row-profile drift cannot separate camera pan from subject motion — but it means group A's "no ffmpeg path exists" is too strong for the STATIC/non-STATIC distinction specifically.)* | 10 | **The source of the upstream splitting tool**, which is not present in this repo |
| **H. Absence of stabilisation, at sub-pixel scale** | `stabilize: false` is corroborated but **not provable in the strict sense**. The 1:1 frame correspondence at a fixed crop rectangle rules out any per-frame geometric warp large enough to register in SSIM, but a sub-pixel stabilisation would not be distinguishable at the 0.95–0.97 SSIM floor imposed by the grade and the 8-bit re-encode. | 2 | Sub-pixel frame registration (optical flow / phase correlation) |
| **I. Whether the 88 px bars are mathematically pure black** | `cropdetect=limit=24` proves only that bar luma sits *below* 24; full-frame YMIN measures 13–16, consistent with legal black. The bars are stated as "black below luma 24", **not** "pure black". | 2 | A **cropped `signalstats` pass over the bar rows** — feasible with ffmpeg alone and not yet run; or frame extraction (prohibited) |
| **J. Provenance above the pack** | The **source of the four vertical files is unknown** — `DJI_0355_proxy.mp4` was ruled out by measurement, but no parent for them exists in the tree searched, and nothing in `manifest.json` documents them. *(**NARROWED 2026-07-27, this session.** This row formerly also carried, as a second, separate claim: "the camera original behind the proxy is absent — the proxy's `Lavc62.11.100 libx264` tag makes it a transcode, so the real master's codec, resolution and bit depth are unknown." That half is **RESOLVED**, not open: the camera original was located at `DJI_20241029174803_0355_D.MP4` (same `.advanced/` directory as the proxy) and pixel-matched against it — PSNR y 29–40 dB at 7 of 9 sampled timestamps spanning the full duration, against a calibrated same-pair floor of 15.5–19.6 dB. Full measurement in §2.1a; moved to §5.2's resolved table. Raw-entries count below reduced 2→1 accordingly — the two original claims were textually distinct ("Separately, ...") so this split is a clean 1-for-1, not an estimate. Only the vertical-family-source question remains genuinely open here.)* | 1 | Access to the originating project/NLE, or a filesystem search wider than the one performed |
| **K. Render order within each rendition pair** | Not determinable from pixels — PSNR is near-symmetric for the viral pair: **34.640697 dB** (4K→1080, bicubic) vs **34.404432 dB** (1080→4K, bicubic), a 0.24 dB gap. *(Corrected 2026-07-27, C57 killed 3/3; the former 31.80 dB counterpart is unreproducible, and scaler choice alone moves the figure across 33.467–34.714 dB — a 1.25 dB spread, five times wider than the corrected 0.24 dB asymmetry. The 0.24 dB result makes this conclusion **stronger**, not weaker.)* mtime is suggestive only, and **for the reel pair it actively conflicts with the naming** (the `_v34` file is the *earlier* render, 2026-02-04; `_test` is later, 02-08). One skeptic further found the reel pair is **not a rendition pair in the pixel sense at all** — 24.267 dB mean downscale PSNR, with the first 81 frames at 19.4–21.3 dB, indistinguishable from a same-source wrong-offset null of 19.94 dB — i.e. frame-locked independent renders. **Unresolved and now wider than when opened.** | 1 | Project files / render logs |
| **L. Whether the verticals were upscaled from an unknown intermediate** | Only **partly** settled. The high-frequency test rules out the 4K being a *bicubic* upscale of the delivered 1080p, but it cannot rule out a sharper upscale (e.g. lanczos, plus grain and re-encode) from an unknown intermediate. | 1 | The originating project, or reference-quality upscale detection |
| **M. Which unaccounted region hosts the "filtered" scenes** | ~10.3 s of the 63.633 s proxy is unaccounted for — the 1.667 s gap between split_004's end and split_003's start, plus the 8.633 s tail after split_001. Presumed to be the 3 filtered scenes; **not verified**, and it does not fit (3 scenes, 2 regions — see MAT-5). | 1 | The splitting tool's scene list |
| **N. Decomposition of the SSIM residual** | The 0.03–0.05 residual (0.95–0.97 rather than ~1.0) cannot be split into its contributing causes — luma grade vs 10→8-bit reduction vs `h264_videotoolbox` re-encode. It **constrains** the processing chain but does not fully characterise it. | 1 | Controlled re-encode experiments against the source with each variable isolated |
| **O. Perceptual / aesthetic quality of anything** | Including whether the 3 frames flagged by a mean + 6σ threshold (t = 1.233333, 3.633333, 17.800000) correspond to anything a human would see. | 1 | **Human viewing** — frame extraction is prohibited here |

### 5.2 Recorded as unverifiable earlier in the run, then RESOLVED by measurement (8)

Kept visible rather than deleted, because they show what changed the answer:

| Originally unverifiable | Resolved by | Outcome |
|---|---|---|
| Whether letterbox bars are baked into the pixels (verticals) | **C1** `cropdetect` on the verticals | Resolved: `crop=1080:1920:0:0` (811 reports) and `crop=2160:3840:0:0` (298 reports) — **no bars** |
| Whether letterbox bars are baked in (splits), and whether `"2.35"` conflicts with a 16:9 frame | **C1** + per-row `signalstats` + SSIM offset sweep | Resolved: bars are real, `crop=1280:544:0:88`, and the claim is **not** a defect (§3.5) |
| Whether the reel pair share content (flagged only from equal CSV byte sizes) | Per-frame PSNR across all 813 frames | Resolved: frame-locked, min 19.08 dB, zero frames below 18. **Not** resolved as a uniform grade — see §1.3, corrected 2026-07-27: divergence is step-changing and concentrated in the first ~40% of the timeline |
| Whether `viral_test_v2` and `viral_test_v2_4k` share source footage | **S2** PSNR + YAVG correlation | Resolved: r = +0.99987, PSNR y 34.64 dB |
| `instagram_reel_test`'s "no hard cuts" conclusion (originally sampled at 6 frames only) | Full recount of all 813 CSV rows | Resolved: max 1.547, **0 frames ≥ 5.0** |
| `auto_speed: true` — "requires the ungraded source, which does not exist on this machine" | **Locating the proxy in `_archive/`** | Resolved: measurable no-op (MAT-1) |
| `color: "drone_aerial"` — same reason | Same | Resolved: luma-only change (MAT-2) |
| **(ADDED 2026-07-27, this session)** Group J's "camera original behind the proxy is absent" — the proxy's `Lavc62.11.100 libx264` tag makes it a transcode, so the real master's codec/resolution/bit depth were unknown | **Locating `DJI_20241029174803_0355_D.MP4`** in the same `.advanced/` directory + lag-swept PSNR/SSIM against the proxy | Resolved: CONFIRMED, high confidence — PSNR y 29–40 dB at 7 of 9 sampled timestamps vs a 15.5–19.6 dB same-pair floor (§2.1a). Also settles group D's residual HLG/BT.2020 question (identical colour tags). Two sub-details remain open: the ~50–67 ms constant timing offset, and the exact frame-index decimation formula |

The `auto_speed`/`color` rows and the new camera-original row all flipped for the same
underlying reason: **the source was found**. That is the strongest argument in this document
for keeping `_archive/` intact — three separate resolutions now trace to it.

### 5.3 Methodological notes — not knowledge gaps (10)

Recorded here because they are reproducibility hazards for anyone re-running this work:

1. **Tooling defect — the scdet recipe.** `-show_entries frame=pts_time,frame_tags=lavfi.scd.score`
   uses a **COMMA** where ffprobe 8.1 requires a **COLON** between section specifiers. With the
   comma, ffprobe treats `frame_tags=…` as a nonexistent field of the frame section, emits
   `pts_time` only, **exits 0**, and prints no warning — so it looks like a successful run that
   found no scene activity. A first pass produced 450 lines containing exactly one comma in the
   whole file. **Correct form:** `-show_entries "frame=pts_time:frame_tags=lavfi.scd.score"`.
   Cross-checked: `ffmpeg -vf scdet=threshold=0,metadata=print` yields identical values
   (`split_001` frame 1 = 2.668 by both paths). All eight stored CSVs escaped this bug — every
   one has a numeric score on every row (813/813, 813/813, 450/450, 450/450, 249/249, 450/450,
   437/437, 437/437).
2. **Tooling defect — the select/metadata recipe.** `select='gt(scene,0.3)',metadata=print`
   with `-loglevel error` is **inert**: `metadata=print` writes at INFO level, which
   `-loglevel error` discards, so it emits nothing **unconditionally**. Demonstrated with a
   positive control — at `gt(scene,0.01)`, which truly matches 94 frames in `viral_test_v2.mp4`,
   the documented form still printed nothing; and on a synthetic clip with two guaranteed hard
   cuts it still printed nothing, because `select` attaches no frame metadata for
   `metadata=print` to print. **Its silence is therefore not a valid negative result.** Working
   substitutes: `select='gt(scene,0.3)',showinfo` (command **X1**), which correctly reported the
   control's cuts at t = 1 and t = 2 and reported 0 frames for all four split files; or
   `metadata=print:file=-`.
3. **Percentile convention.** p90/p99 differences between passes (e.g. `instagram_reel_test`
   p99 quoted variously as 1.104, 1.133, 1.137) are a **nearest-rank vs linear-interpolation**
   difference on adjacent tail samples, **not a data disagreement** — min, p50 and max reproduce
   exactly. Cut counts are threshold-based and unaffected.
4. **File count.** The brief said "9 files"; the media directory holds exactly 9 entries — **8
   `.mp4` files plus `manifest.json`**. A 10th file, `DJI_0355_proxy.mp4`, was measured from
   outside that directory as read-only evidence.
5. **No git verification.** `.git` is corrupt (no objects/refs/index) and **no git command was
   run**. Verification was tool-grounded by other means: `python3 -m json.tool` validated the
   probe JSONs, `wc -l` confirmed row counts, and `ffprobe -count_frames` independently
   confirmed frame counts.
6. **No frames written.** No image or frame file was written anywhere in this repo. The one
   synthetic positive-control clip was built under `/private/tmp` and deleted after use
   (deletion verified).
7. **Source media untouched.** All `00-assets/` mtimes remain Feb/Mar 2026 as listed in §1,
   confirming the read-only asset directory was not modified.
8. **Probe filename inconsistency.** The four `split_*.json` store a bare basename in
   `format.filename` while the verticals store an absolute path (§1).
9. **scdet frame-1 warm-up.** The first scored frame of every file is inflated because
   `prev_mafd` is still 0. Three files' *global* maxima are this artefact (§3.1). Any consumer
   reading `max(scd.score)` naively will overstate activity in `split_001/002/003` by 4–12×.
10. **`nb_frames` vs `-count_frames`.** Header frame counts were independently confirmed with
    **P3** rather than trusted; they agree on every file checked.

### 5.4 Workflow inference, not measurement (1)

The **absence** of an audio stream is verified on all 8 files plus the proxy. Whether an audio
bed was *intended* and is meant to be added downstream is an inference about workflow, **not a
measurement**.

---

## 6. Tooling state, and what it bounds

**`.venv/` is an empty husk.** `ls -la .venv/` shows exactly one entry — `pyvenv.cfg`, 96
bytes, mtime 2026-07-06. There is no `bin/`, no `lib/`, no `site-packages/`. It cannot be
activated and nothing is installed in it.

**System `python3` has none of the video-analysis stack:**

```
python3 -c "import cv2"          -> ModuleNotFoundError: No module named 'cv2'
python3 -c "import numpy"        -> ModuleNotFoundError: No module named 'numpy'
python3 -c "import scenedetect"  -> ModuleNotFoundError: No module named 'scenedetect'
```

Installing anything was prohibited for this work, and nothing was installed. Every number in
this document was produced by:

- **`ffprobe 8.1`** and **`ffmpeg`** (same build) at `/opt/homebrew/bin`, and
- **Python 3 standard library only** — `json`, `statistics`, `subprocess`, `hashlib`, `csv`.

### What that toolchain establishes well

- Container, codec, profile/level, bitrate, resolution, frame count, frame rate and CFR/VFR
  status — exactly, from the bitstream.
- Colour **tagging** — exactly, including the important negative result that four files carry
  no tags at all.
- Frame-difference magnitude per frame (`scdet`), which is sufficient to prove the absence of
  hard cuts to a wide margin against a calibrated positive control.
- Active-picture geometry (`cropdetect`) and per-frame tone statistics (`signalstats`).
- Frame-for-frame similarity between two files (`ssim`, `psnr`) — strong enough to establish
  frame-lock, source offsets to the frame, and to rule out speed ramping.
- Duplicate-frame detection (`mpdecimate`).

### What it cannot reach — the hard boundary

**Everything requiring per-pixel motion direction.** `scdet` returns a *scalar magnitude* per
frame. It cannot distinguish a clockwise orbit from a reveal from a static hold, cannot
separate global camera motion from local subject or overlay motion, and cannot detect sub-pixel
stabilisation. That single limitation is why groups **A**, **F** and **H** of §5.1 — six raw
entries about `motion_type`, two about the front-loaded envelope, two about stabilisation —
remain open. All three would fall to `cv2` + `numpy` optical flow.

**Everything requiring visual inspection.** Overlay/caption detection (group E) and perceptual
quality (group O) need a human or a vision model looking at frames. Writing frame captures is
prohibited in this repo on licensing grounds, so these are out of reach here regardless of
tooling.

**Everything defined by the upstream tool.** `score`, `motion_energy`, `scene_threshold`'s
scale, `enhanced`, and the `quality` label mapping (group G, ten raw entries) are defined by
code that is not in this repo. No measurement can recover them; only the tool's source can.

**Consequence for the pack.** This measurement basis is sufficient to characterise the pack's
**format, geometry, grading envelope, provenance and edit grammar** with high confidence, and
sufficient to falsify five of the manifest's processing claims. It is **not** sufficient to
characterise **camera movement**, which is precisely the axis a drone-video style reference
would most want. Anyone extending this pack toward motion vocabulary must add optical flow
first, and should treat every `motion_type` string in `manifest.json` as unaudited.

---

## Verification outcomes

**Status: verification COMPLETE. All 3 of 3 skeptic lenses reported.** No lens timed out, no
lens returned partial. Every one of the 62 claims in the claim set carries three independent
votes, so no claim survived by default or by non-response — this is the condition that makes
the 54 survivors meaningful rather than merely unchallenged.

**Result: 62 claims → 54 survived, 8 killed by majority refute (≥2 of 3).**

Killed does **not** mean deleted. Nothing was silently removed. Every kill below is recorded
with its reason, the correction the skeptics established, and the artifact edit that applied
it. In four of the eight cases the killed claim's *conclusion* survived and only its *number*
or its *scope* was wrong — those are marked so no reader mistakes a magnitude correction for a
reversal.

### 7.1 The eight kills

| Claim | Vote | What was asserted | Why it died | What replaced it | Artifact fixed |
|---|---|---|---|---|---|
| **C24** | 2/3 refute | The four split clips' provenance is known, with *three of four* frame-exact and split_003 starting one frame late at proxy frame **501** / 16.700 s | Both refuting skeptics independently resolved the alignment to **frame 500** by pixel PSNR, and both showed the "501" figure was an artefact of the metric that produced it — a **raw mean-luma** correlation whose top five lags span only r = 0.99423–0.99706. A 0.0008 spread cannot resolve one frame. Delta-YAVG (first-difference) correlation instead peaks sharply and uniquely at 0/500/750/1200 (r = 0.9856/0.9874/0.9908/0.9252) | **All four clips are frame-exact** at `floor(start_time × 30)` = proxy frames 0 / 500 / 750 / 1200. split_003's 1-frame deficit is at the **END** of its range (it covers frames 500–748, not 500–749), not a late start | `REVIEW.md` §1 row + §3, `reference_pack.json` → `files[].provenance_note` (split_003_s66) and `→ cross_reference.disagreement_explanation` (split_003_s66) — all three annotated "CORRECTED 2026-07-27" (line numbers not cited: they drift as the file is edited; grep for `claim C24 killed` to locate both) |
| **C43** | 2/3 refute | `src/`, `tests/`, `plan.md` and any prior `spec.md` are absent, and **only** `pyproject.toml` and `.gitignore` survived | The absences are all confirmed — that half stands. The universal does not: `.pytest_cache/` also survived at the repo root, and `.claude/specs/reference-pack/spec.md` was **already present** when the claim was recorded (written 09:42, claim logged 11:18), so the cited ABSENT probe was stale | `pyproject.toml` and `.gitignore` are the only surviving **project-specific authority documents**. `.pytest_cache/` exists but holds no `nodeids` and no `lastfailed`, so it proves a test run happened and nothing more. The rest of the root is inherited `claude-template` content that `.gitignore` lines 3–19 disclaim | `.claude/specs/reference-pack/spec.md` §Open Questions Q2 — corrected block added; **conclusion unchanged** |
| **C53** | 2/3 refute | `motion_type`, `score`, **`motion_energy`**, **`scene_threshold`**, `enhanced` and the `quality` mapping are all unverifiable in-session | The list was too broad and **self-contradicting**: C54 in the same set verifies `motion_energy`'s rank order, and C38 in the same set measures `scene_threshold`'s scale. A claim set cannot both verify a quantity and list it as unverifiable | Genuinely opaque: `motion_type` **direction** labels, `score`, `enhanced`, `quality`'s label→bitrate mapping, and `motion_energy`'s **exact magnitudes**. Not opaque: `motion_energy` rank order, `scene_threshold` scale | `REVIEW.md` §5.1 group **G** — scope note added. Group G was already correctly narrow; the *claim* was the broad one |
| **C54** | 2/3 refute | `motion_energy` rank order corroborated; magnitudes diverge by up to **−24.3 %** | Rank order was confirmed by both refuters on two *different* metrics (mean scdet MAFD, and `tblend=difference`→`signalstats` YAVG) — a stronger result than claimed. The magnitude failed: the cited MAFDs 3.2506/2.7098/2.5797/1.9114 reproduced at neither skeptic (one got 2.0579/1.7497/1.6779/1.2971, the other 7.2614/7.0357/6.4456/5.4642), and the ratio between passes is **non-constant** (1.47–1.58×), so it is not a crop or units rescaling | **Rank order: perfect Spearman match, confirmed three ways.** Magnitude divergence is **metric- and surface-dependent** — −18.9 % on cropped-source scdet MAFD, 11.1 % on proxy full-frame 8-bit MAFD. The single figure "−24.3 %" is withdrawn. **Any MAFD number in this pack must state its measurement surface** (proxy vs delivered, cropped vs full, 8- vs 10-bit) | `REVIEW.md` §4 row 17 and MAT-6 §825 — magnitudes withdrawn, rank order retained |
| **C56** | **3/3 refute — unanimous** | The verticals' motion envelope is front-loaded, decaying **13–61×** per second | Every refuter falsified both halves. **Shape**: the envelope is not monotonic — `instagram_reel_test` peaks at **second 17**, `viral_test_v2` at **t = 14.100 s**, the last second of a 14.567 s file. **Number**: the metric behind "13–61×" is defined nowhere, and three attempted reconstructions gave three different answers (33.3/60.7/13.1/6.3; 1.1/2.6/9.7/2.8; 59.4/84.0/11.8/9.0). The claim was also internally inconsistent — its own cited 6.3× falls outside its stated 13–61× band | The effect is **metric-dependent and does not survive on MAFD**. Only `instagram_reel_v34` and `viral_test_v2_4k` are front-loaded at all | **Already correct in JSON, stale in prose.** `editorial_style.json` had set `front_loaded_motion_envelope: null` and `front_loaded_motion_parameter: null` **before** verification; `REVIEW.md:605–606` was the stale copy and is now marked WITHDRAWN |
| **C57** | **3/3 refute — unanimous** | PSNR is near-symmetric between rendition-pair members — **34.64 dB** one way, **31.80 dB** the other | 34.64 dB reproduced *exactly* at two skeptics (34.640697). **31.80 dB reproduced nowhere**, under any of five scalers swept (bicubic 34.404, lanczos 34.300, bilinear 34.714, neighbor 33.467). The claim was also self-defeating: a 2.84 dB gap is not "near-symmetric" | With bicubic both ways: **34.640697 dB** (4K→1080) vs **34.404432 dB** (1080→4K) — a **0.24 dB** gap. The conclusion that neither file is identifiable as the render source is therefore **stronger** than claimed, not weaker. **Scaler choice moves the figure by ~1.25 dB, five times wider than the corrected 0.24 dB asymmetry — no PSNR figure in this pack is meaningful without naming its scaler** | `REVIEW.md:178`, `:183–185`, `:932`; `reference_pack.json:837` — annotated "PARTIALLY CORRECTED 2026-07-27" |
| **C58** | **3/3 refute — unanimous** | Whether the proxy's `bt2020nc` tag is correct — and hence whether the splits' bt709 retag is a defect — is undecidable here | The dispute is partly settled on disk and the claim declined to look. `probe/DJI_0355_proxy.json` carries a **complete, mutually consistent HLG signalling set** | `color_space=bt2020nc` + `color_primaries=bt2020` + `color_transfer=arib-std-b67` + `color_range=tv` + `pix_fmt=yuv420p10le` — three agreeing fields over a 10-bit pixel format is a deliberate HLG encode, not a stray tag. The splits carry `bt709` with primaries and transfer **absent** — an *incomplete* set. Relative tagging quality favours the proxy; only the **camera original's** true colourimetry stays open | `REVIEW.md` §5.1 group **D** — NARROWED, scope reduced rather than deleted |
| **C59** | **3/3 refute — unanimous** | Presence of burned-in captions, logos or graphic overlays in any file is **unmeasured and unmeasurable** in this environment — it needs frame inspection, which the no-persisted-frames prohibition forbids | All three refuters made the same distinction: the prohibition blocks frame **capture**, not frame **measurement**. Region-wise MAFD, `signalstats`, and `freezedetect` on crops all run entirely in-pipe (`ffmpeg ... -f null -`, nothing written to disk) and can detect a static or animated overlay region without ever persisting an image. One refuter ran a coarse 3×6 spatial-grid temporal-variance check on the two 1080p verticals and found no zero-variance region | **"Unmeasurable" → "unidentified."** *Detecting* overlay presence is available and was not attempted (beyond the coarse grid check, which is partial, not a clearance). *Identifying* what an overlay says or looks like still genuinely needs a rendered frame and stays forbidden | `REVIEW.md` §5.1 group E, `README.md` §"Not verifiable with this toolchain", `spec.md` OQ10, `editorial_style.json → open_questions[7]` — all four annotated "CORRECTED 2026-07-27" |

> **Note on how the 8th kill was recovered.** The agent that wrote this section was itself cut
> off mid-stream before recording C59's identity, and initially shipped this row as "NOT
> RECOVERABLE," reasoning from a deliberately truncated 12,000-character slice of the
> verification handoff that happened to end inside C58's text. The full, untruncated verdict set
> — all 62 claims × 3 skeptics — survived independently in the orchestrating session's own
> record and was used to fill this row in directly. No claim was guessed: C59's kill (3/3,
> unanimous) and its three skeptics' corrections are quoted verbatim from that record. This
> means the "4 claims unverified" framing in §7.1's introduction and §7.3 finding 2 below is
> itself now stale — **all 62 claims have a recorded verdict; 8 killed, 54 survived, 0 unknown.**

### 7.2 What the skeptics established beyond the kills

Five results that no claim in the set had asked for, and that survive as findings in their own
right:

1. **The Instagram reel pair is not a rendition pair in the pixel sense.** One skeptic measured
   24.267 dB mean downscale PSNR between `instagram_reel_v34_all_kb_full` and
   `instagram_reel_test`, with the first 81 frames at 19.4–21.3 dB — indistinguishable from a
   same-source wrong-offset null of 19.94 dB. **Independently reproduced while writing this
   section**: over the first 10 s, `[4K bicubic→1080] vs [1080]` gives **PSNR y 19.204 dB** for
   the reel pair against **32.017 dB** for the viral pair, a **12.8 dB** gap on identical
   method. The two reel files are **frame-locked but pixel-divergent** — the same cut rendered
   twice with different grade or overlay content, not one render at two resolutions. The viral
   pair *is* a true rendition pair. **This distinction was never a claim and never an open
   question.** See §7.3 finding 3.
2. **`motion_type STATIC` is partly testable without `cv2`.** A 128-bin row-profile
   cross-correlation, null-controlled at exactly 0 net shift over 200 identical frames, shows
   split_004 — declared `STATIC` — drifting **+0.626 bins/frame (~2.7 px/frame, net +281 bins
   over 449 frames)**. Recorded in §5.1 group G as a caveat, **not** promoted to a finding: it
   is unreplicated, and row-profile drift cannot separate camera pan from subject motion.
3. **Measurement surface is load-bearing and was under-specified throughout.** Three skeptics
   computing "mean MAFD" over the same four clips got three answer sets differing by up to
   2.2×, purely from proxy-vs-delivered, cropped-vs-full and 8-vs-10-bit choices. Every MAFD
   and PSNR figure in this pack now states its surface; any that does not should be distrusted.
4. **The `_v34` / `_test` naming conflicts with mtime.** `instagram_reel_v34_all_kb_full` is
   the **earlier** render (2026-02-04 14:32); `instagram_reel_test` is **later** (2026-02-08
   17:42). Confirmed by two skeptics and re-confirmed here by `ls`. A file named `_test` that
   post-dates the file named `_v34` inverts the obvious reading of both names.
5. **Two claims in the set contradicted each other** (C53 vs C54, and C53 vs C38). This is a
   defect in claim *construction*, not in measurement — a claim set should be checked for
   internal consistency before it is put to a verification pass, and this one was not.

### 7.3 Completeness audit

Seven checks run against the finished pack. Findings are ordered most serious first.

**1. Source media integrity — PASS, no mismatch.** All 9 files in
`00-assets/drone-video-examples/` re-hashed with `shasum -a 256` against the baseline: **9 of 9
match exactly**. mtimes remain Feb/Mar 2026. `DJI_0355_proxy.mp4` in `_archive/` is 92,905,225
bytes with mtime **2026-03-15 17:00**, matching the size recorded at discovery; its sha256 is
`8e0a610f6a00fd140af9a58327706c3738b25a51fbf18565d42270a1171c28cc`. *Caveat stated honestly:
no pre-session hash of the proxy was ever taken, so its integrity rests on size + mtime, which
is weaker evidence than the 9 files have. Anyone re-running this work should hash the proxy
**before** first use.*

**2. RESOLVED 2026-07-27, after this section was first written.** The 8th kill was recovered
from the orchestrating session's untruncated verdict record and is `C59` — see §7.1's `C59`
row. All 62 claims now carry a recorded verdict (8 killed, 54 survived, 0 unknown); nothing in
`C60`–`C62` needed reclassifying, they were correctly recorded as survivors throughout. This is
no longer an open item.

**3. An entire artifact section went through the claim set unverified: `delivery_surfaces`.**
`editorial_style.json → delivery_surfaces` and the corresponding `reference_pack.json` blocks
assert, all at `confidence: "measured"`, a full delivery ladder: resolutions (1080×1920 and
2160×3840), aspect (9:16), fps (30/1), CFR status, observed durations, and **per-file video
bitrates spanning 13,435,909 – 75,890,986 bit/s**. Searching all 62 claims for `bit_rate`,
`bitrate`, `Mbps`, `2160`, `3840`, `1080x1920`, `9:16`, `aspect` and `delivery` returns **no
claim covering resolution, aspect ratio, or the bitrate ladder**. The numbers are correct — all
re-checked against `probe/*.json` this session and they agree — but they received **zero
adversarial votes**. The bitrate ladder is the single most likely value in this pack to be
consumed as a production setting, and it is the least tested thing in it.

Two smaller instances of the same failure:
- The **high-frequency / Laplacian energy ratio** (1.57× vs 1.72×, native 4K vs bicubic-upscaled
  1080) is used in §5.1 group L to rule out the 4K being an upscale, but was never entered as a
  claim. `reference_pack.json:837` flags this itself.
- **OQ3's supporting numbers** — split_004 mean MAFD 1.7130, 63.0 % of family maximum — appear
  in `editorial_style.json` and in no claim.

**4. The Open Question that should have been asked and was not: audio.** Every one of the 8
files, plus the proxy, has **zero audio streams** (`nb_streams = 1`, sole stream
`codec_type=video`) — measured, undisputed, and recorded under `editorial_style.json → audio`.
§5.4 of this document then explicitly states that *whether an audio bed was intended and is
meant to be added downstream* is **"an inference about workflow, not a measurement"** — which
is the definition of an open question. **It was diagnosed as unresolvable and then never
promoted into `open_questions[]`.** Searching all 13 open questions for "audio" returns
**zero**. This matters more than any other omission on this list: the corpus is four
social-vertical deliverables for **audio-first surfaces** (Reels, TikTok), where the cut is
normally timed to the track. A downstream consumer reading this pack as house style will find
13 questions about colour, motion and aspect ratio, and no acknowledgement that the single
largest structural absence in the corpus was never explained.

**Runner-up:** no open question asked **what the relationship between `instagram_reel_test` and
`instagram_reel_v34_all_kb_full` actually is**, now that §7.2 finding 1 has shown they are
frame-locked but pixel-divergent at 19.2 dB. That result reached §5.1 group K as prose but was
never promoted to `open_questions[]`, so `editorial_style.json` — the machine-readable artifact
— did not carry it at all.

> **Both were added, 2026-07-27.** `editorial_style.json → open_questions[]` now holds **15**
> entries, not 13: **OQ14** (audio absence — three incompatible readings the corpus cannot
> separate) and **OQ15** (the reel pair is not a rendition pair; do not use it as evidence for
> a resolution ladder). An open question records ignorance rather than asserting a value, so
> adding one cannot introduce an unmeasured constant — every figure quoted inside OQ15 was
> measured in this session and is reproduced in §7.2. The 13 pre-existing questions are
> unchanged and unrenumbered.
>
> **Disclosure — whole-file reformat.** Writing those two entries re-serialised
> `editorial_style.json` at a uniform `indent=2`, expanding leaf objects that were previously
> inlined on one line. The file grew 58,798 → 67,552 bytes. **The change is presentational
> only and was verified lossless**: it still parses under `python3 -m json.tool`, still has the
> same **14** top-level keys in the same order, and spot-checked values are byte-identical
> (e.g. `delivery_surfaces[0].video_bitrate_bps.value` = `{instagram_reel_test.mp4: 14096352,
> viral_test_v2.mp4: 13435909}`). It now matches the serialisation `reference_pack.json`
> already used. Flagged because a reviewer diffing this file will see the whole document
> change for a two-item addition, and should not read that as a rewrite.

**5. Raw `ffprobe` output retention — PASS, and better than required.** `probe/` holds **9**
`.json` files, not 8: all 8 corpus media plus `DJI_0355_proxy.json`. Checked file by file, all
9 parse under `python3 -m json.tool` (exit 0) and each contains a `streams` array and a
`format` object. Matching per-frame `.scd.csv` scene scores exist for all 9. Nothing is
missing.

**6. Artifact parse check — PASS, both.** `python3 -m json.tool` exits 0 on
`data/reference_pack/editorial_style.json` (58,798 bytes, 14 top-level keys) and on
`data/manifests/reference_pack.json` (54,882 bytes). Neither emitted any diagnostic; the
absence of output *is* the pass condition for `json.tool`.

### 7.4 Independent review pass (2026-07-27, second model family)

After §7.1–7.3 were written, an independent five-lens review (cross-document consistency,
kill-propagation audit, extra-problems disposition, evidence traceability, reader-facing
quality) ran on a second model family, with every critical/major finding adversarially
re-verified before acceptance. **Coverage was partial — the propagation and reader lenses
completed; the other three stalled** — but of the findings reported, 9 critical/major were
confirmed, 4 minor/nit noted, and **0 refuted**. All 13 were then fixed in place. The
substantive ones:

- **Killed-claim residue found at 4 more sites** and corrected: §4 row 17 still asserted
  C54's withdrawn MAFD column and "−24.3 %" bare; §1.3 still called `viral_test_v2`
  "consistent with the front-loaded motion envelope" (C56's own counterexample file);
  `editorial_style.json` carried C58's killed "may be spurious / both branches live" framing
  at two sites; and a C57 header in §1.4 was attached to the (never-adjudicated) Laplacian
  note instead of the PSNR paragraph it belongs to.
- **One correction annotation had inverted its verdict's implication** (README, C58): it
  concluded the splits' bt709 retag was *less* likely a defect, when weakening the
  spurious-tag reading makes the unconverted retag *more* plausibly one. Reworded here,
  in README, and in `editorial_style.json`.
- **A false numeric comparison in the C57 annotations** ("sweep span wider than the
  asymmetry it was cited to prove" — 1.25 dB is wider only than the corrected 0.24 dB, not
  the withdrawn 2.84 dB) fixed at three sites.
- **Corpus-count drift**: README and spec AC1/AC3 still described 8 probe pairs and 16
  files after the `DJI_0355_proxy` pair (1909/1909) made it 9 and 18 — spec amended
  (divergence-amends-spec-first), README layout/table/recipes updated, including a new
  recipe 2b for the proxy pair.
- **Environment drift, independently reproduced**: a homebrew x265 4.1→4.2 upgrade had
  broken every ffmpeg/ffprobe recipe on this machine (`dyld` abort on the deleted
  `libx265.215.dylib`) — AC11 failed through no fault of the artifacts. Repaired via
  `brew reinstall ffmpeg` (now 8.1.2; all pack measurements were made under 8.1), and both
  README and spec AC11 now carry the fragility warning.
- Also: manifest `entry_contract` gained its two undocumented sidecar-only fields; the
  "uniform PSNR" characterisation of the reel pair was corrected to frame-locked-but-
  step-changing; spec AC9's unattributed `12.481161 dB` constant was replaced by a
  named-method requirement; spec OQ3's ranks were relabelled `scdet` score (they were
  mislabelled "frame difference"); the colour-measurement control (8-bit-reduction
  baseline, `crop=1280:544:0:88`, 450 frames) is now stated where the percentages appear;
  and the manifest toolchain block records both tool versions.

The three stalled lenses (full cross-document sweep, full 30-item disposition audit, full
traceability recompute) have **not** run to completion against the corrected artifacts —
the items above cover what their partial output and the §7.1–7.3 records identified, but a
clean full-sweep bill of health has not been issued and should not be inferred.

**7. Write-scope and no-frames prohibitions — PASS, both.** Every file created or modified for
this work lives under `data/` (`data/reference_pack/{README.md, REVIEW.md, editorial_style.json,
probe/, media/}` and `data/manifests/reference_pack.json`) or under
`.claude/specs/reference-pack/spec.md`. A repo-wide `find` for `.png .jpg .jpeg .bmp .ppm .pgm
.tif .tiff .webp .gif` returns **exactly one** hit — `site/assets/images/`, pre-existing MkDocs
build output, untouched. **Zero persisted frame captures anywhere in the repo.**
`data/reference_pack/media/` contains only `.gitkeep`. The only files modified outside `data/`
in the whole window are the `.claude/hookify.*`, `.claude/router.md` and `.claude/settings.json`
files, all with mtime **2026-07-25 19:22:42** — a template sync that predates this work by a
day and was not performed by it. No git command was run at any point; `.git` remains corrupt
and untouched.

---

## 8. Cross-validation across 7 manifest parameter regimes (2026-07-27, this session)

The original manifest reconciliation (§4) tested this pack's four headline findings —
**auto_speed is a measurable no-op**, **the named colour grade is luma-only/chroma-inert**,
**`scene_threshold` is incommensurable with `scdet`'s scale**, **clip boundaries are not
reliably content-derived** — against exactly one `manifest.json`, one set of `split_params`,
one source file. That is N=1. `.drone_clips/.advanced/` holds 7 more manifests, each run
with genuinely different parameters, three against the **raw camera master** rather than the
proxy. Reconciling all 7 turns those four findings from a single anecdote into a
cross-validated result — or exposes them as parameter-specific artifacts. They are not
artifacts.

**Reconciliation method** matched §4 exactly: every manifest read in full, every clip's
claimed duration/start/end checked against this session's ffprobe/scdet measurement of the
delivered file, every summary field checked for internal arithmetic consistency. One
manifest (`highlights_long`) was reconciled directly in this pass; the other six were
reconciled and independently recorded before an unrelated infrastructure failure interrupted
that run's own final write-up — their findings are reproduced here from that recorded
detail, not re-derived, and are flagged as such below.

### 8.1 Manifest parameter regimes compared

| Manifest | Source | `min_duration`/`max_duration` | `scene_threshold` | `color_intensity` | `stabilize` | `letterbox` | `auto_speed` key present? |
|---|---|---|---|---|---|---|---|
| original (§4) | proxy | 7.0 / 15.0 | 7.0 | 0.65 | false | "2.35" | yes |
| `highlights_best` | proxy | 5.0 / 15.0 | 5.0 | 0.65 | false | "2.35" | no |
| `highlights_graded_varied` | proxy | 10.0 / 40.0 | 20.0 | 0.6 | true | null | no |
| `highlights` | raw master | 2.0 / 15.0 | n/a (`min_score` instead) | n/a | n/a | n/a | no (schema has no post_processing at all) |
| `highlights_graded_25s` | **raw master** | 2.0 / 25.0 | 50.0 | 0.6 | true | null | no |
| `highlights_graded` | proxy | 2.0 / 15.0 | 20.0 | 0.6 | true | null | no |
| `highlights_5_22s` | **raw master** | 5.0 / 22.0 | 8.0 | 0.6 | true | null | no |
| `highlights_long` | proxy | 11.0 / 17.0 | 7.0 | 0.65 | false | "2.35" | no |

No two manifests share an identical parameter set, and 3 of the 7 were run directly against
the raw ~59.94fps 4K HEVC master rather than the 30fps proxy the original manifest and 4 of
the 7 archive manifests use — a genuinely different generation pathway, not just different
numbers into the same one.

### 8.2 Do the four original findings generalize?

**auto_speed is a measurable no-op — UNTESTABLE beyond the original manifest, not
re-confirmed.** The `auto_speed` key is **absent** from `split_params` in all 7 archive
manifests, and from every clip's `post_processing` block in 5 of them (`highlights` and
`highlights_graded_25s` have no `post_processing` block at all). This is not a
generalization failure — the parameter simply was not exercised again — but it means the
original manifest's `auto_speed` no-op finding rests on N=1 and stays there. Worth noting for
anyone treating it as house-wide: it isn't, yet.

**The named colour grade is luma-only/chroma-inert — GENERALIZES, with one real nuance.**
Every archive manifest that declares `color: "drone_aerial"` (6 of 7; `highlights` declares
no colour parameters at all) reproduces the chroma-inert signature: `signalstats` UAVG/VAVG/
SATAVG stay at or within measurement noise while luma shifts materially — the same MAT-2
pattern from the original manifest. The nuance: `highlights_graded`'s measured luma
**direction is the opposite sign** of the original manifest's (a lift where the original
showed compression), and `highlights_graded_25s`'s luma reduction is **stronger** (−11.0%)
than the original's (−8.25%) despite a **lower** stated `color_intensity` (0.6 vs 0.65). So
"luma-only" generalizes as a **category** (no chroma effect, ever) but the specific luma
curve is source- or run-generation-specific, not a fixed function of `color_intensity`. Any
downstream pipeline treating `color_intensity` as a linear luma-shift control would be wrong.

**`scene_threshold` incommensurable with `scdet`'s scale — GENERALIZES AND STRENGTHENS.**
Every manifest that declares a `scene_threshold` sits further above its own source's
measured `scdet` ceiling than the original manifest's 7.0-vs-1.706 (≈4×) gap:
`highlights_graded_varied` 20.0 vs source max 1.379 (≈14.5×), `highlights_graded` 20.0 vs
1.379 (≈14.5×), `highlights_graded_25s` 50.0 vs the raw master's own ceiling (≈36×, the
widest gap measured anywhere in this pack), `highlights_5_22s` 8.0 vs the raw master's 0.425
/1.379 ceiling. The parameter is not merely undocumented — at higher nominal values it
becomes proportionally **more** detached from anything `scdet` can express, in every regime
tested.

**Clip boundaries are not reliably content-derived — GENERALIZES AND STRENGTHENS.**
`highlights_graded` shows this most starkly: 7 of 7 boundaries sit at or below the median
`scdet` rank (vs the original's 4 of 5), forming a mechanical, gap-free 10-second grid across
the full source, with `scenes_detected` (7) exactly equal to `total_clips` (7) and
`scenes_filtered` 0 — the strongest evidence in this pack that `scenes_detected` tracks
**output-clip count**, not real scene segmentation. `highlights_5_22s`, sourced from the raw
master directly, shows the same pattern with boundary scores of 0.001/0.014/0.032 — closer
to zero than any boundary measured in the original manifest.

### 8.3 New findings, unique to the archive corpus

Six new problems, none present in — or testable against — the original single-manifest
reconciliation:

1. **`highlights_graded_25s`: 3 documented clips, 10 actual files on disk.** 7 of the 10
   `split_*.mp4` files in that directory (`split_001_s63`, `split_002_s62`,
   `split_003_s61`, `split_004_s61`, `split_005_s61`, `split_006_s58`, `split_007_s55`) are
   **entirely undocumented** by that manifest — a leftover from a differently-parametered
   earlier run of the same tool against the same source, never cleaned up and never folded
   into the manifest that now sits alongside them. All 10 are probed in this pack's `probe/`
   regardless (§2.6).
2. **`highlights_long`: 3 documented clips, 5 actual files, 2 of which are byte-identical
   duplicates.** `split_002_s65.mp4` and `split_003_s65.mp4` share sha256
   `c86f8072c363bb2af060f20899d748ceacf1eb979a90240f0192e495ec7f926f` — the same content
   under two filenames, one of them undocumented. `split_001_s70.mp4` is also undocumented
   (a 22.000 s clip, unrelated in duration to any documented clip). Same underlying failure
   mode as finding 1: stale output from an earlier parametrisation, not reconciled against
   the current manifest.
3. **`highlights_best`: `scenes_detected` (15) minus `scenes_filtered` (0) leaves 15,
   against `total_clips` 5 — a 200% mismatch**, the widest scenes-vs-clips gap measured
   anywhere in this pack (the original manifest's gap was 7−3 vs 4, i.e. 0%; see §4).
   `highlights_graded`/`highlights_graded_25s`'s 7-vs-7 (0% gap, but for the opposite
   reason — see §8.2) is the other extreme. The `scenes_detected`/`scenes_filtered`
   bookkeeping is not merely undocumented, it is **inconsistent in direction** across runs
   of the same tool.
4. **`highlights_best`: one clip's declared `duration` field contradicts its own declared
   `start_time`/`end_time` in the same document**, and is measurably wrong against the
   delivered file — the first instance in this pack of a manifest disagreeing with *itself*,
   not just with measurement.
5. **Undocumented frame-rate conversion, `highlights` manifest.** Source is `59.94fps`
   (`60000/1001`, the raw master); every output clip is exact CFR `30/1`. Nothing in
   `split_params` or any clip record states a frame-rate target — this is a second silent
   transform (alongside the already-documented 10-bit→8-bit reduction and
   `bt2020nc`→`bt709` retag, MAT-8/§2.1a) that the splitting tool performs without
   declaring.
6. **The scdet warm-up artifact reproduces exactly as documented, on new material** —
   `highlights__split_003_s61`'s row-1 score of 7.828 (§2.6) is the artifact this pack's
   README already names, not a new hard cut. Positive validation, not a new problem: the
   pack's own documented mitigation catches it correctly on footage it was never tuned
   against.

### 8.4 What this section establishes

Four findings that could have been an 8-file, one-manifest coincidence are now tested
against 15 files, 8 manifests, 2 source generations (proxy and raw master), and 8 disjoint
parameter regimes. Three of the four generalize and in most regimes strengthen; the fourth
(`auto_speed`) simply was not re-exercised and stays at N=1. The archive corpus additionally
surfaced six defect classes the single-manifest study could not have found by construction
(undocumented files, byte-identical duplicates, self-contradicting fields, inconsistent
scene-count bookkeeping, a silent frame-rate conversion) — evidence that the underlying
splitting tool's manifest output is unreliable **as a class**, not just in the one instance
this pack originally studied.

**Coverage caveat, stated plainly.** The six manifests reconciled in the interrupted prior
run (`highlights_best`, `highlights_graded_varied`, `highlights`, `highlights_graded_25s`,
`highlights_graded`, `highlights_5_22s`) did not receive the independent adversarial
skeptic pass this pack's other claims have (§7). Their findings are reproduced here from
that run's own recorded, evidence-cited detail — not re-verified by a second, independent
measurement — and should be read with correspondingly less certainty than a
skeptic-confirmed claim elsewhere in this pack until that pass runs.


