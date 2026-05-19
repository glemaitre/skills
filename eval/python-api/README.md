# python-api eval

A lightweight behavioural eval for the `python-api` skill, targeted at
**small-model friendliness** (Claude Haiku 4.5).

## Why

Refactoring the 943-line `python-api/SKILL.md` for small-model legibility
has to keep behaviour intact. This eval captures observable behaviours
before/after a refactor so we can diff transcripts and catch regressions.

## What

- `prompts.md` — seven golden prompts that exercise distinct branches of
  the skill (Shape 0–3, stack orientation, named traps, multi-symbol
  consolidation). Each case lists `Must do` / `Must NOT do` bullets used
  for manual scoring.
- `run.py` — stdlib-only runner. Loads `skills/python-api/SKILL.md`
  as the system prompt, sends each case to Haiku 4.5, writes one
  transcript per case under `transcripts/<label>/`.
- `transcripts/` — generated.

## How to run

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# Capture current behaviour:
python3 eval/run.py python-api baseline

# Then run against a refactored copy (kept side-by-side as SKILL_v2.md):
python3 eval/run.py python-api refactored skills/python-api/SKILL_v2.md
```

The third positional arg is an optional path to the SKILL.md to use.
Defaults to the live `skills/python-api/SKILL.md`. Keep the refactored
version in a parallel file (e.g. `SKILL_v2.md`) until the eval passes —
that way the baseline is reproducible without git gymnastics.

Then read both `transcripts/baseline/CASE_NN.md` and
`transcripts/refactored/CASE_NN.md` side by side and tick the bullets
from `prompts.md`.

## Pass criterion

Per case: every `Must do` ticked, zero `Must NOT do` violated.
Overall: ≥ 6/7 cases pass, **and** no `Must NOT do` violation appears in
any transcript. The latter is the hard rule — a violation post-refactor
means a regression slipped in.

## Notes

- The runner gives Haiku **no tools** — it produces a planning narrative
  in text, which is what we score against. We're testing whether the
  skill is clear enough that Haiku can produce the right plan, not
  whether Haiku can execute it.
- Workspace state is handed to the model in the prompt rather than
  requiring it to `ls` the disk — this isolates skill-knowledge from
  tool-use.
- Output is non-deterministic; consider running each label twice and
  treating a case as "passing" only if both runs pass.
