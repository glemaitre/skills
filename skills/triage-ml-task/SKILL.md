---
name: triage-ml-task
description: >
  Route an ambiguous ML request to an install pack or one focused
  skill. Trigger when the user asks what the companion can do or
  gives an unclear ML task. Do not trigger merely because an existing
  ML workspace is opened; `iterate-ml-experiment` owns that session.
---

# Triage ML Task

Use this as a small router, not a methodology owner.

1. Run `python -m skore_skills status`.
2. Classify the request:
   - workspace/environment → `setup`
   - data understanding → `eda`
   - pipeline construction/evaluation/testing → `model`
   - experiment design/iteration/audit → `loop`
3. If two routes remain plausible, ask one question.
4. Name the pack or skill to load; do not execute its methodology.

## Stop conditions

- Do not steal “continue this experiment” or workspace-open triggers
  from `iterate-ml-experiment`.
- Do not load every skill.
- Do not invent workspace facts when status is unavailable.
- Do not install packs without the user's request.

This contract is intentionally minimal; deepen routing together in a
later review.
