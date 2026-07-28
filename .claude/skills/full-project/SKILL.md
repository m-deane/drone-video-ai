---
name: full-project
description: "Autonomous end-to-end project builder — takes a problem statement or spec and delivers a fully developed, tested, quality-gated project in a single session. Chains brainstorming, planning, TDD implementation, multi-dimensional QA review, iterative fix cycles, and deployment. Use when the user says 'build me', 'full project', 'end to end', 'one-shot build', or provides a problem statement and wants a complete, working solution."
---

# Full Project — Autonomous Spec-Driven Development

Build a complete, production-quality project from a problem statement in one autonomous session. This skill orchestrates the entire development lifecycle observed across 18 mature projects — from spec through deploy — invoking existing skills at each phase rather than reimplementing them.

**Announce at start:** "I'm using the full-project skill to build this end-to-end."

<HARD-GATE>
Do NOT skip phases. Do NOT claim completion without evidence. Every phase produces a visible artifact. The only reasons to pause for human input are: genuinely ambiguous requirements (not resolvable by sensible defaults), stack/deploy-target choice when multiple are viable, or a blocked state after 3 fix attempts on the same issue.
</HARD-GATE>

## Phase 0 — Understand (≤2 minutes)

**Goal:** Lock down what to build. Default to sensible choices; only ask if genuinely ambiguous.

1. Read the user's problem statement or spec (passed as skill args or in the conversation)
2. If a spec file is provided (path or inline), read it and extract requirements
3. Determine:
   - **Stack**: Python (default) or Node/TypeScript (if the spec implies web app, React, Next.js)
   - **Project type**: CLI tool / REST API / Streamlit app / React app / Library/SDK / Desktop app
   - **Deploy target**: None (default) / HuggingFace Space / GitHub Pages / PyPI
   - **Name**: derive from the spec (kebab-case slug)
4. If any of the above are genuinely ambiguous (2+ equally valid choices), ask the user ONE question with options. Otherwise, pick the most natural choice and proceed.
5. **Output**: Print a 5-line brief:
   ```
   Project: <name>
   Type: <type>
   Stack: <stack>
   Deploy: <target or "none">
   Scope: <1-sentence summary>
   ```

## Phase 1 — Design (spec)

**Goal:** Produce a design spec with problem statement, scope, acceptance criteria, and out-of-scope.

1. Create the project directory if it doesn't exist
2. Initialise git: `git init && git commit --allow-empty -m "initial commit"`
3. Write `docs/spec.md` with these sections:
   - **Problem Statement**: what problem this solves and for whom
   - **Scope**: what is IN scope (functional requirements, numbered)
   - **Acceptance Criteria**: measurable, verifiable (each maps to a future test)
   - **Out of Scope**: what is explicitly excluded (prevents scope creep)
   - **Technical Decisions**: stack, key libraries, architecture pattern
4. Commit: `git add docs/spec.md && git commit -m "docs: add project spec"`
5. **Output artifact**: `docs/spec.md`

Each functional requirement in Scope must have at least one acceptance criterion phrased as "GIVEN <context>, WHEN <action>, THEN <observable result>". Minimum 5 criteria for any non-trivial project.

Do NOT pause for user approval of the spec — this is autonomous mode. The spec is a working document, not a contract.

## Phase 2 — Plan

**Goal:** Break the spec into bite-sized implementation tasks with file ownership and test strategy.

1. Write `docs/plan.md` with:
   - **File Structure**: every file to create, one line per file, with its responsibility
   - **Tasks**: numbered, each classified as MUST / SHOULD / COULD (MoSCoW), each with:
     - What to implement (concrete, not vague)
     - Which file(s) to create/modify (max 3 files per task; split if more)
     - What test(s) to write (TDD: test first, then implement)
     - Dependencies on other tasks (if any)
   - **Build sequence**: which tasks can run in parallel vs must be sequential
   - **Scope budget**: Maximum 15 MUST tasks per session. COULD tasks go to TODO.md immediately.
2. Tasks should be small enough for one subagent each (15-30 min of work)
3. Check for blockers before finalizing: run `which` for required tools (pytest/ruff/mypy or eslint/tsc). If a task needs external APIs or credentials, flag as RISK. If a credential is unavailable, scope-cut immediately.
4. Commit: `git add docs/plan.md && git commit -m "docs: add implementation plan"`
5. **Output artifact**: `docs/plan.md`

