# reference_pack

Measured, license-clean characterisation of this project's example drone footage.

The pack is **measurements about footage, never footage**. It exists so that every threshold
in `src/drone_video_ai/` can trace to a number someone actually measured over this corpus,
rather than to an invented constant. Its governing spec is
`.claude/specs/reference-pack/spec.md` (**Status: DRAFT — not signed off**).

Source corpus (read-only, never modified by anything here):
`/Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples`
— 9 entries: 8 `.mp4` deliverables plus the tool-written sidecar `manifest.json`.

**Also measured, since 2026-07-27** (read-only, `_archive/`, never copied into this repo):
6 raw camera-original drone masters and 39 derivative clips from 7 more sidecars, used to
cross-validate this pack's findings against different footage and different tool parameters
rather than expand the delivered corpus itself. See REVIEW.md §2.5/§2.6/§8. "The corpus" below
still means the original 9 unless stated otherwise.

---

## The one fact that matters most

**There are zero hard cuts anywhere in this corpus.** Every one of the 8 files is a single
continuous shot, and none has an audio stream.

Recounted directly from the 8 corpus files' delivered CSVs: across all **4,099** scored
corpus frames, **0** frames reach 5.0 and **0** reach 10.0 on ffmpeg `scdet`'s 0–100 scale.
(The pack also carries a 9th probe pair for the out-of-corpus source master
`DJI_0355_proxy.mp4` — 1,909 further scored frames, max 1.706, likewise cut-free — bringing
the pack total to 6,008 scored frames. The zero-cuts statement above is scoped to the 8
delivered corpus files.)

| file | frames | max score |
|---|---|---|
| `split_004_s65` | 450 | 0.516 |
| `instagram_reel_test` | 813 | 1.547 |
| `viral_test_v2_4k` | 437 | 1.776 |
| `viral_test_v2` | 437 | 1.799 |
| `split_003_s66` | 249 | 2.104 |
| `split_002_s69` | 450 | 2.435 |
| `split_001_s70` | 450 | 2.668 |
| `instagram_reel_v34_all_kb_full` | 813 | 3.537 |

For calibration, a synthetic 3-segment positive control (`testsrc2` → `black` → `smptebars`)
scored its two genuine cuts at **31.42** and **42.19** — one to two orders of magnitude above
anything present here.

This is a **positive finding, not a detection failure**, and it has two consequences you
should not work around:

1. This corpus **cannot** validate a shot-boundary detector. It has no boundaries. This
   independently corroborates `pyproject.toml`'s exclusion of any
   TransNetV2/PyTorch/TensorFlow shot-boundary dependency.
2. In `split_001` / `split_002` / `split_003` the global maximum is a **`scdet` warm-up
   artifact at frame index 1** (t = 0.033333 s), not content: `scdet`'s score is
   `|mafd − prev_mafd|` and `prev_mafd` is still 0 at the first inter-frame comparison, so the
   score equals the full MAFD. Excluding it, their true maxima are 0.537 / 0.475 / 0.174.
   **Discard frame index 1 before computing any threshold**, or the artifact will set it.

---

## Directory layout

```
data/reference_pack/
├── README.md                 # this file
├── REVIEW.md                 # full per-file review, manifest reconciliation, verification log
├── editorial_style.json      # machine-readable house style (see "What each artifact means")
├── media/
│   └── .gitkeep              # directory tracked; contents ignored by .gitignore
└── probe/
    ├── {basename}.json       # 54 files — full ffprobe technical facts
    └── {basename}.scd.csv    # 54 files — per-frame scene-change score series
```

**108 files in `probe/` total (54 JSON + 54 CSV), not 18.** Original 9 (8 corpus files +
`DJI_0355_proxy`, the out-of-corpus source master) plus **45 added 2026-07-27**: 6 raw
camera-original masters (including `DJI_20241029174803_0355_D.MP4`, confirmed this session
as the camera original behind `DJI_0355_proxy.mp4` — see REVIEW.md §2.1a) and 39 derivative
clips from 7 more `manifest.json` files in the same `_archive/` tree. Full per-file detail:
REVIEW.md §2.5 (raw masters), §2.6 (derivative summary table), §8 (7-manifest
cross-validation). None of this new material is copied into the repo — every probe file is a
measurement of a read-only external file, same convention as the original `DJI_0355_proxy`
entry.

