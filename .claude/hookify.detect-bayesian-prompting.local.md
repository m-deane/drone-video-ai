---
name: detect-bayesian-prompting
enabled: true
event: prompt
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (bayes(ian)?\s+(prompt(ing)?|principles?|framework|conditions?|pipeline)|shift(ing)?\s+the\s+posterior|prior[- ]domin|condition\s+the\s+(model|session|agent)|switch\s+variables?|calibration\s+retrospective)
action: warn
---

You are using Bayesian-framework vocabulary — conditioning, priors, posteriors, switch variables. Route this deterministically instead of leaving it to semantic fallback.

**Run:** `/goal [implementation|debug|architecture|review]` when a session goal is stated or implied — it chains `/session-conditioner` → `/evidence-injection-template` → `/condition-audit`, the full Bayesian pipeline.

**Run:** `/session-conditioner` alone when the request is only to condition the session (inject L1 stack, L2 posture, switch variables) without a goal pipeline. For post-sprint phrasing ("calibration retrospective", "did the conditions hold"), run `/calibration-retrospective` instead; for "audit the switch variables" against an existing block, run `/condition-audit`.

Why this matters: these phrasings previously matched no Layer-1 rule — routing depended entirely on Layer-3 semantic matching against one skill-description sentence. The skill bodies handle any elicitation (mode, goal, autonomy-level); this rule only guarantees they are reached.
