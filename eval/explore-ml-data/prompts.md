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
- Load `add-python-package` for the chosen frame library,
  `skrub`, `matplotlib`, and `seaborn`.
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
- Scaffold exists. G-TABULAR is `pandas`. Skrub, IPython,
  matplotlib, and seaborn are installed.
- JOURNAL names target `MedHouseVal` (regression).
- Raw data path is known.
- User chose **run** for G-DATA-ANALYSIS.

**Must do:**
- Write `data_analysis/data_analysis_<table>.html` (not under `data/`).
- End overview cells on `TableReport` (or the frame), not on a
  json/dict digest.
- Include duplicate, target-distribution, bivariate-vs-target, and
  leakage cells (not TableReport dtypes/histograms/associations).
- Embed or link that HTML from `data_analysis/data_analysis.md`.
- Put `TableReport.json()` under `scratch/data_analysis/<table>.json`
  and extras under `scratch/data_analysis/extras.json`.

**Must NOT do:**
- Put unique-ratio / column-dict / `report.json()` cells in
  `data_analysis/data_analysis.py`.
- Write HTML under `data/`.
- Modify the user's raw data files.
- Train/test split or install sklearn unless extras were requested.

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

## CASE_07 — Notebook and site on after EDA

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.
- `jupytext`, `nbclient`, and `nbconvert` are installed.

**Must do:**
- Name `python -m skore_skills notebook convert
  data_analysis/data_analysis.py --html` before site build.
- Name `python -m skore_skills site build` before git end-turn.
- Name `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Fail the data-analysis turn if site build errors; name the error.
- Run `cells run` as a substitute for convert.
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

---

## CASE_09 — Notebooks on, site off converts without HTML

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is false.
- `export-ml-notebook` is installed.
- `jupytext` and `nbclient` are installed.

**Must do:**
- Name `python -m skore_skills notebook convert
  data_analysis/data_analysis.py`.
- Name `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Pass `--html` when the site gate is off.
- Run `python -m skore_skills site build`.

---

## CASE_10 — Missing convert toolchain skips in one line

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- `policy.notebooks` is true. `policy.site` is false.
- `export-ml-notebook` is installed.
- `jupytext` and `nbclient` are not importable; `notebook convert`
  fails with that ImportError.

**Must do:**
- Skip the convert in one line, naming `add-python-package` for
  `jupytext` and `nbclient`.
- Name `python -m skore_skills git end-turn --stage data_analysis`.

**Must NOT do:**
- Fail the data-analysis turn because convert failed.
- Run `pixi add` / `uv add` from this skill.

---

## CASE_11 — Default run adds ML-gap cells

**User prompt:**
> Explore the California housing CSV. Target is MedHouseVal.

**Assumed workspace state:**
- Scaffold exists. G-TABULAR is `pandas`.
- `add-python-package` is installed.
- User chose **run** for G-DATA-ANALYSIS.
- IPython is available.

**Must do:**
- Load `add-python-package` for `matplotlib` and `seaborn` (and
  skrub / pandas if missing).
- Write duplicate, target-distribution, bivariate-vs-target, and
  leakage cells in `data_analysis/data_analysis.py`.
- After `data_analysis.md`, AskUserQuestion keep exploring vs
  close (**Close** preselected).

**Must NOT do:**
- Re-plot TableReport univariate histograms or the association
  matrix in extra cells.
- Install sklearn, skore, or pytest on the default path.
- Train/test split the raw table.
- Run `git end-turn` before the user picks Close.

---

## CASE_12 — Unspecified target asks, does not guess

**User prompt:**
> Explore the dataset.

**Assumed workspace state:**
- Scaffold exists. User chose **run**.
- JOURNAL Goal does not name a column.
- Column names are `A`, `B`, `C`.

**Must do:**
- AskUserQuestion for the target (column list plus "no target
  yet") before writing target-aware cells.

**Must NOT do:**
- Guess a target column silently.
- Skip the duplicate-row cell when the user picks "no target yet".

---

## CASE_13 — Prompt already asked for PCA

**User prompt:**
> Explore the data and add a PCA plot of the numeric columns.

**Assumed workspace state:**
- Scaffold exists. User chose **run**. Target is known.
- `add-python-package` is installed.

**Must do:**
- Load `add-python-package` for `scikit-learn`.
- Append a PCA cell from `references/extra_analyses.md`.
- Do not re-ask PCA on the extras board.

**Must NOT do:**
- Treat PCA as a pipeline preprocessor in this skill.
- Run `pixi add scikit-learn` from this skill.

---

## CASE_14 — Close after default pass keeps sklearn off

**User prompt:**
> Explore the dataset. Target is MedHouseVal.

**Assumed workspace state:**
- Default notebook, extras.json, and `data_analysis.md` are on
  disk.
- User picks **Close** on keep-exploring vs close.

**Must do:**
- AskUserQuestion keep exploring vs close (**Close** preselected).
- Name `python -m skore_skills git end-turn --stage data_analysis`
  after Close.

**Must NOT do:**
- Load `add-python-package` for sklearn / scipy / statsmodels.
- Leave modelling implications empty of duplicate/target/leakage
  findings.

---

## CASE_15 — Keep exploring does not end the turn

**User prompt:**
> Explore the dataset. Target is MedHouseVal.

**Assumed workspace state:**
- `data_analysis/data_analysis.md` was just written.
- User picks **Keep exploring the data**.

**Must do:**
- AskUserQuestion extras / research this concern / describe what
  to plot.
- Stay in `explore-ml-data`.

**Must NOT do:**
- Name `python -m skore_skills git end-turn`.
- Invent a domain-specific checklist skill or `references/domains/`.
- Run `python -m skore_skills site build` on keep exploring.

---

## CASE_16 — Keep exploring then research

**User prompt:**
> Is 0.97 correlation with the target leakage?

**Assumed workspace state:**
- EDA markdown exists. User picked Keep exploring, then Research
  this concern.
- `status.skills.research-ml-practice` is true.

**Must do:**
- Load `research-ml-practice`.
- After it returns, copy confirmed candidates into
  `data_analysis.md` even if the `.py` did not change.

**Must NOT do:**
- Drop the correlated column from the raw data.
- Run `git end-turn` in this keep-exploring pass.
- Append a research-recommended plot cell without user
  confirmation.

---

## CASE_17 — Research skill missing is a one-line skip

**User prompt:**
> Is 0.97 correlation with the target leakage?

**Assumed workspace state:**
- EDA markdown exists. User picked Keep exploring, then Research
  this concern.
- `status.skills.research-ml-practice` is false or absent.

**Must do:**
- One-line skip that `research-ml-practice` is not installed.
- Stay in the keep-exploring menu (re-ask extras / research /
  describe what to plot, or keep vs close).

**Must NOT do:**
- Invent papers or leakage thresholds from memory.
- Run `git end-turn` in this keep-exploring pass.
