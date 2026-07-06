"""Exposure scoring via a histogram-based over/under-exposure clipping
measure (NumPy/OpenCV), per plan.md's fallback to ffmpeg ``signalstats``.

Score = ``1 - clipped_fraction``, already in ``[0, 1]`` by construction --
no cross-segment normalization is needed (unlike sharpness/motion-smoothness),
matching the manifest's documented normalization method for this signal.
"""

from __future__ import annotations

from typing import List

import cv2
import numpy as np

# A pixel is considered "clipped" (over- or under-exposed) if its luma value
# falls at or below LOW_CLIP_THRESHOLD or at or above HIGH_CLIP_THRESHOLD on
# the 0-255 scale. These are conservative, documented thresholds -- not
# invented magic numbers buried inline; see highlight_extraction/weights.py
# for the scoring-weight configuration these values feed into.
LOW_CLIP_THRESHOLD = 5
HIGH_CLIP_THRESHOLD = 250


def _sample_frame_indices(start_frame: int, end_frame: int, max_samples: int) -> List[int]:
    n_available = max(1, end_frame - start_frame)
    n_samples = min(max_samples, n_available)
    if n_samples <= 1:
        return [start_frame]
    step = n_available / n_samples
    return [start_frame + int(i * step) for i in range(n_samples)]


def _clipped_fraction(gray_frame: np.ndarray) -> float:
    hist = cv2.calcHist([gray_frame], [0], None, [256], [0, 256]).flatten()
    total = float(gray_frame.size)
    if total == 0:
        return 0.0
    clipped = hist[: LOW_CLIP_THRESHOLD + 1].sum() + hist[HIGH_CLIP_THRESHOLD:].sum()
    return float(clipped / total)


def compute_raw_exposure(
    video_path: str, start_time: float, end_time: float, max_samples: int = 10
) -> float:
    """Return the exposure score (``1 - mean clipped_fraction``) over up to
    ``max_samples`` frames evenly sampled within ``[start_time, end_time)``.

    Already normalized to [0, 1]: 1.0 means no clipped pixels observed across
    sampled frames, 0.0 means every sampled pixel was clipped.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        start_frame = int(round(start_time * fps))
        end_frame = int(round(end_time * fps))
        indices = _sample_frame_indices(start_frame, end_frame, max_samples)

        fractions: List[float] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fractions.append(_clipped_fraction(gray))

        if not fractions:
            return 0.0
        mean_clipped = float(np.mean(fractions))
        return max(0.0, 1.0 - mean_clipped)
    finally:
        cap.release()
