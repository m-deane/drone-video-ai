"""Hard-cut (ffmpeg concat-demuxer ``-c copy``) and transition (ffmpeg
``xfade``) rendering for Capability 2, per plan.md task 2.5 and spec AC2.1-AC2.3.

Hard constraint enforced BY CONSTRUCTION, not a flag (spec AC2.3): this
module never builds an ffmpeg filter-graph string invoking the pixel-editing
filters ``eq``, ``curves``, ``colorbalance``, ``unsharp``, or
``vidstabtransform`` (color grading/correction, sharpening, stabilization),
or a speed-changing ``setpts`` usage (i.e. anything other than the exact
PTS-reset idiom that must follow a ``trim`` -- see the transition
filter_complex construction below, which resets each trimmed window's
presentation timestamps to start at zero without altering playback speed).
There is no public function or CLI flag
anywhere in this module or ``color_pinning.py`` that can reach any of those
filters -- ``tests/reel_stitching/test_forbidden_filters_lint.py`` statically
greps both files' source text to enforce this mechanically, not by convention.

Two rendering paths, corresponding to the two entry types in an
``EditManifest``:

- **Hard cut** (``transition_to_next.type == "cut"``): a maximal run of
  consecutive cut-connected entries is rendered via the ffmpeg concat
  demuxer with per-file ``inpoint``/``outpoint`` directives and ``-c copy``
  -- a pure stream remux, byte-exact to source. Before attempting this,
  every consecutive pair of entries in the run is verified (via
  ``common/ffprobe.py``) to share codec/resolution/pixel-format/time_base,
  and every entry's cut-in point is verified to land on an actual source
  keyframe (within half a frame period) -- because ffmpeg's ``-c copy``
  path silently snaps to the nearest *preceding* keyframe otherwise, which
  would silently render a different start point than requested. Either
  precondition failing raises :class:`RenderError` immediately; this module
  never falls back to re-encoding to paper over an incompatibility.
- **Transition** (any other ``type``): only the narrow overlapping window
  between the two adjacent clips (each exactly ``transition.duration``
  seconds long) is decoded and re-encoded, losslessly (``libx264 -qp 0``),
  with color metadata pinned via ``color_pinning.py``. Milestone 1 supports
  only h264/yuv420p source clips for this lossless path (needed so the
  transition segment's codec matches the surrounding stream-copy segments,
  letting the final assembly pass remain a single, uniform-codec file); any
  other source codec raises :class:`RenderError` rather than silently
  degrading to a lossy or mismatched encode.

The final single output file is assembled by concatenating (again via the
concat demuxer, ``-c copy``) the ordered sequence of per-run stream-copy
segment files and per-transition lossless segment files. Each intermediate
segment file is also retained (under ``work_dir``) and reported in
:class:`RenderResult` so ``verify.py`` can check stream-copy correctness
against the *isolated* per-run file (avoiding any ambiguity from seeking
across a codec-parameter boundary inside the merged final output) and so
transition color metadata can be checked directly against the *isolated*
transition segment file.
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from drone_video_ai.common.ffprobe import (
    SourceFileInfo,
    probe_keyframe_times,
    probe_source_file,
)
from drone_video_ai.reel_stitching.color_pinning import (
    ColorPinningError,
    get_transition_pinned_x264_params,
)
from drone_video_ai.reel_stitching.edit_manifest import EditManifest

# Milestone 1's only supported lossless-transition source codec (see module
# docstring). Chosen so the transition segment's codec_name matches the
# surrounding stream-copy segments, keeping the final assembly a uniform,
# single-codec concat.
SUPPORTED_TRANSITION_SOURCE_CODEC = "h264"

# Half a frame period at a conservative 24fps floor, used as an absolute
# floor when an entry's own fps can't tighten the tolerance further.
_DEFAULT_KEYFRAME_TOLERANCE = 1.0 / 48.0


class RenderError(RuntimeError):
    """Raised on any stream-copy precondition failure or unsupported
    transition-codec case. Never silently re-encoded around."""


@dataclass(frozen=True)
class FrameRangeCheck:
    """One (source range) <-> (rendered-output range, in the *isolated
    per-run* output file's own local timeline starting at 0) correspondence,
    for verify.py's framemd5 check."""

    clip_path: str
    src_start: float
    src_end: float
    out_start: float
    out_end: float


@dataclass(frozen=True)
class RunOutput:
    """One rendered stream-copy run (a maximal sequence of cut-connected
    entries), plus the source<->output frame-range correspondences within
    it."""

    output_path: str
    checks: List[FrameRangeCheck]


@dataclass(frozen=True)
class TransitionOutput:
    """One rendered transition-window segment."""

    output_path: str
    clip_a: str
    clip_b: str
    transition_type: str
    duration: float
    out_start: float
    out_end: float


@dataclass
class RenderResult:
    output_path: str
    work_dir: str
    run_outputs: List[RunOutput] = field(default_factory=list)
    transition_outputs: List[TransitionOutput] = field(default_factory=list)


def _run_ffmpeg(cmd: List[str], ffmpeg_bin: str) -> None:
    full_cmd = [ffmpeg_bin, "-y", "-v", "error"] + cmd
    proc = subprocess.run(full_cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RenderError(
            f"ffmpeg command failed (exit {proc.returncode}): {' '.join(full_cmd)}\n"
            f"stderr: {proc.stderr.strip()}"
        )


def _check_stream_copy_compatible(info_a: SourceFileInfo, info_b: SourceFileInfo) -> None:
    fields = ("codec", "width", "height", "pix_fmt", "time_base")
    mismatches = [f for f in fields if getattr(info_a, f) != getattr(info_b, f)]
    if mismatches:
        raise RenderError(
            f"Stream-copy precondition failed between {info_a.path!r} and "
            f"{info_b.path!r}: mismatched {mismatches} "
            f"({[(f, getattr(info_a, f), getattr(info_b, f)) for f in mismatches]}). "
            "Refusing to silently re-encode -- these clips cannot share a "
            "single -c copy concat-demuxer run."
        )


def _assert_keyframe_aligned(
    path: str, t: float, keyframe_times: List[float], fps: float, ffprobe_bin: str
) -> None:
    tolerance = min(_DEFAULT_KEYFRAME_TOLERANCE, 1.0 / (2.0 * fps)) if fps > 0 else _DEFAULT_KEYFRAME_TOLERANCE
    if not keyframe_times:
        raise RenderError(f"No keyframes found in {path!r}; cannot verify cut-point alignment.")
    nearest = min(keyframe_times, key=lambda k: abs(k - t))
    if abs(nearest - t) > tolerance:
        raise RenderError(
            f"Cut point t={t:.4f}s in {path!r} is not keyframe-aligned "
            f"(nearest keyframe at {nearest:.4f}s, tolerance {tolerance:.4f}s). "
            "ffmpeg's -c copy would silently snap to that earlier keyframe "
            "instead of the requested point -- refusing to render this run "
            "as a stream copy. Re-author the edit manifest's in_tc to land "
            "on a keyframe, or re-encode the source with a tighter GOP."
        )


@dataclass
class _EffectiveEntry:
    clip_path: str
    eff_in: float
    eff_out: float


def _compute_effective_bounds(manifest: EditManifest) -> List[_EffectiveEntry]:
    entries = manifest.entries
    n = len(entries)
    eff_in = [e.in_tc for e in entries]
    eff_out = [e.out_tc for e in entries]
    for i in range(n - 1):
        tr = entries[i].transition_to_next
        if not tr.is_cut:
            eff_out[i] = entries[i].out_tc - tr.duration
            eff_in[i + 1] = entries[i + 1].in_tc + tr.duration
    result = []
    for i in range(n):
        if eff_out[i] <= eff_in[i]:
            raise RenderError(
                f"Entry {i} ({entries[i].clip_path!r}) has non-positive effective "
                f"duration after transition-window adjustment "
                f"(eff_in={eff_in[i]:.4f}, eff_out={eff_out[i]:.4f}); the "
                "transition duration(s) touching this entry are too large "
                "for its trimmed content."
            )
        result.append(_EffectiveEntry(entries[i].clip_path, eff_in[i], eff_out[i]))
    return result


def render_edit_manifest(
    manifest: EditManifest,
    output_path: str,
    *,
    ffmpeg_bin: str = "ffmpeg",
    ffprobe_bin: str = "ffprobe",
    work_dir: Optional[str] = None,
) -> RenderResult:
    """Render ``manifest`` to ``output_path``. See module docstring for the
    two rendering paths. Raises :class:`RenderError` loudly on any
    stream-copy precondition failure or unsupported transition codec --
    never silently re-encodes to route around a failure."""
    entries = manifest.entries
    n = len(entries)
    if n == 0:
        raise RenderError("EditManifest has no entries to render.")

    wd = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="drone_stitch_"))
    wd.mkdir(parents=True, exist_ok=True)

    info_cache = {}

    def get_info(path: str) -> SourceFileInfo:
        if path not in info_cache:
            info_cache[path] = probe_source_file(path, ffprobe_bin=ffprobe_bin)
        return info_cache[path]

    keyframe_cache = {}

    def get_keyframes(path: str) -> List[float]:
        if path not in keyframe_cache:
            keyframe_cache[path] = probe_keyframe_times(path, ffprobe_bin=ffprobe_bin)
        return keyframe_cache[path]

    eff = _compute_effective_bounds(manifest)

    # Partition entry indices into maximal cut-connected runs.
    runs: List[List[int]] = []
    current = [0]
    for i in range(n - 1):
        if entries[i].transition_to_next.is_cut:
            current.append(i + 1)
        else:
            runs.append(current)
            current = [i + 1]
    runs.append(current)

    run_outputs: List[RunOutput] = []
    transition_outputs: List[TransitionOutput] = []
    # Ordered list of (kind, artifact) matching the final timeline order,
    # used to build the final assembly concat list.
    ordered_segments: List[str] = []

    run_for_start_index = {r[0]: idx for idx, r in enumerate(runs)}

    for run_idx, run in enumerate(runs):
        # Precondition checks across the run.
        for a_idx, b_idx in zip(run, run[1:]):
            _check_stream_copy_compatible(get_info(entries[a_idx].clip_path), get_info(entries[b_idx].clip_path))
        for idx in run:
            info = get_info(entries[idx].clip_path)
            kf = get_keyframes(entries[idx].clip_path)
            _assert_keyframe_aligned(entries[idx].clip_path, eff[idx].eff_in, kf, info.fps, ffprobe_bin)

        concat_list_path = wd / f"run_{run_idx}_list.txt"
        with open(concat_list_path, "w") as f:
            for idx in run:
                f.write(f"file '{Path(entries[idx].clip_path).resolve()}'\n")
                f.write(f"inpoint {eff[idx].eff_in}\n")
                f.write(f"outpoint {eff[idx].eff_out}\n")

        run_output_path = wd / f"run_{run_idx}.mp4"
        _run_ffmpeg(
            ["-f", "concat", "-safe", "0", "-i", str(concat_list_path), "-c", "copy", str(run_output_path)],
            ffmpeg_bin,
        )

        checks = []
        cursor = 0.0
        for idx in run:
            dur = eff[idx].eff_out - eff[idx].eff_in
            checks.append(
                FrameRangeCheck(entries[idx].clip_path, eff[idx].eff_in, eff[idx].eff_out, cursor, cursor + dur)
            )
            cursor += dur
        run_outputs.append(RunOutput(str(run_output_path), checks))
        ordered_segments.append(str(run_output_path))

        # If this run is followed by a transition (i.e. its last entry's
        # transition_to_next is not "cut"), render that transition segment
        # next, in timeline order.
        last_idx = run[-1]
        if last_idx < n - 1:
            tr = entries[last_idx].transition_to_next
            if not tr.is_cut:
                next_idx = last_idx + 1
                clip_a = entries[last_idx].clip_path
                clip_b = entries[next_idx].clip_path
                info_a = get_info(clip_a)
                info_b = get_info(clip_b)
                if info_a.codec != SUPPORTED_TRANSITION_SOURCE_CODEC or info_b.codec != SUPPORTED_TRANSITION_SOURCE_CODEC:
                    raise RenderError(
                        f"Transition between {clip_a!r} (codec={info_a.codec}) and "
                        f"{clip_b!r} (codec={info_b.codec}): Milestone 1 only supports "
                        f"'{SUPPORTED_TRANSITION_SOURCE_CODEC}' source clips for lossless "
                        "transition rendering. Refusing to silently fall back to a "
                        "mismatched or lossy encode."
                    )
                if info_a.pix_fmt != info_b.pix_fmt:
                    raise RenderError(
                        f"Transition between {clip_a!r} (pix_fmt={info_a.pix_fmt}) and "
                        f"{clip_b!r} (pix_fmt={info_b.pix_fmt}): pixel formats must match."
                    )

                a_start, a_end = eff[last_idx].eff_out, entries[last_idx].out_tc
                b_start, b_end = entries[next_idx].in_tc, eff[next_idx].eff_in
                try:
                    x264_params = get_transition_pinned_x264_params(
                        clip_a, clip_b, ffprobe_bin=ffprobe_bin
                    )
                except ColorPinningError as exc:
                    raise RenderError(
                        f"Color-metadata pinning failed for transition between "
                        f"{clip_a!r} and {clip_b!r}: {exc}"
                    ) from exc

                transition_output_path = wd / f"transition_{run_idx}.mp4"
                filter_complex = (
                    f"[0:v]trim=start={a_start}:end={a_end},setpts=PTS-STARTPTS[va];"
                    f"[1:v]trim=start={b_start}:end={b_end},setpts=PTS-STARTPTS[vb];"
                    f"[va][vb]xfade=transition={tr.type}:duration={tr.duration}:offset=0[v]"
                )
                cmd = [
                    "-i", str(Path(clip_a).resolve()),
                    "-i", str(Path(clip_b).resolve()),
                    "-filter_complex", filter_complex,
                    "-map", "[v]",
                    "-c:v", "libx264", "-qp", "0",
                    "-pix_fmt", info_a.pix_fmt,
                ]
                if x264_params:
                    cmd += ["-x264-params", x264_params]
                cmd.append(str(transition_output_path))
                _run_ffmpeg(cmd, ffmpeg_bin)
                out_start = cursor  # cursor already advanced past this run's content
                transition_outputs.append(
                    TransitionOutput(
                        str(transition_output_path), clip_a, clip_b, tr.type, tr.duration,
                        out_start, out_start + tr.duration,
                    )
                )
                ordered_segments.append(str(transition_output_path))

    # Final assembly: concat all ordered segments (each already a clean,
    # keyframe-starting, mutually-compatible-codec file) via -c copy.
    final_list_path = wd / "final_list.txt"
    with open(final_list_path, "w") as f:
        for seg in ordered_segments:
            f.write(f"file '{Path(seg).resolve()}'\n")
    _run_ffmpeg(
        ["-f", "concat", "-safe", "0", "-i", str(final_list_path), "-c", "copy", str(Path(output_path).resolve())],
        ffmpeg_bin,
    )

    return RenderResult(
        output_path=str(output_path),
        work_dir=str(wd),
        run_outputs=run_outputs,
        transition_outputs=transition_outputs,
    )
