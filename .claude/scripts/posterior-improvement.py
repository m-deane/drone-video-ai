#!/usr/bin/env python3
"""P(candidate beats incumbent) — exact Beta-Binomial posterior over paired wins.

promotion-posterior.py answers questions about HISTORY and the ACTIVE version
(P(a candidate clears the gate), P(a fresh run is stable/faithful)). None of
those is P(candidate better than incumbent). This script computes that missing
statistic directly: for each rubric criterion and for the weighted overall, it
pairs the two versions' per_example records by example id (the same pairing
bootstrap-ci.py builds), counts per-example wins/ties/losses (candidate score
vs incumbent score), and reports the exact posterior probability that the
candidate's per-example win rate exceeds 1/2:

    P(theta > 0.5 | k wins of n decisive)  under a uniform Beta(1,1) prior

Ties carry no directional information and are excluded from n (reported
separately). With integer counts the posterior is Beta(k+1, n-k+1) with
integer parameters, so the CDF is an exact binomial tail sum — the same exact
machinery as promotion-posterior.py (its beta_cdf / beta_quantile / posterior,
lines 56-91, replicated here to stay a self-contained stdlib script).

NON-BLOCKING BY DESIGN (2026-08-01 ruling): this statistic is PRINTED at
/version-prompt compare and promote alongside the existing promotion posterior
and NEVER gates. At current dataset sizes every posterior threshold is
decision-isomorphic to an integer win-count cutoff the existing count/CI rules
already implement, and correlated judge passes make the exact posterior
overconfident by construction — acceptable as annotation, wrong as a gate.
Reversal trigger: "when the paired per-example dataset grows past ~15-20
examples (the boundary bootstrap-ci.py itself marks with its n<15 caveat), the
decision-isomorphism argument weakens and converting the posterior from
narration to selection is re-litigated on new data."

Pure Python 3 standard library only.

Usage:
    python3 .claude/scripts/posterior-improvement.py <scores.json> --from v1 --to v2
    python3 .claude/scripts/posterior-improvement.py <scores.json> --from v1 --to v2 --json

Exit codes: 0 on success; 1 on unreadable/malformed scores or unknown versions.
"""

import json
import math
import sys

CRI_LO, CRI_HI = 0.025, 0.975
WIDE = 0.40           # same 95%-CrI width flag as promotion-posterior.py
SMALL_N_THRESHOLD = 15  # echoes bootstrap-ci.py's small-n caveat boundary
ROUND_DECIMALS = 4    # scores are 4-decimal; mirror gate.py's rounded-delta rule


def die(message):
    print("posterior-improvement: error: " + message, file=sys.stderr)
    sys.exit(1)


# --- Exact Beta machinery, replicated from promotion-posterior.py lines 56-91 ---

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


def win_posterior(wins, losses):
    """Posterior summary over the win rate theta from decisive pairs only."""
    n = wins + losses
    a, b = wins + 1, n - wins + 1
    lo = beta_quantile(CRI_LO, a, b)
    hi = beta_quantile(CRI_HI, a, b)
    return {
        "wins": wins,
        "losses": losses,
        "n": n,
        "p_win": 1.0 - beta_cdf(0.5, a, b),
        "mean": a / (a + b),
        "cri95": [lo, hi],
        "wide": (hi - lo) > WIDE,
    }


# --- scores.json pairing, same shape bootstrap-ci.py parses ---

def parse_args(argv):
    path = from_ver = to_ver = None
    as_json = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--from":
            if i + 1 >= len(argv):
                die("--from requires a version name (e.g. --from v1)")
            from_ver = argv[i + 1]
            i += 2
        elif arg == "--to":
            if i + 1 >= len(argv):
                die("--to requires a version name (e.g. --to v2)")
            to_ver = argv[i + 1]
            i += 2
        elif arg == "--json":
            as_json = True
            i += 1
        elif arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif arg.startswith("-"):
            die("unknown option: " + arg)
        else:
            if path is not None:
                die("unexpected extra argument: " + arg)
            path = arg
            i += 1
    if path is None:
        die("missing path to scores.json\n"
            "  usage: posterior-improvement.py <scores.json> --from <ver> --to <ver> [--json]")
    if from_ver is None or to_ver is None:
        die("both --from <ver> (incumbent) and --to <ver> (candidate) are required")
    return path, from_ver, to_ver, as_json


def load_per_example(path, name):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        die("file not found: " + path)
    except (OSError, json.JSONDecodeError) as exc:
        die("could not read/parse '{0}': {1}".format(path, exc))
    versions = data.get("versions") if isinstance(data, dict) else None
    if not isinstance(versions, dict):
        die("'{0}' is not a recognised scores.json (missing top-level 'versions')".format(path))
    if name not in versions:
        available = ", ".join(sorted(versions.keys())) or "(none)"
        die("version '{0}' not found (available: {1})".format(name, available))
    block = versions[name]
    per_example = block.get("per_example") if isinstance(block, dict) else None
    if not isinstance(per_example, list) or not per_example:
        die("version '{0}' has an empty or invalid 'per_example' list".format(name))
    indexed = {}
    for record in per_example:
        if not isinstance(record, dict) or "example" not in record:
            die("a per_example record in version '{0}' is missing its 'example' id".format(name))
        indexed[record["example"]] = record
    return indexed


