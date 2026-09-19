# choose-python-library eval

---

## CASE_01 — Competing optional libraries

**User prompt:**
> Add either optuna or scikit-optimize for tuning. You choose.

**Assumed workspace state:**
- Pixi project; neither package is installed.
- The stack does not fix one canonical tuning library.
- `add-python-package` is installed (`status.skills` true).

**Must do:**
- Present the smallest useful comparison and ask the user to choose.
- After a choice, load `add-python-package` rather than calling
  `env add` directly.

**Must NOT do:**
- Install both candidates.
- Pick silently because the user said “you choose.”
- Run `pip install`.
- Run `python -m skore_skills env add` from this skill.

---

## CASE_02 — Add skill not installed

**User prompt:**
> Add either optuna or scikit-optimize for tuning.

**Assumed workspace state:**
- Pixi project; neither package is installed.
- The stack does not fix one canonical tuning library.
- `status.skills.add-python-package` is `false`.

**Must do:**
- Ask the user to choose.
- After a choice, name the package and stop.

**Must NOT do:**
- Run `python -m skore_skills env add`.
- Invent the `add-python-package` procedure from memory.

---

## CASE_03 — Plotting is not a competing ask

**User prompt:**
> Which plotting library should I use, matplotlib or seaborn?

**Assumed workspace state:**
- `plot-ml-figure` is installed (`status.skills` true).

**Must do:**
- Load `plot-ml-figure` rather than asking matplotlib vs seaborn
  vs plotly.

**Must NOT do:**
- Present the competing plotting set as a user choice.
- Run `pip install`.
