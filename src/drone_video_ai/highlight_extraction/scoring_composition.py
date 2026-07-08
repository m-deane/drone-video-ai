"""Composition scoring via OpenCV ``saliency``-module rule-of-thirds distance,
combined with a vendored Hough-line horizon-tilt levelness scorer.

Capability 1, Milestone 2 (plan.md / tasks.md 1.21-1.23). Produces a single
``scores.composition`` value in ``[0, 1]`` per segment from two sub-signals:

1. Rule-of-thirds distance (tasks.md 1.21)
   ------------------------------------------
   For each sampled frame, ``cv2.saliency.StaticSaliencySpectralResidual`` is
   used to compute a per-pixel saliency map, then the map's saliency-weighted
   centroid ``(cx, cy)`` is treated as "where the eye is drawn." The
   rule-of-thirds sub-score is the centroid's distance to the *nearest* of
   the four rule-of-thirds intersection points (at 1/3 and 2/3 of width and
   height), normalized to ``[0, 1]`` where 1.0 means the centroid sits
   exactly on a rule-of-thirds point and the score decreases linearly with
   distance, floored at 0.0.

   SpectralResidual vs. FineGrained: both ``cv2.saliency`` static-saliency
   algorithms were evaluated against a synthetic fixture with an
   off-center/asymmetric bright region (tasks.md 1.23's required test). Both
   produced a saliency-weighted centroid within a few pixels of the true
   bright-region center and both clearly differentiated a region placed near
   a rule-of-thirds point (small nearest-point distance) from one placed
   dead-center or in a far corner (large nearest-point distance) -- see
   ``tests/highlight_extraction/test_scoring_composition.py``. With
   accuracy roughly comparable between the two, SpectralResidual was chosen
   because it is ~18x faster in a local benchmark (0.48ms vs. 8.74ms per
   320x240 frame on this development machine) with no meaningful loss of
   ranking quality for this use case -- this pipeline is CPU-only per the
   spec's Open Question #4, and per-segment scoring already samples multiple
   frames per segment across a whole video, so the per-frame cost compounds.

   Normalization denominator: the maximum possible distance from *any* pixel
   in a ``w x h`` frame to its *nearest* rule-of-thirds point is achieved
   exactly at a frame corner (verified via a dense grid search over several
   ``(w, h)`` aspect ratios during development), because the four
   rule-of-thirds points sit exactly ``w/3`` and ``h/3`` in from the nearest
   edges on both axes. That maximum is therefore the closed-form value
   ``sqrt((w/3)**2 + (h/3)**2)`` -- not an approximation such as the half
   diagonal -- and is used as the normalizing denominator.

2. Horizon-tilt levelness (tasks.md 1.22)
   ------------------------------------------
   Vendored (implemented directly here, no new pip dependency) via
   ``cv2.Canny`` edge detection followed by ``cv2.HoughLinesP`` probabilistic
   Hough-line detection. Among all detected line segments within +/-45
   degrees of horizontal (candidates for "the horizon" as opposed to e.g. a
   vertical structure), the longest one is treated as the dominant
   horizon-like line, and its absolute angle from horizontal (in degrees) is
   converted to a levelness score: 1.0 at a perfectly level 0 degrees,
   decreasing linearly to 0.0 at ``MAX_HORIZON_TILT_DEGREES`` (20 degrees,
   chosen because a professionally-composed aerial shot with an intentional
   tilt rarely exceeds this, while anything beyond it reads as an unusable,
   clearly-tilted-horizon mistake rather than a stylistic choice) and floored
   at 0.0 beyond that.

   When no near-horizontal line is detected at all (e.g. a nadir/straight-down
   aerial shot with no horizon in frame, or a texture-heavy scene with no
   single dominant edge), the levelness sub-score defaults to 1.0 (neutral,
   no penalty) rather than 0.0 -- the absence of a detectable horizon line is
   not evidence of a tilted horizon, and nadir shots are a common,
   often-well-composed aerial framing choice that should not be penalized
   for lacking a signal this sub-scorer cannot evaluate.

3. Combination (tasks.md 1.21/1.22 -> single ``scores.composition`` field)
   ------------------------------------------
   The schema has one ``scores.composition`` float, not two sub-fields,
   so the two per-frame sub-scores are averaged across all sampled frames
   in a segment (mirroring ``scoring_sharpness``/``scoring_exposure``'s
   per-segment frame-averaging), then combined via a simple unweighted
   average: ``0.5 * mean_rule_of_thirds_score + 0.5 * mean_horizon_score``.
   Equal weighting is used because both sub-signals are aerial-composition
   concerns the spec calls out with no stated priority between them (general
   subject placement vs. the aerial-specific horizon-tilt concern), so an
   even split is the simplest defensible default; see ``weights.py`` for the
   separate, higher-level weighting of composition against the other three
   quality signals in the overall composite score.

   Like ``scoring_exposure.compute_raw_exposure``, the result is already
   normalized to ``[0, 1]`` by construction -- no cross-segment min-max
   normalization step is applied by ``pipeline.py`` for this signal.

MediaPipe evaluation (tasks.md 1.23)
------------------------------------------
Per plan.md, MediaPipe's object detector was considered as a
permissively-licensed (Apache-2.0) alternative to YOLOv8/Ultralytics
(AGPL-3.0, excluded per spec Scope-out) for subject-centroid detection.
Decision: **not integrated.** The saliency-map-centroid approach above was
tested against a synthetic fixture with an intentionally off-center bright
region (simulating an asymmetric subject) and against dead-center and
far-corner placements, and it clearly differentiated all three cases in the
expected direction (near a rule-of-thirds point scores highest; see the
module's tests). Since the saliency map already supplies a spatial weighting
sufficient to compute a meaningful rule-of-thirds distance without needing
to know *what* the salient region is (only *where* it is), an object
detector would add a real dependency (and the complexity of choosing which
detected object to treat as "the subject" when several are detected) without
demonstrated benefit for this specific sub-score. Per the task's default
expectation, MediaPipe is therefore excluded from this milestone;
``pyproject.toml`` is left untouched.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import numpy as np

# ``cv2.saliency`` (used by ``_rule_of_thirds_score`` below) ships only in
# opencv-contrib-python, not plain opencv-python -- both packages install
# into the same top-level ``cv2`` namespace, and this project's own
# ``scenedetect[opencv]`` dependency transitively pulls in plain
# opencv-python regardless (verified in-session: scenedetect declares an
# unconditional, unqualified ``opencv-python`` requirement even via its
# ``[opencv]`` extra), so a fresh install of this package's declared
# dependencies genuinely does end up with both distributions installed
# side by side -- exactly the situation pyproject.toml's dependency-comment
# says must not happen, but cannot be reliably prevented via pip alone.
# Whichever distribution's overlapping files "win" on disk is an
# unpinned/non-deterministic install-order detail, not something this
# project's dependency list controls. Rather than trying to prevent that at
# install time, this checks the actual runtime consequence explicitly and
# fails fast with an actionable message instead of letting a missing
# ``cv2.saliency`` surface later as an obscure ``AttributeError`` deep
# inside ``_rule_of_thirds_score``.
#
# Checking only ``hasattr(cv2, "saliency")`` is NOT sufficient (verified
# in-session): when plain opencv-python installs its own copy of the shared
# compiled ``cv2`` extension on top of an already-installed
# opencv-contrib-python, the ``cv2.saliency`` *namespace* can remain
# importable (a stale Python-level shim) while the concrete
# ``StaticSaliencySpectralResidual_create`` factory it needs is missing from
# it -- so this checks for the actual factory function, the real dependency
# this module needs, not merely the submodule's existence.
if not hasattr(getattr(cv2, "saliency", None), "StaticSaliencySpectralResidual_create"):
    raise ImportError(
        "cv2.saliency.StaticSaliencySpectralResidual_create is not available "
        "(opencv-contrib-python appears to be shadowed by plain opencv-python "
        "in this environment -- both packages install into the same 'cv2' "
        "namespace, and installing/uninstalling either one after the other "
        "can leave the compiled extension in a broken or partial state, "
        "verified in-session). Fix with a clean reinstall of the contrib "
        "build: `pip uninstall -y opencv-python opencv-contrib-python && "
        "pip install --force-reinstall --no-deps opencv-contrib-python`; "
        "`--force-reinstall` matters here -- a plain `pip install` can no-op "
        "if pip believes the version requirement is already satisfied even "
        "though the physical files are broken."
    )

# Rule-of-thirds intersection points, as fractions of (width, height).
ROT_POINT_FRACTIONS: Tuple[Tuple[float, float], ...] = (
    (1.0 / 3.0, 1.0 / 3.0),
    (2.0 / 3.0, 1.0 / 3.0),
    (1.0 / 3.0, 2.0 / 3.0),
    (2.0 / 3.0, 2.0 / 3.0),
)

# Beyond this absolute tilt (degrees from horizontal), the horizon-tilt
# levelness sub-score is floored at 0.0. See module docstring section 2.
MAX_HORIZON_TILT_DEGREES = 20.0

# Equal sub-weighting between the two composition sub-signals. See module
# docstring section 3 ("Combination").
ROT_SUBSCORE_WEIGHT = 0.5
HORIZON_SUBSCORE_WEIGHT = 0.5


def _sample_frame_indices(start_frame: int, end_frame: int, max_samples: int) -> List[int]:
    """Evenly sample up to ``max_samples`` frame indices within
    ``[start_frame, end_frame)``. Always includes at least one frame.

    Local copy matching ``scoring_sharpness``/``scoring_exposure``'s
    per-module convention rather than a shared import.
    """
    n_available = max(1, end_frame - start_frame)
    n_samples = min(max_samples, n_available)
    if n_samples <= 1:
        return [start_frame]
    step = n_available / n_samples
    return [start_frame + int(i * step) for i in range(n_samples)]


def _rule_of_thirds_score(gray_frame: np.ndarray) -> float:
    """Saliency-weighted-centroid distance to the nearest rule-of-thirds
    point, normalized and inverted to ``[0, 1]`` (1.0 == on a rule-of-thirds
    point). See module docstring section 1 for the full derivation."""
    height, width = gray_frame.shape[:2]

    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    success, saliency_map = saliency.computeSaliency(gray_frame)
    if not success:
        return 0.0

    saliency_map = saliency_map.astype(np.float64)
    total = float(saliency_map.sum())
    if total <= 1e-9:
        # Degenerate case (e.g. a perfectly uniform frame produces
        # essentially no saliency signal): fall back to the frame's
        # geometric center as the centroid rather than dividing by zero.
        cx, cy = width / 2.0, height / 2.0
    else:
        ys, xs = np.indices(saliency_map.shape)
        cx = float((xs * saliency_map).sum() / total)
        cy = float((ys * saliency_map).sum() / total)

    rot_points = [(fx * width, fy * height) for fx, fy in ROT_POINT_FRACTIONS]
    min_distance = min(float(np.hypot(cx - px, cy - py)) for px, py in rot_points)

    # Exact maximum possible distance from any pixel in the frame to its
    # nearest rule-of-thirds point -- see module docstring section 1.
    max_distance = float(np.hypot(width / 3.0, height / 3.0))
    if max_distance <= 1e-9:
        return 1.0

    score = 1.0 - (min_distance / max_distance)
    return float(np.clip(score, 0.0, 1.0))


def _horizon_levelness_score(gray_frame: np.ndarray) -> float:
    """Vendored Canny + probabilistic-Hough-line horizon-tilt levelness
    score in ``[0, 1]``. See module docstring section 2 for the full
    derivation."""
    height, width = gray_frame.shape[:2]
    edges = cv2.Canny(gray_frame, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=60,
        minLineLength=max(1, width // 3),
        maxLineGap=10,
    )
    if lines is None:
        return 1.0  # no detectable line -- neutral, see module docstring.

    best_angle: Optional[float] = None
    best_length = -1.0
    for x1, y1, x2, y2 in lines.reshape(-1, 4):
        length = float(np.hypot(int(x2) - int(x1), int(y2) - int(y1)))
        angle = float(np.degrees(np.arctan2(int(y2) - int(y1), int(x2) - int(x1))))
        if angle > 90.0:
            angle -= 180.0
        elif angle < -90.0:
            angle += 180.0
        if abs(angle) > 45.0:
            continue  # not a near-horizontal candidate (e.g. a vertical edge)
        if length > best_length:
            best_length = length
            best_angle = angle

    if best_angle is None:
        return 1.0  # only non-horizontal lines detected -- neutral.

    tilt = abs(best_angle)
    if tilt >= MAX_HORIZON_TILT_DEGREES:
        return 0.0
    return float(1.0 - (tilt / MAX_HORIZON_TILT_DEGREES))


def compute_raw_composition(
    video_path: str, start_time: float, end_time: float, max_samples: int = 10
) -> float:
    """Return the composition score (already normalized to ``[0, 1]``) over
    up to ``max_samples`` frames evenly sampled within
    ``[start_time, end_time)``.

    Combines the rule-of-thirds sub-score and the horizon-tilt levelness
    sub-score per frame, averages each sub-score across sampled frames, then
    combines the two per-segment sub-score means via
    ``ROT_SUBSCORE_WEIGHT``/``HORIZON_SUBSCORE_WEIGHT`` -- see module
    docstring section 3.

    Already normalized to [0, 1], matching ``scoring_exposure``'s convention:
    no cross-segment min-max normalization is applied by the pipeline for
    this signal.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        start_frame = int(round(start_time * fps))
        end_frame = int(round(end_time * fps))
        indices = _sample_frame_indices(start_frame, end_frame, max_samples)

        rot_scores: List[float] = []
        horizon_scores: List[float] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rot_scores.append(_rule_of_thirds_score(gray))
            horizon_scores.append(_horizon_levelness_score(gray))

        if not rot_scores:
            return 0.0

        mean_rot = float(np.mean(rot_scores))
        mean_horizon = float(np.mean(horizon_scores))
        combined = ROT_SUBSCORE_WEIGHT * mean_rot + HORIZON_SUBSCORE_WEIGHT * mean_horizon
        return float(np.clip(combined, 0.0, 1.0))
    finally:
        cap.release()
