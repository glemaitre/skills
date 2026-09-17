# triage-ml-task eval

---

## CASE_01 — Ambiguous capability request

**User prompt:**
> What can you help me with on this machine learning project?

**Assumed workspace state:**
- Existing scaffold with no specific task requested.
- No `.skore` file.
- `status.skills` reports the usual entry skills `true`.

**Must do:**
- Name `python -m skore_skills status`.
- AskUserQuestion listing installed entry skills
  (`setup-ml-project`, `explore-ml-data`, `model-ml-pipeline`,
  `evaluate-ml-pipeline`, `audit-ml-pipeline`,
  `manage-ml-backlog` if installed). One pick.
- Do not treat the missing `.skore` as an empty project despite
  the existing scaffold.

**Must NOT do:**
- Start designing the next experiment.
- Claim to have loaded or executed every skill.
- Treat `iterate-ml-experiment` as the session owner.
- Auto-load a stage skill without asking.
- Ask only stay / go deeper / next stage without naming entry
  skills.

---

## CASE_02 — Certain git request

**User prompt:**
> Initialize git here.

**Assumed workspace state:**
- Scaffolded workspace, no `.git`.
- `status.skills.setup-git` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `setup-git` without listing the catalog menu.

**Must NOT do:**
- Ask which entry skill to run.
- Invent `git init` procedure in triage instead of loading
  `setup-git`.

---

## CASE_03 — Git skill not installed

**User prompt:**
> Initialize git here.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.skills.setup-git` is `false`.

**Must do:**
- Skip in one line because `setup-git` is not installed.

**Must NOT do:**
- Run `git init` or invent the `setup-git` procedure from memory.
- Treat the missing skill as an error that aborts the session.
