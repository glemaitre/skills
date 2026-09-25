---
name: frame-ml-problem
description: >
  Lock the problem, the deployment setting, the comparison metric,
  the baseline, and the validation scheme in the journal before any
  model code. One question per turn, from `frame show`. Does not
  write Python, estimator hyperparameters, or splitter constructors.

  TRIGGER when the user asks which metric to compare on, how new
  rows should be split, which baseline to use, or says a problem
  constraint changed. Not when they ask to run evaluation or CV.

  HOW TO USE: run `python -m skore_skills frame show`. Read the
  single `reference` it names, ask `missing[0]`, write that cell,
  and stop the turn. If that command is missing, or the problem is
  not classification or regression, read `references/fallback.md`
  and do not invent the closed menu.
---

# Frame ML Problem

Write `## Modeling decisions` in `journal/JOURNAL.md`. The table
is the contract. This skill does not declare a learner and does
not evaluate one.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Journal cells describe this dataset. Do not name the skills
framework, the CLI, or a splitter class in the table. Questions
use data-science language — not skill ids, `G-*` names, or the
wrapper CLI.

## Procedure

1. Run `python -m skore_skills status`. If `has_journal` is false,
   send the user to setup and stop. If `data_analysis` is
   `missing` and `explore-ml-data` is installed, **AskUserQuestion**:
   explore first (default) or continue from facts the user stated.
   Explore loads `explore-ml-data` and stops. Do not invent dataset
   facts. Do not ask this again once `data_analysis` is `present`
   or `skipped`.
2. Run `python -m skore_skills frame show`. When the user is
   changing a locked constraint, add `--revise`. JSON `action` is
   authoritative. Do not invent a menu. If the command is missing
   or exits without JSON, read `references/fallback.md` and follow
   it. Do not open another reference. Do not guess candidates.
3. `stop` — say the JSON `reason` and stop.
4. `ask` / `uncovered` — read `references/fallback.md` only. Write
   Prediction goal `uncovered` and the prose cells it names. Set
   Status to `draft`. Stop this turn.
5. `ask` / `missing_keys` — if `reference` is set, read that file
   before asking. Do not open any other file under `references/`.
   Ask `missing[0]` only. When `candidates` is present, those are
   the options. When it is absent, ask for the value the reference
   describes. Draw on three sources, and only what they actually
   say: the EDA report, free-form text that came with the data if
   any is present (notes, a dictionary, or a README beside the raw
   files), and facts the user stated. If none of that text is
   present, do not invent it. When one of them already states the
   fact, quote it in the question. Write that Value cell. Do not
   rename Variable cells.
   When the deployment or the validation makes other rows
   inapplicable, set those cells to `n/a` in the same edit. Once
   any decision cell is filled and Status is not `locked`, set
   Status to `draft`. Stop this turn.
6. `ask` / `confirm_lock` or `ask` / `revise` — quote JSON
   `context` inline, then offer JSON `choices` only.
   - `lock` sets Status to `locked`.
   - `modify` on a revise sets Status to `draft` and Revised on
     to today's date (`YYYY-MM-DD`), then stop for the next
     `frame show`.
   - `keep` leaves the locked table unchanged.
   - `stop` writes nothing further.
7. `proceed` — the table is locked. If `translation` is null, say
   that this lock has no splitter translation. Do not load
   `build-ml-pipeline`. Run
   `python -m skore_skills git end-turn --stage implement`. If
   JSON `action` is `invoke`, load `persist-ml-git` only if
   `status.skills.persist-ml-git` is true and stop. Otherwise
   load `triage-ml-task` only if that skill is installed.

## Stop conditions

- Do not write Python, a pipeline, a test, or a design note.
- Do not put a class name or a constructor argument in the journal.
  `TimeSeriesSplit`, `KFold`, `GroupKFold`, and `gap=` stay out of
  the table.
- Do not re-ask a key that is absent from `missing`.
- Do not add an option that is absent from `candidates`.
- Do not open a reference the JSON did not name, except
  `references/fallback.md` when the command is missing.
- A locked table changes only through `frame show --revise`, then
  the same fill and confirm gates. `keep` does not edit it.