## Phase 3 — Scaffold

**Goal:** Create the project skeleton so implementation agents have a consistent structure to work in.

### Python projects:
```
<project-name>/
├── pyproject.toml          (hatchling build, [tool.pytest], [tool.ruff], [tool.mypy])
├── README.md               (title + one-liner from spec; "full docs below")
├── CLAUDE.md               (project context, stack, key paths, commands, architecture, anti-patterns)
├── .gitignore              (Python defaults — MUST exist before first git add)
├── .pre-commit-config.yaml (from dev-toolkit template if available)
├── src/<package_name>/     (or app.py + lib/ for Streamlit apps)
│   ├── __init__.py
│   └── (empty modules per plan)
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── TODO.md                 (empty, populated in Phase 6 with deferred items)
├── CHANGELOG.md            (initial "## [0.1.0] - YYYY-MM-DD" entry)
└── docs/
    ├── spec.md             (from Phase 1)
    └── plan.md             (from Phase 2)
```

### Node/TypeScript projects:
```
<project-name>/
├── package.json            (name, scripts: test/lint/build/start)
├── tsconfig.json
├── README.md
├── CLAUDE.md
├── .gitignore
├── src/                    (or App Router structure for Next.js)
│   └── index.ts
├── tests/
│   └── (empty)
├── TODO.md
├── CHANGELOG.md
└── docs/
    ├── spec.md
    └── plan.md
```

### For ALL project types:
- **Task runner detection**: Check for existing Makefile, pyproject.toml scripts, or package.json scripts. Use the first available. If none exist, create a Makefile with targets: `test`, `lint`, `type-check`, `run`, `clean`. Document the chosen task runner commands in CLAUDE.md.
- Store the resolved test/lint/type-check commands in `docs/plan.md` under a "Commands" section. All subsequent phases use THESE commands, not hardcoded `make test`.
- `CLAUDE.md` must document: project purpose, stack, key paths, how to test, how to run, architecture overview (if non-trivial), and key anti-patterns to avoid.
- Verify the test runner works: install it if missing (pytest/vitest), create a smoke test, run it. Do not proceed to Phase 4 with a broken test runner.

Commit: stage only project files explicitly (e.g., `git add pyproject.toml README.md CLAUDE.md .gitignore src/ tests/ docs/ TODO.md CHANGELOG.md`) — `git commit -m "feat: scaffold project structure"`

## Phase 4 — Implement (subagent-driven)

**Goal:** Execute the plan using one subagent per independent task, with TDD discipline.

1. Capture the test baseline: run the test suite and record exact pass/fail/skip counts.
2. Create a task list using TaskCreate for each task in the plan.
3. For each task (or parallel group of independent tasks), dispatch a subagent with:
   - The task description from the plan
   - The spec (for acceptance criteria reference)
   - The instruction: "Write the failing test FIRST, then implement to make it pass. For every function crossing a system boundary (file I/O, network, serialization, user input), handle errors explicitly and write at least one error-path test. Run the test and confirm it passes before reporting done."
   - File ownership boundaries (which files this agent may touch)
4. After each agent returns, the ORCHESTRATOR must independently verify:
   - Run the resolved test command to verify no regressions — do NOT trust the subagent's reported results
   - Compare pass/fail/skip against baseline. If a previously-passing test now fails, treat as regression and fix before proceeding.
   - If the subagent reported success but orchestrator run shows failures: treat the task as FAILED
   - Mark the task complete via TaskUpdate only after orchestrator verification
5. Before committing, run the full pre-commit gate: tests + lint + type-check (using resolved commands from Phase 3). Only commit if all pass.
6. After all tasks complete:
   - Run the full test suite one final time
   - Stage files explicitly: `git add src/ tests/` — never `git add -A`
   - Commit: `git commit -m "feat: implement all planned tasks"`
   - Report scope: "Plan had N tasks. Executed N+M tasks (M unplanned)." Flag if M > 3.

**Continuous execution:** Do not pause between tasks. The only reasons to stop are: BLOCKED status after 3 attempts, or all tasks complete. No new tasks during Phase 4 — if implementation reveals needed work, add it to TODO.md unless it blocks a MUST task.

