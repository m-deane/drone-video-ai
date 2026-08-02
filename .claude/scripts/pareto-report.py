#!/usr/bin/env python3
"""Per-example dominance matrix -- WHICH examples moved, and in which direction.

posterior-improvement.py answers HOW LIKELY the candidate is better: it counts
paired wins per metric and reports P(theta > 0.5) as an exact Beta(1,1)
posterior. bootstrap-ci.py answers HOW BIG the mean difference is, with a 95%
CI on it. Neither answers WHICH example moved: on the live summarisation-eval
registry posterior-improvement.py prints `conciseness 0/5/2` without ever
naming the two examples that regressed, and a CI on a mean cannot name them
either. This script computes that missing view directly.

It pairs two versions' per_example records by example id (the same pairing
bootstrap-ci.py and posterior-improvement.py build), then prints one row per
example and one column per metric -- every rubric criterion plus the rubric
`overall` plus stability `mean_jaccard` -- classifying each cell as a win, a
tie, or a loss for the candidate. It closes with a Pareto-front summary over
those cells and, most importantly, an explicit list of every per-example loss
that falls OUTSIDE the noise band. /version-prompt Step 4 requires those losses
to be named in the promotion request; before this script nothing named them.

It does NOT compute or restate P(win) -- that is posterior-improvement.py's
statistic and duplicating it would invite two numbers drifting apart.

TWO TIE RULES, BOTH PRINTED (never silently reconciled):

  strict      round(delta, 4) == 0. Identical to posterior-improvement.py's
              rule (its ROUND_DECIMALS = 4), so the strict W/T/L totals in this
              report reproduce that script's counts exactly, cell by cell.

  noise-band  a cell is a TIE when |delta| <= 0.02 (the /version-prompt
              noise-floor tolerance) OR when the metric's bootstrap 95% CI on
              the mean difference includes 0 ("within noise" -- the data-driven
              replacement for that fixed band, computed here with bootstrap-ci.py's
              seed, resample count and metric ordering, so the verdicts match).
              This is the rule the Pareto front and the beyond-noise loss list
              use, because it is the rule /version-prompt promotion policy uses.

Cells where the two rules disagree are marked (`w*` = strict win, noise tie;
`l*` = strict loss, noise tie) and both fronts are reported. A divergence is
information, not an inconsistency to hide.

SCORES ARE RELATIVE-ONLY (guardrail): the rubric criteria are LLM-judged, so
every number here is valid for comparing this candidate against this incumbent
and for nothing else -- never as an absolute quality measure. mean_jaccard
measures self-consistency, not correctness; maximising it rewards rigidity.
This report ranks nothing on a judge score alone; it locates movement for a
human to read.

Pure Python 3 standard library only (random for the bootstrap -- no numpy/scipy).

Usage:
    python3 .claude/scripts/pareto-report.py <scores.json> --from v2 --to v3
    python3 .claude/scripts/pareto-report.py <scores.json> --from v2 --to v3 --json

Exit codes: 0 on success; 1 on unreadable/malformed scores or unknown versions.
"""

import json
import random
import sys

# Bootstrap constants replicated from bootstrap-ci.py so the "within noise"
# verdicts in this report are the same verdicts that tool prints. Same seed,
# same resample count, same metric ordering, same single RNG stream.
SEED = 1234
RESAMPLES = 2000
CI_LOWER_PCT = 2.5
CI_UPPER_PCT = 97.5
MIN_PAIRED_EXAMPLES = 3   # below this a percentile bootstrap degenerates
SMALL_N_THRESHOLD = 15    # bootstrap-ci.py's small-n caveat boundary

ROUND_DECIMALS = 4        # posterior-improvement.py's rounded-delta rule
NOISE_BAND = 0.02         # /version-prompt Step 4/5 noise-floor tolerance

STABILITY_METRIC = "mean_jaccard"


def die(message):
    """Print a one-line error to stderr and exit non-zero (no traceback)."""
    print("pareto-report: error: " + message, file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    """Parse <scores.json> --from VER --to VER [--json]."""
    path = None
    from_ver = None
    to_ver = None
    as_json = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--from":
            if i + 1 >= len(argv):
                die("--from requires a version name (e.g. --from v2)")
            from_ver = argv[i + 1]
            i += 2
        elif arg == "--to":
            if i + 1 >= len(argv):
                die("--to requires a version name (e.g. --to v3)")
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
            "  usage: pareto-report.py <scores.json> --from <ver> --to <ver> [--json]")
    if from_ver is None or to_ver is None:
        die("both --from <ver> (incumbent) and --to <ver> (candidate) are required")
    return path, from_ver, to_ver, as_json


