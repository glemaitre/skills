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
