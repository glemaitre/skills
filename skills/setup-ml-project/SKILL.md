---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Ask a multi-select
  of installed pieces (env, workspace, editable, git), all
  preselected; run only what stays checked.
---

# Set Up ML Project

Ordering only. Never run a skipped skill's steps from memory.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (read skills + has_src)
- [ ] ask which pieces (all installed boxes preselected)
- [ ] load selected | skip
- [ ] status again; load triage-ml-task if installed
```

## Sequence

1. Run `python -m skore_skills status`.
2. **AskUserQuestion** with `allow_multiple`. Include a box only
   when `status.skills` is true:

   - Python environment (`setup-python-env`)
   - Workspace layout (`setup-workspace`)
   - Editable install (`add-python-package`) — show when that
     skill is installed and (`has_src` is true **or** workspace
     is on this board)
   - Git (`setup-git`)

   **Preselect every installed piece** (all boxes on). Do not
   leave a box off because the layout already looks done. The
   user may uncheck.
3. Load **still-checked** skills only, in this order: env →
   workspace → editable (`has_src`) → git.
4. Unchecked or `skills: false` → one-line skip.
5. Editable checked, `has_src` false, and workspace not selected
   → one-line stop. Do not scaffold from this meta.
6. `status` again. Load `triage-ml-task` if installed, else stop.
   Do not start EDA or a pipeline.

## Stop conditions

- Do not pick package name or env manager here; the loaded skills
  ask those.
- Do not ask tabular library or skore mode.
- Do not install sklearn, skrub, skore, or pandas.
- Do not write experiment or pipeline bodies.
- Do not commit except by loading `setup-git`.
- Do not abort setup because one skill is missing.
- Do not invent a missing skill's procedure.