def load_indexed(path, name):
    """Return {example id -> record} for one version, or exit with a clear message."""
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


def metric_value(record, metric):
    """Extract one metric from a per_example record, or None when absent.

    Same accessor shape as bootstrap-ci.py: mean_jaccard lives under
    `stability`, every other metric under `rubric`.
    """
    if not isinstance(record, dict):
        return None
    if metric == STABILITY_METRIC:
        stability = record.get("stability")
        if isinstance(stability, dict):
            value = stability.get(STABILITY_METRIC)
            return float(value) if isinstance(value, (int, float)) else None
        return None
    rubric = record.get("rubric")
    if isinstance(rubric, dict):
        value = rubric.get(metric)
        return float(value) if isinstance(value, (int, float)) else None
    return None


def derive_criteria(from_idx, to_idx, shared_ids):
    """Union of per_example rubric keys across both versions, first-seen order.

    Excludes the computed 'overall' (re-added afterwards as its own column) so
    the tool works for any skill's rubric, not just summarisation. Identical
    derivation to bootstrap-ci.py and posterior-improvement.py.
    """
    criteria = []
    seen = set()
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


def mean(values):
    return sum(values) / len(values)


def percentile(sorted_values, pct):
    """Linear-interpolation percentile on an already-sorted list (pct in 0..100)."""
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = int(rank)
    high = min(low + 1, len(sorted_values) - 1)
    frac = rank - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * frac


def bootstrap_verdicts(deltas_by_metric, metrics, n_shared):
    """Metric -> "improvement" / "regression" / "within noise" / None.

    Replicates bootstrap-ci.py exactly: one RNG seeded with SEED, metrics
    consumed in the same order, metrics with fewer than MIN_PAIRED_EXAMPLES
    paired values skipped. None means "no bootstrap verdict available" -- the
    noise-band rule then falls back to the fixed +/-0.02 band alone.
    """
    verdicts = {}
    if n_shared < MIN_PAIRED_EXAMPLES:
        return {metric: None for metric in metrics}
    rng = random.Random(SEED)
    for metric in metrics:
        diffs = deltas_by_metric.get(metric) or []
        if len(diffs) < MIN_PAIRED_EXAMPLES:
            verdicts[metric] = None
            continue
        boot_means = []
        n = len(diffs)
        for _ in range(RESAMPLES):
            boot_means.append(mean([diffs[rng.randrange(n)] for _ in range(n)]))
        boot_means.sort()
        lo = percentile(boot_means, CI_LOWER_PCT)
        hi = percentile(boot_means, CI_UPPER_PCT)
        if lo > 0:
            verdicts[metric] = "improvement"
        elif hi < 0:
            verdicts[metric] = "regression"
        else:
            verdicts[metric] = "within noise"
    return verdicts


def classify_strict(delta):
    """posterior-improvement.py's rule: rounded delta == 0 is a tie."""
    rounded = round(delta, ROUND_DECIMALS)
    if rounded > 0:
        return "win"
    if rounded < 0:
        return "loss"
    return "tie"


def classify_noise(delta, metric_verdict):
    """The promotion-policy rule: inside the band, or inside the CI, is a tie."""
    if metric_verdict == "within noise":
        return "tie"
    rounded = round(delta, ROUND_DECIMALS)
    if abs(rounded) <= NOISE_BAND:
        return "tie"
    return "win" if rounded > 0 else "loss"


CELL_SYMBOL = {
    ("win", "win"): "W",
    ("tie", "tie"): "T",
    ("loss", "loss"): "L",
    ("win", "tie"): "w*",
    ("loss", "tie"): "l*",
}


def cell_symbol(strict, noise):
    """Symbol for one cell; divergent rules are marked, never hidden."""
    return CELL_SYMBOL.get((strict, noise), "{0}/{1}".format(strict[0].upper(), noise[0]))


def totals(cells, rule):
    """(wins, ties, losses) over a list of cell dicts under one rule."""
    wins = sum(1 for c in cells if c[rule] == "win")
    ties = sum(1 for c in cells if c[rule] == "tie")
    losses = sum(1 for c in cells if c[rule] == "loss")
    return wins, ties, losses


def pareto_front(cells, rule, from_ver, to_ver):
    """Pareto front over the per-example x per-metric objective cells.

    Each (example, metric) pair is one objective. The candidate dominates when
    it is no worse on every objective and strictly better on at least one, and
    symmetrically for the incumbent. When each side wins somewhere, neither
    dominates and both versions are on the front.
    """
    to_wins = sum(1 for c in cells if c[rule] == "win")
    to_losses = sum(1 for c in cells if c[rule] == "loss")
    if to_losses == 0 and to_wins > 0:
        return [to_ver]
    if to_wins == 0 and to_losses > 0:
        return [from_ver]
    # Either each side wins somewhere (mutually non-dominating) or every cell is
    # a tie (indistinguishable). Both cases leave both versions on the front.
    return sorted([from_ver, to_ver])


