"""Scene/shot boundary segmentation via PySceneDetect's ``AdaptiveDetector``,
unioned with motion-derivative local minima (``motion.py``), producing a
single candidate-boundary set honoring configurable min/max clip duration.

``AdaptiveDetector`` was chosen specifically (per spec line 20) for its
resistance to false triggers during camera panning/movement -- a plain
``ContentDetector`` threshold would misfire constantly on continuous drone
camera motion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from scenedetect import SceneManager, open_video
from scenedetect.detectors import AdaptiveDetector

from drone_video_ai.highlight_extraction.motion import MotionSample, find_local_minima_boundaries

DEFAULT_SCENE_THRESHOLD = 3.0  # AdaptiveDetector's adaptive_threshold default
DEFAULT_MIN_SCENE_LEN_FRAMES = 15  # AdaptiveDetector's own min_scene_len default


def detect_scene_boundaries(
    video_path: str,
    scene_threshold: float = DEFAULT_SCENE_THRESHOLD,
    min_scene_len_frames: int = DEFAULT_MIN_SCENE_LEN_FRAMES,
) -> List[float]:
    """Run PySceneDetect's AdaptiveDetector and return interior scene-cut
    timestamps (seconds) -- i.e. every scene's start time except the very
    first (which is always 0.0 and not a meaningful "cut")."""
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        AdaptiveDetector(adaptive_threshold=scene_threshold, min_scene_len=min_scene_len_frames)
    )
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    boundaries: List[float] = []
    for i, (start, _end) in enumerate(scene_list):
        if i == 0:
            continue  # the first scene's start (0.0) is not an interior cut
        boundaries.append(start.seconds)
    return boundaries


@dataclass
class CandidateBoundarySet:
    scene_boundaries: List[float]
    motion_minima_boundaries: List[float]
    union_boundaries: List[float]  # sorted, deduplicated, includes 0.0 and video duration


def _dedupe_sorted(values: List[float], tolerance: float = 1e-6) -> List[float]:
    if not values:
        return []
    out = [values[0]]
    for v in values[1:]:
        if v - out[-1] > tolerance:
            out.append(v)
    return out


def build_candidate_boundaries(
    video_path: str,
    duration: float,
    motion_samples: List[MotionSample],
    scene_threshold: float = DEFAULT_SCENE_THRESHOLD,
    min_scene_len_frames: int = DEFAULT_MIN_SCENE_LEN_FRAMES,
    motion_smoothing_window: int = 5,
    motion_min_gap_seconds: float = 1.0,
) -> CandidateBoundarySet:
    """Union PySceneDetect scene boundaries with motion-derivative-minima
    boundaries into a single sorted candidate-cut-point set that always
    includes 0.0 and ``duration`` as the outer bounds."""
    scene_boundaries = detect_scene_boundaries(
        video_path, scene_threshold=scene_threshold, min_scene_len_frames=min_scene_len_frames
    )
    motion_minima_boundaries = find_local_minima_boundaries(
        motion_samples,
        smoothing_window=motion_smoothing_window,
        min_gap_seconds=motion_min_gap_seconds,
    )

    union = sorted(set([0.0, duration] + scene_boundaries + motion_minima_boundaries))
    union = _dedupe_sorted(union)

    return CandidateBoundarySet(
        scene_boundaries=sorted(scene_boundaries),
        motion_minima_boundaries=sorted(motion_minima_boundaries),
        union_boundaries=union,
    )


def split_segments(
    union_boundaries: List[float],
    min_duration: float,
    max_duration: float,
    eps: float = 1e-6,
) -> List[tuple]:
    """Given the sorted candidate-boundary set (including 0.0 and total
    duration), greedily produce a list of ``(start, end)`` segment tuples
    such that:

    - every ``start``/``end`` is a member of ``union_boundaries`` (spec
      AC1.3's boundary-membership invariant -- this function only ever picks
      a cut point already present in that set, never an invented interior
      point);
    - every segment's duration falls within ``[min_duration, max_duration]``
      whenever the boundary set makes that achievable (spec AC1.4). At each
      step, take the NEAREST boundary that is at least ``min_duration`` away
      and no more than ``max_duration`` away. If no boundary is legal because
      every remaining one overshoots ``max_duration``, take the smallest
      overshoot -- a boundary-violating segment is preferred over inventing a
      non-boundary cut point.

    CHANGED 2026-08-01 -- audit finding 0, "segmentation is inert on 6 of 8
    corpus files". This function previously took the FARTHEST boundary within
    ``max_duration``, which meant that whenever the whole file fit inside
    ``max_duration`` it returned exactly one segment spanning the file and
    silently discarded every interior boundary it had just been handed.
    Measured over the whole 6-clip corpus mirror on 2026-08-01, with the
    default 2-15 s profile:

    ==================== ======== ============== ========== ==========
    clip                 duration union boundaries farthest   nearest
    ==================== ======== ============== ========== ==========
    split_003_s66         8.3 s          9             1          4
    split_001_s70        15.0 s         14             1          6
    split_002_s69        15.0 s         14             1          5
    split_004_s65        15.0 s         15             1          6
    instagram_reel_test  27.1 s         27             2         12
    viral_test_v2        14.6 s         15             1          6
    ==================== ======== ============== ========== ==========

    One segment makes the within-file rank undefined by construction, so
    ``sharpness`` and ``motion_smoothness`` came back null (see
    ``scoring_sharpness.min_max_normalize``) and the extractor could not rank
    highlights because it never produced more than one.

    **This choice is policy, not measurement, and is recorded as such.** Every
    boundary in this corpus comes from a motion-derivative minimum (zero scene
    cuts were detected in any of the six clips, independently reproducing
    ``data/reference_pack/``'s central finding), and those minima land roughly
    1-1.5 s apart because ``motion.find_local_minima_boundaries`` enforces a
    1.0 s minimum gap. With candidates that dense, ANY rule inside a 2-15 s
    window is choosing a segment length that the footage does not determine:
    the old rule chose the maximum, this one chooses the minimum, and the pack
    measured no cut rhythm that would justify a target in between -- inventing
    one would be exactly the invented constant this project prohibits. The
    nearest-legal rule is preferred because it is the only one of the two that
    lets the capability work: it yields 4-12 rankable candidates per clip,
    all within the configured bounds, versus one unrankable whole-file span.
    """
    boundaries = sorted(set(union_boundaries))
    if len(boundaries) < 2:
        return []

    segments: List[tuple] = []
    start = boundaries[0]
    end_of_video = boundaries[-1]

    while start < end_of_video - eps:
        candidates = [b for b in boundaries if b > start + eps]
        if not candidates:
            break

        legal = [
            b
            for b in candidates
            if min_duration - eps <= (b - start) <= max_duration + eps
        ]
        if legal:
            chosen = min(legal)
        else:
            overshooting = [b for b in candidates if (b - start) > max_duration + eps]
            if overshooting:
                # Every remaining candidate already overshoots max_duration --
                # take the smallest overshoot rather than inventing a cut point.
                chosen = min(overshooting)
            else:
                # Only sub-min_duration candidates remain, i.e. we are inside
                # the final short remainder of the video. Run to the end; the
                # tail-merge below folds it into its predecessor where it can.
                chosen = end_of_video

        segments.append((start, chosen))
        start = chosen

    # A final segment shorter than min_duration is an artefact of where the
    # boundaries happened to fall, not a candidate anyone asked for. Fold it
    # into its predecessor when doing so stays inside max_duration; otherwise
    # leave it, on the same principle as the overshoot branch above -- a
    # bounds-violating segment beats an invented cut point.
    if len(segments) >= 2 and (segments[-1][1] - segments[-1][0]) < min_duration - eps:
        tail_start, tail_end = segments[-1]
        prev_start, _prev_end = segments[-2]
        if (tail_end - prev_start) <= max_duration + eps:
            segments.pop()
            segments[-1] = (prev_start, tail_end)

    return segments
