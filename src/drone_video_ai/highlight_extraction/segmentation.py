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
      whenever the boundary set makes that achievable. At each step, prefer
      the farthest available boundary that keeps the segment within
      ``max_duration``; if that farthest boundary would still be shorter
      than ``min_duration`` (boundaries are sparse), fall back to the
      nearest boundary that reaches ``min_duration`` even if it overshoots
      ``max_duration`` -- a boundary-violating segment is preferred over
      inventing a non-boundary cut point.
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

        within_max = [b for b in candidates if (b - start) <= max_duration + eps]
        if within_max:
            chosen = max(within_max)
            if (chosen - start) < min_duration - eps:
                meets_min = [b for b in candidates if (b - start) >= min_duration - eps]
                chosen = min(meets_min) if meets_min else end_of_video
        else:
            # Every remaining candidate already overshoots max_duration --
            # take the smallest overshoot rather than inventing a cut point.
            chosen = min(candidates)

        segments.append((start, chosen))
        start = chosen

    return segments
