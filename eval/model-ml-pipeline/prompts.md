# model-ml-pipeline eval

---

## CASE_01 — Approved model implementation

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.

**Must do:**
- Dispatch build, evaluate, then smoke-test in that order.
- Preserve the matching experiment stem.
- Name `python -m skore_skills git end-turn --stage implement`
  after build and smoke.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Replace skrub DataOps with a bare sklearn Pipeline.
- Mark the experiment done while smoke tests fail.
- Run `git commit` in this skill or `git push`.
- Distill `scratch/research/` here instead of loading
  `build-ml-pipeline`.

---

## CASE_02 — Missing design note stops before code

**User prompt:**
> Implement experiment 02 for the selected target transform.

**Assumed workspace state:**
- The Backlog choice is confirmed with stem `02_target_transform`.
- `journal/02_target_transform.md` does not exist.

**Must do:**
- Name `python -m skore_skills scaffold --journal --stem
  02_target_transform` to create the packaged design-note shell.
- State that Question, Motivation, Method, and Risks are filled only
  after that command creates the shell, then stop for user approval.

**Must NOT do:**
- Write model or experiment code before the design note is approved.
- Recreate or fill the design-note shape from memory when the CLI
  command did not run this turn.

---

## CASE_03 — Site on rebuilds after implement

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.
- `policy.site` is true. `policy.notebooks` is false.
- `export-ml-site` is installed.

**Must do:**
- Dispatch build, evaluate, then smoke-test in that order.
- Name `python -m skore_skills site build` after smoke, before
  git end-turn.
- Name `python -m skore_skills git end-turn --stage implement`.

**Must NOT do:**
- Fail the model turn if site build errors; name the error.
- Run `notebook convert` while the notebooks gate is off.
- Run `git commit` in this skill or `git push`.

---

## CASE_04 — Notebooks on converts the experiment script

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Approved design note and experiment shell exist with stem
  `01_baseline`.
- `policy.notebooks` is true. `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.
- `jupytext`, `nbclient`, and `nbconvert` are installed.

**Must do:**
- Name `python -m skore_skills notebook convert
  experiments/01_baseline.py --html` after smoke, before site
  build.
- Name `python -m skore_skills site build` before git end-turn.
- Name `python -m skore_skills git end-turn --stage implement`.

**Must NOT do:**
- Fail the model turn if convert errors; name the error.
- Run `cells run` as a substitute for convert.
- Run `git commit` in this skill or `git push`.
