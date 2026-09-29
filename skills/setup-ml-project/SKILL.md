---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Ask the installed
  pieces (all preselected), then in that same opening phase ask the
  environment manager, whether we manage the env, the import name,
  and git autocommit — only for boxes that stay checked and answers
  that are not already recorded. Persist those answers, then run
  only what stays checked. Git may ask once, just before the first
  commit, which unknown files to keep.
---

# Set Up ML Project

Ordering only. Never run a skipped skill's steps from memory.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Questions use data-science labels only (Python environment,
workspace layout, editable install, Git, environment manager,
whether we manage the Python environment, Python import name,
automatic commits). Do not put skill ids, `G-*` names, or the
wrapper CLI in the question.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status + env detect (read-only)
- [ ] ask which pieces (all installed boxes preselected)
- [ ] editable without workspace and no src → stop
- [ ] ask remaining choices; persist
- [ ] load selected | skip
- [ ] status again; load triage-ml-task only if
      status.skills.triage-ml-task is true
```

## Sequence

1. Run `python -m skore_skills status` and
   `python -m skore_skills env detect`. `status.skills` is a
   per-id dict, never a boolean. Do not `env init`, `scaffold`,
   install a package, or `git init` in this opening phase.
2. **AskUserQuestion** with `allow_multiple`. Say first, in 2–4
   lines, what the answer authorizes (which pieces run, in which
   order) and the `status` facts each box rests on — detected
   manager, `has_src`, git presence. A file link is an addition,
   never the context. Include a box only when **that** id is true.
   Option labels (user-visible, no ids):

   - Python environment
   - Workspace layout
   - Editable install — show when
     `status.skills.add-python-package` is true and (`has_src`
     is true **or** workspace is on this board)
   - Git

   Map checked labels to `setup-python-env`, `setup-workspace`,
   `add-python-package`, `setup-git` when loading.

   **Preselect every installed piece** (all boxes on). Do not
   leave a box off because the layout already looks done. The
   user may uncheck.
3. Editable checked, `has_src` false, and workspace not selected
   → one-line stop. Do not ask the remaining choices. Do not
   scaffold from this meta.
4. Ask the remaining choices **now**, before any write. Skip a
   question when its piece was unchecked or the value is already
   recorded. Each ask states in 2–4 lines what the answer
   authorizes. Order:

   - **Environment manager** — Python environment stayed
     checked. If `env_manager` is not `"none"`, `ambiguous` is
     false, `mismatch` is false, and `policy.env_manager` is
     unset, persist that detected manager. Do not ask. Otherwise
     ask when (`env_manager` is `"none"` and
     `policy.env_manager` is unset, or `ambiguous` is true, or
     `mismatch` is true). Ask with `AskUserQuestion`, using
     `recommended` order. PATH is not permission. Do not
     `curl | sh`. Persist
     `python -m skore_skills policy set env_manager <manager>`.
   - **Whether we manage the env** — Python environment stayed
     checked and `policy.env.managed` is null. Default yes.
     Persist `policy set env.managed true` or `false`.
   - **Python import name** — workspace stayed checked, the
     layout is fresh or manager-only (no `src/` and no
     `journal/`), `policy.package` is unset, and `src/<pkg>/`
     does not already name it. Folder name is the default
     option. “You pick” / “go fast” does not resolve it.
     Persist `policy set package <pkg>`.
   - **Automatic commits** — Git stayed checked and
     `policy.git.autocommit` is null. Ask once: should later
     stages persist with `git commit` (`on`) or never (`off`)?
     That answer consents to the first commit. It does not
     authorize tracking unknown hidden files or review paths.
     Persist `policy set git.autocommit on` or `off`.

   Do not ask notebooks, the documentation site, tabular
   library, or where reports go.
5. Load **still-checked** skills only, in this order: env →
   workspace → editable (`has_src`) → git. Load `<id>` only if
   `status.skills.<id>` is true; else one-line skip. Do not
   invent that skill's steps. The loaded skills must not ask
   again for a choice persisted in step 4.
6. Unchecked or that id is false → one-line skip.
7. `status` again. Load `triage-ml-task` only if
   `status.skills.triage-ml-task` is true; else stop. Do not
   start exploratory data analysis or a pipeline. That handoff
   may ask what to do next; it is not a setup question.

## Stop conditions

- Do not `env init`, `scaffold`, install a package, or `git init`
  until step 4 has finished.
- Do not ask tabular library, skore mode, notebooks, or site.
- Do not ask which hidden files or review paths to keep; `setup-git`
  asks that once, before the first commit.
- Do not install sklearn, skrub, or pandas. The selected
  `setup-python-env` skill installs plain `skore` during bootstrap;
  do not install or configure Skore directly from this coordinator.
- Do not write experiment or pipeline bodies.
- Do not commit except by loading `setup-git`.
- Do not abort setup because one skill is missing.
- Do not invent a missing skill's procedure.
- Do not `pixi add` / `uv add` from this coordinator;
  `add-python-package` owns install.
