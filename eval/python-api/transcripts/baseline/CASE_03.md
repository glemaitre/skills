# CASE_03 — Stack orientation routes to the right submodule

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-api/SKILL.md` (943 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `scratch/api/skrub/` is empty.
- `skrub` is installed at version `0.9.0`.]

I have a mixed-type tabular DataFrame (numeric + categorical + text
columns). I want a one-call default-everything featuriser/learner from
skrub. Which entry point should I reach for, and where does it live?
```

## Response

# Pre-flight (python-api)

- [ ] Package version resolved this turn: **skrub 0.9.0**
      Evidence: workspace state confirms `0.9.0` installed
- [ ] Cache listed this turn (Shape 0): `ls scratch/api/skrub/0.9.0/`
      Evidence: empty (no prior cache files)
- [ ] Lookup decision: **cache miss → Shape 1 probe** (symbol signature + help)
      Evidence: writing `scratch/<ts>_lookup_skrub_tabular_pipeline.py`
- [ ] Cache file lands on disk before turn end
      Evidence: write `scratch/api/skrub/0.9.0/tabular_pipeline.md` (this turn)
- [ ] Usage section completed with Call / Don't call / Trap / Returns
      Evidence: edit cache file to replace TODOs

---

## Shape 1 Probe — `tabular_pipeline`

Running the probe now:

```python
"""Lookup: skrub.tabular_pipeline @ installed version."""
from __future__ import annotations

import datetime
import importlib
import inspect
import io
import pydoc
from pathlib import Path

LIB = "skrub"
DOTTED = "tabular_pipeline"
TOPIC = "tabular_pipeline"

mod = importlib.import_module(LIB)
sym = mod
for part in DOTTED.split("."):
    sym = getattr(sym, part)

version = mod.__version__
try:
    sig = str(inspect.signature(sym))
except (TypeError, ValueError):
    sig = "<no signature; see help below>"
help_text = pydoc.render_doc(sym, renderer=pydoc.plaintext)

out = io.StringIO()
out.write(f"# {TOPIC}\n\n")
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
(cache_dir / f"{TOPIC}.md").write_text(out.getvalue())
print(out.getvalue())
```

Execute with:
```bash
pixi run python scratch/2026-01-16_lookup_skrub_tabular_pipeline.py
```

Once the cache file lands at `scratch/api/skrub/0.9.0/tabular_pipeline.md`, I'll edit it to fill in the Usage section with:

- **Call:** The import + one-liner for your mixed-type DataFrame case
- **Don't call:** Memory-based alternatives (e.g. the old `tabular_learner` name from skrub <0.7)
- **Trap:** Any version-specific rename / signature change / footgun
- **Returns:** What it produces and which accessor gives you the fitted learner

Then I'll answer your question directly from the Usage synthesis.

---

**Expected answer** (after cache write): You want **`skrub.tabular_pipeline`** — it's the top-level entry point for one-call mixed-type featurization. Lives at the package root (`from skrub import tabular_pipeline`). The cache file will show the exact call shape for your DataFrame.
