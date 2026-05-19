# CASE_07 — `pixi init` shortcut

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder, no manifests yet.]

`pixi` is already on PATH. Just run `pixi init` to get a manifest
going.
```

## Response

I appreciate the direct ask, but I need to pause and invoke the **Stop conditions** here.

You're asking me to run `pixi init`, which would:
1. Create a `pixi.toml` manifest
2. Infer a project `name` from the folder name (via pixi's default)

Both of these bypass the **mandatory gates**:
- **G-PKG-NAME** — the package name for `src/<pkg>/` must be decided via structured `AskUserQuestion`, not inferred from folder name as a side effect of `pixi init`.
- **G-ENV-MGR** — the manager choice (pixi vs. poetry vs. uv) must be confirmed via `python-env-manager`, not assumed because pixi is on PATH.

The forbidden-shortcuts table specifically calls this out:
> `pixi` on PATH → run `pixi init` to get a manifest, then read the name back — **Violates G-ENV-MGR AND G-PKG-NAME**.

---

## What I'll do instead:

**Sibling skills (open just-in-time):**
- data-science-python-stack, python-env-manager, python-api,
  python-code-style, iterate-ml-experiment, build-ml-pipeline,
  evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline

Let me hand off to **`python-env-manager`** first to confirm pixi is the right choice, and to **`data-science-python-stack`** to lock down what's being installed. Then I'll return here with G-ENV-MGR and G-TABULAR passed, and we'll do G-PKG-NAME before any manifest creation.

**Ready to move to those skills, or would you prefer I ask the three gates directly here?**
