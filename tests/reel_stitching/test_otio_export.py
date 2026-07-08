"""AC2.4's schema/structural validation from plan.md task 2.14: the
``.otio`` half (task 2.12) and the CMX3600 ``.edl`` half (task 2.13), each
read back and checked mechanically -- never a manual/visual NLE check.

Per spec AC2.4's own text, "schema/structural validation is sufficient for
automated CI; actual NLE round-trip is a manual acceptance step" -- nothing
here opens a real NLE."""

from __future__ import annotations

import re

import opentimelineio as otio
import pytest

from drone_video_ai.reel_stitching.edit_manifest import EditEntry, EditManifest, TransitionSpec
from drone_video_ai.reel_stitching.otio_export import (
    DEFAULT_DURATION_TOLERANCE,
    EDIT_MANIFEST_RATE,
    OTIOExportError,
    edit_manifest_to_otio,
    export_edl,
    export_otio,
    validate_export,
)

# A well-formed CMX3600 event line, e.g.:
#   001  amp4     V     C        00:00:00:00 00:00:04:00 00:00:00:00 00:00:04:00
#   003  cmp4     V     D 030    00:00:00:15 00:00:04:00 00:00:07:00 00:00:10:15
# (the second form is how the installed cmx_3600 adapter represents a
# dissolve -- confirmed empirically in this session, not guessed).
_EDL_EVENT_LINE = re.compile(
    r"^(?P<event>\d{3})\s+(?P<reel>\S+)\s+(?P<track>[AV])\s+"
    r"(?P<edit_type>C|D)(?:\s+(?P<trans_dur>\d+))?\s+"
    r"(?P<src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+(?P<src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
    r"(?P<rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+(?P<rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
)
_TITLE_LINE = re.compile(r"^TITLE:\s*\S+")


def _assert_valid_timecode(tc: str, rate: float = EDIT_MANIFEST_RATE) -> None:
    hh, mm, ss, ff = (int(part) for part in tc.split(":"))
    assert 0 <= hh
    assert 0 <= mm < 60
    assert 0 <= ss < 60
    assert 0 <= ff < round(rate)


def _multi_entry_manifest(clip_a: str, clip_b: str, clip_c: str, clip_d: str) -> EditManifest:
    """Four entries: a hard cut, an ``xfade`` dissolve, a ``wipeleft``
    dissolve (CMX3600-lossy -- both degrade to a generic OTIO
    SMPTE_Dissolve/EDL "D" edit, see otio_export.py's module docstring),
    then a final hard cut."""
    return EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("xfade", 1.0)),
            EditEntry(clip_c, 0.5, 4.5, TransitionSpec("wipeleft", 0.5)),
            EditEntry(clip_d, 0.0, 3.0, TransitionSpec("cut", 0.0)),
        ]
    )


@pytest.fixture
def four_clip_paths(cuttable_clip_factory):
    """Four distinct synthetic source clips (see conftest.py's fixture
    docstring) -- otio_export.py never probes or reads clip content, only
    stores each ``clip_path`` as an OTIO ``ExternalReference`` string, but
    real files are used here for realism and to match this test suite's
    no-checked-in-binaries convention."""
    return [
        str(cuttable_clip_factory(name=f"{letter}.mp4", duration=6.0, fps=10, size="160x120"))
        for letter in ("a", "b", "c", "d")
    ]


def test_export_creates_nonempty_otio_and_edl_files(four_clip_paths, tmp_path):
    manifest = _multi_entry_manifest(*four_clip_paths)
    otio_path = tmp_path / "reel.otio"
    edl_path = tmp_path / "reel.edl"

    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    assert otio_path.exists()
    assert edl_path.exists()
    assert otio_path.stat().st_size > 0
    assert edl_path.stat().st_size > 0


def test_otio_readback_has_expected_clip_count_and_duration(four_clip_paths, tmp_path):
    manifest = _multi_entry_manifest(*four_clip_paths)
    otio_path = tmp_path / "reel.otio"
    export_otio(manifest, otio_path)

    read_back = otio.adapters.read_from_file(str(otio_path))
    clips = list(read_back.find_clips())

    assert len(clips) == len(manifest.entries) == 4
    assert read_back.duration().to_seconds() == pytest.approx(
        manifest.content_duration, abs=DEFAULT_DURATION_TOLERANCE
    )


