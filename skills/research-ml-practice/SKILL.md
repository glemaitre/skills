---
name: research-ml-practice
description: >
  Literature and web research for an ML methodology concern
  (EDA interpretation, leakage, transforms, feature engineering,
  learner family), or an open survey that proposes concerns.
  Trigger when explore-ml-data or build-ml-pipeline load this
  skill. Not for routine profiling or a single API signature —
  use `api get` for symbols. Not a session owner — callers
  distill and write project files.

  HOW TO USE: skip intake fields the caller already supplied.
  Mode survey or a named concern; search distinct angles in
  parallel, read primary sources, write `scratch/research/`
  (`survey-<slug>.md` or a lane-tagged depth note). Return the
  path plus one or two sentences to the caller. Never mutate
  raw data, pick the final learner, or write
  `data_analysis.md` / the design note.
---

# Research ML Practice

Worker skill. Callers own the stage turn and the user-facing
summary. Do not `git end-turn`.

## Sequence

1. **Intake.** Infer modality from dtypes / JOURNAL when
   obvious; use a stated domain and stage (`data_analysis` |
   `model`) if the caller named them. Then pick a mode
   (`references/search.md`):
   - Caller passed a **named concern** → **depth**. Do not
     re-ask. Do not run a survey first.
   - Caller passed **mode survey** (open research) → **survey**.
     Do not ask for a concern first.
   - Neither → **AskUserQuestion** one pick, none recommended:
     survey first vs I will name a concern. Do **not** offer
     EDA Open questions as a closed concern menu. Do **not**
     start a **depth** search with an empty concern. If they
     will name it, wait for the concern then depth.
2. Run searches for that mode (`references/search.md`). Fetch
   primary pages for any modelling claim — not snippets.
3. Write `scratch/research/` using the matching template
   (survey: `survey-<slug>.md`; depth: `<slug>.md` with lanes).
   Gitignored.
4. Return to the caller: scratch path and a one- or two-sentence
   finding. Do not dump the full note in chat. Do not write
   `data_analysis.md`, the design note, or `data/`. The caller
   asks which survey concerns to deepen.

## Stop conditions

- Do not drop, impute, or remove outliers. Do not change the split.
- Do not pick the final learner or architecture.
- Do not treat a single blog as ground truth; say when sources
  disagree. Thresholds need two independent sources.
- Do not `pixi add` / `uv add` / `env add`. If code needs a
  library, name `add-python-package` and return.
- Do not run `api get` as a substitute for literature (symbols
  still go through `api get` in the caller).
- Missing skill from a caller → that caller one-line skips.
- Do not turn Open questions / EDA findings into search queries
  or a concern board. Survey proposes concerns from sources.
