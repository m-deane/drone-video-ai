"""``EditManifest`` -> OpenTimelineIO (``.otio``) timeline export, and a
derived CMX3600 EDL (``.edl``) export, per plan.md tasks 2.12-2.13 and spec
AC2.4: "The pipeline emits both the primary JSON manifest and a derived
``.otio`` timeline; a CMX3600 EDL export succeeds via ``otioconvert``/
``otio-cmx3600-adapter`` and opens without error in at least one target NLE
format check (schema/structural validation is sufficient for automated CI;
actual NLE round-trip is a manual acceptance step)."

This is Capability 2's secondary, lossy-for-custom-transition-metadata
export (spec line 33) -- the JSON edit manifest remains the primary source
of truth (``edit_manifest.py``); this module never reads back an exported
``.otio``/``.edl`` file to reconstruct an ``EditManifest``, only to validate
it structurally (see :func:`validate_export`).

Grounding notes for the OTIO API calls below (confirmed in this session
against the installed ``opentimelineio`` 0.18.1 + ``otio-cmx3600-adapter``
1.0.0, not assumed from general familiarity):

- ``EditEntry``/``EditManifest`` carry no fps field (timecodes are float
  seconds throughout, per plan.md's edit-manifest schema and
  ``edit_manifest.py``'s own module docstring). OTIO's ``RationalTime``
  requires a rate, so this module fixes one: :data:`EDIT_MANIFEST_RATE`
  (30.0 fps), applied uniformly to every ``RationalTime``/``TimeRange`` it
  constructs. This is a documented modelling choice, not a per-clip
  measurement -- it does not need to match any source clip's real fps for
  the structural export/validation this module performs.
- ``otio.schema.Clip(name=..., media_reference=..., source_range=...)``,
  ``otio.schema.ExternalReference(target_url=...)``,
  ``otio.schema.Track(name=..., kind=otio.schema.TrackKind.Video)``,
  ``otio.schema.Transition(name=..., transition_type=..., in_offset=...,
  out_offset=...)``, and ``otio.schema.Timeline(name=..., tracks=[track])``
  constructor signatures were confirmed via
  ``help(cls.__init__)`` on the live installed classes (they are pybind11
  C-extension types under ``opentimelineio._otio``/``_opentime``, not pure
  Python, despite the top-level package being pure-Python wrapper modules).
- **Transition offset semantics** (confirmed empirically): a ``Transition``
  placed between two ``Clip`` children in a ``Track`` contributes **zero**
  to that ``Track``'s/``Timeline``'s ``.duration()`` regardless of its
  ``in_offset``/``out_offset`` values -- the track's total duration is
  simply the sum of its non-transition children's own (possibly trimmed)
  durations. This is OTIO's "handle-based" transition model: a transition
  normally *reuses* footage already counted within its neighboring clips'
  declared ranges, so it adds no extra program length.
  This project's own transition semantics (``EditManifest.content_duration``'s
  docstring: "a crossfade of duration D between two clips shortens the
  combined timeline by D, since the transition window is shared between
  them, not appended") are a *different* model -- ours has no extra handle
  footage beyond ``in_tc``/``out_tc``; the transition merges the tail D
  seconds of one entry and the head D seconds of the next into a single
  D-second output segment, netting one D-second reduction versus naive
  concatenation. To reconcile the two so that this module's exported
  timeline's total duration equals ``manifest.content_duration`` (which is
  what :func:`validate_export`/AC2.4 checks), each ``Clip`` this module
  builds has its *own* OTIO ``source_range`` duration pre-shrunk by half of
  every non-cut transition duration touching it (half from the head if the
  previous entry transitions into it, half from the tail if it transitions
  into the next entry), and the corresponding ``Transition``'s
  ``in_offset``/``out_offset`` are each set to that same half-duration --
  a symmetric split. This was verified empirically (not assumed): summing
  two half-shrunk clip durations either side of such a ``Transition``
  reproduces ``dur_a + dur_b - D`` exactly, matching
  ``content_duration``'s definition. This split is a deliberate, documented
  modelling choice for this lossy secondary export -- it does not need to
  (and does not attempt to) reproduce ``render.py``'s own internal
  frame-accurate effective-bounds computation, which serves a different,
  pixel-exact rendering job.
- **CMX3600 lossiness for custom transition names** (per spec line 33 and
  the module-level task instructions): OTIO's core ``Transition`` schema
  has only ``Transition.Type.SMPTE_Dissolve`` and ``Transition.Type.Custom``
  -- there is no field carrying an arbitrary named wipe direction such as
  this project's own ``"wipeleft"``/``"xfade"`` transition-spec type
  strings. Every non-cut ``TransitionSpec`` (any ``type`` other than
  ``"cut"``) is therefore mapped to a generic
  ``otio.schema.TransitionTypes.SMPTE_Dissolve``, regardless of its
  original type string (which is instead preserved only informationally, in
  the ``Transition``'s own ``name`` field). The CMX3600 EDL writer in turn
  renders any such transition as a generic dissolve ("D" edit type,
  duration in frames) -- there is no richer wipe-direction encoding in the
  format. This degradation is intentional and accepted per spec's own text
  calling this export "lossy-for-custom-transition-metadata," not a defect
  to silently paper over.
- **The installed CMX3600 writer mutates its input ``Timeline`` in place**
  (confirmed empirically in this session, reading
  ``otio_cmx3600_adapter/cmx_3600.py``'s ``EDLWriter.get_content_for_track_at_index``):
  writing an EDL reshapes the *same* ``Track``/``Clip``/``Transition``
  objects it was given (extending/shortening neighboring clips' declared
  ``source_range``s and zeroing/redistributing a ``Transition``'s
  ``in_offset``) to match CMX3600's own "b-side gets the whole transition"
  event-representation convention -- it does not operate on a private copy.
  Because of this, :func:`export_otio` and :func:`export_edl` each build
  their own fresh ``Timeline`` via :func:`edit_manifest_to_otio` rather than
  sharing one -- a shared instance risks each export's output depending on
  call order.
- ``otio.adapters.write_to_file``/``read_from_file`` infer the adapter from
  the path's file extension (``.otio`` -> the built-in ``otio_json``
  adapter; ``.edl`` -> the ``cmx_3600`` adapter, which
  ``otio.plugins.manifest.load_manifest()`` lists as installed and
  confirmed present via the separate ``otio-cmx3600-adapter`` package this
  session found registered at
  ``otio_cmx3600_adapter/cmx_3600.py``); this module still passes
  ``adapter_name`` explicitly for clarity and to be robust to a caller
  supplying a path without that extension. Reading a ``.edl`` back requires
  an explicit ``rate=`` kwarg (the cmx_3600 adapter's own ``read_from_string``
  defaults to 24fps and EDLs carry no embedded rate) -- this module always
  passes :data:`EDIT_MANIFEST_RATE` for that read-back, matching the rate
  every timecode was written at.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union

import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

from drone_video_ai.reel_stitching.edit_manifest import EditManifest

# Fixed frame rate assumed for every RationalTime/TimeRange this module
# constructs -- see module docstring. EditManifest/EditEntry carry no fps
# field of their own to derive this from.
EDIT_MANIFEST_RATE = 30.0

# The single video track this module ever builds. CMX3600 EDL only supports
# a single video track (confirmed in otio_cmx3600_adapter/cmx_3600.py's
# write_to_string, which raises exceptions.NotSupportedError otherwise), so
# this module never builds more than one.
DEFAULT_VIDEO_TRACK_NAME = "V1"

# AC2.5 elsewhere in Capability 2 uses +/-0.5s as its pacing tolerance; this
# module reuses the same figure as its default structural-validation
# duration tolerance (documented here, not silently inherited).
DEFAULT_DURATION_TOLERANCE = 0.5

# CMX3600 EDL style passed to the cmx_3600 writer -- 'avid' is the adapter's
# own default and produces '* FROM CLIP:' media-reference comment lines
# (confirmed against the installed adapter's VALID_EDL_STYLES mapping).
DEFAULT_EDL_STYLE = "avid"

PathLike = Union[str, "Path"]


class OTIOExportError(RuntimeError):
    """Raised when an EditManifest cannot be represented as a valid OTIO
    timeline (e.g. a transition's duration leaves an entry with
    non-positive effective clip duration), or when the AC2.4 structural
    validation check in :func:`validate_export` fails."""


@dataclass(frozen=True)
class ExportValidationResult:
    """Return value of :func:`validate_export` -- the read-back facts it
    checked, for callers that want to report/log them rather than just
    getting a pass/fail."""

    otio_clip_count: int
    otio_duration: float
    edl_clip_count: int
    edl_duration: float


def _seconds_to_rational(seconds: float) -> RationalTime:
    """Convert ``seconds`` to a ``RationalTime`` at :data:`EDIT_MANIFEST_RATE`,
    rounded to the nearest whole frame.

    Rounding here (rather than passing the raw fractional-frame float
    straight to ``RationalTime``) is required, not cosmetic: verified
    in-session that an unrounded fractional-frame value (e.g. a clip
    duration of 3.67s = 110.1 frames at 30fps, which arises routinely from
    ``_entry_shrink``'s half-transition-duration math on ordinary,
    non-adversarial transition durations) makes the CMX3600 writer/reader
    round-trip inconsistently between an event's source-side and
    record-side duration representations, producing a 1-frame mismatch that
    the ``otio-cmx3600-adapter`` itself rejects on read-back with
    ``EDLParseError: Source and record duration don't match``. Every
    ``RationalTime``/``TimeRange`` this module builds must therefore land on
    a whole-frame boundary."""
    return RationalTime(round(seconds * EDIT_MANIFEST_RATE), EDIT_MANIFEST_RATE)


def _entry_shrink(manifest: EditManifest, index: int) -> Tuple[float, float]:
    """Return ``(head_shrink, tail_shrink)`` in seconds for
    ``manifest.entries[index]`` -- half the duration of any non-cut
    transition touching this entry on that side (see module docstring for
    why half: it is the split that makes the exported timeline's total
    duration equal ``manifest.content_duration``)."""
    entries = manifest.entries
    head = 0.0
    if index > 0:
        prev_transition = entries[index - 1].transition_to_next
        if not prev_transition.is_cut:
            head = prev_transition.duration / 2.0
    tail = 0.0
    if index < len(entries) - 1:
        next_transition = entries[index].transition_to_next
        if not next_transition.is_cut:
            tail = next_transition.duration / 2.0
    return head, tail


def edit_manifest_to_otio(
    manifest: EditManifest, *, timeline_name: str = "edit_manifest"
) -> "otio.schema.Timeline":
    """Build (but do not write) an OTIO ``Timeline`` from ``manifest``, one
    video track, one ``Clip`` per ``EditEntry`` in order. ``cut`` transitions
    become plain clip adjacency (no ``Transition`` object between them); any
    other ``transition_to_next.type`` becomes an
    ``otio.schema.Transition(transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve)``
    between the two adjacent clips, with ``in_offset == out_offset ==
    transition_to_next.duration / 2.0`` (see module docstring for the
    grounding behind this split). Raises :class:`OTIOExportError` if any
    entry's effective (post-shrink) duration would be non-positive."""
    entries = manifest.entries

    clips = []
    for i, entry in enumerate(entries):
        head, tail = _entry_shrink(manifest, i)
        eff_start = entry.in_tc + head
        eff_duration = entry.duration - head - tail
        if eff_duration <= 0.0:
            raise OTIOExportError(
                f"Entry {i} ({entry.clip_path!r}) has non-positive effective "
                f"duration ({eff_duration:.4f}s) once the transition-window "
                "half-shrink from its neighboring transition(s) is applied "
                f"(head_shrink={head:.4f}s, tail_shrink={tail:.4f}s); the "
                "transition duration(s) touching this entry are too large "
                "for its trimmed content."
            )
        media_reference = otio.schema.ExternalReference(target_url=entry.clip_path)
        source_range = TimeRange(
            start_time=_seconds_to_rational(eff_start),
            duration=_seconds_to_rational(eff_duration),
        )
        clip = otio.schema.Clip(
            name=f"entry_{i}_{Path(entry.clip_path).name}",
            media_reference=media_reference,
            source_range=source_range,
        )
        clips.append(clip)

    track = otio.schema.Track(name=DEFAULT_VIDEO_TRACK_NAME, kind=otio.schema.TrackKind.Video)
    track.append(clips[0])
    for i in range(len(entries) - 1):
        transition = entries[i].transition_to_next
        if not transition.is_cut:
            half = _seconds_to_rational(transition.duration / 2.0)
            otio_transition = otio.schema.Transition(
                name=f"{transition.type}_{i}_to_{i + 1}",
                transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                in_offset=half,
                out_offset=half,
            )
            track.append(otio_transition)
        track.append(clips[i + 1])

    timeline = otio.schema.Timeline(
        name=timeline_name,
        tracks=[track],
        metadata={
            "drone_video_ai": {
                "edit_manifest_version": manifest.version,
                "target_duration": manifest.target_duration,
            }
        },
    )
    return timeline


