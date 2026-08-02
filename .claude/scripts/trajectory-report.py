#!/usr/bin/env python3
"""Sprint-aggregate trajectory counts from .claude/activity.md — advisory only.

Reads the append-only activity log written by the PostToolUse/Stop hooks
(`.claude/hooks/log-activity.py:54`, `.claude/hooks/turn-boundary.py:65`) and
reports mechanical counts for a timestamp window: Bash commands, file edits,
distinct files touched, turn boundaries, and a repeated-identical-command retry
proxy.

Scope and deliberate non-goals:

* **Sprint-aggregate only.** The log records `timestamp | label | detail` with
  no agent attribution, so per-agent claims ("agent X took 40 calls where 5
  would do") are NOT derivable from this source and are not attempted.
* **No scoring, no thresholds, no verdict.** The numbers are advisory. No
  baseline exists for this repo; at least three real sprints of recorded data
  are needed before any of these counts could justify a hard gate.
* **Mechanical sources only.** Counts come from the hook-written log, never
  from an agent's self-reported step count (root CLAUDE.md Constitution rule 6).

Line formats consumed (both produced by the hooks named above):

    2026-08-01 23:02:11 | Bash  | wc -l .claude/activity.md
    2026-08-01 23:01:56 | Edit  | /path/to/file.md
    2026-08-01 23:01:42 | Write | /path/to/file.md
    --- TURN END 2026-08-01 23:02:06 | 5 edits, 112 cmds | a.md, b.md ---

Usage:
    python3 .claude/scripts/trajectory-report.py \
        --activity .claude/activity.md \
        --since 20260801-150000 [--until "2026-08-01 18:00:00"]

Accepted timestamp forms: "YYYY-MM-DD HH:MM:SS", "YYYY-MM-DDTHH:MM:SS",
"YYYYMMDD-HHMMSS" (the sprint_id prefix), and "YYYY-MM-DD" (midnight).

Exit codes: 0 = report written to stdout; 1 = bad arguments or unreadable log.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

BOUNDARY_PREFIX = "--- TURN END"
EDIT_LABELS = {"Edit", "Write"}
TS_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y%m%d-%H%M%S", "%Y-%m-%d")


def parse_ts(raw: str) -> datetime.datetime:
    """Parse a timestamp in any of the accepted forms, else raise ValueError."""
    text = raw.strip()
    for fmt in TS_FORMATS:
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"unparseable timestamp {raw!r} — expected one of: " + ", ".join(TS_FORMATS)
    )


def collect(lines, since: datetime.datetime, until: datetime.datetime) -> dict:
    """Count in-window activity lines. Malformed lines are skipped, not fatal."""
    commands: list[str] = []
    files: list[str] = []
    turns = 0

    for line in lines:
        line = line.rstrip("\n")
        if line.startswith(BOUNDARY_PREFIX):
            rest = line[len(BOUNDARY_PREFIX):].strip()
            stamp = rest.split("|", 1)[0].strip()
            try:
                ts = parse_ts(stamp)
            except ValueError:
                continue
            if since <= ts <= until:
                turns += 1
            continue

        parts = line.split(" | ", 2)
        if len(parts) != 3:
            continue
        try:
            ts = parse_ts(parts[0])
        except ValueError:
            continue
        if not (since <= ts <= until):
            continue

        label, detail = parts[1].strip(), parts[2].strip()
        if not detail:
            continue
        if label == "Bash":
            commands.append(detail)
        elif label in EDIT_LABELS:
            files.append(detail)

    return {
        "commands": len(commands),
        "edits": len(files),
        "distinct_files": len(set(files)),
        "turns": turns,
        # Retry proxy: every command occurrence beyond the first identical one.
        "repeats": len(commands) - len(set(commands)),
    }


def render(counts: dict, activity: Path, since: datetime.datetime,
           until: datetime.datetime) -> str:
    fmt = "%Y-%m-%d %H:%M:%S"
    rows = [
        ("Bash commands", counts["commands"]),
        ("File edits (Write/Edit/MultiEdit/NotebookEdit)", counts["edits"]),
        ("Distinct files touched", counts["distinct_files"]),
        ("Turn boundaries", counts["turns"]),
        ("Repeated identical commands (retry proxy)", counts["repeats"]),
    ]
    out = [
        "## Trajectory (advisory)",
        "",
        f"Window: {since.strftime(fmt)} → {until.strftime(fmt)}",
        f"Source: {activity} — sprint-aggregate; the log carries no agent attribution, "
        "so these counts describe the whole window, never an individual agent.",
        "",
        "| Metric | Count |",
        "|--------|-------|",
    ]
    out += [f"| {name} | {value} |" for name, value in rows]
    out += [
        "",
        "Advisory only: no thresholds, no verdict, no effect on the gate result. "
        "No baseline exists yet — at least three recorded sprints are needed before "
        "any of these counts could support a pass/fail rule.",
    ]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Sprint-aggregate trajectory counts from .claude/activity.md "
                    "(advisory only — no scoring, no thresholds)."
    )
    parser.add_argument("--activity", required=True,
                        help="path to the activity log (usually .claude/activity.md)")
    parser.add_argument("--since", required=True,
                        help="window start, inclusive (e.g. the sprint_id prefix "
                             "20260801-150000)")
    parser.add_argument("--until", default=None,
                        help="window end, inclusive; defaults to now")
    args = parser.parse_args(argv)

    try:
        since = parse_ts(args.since)
        until = parse_ts(args.until) if args.until else datetime.datetime.now()
    except ValueError as exc:
        print(f"trajectory-report: {exc}", file=sys.stderr)
        return 1

    if until < since:
        print(f"trajectory-report: --until ({until}) precedes --since ({since})",
              file=sys.stderr)
        return 1

    activity = Path(args.activity)
    try:
        text = activity.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"trajectory-report: cannot read {activity}: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(render(collect(text.splitlines(), since, until),
                            activity, since, until))
    return 0


if __name__ == "__main__":
    sys.exit(main())
