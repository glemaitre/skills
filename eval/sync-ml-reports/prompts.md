# sync-ml-reports eval

---

## CASE_01 — Switch local to Hub

**User prompt:**
> Switch the default destination to Hub workspace acme-corp for
> project load-forecast. Transfer now, not a dry run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- `experiments/01_baseline.py` has `skore.Project(name="load-forecast",
  mode="local", workspace=str(PROJECT_ROOT / "reports"))`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is set.
- `skore` is on PATH.
- `persist-ml-git` and `triage-ml-task` are installed.

**Must do:**
- Name `python -m skore_skills status`.
- Load `add-python-package` for Skore at Hub mode.
- Name `skore sync load-forecast --from=local --to=hub` with
  `--from-workspace` on `reports/` and `--to-workspace=acme-corp`.
- Persist `python -m skore_skills policy set skore_mode hub`.
- Rewrite the Project init to Hub form (`login` + `workspace="acme-corp"`).
- Name `python -m skore_skills git end-turn --stage evaluate`.

**Must NOT do:**
- Call `Project.sync` in Python.
- Run `git commit` in this skill.
- Ask G-SKORE-MODE as a first-time local / hub / mlflow pick.
- Pass `--from-workspace` / `--to-workspace` as an MLflow flag.

---

## CASE_02 — Copy only, keep local mode

**User prompt:**
> Copy our local reports to Hub workspace acme-corp for project
> load-forecast. Keep evaluating locally. Transfer now, not a dry
> run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- Project name is `load-forecast`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is set.
- `skore` is on PATH.

**Must do:**
- Name `python -m skore_skills status`.
- Name `skore sync` from `local` to `hub` with Hub
  `--to-workspace=acme-corp`.
- Name `python -m skore_skills git end-turn --stage evaluate`.

**Must NOT do:**
- Persist `policy set skore_mode`.
- Rewrite Project init blocks.
- Call `Project.sync` in Python.
- Run `git commit` in this skill.

---

## CASE_03 — Unset mode does not steal G-SKORE-MODE

**User prompt:**
> Upload the reports to Hub.

**Assumed workspace state:**
- `policy.skore_mode` is unset.
- `evaluate-ml-pipeline` is installed.

**Must do:**
- Name `python -m skore_skills status`.
- Stop because first pick is G-SKORE-MODE in
  `evaluate-ml-pipeline`.

**Must NOT do:**
- Run `skore sync`.
- Persist `policy set skore_mode`.
- Ask local / hub / mlflow as this skill's first G-SKORE-MODE.

---

## CASE_04 — Missing Hub API key

**User prompt:**
> Switch the default destination to Hub workspace acme-corp.
> Transfer now, not a dry run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- Project name is `load-forecast`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is unset / missing.

**Must do:**
- Name `python -m skore_skills status`.
- Name `SKORE_HUB_API_KEY` and stop.

**Must NOT do:**
- Open a browser login.
- Run `skore sync`.
- Call `Project.sync` in Python.
- Read `.skore` for the key.
