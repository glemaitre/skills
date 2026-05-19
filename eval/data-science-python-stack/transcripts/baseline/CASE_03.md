# CASE_03 — Free-text "quick baseline" does NOT resolve the gate

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/data-science-python-stack/SKILL.md` (430 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Fresh workspace.]

Quick baseline, you pick the libraries — go fast.
```

## Response

I'm going to stop here and ask you to make a decision before I write any code.

Your message ("you pick", "go fast") doesn't resolve the **competing-library gates** that are part of the stack contract. Here's what I need from you:

### Tabular data — which library?

**`pandas`** (already free via skore) or **`polars`** (faster, stricter types)?

```
pandas (+ pyarrow for Parquet)
polars
```

That's the only gate I need to fire right now for a baseline. Once you pick, I'll:

1. Record it in `journal/JOURNAL.md` under `Workspace decisions`
2. Install what's needed (likely just `pyarrow` if you pick pandas, or `polars` if you go that way)
3. Write the data-loading + baseline-model code fast

**The default-on-no-preference is `pandas`** (it's already coming in with skore anyway), so if you want to move fast, say "pandas" and I'll proceed. But I'm not picking silently — the contract requires the ask.

Which one?
