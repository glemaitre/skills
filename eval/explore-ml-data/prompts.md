# explore-ml-data eval

---

## CASE_01 — End of turn uses git hook

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.

**Must do:**
- Name `python -m skore_skills git end-turn --stage data_analysis`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Run `git commit` in this skill.
- Run `git push`.

---

## CASE_02 — G-TABULAR before first EDA script

**User prompt:**
> Explore the dataset before we design a model.

**Assumed workspace state:**
- Scaffold exists (`has_src`, `journal/JOURNAL.md`).
- Raw data path is known.
- `policy.tabular` is unset.
- `choose-python-library` and `add-python-package` are installed.

**Must do:**
- Read `status.policy.tabular` and fire G-TABULAR (pandas vs
  polars, recommend pandas) via `choose-python-library` or ask
  here if that skill is missing.
- Persist `policy set tabular` after confirmation.
- Load `add-python-package` for the chosen frame library and
  `skrub` (confirm skrub is required).
- Do not place `data_analysis/data_analysis.py` before the gate resolves.

**Must NOT do:**
- Silent-default pandas and write `data_analysis.py` first.
- Install sklearn, skore, or pytest in this turn.
- Call `env add` from this skill instead of `add-python-package`.

---

## CASE_03 — Skip G-DATA-ANALYSIS

**User prompt:**
> Skip the EDA. I already know the data.

**Assumed workspace state:**
- Scaffold exists (`has_src`, `journal/JOURNAL.md`).
- `status.data_analysis` is `missing`.
- No `data_analysis/data_analysis.md`.

**Must do:**
- Record JOURNAL § Data understanding `Status: skipped` with a
  date.
- Stop without placing `data_analysis/data_analysis.py`.

**Must NOT do:**
- Run `python -m skore_skills cells run`.
- Write `data_analysis/data_analysis.py` or `data_analysis/data_analysis.md`.
- Pick a package name or start modeling.
- Run `python -m skore_skills site build`.

---

## CASE_04 — EDA already present, no refresh

**User prompt:**
> Explore the dataset.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` exists.
- JOURNAL § Data understanding records `Status: done`.
- The user did not ask to re-run or refresh EDA.

**Must do:**
- Detect exploratory data analysis already recorded (`status.data_analysis` present).
- Stop without overwriting `data_analysis/data_analysis.py` or `data_analysis/data_analysis.md`.

**Must NOT do:**
- Re-run `cells run` or rewrite the report.
- Design a model in this skill.

---

## CASE_05 — Human notebook vs agent scratch

**User prompt:**
> Explore the dataset. Write the TableReport HTML next to the EDA
> script.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`. Skrub and IPython are
  installed.
- Raw data path is known.
- User chose **run** for G-DATA-ANALYSIS.

**Must do:**
- Write `data_analysis/data_analysis_<table>.html` (not under `data/`).
- End overview cells on `TableReport` (or the frame), not on a
  json/dict digest.
- Embed or link that HTML from `data_analysis/data_analysis.md`.
- Put `TableReport.json()` under `scratch/data_analysis/`, not in `data_analysis.py`.

**Must NOT do:**
- Put unique-ratio / column-dict / `report.json()` cells in
  `data_analysis/data_analysis.py`.
- Write HTML under `data/`.
- Modify the user's raw data files.

---

## CASE_06 — Missing IPython delegates to add-python-package

**User prompt:**
> Run the EDA now.

**Assumed workspace state:**
- Scaffold exists. User chose **run**.
- `ipython` is not importable in the project env.
- `add-python-package` is installed.

**Must do:**
- Load `add-python-package` for `ipython` (`env route` agent
  scope). Do not place a fabricated digest.

**Must NOT do:**
- Run `pixi add ipython` / `uv add ipython` from this skill.
- Hand-write expected exploratory data analysis output.

---

## CASE_07 — Site on rebuilds after EDA

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- Name `python -m skore_skills site build` before git end-turn.
- Name `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Fail the data-analysis turn if site build errors; name the error.
- Run `notebook convert`.
- Run `git commit` in this skill.

---

## CASE_08 — Site off skips rebuild

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.site` is false.

**Must do:**
- Skip site build in one line.
- Name `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Run `python -m skore_skills site build`.
