---
name: export-ml-project
description: >
  Coordinate on-demand export: executed notebooks and/or an
  offline MkDocs documentation site. Trigger on a generic
  "export" request, or to flip the notebooks/site gates after
  setup.
---

# Export ML Project

Ordering only. Children own convert and site commands.

## Sequence

1. `python -m skore_skills status`. Read `policy.notebooks`,
   `policy.site`, and `skills`.
2. **AskUserQuestion** with `allow_multiple`:

   - Executed notebooks — preselected iff `policy.notebooks` is
     true
   - Documentation site — preselected iff `policy.site` is true

3. Persist each box (`true` / `false`). JOURNAL
   workspace-decisions `notebooks` / `site` `on|off`.
4. Load checked children if `skills` is true; missing skill →
   one-line skip:

   - notebooks → `export-ml-notebook` (installs toolchain if this
     is the first yes, then convert; `--html` only if the user
     wants the notebook viewer on the site)
   - site → `export-ml-site` (installs `mkdocs-material` if first
     yes, init if needed, then build; never convert)

5. Return to `triage-ml-task` if installed.

## Stop conditions

- Do not `git end-turn` or `git commit`.
- Do not invent convert or `mkdocs` steps when the child skill is
  missing.
- Do not `pixi add` / `uv add` from this coordinator.
