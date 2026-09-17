# explore-ml-data eval

---

## CASE_01 — End of turn uses git hook

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `eda/eda.md` was just written.

**Must do:**
- Name `python -m skore_skills git end-turn --stage eda`.
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
- Do not place `eda/eda.py` before the gate resolves.

**Must NOT do:**
- Silent-default pandas and write `eda.py` first.
- Install sklearn, skore, or pytest in this turn.
- Call `env add` from this skill instead of `add-python-package`.
