---
name: export-ml-site
description: >
  Package JOURNAL, exploratory data analysis markdown, and design notes into an offline
  MkDocs site opened via <package>.html at the workspace root. Embeds existing notebook HTML
  companions in their associated reports. Never executes Python. Trigger
  when the user asks for a website, mkdocs, or documentation site.
---

# Export ML Site

The site is a derived index of files other skills already write.
Markdown is the report: its figures, TableReport HTML, and existing
converted notebooks (`<stem>.nb.html`, written only by
`export-ml-notebook` with `notebook convert --html`) are embedded
inline. HTML viewers have open-separately and fullscreen controls.
Each experiment design note has one `## Notebooks` section:
evaluation first, then audit; a missing viewer is omitted.
The gitignored serialized Skore `reports/` directory is private
runtime state and is never copied into the site. Only Markdown and
already-generated notebook/HTML viewers are exported.
On desktop, site pages are in the top bar (experiments in a
scrollable dropdown) and the page contents are in a collapsible
left rail beside a 1200px report column. Mobile uses a drawer.

## Sequence

1. `python -m skore_skills status`. Read `policy.site`.
2. If `policy.site` is `null`: AskUserQuestion documentation site
   on/off (default off). Persist. If true, load
   `add-python-package` for `mkdocs-material` (agent) then
   `python -m skore_skills site init`. If false, stop.
3. If `policy.site` is false: say the gate is off; offer to turn
   it on. Do not init or build until it is true.
4. If this is the first site turn, run `site init` (gitignore
   only). Later turns only `site build`.
5. `python -m skore_skills site build`. Do not run
   `notebook convert`. Name a build error; the markdown sources
   remain the record. Tell the user to open `<package>.html` at
   the workspace root (`status.package`; double-click; no server).

## Stop conditions

- Do not `git commit` or `git end-turn`.
- Do not `pixi add` / `uv add`; load `add-python-package`.
- Do not convert or execute `# %%` scripts.
- Do not copy or link serialized files from gitignored `reports/`.
- Skip in one line if this skill is not installed.
