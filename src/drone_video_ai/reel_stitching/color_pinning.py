"""Color-metadata pinning for xfade transition-window renders (plan.md task
2.4, spec AC2.2).

Reads ``color_range``/``color_primaries``/``color_trc``/``colorspace`` from
the two source clips flanking a transition via ``common/ffprobe.py``, and
constructs the matching ffmpeg output args so the transition-window render's
color metadata is never left to ffmpeg's default guessing.

Per plan.md's grounding note (confirmed in this repo's own sample footage):
these tags frequently read the literal string ``"unknown"`` or are entirely
absent from ffprobe's output. This module never substitutes a default for
either case -- when a tag is unknown/absent on the source, the corresponding
``-color_*``/``-colorspace`` ffmpeg flag is simply omitted from the encode
args (there is no ffmpeg CLI value that reliably forces "explicitly
unset" independent of codec/container, so omission is the closest
correct behavior), leaving the encoder's own "unspecified" default -- which
is what ffprobe will then report on the *output*, matching the source's own
"unknown"/absent state. This is verified by
``tests/reel_stitching/test_xfade_color_metadata.py``, which asserts output
tags exactly match source, including in the unknown/absent case.

If the two clips flanking a transition disagree on any of these four tags,
this module raises rather than silently picking one side's value -- pinning
to an arbitrary side would make the transition disagree with whichever clip
it wasn't drawn from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from drone_video_ai.common.ffprobe import SourceFileInfo, probe_source_file

# Tags that are unset/unknown in ffprobe's own vocabulary. Never treated as
# a real value to pin -- and never substituted with a default.
_UNKNOWN_TAG_VALUES = {None, "unknown", "unspecified"}

# Maps SourceFileInfo attribute name -> the ffmpeg output CLI flag that pins it.
_FIELD_TO_FFMPEG_FLAG = {
    "color_range": "-color_range",
    "color_primaries": "-color_primaries",
    "color_transfer": "-color_trc",
    "color_space": "-colorspace",
}


class ColorPinningError(RuntimeError):
    """Raised when the two clips flanking a transition disagree on a
    color-metadata tag, so no single correct pin value exists."""


@dataclass(frozen=True)
class PinnedColorMetadata:
    color_range: Optional[str]
    color_primaries: Optional[str]
    color_transfer: Optional[str]
    color_space: Optional[str]

    def to_ffmpeg_args(self) -> List[str]:
        """Return the generic ffmpeg output args pinning every *known* tag
        (``-color_range``/``-color_primaries``/``-color_trc``/
        ``-colorspace``). Tags that are unknown/absent on the source are
        omitted entirely (see module docstring) rather than defaulted."""
        args: List[str] = []
        for field_name, flag in _FIELD_TO_FFMPEG_FLAG.items():
            value = getattr(self, field_name)
            if value not in _UNKNOWN_TAG_VALUES:
                args += [flag, value]
        return args

    def to_x264_params(self) -> Optional[str]:
        """Return a ``-x264-params`` value string (``colorprim=...:
        transfer=...:colormatrix=...:fullrange=...``) pinning every *known*
        tag directly into libx264's VUI parameters, or ``None`` if every
        tag is unknown/absent.

        This exists because this build's libx264 wrapper does not reliably
        propagate the generic ``-color_primaries``/``-color_trc`` output
        flags into the encoded VUI (confirmed empirically in this
        environment: ffprobe on the resulting file omits those two tags
        even when the flags are passed), while ``-x264-params`` does. Since
        Milestone 1's lossless transition encode is libx264-only (see
        ``render.py``), this is the codec-specific mechanism actually used
        to satisfy "explicitly passed through, never left to ffmpeg's
        default guessing" for that encoder.
        """
        parts = []
        if self.color_primaries not in _UNKNOWN_TAG_VALUES:
            parts.append(f"colorprim={self.color_primaries}")
        if self.color_transfer not in _UNKNOWN_TAG_VALUES:
            parts.append(f"transfer={self.color_transfer}")
        if self.color_space not in _UNKNOWN_TAG_VALUES:
            parts.append(f"colormatrix={self.color_space}")
        if self.color_range not in _UNKNOWN_TAG_VALUES:
            if self.color_range == "tv":
                parts.append("fullrange=off")
            elif self.color_range == "pc":
                parts.append("fullrange=on")
        if not parts:
            return None
        return ":".join(parts)


def _assert_tags_agree(info_a: SourceFileInfo, info_b: SourceFileInfo) -> None:
    for field_name in _FIELD_TO_FFMPEG_FLAG:
        a = getattr(info_a, field_name)
        b = getattr(info_b, field_name)
        if a != b:
            raise ColorPinningError(
                f"Transition clips disagree on {field_name}: "
                f"{info_a.path!r}={a!r} vs {info_b.path!r}={b!r}. Milestone 1 "
                "requires both clips in a transition pair to agree on every "
                "color-metadata tag; refusing to silently pick one side."
            )


def get_transition_pinned_color_args(
    clip_a_path: str, clip_b_path: str, ffprobe_bin: str = "ffprobe"
) -> List[str]:
    """Probe both clips flanking a transition and return the ffmpeg output
    args pinning their (agreed) color metadata onto the transition-window
    encode. Raises :class:`ColorPinningError` if the two clips disagree on
    any tag."""
    info_a = probe_source_file(clip_a_path, ffprobe_bin=ffprobe_bin)
    info_b = probe_source_file(clip_b_path, ffprobe_bin=ffprobe_bin)
    _assert_tags_agree(info_a, info_b)
    pinned = PinnedColorMetadata(
        color_range=info_a.color_range,
        color_primaries=info_a.color_primaries,
        color_transfer=info_a.color_transfer,
        color_space=info_a.color_space,
    )
    return pinned.to_ffmpeg_args()


def get_transition_pinned_x264_params(
    clip_a_path: str, clip_b_path: str, ffprobe_bin: str = "ffprobe"
) -> Optional[str]:
    """Same precondition/agreement check as
    :func:`get_transition_pinned_color_args`, but returns a
    ``-x264-params`` value string (or ``None`` if every tag is
    unknown/absent) -- see :meth:`PinnedColorMetadata.to_x264_params`."""
    info_a = probe_source_file(clip_a_path, ffprobe_bin=ffprobe_bin)
    info_b = probe_source_file(clip_b_path, ffprobe_bin=ffprobe_bin)
    _assert_tags_agree(info_a, info_b)
    pinned = PinnedColorMetadata(
        color_range=info_a.color_range,
        color_primaries=info_a.color_primaries,
        color_transfer=info_a.color_transfer,
        color_space=info_a.color_space,
    )
    return pinned.to_x264_params()
