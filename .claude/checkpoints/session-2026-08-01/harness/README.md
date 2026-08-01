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

| `MUTANT` | Reverts | Expected 2026-08-01 |
|---|---|---|
| `letterbox` | `ActiveRect.crop` → identity (pre-`0644fb7`) | 1 failed, 9 passed — `letterbox not excluded: 0.7556 vs 1.0000`, delta `0.24444315933124017` |
| `rank` | degenerate branches → `1.0` (pre-`bc3a499`) | 1 failed, 9 passed — `assert 1.0 is None` at `test_corpus_footage.py:135` |
| unset / `none` | nothing | 10 passed |

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

| `FOOTAGE` | Expected 2026-08-01 |
|---|---|
| `absent` | 10 skipped, exit 0, 0.29 s — correct fresh-clone behaviour |
| `partial` (1 of 6 clips) | **5 passed, 5 skipped, exit 0** — green, with both vertical-family tests silently skipped (finding P1-T2) |

The `partial` case is the one to re-run **after relocating this repo** — see
`../MOVE-READINESS.md`. A half-copied `data/raw/` produces a green suite.

## Note

If P1-T1 is fixed as recommended (decoupling the test from `max_duration`), the `rank`
mutant's expected failure line number will move. The expected *behaviour* — one failure,
naming a fabricated rank — should not.
