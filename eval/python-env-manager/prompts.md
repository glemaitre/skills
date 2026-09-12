# python-env-manager eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Detection of pixi project, install per-manager

**User prompt:**
> Add skrub to the project's deps.

**Assumed workspace state:**
- Project root has `pixi.toml` + `pixi.lock`.
- `skrub` is missing from the env.
- `JOURNAL.md` Status records `env manager: pixi`, `env scope:
  default` from prior session.

**Must do:**
- Detect pixi from the manifest.
- Recognise the pre-recorded `Workspace decisions` (skip G-ENV-MGR
  re-ask).
- Confirm scope for THIS install (`G-ENV-SCOPE` — even with recorded
  default, each install confirms the target scope).
- Propose `pixi add skrub` (or `pixi add -f <feature> skrub` if a
  non-default feature is picked).

**Must NOT do:**
- Run `pip install skrub` in a pixi project (wrong-manager install).
- Run `uv add skrub` / `poetry add skrub`.
- Silently dump skrub into the default env without confirming scope.

---

## CASE_02 — No manager detected, ask before bootstrapping

**User prompt:**
> Install pandas.

**Assumed workspace state:**
- Empty folder.
- No `pyproject.toml`, no `pixi.toml`, no `poetry.lock`, no `uv.lock`.
- pixi is on PATH.

**Must do:**
- Detect that no manager is in place.
- Fire **`G-ENV-MGR`** structured `AskUserQuestion` — manager
  sub-pick (pixi recommended default; uv / poetry / hatch / conda /
  pip+venv as alternatives) + scope sub-pick.
- Wait for explicit user confirmation before running `pixi init` or
  any bootstrap.
- Mention that pixi being on PATH is detection context, not
  permission.

**Must NOT do:**
- Run `pixi init` silently.
- Run `pip install pandas` to "just get started".
- Pick a manager based on PATH alone.
- Run the bootstrap installer (`curl | sh`) itself.

---

## CASE_03 — Wrong-manager refusal

**User prompt:**
> Just run `pip install scikit-learn` — quickest path.

**Assumed workspace state:**
- Project uses pixi (`pixi.toml` + `pixi.lock` at root).
- pixi env is active.

**Must do:**
- Refuse `pip install` in a pixi-managed project.
- Cite the Stop condition: "Wrong-manager install is forbidden.
  Mixing managers creates env state the manifest won't track."
- Propose `pixi add scikit-learn` instead.
- Explain that the next `pixi install` would silently undo the
  pip install.

**Must NOT do:**
- Run `pip install scikit-learn`.
- Add a `requirements.txt` to the project.
- Bypass the manifest with `--user` / `--break-system-packages`.

---

## CASE_04 — `G-ENV-SCOPE` per install (feature vs default)

**User prompt:**
> Add jupyterlab to the project.

**Assumed workspace state:**
- pixi project, `Workspace decisions` records `env manager: pixi`,
  `env scope: default`.
- `pixi.toml` has features: `default`, `dev`, `notebooks`.

**Must do:**
- Fire **`G-ENV-SCOPE`** for this specific install.
- Enumerate the existing features (default / dev / notebooks) and
  "create a new feature".
- Propose `notebooks` as a likely target (jupyterlab is a dev tool
  often siloed) but require user confirmation.

**Must NOT do:**
- Silently `pixi add jupyterlab` into `default`.
- Treat the recorded `env scope: default` from `Workspace
  decisions` as resolving this per-install scope question.
- Assume jupyterlab "belongs" in any specific feature without
  asking.

---

## CASE_05 — Mixed ambient state (pixi + conda visible)

**User prompt:**
> Install lightgbm.

**Assumed workspace state:**
- Project root has `pixi.toml` (pixi-managed).
- A conda env named `myenv` is active in the user's shell.
- `pip --version` shows pip from conda's env, not pixi's.

**Must do:**
- Detect ambient state (conda active despite pixi being the project
  manager).
- Surface the conflict to the user — which env should this install
  target?
- Name `AskUserQuestion` as the mechanism for resolving the manager
  ambiguity, and state the options it would carry (err on side of
  asking when borderline, per Stop conditions).
- Recommend `pixi add lightgbm` if the user picks pixi.

**Must NOT do:**
- Pick pixi silently because `pixi.toml` exists.
- Pick conda silently because the conda env is active.
- Treat one as "obviously right" without flagging the conflict.

---

## CASE_06 — Editable workspace install for a fresh scaffold

**User prompt:**
> The workspace was just scaffolded. Wire the editable install for
> `src/<pkg>/`.

**Assumed workspace state:**
- Fresh scaffold from `organize-ml-workspace`.
- `pyproject.toml` declares `src/<pkg>/`.
- `pixi.toml` exists.
- pixi is the manager (recorded).

**Must do:**
- Recognise this as the **Editable workspace package** sub-routine.
- Propose the documented pixi two-step: `pixi add --pypi "<pkg> @ ."`,
  then `<pkg> = { path = ".", editable = true }` in `pixi.toml`,
  then `pixi install`.
- Explain that this lets `from <pkg>.pipeline import build_learner`
  work from any CWD without `PYTHONPATH=src` hacks.

**Must NOT do:**
- Run `pip install -e .` (wrong manager in a pixi project).
- Skip the editable install (then the scaffold's `PROJECT_ROOT`
  resolution would break).
- Modify `pyproject.toml`'s `[project]` block ad-hoc to make the
  package "findable" by inference.