**Scope-cut protocol:** If a task is BLOCKED after 3 attempts, move to TODO.md with reason. If >50% of MUST tasks are blocked, STOP and present a scope-cut proposal: what can ship, what is blocked, whether reduced scope is viable.

## Phase 5 — Quality Gate

**Goal:** Run all applicable quality checks and fix any issues.

Invoke the `dev-toolkit:quality-gate` skill logic using the resolved commands from Phase 3:

1. **Lint**: resolved lint command (e.g., `ruff check .`, `eslint .`, `npm run lint`). Skip if tool unavailable.
2. **Type-check**: resolved type-check command (e.g., `mypy src/`, `tsc --noEmit`). Skip if tool unavailable; note in report.
3. **Tests**: resolved test command (with coverage if configured)
4. **Security**: `gitleaks detect --no-git` (if installed). Also manually check for obviously-named sensitive files: `find . -name "*.env" -o -name "credentials.*" -o -name "*.key" -o -name "*.pem" | grep -v node_modules | grep -v .gitignore`

If any check fails:
- Auto-fix what is auto-fixable (ruff --fix, ruff format)
- For type errors or test failures: fix manually and re-run
- Stage only changed files explicitly — never `git add -A`
- Commit fixes: `git commit -m "fix: quality gate fixes"`

Repeat until all checks pass OR 3 fix iterations exhausted.

**Output**: Quality gate report table (PASS/FAIL/SKIP per check).

## Phase 6 — Review Loop (max 5 iterations)

**Goal:** Multi-dimensional self-review with iterative fix cycles, modelled on the ultra-review pattern.

Before starting: capture the regression baseline (exact pass/fail/skip test set).

### Each iteration:

**Step 1: Review** — Examine the codebase through 4+ lenses (dispatch as parallel subagents if possible):
- **Functionality**: Does each acceptance criterion from the spec have a passing test? Are there edge cases not covered?
- **Code quality**: Dead code, duplicated logic, unclear naming, missing error handling at system boundaries
- **Security**: Input validation, credential exposure, injection vectors (if applicable)
- **Completeness**: Are all plan tasks implemented? README accurate? CLAUDE.md complete?
- **Domain correctness** (if applicable): Are calculations, algorithms, and business rules correct per the problem domain?
- **UX** (if applicable): For apps with a UI, are there obvious usability issues?

**Step 1b: Adversarial Verification** — For each finding from review subagents, the orchestrator MUST:
- Confirm the finding exists at the cited file:line location
- Spot-check at least 2 findings per agent by reading the source and reproducing the issue
- Downgrade or discard findings that cannot be reproduced (review agents overstate severity ~30%)
- If >30% of spot-checked findings are false positives: re-dispatch that review lens with stricter instructions

**Step 2: Triage** — Assign each finding a unique ID (format: LENS-NN, e.g., FUNC-01, SEC-03). Classify:
- P0/P1 (must fix): functional bugs, security issues, missing acceptance criteria
- P2 (should fix): code quality, missing edge-case tests
- P3 (defer): cosmetic, nice-to-have

**Step 3: Fix** — Fix all P0/P1 items. Fix P2 if time permits. Defer P3 to TODO.md. Never batch more than 5 fixes per commit. Fix commits must reference finding IDs (e.g., "fix FUNC-01, SEC-03").

**Step 4: Verify** — After each fix batch:
1. Run the full test suite and lint using resolved commands
2. Compare the passing test set against the regression baseline — any test that was passing before but fails now is a REGRESSION
3. If regression detected: fix in the SAME batch before proceeding. If unresolvable in 2 attempts, REVERT the fix and record in TODO.md.
4. Report: "N tests passing (was M), 0 regressions" or "REGRESSION: test_X now fails after fixing FUNC-NN"

**Stop conditions** (check after each iteration):
- All P0/P1 resolved AND quality gate green -> STOP, proceed to Phase 7
- 5 iterations completed -> STOP, record remaining items in TODO.md
- Same failure appears 3 times across iterations -> STOP, flag as architectural issue
- Two consecutive iterations produce fewer than 2 net findings resolved -> STOP, surface blockers

Commit after each iteration: stage only changed files — `git commit -m "fix: review iteration N — M findings fixed (IDs)"`

