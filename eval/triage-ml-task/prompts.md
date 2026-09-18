# triage-ml-task eval

---

## CASE_01 — Ambiguous capability request

**User prompt:**
> What can you help me with on this machine learning project?

**Assumed workspace state:**
- Existing scaffold with no specific task requested.
- No `.skore` file.
- `status.data_analysis` is `missing`.
- `status.skills` reports the usual entry skills `true`.

**Must do:**
- Name `python -m skore_skills status`.
- AskUserQuestion listing installed entry skills
  (`setup-ml-project`, `explore-ml-data`, `model-ml-pipeline`,
  `evaluate-ml-pipeline`, `audit-ml-pipeline`,
  `manage-ml-backlog`, `export-ml-project` if installed). One pick.
- Name `explore-ml-data` as the recommended next stage; do not
  auto-load it.
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
- Start exploratory data analysis methodology in triage instead of loading the skill.

---

## CASE_07 — Model request while EDA is missing

**User prompt:**
> Build the first baseline model.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.data_analysis` is `missing`.
- `status.skills.explore-ml-data` is `true`.
- `status.skills.model-ml-pipeline` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- AskUserQuestion: run exploratory data analysis first (default) vs proceed to modeling
  with user-supplied facts.
- Do not invent dataset facts.

**Must NOT do:**
- Auto-load `model-ml-pipeline`.
- Auto-load `explore-ml-data` without asking.

---

## CASE_08 — Model request after EDA is present

**User prompt:**
> Build the first baseline model.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.data_analysis` is `present`.
- `status.skills.model-ml-pipeline` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `model-ml-pipeline` without an exploratory data analysis AskUserQuestion.

**Must NOT do:**
- Ask which entry skill to run.
- Load `explore-ml-data` first.

---

## CASE_09 — Certain notebook request

**User prompt:**
> Give me an executed ipynb of the EDA.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.skills.export-ml-notebook` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `export-ml-notebook` without listing the catalog menu.

**Must NOT do:**
- Load `export-ml-project` as the certain skill.
- Ask which entry skill to run.

---

## CASE_10 — Certain website request

**User prompt:**
> Build the MkDocs documentation site.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.skills.export-ml-site` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `export-ml-site` without listing the catalog menu.

**Must NOT do:**
- Load `export-ml-project` as the certain skill.
- Ask which entry skill to run.

---

## CASE_11 — Generic export

**User prompt:**
> Export the project.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.skills.export-ml-project` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `export-ml-project` without listing the catalog menu.

**Must NOT do:**
- Load `export-ml-notebook` as the certain skill.
- Ask which entry skill to run.

---

## CASE_12 — Certain HTML notebook request

**User prompt:**
> Give me an HTML notebook of the EDA.

**Assumed workspace state:**
- Scaffolded workspace.
- `status.skills.export-ml-notebook` is `true`.

**Must do:**
- Name `python -m skore_skills status`.
- Load `export-ml-notebook` without listing the catalog menu.

**Must NOT do:**
- Load `export-ml-project` as the certain skill.
- Load `export-ml-site` as the certain skill.
- Ask which entry skill to run.
