# export-ml-project eval

---

## CASE_01 — Ask then load children

**User prompt:**
> Export the project.

**Assumed workspace state:**
- `policy.notebooks` is false.
- `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.

**Must do:**
- Name `python -m skore_skills status`.
- AskUserQuestion `allow_multiple`: notebooks **not** preselected,
  site preselected.
- Load `export-ml-site` if site stays checked.

**Must NOT do:**
- Run `git end-turn`.
- Invent `mkdocs` steps instead of loading the child.

---

## CASE_02 — Missing child skips

**User prompt:**
> Export notebooks and the site.

**Assumed workspace state:**
- User checks both boxes.
- `status.skills.export-ml-notebook` is `false`.
- `status.skills.export-ml-site` is `true`.

**Must do:**
- Skip notebooks in one line because `export-ml-notebook` is not
  installed.
- Load `export-ml-site`.

**Must NOT do:**
- Invent `notebook convert` from memory.
- Treat the missing skill as an error that aborts export.
