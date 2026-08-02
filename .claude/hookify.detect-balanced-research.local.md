---
name: detect-balanced-research
enabled: true
event: prompt
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (both\s+sides\s+of\s+(the|this|that))|(fair\s+assessment\s+of)|(balanced\s+(research|view|take|look)\s+(on|at|of))
action: warn
---

Invoking `/balanced-research`. Researches the question with mandatory disconfirming evidence — searches both for and against the hypothesis and presents a calibrated assessment.

Run: `/balanced-research {question}`

Skipping this means the research samples only one side of the evidence distribution: confirming sources get gathered, disconfirming ones don't, and the conclusion inherits the prompt's framing instead of the evidence's balance (Constitution rule 7 — epistemic balance).