def test_edl_has_well_formed_cmx3600_structure(four_clip_paths, tmp_path):
    manifest = _multi_entry_manifest(*four_clip_paths)
    edl_path = tmp_path / "reel.edl"
    export_edl(manifest, edl_path)

    lines = edl_path.read_text().splitlines()

    # A valid title line near the top.
    assert any(_TITLE_LINE.match(line) for line in lines[:3]), (
        f"No well-formed 'TITLE:' line found in first 3 lines: {lines[:3]!r}"
    )

    event_lines = [line for line in lines if _EDL_EVENT_LINE.match(line)]
    assert event_lines, "No well-formed CMX3600 event lines found in EDL output."

    event_numbers = []
    for line in event_lines:
        m = _EDL_EVENT_LINE.match(line)
        assert m is not None
        event_numbers.append(int(m.group("event")))
        for tc_group in ("src_in", "src_out", "rec_in", "rec_out"):
            _assert_valid_timecode(m.group(tc_group))
        assert m.group("edit_type") in ("C", "D")

    # Event numbers are non-decreasing (a dissolve's two component lines
    # legitimately share one event number -- standard CMX3600 behavior,
    # confirmed against this session's own generated output). The
    # deduplicated sequence must be strictly sequential starting at 1.
    assert event_numbers == sorted(event_numbers)
    unique_numbers = sorted(set(event_numbers))
    assert unique_numbers == list(range(1, len(unique_numbers) + 1)), (
        f"Event numbers are not sequential starting at 1: {unique_numbers!r}"
    )
    # 4 entries, 2 of which are dissolves -> 4 distinct events (one per
    # entry-to-entry cut/transition boundary rendered as its own event).
    assert len(unique_numbers) == 4

    # Both non-cut transitions in _multi_entry_manifest degrade to a
    # generic dissolve ("D") edit -- confirms the documented CMX3600
    # lossy-for-custom-transition-metadata behavior mechanically.
    dissolve_lines = [line for line in event_lines if _EDL_EVENT_LINE.match(line).group("edit_type") == "D"]
    assert len(dissolve_lines) == 2


def test_validate_export_passes_for_well_formed_manifest(four_clip_paths, tmp_path):
    manifest = _multi_entry_manifest(*four_clip_paths)
    otio_path = tmp_path / "reel.otio"
    edl_path = tmp_path / "reel.edl"
    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    result = validate_export(manifest, otio_path, edl_path)

    assert result.otio_clip_count == 4
    assert result.edl_clip_count == 4
    assert result.otio_duration == pytest.approx(manifest.content_duration, abs=DEFAULT_DURATION_TOLERANCE)
    assert result.edl_duration == pytest.approx(manifest.content_duration, abs=DEFAULT_DURATION_TOLERANCE)


def test_all_cut_manifest_has_plain_adjacency_and_no_dissolves(four_clip_paths, tmp_path):
    clip_a, clip_b, clip_c, _clip_d = four_clip_paths
    manifest = EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_c, 0.0, 4.0, TransitionSpec("cut", 0.0)),
        ]
    )
    assert manifest.content_duration == pytest.approx(12.0)

    otio_path = tmp_path / "cuts.otio"
    edl_path = tmp_path / "cuts.edl"
    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    timeline = edit_manifest_to_otio(manifest)
    assert not any(isinstance(child, otio.schema.Transition) for child in timeline.tracks[0])

    result = validate_export(manifest, otio_path, edl_path)
    assert result.otio_clip_count == 3
    assert result.edl_clip_count == 3
    assert result.otio_duration == pytest.approx(12.0, abs=DEFAULT_DURATION_TOLERANCE)
    assert result.edl_duration == pytest.approx(12.0, abs=DEFAULT_DURATION_TOLERANCE)

    event_types = {
        _EDL_EVENT_LINE.match(line).group("edit_type")
        for line in edl_path.read_text().splitlines()
        if _EDL_EVENT_LINE.match(line)
    }
    assert event_types == {"C"}


def test_transition_too_long_for_entry_raises_otio_export_error(four_clip_paths):
    clip_a, clip_b, _clip_c, _clip_d = four_clip_paths
    # entry 0 spans only 1.0s but its outgoing transition claims 3.0s --
    # larger than the entry itself can supply half of on its own side once
    # combined with any incoming shrink (here zero), so the effective
    # duration goes negative.
    manifest = EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 1.0, TransitionSpec("fade", 3.0)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("cut", 0.0)),
        ]
    )
    with pytest.raises(OTIOExportError):
        edit_manifest_to_otio(manifest)


