#!/usr/bin/env python3
"""Beta-Binomial promotion posterior for /version-prompt decisions.

The template's conditions framework is described as Bayesian; this script is the
Bayesian inference behind that label for the versioning layer. With a uniform
Beta(1,1) prior it computes exact posteriors over three Bernoulli processes a
promotion decision actually rests on:

  1. promotion    — P(a candidate version of this skill clears the promotion
                    gate), from registry.yml version outcomes: n = versions with
                    eval evidence, k = versions ever promoted (status `active`
                    or `superseded` — superseded means formerly active). A
                    `candidate` with no decision yet is excluded (not a
                    Bernoulli outcome); a `rejected`/`retired` evaluated version
                    counts as a failure.
  2. stability    — P(a fresh example run of the ACTIVE version is stable),
                    from scores.json per_example: k = examples with stability
                    verdict "stable" (fallback: mean_jaccard >= 0.80), n = all.
  3. faithfulness — P(a fresh example run of the ACTIVE version is FAITHFUL),
                    same records, k = examples with verdict FAITHFUL.

With integer counts and the uniform prior, the posterior is Beta(k+1, n-k+1)
with integer parameters, so the CDF is an exact binomial tail sum
(math.comb — no scipy) and the 95% credible interval is found by bisection.
No approximation, no LLM, stdlib only.

Consumption contract (what /version-prompt does with this):
  - `compare` and `promote` run this script and print the table verbatim.
  - The stored promotion record must carry the three posterior lines.
  - A WIDE interval (95% CrI width > 0.40) adds a mandatory caution line —
    small-n evidence IS the honest state; per the 2026-07-31 decision the gate
    does NOT hard-fail on it.

Usage:
    python3 .claude/scripts/promotion-posterior.py .claude/versions/<skill>
    python3 .claude/scripts/promotion-posterior.py .claude/versions/<skill> --json

Exit codes: 0 on success (including WIDE posteriors); 1 on unreadable/absent
registry or malformed scores.
"""

import json
import math
import sys
from pathlib import Path

CRI_LO, CRI_HI = 0.025, 0.975
WIDE = 0.40


def die(message):
    print("promotion-posterior: error: " + message, file=sys.stderr)
    sys.exit(1)


def beta_cdf(x, a, b):
    """Exact Beta(a, b) CDF for integer a, b >= 1 via the binomial tail sum."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    n = a + b - 1
    return sum(
        math.comb(n, j) * (x ** j) * ((1.0 - x) ** (n - j)) for j in range(a, n + 1)
    )


def beta_quantile(p, a, b):
    """Invert the exact CDF by bisection (60 iterations ~ 1e-18 width)."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if beta_cdf(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def posterior(k, n):
    """Uniform-prior Beta-Binomial posterior summary for k successes of n."""
    a, b = k + 1, n - k + 1
    lo = beta_quantile(CRI_LO, a, b)
    hi = beta_quantile(CRI_HI, a, b)
    return {
        "k": k,
        "n": n,
        "mean": a / (a + b),
        "cri95": [lo, hi],
        "wide": (hi - lo) > WIDE,
    }


def load_registry(skill_dir):
    reg_path = skill_dir / "registry.yml"
    if not reg_path.is_file():
        die("no registry.yml under " + str(skill_dir))
    try:
        import yaml
    except ImportError:
        die("PyYAML is required to read registry.yml (verify-versions.py has the same dependency)")
    try:
        return yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        die("registry.yml unparseable: " + str(exc))


def promotion_counts(registry):
    """(k, n) over decided, evidence-bearing versions."""
    k = n = 0
    for entry in (registry.get("versions") or {}).values():
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("status", "")).lower()
        if status == "candidate":
            continue
        if not entry.get("eval_scores"):
            continue
        n += 1
        if status in ("active", "superseded"):
            k += 1
    return k, n


def active_example_counts(skill_dir, registry):
    """((stable_k, n), (faithful_k, n)) for the active version, or None."""
    active = registry.get("active_version")
    scores_path = skill_dir / "scores.json"
    if not active or not scores_path.is_file():
        return None
    try:
        data = json.loads(scores_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die("scores.json unreadable: " + str(exc))
    entry = (data.get("versions") or {}).get(active)
    if not isinstance(entry, dict):
        return None
    examples = entry.get("per_example") or []
    if not examples:
        return None
    stable = faithful = 0
    for ex in examples:
        stab = ex.get("stability") or {}
        if stab.get("verdict") == "stable" or (
            "verdict" not in stab and float(stab.get("mean_jaccard", 0.0)) >= 0.80
        ):
            stable += 1
        if (ex.get("faithfulness") or {}).get("verdict") == "FAITHFUL":
            faithful += 1
    n = len(examples)
    return (stable, n), (faithful, n), active


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("-")]
    if len(paths) != 1:
        die("usage: promotion-posterior.py <.claude/versions/skill-dir> [--json]")
    skill_dir = Path(paths[0])
    registry = load_registry(skill_dir)
    skill = registry.get("skill", skill_dir.name)

    rows = {}
    k, n = promotion_counts(registry)
    if n:
        rows["promotion"] = posterior(k, n)
    active_counts = active_example_counts(skill_dir, registry)
    active = None
    if active_counts:
        (sk, sn), (fk, fn), active = active_counts
        rows["stability"] = posterior(sk, sn)
        rows["faithfulness"] = posterior(fk, fn)
    if not rows:
        die("no decided versions with eval evidence and no active per-example scores — nothing to infer from")

    if as_json:
        print(json.dumps({
            "skill": skill,
            "active_version": active,
            "prior": "Beta(1,1) uniform",
            "posteriors": {
                name: {**p, "mean": round(p["mean"], 4),
                       "cri95": [round(p["cri95"][0], 4), round(p["cri95"][1], 4)]}
                for name, p in rows.items()
            },
        }, indent=2))
        return 0

    print(f"Beta-Binomial promotion posterior — {skill} (prior: uniform Beta(1,1); exact integer-parameter CrI)")
    if active:
        print(f"Active version: {active}")
    print(f"{'process':<14} {'k/n':>7} {'post. mean':>11} {'95% CrI':>18} {'note':>6}")
    print("-" * 60)
    any_wide = False
    for name, p in rows.items():
        note = "WIDE" if p["wide"] else ""
        any_wide = any_wide or p["wide"]
        print(f"{name:<14} {p['k']}/{p['n']:>4} {p['mean']:11.4f} "
              f"[{p['cri95'][0]:.4f}, {p['cri95'][1]:.4f}] {note:>6}")
    if any_wide:
        print("Caution: at least one 95% credible interval is wider than 0.40 — the")
        print("evidence is small-n and the posterior honestly says so. Per the")
        print("2026-07-31 decision this does not block promotion; carry these lines")
        print("into the promotion record so the decision's uncertainty is on file.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