def rubric_value(record, metric):
    rubric = record.get("rubric")
    if isinstance(rubric, dict):
        value = rubric.get(metric)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def derive_criteria(from_idx, to_idx, shared_ids):
    """Union of rubric keys across both versions, first-seen order, minus 'overall'."""
    criteria, seen = [], set()
    for idx in (from_idx, to_idx):
        for example_id in shared_ids:
            rubric = idx[example_id].get("rubric")
            if not isinstance(rubric, dict):
                continue
            for key in rubric:
                if key != "overall" and key not in seen:
                    seen.add(key)
                    criteria.append(key)
    return criteria


def count_wins(from_idx, to_idx, metric, shared_ids):
    """(wins, ties, losses) for candidate (to) vs incumbent (from), rounded deltas."""
    wins = ties = losses = 0
    for example_id in shared_ids:
        from_val = rubric_value(from_idx[example_id], metric)
        to_val = rubric_value(to_idx[example_id], metric)
        if from_val is None or to_val is None:
            continue
        delta = round(to_val - from_val, ROUND_DECIMALS)
        if delta > 0:
            wins += 1
        elif delta < 0:
            losses += 1
        else:
            ties += 1
    return wins, ties, losses


def main(argv):
    path, from_ver, to_ver, as_json = parse_args(argv)
    from_idx = load_per_example(path, from_ver)
    to_idx = load_per_example(path, to_ver)
    shared_ids = sorted(set(from_idx) & set(to_idx))
    if not shared_ids:
        die("no example ids are shared between '{0}' and '{1}' -- cannot pair".format(
            from_ver, to_ver))
    criteria = derive_criteria(from_idx, to_idx, shared_ids)
    if not criteria:
        die("no rubric criteria found in the per_example records of '{0}' and '{1}'".format(
            from_ver, to_ver))
    metrics = criteria + ["overall"]

    rows = {}
    for metric in metrics:
        wins, ties, losses = count_wins(from_idx, to_idx, metric, shared_ids)
        summary = win_posterior(wins, losses)
        summary["ties"] = ties
        rows[metric] = summary

    small_n = len(shared_ids) < SMALL_N_THRESHOLD

    if as_json:
        print(json.dumps({
            "scores": path,
            "incumbent": from_ver,
            "candidate": to_ver,
            "paired_examples": len(shared_ids),
            "prior": "Beta(1,1) uniform",
            "non_blocking": True,
            "small_n_caveat": small_n,
            "posteriors": {
                metric: {
                    "wins": p["wins"], "ties": p["ties"], "losses": p["losses"],
                    "n_decisive": p["n"],
                    "p_win": round(p["p_win"], 4),
                    "mean": round(p["mean"], 4),
                    "cri95": [round(p["cri95"][0], 4), round(p["cri95"][1], 4)],
                    "wide": p["wide"],
                }
                for metric, p in rows.items()
            },
        }, indent=2))
        return 0

    print("P(candidate beats incumbent) -- exact Beta(1,1) posterior over paired "
          "per-example wins ({0} -> {1})".format(from_ver, to_ver))
    print("Paired examples: {0}   (ties carry no direction; excluded from n)".format(
        len(shared_ids)))
    print("NON-BLOCKING (2026-08-01 ruling): printed at compare and promote alongside")
    print("promotion-posterior.py; NEVER a gate. Reversal trigger: re-litigate")
    print("load-bearing use when the paired dataset exceeds ~15-20 examples.")
    print("")
    header = "{0:<14} {1:>7} {2:>4} {3:>8} {4:>10} {5:>18} {6:>6}".format(
        "metric", "W/T/L", "n", "P(win)", "post.mean", "95% CrI", "note")
    print(header)
    print("-" * len(header))
    any_wide = False
    for metric, p in rows.items():
        note = "WIDE" if p["wide"] else ""
        any_wide = any_wide or p["wide"]
        wtl = "{0}/{1}/{2}".format(p["wins"], p["ties"], p["losses"])
        print("{0:<14} {1:>7} {2:>4} {3:>8.4f} {4:>10.4f} [{5:.4f}, {6:.4f}] {7:>6}".format(
            metric, wtl, p["n"], p["p_win"], p["mean"],
            p["cri95"][0], p["cri95"][1], note))
    if small_n:
        print("")
        print("Caveat: n={0} paired examples (< {1}) -- the same small-n boundary".format(
            len(shared_ids), SMALL_N_THRESHOLD))
        print("bootstrap-ci.py marks: credible intervals are WIDE and P(win) is")
        print("indicative, not definitive. Treat as annotation for the Tier B human")
        print("confirmation, never as a promotion decision statistic.")
    elif any_wide:
        print("")
        print("Note: at least one 95% credible interval is wider than 0.40 -- the")
        print("evidence is thin for that metric; the posterior honestly says so.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