`.gitignore` pre-declares this shape:
`/data/reference_pack/media/*` is ignored with `!/data/reference_pack/media/.gitkeep`
re-included. `probe/` is small text and is tracked. Sibling `data/manifests/` is
**deliberately not ignored** ("small JSON — safe to commit selectively") and is the correct
home for any derived manifest; `data/interim/` and `data/output/` are ignored as regenerable.

Current contents of the **original 9** — one JSON and one CSV per file:

| basename | CSV rows | scored rows |
|---|---|---|
| `instagram_reel_test` | 813 | 813 |
| `instagram_reel_v34_all_kb_full` | 813 | 813 |
| `split_001_s70` | 450 | 450 |
| `split_002_s69` | 450 | 450 |
| `split_003_s66` | 249 | 249 |
| `split_004_s65` | 450 | 450 |
| `viral_test_v2` | 437 | 437 |
| `viral_test_v2_4k` | 437 | 437 |
| `DJI_0355_proxy` *(source master, not in corpus)* | 1909 | 1909 |

The **45 added 2026-07-27** are not tabulated per-file here — REVIEW.md §2.5/§2.6 carry that
detail at the appropriate density (individual writeups for the 6 raw masters, one summary
table for the 39 derivatives, since 39 near-identical per-clip rows here would just duplicate
that table). `data/manifests/reference_pack.json` → `archive_expansion` is the machine-
readable index.

Row count **must** equal the file's `nb_frames`, and scored rows must equal row count. See
"Two silent-failure traps" — a row-count check alone passes on a broken CSV.

---

## What each artifact means

### `probe/{basename}.json`

Raw, unedited ffprobe output: a `streams` array and a `format` object. Nothing is
interpreted, filtered, or renamed, so it stays a primary source. Read fields from it rather
than trusting any summary, including this one.

Fields that turned out to be load-bearing:

- **`nb_frames` + `duration` + `r_frame_rate` / `avg_frame_rate`** — every file is CFR 30/1,
  confirmed three ways: `r_frame_rate == avg_frame_rate`, `nb_frames / duration == 30.000`
  exactly, and `duration_ts / time_base` landing on the exact duration.
- **`color_space` / `color_primaries` / `color_transfer` / `color_range`** — the sharpest
  split in the corpus. The four `split_*` files carry `color_space=bt709` and
  `color_range=tv`, with `color_primaries` and `color_transfer` **absent**. All four vertical
  files carry **no colour keys at all**. Any BT.709 assumption for the verticals is an
  inference, not a measurement.
- **Encoder tags** — cleanly separate the two families: splits are
  `Lavc61.19.100 h264_videotoolbox` (Apple hardware), `has_b_frames=0`, level 3.1; verticals
  are `Lavc61.19.100 libx264`, `has_b_frames=2`, level 4.1/5.1. Both muxed `Lavf61.7.100`.
  Every file is an ffmpeg-produced re-encode; **no camera original is present among these 9
  probed files**. *(Clarified 2026-07-27, this session: this describes the 9-file probe set
  only, not the wider world — the camera original behind `DJI_0355_proxy.mp4` was
  subsequently located at `DJI_20241029174803_0355_D.MP4` in the same `.advanced/` directory
  and pixel-matched against the proxy. It is outside this 9-file probe set, not nonexistent.
  See §2c below and `REVIEW.md` §2.1a.)*
- **Absence of `side_data_list`** — no rotation / display-matrix metadata on any file.

### `probe/{basename}.scd.csv`

Two columns, no header: `pts_time,lavfi.scd.score`. One row per frame, captured with
`scdet=threshold=0` so `scdet` tags **every** frame and filters nothing. Thresholding is
deliberately deferred to offline analysis so that the choice of threshold is auditable
instead of baked into the capture.

Scores are on a **0–100** scale. A hard cut scores in the tens; a continuous shot stays near
zero. Frame 0 always scores 0.000 (no predecessor), and frame 1 is the warm-up artifact
described above.

**Do not convert between `scdet`'s score and the `select` filter's `scene` value.** They are
different metrics, not a rescaling of one another: at `pts_time` 0.033333 in `viral_test_v2`,
`scdet` reports 0.870 while `scene_score` reports 0.022261 (0.870/100 would be 0.0087).
"scene 0.3" is **not** "scdet 30".

---

## Two silent-failure traps

Both were confirmed by direct reproduction in this environment (ffprobe/ffmpeg 8.1), and both
**exit 0 while producing wrong output**. Both have already produced bad artifacts in this
pack's history. Do not paste the broken forms from memory.

### Trap 1 — comma vs colon in `-show_entries` drops every score

`-show_entries` separates section specifiers with a **colon**. With a comma, ffprobe parses
`frame_tags=...` as a field name inside the `frame` section and silently emits timestamps only.