## Phase 7 — Deploy (conditional)

**Goal:** Deploy if a deploy target was identified in Phase 0.

| Target | Action |
|--------|--------|
| HuggingFace Space | Create Dockerfile if not present; add `hf` git remote; `git push hf main`; poll for RUNNING status |
| PyPI | Verify version in pyproject.toml; `python -m build && twine upload dist/*` (or just build and report) |
| GitHub Pages | `mkdocs gh-deploy` or `sphinx-build` + push |
| None | Skip this phase entirely |

If deploy fails: report the error and continue to Phase 8. Do not retry more than once.

## Phase 8 — Document & Close

**Goal:** Ensure the project is self-documenting and ready for future sessions.

**Pre-documentation housekeeping:**
- Remove stale imports and unused dependencies
- Verify all TODO.md items have a clear "why deferred" reason; cut items without one
- If CHANGELOG.md exists, ensure it has an entry for this build

1. **README.md** — Update with:
   - Project title and description (from spec)
   - Installation instructions
   - Usage examples (at least one)
   - How to run tests
   - How to deploy (if applicable)
   - Architecture overview (if non-trivial)

2. **CLAUDE.md** — Update with:
   - Project purpose (1 sentence)
   - Stack and key dependencies
   - Key paths (src, tests, docs, config)
   - Common commands (exact test/lint/run/deploy commands — not generic `make test`)
   - Architecture overview (if non-trivial)
   - Key patterns and anti-patterns to avoid

3. **TODO.md** — Update with any deferred P2/P3 items from Phase 6

4. **CHANGELOG.md** — Generate initial entry from git log

5. Final commit: stage only docs files — `git add README.md CLAUDE.md TODO.md CHANGELOG.md docs/` — `git commit -m "docs: complete project documentation"`

## Summary Report

After all phases complete, print a structured summary:

```
═══════════════════════════════════════════
FULL PROJECT COMPLETE
═══════════════════════════════════════════
Project:    <name>
Type:       <type>
Stack:      <stack>
Directory:  <absolute path>

Phases completed: 0-8 (or note which were skipped)

Files created:  <count>
Total commits:  <count>
Tests:          <pass>/<total> passing
Coverage:       <N%> (if measured)
Quality gate:   PASS / FAIL (with details)
Deploy:         <status or "skipped">

Review iterations: <N>
Findings fixed:    <N> (by ID)
Deferred items:    <N> (see TODO.md)
Scope:             <N planned tasks, M unplanned, K deferred>
Fix:feat ratio:    <fix commits>:<feat commits>

Key artifacts:
  docs/spec.md    — project specification
  docs/plan.md    — implementation plan
  README.md       — user documentation
  CLAUDE.md       — developer context
  TODO.md         — remaining work
═══════════════════════════════════════════
```

## Commit Hygiene (applies to ALL phases)

NEVER use `git add -A` or `git add .`. Instead:
1. Run `git status` before every commit and review the file list.
2. Stage files explicitly by directory or name (e.g., `git add src/ tests/`).
3. NEVER stage: `.env`, `*.key`, `*.pem`, `credentials.*`, `secrets.*`, `__pycache__/`, `node_modules/`, `dist/`, `build/`, `.DS_Store`.
4. `.gitignore` MUST exist before the first `git add` (created in Phase 3).

## Edge Cases

- **No deploy target**: Skip Phase 7 entirely. This is the default.
- **No docs framework**: Skip docs-build but still generate README + CLAUDE.md.
- **Spec is vague**: Make reasonable assumptions, document them in spec.md, and proceed. Do not ask 10 questions.
- **Tests won't pass after 5 fix iterations**: Record the failures in TODO.md, commit what works, and report honestly. Do not fake a green build.
- **Multi-language project**: Scaffold both stacks. Run both test suites. Quality gate covers both.
- **User provides a partial spec**: Treat it as Phase 0 input and flesh it out in Phase 1. Do not ask them to rewrite it.
- **Regression introduced by a fix**: Revert the fix (`git revert HEAD`), record it in TODO.md as "fix-blocked: <reason>", proceed to next finding. Do not chain fix-on-fix attempts beyond 2.
- **No quality tools installed**: Skip that gate check, note as SKIP in the report, and add the tool to TODO.md as a setup task. Never fail silently.
