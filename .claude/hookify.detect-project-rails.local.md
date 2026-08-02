---
name: detect-project-rails
enabled: true
event: prompt
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: \b(?:project\s+rails|vibe[-\s]code[-\s]common[-\s]sense|vc-sense|agents\.md|product[_\s]timeline|project\s+blueprint|scaffold\s+(?:a\s+)?new\s+project)\b
action: warn
---

You are being asked to scaffold or maintain project rails — the day-0 guidance system for an AI-built project (README, AGENTS.md, blueprint, roadmap, architecture notes, development cycle, and the `docs/PRODUCT_TIMELINE.md` tracker).

Invoke `/project-rails` before writing any product code. It reads the current repo state, creates only the missing rails from its bundled templates, and makes `docs/PRODUCT_TIMELINE.md` the source of truth for what to build next.

Boundaries:

- Single-feature spec inside an already-tracked project → `/spec-first`, not this skill.
- "What remains to do" punch list → `/whats-left`, not this skill.
- After rails exist, every PR must mark the completed timeline item `[x]` with its PR number.
