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
- Invent a deleted iterate skill as the session owner.
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

---

## CASE_04 — Generic bootstrap

**User prompt:**
> Bootstrap this project for me.

**Assumed workspace state:**
- Empty folder.
- `status.skills.setup-ml-project` is `true`.
- `status.skills.setup-python-env` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `setup-ml-project` without listing the catalog menu.

**Must NOT do:**
- Load `setup-python-env` as the certain skill.
- Ask which entry skill to run.

---

## CASE_05 — Certain env manager request

**User prompt:**
> Get pixi going for this folder.

**Assumed workspace state:**
- Empty folder.
- `status.skills.setup-python-env` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `setup-python-env` without listing the catalog menu.

**Must NOT do:**
- Load `setup-ml-project` as the certain skill.
- Ask which entry skill to run.

---

## CASE_06 — Certain EDA request

**User prompt:**
> Explore the data in data/.

**Assumed workspace state:**
- Scaffolded workspace with `data/` present.
- `status.skills.explore-ml-data` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `explore-ml-data` without listing the catalog menu.

**Must NOT do:**
- Ask which entry skill to run.
- Start EDA methodology in triage instead of loading the skill.
