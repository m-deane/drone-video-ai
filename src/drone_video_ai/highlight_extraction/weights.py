"""Documented, versioned scoring-weight configuration.

Per spec line 23 ("A documented, versioned scoring-weight configuration
(not hardcoded constants) so weights can be tuned per footage type without
code changes") and plan.md task 1.11: this is a plain Python module (not a
literal buried inside ``composite.py``) exposing a dataclass + named default
profiles, so a future footage-type-specific profile is a new constant here,
not a code change to the composite-scoring math.

Milestone 1 vs. Milestone 2 weight profiles
------------------------------------------
``composition`` stayed ``0.0`` in the Milestone-1 ``"default-v1"`` profile,
matching that milestone's deliberate deferral of composition scoring (its
score was always ``None``, so a nonzero weight there would have been a
latent bug, not a feature).

Milestone 2 (tasks.md 1.24) implements composition scoring for real (see
``scoring_composition.py``), so a new, immutable ``"default-v2"`` profile is
added below -- following the same immutable-named-profile pattern
``DURATION_PROFILES`` already establishes in this module -- rather than
mutating ``"default-v1"`` in place. ``"default-v1"`` is left exactly as it
was, so any code that explicitly requests it (e.g. re-scoring old footage
under the original Milestone-1 weighting) keeps getting the original
values.

Chosen split for ``"default-v2"``: equal quarters (0.25 each) across all
four signals. This keeps the three original signals (sharpness, exposure,
motion_smoothness) in exactly the same 1:1:1 relative proportion to each
other that Milestone 1 used, so introducing composition doesn't distort
their established relative importance -- it simply takes an even fourth
slice out of a total that used to be split three ways. There is no
spec-stated reason to weight composition more or less than the other three
signals, so the simplest, most defensible default is used.

``"default-v2"`` is also made the module's overall default (see
``DEFAULT_WEIGHTS_VERSION`` below), so ``pipeline.py``'s existing
``weights = default_weights()`` call site needs no code change to pick up
the new Milestone-2 default -- it is the default *parameter value* that
changed, not the call site (see also the comment at that call site in
``pipeline.py``).
"""

from __future__ import annotations

from dataclasses import dataclass

from drone_video_ai.common.manifest import ScoringWeights


@dataclass(frozen=True)
class WeightsProfile:
    """Named, immutable scoring-weight profile (mirrors ``DurationProfile``
    below). ``WEIGHTS_PROFILES`` looks these up by name so
    ``default_weights(weights_version=...)`` returns the *real* weight
    values for that named profile, rather than merely labeling whatever
    values happen to be hardcoded in the function body."""

    name: str
    sharpness: float
    exposure: float
    motion_smoothness: float
    composition: float


# Milestone 1: composition not yet scored -- kept exactly as originally
# shipped; see module docstring.
WEIGHTS_V1 = WeightsProfile(
    name="default-v1",
    sharpness=1.0 / 3.0,
    exposure=1.0 / 3.0,
    motion_smoothness=1.0 / 3.0,
    composition=0.0,
)

# Milestone 2: composition scored for real (scoring_composition.py); equal
# quarters across all four signals -- see module docstring for rationale.
WEIGHTS_V2 = WeightsProfile(
    name="default-v2",
    sharpness=0.25,
    exposure=0.25,
    motion_smoothness=0.25,
    composition=0.25,
)

WEIGHTS_PROFILES = {
    WEIGHTS_V1.name: WEIGHTS_V1,
    WEIGHTS_V2.name: WEIGHTS_V2,
}

# The module-wide default profile. Bumped from "default-v1" to "default-v2"
# for Milestone 2 -- see module docstring.
DEFAULT_WEIGHTS_VERSION = WEIGHTS_V2.name


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
    """Return the named scoring-weight profile identified by
    ``weights_version`` (default: the current module-wide default,
    ``"default-v2"`` as of Milestone 2 -- see module docstring).

    Looks the profile up in ``WEIGHTS_PROFILES`` by name, so passing an
    explicit ``weights_version`` (e.g. ``"default-v1"``) returns that
    profile's real, distinct weight values rather than always returning the
    same hardcoded numbers regardless of which version string was passed.
    """
    profile = WEIGHTS_PROFILES[weights_version]
    return ScoringWeights(
        weights_version=profile.name,
        sharpness=profile.sharpness,
        exposure=profile.exposure,
        motion_smoothness=profile.motion_smoothness,
        composition=profile.composition,
    )
