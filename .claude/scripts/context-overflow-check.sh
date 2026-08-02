#!/usr/bin/env bash
# Check if context usage exceeds 80% and emit a warning.
# Called as a PostToolUse hook. Reads the transcript path from
# the CLAUDE_TRANSCRIPT environment variable (if available) or
# attempts to find the most recent transcript.
# Exits silently if context data is unavailable.

set -euo pipefail

THRESHOLD="${CONTEXT_OVERFLOW_THRESHOLD:-80}"

# Try to find transcript path
TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ]; then
  TRANSCRIPT_DIR="$HOME/.claude/projects"
  if [ -d "$TRANSCRIPT_DIR" ]; then
    TRANSCRIPT=$(find "$TRANSCRIPT_DIR" -name "*.jsonl" -type f -mmin -5 2>/dev/null | head -1)
  fi
fi

[ -z "$TRANSCRIPT" ] && exit 0
[ ! -f "$TRANSCRIPT" ] && exit 0

# Parse the most recent usage from the transcript
PERCENT=$(python3 -c "
import json, sys, os

path = sys.argv[1]
expected = os.path.expanduser('~/.claude/')
if not os.path.realpath(path).startswith(expected):
    sys.exit(0)

try:
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    for line in reversed(lines[-20:]):
        try:
            d = json.loads(line.strip())
            if d.get('type') == 'assistant':
                u = d.get('message', {}).get('usage', {})
                if u:
                    total = u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
                    if total > 0:
                        print(int(min(100, (total / 200000) * 100)))
                        sys.exit(0)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
except Exception:
    pass
" "$TRANSCRIPT" 2>/dev/null)

[ -z "$PERCENT" ] && exit 0

if [ "$PERCENT" -ge "$THRESHOLD" ]; then
  printf 'CONTEXT_WARNING: Context usage is at %s%% (threshold: %s%%). Save any pending work and consider compacting.\n' "$PERCENT" "$THRESHOLD"
fi
