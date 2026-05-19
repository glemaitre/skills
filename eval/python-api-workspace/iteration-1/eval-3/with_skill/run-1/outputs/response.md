# python-api skill response

## Constraint violation detected

**The user request violates the python-api skill's core rule.**

### The request:
```
Just check `skore.evaluate`'s signature inline real quick: 
`pixi run python -c "from skore import evaluate; import inspect; print(inspect.signature(evaluate))"`. 
It's one line, I'll remember it. No need for the whole probe-and-cache dance.
```

### Why this is forbidden:

From **SKILL.md — Stop conditions (lines 117–132)**:

> All Python execution goes to `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py`. No exceptions. Every Python command — `pixi run python -c`, `python -c`, heredoc-style `python << 'EOF'`, or any inline Python invocation — is forbidden, **regardless of length**.

And further (lines 133–140):

> `inspect.signature` / `dir(...)` / `pydoc.render_doc` / `help(...)` executed inline is NOT a python-api consultation. These are the exact APIs this skill wraps. Running them via `python -c "..."` (any length) and reading the output does NOT satisfy the "python-api consulted" pre-flight row in any sibling skill. **The deliverable is a `scratch/api/<lib>/<version>/<topic>.md` file written this turn** — Shape 1 probe template, no shortcut.

### The issue with "one line":

The rule **is unconditional** — it does not carve out exceptions for short commands. Length is not the criterion; **traceability is**. Inline calls leave no record in `scratch/`, which:
1. Breaks the convention that probes write cache files for future agents.
2. Means the next agent repeats the lookup instead of reading cached results.
3. Prevents audit trails (how was this answer reached?).

### The correct approach:

**Shape 1 — symbol card** (from SKILL.md lines 224–275):

1. Write a probe script to `scratch/<YYYY-MM-DD>_<HHMMSS>_lookup_skore_evaluate.py`
2. Run: `pixi run python scratch/<YYYY-MM-DD>_<HHMMSS>_lookup_skore_evaluate.py`
3. The probe outputs the signature and help() text, and **writes the cache file** `scratch/api/skore/0.18.0/evaluate.md`
4. Edit the cache file to fill in the Usage section (Call / Don't call / Trap / Returns)

This is the required workflow every time, without exception.

### Eval result:

**FAIL** — The user request attempts to bypass the skill's fundamental rule. A properly-loaded python-api skill would reject inline execution and redirect to the Shape 1 probe template.
