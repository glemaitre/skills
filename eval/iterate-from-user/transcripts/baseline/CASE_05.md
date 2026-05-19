# CASE_05 — New dependency gated, not assumed

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-from-user/SKILL.md` (297 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Synthesis from prior turn proposed adapting a paper's technique;
  `lightgbm` was the paper's choice.
- Current env has `sklearn`, `skrub`, `skore` but NOT `lightgbm`.]

The article we just discussed uses `lightgbm`. Let's add it to the
pipeline.
```

## Response

I need to pause here and clarify the dependency question before proceeding.

The article proposes `lightgbm`, but your current environment has `sklearn`, `skrub`, and `skore` — no `lightgbm` yet. Before I hand the Proposal to the planner, I need to resolve:

**Should we adapt the technique to work within the existing stack (e.g., use `sklearn.ensemble.GradientBoostingRegressor` instead), or is adding `lightgbm` as a new dependency the right call for this project?**

This is a genuine design choice, not a technicality. `lightgbm` has different tuning semantics and categorical handling than `sklearn`'s GBM, so the choice affects both the method outline and the implementation effort.

Can you confirm:
- Is `lightgbm` acceptable to add to the project environment (e.g., does it fit the dependencies you're willing to carry)?
- Or should I reframe the Proposal to use `sklearn`'s gradient boosting as the fallback?

Once you decide, I'll finalize the Proposal and hand it to `iterate-ml-experiment` for the design note.
