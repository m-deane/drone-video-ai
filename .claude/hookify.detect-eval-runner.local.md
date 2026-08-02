---
name: detect-eval-runner
enabled: true
event: prompt
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (eval[- ]runner)|(dataset\s+scorecard)|(evaluate\s+.{0,40}across\s+the\s+(whole\s+)?dataset)|(score\s+.{0,40}on\s+(all|every)\s+examples?)
action: warn
---

Invoking `/eval-runner`. Sweeps the full eval dataset for one prompt-under-test — stability, rubric, and source-grounded faithfulness per example — and aggregates into a dataset scorecard.

Run: `/eval-runner {prompt-or-skill} {dataset}`

Skipping this means judging the prompt on a single hand-picked example: one draw from the output distribution presented as the distribution. The scorecard exists so per-example variance is measured, not assumed.
