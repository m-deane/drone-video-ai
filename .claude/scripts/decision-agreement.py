#!/usr/bin/env python3
"""Mechanical decision-agreement score for /stability-test run outputs.

Token Jaccard (jaccard.py) false-negatives runs that agree on every DECISION but
phrase them differently — BAYESIAN-PARITY.md §7 documents K=5 runs that "agree
semantically on decisions" scoring 0.24-0.39 lexical Jaccard. This script is the
mechanical counterpart for that failure mode: it extracts each run's decision
tokens with fixed regexes (no LLM, no judgment), then computes pairwise Jaccard
over the decision-token sets.

Extraction (fixed, stdlib re only):
  1. Verdict vocabulary — ALL-CAPS words from a fixed list (PASS, FAIL, STABLE,
     MARGINAL, UNSTABLE, BROKEN, ACHIEVED, VALID, INVALID, COMPLETE, INCOMPLETE,
     SUPPORTED, UNSUPPORTED, UNCERTAIN, VERIFIED, HALLUCINATED, FAITHFUL,
     UNFAITHFUL, WINNER, REGRESSION, INCONCLUSIVE, TIE, SIGNAL, NOISE, MAJOR,
     MINOR, CONFIRMED, REFUTED, BLOCKED, APPROVED, REJECTED, YES, NO).
     Case-sensitive: only the capitalised verdict form counts as a decision.
  2. Numbers — standalone integers/decimals (counts, scores, totals).
  Each file's matches collapse into a set; duplicates don't matter.

Scoring per pair: Jaccard over the two decision-token sets. Both sets empty ->
1.0 (nothing decided, nothing disagreed); exactly one empty -> 0.0 (one run
decided, the other did not).

SUPPLEMENTARY SCORE ONLY: no verdict bands are attached — this score never
replaces token Jaccard, never maps onto the 0.80/0.50/0.30 thresholds, and is
never a promotion-gate or ACHIEVED-bar input. Low token Jaccard with decision
agreement 1.0 diagnoses format variance, not decision variance (fix L6, not L3).

Pure Python 3 standard library only.

Usage:
    python3 .claude/scripts/decision-agreement.py run-1.md run-2.md [run-3.md ...]
    python3 .claude/scripts/decision-agreement.py --json run-*.md   # machine-readable

--json prints a single JSON object:
    {"files": [...], "tokens": {file: [...], ...},
     "pairwise": [{"a": ..., "b": ..., "agreement": ...}, ...], "mean": ...}
"""

import json
import re
import sys

VERDICT_WORDS = (
    "PASS|FAIL|STABLE|MARGINAL|UNSTABLE|BROKEN|ACHIEVED|VALID|INVALID|"
    "COMPLETE|INCOMPLETE|SUPPORTED|UNSUPPORTED|UNCERTAIN|VERIFIED|"
    "HALLUCINATED|FAITHFUL|UNFAITHFUL|WINNER|REGRESSION|INCONCLUSIVE|TIE|"
    "SIGNAL|NOISE|MAJOR|MINOR|CONFIRMED|REFUTED|BLOCKED|APPROVED|REJECTED|YES|NO"
)
VERDICT_RE = re.compile(r"\b(?:" + VERDICT_WORDS + r")\b")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def die(message):
    """Print a one-line error to stderr and exit non-zero (no traceback)."""
    print("decision-agreement: error: " + message, file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    """Parse [--json] file file [file ...]. Returns (paths, as_json)."""
    as_json = False
    paths = []
    for arg in argv:
        if arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif arg == "--json":
            as_json = True
        elif arg.startswith("-"):
            die("unknown option: " + arg)
        else:
            paths.append(arg)
    if len(paths) < 2:
        die("need at least 2 files to compare\n"
            "  usage: decision-agreement.py [--json] <file1> <file2> [file3 ...]")
    return paths, as_json


def extract(path):
    """Read a file and return its decision-token set (verdict words + numbers)."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError:
        die("file not found: " + path)
    except OSError as exc:
        die("could not read file '{0}': {1}".format(path, exc.strerror or str(exc)))
    return set(VERDICT_RE.findall(text)) | set(NUMBER_RE.findall(text))


def agreement(set_a, set_b):
    """Jaccard over decision-token sets; both empty -> 1.0, one empty -> 0.0."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def main(argv):
    paths, as_json = parse_args(argv)
    token_sets = {path: extract(path) for path in paths}

    pairs = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            pairs.append({
                "a": paths[i],
                "b": paths[j],
                "agreement": agreement(token_sets[paths[i]], token_sets[paths[j]]),
            })
    mean_score = sum(pair["agreement"] for pair in pairs) / len(pairs)

    if as_json:
        print(json.dumps({
            "files": paths,
            "tokens": {p: sorted(token_sets[p]) for p in paths},
            "pairwise": pairs,
            "mean": round(mean_score, 4),
        }, indent=2))
        return 0

    print("Decision-agreement score (fixed verdict vocabulary + numbers, set-based)")
    print("Files: {0}   Pairs: {1}".format(len(paths), len(pairs)))
    print("")
    for path in paths:
        tokens = sorted(token_sets[path])
        print("{0}: {1}".format(path, " ".join(tokens) if tokens else "(no decision tokens)"))
    print("")
    width = max(len(pair["a"]) + len(pair["b"]) for pair in pairs) + 4
    for pair in pairs:
        label = "{0} vs {1}".format(pair["a"], pair["b"])
        print("{0:<{1}} {2:.4f}".format(label, width, pair["agreement"]))
    print("")
    print("Mean: {0:.4f}".format(mean_score))
    print("Supplementary score — no verdict bands; never replaces token Jaccard "
          "and never feeds a promotion gate or the ACHIEVED bar.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
