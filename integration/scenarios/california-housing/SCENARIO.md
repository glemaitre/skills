# California housing journey

This file is the authorized user for one unattended spine. Do not ask
again for a choice listed here. If the workspace contradicts a choice,
stop and explain the contradiction. Do not invent a replacement choice.

Manual turns and forks remain available for branch tests. This file is
only the spine.

## Before the journey

The runner has already loaded the `ml-experimentation` skills from the
checkout at `{{SKILLS_REPO}}` and supplied that checkout's
`skore_skills` on `PYTHONPATH`.

- Start with `skill("setup-ml-project")`. Use `skill("<id>")` for every
  later skill handoff.
- Never read a workflow `SKILL.md` directly. Do not search or install
  public skills, create `.agents/skills`, run `npx skills`, invoke
  `find-skills`, or reload resources.
- If `skill("setup-ml-project")` is unavailable, stop immediately and
  report: `pi install npm:@probabl/pi-skore` is required. Do not continue
  by reading skill files directly.
- After pixi is initialized, add this checkout as the editable
  `skore-skills` dependency:

  ```bash
  pixi add --pypi --editable "skore-skills @ {{SKILLS_REPO_URI}}"
  ```

  If `env add-skore` later replaces it with a published build, run this
  editable add again before continuing.

## Setup

- Keep all four pieces selected: Python environment, workspace layout,
  editable install, and Git.
- Environment manager: pixi.
- Manage the Python environment: yes.
- Python import name: `housing`.
- Automatic commits: off.

## Framing

- Continue from `DATA.md`. Do not explore the data first.
- Prediction goal: `point_predictions`.
- Deployment: `iid`.
- Horizon, gap, generalize-to, known at predict, and time role: `n/a`.
- Metric role: `point_error`.
- Metric: `RMSE`.
- Baseline: `dummy`.
- Baseline note: mean house value.
- Folds: `2`.
- Lock these modeling decisions.

## Baseline

- Build the locked baseline.
- Approve the proposal and the design note.
- Evaluate and keep the report local.
- Review the result.

## Backlog and next experiment

- Promote the first open idea into the backlog.
- Set every other open idea aside.
- Take backlog item `B1` as the next experiment.
- Approve its proposal and design note.
- Build and smoke-test that second experiment.
- Stop before evaluating the second experiment.
