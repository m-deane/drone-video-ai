# Mutation / skip-path harness for the integration suite

Two pytest plugins used on 2026-08-01 to produce the `review-tests.md` findings. They exist
so those findings stay **re-checkable** rather than having to be taken on trust.

Neither modifies `src/`. Both patch at runtime in `pytest_configure`, so a run is a pure
read of the working tree.

## `mutants.py` — does the suite actually catch a reverted fix?

```bash
cd <repo root>
H=.claude/checkpoints/session-2026-08-01/harness
PYTHONPATH=$H MUTANT=letterbox ./.venv/bin/python -m pytest -q -m integration -p mutants
PYTHONPATH=$H MUTANT=rank      ./.venv/bin/python -m pytest -q -m integration -p mutants
```

| `MUTANT` | Reverts | Expected (re-measured 2026-08-01 post-move) |
|---|---|---|
| `letterbox` | `ActiveRect.crop` → identity (pre-`0644fb7`) | 1 failed, 10 passed — `letterbox not excluded: 0.7556 vs 1.0000`, delta `0.24444315933124017` |
| `rank` | degenerate branches → `1.0` (pre-`bc3a499`) | 1 failed, 10 passed — `assert 1.0 is None` at `test_corpus_footage.py:156` |
| unset / `none` | nothing | 11 passed |

Counts were `1 failed, 9 passed` / `10 passed` before the P1-T1 fix added an eleventh
integration test; the delta and the failure messages are unchanged, and the `rank` mutant's
line moved from `:135` to `:156` exactly as the note at the bottom of this file predicted.

Each mutant failing **exactly one** test is itself a finding: every fix has a single guard,
with no redundancy. See `review-tests.md` P2-T5.

## `footage.py` — what happens when the footage mirror is incomplete?

```bash
H=.claude/checkpoints/session-2026-08-01/harness
PYTHONPATH=$H FOOTAGE=absent ./.venv/bin/python -m pytest -q -m integration -p footage -rs

mkdir -p /tmp/partial && ln -sf "$PWD/data/raw/corpus/split_003_s66.mp4" /tmp/partial/
PYTHONPATH=$H FOOTAGE=partial PARTIAL_DIR=/tmp/partial \
  ./.venv/bin/python -m pytest -q -m integration -p footage -rs
```

| `FOOTAGE` | Expected (re-measured 2026-08-01 post-move) |
|---|---|
| `absent` | 11 skipped, exit 0 — correct fresh-clone behaviour, unchanged |
| `partial` (1 of 6 clips) | **11 skipped, exit 0**, each naming the missing clips — P1-T2 FIXED |

Before the P1-T2 fix, `partial` reported **5 passed, 5 skipped, exit 0** — green, with both
vertical-family tests silently skipped, i.e. the letterbox false-positive guard gone and
nothing saying so. `corpus_dir` now requires every member of `SPLIT_FAMILY + VERTICAL_FAMILY`
and skips the whole suite with an explicit "incomplete corpus mirror: missing …" message.

The `partial` case is the one to re-run **after relocating this repo** — see
`../MOVE-READINESS.md`. It was re-run immediately after the 2026-08-01 SSD move and both
paths behave as tabulated.

## Note

If P1-T1 is fixed as recommended (decoupling the test from `max_duration`), the `rank`
mutant's expected failure line number will move. The expected *behaviour* — one failure,
naming a fabricated rank — should not.

**Happened 2026-08-01.** P1-T1 was fixed, the line moved `:135` → `:156`, and the behaviour
did not change. The tables above are updated accordingly.
