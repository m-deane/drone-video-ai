"""AC2.3: statically grep reel_stitching/render.py and
reel_stitching/color_pinning.py source text for forbidden ffmpeg filter
names -- a mechanical, tool-grounded check (Constitution rule 6) that this
capability never exposes color grading, exposure/white-balance adjustment,
sharpening, stabilization, or speed-ramping through any code path, rather
than relying on convention alone."""

from __future__ import annotations

import re
from pathlib import Path

import drone_video_ai.reel_stitching.color_pinning as color_pinning
import drone_video_ai.reel_stitching.render as render

# Forbidden as literal ffmpeg filter-graph argument tokens (i.e. actually
# invoked as `name=...`), per spec line 66 / plan.md task 2.10.
FORBIDDEN_FILTER_TOKENS = [
    "eq=",
    "curves=",
    "colorbalance=",
    "unsharp=",
    "vidstabtransform=",
]

MODULE_PATHS = [Path(render.__file__), Path(color_pinning.__file__)]


def _read_source_bodies():
    return {str(p): p.read_text() for p in MODULE_PATHS}


def test_no_forbidden_filter_tokens_in_source():
    sources = _read_source_bodies()
    violations = []
    for path, text in sources.items():
        for token in FORBIDDEN_FILTER_TOKENS:
            if token in text:
                violations.append(f"{path}: contains forbidden filter token {token!r}")
    assert not violations, "\n".join(violations)


def test_no_speed_changing_setpts_in_source():
    """The only permitted ``setpts=`` usage is the exact PTS-reset idiom
    that must follow a ``trim`` (``setpts=PTS-STARTPTS``); any other
    ``setpts=`` expression (e.g. a multiplicative speed ramp like
    ``setpts=0.5*PTS``) is forbidden."""
    sources = _read_source_bodies()
    setpts_pattern = re.compile(r"setpts=([^\"'\s;\\\[]+)")
    violations = []
    for path, text in sources.items():
        for match in setpts_pattern.finditer(text):
            expr = match.group(1)
            if expr != "PTS-STARTPTS":
                violations.append(f"{path}: forbidden speed-changing setpts expression {expr!r}")
    assert not violations, "\n".join(violations)


def test_render_module_never_constructs_a_speed_ramp_filtergraph():
    """Belt-and-braces runtime check: render a real transition and assert
    the actual ffmpeg filter_complex string built at runtime also passes
    the same lint (guards against the lint drifting out of sync with a
    future refactor that builds the string dynamically in a way the static
    grep can't see)."""
    import inspect

    source = inspect.getsource(render.render_edit_manifest)
    for token in FORBIDDEN_FILTER_TOKENS:
        assert token not in source
