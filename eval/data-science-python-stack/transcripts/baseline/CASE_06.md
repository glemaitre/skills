# CASE_06 — Refuse non-stack tree booster, redirect

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/data-science-python-stack/SKILL.md` (430 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `xgboost` not in the env.
- sklearn's `HistGradientBoostingRegressor` is available.]

Switch the predictor to `xgboost.XGBRegressor`. It usually beats
sklearn.
```

## Response

I need to stop here and clarify a design point about this stack.

**The stack's rule is: use sklearn's `HistGradientBoosting{Classifier,Regressor}` instead of pulling in xgboost or lightgbm.** This is explicit in the [`scikit-learn`](references/scikit-learn.md) entry of Tier 1.

`HistGradientBoostingRegressor` is available in your env right now (pulled in by `scikit-learn`), and it's the stack's designated gradient-boosting tool. It's well-tuned for tabular data and integrates seamlessly with sklearn pipelines and `skore` evaluation.

**Why not xgboost here?**

- It's a *substitute* on a job already covered by Tier 1, not a new tool (see "One tool per job" convention).
- The stack avoids the xgboost/lightgbm/catboost proliferation so that every project has a consistent, learnable shape.
- `HistGradientBoosting` is genuinely competitive on most tabular tasks, especially when hyperparameter-tuned.

**If you want to benchmark xgboost against the sklearn booster,** that's a fair experiment — but it would be an *optional* addition (Tier 3), not a replacement. The decision to add it would need to be explicit and live in `journal/JOURNAL.md` Status as a `Workspace decisions` row.

**Want to proceed with `HistGradientBoostingRegressor` as-is, or do you want to make a case for adding xgboost as an experimental alternative?**
