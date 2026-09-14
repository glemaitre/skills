---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Dispatch workspace,
  environment, and git actions in order; do not duplicate them.
---

# Set Up ML Project

This meta skill owns ordering only:

1. `organize-ml-workspace` — detect/glue or scaffold after package,
   tabular, environment-manager, and skore-mode gates.
2. `python-env-manager` — install the editable package and required
   dependencies through the detected manager.
3. `setup-git` — initialize version control only with the user's
   first-commit decision.

Run `python -m skore_skills status` before dispatch and after setup
to surface missing pieces.

## Stop conditions

- Never silently pick package name, tabular library, env manager, or
  skore mode.
- Never run `pip install` in a pixi project.
- Never commit without asking.
- Do not write pipeline or experiment bodies; setup stops at a safe
  scaffold.

This is a deliberately small dispatcher pending joint review.
