# California housing journey

This file is the authorized user for one unattended spine. Do not ask
again for a choice listed here. If the workspace contradicts a choice,
stop and explain the contradiction. Do not invent a replacement choice.

Manual turns and forks remain available for branch tests. This file is
only the spine.

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
