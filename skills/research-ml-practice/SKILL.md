---
name: research-ml-practice
description: >
  Literature and web research for an ML methodology concern
  (EDA interpretation, leakage, transforms, feature engineering,
  learner family). Trigger when explore-ml-data or
  build-ml-pipeline load this skill. Not for routine profiling or
  a single API signature — use `api get` for symbols. Not a
  session owner — callers distill and write project files.

  HOW TO USE: skip intake fields the caller already supplied.
  Search distinct angles in parallel, read primary sources, write
  `scratch/research/<slug>.md` with lane-tagged candidates.
  Return the path plus one or two sentences to the caller. Never
  mutate raw data, pick the final learner, or write
  `data_analysis.md` / the design note.
---

# Research ML Practice

Worker skill. Callers own the stage turn and the user-facing
summary. Do not `git end-turn`.

## Sequence

1. **Intake.** Need a specific concern. Infer modality from
   dtypes / JOURNAL when obvious; use a stated domain and stage
   (`data_analysis` | `model`) if the caller named them. Ask only
   missing gaps (concern plus at most two follow-ups). Do not
   start search with an empty concern.
2. Classify: lookup / breadth / depth / synthesis. Details:
   `references/search.md`.
3. Run 3–5 **distinct-angle** web searches in parallel (practice,
   implementation, pitfalls; add theory/papers if the first pass
   is thin). If a domain is known, bake it into the queries.
   Fetch primary pages for any modelling claim — not snippets.
4. Write `scratch/research/<slug>.md` using the template in
   `references/search.md` (lanes on every candidate). Gitignored.
5. Return to the caller: scratch path and a one- or two-sentence
   finding. Do not dump the full note in chat. Do not write
   `data_analysis.md`, the design note, or `data/`.

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
