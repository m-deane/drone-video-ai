"""Active-picture-area detection, so scorers measure the picture rather than
the letterbox mask.

Why this module exists
----------------------
``data/reference_pack/`` measured this project's own corpus and found that four
of its eight files carry **baked-in letterbox bars**: an active picture of
1280x544 inside a 1280x720 coded frame, bars at rows 0-87 and 632-719, bar luma
16, costing 24.4% of every frame (``editorial_style.json`` ->
``letterbox.horizontal_split_family``, all leaves ``confidence: "measured"``).

Until 2026-07-28 no scorer in this package cropped those bars, while *every*
measurement in the reference pack used ``crop=1280:544:0:88``. The measured
consequence, reproduced by running the real pipeline on
``split_001_s70.mp4`` and again on the same file pre-cropped:

    exposure  letterboxed 0.7556   cropped 1.0000   delta +0.2444

0.2444 is exactly the pack's measured ``content_cost`` of 24.4%. The mechanism:
the bars code as luma 16 in a ``color_range: tv`` stream, OpenCV decodes to full
range, 16 maps to 0, and ``scoring_exposure.LOW_CLIP_THRESHOLD = 5`` therefore
counts every bar pixel as under-exposed. Exposure was scoring the mask, not the
picture. Composition was similarly affected (+0.0336) because the bar edge is a
full-width, high-contrast horizontal line -- a perfect false horizon.

Detection method
----------------
``ffmpeg cropdetect``, using the exact parameters the reference pack's own
regeneration recipe documents (``data/reference_pack/README.md`` section 5,
"Letterbox geometry"): ``cropdetect=limit=24:round=2:reset=0``. Using the pack's
own recipe rather than a fresh one means a disagreement between this module and
the pack is a real disagreement, not a parameter difference.

The pack's stated caveat is carried forward deliberately: ``limit=24`` proves
the bars are *below luma 24*, not that they are mathematically pure black. This
module therefore reports a detected active rect, never "the bars are black".
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from typing import Optional

# Verbatim from data/reference_pack/README.md section 5. Do not "tune" these
# without re-running the pack's recipe -- they are the parameters under which
# every letterbox fact in the pack was measured.
CROPDETECT_FILTER = "cropdetect=limit=24:round=2:reset=0"

# How much of the file to analyse. The pack's own run observed a single stable
# crop value across 247 samples of split_003_s66.mp4, so a short prefix is
# sufficient; 5s at 30fps is ~150 samples, the same order of magnitude.
DEFAULT_PROBE_SECONDS = 5.0

_CROP_RE = re.compile(r"crop=(\d+):(\d+):(\d+):(\d+)")


@dataclass(frozen=True)
class ActiveRect:
    """The active picture area within the coded frame, in pixels."""

    width: int
    height: int
    x: int
    y: int

    @property
    def is_full_frame(self) -> bool:
        return self.x == 0 and self.y == 0

    def crop(self, frame):
        """Return the active-area view of a decoded frame (a NumPy slice, not a
        copy). Applied to a frame whose dimensions do not match the coded frame
        this rect was detected from, this would silently mis-slice -- callers
        must pass frames from the same video."""
        return frame[self.y : self.y + self.height, self.x : self.x + self.width]


def detect_active_rect(
    video_path: str,
    probe_seconds: float = DEFAULT_PROBE_SECONDS,
    ffmpeg_bin: str = "ffmpeg",
) -> Optional[ActiveRect]:
    """Return the modal ``cropdetect`` rect over the first ``probe_seconds`` of
    ``video_path``, or ``None`` if ffmpeg emitted no crop line at all.

    Returns the MODAL value, not the last one: ``cropdetect`` refines its
    estimate frame by frame and a single transient reading (a dark frame early
    in a fade, for instance) should not decide the geometry for the whole file.
    """
    cmd = [
        ffmpeg_bin,
        "-nostats",
        "-loglevel", "info",
        "-t", str(probe_seconds),
        "-i", video_path,
        "-vf", CROPDETECT_FILTER,
        "-f", "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    matches = _CROP_RE.findall(proc.stderr)
    if not matches:
        return None

    modal, _count = Counter(matches).most_common(1)[0]
    w, h, x, y = (int(v) for v in modal)
    if w <= 0 or h <= 0:
        return None
    return ActiveRect(width=w, height=h, x=x, y=y)
