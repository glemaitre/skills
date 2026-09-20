---
name: model-ml-pipeline
description: >
  Coordinate the model workflow after an experiment design is
  approved: build the declaration, evaluate it, then smoke-test it.
  Trigger for an end-to-end modeling implementation, not a single
  action already owned by a child skill.
---

# Model ML Pipeline

This meta skill owns ordering, not implementation details:

1. `build-ml-pipeline` — declare the skrub DataOps learner.
2. `evaluate-ml-pipeline` — choose the leakage-safe splitter and
   write evaluation in the experiment script.
3. `smoke-test-ml-pipeline` — verify prediction on held-out/future
   input and exact row-count preservation.

Before new library symbols are written, use
`python -m skore_skills api get <dotted>`.

## Stop conditions

- If `journal/NN_<short>.md` is missing, create its packaged shell
  with `python -m skore_skills scaffold --journal --stem
  <NN_short>`. Name that command. One sentence: Question,
  Motivation, Method, and Risks are filled only after that
  command creates the shell; then stop for user approval. Do
  not outline or populate those four fields this turn. If the
  CLI cannot run this turn, name the command and stop without
  recreating the template from memory.
- Require that design note to be approved before code.
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while smoke tests fail.
- Do not duplicate child-skill methodology in this dispatcher.
- If `status.data_analysis` is `missing`, continue with facts the user
  stated; do not invent an exploratory data analysis report.
- Literature-backed feature-engineering or learner-family
  questions: load `build-ml-pipeline` (it loads
  `research-ml-practice` if installed). Do not distill research
  here; do not invent papers from memory.

After build and smoke succeed, if `policy.notebooks` is true,
`export-ml-notebook` is installed, run
`python -m skore_skills notebook convert experiments/<stem>.py`,
with `--html` when `policy.site` is also true. Convert re-executes
the script; say so when it is slow. Missing jupytext / nbclient /
nbconvert → one-line skip naming `add-python-package`; do not fail
the turn.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build`. Skip in one line otherwise.
Name a build error; do not fail the model turn.

Then run
`python -m skore_skills git end-turn --stage implement`. If JSON
`action` is `invoke`, load `persist-ml-git` and follow it. Then
load `triage-ml-task`. Do not run `git commit` in this skill.

This first version is intentionally narrow pending joint review.
