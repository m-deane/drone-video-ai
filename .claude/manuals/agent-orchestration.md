# Manual: Parallel Agent Sprints & Recovery

> **Why this manual exists.** Multi-agent work is where the most work is lost — to stream
> idle timeouts, to context flooding, and (in ephemeral/web environments) to the container
> being reclaimed mid-run. Fable-5 sessions survive this by disciplined checkpointing and
> wave sizing. This manual makes that discipline explicit and tool-checkable.
> **Canonical source: root `CLAUDE.md` → "Long-Running Agent Work" and "Stream Idle Timeout — Prevention and Recovery".**

## Purpose & scope

Covers dispatching a parallel agent sprint, per-agent conditioning, checkpoint persistence,
and recovery from timeouts/interruptions. Out of scope: what each agent *does* (that is the
task's own domain manual).

## Preconditions

```bash
ls .claude/skills/sprint/SKILL.md .claude/skills/resume/SKILL.md \
   .claude/skills/retry/SKILL.md .claude/skills/checkpoint-gate/SKILL.md \
   .claude/skills/synthesis-validator/SKILL.md      # orchestration skills exist
ls .claude/checkpoints/                              # where checkpoints live (git-tracked in this repo)
git log --oneline -5                                 # commits (see counting rule below)
grep -c 'TURN END' .claude/activity.md 2>/dev/null   # tool-call tally: one --- TURN END --- per turn
```

**Mandatory pre-dispatch checkpoint (trigger).** If this session includes **3+ prior commits
OR 10+ tool calls** (either alone is sufficient), write
`.claude/checkpoints/{sprint-label}-pre-dispatch/context.md` covering: current branch, recent
commits, in-progress work, and decisions made this session — *before* dispatching any agent
team. Name the pre-dispatch dir **identically to the sprint dir it precedes, plus the
`-pre-dispatch` suffix** (e.g. `20260609-promptlab-pre-dispatch` pairs with sprint dir
`20260609-promptlab`).

**Counting the trigger deterministically (no session memory required).**
- *Commits this session:* `git log --oneline -5` has no session boundary. Count only commits
  after the ref you branched from — e.g. `git log --oneline $(git merge-base HEAD main)..HEAD`
  (substitute your base branch) — or, if no anchor is available, treat the count as unknown.
- *Tool calls:* count `--- TURN END ---` markers in `.claude/activity.md` with the `grep -c`
  above when that log is present; otherwise the tally is unknown.
- *Default-fire rule:* if you cannot positively determine **both** counts for THIS session,
  treat the trigger as **FIRED** and write the pre-dispatch checkpoint anyway — it is cheap
  and errs toward safe.

## Decision procedure

| IF | THEN |
|----|------|
| task needs ≤ 4–5 agents | dispatch one wave |
| task needs 6+ agents | sequential waves, `/resume` between waves. Partition rule: fill each wave to the max of 5 before opening the next (6 → 5+1, 9 → 5+4, 11 → 5+5+1) unless an ordering dependency forces a producer agent into an earlier wave (combined output of >5 agents floods the orchestrating context) |
| session has 3+ commits OR 10+ tool calls | write the pre-dispatch checkpoint first |
| an agent returns `API Error: Stream idle timeout - partial response received` | run `/retry` immediately |
| `/retry` unavailable | (1) check if the checkpoint file was written — partial work is recoverable; (2) re-dispatch with narrower scope; (3) switch to `model: sonnet`; (4) split into sequential single-file agents if sonnet also times out |
| environment is ephemeral/web (container reclaimed on inactivity) | prefer **synchronous, in-turn** authoring or short waves that finish within one turn — background agents may not survive container dormancy |
| all agents done, before synthesis | run `/checkpoint-gate`; only synthesise on a COMPLETE verdict |
| synthesis conclusion not traceable to an agent's checkpoint | `/synthesis-validator` flags it UNSUPPORTED — drop or re-derive it |

**Classifying the environment (choose the branch *before* dispatch).** Treat the environment
as **ephemeral** (choose synchronous, in-turn authoring) UNLESS you can positively confirm the
container persists across idle periods. Concretely: if the session runs on Claude Code web / a
reclaimable container, or you cannot confirm persistence, default to **ephemeral** and author
each file synchronously with the file tools. Only choose background waves when persistence is
confirmed. Worked Example 2 below shows the *post-hoc* symptoms (0 files produced + stale
transcript mtimes); this rule makes ephemeral the safe default when persistence is unknown.

## Step-by-step procedure

1. **Pre-dispatch checkpoint** (if the trigger fires — see the default-fire rule above):
   ```bash
   # {sprint-label} = the SAME slug as the sprint dir this precedes (e.g. 20260609-promptlab)
   mkdir -p .claude/checkpoints/{sprint-label}-pre-dispatch
   # write context.md: branch, recent commits, in-progress work, decisions
   ```
2. **Compose each agent's Conditions block.** Every condition that must govern the agent's
   work must be written *into that agent's prompt* — agents do not inherit session context.
   A complete block carries the 6 layers plus switch variables: **L1 Jurisdiction** (stack /
   project constraints), **L2 Posture** (implementation / review / diagnosis / synthesis),
   **L3 Objective** (a stated, externally verifiable success criterion — not just a task
   description), **L4 Constraints** (what the agent must not do), **L5 Facts** (each named
   file *and why it is relevant* — agents prune files with no stated purpose), **L6 Output**
   (the checkpoint path + return contract), plus the project switch variables. Validate the
   block with `/condition-audit` (missing **L1, L3, or L4 = do not dispatch**) or pre-fill it
   with `/evidence-injection-template` for the scenario type.
3. **Embed the stream-idle-timeout prevention line verbatim** in every agent prompt:
   > "Write ALL code and detail to your checkpoint file. Inline return: ≤150 words. Write
   > checkpoint FIRST — even a skeleton. Update after each step. Stop immediately after your
   > inline summary."
4. **Dispatch the wave** (max 4–5 agents). For 6+, do sequential waves with `/resume`.
5. **Gate:** run `/checkpoint-gate` after all agents complete.
6. **Synthesise**, then run `/synthesis-validator` against the agent checkpoints.

## Verification gate

- **Checkpoint gate (pass criterion):** `/checkpoint-gate` returns **COMPLETE** — every
  expected agent wrote a **non-empty** checkpoint file. An INCOMPLETE verdict names the
  missing agents; do not synthesise until they are re-dispatched and complete.
  Manual pre-check (weaker than the skill — a non-empty test only, **NOT** a full
  substitute). Checkpoint files are **flat, one per agent**, named `{agent_name}.md`
  directly inside the sprint dir — there are no per-agent subdirs and no file named
  `checkpoint.md`. Substitute `<sprint-dir>` with a real dated dir from
  `ls .claude/checkpoints/`:
  ```bash
  shopt -s nullglob
  for f in .claude/checkpoints/<sprint-dir>/*.md; do
    [ -s "$f" ] && echo "OK  $f" || echo "EMPTY $f"; done
  ```
  Pass (this pre-check) = zero `EMPTY` lines. `nullglob` makes a truly empty/absent sprint
  dir yield no lines rather than a spurious literal-glob line. This check only catches
  empty/missing files; the **authoritative** pass criterion is `/checkpoint-gate`, which is
  stricter — it flags a file as SKELETON (incomplete) unless it is non-empty **AND** has 10+
  lines **AND** at least one `^#` heading.
- **Synthesis gate (pass criterion):** `/synthesis-validator` reports zero UNSUPPORTED
  conclusions and zero DROPPED FLAGS (agent caveats missing from the synthesis).

## Failure modes & recovery

| Failure | Symptom | Recovery |
|---------|---------|----------|
| Stream idle timeout | `API Error: Stream idle timeout - partial response received` | `/retry`; if unavailable, follow the 4-step fallback in the decision table |
| Context flooding | orchestrator degrades after a large wave | cap waves at 4–5; keep inline returns ≤150 words; push detail to checkpoints |
| Container reclaimed mid-run | background agents launched, then hours later produced **nothing**; their transcript files are stale | this environment reclaims idle containers — do the work synchronously in-turn so each written file persists immediately; re-dispatch survivors via `/resume` |
| Lost work on timeout | agent died mid-task | the checkpoint file holds partial work — resume from it, don't restart |
| Unsupported synthesis | conclusion cites nothing | `/synthesis-validator` catches it; re-derive from checkpoints or drop |

## Worked examples

**Example 1 — pre-dispatch checkpoint (real pattern in this repo).**
`.claude/checkpoints/20260609-promptlab-pre-dispatch/` exists as the pre-dispatch checkpoint
for the promptlab sprint. Input: "launch an agent team to build promptlab" after several
commits. Expected output: a `context.md` under a `-pre-dispatch` dir capturing branch +
recent commits + decisions, written *before* the agents were dispatched. Verify the pattern:
```bash
ls -d .claude/checkpoints/*-pre-dispatch/    # e.g. 20260609-promptlab-pre-dispatch/
```

**Example 2 — recovery when background agents don't survive.**
Input: 4 agents dispatched in a web/ephemeral session; on resume hours later,
`ls .claude/manuals/*.md` shows 0 files and the agents' transcript mtimes are stale by hours.
Expected output: conclude the container was reclaimed (agents dead), switch to synchronous
in-turn authoring (write each file with the file tools so it persists), and only then
consider re-dispatching. This is the recovery this very manual set used.

## Escalation criteria — stop and ask the user when

- A wave would exceed 5 agents *and* the sub-tasks are not cleanly separable into sequential
  waves — confirm the decomposition first. Sub-tasks are **separable** IF (a) no two share
  file ownership **AND** (b) there is no ordering dependency (no task consumes another task's
  output). If either fails — shared files, or an ordering dependency across the split — treat
  them as **NOT cleanly separable** and escalate to the user before dispatching.
- `/checkpoint-gate` returns INCOMPLETE after two re-dispatch attempts — surface which agents
  keep failing rather than synthesising partial results.
- Recovery requires switching model tier or narrowing scope in a way that changes the
  deliverable — confirm the reduced scope with the user.
- The orchestration itself is Tier C (e.g. agents will make irreversible external changes) —
  confirm every wave.
