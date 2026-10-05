# California housing journey

This file is the authorized user for one unattended spine. Do not ask
again for a choice listed here. If the workspace contradicts a choice,
stop and explain the contradiction. Do not invent a replacement choice.

Manual turns and forks remain available for branch tests. This file is
only the spine.

## Before the journey

Do this before the spine. Do not search a public skill registry, and do
not run `npx skills` or `find-skills`.

The skills and `skore-skills` for this run are the checkout at
`{{SKILLS_REPO}}`.

- Read the `ml-experimentation` workflow in
  `{{SKILLS_REPO}}/.catalog.json`. For each included skill id, install
  that skill into `.agents/skills/<id>` in this workspace. Symlink each
  file and directory from `{{SKILLS_REPO}}/skills/<id>` into that
  workspace directory. Write a real `.skore-skill.json` there, containing
  `{"id": "<id>"}`. Do not write that sidecar through a symlink into the
  checkout.
- `python -m skore_skills` must import this checkout. Before a project
  environment exists, editable-install the checkout into the interpreter
  that will run those commands (`pip install -e` or `uv pip install -e`
  of `{{SKILLS_REPO}}`). Do not install `skore-skills` from PyPI.
- After pixi exists, add the same checkout:

  ```bash
  pixi add --pypi --editable "skore-skills @ {{SKILLS_REPO_URI}}"
  ```

  `setup-python-env` later runs `env add-skore`, which installs the
  `skore` library and can replace `skore-skills` with the published
  build. If that happens, run the editable add again before continuing.

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
