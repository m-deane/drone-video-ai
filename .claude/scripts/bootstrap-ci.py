#!/usr/bin/env python3
"""Bootstrap confidence-interval helper for /version-prompt promotion decisions.

The /version-prompt promotion gate uses a hand-set +/-0.02 noise-floor heuristic
to decide whether a candidate version's score change on a rubric criterion is a
real improvement or just scoring noise (a "tie"). That single hard-coded tolerance
is a guess: it ignores how many examples were scored and how variable the per-example
differences actually are.

This helper replaces that guess with a data-driven test. Given a scores.json
produced by the summarisation eval (versions -> {ver} -> per_example -> [...]),
it pairs examples across two versions by their example id, computes the example-wise
score difference (to - from) for each rubric criterion, the rubric overall, and
stability mean_jaccard, then builds a 95% bootstrap confidence interval on the mean
difference (~2000 resamples, fixed seed for reproducibility).

The rubric criteria are DERIVED FROM THE DATA -- the union of per_example rubric
keys across both versions (excluding 'overall'), in first-seen order -- so the
tool works for any skill's rubric, not just summarisation.

Fewer than 3 paired examples is refused with a non-zero exit: a percentile
bootstrap on n<3 degenerates (n=1 collapses the CI to the point estimate, so any
nonzero diff would read as a real change -- exactly the single-example
over-promotion this tool exists to prevent). Below 15 paired examples a caveat
is printed: treat verdicts as indicative, not definitive.

Interpretation, which hardens the /version-prompt noise-floor tolerance:
  - CI entirely above 0      -> "improvement" (the gain is real, not noise)
  - CI entirely below 0      -> "regression" (the drop is real)
  - CI includes 0            -> "within noise" -> treat as a TIE

A difference whose 95% CI includes 0 is a tie regardless of its point estimate: the
data cannot distinguish it from zero. This is the principled replacement for the
fixed +/-0.02 band -- the tolerance now scales with the observed variance and sample
size instead of being asserted up front.

Pure Python 3 standard library only (random for resampling -- no numpy/scipy).

Usage:
    python3 .claude/scripts/bootstrap-ci.py <scores.json> --from v2 --to v3
"""

import json
import random
import sys

# Fixed seed so the bootstrap CIs are reproducible across runs and machines.
SEED = 1234
RESAMPLES = 2000
CI_LOWER_PCT = 2.5
CI_UPPER_PCT = 97.5

# Fewer than this many paired examples and a percentile bootstrap is meaningless:
# n=1 collapses the CI to the point estimate (any nonzero diff reads as a real
# change), n=2 barely resamples. Refuse rather than mislead.
MIN_PAIRED_EXAMPLES = 3

# Below this many paired examples, percentile CIs undercover -- verdicts are
# indicative, not definitive. A caveat line is printed.
SMALL_N_THRESHOLD = 15


def die(message):
    """Print a one-line error to stderr and exit non-zero (no traceback)."""
    print("bootstrap-ci: error: " + message, file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    """Parse <scores.json> --from VER --to VER. Returns (path, from_ver, to_ver)."""
    path = None
    from_ver = None
    to_ver = None
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
            "  usage: bootstrap-ci.py <scores.json> --from <ver> --to <ver>")
    if from_ver is None or to_ver is None:
        die("both --from <ver> and --to <ver> are required")
    return path, from_ver, to_ver