```
# BROKEN — emits bare timestamps, no score column, exit 0
0.000000,
0.033333
0.066667

# CORRECT — colon
0.000000,0.000,
0.033333,2.104
0.066667,0.174
```

This is why the integrity check is "**scored** rows", not "rows".

### Trap 2 — `metadata=print` is inert under `-loglevel error`

`metadata=print` writes to the ffmpeg log at **INFO** level, which `-loglevel error`
suppresses. Proven with a positive control on `split_003_s66.mp4`: at `gt(scene,0.01)`, which
genuinely matches frames, the `metadata=print` form printed **nothing**, while
`metadata=print:file=-` printed `lavfi.scene_score=0.053851`.

**Consequence: silence from the `-loglevel error` + `metadata=print` form carries no
information and must never be cited as evidence of "no cuts".** Always use
`metadata=print:file=-`.

---

## How to regenerate the pack

Prerequisites: ffprobe/ffmpeg **8.1** at `/opt/homebrew/bin` and Python 3 stdlib. Nothing
else. There is deliberately no `cv2` / `numpy` / `scenedetect` / `opentimelineio` path —
`.venv/` is an empty husk and the declared runtime dependencies are not installed. **Do not
pip install anything to regenerate this pack**; every recipe below is stdlib + ffmpeg.

> **Toolchain fragility — check before trusting any recipe (spec AC11).** These recipes
> assume the homebrew ffmpeg link set at `/opt/homebrew/bin` is intact, and that assumption
> has already failed once: on 2026-07-27 a routine `brew upgrade` moved x265 4.1→4.2,
> deleting `libx265.215.dylib` that ffmpeg 8.1 was linked against, and **every ffmpeg/ffprobe
> recipe on this page aborted at load** (`dyld: Library not loaded`) until
> `brew reinstall ffmpeg` relinked it (now 8.1.2; the measurements in this pack were made
> under 8.1). `scdet`/`cropdetect`/`signalstats` behaviour is version-dependent — record the
> `ffprobe -version` output alongside any new measurement. First command in any new session:
> `ffprobe -version` — if it dies with a `dyld` error, run `brew reinstall ffmpeg` before
> anything else.

Every command below was executed in this environment and produced the documented output
(under ffmpeg 8.1, before the relink noted above).

```bash
export PATH=/opt/homebrew/bin:$PATH
SRC=/Users/mac/Documents/photography-WORKFLOW-local/00-assets/drone-video-examples
OUT=/Users/mac/Documents/photography-WORKFLOW-local/04-drone-video-editing-ai/data/reference_pack/probe
```

### 1. Technical probe (`probe/{basename}.json`)

```bash
for f in "$SRC"/*.mp4; do
  b=$(basename "$f" .mp4)
  ffprobe -v error -print_format json -show_format -show_streams "$f" > "$OUT/$b.json"
done
```

Note (2026-07-27): as pasted, this is **not byte-for-byte** with the delivered JSON — the
delivered files' `format.filename` is a bare basename (e.g. `split_003_s66.mp4`); running
this loop verbatim writes the full `$SRC` path into that field instead, since ffprobe echoes
back whatever path it was invoked with. Every other field is unaffected and reproduces
exactly (verified this session). To match byte-for-byte, `cd "$SRC"` first and pass `$f` as a
bare filename. Same caveat applies to recipe 2b below.

### 2. Per-frame scene-change scores (`probe/{basename}.scd.csv`)

Note the **colon** before `frame_tags` (Trap 1):

```bash
for f in "$SRC"/*.mp4; do
  b=$(basename "$f" .mp4)
  ffprobe -v error -f lavfi -i "movie=$f,scdet=threshold=0" \
    -show_entries 'frame=pts_time:frame_tags=lavfi.scd.score' \
    -of csv=p=0 > "$OUT/$b.scd.csv"
done
```

### 2b. Source-master probe pair (`probe/DJI_0355_proxy.{json,scd.csv}`)

Recipes 1–2 loop over the 8 corpus files only; the 9th probe pair — the out-of-corpus source
master the manifest's `source_master.probe_artefacts` points at — is produced separately.
The proxy is **read-only input**; these commands only read it:

```bash
PROXY="/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4"
ffprobe -v error -print_format json -show_format -show_streams "$PROXY" > "$OUT/DJI_0355_proxy.json"
ffprobe -v error -f lavfi -i "movie=$PROXY,scdet=threshold=0" \
  -show_entries 'frame=pts_time:frame_tags=lavfi.scd.score' \
  -of csv=p=0 > "$OUT/DJI_0355_proxy.scd.csv"
```

