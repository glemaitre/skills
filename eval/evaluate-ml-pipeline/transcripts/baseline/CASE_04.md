# CASE_04 — Empty `split_kwargs` BUT possible group structure

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/evaluate-ml-pipeline/SKILL.md` (372 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `pipeline.py` X-marker has empty `split_kwargs`.
- `region` is a potential group key but wasn't wired in.]

Wire `evaluate.py`. The data has a `region` column. Not sure if
we should treat it as a group.
```

## Response

# Decision Gate: Is `region` a natural grouping variable?

Before I write `evaluate.py`, I need to understand the structural role of `region` in your data. This determines whether it becomes a group key in the splitter.

**Fire `AskUserQuestion`:**

---

In your dataset, does `region` represent a natural *grouping structure* that should be respected during cross-validation? That is:

1. **Yes, groups** — Observations within the same region are not independent (e.g., regional market effects, geographic clustering, institutional affiliation). A single fold should not mix train and test regions; each region should appear wholly in either the train or test set of a fold. Use `GroupKFold`.

2. **No, covariate only** — `region` is just a feature. Observations are independent across regions; there's no structural reason to keep a region intact during folding. Use plain `KFold`.

3. **Uncertain — need to look at the data** — Show me: (a) the unique region count, (b) rows per region (distribution), (c) whether regions have inherent hierarchies or dependencies. I'll help you decide.

4. **Domain-specific logic** — The answer depends on something else (e.g., "only if we have ≥10 regions", "yes, but only for the validation stage, not hyperparameter tuning"). Describe the logic.

---

**Which applies to your case?** Once you pick, I'll:
- Route `region` into `split_kwargs` in `pipeline.py` (via `build-ml-pipeline` if needed), or confirm it stays as a covariate.
- Wire the right splitter (`GroupKFold` or `KFold`) into `evaluate.py`.
- Emit the pre-flight checklist and write the evaluation code.