def load_scores(path):
    """Read and JSON-parse scores.json, or exit non-zero with a clear message."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except FileNotFoundError:
        die("file not found: " + path)
    except OSError as exc:
        die("could not read file '{0}': {1}".format(path, exc.strerror or str(exc)))

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        die("could not parse JSON in '{0}': {1}".format(path, exc.msg))

    if not isinstance(data, dict) or "versions" not in data:
        die("'{0}' is not a recognised scores.json (missing top-level 'versions')".format(path))
    if not isinstance(data["versions"], dict):
        die("'versions' in '{0}' must be an object keyed by version name".format(path))
    return data


def get_version(data, name):
    """Return the per_example list for a named version, or exit if absent/malformed."""
    versions = data["versions"]
    if name not in versions:
        available = ", ".join(sorted(versions.keys())) or "(none)"
        die("version '{0}' not found in scores.json (available: {1})".format(name, available))
    block = versions[name]
    if not isinstance(block, dict) or "per_example" not in block:
        die("version '{0}' has no 'per_example' list".format(name))
    per_example = block["per_example"]
    if not isinstance(per_example, list) or not per_example:
        die("version '{0}' has an empty or invalid 'per_example' list".format(name))
    return per_example


def metric_value(example, metric):
    """Extract a metric value from one per_example record, or None if absent."""
    if not isinstance(example, dict):
        return None
    if metric == "mean_jaccard":
        stability = example.get("stability")
        if isinstance(stability, dict):
            return stability.get("mean_jaccard")
        return None
    rubric = example.get("rubric")
    if isinstance(rubric, dict):
        return rubric.get(metric)
    return None


def index_by_example(per_example, version_name):
    """Map example id -> record, exiting if any record lacks an 'example' id."""
    indexed = {}
    for record in per_example:
        if not isinstance(record, dict) or "example" not in record:
            die("a per_example record in version '{0}' is missing its 'example' id".format(version_name))
        indexed[record["example"]] = record
    return indexed


def derive_criteria(from_idx, to_idx, shared_ids):
    """Collect rubric criteria names from the data itself, in first-seen order.

    The criteria are the union of every per_example record's rubric keys across
    BOTH versions, excluding the computed 'overall'. Deriving them from the data
    (instead of hard-coding one task's rubric) makes the tool work for any
    skill's scores.json.
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


def paired_diffs(from_idx, to_idx, metric, shared_ids):
    """Return example-wise (to - from) diffs for a metric over shared example ids.

    Skips ids where either side lacks a numeric value for this metric.
    """
    diffs = []
    for example_id in shared_ids:
        from_val = metric_value(from_idx[example_id], metric)
        to_val = metric_value(to_idx[example_id], metric)
        if isinstance(from_val, (int, float)) and isinstance(to_val, (int, float)):
            diffs.append(float(to_val) - float(from_val))
    return diffs


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


def bootstrap_ci(diffs, rng):
    """95% bootstrap CI on the mean of paired differences via RESAMPLES resamples."""
    n = len(diffs)
    boot_means = []
    for _ in range(RESAMPLES):
        resample = [diffs[rng.randrange(n)] for _ in range(n)]
        boot_means.append(mean(resample))
    boot_means.sort()
    lo = percentile(boot_means, CI_LOWER_PCT)
    hi = percentile(boot_means, CI_UPPER_PCT)
    return lo, hi


def verdict_for(lo, hi):
    """Classify a CI relative to zero."""
    if lo > 0:
        return "improvement"
    if hi < 0:
        return "regression"
    return "within noise"


def main(argv):
    path, from_ver, to_ver = parse_args(argv)
    data = load_scores(path)

    from_examples = get_version(data, from_ver)
    to_examples = get_version(data, to_ver)

    from_idx = index_by_example(from_examples, from_ver)
    to_idx = index_by_example(to_examples, to_ver)

    shared_ids = sorted(set(from_idx) & set(to_idx))
    if not shared_ids:
        die("no example ids are shared between '{0}' and '{1}' -- cannot pair".format(from_ver, to_ver))
    if len(shared_ids) < MIN_PAIRED_EXAMPLES:
        die("only {0} paired example(s) shared between '{1}' and '{2}' -- a bootstrap CI "
            "needs at least {3}. With n<{3} the CI degenerates (n=1 collapses to the point "
            "estimate, so any nonzero diff reads as a real change). Sweep more examples "
            "before comparing.".format(len(shared_ids), from_ver, to_ver, MIN_PAIRED_EXAMPLES))

    rng = random.Random(SEED)
    criteria = derive_criteria(from_idx, to_idx, shared_ids)
    if not criteria:
        die("no rubric criteria found in the per_example records of '{0}' and '{1}' "
            "(expected rubric objects with per-criterion scores)".format(from_ver, to_ver))
    metrics = criteria + ["overall", "mean_jaccard"]

    rows = []
    for metric in metrics:
        diffs = paired_diffs(from_idx, to_idx, metric, shared_ids)
        if not diffs:
            rows.append((metric, None, None, None, "no data"))
            continue
        mean_diff = mean(diffs)
        if len(diffs) < MIN_PAIRED_EXAMPLES:
            # Some shared examples lack a numeric value for this metric; too few
            # pairs survive to bootstrap. Report the mean but refuse a verdict.
            rows.append((metric, mean_diff, None, None,
                         "insufficient pairs (n={0} < {1})".format(len(diffs), MIN_PAIRED_EXAMPLES)))
            continue
        lo, hi = bootstrap_ci(diffs, rng)
        rows.append((metric, mean_diff, lo, hi, verdict_for(lo, hi)))

    print("Bootstrap 95% CI on mean per-example difference ({0} -> {1})".format(from_ver, to_ver))
    print("Paired examples: {0}   Resamples: {1}   Seed: {2}".format(
        len(shared_ids), RESAMPLES, SEED))
    print("Criteria (derived from per_example rubric keys): {0}".format(", ".join(criteria)))
    print("A difference whose CI includes 0 is a TIE (within noise) -- "
          "the data-driven replacement for the fixed +/-0.02 noise floor.")
    if len(shared_ids) < SMALL_N_THRESHOLD:
        print("Caveat: n={0} paired examples (< {1}) -- percentile bootstrap CIs undercover "
              "at small n; treat these verdicts as indicative, not definitive.".format(
                  len(shared_ids), SMALL_N_THRESHOLD))
    print("")
    header = "{0:<14} {1:>10} {2:>22} {3}".format("metric", "mean_diff", "95% CI [lo, hi]", "verdict")
    print(header)
    print("-" * len(header))
    for metric, mean_diff, lo, hi, verdict in rows:
        if mean_diff is None:
            print("{0:<14} {1:>10} {2:>22} {3}".format(metric, "-", "-", verdict))
            continue
        if lo is None:
            print("{0:<14} {1:>+10.4f} {2:>22} {3}".format(metric, mean_diff, "-", verdict))
            continue
        ci_text = "[{0:+.4f}, {1:+.4f}]".format(lo, hi)
        print("{0:<14} {1:>+10.4f} {2:>22} {3}".format(metric, mean_diff, ci_text, verdict))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