Expected: 1909 rows, all scored, max 1.706. If the archive path has moved, locate the file by
its recorded sha256 (`8e0a610f...`, see `data/manifests/reference_pack.json` →
`source_master`) rather than assuming a same-named file is the same bytes.

### 2c. The camera original behind the proxy — located and pixel-matched (2026-07-27)

`DJI_0355_proxy.mp4` is a re-encode (`Lavc62.11.100 libx264`), not a camera file. The camera
original behind it was located this session in the **same** `.advanced/` directory:
`DJI_20241029174803_0355_D.MP4` (994,725,078 bytes). Re-probed this session and confirmed
against `REVIEW.md` §2.1a: HEVC (`hvc1`) Main 10, 3840×2160, `r_frame_rate ==
avg_frame_rate == 60000/1001` (59.94 fps), `duration` 63.580183 s, `nb_frames` 3811,
`pix_fmt` yuv420p10le, `color_space=bt2020nc`/`color_primaries=bt2020`/
`color_transfer=arib-std-b67`/`color_range=tv` — **the identical complete HLG tag set as the
proxy**, `format.tags.encoder = "DJI Mavic3Pro"`, `creation_time = 2024-10-29T17:48:03Z`
(matches the filename's embedded timestamp). `cropdetect` returns the full 3840×2160 raster
at both ends of the file — no baked-in letterbox, so no crop reconciliation was needed before
comparing it to the proxy (unlike the split-vs-proxy comparisons in §2.2 of `REVIEW.md`,
which do need the proxy's letterbox crop).

**Method.** Raw is 59.94 fps and the proxy is exact 30/1 CFR — a 2000:1001 ≈ 1.998:1 ratio,
not a clean 2:1 — so frame-index correspondence cannot be assumed. Each sampled proxy
timestamp *T* was matched by sweeping single raw frames (bicubic-scaled 3840×2160 →
1280×720, no crop) across a window of raw times around *T*, in raw-frame steps
(1001/60000 = 0.016683 s), and reading the PSNR y peak:

```bash
RAW="/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_20241029174803_0355_D.MP4"
PROXY="/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4"
ffmpeg -nostdin -nostats -loglevel info \
  -ss "$RAW_T" -i "$RAW" -ss "$PROXY_T" -i "$PROXY" -frames:v 1 \
  -lavfi "[0:v]scale=1280:720:flags=bicubic,format=yuv420p[a];[1:v]format=yuv420p[b];[a][b]psnr" \
  -f null -
```

**`-nostdin` is required** when looping this command inside a shell `while read` loop over a
piped offset list — without it, ffmpeg competes with the loop for stdin and silently corrupts
the loop variable on every iteration after the first (discovered this session; verify any
sweep script includes it).

**Independent re-verification this session, at two sampled points not in `REVIEW.md`'s
original nine-point table:**

| Proxy *T* | Best-match raw *t* | Offset | PSNR y at peak | PSNR y, adjacent raw frames |
|---|---|---|---|---|
| 15 s | 14.916583–14.933267 s | −0.067 to −0.083 s | 26.95 / 26.91 dB (near-tied double peak) | 22.2–24.1 dB |
| 45 s | 44.94995 s | −0.050 s | 35.30 dB (sharp single peak) | 31.1–31.5 dB adjacent, 26–28 dB further out |

Calibration floor, re-verified this session with a deliberately mismatched pair (proxy T=15 s
against the raw's T≈45 s window): flat **18.2–18.3 dB**, no peak — consistent with
`REVIEW.md`'s own floor of 15.5–19.6 dB. Both new points clear that floor by 7–17 dB.

**Verdict: CONFIRMED, high confidence** — same conclusion as `REVIEW.md` §2.1a, now
corroborated at two additional timestamps. Two things remain explicitly unresolved:

1. A **constant offset**, not zero, is needed at every point tested (this session: −0.050 s
   at t=45s, −0.067 to −0.083 s at t=15s; `REVIEW.md` §2.1a: −0.050 to −0.067 s at t=1–50s) —
   too large and non-growing to be pure frame-rate-ratio drift, and not yet mechanistically
   explained.
2. The **exact frame-index mapping**. At t=45s the peak is a sharp isolated spike (favouring
   discrete nearest-frame selection); at t=15s the two adjacent best-matching raw frames are
   within 0.04 dB of each other (a plateau, not a spike) — a nuance not present in `REVIEW.md`'s
   original table, and it argues the decimation is not perfectly uniform across the clip. The
   precise formula is still not derived.

**Cross-check against the 5 sibling manifests that name this raw file directly.** Of the 7
`manifest.json` files under `.advanced/{highlights,highlights_5_22s,highlights_best,
highlights_graded,highlights_graded_25s,highlights_graded_varied,highlights_long}/`,
independently re-loaded and checked this session: **5 name `DJI_20241029174803_0355_D.MP4`
directly as `source_file`** (`highlights`, `highlights_5_22s`, `highlights_graded`,
`highlights_graded_25s`, `highlights_graded_varied`) and their last clip's `end_time` caps at
**63.58**, matching the raw file's own measured duration (63.580183 s) to 2 dp. The other 2
(`highlights_best`, `highlights_long`) name `DJI_0355_proxy.mp4`, and their last clip's
`end_time` caps at **63.63**, matching the proxy's own measured duration (63.633333 s) to
2 dp. Whichever tool produced these manifests read real per-file duration from whichever of
the two files it was pointed at — corroborating, not merely consistent with, this session's
pixel-match verdict that both are the same underlying shot.

Full nine-point table, calibration methodology and additional corroborating detail: see
`REVIEW.md` §2.1a.

### 3. Identity anchors

```bash
shasum -a 256 "$SRC"/*.mp4
```

Re-verified this session:
`33dd47b0a2980a7033c639a95087059104bfe445258bd56793e3785fe26e396c  split_003_s66.mp4`
`e1fb91b6b99eaaff69711f6617b38d4c7c07cbf4fc384c25a4d83ad7f02a4eb8  instagram_reel_test.mp4`

### 4. Independent cut cross-check

Note `metadata=print:file=-` (Trap 2). Emitting nothing here is a **valid and informative**
result — but only because the positive control above proves this form is not inert:

```bash
ffmpeg -nostats -loglevel error -i "$SRC/split_003_s66.mp4" \
  -vf "select='gt(scene,0.3)',metadata=print:file=-" -f null -
```

To re-run the positive control that validates the recipe itself, lower the gate to a value
that genuinely matches (`0.01`) and confirm output appears.

### 5. Letterbox geometry

```bash
ffmpeg -nostats -loglevel info -i "$SRC/split_003_s66.mp4" \
  -vf "cropdetect=limit=24:round=2:reset=0" -f null - 2>&1 \
  | grep -o 'crop=[0-9:]*' | sort | uniq -c
```

Reproduced this session: `247 crop=1280:544:0:88` for `split_003_s66.mp4` (a single stable
value, no other), and `88 crop=1080:1920:0:0` over the first 3 s of `instagram_reel_test.mp4`
— i.e. splits are letterboxed, verticals are not.

Caveat: `cropdetect` thresholds at luma `limit=24`, so this proves the bars are **below that
level**, not that they are mathematically pure black.

### 6. Audio absence

```bash
ffprobe -v error -select_streams a -show_entries stream=index -of json "$SRC/split_003_s66.mp4"
```

Returns an empty `streams` array. All 8 files report `format.nb_streams=1` with the sole
stream `codec_type=video`.

### 7. Validate the regenerated pack

```bash
cd "$OUT"
for f in *.json; do python3 -m json.tool "$f" > /dev/null && echo "JSON OK: $f"; done
python3 - <<'EOF'
import csv, glob, os
for p in sorted(glob.glob('*.scd.csv')):
    rows = [r for r in csv.reader(open(p)) if r]
    scored = sum(1 for r in rows if len(r) >= 2 and r[1].strip())
    print(f"{os.path.basename(p):45s} rows={len(rows):4d} scored={scored:4d}")
EOF
```

`rows` must equal `scored` on every line, and must match the `nb_frames` table above.

---

## Interpreting the corpus

### Two independent families, not one pipeline

The 4 splits and the 4 verticals share **no source, no encoder, no colour policy, and no
framing**. By mtime the vertical family predates the split family by roughly five weeks
(2026-02-04 → 02-08 versus **03-16 only** for all four `split_*` files), so the splits are
not intermediates for the reels. *(Corrected 2026-07-27: this previously read "03-15 →
03-16" — 03-15 17:00 is `DJI_0355_proxy.mp4`'s mtime, the out-of-corpus source master, not
any split file's. All four splits carry 03-16 19:21–19:23 mtimes, confirmed by `stat`.)*

**Split family** — `DJI_20241029174803_0355_D.MP4` (camera original, located and pixel-matched
2026-07-27, this session — see §2c) → `DJI_0355_proxy.mp4` (720p, 10-bit HLG/BT.2020
proxy, 1909 frames, 63.633333 s) → the four `split_*` clips. Provenance is **known**:
documented in `manifest.json` *and* verified by pixel measurement, with **all four clips**
landing frame-exactly at `floor(start_time × 30)` on their declared `start_time`. *(Corrected
2026-07-27 — adversarial verification killed claim C24, 2/3 refute: the original "three of
four, with split_003 one frame late at proxy frame 501" was an artefact of a raw mean-luma
correlation too flat to resolve one frame. First-difference PSNR resolves it unambiguously to
frame 500; split_003's 1-frame shortfall is at the **end** of its range, not a late start. See
`REVIEW.md` §7.1.)*

The proxy is **not** in the read-only corpus directory. `manifest.json` records it at
`/Users/matthewdeane/Documents/Data Science/python/_projects/...`, which **does not resolve**
(`/Users/matthewdeane` does not exist). It was located at
`/Users/mac/Documents/photography-WORKFLOW-local/_archive/_p-ai-drone-video/.drone_clips/.advanced/DJI_0355_proxy.mp4`
(92,905,225 bytes) — same relative subpath, different root. That directory is read-only too.
The proxy is itself a re-encode (`Lavc62.11.100 libx264`), so even it is not a camera file —
but its own camera original is no longer absent: it was located this session, in the same
`.advanced/` directory, and pixel-matched against the proxy. See §2c above.

**Vertical family** — provenance is **inferred**, not known. Nothing in any surviving artifact
documents these four files. `DJI_0355_proxy.mp4` was **ruled out** by measurement against a
calibrated null. `viral_test_v2` ↔ `viral_test_v2_4k` and `instagram_reel_test` ↔
`instagram_reel_v34_all_kb_full` are each frame-locked pairs — same frame count, exactly 2×
linear resolution — but their shared parent timeline is absent from the searched tree.

### Anchor every similarity claim against the corpus's own null

The null here is **large enough to invalidate naive luma matching**, so an unanchored
correlation is not evidence:

- Time-reversed `split_003` vs `instagram_reel_test` scores r = **+0.9421**, *higher* than
  the forward r = +0.7497.
- Known-disjoint split pairs reach r = +0.8831 (`001` vs `003`) and +0.8753 (`003` vs `004`).
- The matched-geometry unrelated-pair control is PSNR y = **12.481161 dB**
  (`viral_test_v2` vs `instagram_reel_test`, **no crop, no scale** — both are natively
  1080×1920, compared directly over the shorter clip's 437 frames):
  `ffmpeg -i viral_test_v2.mp4 -i instagram_reel_test.mp4 -lavfi "[0:v][1:v]psnr" -f null -`.
  Reproduced verbatim 2026-07-27 (per spec.md AC9's amended naming requirement).

Genuine source matches, by contrast, score r = 0.95975–0.99948. Use the negative control or a
time-reversed null in any claim, or the claim is a coin flip.

### Letterbox: the apparent `manifest.json` contradiction is resolved, not smoothed over

`manifest.json` claims `letterbox: "2.35"` while the coded frame is 16:9. Both are true and
compatible. `cropdetect` returns a single stable `crop=1280:544:0:88` on all four splits —
88 px black bars top and bottom (88 + 544 + 88 = 720 exactly), active picture
1280×544 = **2.352941:1** — baked into a genuine 1280×720 raster with no SAR/DAR tags. Exact
2.35 would need height 544.681 px, so 544 is the nearest even value; `"2.35"` is a correct
2-dp label for the real geometry.

Mechanism measured: a vertical **centre crop**, not an anamorphic squeeze. Two independent
discriminators agree — PSNR 28.97 dB for the crop hypothesis vs 22.86 dB for the squeeze, and
`split_001`'s correlation at its declared offset is +0.95975 against the proxy centre-crop but
only +0.30494 against the proxy full frame. The source `cropdetect`s as unletterboxed
`1280:720:0:0`, so the bars originate in this pipeline. Consequence: `resolution: "source"` is
true of the raster while **24.4% of source rows (176 of 720) were discarded**.

The verticals have no bars and no pillarbox: `crop=1080:1920:0:0` and `crop=2160:3840:0:0`.

### Trust `manifest.json` on geometry and timing; distrust it on processing semantics

Reliable, verified: `start_time` offsets (frame-exact on all four), letterbox, durations
(except `split_003`), raster, and `sort`.

Unreliable, measurably: `auto_speed: true` is a no-op (clip frame N maps to source frame
offset+N for all 1,599 frames, net speed factor 1.000); `color: "drone_aerial"` at intensity
0.65 changed **luma only**, with chroma within noise; `filtered: false` contradicts
`summary.scenes_filtered: 3` in the same document; and the scene-detection narrative does not
describe what produced these clips — 3 of 4 clips are exactly `max_duration` long and 4 of 5
boundaries sit at or below the median frame difference.

Traps for consumers:

- **`clips[]` is score-sorted, not timeline order** (and the manifest never says so). Timeline
  order is `split_004` → `split_003` → `split_002` → `split_001` — exactly reversed. Iterating
  `clips[]` in order gives you reverse-chronological footage.
- **`start_time` / `end_time` are 2 dp, coarser than one frame period** (0.033333 s). This
  caused `split_003_s66.mp4`'s real 1-frame shortfall: `25.0 − 16.67 = 8.33`;
  `8.33 × 30 = 249.9`; `floor → 249` frames against a true 250-frame span. Recomputing frame
  ranges from these fields reproduces the same off-by-one.
- **`total_size_mb: 95.4` is mebibytes, not megabytes** (95.3939 MiB vs 100.0278 SI MB).
- Filename suffixes `s70`/`s69`/`s66`/`s65` are `int()` **truncations** of the scores, not
  roundings (69.8 → `s69`, 66.8 → `s66`).

### Percentile convention

`p90`/`p99` figures may differ in the last digit between analyses (e.g. `instagram_reel_test`
p99 quoted as 1.104, 1.133 and 1.137) — that is nearest-rank versus linear interpolation on
adjacent tail samples, **not** a data disagreement. `min`, `p50` and `max` reproduce exactly,
and threshold-based cut counts are unaffected. State your convention when adding numbers.

### Not verifiable with this toolchain

Declared, not filled in. Do not guess these:

- **`manifest.json`'s `motion_type` labels** (`REVEAL` / `ORBIT_CW` / `STATIC`) — the
  *direction* labels (REVEAL vs ORBIT_CW) need per-pixel motion direction and rotation
  estimation, i.e. optical flow via `cv2`, which is unavailable. `scdet`'s MAFD gives
  magnitude only and is direction-blind. The `STATIC` label is *partly* testable without
  `cv2` (a null-controlled row-profile cross-correlation showed split_004, declared STATIC,
  drifting ~2.7 px/frame — single-run, unreplicated, a caveat not a finding; `REVIEW.md`
  §5.1 group G).
- **`score` and `motion_energy` values** — undocumented algorithms. `motion_energy`'s *rank
  order* was corroborated (perfect Spearman match against mean MAFD, confirmed three ways).
  The magnitude divergence is **metric- and measurement-surface-dependent** — −18.9% on
  cropped-source scdet MAFD, 11.1% on proxy full-frame 8-bit MAFD — not a single figure.
  *(Corrected 2026-07-27 — C54 killed 2/3: the original "up to 24.3%" did not reproduce at
  either refuting skeptic and is withdrawn. Any MAFD number in this pack must state its
  measurement surface. See `REVIEW.md` §7.1.)*
- **`scene_threshold: 7.0`, `enhanced`, and `quality`'s label→bitrate mapping** — no
  observable maps to them. `7.0` is on a scale incommensurable with `scdet`'s: zero of 1,909
  source frames exceed even 2.0.
- **Whether the proxy's `bt2020nc` tag is correct** — narrowed, and its residual branch is now
  **resolved**. *(Corrected 2026-07-27 — C58 killed 3/3: the proxy's tagging
  (`bt2020nc`/`bt2020`/`arib-std-b67` over a 10-bit stream — three fields agreeing) is
  complete and unambiguous, not a spurious lone tag. Since the spurious-tag reading is now much
  weaker, the splits' bt709 retag **without** chroma conversion is correspondingly **more**
  plausibly a colour-management defect — the retag can only be harmless if the source tag was
  wrong. **FURTHER RESOLVED 2026-07-27, this session, same day**: whether that tagging is
  faithful to the camera original is no longer open — the camera original was located
  (`DJI_20241029174803_0355_D.MP4`, §2c) and pixel-matched against the proxy at 7 of 9 sampled
  timestamps (PSNR y 29–40 dB vs a 15.5–19.6 dB floor), and it declares the identical
  `bt2020nc`/`bt2020`/`arib-std-b67`/`tv` HLG tag set. Yes, the camera original was itself
  HLG/BT.2020. What remains genuinely open, narrower still, is only whether the `drone_aerial`
  grade was applied as specified — a separate question this measurement does not touch. See
  `REVIEW.md` §2.1a and §5.1 group D.)*
- **Burned-in captions, logos, or overlays — identification**, i.e. what they say or look
  like, needs a rendered frame and the prohibition below forbids that. *Presence* is a
  different question: region-wise MAFD / `signalstats` / `freezedetect` on crops can detect a
  static or animated overlay region entirely in-pipe (`ffmpeg ... -f null -`, nothing
  persisted) and this was **not attempted** in this pass — a coarse 3×6 spatial-grid check
  found no zero-variance region on the two 1080p verticals, but that is a partial check, not a
  clearance. *(Corrected 2026-07-27 — C59 killed 3/3: "unmeasured and unmeasurable" was wrong;
  the prohibition blocks frame capture, not frame measurement. See `REVIEW.md` §5.1 group E.)*
- **Whether the verticals' opening seconds carry elevated motion** — real but narrower than
  first reported. *(Corrected 2026-07-27 — C56 killed 3/3, unanimous: the original "front-loaded,
  decaying 13–61×" claimed a monotonic per-second decay, but the per-second maximum for
  `instagram_reel_test` falls at t≈17.8s and for `viral_test_v2` at t=14.1s — not the opening
  second — and the "13–61×" range is undefined and metric-dependent (it collapses on MAFD).
  The defensible residue: only `instagram_reel_v34` and `viral_test_v2_4k` show front-loading at
  all, and only as elevated *range* in the first ~4s, not a decay rate. `editorial_style.json`
  already carried the corrected (null) value; this file did not. See `REVIEW.md` §3.7.)*

---

## What this pack must never contain

These are prohibitions, not preferences. `.gitignore` encodes them and the spec's Scope (out)
restates them.

1. **No persisted frames or images. Ever.** No PNG, JPEG, BMP, PPM, thumbnail, contact sheet,
   filmstrip, or any other rasterised single-frame artifact, anywhere in this repo — not under
   `probe/`, not under `media/`, not at the repo root, not in a scratch subdirectory.
   `.gitignore` names `/seek*.png`, `/short*.png`, `/shot-initial.png` and `/.playwright-mcp/`
   as strays to clean up, and states that a frame-capture PNG of an all-rights-reserved source
   video is "exactly the kind of footage-adjacent artifact this project's reference pack must
   never persist".

   Frames may be **decoded in a pipe**; they may not be **written**. Every recipe above ends
   in `-f null -` or a text sink for that reason. If a measurement genuinely needs
   intermediate frames, write them to a scratch directory outside this repo and delete it.

   Note the current scope is an **assumption under the strictest reading**, not a settled rule:
   whether `media/` may hold derived artifacts from the user's *own* footage while
   categorically excluding third-party reference frames is Open Question 1 in the spec, and is
   the user's call. Until answered, persist nothing.

2. **No footage.** No source video, no clip, no proxy, no transcode, no excerpt under
   `media/`. `.gitignore` ignores `/data/reference_pack/media/*` and re-includes only
   `.gitkeep`. The pack is measurements about footage.

3. **No modification of the read-only sources.** Nothing here may move, rename, modify,
   delete, or re-encode anything in `00-assets/drone-video-examples/` or in
   `_archive/_p-ai-drone-video/`. All recipes above are read-only on their inputs.

4. **No license-excluded dependency, and no artifact produced by one.** Per `pyproject.toml`
   lines 12–14: `ultralytics`/YOLOv8 (AGPL-3.0), `pyiqa`/IQA-PyTorch (non-commercial), and any
   TransNetV2/PyTorch/TensorFlow shot-boundary dependency. Measurements derived from those
   tools are as excluded as the tools themselves. As it happens the corpus has no shot
   boundaries to detect, so nothing is lost.

5. **No invented constants and no unverified numbers.** Every value in this pack must trace to
   a command someone actually ran. A threshold must ship with its derivation from the measured
   distribution. Where something is not measurable with ffprobe/ffmpeg plus the stdlib, it is
   recorded as **UNVERIFIABLE IN-SESSION** — never filled with a plausible-looking guess.

6. **No unanchored similarity claim.** Given the corpus's null (a time-reversed pair scoring
   r = +0.9421), any correlation or PSNR claim without its negative control is misinformation,
   not a finding.

7. **No regenerable bulk.** `data/interim/` and `data/output/` are ignored as regenerable.
   Derived manifests belong in the tracked `data/manifests/`, not here.
