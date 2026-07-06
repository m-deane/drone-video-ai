"""Documented, versioned scoring-weight configuration.

Per spec line 23 ("A documented, versioned scoring-weight configuration
(not hardcoded constants) so weights can be tuned per footage type without
code changes") and plan.md task 1.11: this is a plain Python module (not a
literal buried inside ``composite.py``) exposing a dataclass + a named
default profile, so a future footage-type-specific profile is a new
constant here, not a code change to the composite-scoring math.

``composition`` MUST stay ``0.0`` in every Milestone 1 weight profile --
composition scoring (OpenCV ``saliency`` + Hough-line horizon-tilt) is
deferred to Milestone 2 (plan.md), so its score is always ``None`` and must
never receive nonzero weight, or the composite sum would silently include a
null value's coercion artifact.
"""

from __future__ import annotations

from dataclasses import dataclass

from drone_video_ai.common.manifest import ScoringWeights

DEFAULT_WEIGHTS_VERSION = "default-v1"


@dataclass(frozen=True)
class DurationProfile:
    """Named min/max segment-duration profile (spec AC1.4)."""

    name: str
    min_duration: float
    max_duration: float


# Default profile: 2-15s, per spec's stated default (spec AC1.4).
DEFAULT_DURATION_PROFILE = DurationProfile(name="default", min_duration=2.0, max_duration=15.0)

# Alternate named profile matching the legacy DJI_0355/manifest.json precedent
# (7-15s) -- documented here as an available profile, not hardcoded into the
# pipeline's control flow.
LEGACY_DJI_DURATION_PROFILE = DurationProfile(name="legacy-dji", min_duration=7.0, max_duration=15.0)

DURATION_PROFILES = {
    DEFAULT_DURATION_PROFILE.name: DEFAULT_DURATION_PROFILE,
    LEGACY_DJI_DURATION_PROFILE.name: LEGACY_DJI_DURATION_PROFILE,
}


def default_weights(weights_version: str = DEFAULT_WEIGHTS_VERSION) -> ScoringWeights:
    """Return the default Milestone-1 scoring-weight configuration.

    Sharpness, exposure, and motion_smoothness are weighted equally
    (1/3 each); composition is fixed at 0.0 (Milestone 1 -- not scored).
    """
    return ScoringWeights(
        weights_version=weights_version,
        sharpness=1.0 / 3.0,
        exposure=1.0 / 3.0,
        motion_smoothness=1.0 / 3.0,
        composition=0.0,
    )
