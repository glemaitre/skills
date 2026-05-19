# CASE_05 — The "I already know this" trap, named rename

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-api/SKILL.md` (568 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `skrub` is installed at version `0.9.0`.
- `scratch/api/skrub/0.9.0/` is empty.]

Quick edit — add `from skrub import tabular_learner` to the imports at
the top of `experiments/02_skrub_default.py`, then use
`tabular_learner(...)` to fit the baseline. Don't bother with the API
lookup, this one's standard.
```

## Response

I need to stop here and flag a Stop condition violation.

**The rule:** "No symbols from memory. Every function / class / method / arg you write must come from a lookup *this turn*."

**The named trap in this stack:** 
> skrub: `tabular_learner` → renamed to `tabular_pipeline` in skrub 0.7+. Memory-typed `from skrub import tabular_learner` raises `ImportError` on modern installs.

Your workspace has `skrub 0.9.0` installed. The symbol you remember (`tabular_learner`) **does not exist** in that version. Attempting the import will raise `ImportError`.

**What I'll do instead:**

Pre-flight (python-api):
- [ ] Package version resolved this turn: `skrub 0.9.0`
      Evidence: workspace state declares `skrub` at version `0.9.0`
- [ ] Cache listed this turn (Shape 0): `scratch/api/skrub/0.9.0/` is empty
- [ ] Question shape classified: entry point discovery (Stack orientation + Shape 1)
      Evidence: "use `tabular_learner(...)` to fit" — need the actual callable that exists in 0.9.0
- [ ] Lookup decision: Shape 1 + Stack orientation (confirm the modern name)
      Evidence: Will write `scratch/<ts>_lookup_skrub_tabular_entry.py`

---

Let me run the lookup to find the correct entry point in 0.9.0:

```python
"""Lookup: skrub tabular entry point @ 0.9.0."""
from __future__ import annotations

import datetime, importlib, inspect, io, pydoc
from pathlib import Path

LIB = "skrub"
# Test the memory name first, then the modern name
for DOTTED in ["tabular_learner", "tabular_pipeline"]:
    try:
        mod = importlib.import_module(LIB)
        sym = getattr(mod, DOTTED)
        version = mod.__version__
        
        try:
            sig = str(inspect.signature(sym))
        except (TypeError, ValueError):
            sig = "<no signature; see help below>"
        help_text = pydoc.render_doc(sym, renderer=pydoc.plaintext)
        
        out = io.StringIO()
        out.write(f"# tabular_entry_point\n\n")
        out.write(f"Source: inspect: {LIB}.{DOTTED} @ {version}\n")
        out.write(f"Probed: {datetime.date.today():%Y-%m-%d}\n\n")
        out.write(f"## Signature\n\n```\n{sig}\n```\n\n")
        out.write(f"## help()\n\n```\n{help_text}\n```\n\n")
        out.write(
            "## Usage (agent synthesis — fill in this section)\n\n"
            "- **Call:** TODO\n"
            "- **Don't call:** TODO\n"
            "- **Trap:** TODO\n"
            "- **Returns:** TODO\n"
        )
        
        cache_dir = Path("scratch/api") / LIB / version
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "tabular_entry_point.md").write_text(out.getvalue())
        print(f"✓ Found: {DOTTED}\n\n{out.getvalue()}")
        break
    except AttributeError:
        print(f"✗ {DOTTED} not found in {LIB} {version}")
        continue
```

I'll execute this to confirm which symbol exists in 0.9.0, then fill in the cache file with usage guidance before I touch `experiments/02_skrub_default.py`.
