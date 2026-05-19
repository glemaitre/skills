# CASE_01 — Standard run-ruff-on-touched-files

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-code-style/SKILL.md` (263 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `src/claim_predictor/pipeline.py` was modified this turn.
- `ruff.toml` exists at project root.
- `pixi run ruff --version` succeeds (ruff is installed).]

I just edited `src/claim_predictor/pipeline.py`. Run the style
pass.
```

## Response

# Pre-flight (python-code-style)

- [x] ruff importable in the project's env (`pixi run ruff --version` succeeds)
- [x] `ruff.toml` present at project root
- [x] File list: `src/claim_predictor/pipeline.py`
- [x] First ruff pass on this file (proceed)
- [x] One-fix-per-file rule acknowledged

---

Running the style pass on `src/claim_predictor/pipeline.py`:

```bash
pixi run ruff format src/claim_predictor/pipeline.py
pixi run ruff check --fix src/claim_predictor/pipeline.py
pixi run ruff check src/claim_predictor/pipeline.py
```

Please share the output and I'll address any remaining diagnostics.