def export_otio(
    manifest: EditManifest, path: PathLike, *, timeline_name: str = "edit_manifest"
) -> "otio.schema.Timeline":
    """Build a fresh OTIO timeline from ``manifest`` (via
    :func:`edit_manifest_to_otio`) and write it to ``path`` as OTIO's native
    JSON format (``adapter_name="otio_json"``). Returns the ``Timeline``
    object that was written (this exact object is never reused for
    :func:`export_edl` -- see module docstring on the CMX3600 writer's
    in-place mutation)."""
    timeline = edit_manifest_to_otio(manifest, timeline_name=timeline_name)
    otio.adapters.write_to_file(timeline, str(path), adapter_name="otio_json")
    return timeline


def export_edl(
    manifest: EditManifest,
    path: PathLike,
    *,
    timeline_name: str = "edit_manifest",
    rate: float = EDIT_MANIFEST_RATE,
    style: str = DEFAULT_EDL_STYLE,
) -> "otio.schema.Timeline":
    """Build a fresh OTIO timeline from ``manifest`` (via
    :func:`edit_manifest_to_otio`) and write it to ``path`` as a CMX3600 EDL
    (``adapter_name="cmx_3600"``) via the installed ``otio-cmx3600-adapter``
    plugin. Per CMX3600's own single-video-track limitation (enforced by the
    adapter itself), ``manifest`` may only ever produce one video track --
    always true here since :func:`edit_manifest_to_otio` never builds more
    than one. Returns the (adapter-mutated -- see module docstring)
    ``Timeline`` object that was passed to the writer; callers should not
    rely on its contents afterwards."""
    timeline = edit_manifest_to_otio(manifest, timeline_name=timeline_name)
    otio.adapters.write_to_file(
        timeline, str(path), adapter_name="cmx_3600", rate=rate, style=style
    )
    return timeline


