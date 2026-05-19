# Investigation: Missing Baseline Report

## Finding

The `KeyError` from `project.get("01_baseline")` does **not** indicate the report is missing. This is a lookup-shape issue:

**`skore.Project.get()` resolves by `id`, not by user-facing `key`.** The string `"01_baseline"` is a user-facing key, not an id.

**Do not re-run the experiment to recreate the artifact.** Re-running writes a duplicate row to the Project, violating the data integrity contract.

## What to do instead

1. **Enumerate the Project to find the report's id:**
   ```python
   df = project.summarize()
   print(df)  # See (key, id) pairs
   ```
   This returns a DataFrame indexed by `id` with a `key` column. Locate the baseline row and its id.

2. **Access the report by its id:**
   ```python
   report = project.get(id_value)  # Use the id from summarize(), not the key
   ```

## Reference

See `python-api` skill § "Stop conditions — read before any lookup":
> `skore.Project.get(...)` is by **id**, not user-facing `key`; enumerate via `project.summarize()` first. A failed `get(key)` does **not** mean the report is missing.
