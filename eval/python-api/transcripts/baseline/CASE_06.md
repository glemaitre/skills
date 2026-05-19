# CASE_06 — The `project.get` lookup-shape trap

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-api/SKILL.md` (943 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `skore.Project` instance bound to `project`, mode `local`.
- The baseline experiment was run last week; its report is in the
  Project under key `"01_baseline"`.]

`project.get("01_baseline")` is raising `KeyError`. The report must be
missing — let's re-run `experiments/01_baseline.py` to put it back.
```

## Response

**STOP.** This is the "lookup shape is wrong" trap, not a missing artifact. Before re-running the experiment, I need to verify the correct way to retrieve the report from the Project.

## Pre-flight (python-api)

```
Pre-flight (python-api):
- [ ] Package version resolved this turn: skore <version>
- [ ] Cache listed this turn (Shape 0): `ls scratch/api/skore/<version>/`
- [ ] Lookup decision: Shape 1 probe → project_local.md (Project.get / .summarize)
- [ ] Cache file lands on disk before turn end
- [ ] Usage section filled: Call / Don't call / Trap / Returns
```

Let me resolve the version and check the cache.

```bash
pixi run python -c "import skore; print(skore.__version__)"
```

Then:

```bash
ls scratch/api/skore/*/
```

Once I have the version and cache status, I'll either read an existing `project_local.md` or run a Shape 1 probe to understand the correct accessor for `Project.get(...)`. The docs mention that `get` resolves **by id**, not by the user-facing `key` you put the report under — `project.summarize()` is what enumerates the `(key, id)` pairs.

**Do not re-run the experiment yet.** The KeyError is almost certainly telling us the lookup shape is wrong, not that the report is gone. Let me confirm.
