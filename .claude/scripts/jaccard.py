#!/usr/bin/env python3
"""Mechanical pairwise Jaccard similarity for /stability-test run outputs.

The stability signal is sold as "mechanical and bias-free", which only holds if
the arithmetic is actually performed by a tool rather than an LLM following
prose instructions. This script IS that tool. Given 2+ text files (one prompt
run output per file), it:

  1. Tokenises each file exactly as documented in stability-test/SKILL.md:
     split on whitespace, lowercase every token, collapse duplicates into a set.
  2. Computes Jaccard(i, j) = |A intersect B| / |A union B| for every pair.
  3. Prints a pairwise matrix, the mean over all C(N, 2) pairs, and the verdict
     band the mean falls into:
        >= 0.80        STABLE
        0.50 - 0.79    MARGINAL
        0.30 - 0.49    UNSTABLE
        <  0.30        BROKEN
     (Two files of empty/whitespace-only content count as identical: 1.0.)

Pure Python 3 standard library only.

Usage:
    python3 .claude/scripts/jaccard.py run-1.md run-2.md [run-3.md ...]
    python3 .claude/scripts/jaccard.py --json run-*.md     # machine-readable
    python3 .claude/scripts/jaccard.py --select run-*.md   # also pick the consensus run

--select additionally reports the file with the highest mean pairwise Jaccard
against all others (ties broken by argument order) — Universal-Self-Consistency-
style selection done mechanically. Selection is supplementary: it never changes
the mean or the verdict band.

--json prints a single JSON object:
    {"files": [...], "pairwise": [{"a": ..., "b": ..., "jaccard": ...}, ...],
     "per_file_mean": {file: mean, ...}, "mean": ...,
     "verdict": "stable|marginal|unstable|broken",
     "selected": file-or-absent (present only with --select)}
"""

import json
import sys

VERDICT_BANDS = [
    (0.80, "stable"),
    (0.50, "marginal"),
    (0.30, "unstable"),
]
BROKEN = "broken"


def die(message):
    """Print a one-line error to stderr and exit non-zero (no traceback)."""
    print("jaccard: error: " + message, file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    """Parse [--json] [--select] file file [file ...]. Returns (paths, as_json, do_select)."""
    as_json = False
    do_select = False
    paths = []
    for arg in argv:
        if arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif arg == "--json":
            as_json = True
        elif arg == "--select":
            do_select = True
        elif arg.startswith("-"):
            die("unknown option: " + arg)
        else:
            paths.append(arg)
    if len(paths) < 2:
        die("need at least 2 files to compare\n"
            "  usage: jaccard.py [--json] [--select] <file1> <file2> [file3 ...]")
    return paths, as_json, do_select


def tokenise(path):
    """Read a file and return its whitespace-split, lowercased token set."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        die("file not found: " + path)
    except OSError as exc:
        die("could not read file '{0}': {1}".format(path, exc.strerror or str(exc)))
    return set(text.lower().split())


def jaccard(set_a, set_b):
    """|A intersect B| / |A union B|. Two empty sets are identical -> 1.0."""
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def verdict_for(mean_score):
    """Map a mean Jaccard score to its verdict band."""
    for floor, label in VERDICT_BANDS:
        if mean_score >= floor:
            return label
    return BROKEN


def main(argv):
    paths, as_json, do_select = parse_args(argv)
    token_sets = [tokenise(path) for path in paths]

    pairs = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            pairs.append({
                "a": paths[i],
                "b": paths[j],
                "jaccard": jaccard(token_sets[i], token_sets[j]),
            })

    mean_score = sum(pair["jaccard"] for pair in pairs) / len(pairs)
    verdict = verdict_for(mean_score)

    per_file_mean = {}
    for idx, path in enumerate(paths):
        scores = [
            pair["jaccard"]
            for k, pair in enumerate(pairs)
            if pair["a"] == path or pair["b"] == path
        ]
        per_file_mean[path] = sum(scores) / len(scores)
    selected = None
    if do_select:
        best = max(per_file_mean.values())
        selected = next(p for p in paths if per_file_mean[p] == best)

    if as_json:
        payload = {
            "files": paths,
            "pairwise": pairs,
            "per_file_mean": {p: round(v, 4) for p, v in per_file_mean.items()},
            "mean": round(mean_score, 4),
            "verdict": verdict,
        }
        if do_select:
            payload["selected"] = selected
        print(json.dumps(payload, indent=2))
        return 0

    print("Pairwise Jaccard similarity (whitespace-tokenised, lowercase, set-based)")
    print("Files: {0}   Pairs: {1}".format(len(paths), len(pairs)))
    print("")
    width = max(len(pair["a"]) + len(pair["b"]) for pair in pairs) + 4
    for pair in pairs:
        label = "{0} vs {1}".format(pair["a"], pair["b"])
        print("{0:<{1}} {2:.4f}".format(label, width, pair["jaccard"]))
    print("")
    print("Mean: {0:.4f}".format(mean_score))
    print("Verdict: {0}  (>=0.80 stable | 0.50-0.79 marginal | <0.50 unstable | <0.30 broken)".format(
        verdict.upper()))
    if do_select:
        print("Selected: {0}  (mean pairwise {1:.4f}; ties break by argument order; "
              "selection never changes the verdict)".format(selected, per_file_mean[selected]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
