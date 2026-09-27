---
name: review-ml-choices
description: >
  Show the project choices already stored in status and let the
  user change one by re-entering the skill that owns it. Trigger
  when the user asks what we decided, what the current settings
  are, or to change a stored project choice.

  SKIP an explicit sync, export, or “a constraint changed”
  request — those load sync-ml-reports, export-ml-project, or
  frame-ml-problem directly.

  HOW TO USE: run status, show the board, then load one owning
  skill. Do not policy set from here.
---

# Review ML Choices

Show stored choices. A change loads the skill that already owns
that decision. Do not write `.skore` or the journal from here.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
The board uses data-science labels: where reports go, executed
notebooks, documentation site, git commits, who manages the
environment, data analysis, and each filled framing cell
(prediction goal, deployment, metric, validation, and the
others below). Do not put skill
ids, `G-*` names, or the wrapper CLI in the question.

## Sequence

1. Run `python -m skore_skills status`. Read `policy`,
   `data_analysis`, `modeling_decisions`, `loop_stage`,
   `env_manager`, `mismatch`, and `skills`. When
   `modeling_decisions` is `draft` or `locked` and
   `status.skills.frame-ml-problem` is true, run
   `python -m skore_skills frame show`. Read `decisions` when
   that key is present, otherwise `context`. Do not pass
   `--revise` here.
2. **AskUserQuestion**, one pick. Say first, in 2–4 lines, what a
   change authorizes — re-entering that setup, not a silent flag
   flip — and echo the current values inline. A file link is an
   addition, never the context.

   Options are **Keep these** plus one option per changeable row
   whose owning skill is installed. Read-only rows are in the
   context, not options.

   Read-only:

   - Python package (`policy.package`, or not chosen). An
     existing `src/` tree is not renamed.
   - Environment manager (`policy.env_manager`; mention
     `mismatch` when true). Switching would leave two lockfiles.
   - Tabular library (`policy.tabular`, or not chosen). Analysis
     and pipeline code already import one library.
   - Loop position (`loop_stage`, and `policy.loop.stem` when
     set). It follows the files. Do not `policy set loop.stage`
     or `loop.stem`.

   Changeable when `status.skills.<id>` is true; otherwise show
   the value and do not offer it:

   - Where reports go — `policy.skore_mode` (`local`, `hub`, or
     `mlflow`) → `sync-ml-reports`. If it is unset, show “not
     chosen yet” and do not offer it. The first choice happens
     when a report is stored.
   - Executed notebooks and documentation site —
     `policy.notebooks` and `policy.site` → `export-ml-project`.
     One row, both values.
   - Git commits at the end of a stage —
     `policy.git.autocommit` → `setup-git`.
   - Who manages the environment — `policy.env.managed` →
     `setup-python-env`.
   - Data analysis — `data_analysis` `missing` or `skipped` →
     `explore-ml-data` (run or skip). `present` → the same skill,
     to run the written analysis again. Skip is not available
     while `data_analysis/data_analysis.md` exists.
   - One option per filled framing cell, from `frame show`. Skip
     empty cells and cells whose value is `n/a`. If
     `modeling_decisions` is `missing`, `frame show` returns
     `stop`, or `frame-ml-problem` is not installed, show “not
     framed yet” and do not offer these rows. Labels and keys:

     - Prediction goal — `prediction_goal`
     - Deployment — `deployment`
     - Horizon — `horizon` (only when deployment is `time`)
     - Gap — `gap` (only when deployment is `time`)
     - Time role — `time_role` (only when deployment is `time`)
     - Generalize to — `generalize_to` (only when deployment is
       `groups`)
     - Known at predict time — `known_at_predict`
     - Metric role — `metric_role`
     - Metric — `metric`
     - Baseline — `baseline`
     - Baseline note — `baseline_note`
     - Validation — `validation`
     - Folds — `folds` (only when validation is `cv`)

     Each of these loads `frame-ml-problem` naming that cell.

3. **Keep these** → stop. Do not load a skill.
4. One change → load that skill and stop. Do not `policy set`.
   Do not run the child's commands from memory.

   - Recorded report destination → `sync-ml-reports`.
   - Notebooks and site → `export-ml-project`.
   - Git commits → `setup-git`. The user asked to change that
     choice.
   - Who manages the environment → `setup-python-env`. Do not
     run `env add-skore` here. If `policy.skore_mode` is `hub`
     or `mlflow`, do not use `--mode local`.
   - Data analysis `missing` or `skipped` → `explore-ml-data`.
   - Data analysis `present` → `explore-ml-data`. Do not write a
     JOURNAL `skipped` row.
   - One framing cell → `frame-ml-problem`, naming that cell.
     Do not blank the cell here. Do not `frame show --revise`
     here.

5. A request to change a read-only row (rename the package,
   switch the environment manager, switch the tabular library,
   or set the loop position): say why it stays and stop. Do not
   load `setup-workspace` to rename. Do not `policy set`.

## Stop conditions

- Do not `policy set` any key.
- Do not edit JOURNAL, including a Data understanding `skipped`
  row.
- Do not load `sync-ml-reports` when `policy.skore_mode` is
  unset.
- Do not `env add-skore`, `git commit`, or scaffold `src/`.
- If the owning skill is not installed, show the value and skip
  the change in one line. Do not invent that skill's steps.
