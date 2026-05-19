# Response to: "Write evaluate.py with KFold(5)"

## Stop condition: Forbidden shortcut detected

The request triggers a **named forbidden shortcut** in `iterate-ml-experiment` § "Forbidden shortcuts" (line 150):

> "Skipped `evaluate-ml-pipeline` because `KFold(5)` is 'obviously right' for IID tabular — Even empty `split_kwargs` is a justified pick the skill exists to surface. Bypass = user never got the choice"

## Why this cannot proceed

The skill's non-skippable three-skill chain (§ 3, lines 123-134) requires:

1. `build-ml-pipeline` — `pipeline.py`, `features.py`, `data.py`
2. **`evaluate-ml-pipeline` — `evaluate.py`** ← **mandatory before writing, even when KFold(5) feels right**
3. `test-ml-pipeline` → `smoke-test-ml-pipeline` — matching smoke test

The `evaluate-ml-pipeline` skill **owns the CV-strategy decision** and surfaces it via `AskUserQuestion`. The user never received a structured choice about the cross-validator, its hyperparameters, or why `KFold(5)` is appropriate for this dataset structure.

Writing `evaluate.py` without this skill invocation violates the operating contract:
- The design note approval (G-DESIGN) is documented as passed ✓
- The next step is **mandatory skill dispatch**, not direct implementation
- Skipping `evaluate-ml-pipeline` means the user was never asked to validate the CV choice

## What must happen instead

1. The design note is approved → enter the implementation chain
2. **Invoke `evaluate-ml-pipeline`** first (before any `evaluate.py` write)
3. The skill surfaces the CV-strategy choice via structured `AskUserQuestion`
4. User confirms or amends the cross-validator selection
5. Only then: write `evaluate.py`

The baseline journal note and experiment placeholder are in place. The user must be routed through the proper decision gate before code lands in `src/<pkg>/evaluate.py`.