def test_export_otio_propagates_otio_export_error(four_clip_paths, tmp_path):
    clip_a, clip_b, _clip_c, _clip_d = four_clip_paths
    manifest = EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 1.0, TransitionSpec("fade", 3.0)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("cut", 0.0)),
        ]
    )
    with pytest.raises(OTIOExportError):
        export_otio(manifest, tmp_path / "bad.otio")


def test_dual_transition_with_uneven_fractional_durations_exports_and_validates(
    four_clip_paths, tmp_path
):
    """Regression test: an entry with both an incoming and an outgoing
    non-cut transition, where the two transition durations land the entry's
    effective (post-shrink) duration on a fractional frame count (e.g.
    4.0 - 0.37/2 - 0.29/2 = 3.67s = 110.1 frames at 30fps), previously made
    the CMX3600 writer/reader round-trip inconsistently and raise
    ``EDLParseError: Source and record duration don't match`` on read-back --
    ``_seconds_to_rational``'s whole-frame rounding (otio_export.py) fixes
    this. 0.37/0.29 specifically reproduces the originally-reported bug;
    this asserts the full export -> validate round trip now succeeds
    end-to-end rather than merely not raising at export time."""
    clip_a, clip_b, clip_c = four_clip_paths[:3]
    manifest = EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 4.0, TransitionSpec("fade", 0.37)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("fade", 0.29)),
            EditEntry(clip_c, 0.0, 4.0, TransitionSpec("cut", 0.0)),
        ]
    )
    otio_path = tmp_path / "uneven.otio"
    edl_path = tmp_path / "uneven.edl"
    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    result = validate_export(manifest, otio_path, edl_path)

    assert result.otio_clip_count == 3
    assert result.edl_clip_count == 3
    assert result.otio_duration == pytest.approx(manifest.content_duration, abs=DEFAULT_DURATION_TOLERANCE)
    assert result.edl_duration == pytest.approx(manifest.content_duration, abs=DEFAULT_DURATION_TOLERANCE)


def test_single_entry_manifest_exports_and_validates(four_clip_paths, tmp_path):
    """Boundary case: a 1-entry EditManifest never enters
    ``edit_manifest_to_otio``'s transition-building loop (``range(len(entries)
    - 1)`` is empty), a distinct code path from every other test in this
    file, which all use 2+ entries."""
    (clip_a,) = four_clip_paths[:1]
    manifest = EditManifest(entries=[EditEntry(clip_a, 0.0, 4.0, TransitionSpec("cut", 0.0))])

    otio_path = tmp_path / "single.otio"
    edl_path = tmp_path / "single.edl"
    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    result = validate_export(manifest, otio_path, edl_path)
    assert result.otio_clip_count == 1
    assert result.edl_clip_count == 1
    assert result.otio_duration == pytest.approx(4.0, abs=DEFAULT_DURATION_TOLERANCE)
    assert result.edl_duration == pytest.approx(4.0, abs=DEFAULT_DURATION_TOLERANCE)


def test_validate_export_raises_otio_export_error_on_corrupted_edl(four_clip_paths, tmp_path):
    """``validate_export``'s docstring promises ``OTIOExportError`` on every
    validation failure. Before this fix, an adapter-level parse failure (e.g.
    the installed cmx_3600 adapter's own ``EDLParseError``, which does not
    inherit from ``OTIOExportError``) leaked out uncaught instead."""
    clip_a, clip_b = four_clip_paths[:2]
    manifest = EditManifest(
        entries=[
            EditEntry(clip_a, 0.0, 4.0, TransitionSpec("cut", 0.0)),
            EditEntry(clip_b, 0.0, 4.0, TransitionSpec("cut", 0.0)),
        ]
    )
    otio_path = tmp_path / "corrupt.otio"
    edl_path = tmp_path / "corrupt.edl"
    export_otio(manifest, otio_path)
    export_edl(manifest, edl_path)

    corrupted = edl_path.read_text().replace("00:00:00:00", "NOT_A_TIMECODE")
    edl_path.write_text(corrupted)

    with pytest.raises(OTIOExportError):
        validate_export(manifest, otio_path, edl_path)