def build_cells(from_idx, to_idx, shared_ids, metrics, verdicts):
    """One dict per (example, metric) pair that has a numeric value on both sides."""
    cells = []
    for example_id in shared_ids:
        for metric in metrics:
            from_val = metric_value(from_idx[example_id], metric)
            to_val = metric_value(to_idx[example_id], metric)
            if from_val is None or to_val is None:
                continue
            delta = to_val - from_val
            cells.append({
                "example": example_id,
                "metric": metric,
                "from": from_val,
                "to": to_val,
                "delta": round(delta, ROUND_DECIMALS),
                "strict": classify_strict(delta),
                "noise": classify_noise(delta, verdicts.get(metric)),
            })
    return cells


def main(argv):
    path, from_ver, to_ver, as_json = parse_args(argv)
    if from_ver == to_ver:
        die("--from and --to are the same version ('{0}') -- nothing to compare".format(from_ver))

    from_idx = load_indexed(path, from_ver)
    to_idx = load_indexed(path, to_ver)

    shared_ids = sorted(set(from_idx) & set(to_idx))
    if not shared_ids:
        die("no example ids are shared between '{0}' and '{1}' -- cannot pair".format(
            from_ver, to_ver))

    criteria = derive_criteria(from_idx, to_idx, shared_ids)
    if not criteria:
        die("no rubric criteria found in the per_example records of '{0}' and '{1}' "
            "(expected rubric objects with per-criterion scores)".format(from_ver, to_ver))
    metrics = criteria + ["overall", STABILITY_METRIC]

    deltas_by_metric = {}
    for metric in metrics:
        diffs = []
        for example_id in shared_ids:
            from_val = metric_value(from_idx[example_id], metric)
            to_val = metric_value(to_idx[example_id], metric)
            if from_val is not None and to_val is not None:
                diffs.append(to_val - from_val)
        deltas_by_metric[metric] = diffs

    verdicts = bootstrap_verdicts(deltas_by_metric, metrics, len(shared_ids))
    cells = build_cells(from_idx, to_idx, shared_ids, metrics, verdicts)

    per_metric = {}
    for metric in metrics:
        metric_cells = [c for c in cells if c["metric"] == metric]
        s_w, s_t, s_l = totals(metric_cells, "strict")
        n_w, n_t, n_l = totals(metric_cells, "noise")
        per_metric[metric] = {
            "strict": {"wins": s_w, "ties": s_t, "losses": s_l},
            "noise_band": {"wins": n_w, "ties": n_t, "losses": n_l},
            "bootstrap_verdict": verdicts.get(metric),
        }

    beyond_noise_losses = [c for c in cells if c["noise"] == "loss"]
    within_noise_losses = [c for c in cells if c["strict"] == "loss" and c["noise"] == "tie"]
    front_noise = pareto_front(cells, "noise", from_ver, to_ver)
    front_strict = pareto_front(cells, "strict", from_ver, to_ver)
    small_n = len(shared_ids) < SMALL_N_THRESHOLD

    if as_json:
        print(json.dumps({
            "scores": path,
            "incumbent": from_ver,
            "candidate": to_ver,
            "paired_examples": len(shared_ids),
            "examples": shared_ids,
            "metrics": metrics,
            "tie_rules": {
                "strict": "round(delta, {0}) == 0".format(ROUND_DECIMALS),
                "noise_band": "|delta| <= {0} OR the metric's bootstrap 95% CI "
                              "includes 0".format(NOISE_BAND),
            },
            "small_n_caveat": small_n,
            "relative_only": True,
            "p_win_reported_by": "posterior-improvement.py (not recomputed here)",
            "cells": cells,
            "per_metric": per_metric,
            "beyond_noise_losses": beyond_noise_losses,
            "within_noise_losses": within_noise_losses,
            "pareto_front": front_noise,
            "pareto_front_strict": front_strict,
            "tie_rules_agree_on_front": front_noise == front_strict,
        }, indent=2))
        return 0

    print("Per-example dominance matrix ({0} -> {1})".format(from_ver, to_ver))
    print("Paired examples: {0}   Metrics: {1}".format(len(shared_ids), len(metrics)))
    print("P(candidate beats incumbent) is reported by posterior-improvement.py -- "
          "this report")
    print("locates WHICH examples move, not how likely the win is.")
    print("")
    print("Tie rules (both applied; disagreements marked, never reconciled silently):")
    print("  strict      round(delta, {0}) == 0 -- posterior-improvement.py's rule; "
          "the strict".format(ROUND_DECIMALS))
    print("              totals below reproduce that script's W/T/L counts.")
    print("  noise-band  |delta| <= {0:.2f} OR the metric's bootstrap 95% CI includes 0 "
          "(\"within".format(NOISE_BAND))
    print("              noise\", seed {0}/{1} resamples, matching bootstrap-ci.py). "
          "This is the".format(SEED, RESAMPLES))
    print("              promotion-policy rule; the Pareto front and the loss list use it.")
    print("Cells: W win  T tie  L loss  |  w* strict win, noise tie  |  "
          "l* strict loss, noise tie")
    print("")

    id_width = max([len("example")] + [len(str(i)) for i in shared_ids])
    col_widths = [max(len(m), 5) for m in metrics]
    header = "{0:<{1}}".format("example", id_width) + "".join(
        " {0:>{1}}".format(m, w) for m, w in zip(metrics, col_widths))
    print(header)
    print("-" * len(header))
    by_pair = {(c["example"], c["metric"]): c for c in cells}
    for example_id in shared_ids:
        row = "{0:<{1}}".format(example_id, id_width)
        for metric, width in zip(metrics, col_widths):
            cell = by_pair.get((example_id, metric))
            symbol = "-" if cell is None else cell_symbol(cell["strict"], cell["noise"])
            row += " {0:>{1}}".format(symbol, width)
        print(row)
    print("-" * len(header))

    print("")
    totals_header = "{0:<14} {1:>13} {2:>15} {3}".format(
        "metric", "strict W/T/L", "noise W/T/L", "bootstrap verdict")
    print(totals_header)
    print("-" * len(totals_header))
    for metric in metrics:
        block = per_metric[metric]
        strict_text = "{0}/{1}/{2}".format(
            block["strict"]["wins"], block["strict"]["ties"], block["strict"]["losses"])
        noise_text = "{0}/{1}/{2}".format(
            block["noise_band"]["wins"], block["noise_band"]["ties"],
            block["noise_band"]["losses"])
        verdict = block["bootstrap_verdict"] or "n/a (too few pairs)"
        print("{0:<14} {1:>13} {2:>15} {3}".format(metric, strict_text, noise_text, verdict))

    print("")
    print("Per-example losses OUTSIDE the noise band "
          "(/version-prompt Step 4 requires these to be")
    print("named explicitly in any promotion request):")
    if beyond_noise_losses:
        for cell in beyond_noise_losses:
            print("  - {0} / {1}: {2:.4f} -> {3:.4f} ({4:+.4f})".format(
                cell["example"], cell["metric"], cell["from"], cell["to"], cell["delta"]))
    else:
        print("  none")

    print("")
    print("Losses that the noise band absorbs (recorded so they are visible, not hidden):")
    if within_noise_losses:
        for cell in within_noise_losses:
            reason = ("metric CI includes 0"
                      if verdicts.get(cell["metric"]) == "within noise"
                      else "|delta| <= {0:.2f}".format(NOISE_BAND))
            print("  - {0} / {1}: {2:+.4f} -- tie by {3}".format(
                cell["example"], cell["metric"], cell["delta"], reason))
    else:
        print("  none")

    print("")
    print("Pareto front (objectives = every example x metric cell)")
    print("  noise-band rule: {{{0}}}".format(", ".join(front_noise)))
    print("  strict rule:     {{{0}}}".format(", ".join(front_strict)))
    if front_noise != front_strict:
        print("  The two rules disagree: cells marked w*/l* above are the difference.")
    if len(front_noise) == 1:
        print("  A single-member front is degenerate -- {0} is not worse on any "
              "objective.".format(front_noise[0]))
    else:
        print("  Both versions are on the front -- each wins at least one objective the "
              "other loses.")

    print("")
    if small_n:
        print("Caveat: n={0} paired examples (< {1}) -- the same small-n boundary "
              "bootstrap-ci.py".format(len(shared_ids), SMALL_N_THRESHOLD))
        print("marks. Per-cell classifications are indicative, not definitive.")
    print("Relative-only: the rubric criteria are LLM-judged, so these scores compare "
          "THIS candidate")
    print("to THIS incumbent and mean nothing as absolute quality. mean_jaccard measures "
          "self-")
    print("consistency, not correctness -- maximising it rewards rigidity. This report "
          "ranks nothing;")
    print("it locates movement for a human to read. It never gates a promotion.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
