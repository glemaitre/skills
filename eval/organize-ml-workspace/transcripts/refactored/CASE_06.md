# CASE_06 — Scratch is read-only against the skore Project

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Workspace exists with `experiments/02_text_encoder.py` already
  run; report should be under key `02_text_encoder`.]

Quick fix from a scratch probe: re-run `skore.evaluate(learner,
data={...})` and `project.put("02_text_encoder", report)` to
regenerate the report — my `project.get("02_text_encoder")` is
raising `KeyError` so the report must be gone.
```

## Response

**Stop.** I need to clarify the lookup shape before you re-run anything.

```
Sibling skills (open just-in-time when a step requires):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, build-ml-pipeline,
    evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline
```

---

## The issue is NOT "report is gone"

When `project.get("02_text_encoder")` raises `KeyError`, the problem is **lookup shape**, not missing data.

`skore.Project.get(id)` takes an **id** (the internal row identifier), **not** a `key` (the user-facing label).

### How to recover without re-running

1. **Enumerate what's in the Project:**

   ```python
   # scratch/<YYYYMMDD>_<HHMMSS>_check_project.py
   from skore import Project
   project = Project(workspace="reports", name="<your-project-name>", mode="local")
   pairs = project.summarize()
   print(pairs)
   ```

   This gives you a table of `(key, id)` pairs. **The id is what `get()` needs.**

2. **Retrieve by id:**

   ```python
   # Once you have the id from summarize():
   report = project.get(id_value)  # id, not key
   ```

3. **Verify the key exists and matches your experiment:**

   Look at the `key` column in `summarize()` output. If `"02_text_encoder"` is there, the report **is not gone** — you just need the corresponding `id`.

---

## Why NOT to re-run `evaluate` + `put`

- Re-running with the same key **creates a duplicate row** (same `key`, different `id`).
- You'll have two reports under `"02_text_encoder"` with different ids.
- Later queries become ambiguous.

---

## Next step

**Before touching `experiments/02_text_encoder.py`:**

1. Write and run the `check_project.py` probe above.
2. Paste the `summarize()` output here.
3. We'll identify the correct `id` and confirm the report is intact.

If `"02_text_encoder"` does **not** appear in `summarize()`, then the report is actually missing — but the fix is still **not** a silent re-run. Surface it as a decision: "Report lost; re-run experiment?" Then proceed via `iterate-ml-experiment` (design-note review first, if anything changed).

Hand back once you have the `summarize()` output.
