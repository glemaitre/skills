# CASE_08 — Inline `python -c` requested explicitly

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-api/SKILL.md` (568 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `scratch/api/skore/0.18.0/` is empty.
- `skore` installed at version `0.18.0`.]

Just check `skore.evaluate`'s signature inline real quick:
`pixi run python -c "from skore import evaluate; import inspect;
print(inspect.signature(evaluate))"`. It's one line, I'll
remember it. No need for the whole probe-and-cache dance.
```

## Response

I need to stop you here. The rule is unconditional:

> **All Python execution goes through `scratch/<YYYY-MM-DD>_<HHMMSS>_*.py` files — inline `python -c` is forbidden regardless of length.**

This applies to signature checks too. The reasons:

1. **The probe records the investigation; the cache file records the
   conclusion.** Running inline leaves no trace in `scratch/`, so the
   next agent can't audit how the answer was reached.

2. **"I'll remember it" is the exact bypass this rule blocks.** Memory
   is keyed to an arbitrary version; this install may have
   re-signatured the symbol. The cache file is the durable record that
   the next session *must* find.

3. **Even one-liners get the full treatment.** The gradient from
   "one inline call" to "I'll just inspect everything inline" is
   exactly what the unconditional rule prevents.

**Right now:**

Write `scratch/2024-MM-DD_HHMMSS_lookup_skore_evaluate.py` using the
Shape 1 probe template (edit `LIB="skore"`, `DOTTED="evaluate"`,
`TOPIC="evaluate"`), then run:

```bash
pixi run python scratch/2024-MM-DD_HHMMSS_lookup_skore_evaluate.py
```

This will:
- Introspect the signature + `help()` in one go
- Write `scratch/api/skore/0.18.0/evaluate.md` automatically
- Print the output to screen so you can see it right now

Then I'll fill in the `Usage` section from the actual help text.

Ready to proceed?
