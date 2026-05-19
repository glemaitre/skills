# CASE_04 — Missing dependency → install, not substitute

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/data-science-python-stack/SKILL.md` (430 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Project uses pixi.
- skore + sklearn already importable; skrub is missing.]

`import skrub` raises `ModuleNotFoundError`. Should I just use
`sklearn.Pipeline` instead?
```

## Response

**No — install `skrub`, do not substitute.**

Per the stack's "Missing dependency" rule: when code in this stack needs a library but `import` fails, the answer is **install it**, not rewrite to a non-stack equivalent. Substituting `sklearn.Pipeline` for `skrub` silently breaks the contract that the data-cleaning + feature-engineering layer depends on — `skrub` wraps custom dataframe operations in a sklearn-compatible computation graph that **replays deterministically** across train and test splits, which `Pipeline` alone doesn't enforce for custom steps.

Here's the install command:

```bash
pixi add skrub
```

Once that completes, `import skrub` will work. If you hit any issues during the add, let me know and we'll debug; otherwise you're ready to proceed with the skrub-based cleaning layer.
