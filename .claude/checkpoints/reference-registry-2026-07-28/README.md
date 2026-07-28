# Sprint: reference-registry — 2026-07-28

Goal: complete the archived-research census the 2026-07-27 session left unfinished, and write
`data/reference/REGISTRY.md`. **Status: COMPLETE.** Deliverable is at `data/reference/REGISTRY.md`.

## Live checkpoints — the evidence behind REGISTRY.md

| File | Slice | Files read | Lines |
|---|---|---:|---:|
| `census-viral-research-core.md` | `.claude_research/` viral research core | 5 | 2,582 |
| `census-craft-research.md` | colour / transitions / craft research | 5 | 4,647 |
| `census-url-attribution-sweep.md` | exhaustive URL + handle sweep, whole corpus | all | — |
| `census2-bench-a.md` | the two `viral_drone_benchmark*.md` documents | 2 | 1,035 |
| `census2-bench-b.md` | `v21_viral_research.md`, `research_viral_trends.md` | 2 | 666 |
| `census2-eval-a.md` | `v21_viral_benchmark_review.md`, `v21_technical_analysis.md` | 2 | 474 |
| `census2-eval-b.md` | qualitative/visual scoring documents | 3 | 788 |
| `census2-eval-c.md` | `source_footage_analysis.md`, `detection_tuning_params.md` | 2 | 924 |

## Superseded — do not treat as incomplete work

`census-benchmark-plans.md` (33 lines) and `census-evaluation-docs.md` (28 lines) are **skeleton
stubs only**. Their agents stalled mid-stream before writing content. Those two slices were
re-dispatched, split narrower, as the five `census2-*` files above, which cover the same source
files completely. The stubs are retained rather than deleted (`.git` is corrupt; deletion has no
undo) but contain no findings.

## What stalled, and why it mattered

Wave 1: 4 of 5 agents stalled. Cause, from the run journal: oversized structured-return schemas
(`maxItems: 60` with long free-text fields) produced repeated `StructuredOutput` validation
failures, then stream stalls — *after* the agents had finished their analysis. Two of the four had
already written complete checkpoints to disk and were recovered in full; two had not.

Wave 2: same corpus, narrower slices, and a small return schema (counts + ~12 top items with
`maxLength` caps, everything else in the checkpoint file). 5 of 5 returned. The retry log still
shows three stalls, all recovered automatically.

The operative lesson is not "agents stall" — it is that the checkpoint-first instruction is what
made the stalls survivable, and that the return schema is the thing to keep small.
