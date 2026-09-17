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

1. Run `python -m skore_skills status`. Read `skills` and the
   filesystem snapshot. If `.skore` is missing, that is expected.
   Do not treat a missing file as an empty project when `src/` or
   `journal/` exist.
2. **Certain request** — name and load that skill. Do not list the
   catalog. Only if `status.skills` is true; otherwise skip in one
   line and do not invent the procedure:

   | User intent | Skill |
   |---|---|
   | env / pixi / uv / python environment | `setup-python-env` |
   | scaffold / layout / package folders | `setup-workspace` |
   | git init / first commit / ignore | `setup-git` |
   | add or install a named package | `add-python-package` |
   | EDA / explore the data | `explore-ml-data` |
   | evaluate / metrics / skore report | `evaluate-ml-pipeline` |
   | set up / bootstrap this project (generic) | `setup-ml-project` |

3. **Uncertain** (open session, “what can you do”, finished stage,
   mixed intent) — **AskUserQuestion** with the **installed**
   entry skills only. One pick, then load it.

   Offer if `skills` is true: `setup-ml-project`, `explore-ml-data`,
   `model-ml-pipeline`, `evaluate-ml-pipeline`, `audit-ml-pipeline`,
   `manage-ml-backlog`.

   Do not put internals on this board (`build-ml-pipeline`,
   `choose-python-library`, stack refs) unless step 2 is certain.

## Stop conditions

- Do not design experiments, write pipelines, or run EDA yourself.
- Do not load every skill.
- Do not invent workspace facts when status is unavailable.
- Do not treat a missing `.skore` as an empty project when `src/`
  or `journal/` exist.
- Do not invent a missing skill's steps from memory.
- Do not treat iterate as the session owner.

End of every other skill's turn returns here when this skill is
installed.
