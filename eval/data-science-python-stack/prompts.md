# data-science-python-stack eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Tier 1 mandatory libs at project start

**User prompt:**
> Starting a fresh ML project. What's the mandatory stack?

**Assumed workspace state:**
- Empty folder.

**Must do:**
- Name the Tier 1 mandatory libraries (sklearn, skrub, skore, ruff,
  pytest at minimum — read the skill for the full list).
- Mention these are installed at project start, no exceptions.
- Mention `python-env-manager` for the actual install mechanism.

**Must NOT do:**
- Skip the tabular library (that's Tier 2 — competing library).
- Recommend `mlflow` for tracking (skore is canonical;
  mlflow is reserved for serving / registry).
- Recommend `black` / `isort` / `flake8` (ruff is canonical).

---

## CASE_02 — Tier 2 tabular library: pandas vs polars structured ask

**User prompt:**
> Scaffold the workspace. Tabular regression task.

**Assumed workspace state:**
- Empty folder, fresh.
- `journal/JOURNAL.md` doesn't exist yet (no recorded
  `Workspace decisions`).

**Must do:**
- Fire **`AskUserQuestion`** for tabular library (G-TABULAR /
  pandas vs polars).
- Mention persisting the answer to `JOURNAL.md` Status
  `Workspace decisions` (handled by `iterate-ml-experiment`'s
  template).
- Surface the `Default-on-no-preference` if needed (per the
  Tier 2 table).

**Must NOT do:**
- Silently default to pandas because "skore pulls it in
  transitively".
- Treat "tabular regression" as resolving the pick.
- Recommend both libraries simultaneously.

---

## CASE_03 — Free-text "quick baseline" does NOT resolve the gate

**User prompt:**
> Quick baseline, you pick the libraries — go fast.

**Assumed workspace state:**
- Fresh workspace.

**Must do:**
- Refuse to silent-pick on competing-library jobs.
- Cite that "quick" / "go fast" / "you pick" do NOT resolve the
  Tier 2 competing-library gate.
- Surface the `Default-on-no-preference` and ask for confirmation
  (per free-text resolution rule: "You pick / no preference"
  surfaces the default and asks).
- Fire `AskUserQuestion` for the actual pick.

**Must NOT do:**
- Pick pandas (or any tabular lib) silently.
- Pick a deep-learning framework silently.
- Treat folder structure as a preference signal.

---

## CASE_04 — Missing dependency → install, not substitute

**User prompt:**
> `import skrub` raises `ModuleNotFoundError`. Should I just use
> `sklearn.Pipeline` instead?

**Assumed workspace state:**
- Project uses pixi.
- skore + sklearn already importable; skrub is missing.

**Must do:**
- Refuse the substitution.
- Cite that skrub is Tier 1 mandatory; missing dependency → install,
  not substitute.
- Route to `python-env-manager` for the right install command
  (`pixi add skrub` or equivalent).

**Must NOT do:**
- Rewrite the code as `sklearn.Pipeline` / `make_pipeline`.
- Drop skrub from the design.
- Treat the import failure as "skrub isn't right for this stack".

---

## CASE_05 — Refuse mlflow for tracking, redirect to skore

**User prompt:**
> Let's use `mlflow.log_metric` for tracking the experiment's
> metrics, since it's the industry standard.

**Assumed workspace state:**
- skore is installed.

**Must do:**
- Refuse the mlflow-for-tracking substitution.
- Cite that **skore** is canonical for evaluation / reporting /
  tracking in this stack.
- Mention mlflow's role is reserved for model serving / registry,
  not tracking.

**Must NOT do:**
- Add `import mlflow` to the workspace.
- Add `mlflow.log_metric(...)` to the experiment script.
- Treat "industry standard" as overriding the stack pick.

---

## CASE_06 — Refuse non-stack tree booster, redirect

**User prompt:**
> Switch the predictor to `xgboost.XGBRegressor`. It usually beats
> sklearn.

**Assumed workspace state:**
- `xgboost` not in the env.
- sklearn's `HistGradientBoostingRegressor` is available.

**Must do:**
- Surface that `xgboost` / `lightgbm` are NOT in this stack's Tier 1
  / Tier 2 (they're third-party substitutes).
- Recommend `sklearn.ensemble.HistGradientBoostingRegressor` as the
  in-stack equivalent.
- If the user has a specific reason for xgboost, route through the
  § "Competing libraries — general rule" path: treat it as a new
  competing-library job (add a row to the competing-jobs table OR
  surface the gap to the user) and name `AskUserQuestion` as the
  gate that resolves it.

**Must NOT do:**
- Run `pixi add xgboost` silently.
- Substitute the predictor without surfacing the stack mismatch.
- Treat "usually beats sklearn" as resolving a library choice.
