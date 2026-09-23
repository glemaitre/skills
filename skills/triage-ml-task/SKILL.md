---
name: triage-ml-task
description: >
  Session owner: list installed entry skills and ask which to run.
  Load a skill without asking only when the request is certain to
  be that skill. Trigger on an ambiguous request, a finished stage,
  a workspace-open session, or "what should we do next".
---

# Triage ML Task

This is the session owner. Stage skills do the work; you only
route and ask. Do not execute another skill's methodology.

## Procedure

1. Run `python -m skore_skills status`. Read `skills`, `data_analysis`,
   `loop_stage`, and the filesystem snapshot. If `.skore` is
   missing, that is expected. Do not treat a missing file as an
   empty project when `src/` or `journal/` exist.
2. **Certain request** — name and load that skill. Do not list the
   catalog. `status.skills` is a per-id dict. Load the mapped
   skill only if `status.skills.<id>` is true; else one-line skip
   and do not invent that skill's steps:

   | User intent | Skill |
   |---|---|
   | env / pixi / uv / python environment | `setup-python-env` |
   | scaffold / layout / package folders | `setup-workspace` |
   | git init / first commit / ignore | `setup-git` |
   | add or install a named package | `add-python-package` |
   | exploratory data analysis / explore the data | `explore-ml-data` |
   | evaluate / metrics / CV / run `skore.evaluate` | `evaluate-ml-pipeline` (child gate may STOP) |
   | audit / open / narrate an existing report | `audit-ml-pipeline` (child gate may STOP) |
   | build / model a pipeline | `model-ml-pipeline` |
   | smoke / pytest row-count / why is smoke failing | `smoke-test-ml-pipeline` (debug; does not start evaluate) |
   | backlog / history / record the run | `manage-ml-backlog` |
   | what next / explore ideas / next experiment | `explore-ml-directions` |
   | I want to try X / here is an idea / what if we | `iterate-from-user` |
   | papers / literature / what do people do for | `iterate-from-literature` |
   | mine the report / what does skore suggest | `iterate-from-skore` |
   | notebook / ipynb | `export-ml-notebook` |
   | notebook viewer on the site / executed report | `export-ml-notebook` (`--html`) |
   | website / mkdocs / documentation site | `export-ml-site` |
   | export (generic) | `export-ml-project` |
   | sync / migrate reports / switch skore mode / upload reports to hub or mlflow | `sync-ml-reports` |
   | set up / bootstrap this project (generic) | `setup-ml-project` |
   | “is this leakage” on the table | `explore-ml-data` (even if `data_analysis` is present). Do not load `research-ml-practice` or `iterate-from-literature`. |
   | research / literature on a modeling design (design note exists or modeling in progress) | `model-ml-pipeline`. Do not load `research-ml-practice`. |

   Certain EDA: name `python -m skore_skills status`, load
   `explore-ml-data`, stop. Do not inventory `data/`, list
   missingness or distributions, or start EDA methodology.

   Certain generic export: first name
   `python -m skore_skills status`, then load
   `export-ml-project`. Do not list notebook / `--html` / site
   as sibling options.

   **Modeling while `status.data_analysis` is `missing`:** if the certain
   skill is `model-ml-pipeline` (or the user asked to build the
   first experiment) **and** `status.skills.explore-ml-data` is
   true, do not load modeling yet. **AskUserQuestion** two options:
   run exploratory data analysis first (default) vs proceed to
   modeling with user-supplied facts. Do not invent dataset facts
   here. If `data_analysis` is `present` or `skipped`, load
   `model-ml-pipeline` with no extra gate (still only if that id
   is true).

3. **Uncertain** (open session, “what can you do”, finished stage,
   mixed intent) — **AskUserQuestion** with the **installed**
   entry skills only. One pick, then load it.

   Offer an entry only if `status.skills.<id>` is true:
   `setup-ml-project`, `explore-ml-data`, `model-ml-pipeline`,
   `explore-ml-directions`, `manage-ml-backlog`, `export-ml-project`,
   `sync-ml-reports`. If none of those ids are true, say so in one
   line; do not invent a menu.

   Do not put `evaluate-ml-pipeline` or `audit-ml-pipeline` on this
   board (certain requests still load them). Do not put
   `iterate-from-user`, `iterate-from-literature`, or
   `iterate-from-skore` on this board (certain requests still load
   them).

   If `status.data_analysis` is `missing` and
   `status.skills.explore-ml-data` is true, name `explore-ml-data`
   as the recommended next stage (`loop_stage: data_analysis`). Do
   not auto-load it. When `data_analysis` is `present` or `skipped`,
   `loop_stage` is `backlog`, and
   `status.skills.explore-ml-directions` is true, name
   `explore-ml-directions` as the recommended next stage. Do not
   auto-load it.

   Do not put internals on this board (`build-ml-pipeline`,
   `smoke-test-ml-pipeline` except as a **certain** debug load,
   `choose-python-library`, `research-ml-practice`,
   `plot-ml-figure`, stack refs).

## Stop conditions

- Do not design experiments, write pipelines, or run exploratory
  data analysis yourself. Certain EDA is load `explore-ml-data`
  only — no data inventory and no EDA checklist.
- Do not load every skill.
- Do not invent workspace facts when status is unavailable.
- Do not treat a missing `.skore` as an empty project when `src/`
  or `journal/` exist.
- Do not invent a missing skill's steps from memory.
- Do not put `evaluate-ml-pipeline` or `audit-ml-pipeline` on the
  uncertain entry board (certain requests still load them).
- Do not put `iterate-from-user`, `iterate-from-literature`, or
  `iterate-from-skore` on the uncertain entry board (certain
  requests still load them).
- A missing explore or sourcing skill is a one-line skip. Do not
  invent that skill's menu.
- Certain generic export: name `python -m skore_skills status`,
  load `export-ml-project` only — no sibling-skill menu.

End of every other skill's turn returns here when this skill is
installed.
