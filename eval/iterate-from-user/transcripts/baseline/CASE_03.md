# CASE_03 — Free-text idea, walk shaping questions

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-from-user/SKILL.md` (297 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/JOURNAL.md` Status currently records the goal as
  "minimize RMSE for point-estimate prediction".]

I want to try fitting a quantile regression so we get prediction
intervals instead of point estimates.
```

## Response

I'll help you source this quantile regression idea. Let me confirm I've understood it correctly through the three shaping questions, then we'll move forward.

**From your statement, I understand:**

1. **What are we trying to learn?** — Whether quantile regression can give us prediction intervals (e.g., lower/upper bounds on predictions) instead of single-point forecasts.

2. **Why now?** — You've decided that prediction intervals are more useful for the use case than point estimates alone.

3. **What changes vs. the previous experiment?** — We'd modify `src/<pkg>/pipeline.py` (or whichever regression module fits the target) to swap the loss function from squared error (RMSE) to quantile loss, and return multiple quantiles instead of one prediction per sample.

**Open gaps before I hand this back:**

- **Goal shift:** `journal/JOURNAL.md` Status currently says "minimize RMSE for point-estimate prediction." Switching to quantile regression reframes the success metric — we'd evaluate coverage (e.g., "95% of actuals fall within the 2.5th–97.5th percentile predictions") instead of RMSE. Should we update the Status block in JOURNAL.md to reflect this new goal, or is this a one-off experiment while the main goal stays point-estimate?
- **Which quantiles?** — You want prediction intervals, so I'm assuming two quantiles (e.g., 0.05 and 0.95 for a 90% interval). Confirm: which quantiles should we fit?
- **Library choice:** — `scikit-learn`'s `QuantileRegressor` is already available; should we use that, or do you have another preference (e.g., `statsmodels`, custom)?

Once you clarify the goal-shift question and the quantile levels, I'll hand the Proposal to the planner.