def validate_export(
    manifest: EditManifest,
    otio_path: PathLike,
    edl_path: PathLike,
    *,
    duration_tolerance: float = DEFAULT_DURATION_TOLERANCE,
    edl_rate: float = EDIT_MANIFEST_RATE,
) -> ExportValidationResult:
    """AC2.4's schema/structural validation check, runnable in CI with no
    NLE involved: read both ``otio_path`` and ``edl_path`` back via
    ``otio.adapters.read_from_file`` and assert each read-back timeline has
    (a) exactly ``len(manifest.entries)`` clips and (b) a total duration
    matching ``manifest.content_duration`` within ``duration_tolerance``
    seconds. Raises :class:`OTIOExportError` on the first check that fails --
    including a malformed/unreadable ``.otio``/``.edl`` file, whose
    underlying adapter-level exception (e.g. ``otio_cmx3600_adapter``'s own
    ``EDLParseError``, which does not inherit from :class:`OTIOExportError`)
    is caught and re-raised as :class:`OTIOExportError` here, so this
    function always raises the one exception type its docstring promises.

    This is deliberately *not* a pixel/visual/NLE round-trip check -- per
    spec AC2.4, that stays a manual acceptance step; this function only
    confirms the exported files are well-formed and structurally faithful
    to the manifest's own accounting of clip count and total duration."""
    expected_clip_count = len(manifest.entries)
    expected_duration = manifest.content_duration

    try:
        otio_timeline = otio.adapters.read_from_file(str(otio_path))
    except Exception as exc:
        raise OTIOExportError(f".otio read-back at {otio_path!r} failed: {exc}") from exc
    otio_clips = list(otio_timeline.find_clips())
    otio_duration = otio_timeline.duration().to_seconds()
    if len(otio_clips) != expected_clip_count:
        raise OTIOExportError(
            f".otio read-back at {otio_path!r} has {len(otio_clips)} clip(s), "
            f"expected {expected_clip_count} (one per EditManifest entry)."
        )
    if abs(otio_duration - expected_duration) > duration_tolerance:
        raise OTIOExportError(
            f".otio read-back at {otio_path!r} has duration {otio_duration:.4f}s, "
            f"expected {expected_duration:.4f}s (manifest.content_duration) "
            f"within tolerance {duration_tolerance}s."
        )

    try:
        edl_timeline = otio.adapters.read_from_file(str(edl_path), rate=edl_rate)
    except Exception as exc:
        raise OTIOExportError(f".edl read-back at {edl_path!r} failed: {exc}") from exc
    edl_clips = list(edl_timeline.find_clips())
    edl_duration = edl_timeline.duration().to_seconds()
    if len(edl_clips) != expected_clip_count:
        raise OTIOExportError(
            f".edl read-back at {edl_path!r} has {len(edl_clips)} clip(s), "
            f"expected {expected_clip_count} (one per EditManifest entry)."
        )
    if abs(edl_duration - expected_duration) > duration_tolerance:
        raise OTIOExportError(
            f".edl read-back at {edl_path!r} has duration {edl_duration:.4f}s, "
            f"expected {expected_duration:.4f}s (manifest.content_duration) "
            f"within tolerance {duration_tolerance}s."
        )

    return ExportValidationResult(
        otio_clip_count=len(otio_clips),
        otio_duration=otio_duration,
        edl_clip_count=len(edl_clips),
        edl_duration=edl_duration,
    )
