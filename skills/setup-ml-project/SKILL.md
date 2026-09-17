---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Dispatch
  setup-python-env, setup-workspace, add-python-package (editable),
  then setup-git; skip any that is not installed.
---

# Set Up ML Project

Ordering only. Run `python -m skore_skills status` and read
`skills`:

- `true` — load that skill and follow it.
- `false` or unknown and not in this session — skip in one line,
  continue.

Never run a skipped skill's steps from memory.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (read skills + has_src)
- [ ] load setup-python-env | skip
- [ ] load setup-workspace | skip
- [ ] load add-python-package editable | skip until has_src
- [ ] load setup-git | skip
- [ ] status again; load triage-ml-task if installed
```

## Sequence

1. `setup-python-env`
2. `setup-workspace`
3. `add-python-package` — editable install of `src/<pkg>/` only,
   after `has_src` is true
4. `setup-git`

Then `status` again. Load `triage-ml-task` if it is installed,
otherwise stop. Do not start EDA or a pipeline.

## Stop conditions

- Do not pick package name or env manager here; the loaded skills
  ask those.
- Do not ask tabular library or skore mode.
- Do not install sklearn, skrub, skore, or pandas.
- Do not write experiment or pipeline bodies.
- Do not commit except by loading `setup-git`.
- Do not abort setup because one skill is missing.
