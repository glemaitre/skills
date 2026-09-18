# export-ml-site eval

---

## CASE_01 — Init then build

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is true.
- `mkdocs-material` is installed.
- The workspace is scaffolded.

**Must do:**
- Name `python -m skore_skills site init`.
- Name `python -m skore_skills site build`.
- Name `html/index.html` as the file to open.

**Must NOT do:**
- Run `notebook convert`.
- Run `git commit`.
- Load `add-python-package` for `jupytext` or `nbclient`.

---

## CASE_02 — Later turns only build

**User prompt:**
> Rebuild the site.

**Assumed workspace state:**
- `policy.site` is true.
- `site init` already ran.

**Must do:**
- Name `python -m skore_skills site build`.
- Do not run `site init` again.
- Name `html/index.html` as the file to open.

**Must NOT do:**
- AskUserQuestion for the site gate again.
- Run `notebook convert`.
- Run `git end-turn`.

---

## CASE_03 — Gate off

**User prompt:**
> Build the MkDocs site.

**Assumed workspace state:**
- `policy.site` is false.

**Must do:**
- Say the documentation-site gate is off and offer to turn it on.

**Must NOT do:**
- Run `site init` or `site build` while the flag is false.

---

## CASE_04 — Null gate installs mkdocs only

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is null.
- `add-python-package` is installed.

**Must do:**
- AskUserQuestion documentation site (default off).
- If the user says yes: persist `site true`, load
  `add-python-package` for `mkdocs-material`, then init and build.

**Must NOT do:**
- Install `jupytext`, `nbclient`, or `nbconvert` for the site gate.
- Convert while only turning the site on.
