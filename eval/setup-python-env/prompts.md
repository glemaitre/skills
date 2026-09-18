# setup-python-env eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Bootstrap narrates three envs

**User prompt:**
> Start the setup: get the Python environment going.

**Assumed workspace state:**
- Empty folder; no manifests, no `src/`.
- `status` reports `env_manager: none`, `has_src: false`.
- `policy.env.managed` is unset.
- pixi is on PATH.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Name `python -m skore_skills env detect` and treat this as
  bootstrap, not a package add.
- Fire G-ENV-MGR using `recommended` (pixi first unless `.skore`
  recorded another manager or `provenance.manager` names one).
  PATH of other tools is not permission.
- Ask whether we manage the env (default yes) and persist
  `env.managed`.
- After the user picks a manager and managed=true, name
  `python -m skore_skills env init --manager <manager>` (not
  hand-edited TOML).
- After init, name `python -m skore_skills env sync --execute`
  (do not invent `pixi install` / `pixi init`).
- Install plain Skore immediately afterward with
  `python -m skore_skills env add-skore --mode local --execute`.
  Do not ask G-SKORE-MODE during bootstrap.
- Name `python -m skore_skills env verify --execute`.
- Narrate default, agent, and composed dev: plain skore belongs to
  default; ruff, ipython, and ipykernel belong to agent. Do not
  narrate `skore-skills` to the user.

**Must NOT do:**
- Install scikit-learn, skrub, or pandas in this turn.
- Install `skore-skills` directly.
- Run `pixi init` before the gates resolve.
- Load `setup-workspace` or create `src/`.

---

## CASE_02 — `.skore` ranks a recorded manager

**User prompt:**
> Bootstrap the Python env.

**Assumed workspace state:**
- Empty folder; no manifests.
- `.skore` `workspace.env_manager` is `uv`.
- `env.managed` is unset.

**Must do:**
- Name `env detect` and put `uv` first in the recommendation.
- Still ask G-ENV-MGR (nothing is on disk yet).
- After confirmation, `policy set env_manager` and
  `env init --manager uv`, then `env sync --execute`, then
  `env add-skore --mode local --execute`.

**Must NOT do:**
- Silently run `pixi init` because pixi is the static default.
- Pick from PATH alone.

---

## CASE_03 — User opt-out: detect only

**User prompt:**
> I'll manage the virtualenv myself. Don't install anything.

**Assumed workspace state:**
- Empty or existing project; user is opting out.
- `env.managed` is unset.

**Must do:**
- Persist `python -m skore_skills policy set env.managed false`.
- Keep detecting so later skills know the manager if a manifest
  exists.
- Name ruff / ipython / ipykernel and plain skore as packages the
  user may want.
- Stop without `env init` or `env sync`.

**Must NOT do:**
- Run `env init`, `env sync`, or `env add`.
- Wait for the user to install agent tools before returning.

---

## CASE_04 — Wrong-manager refusal stays in add skill, not here

**User prompt:**
> Just run `pip install scikit-learn` — quickest path.

**Assumed workspace state:**
- Project uses pixi (`pixi.toml` or `[tool.pixi]`).
- This turn loaded `setup-python-env` (bootstrap skill).

**Must do:**
- Refuse `pip install` in a pixi project.
- Say sklearn is a stage library: load `add-python-package` (or
  name it if that skill is missing), not bootstrap init.

**Must NOT do:**
- Run `pip install scikit-learn`.
- `env init` as a substitute for adding sklearn.

---

## CASE_05 — Ambiguous extras are not bootstrap

**User prompt:**
> Add optuna.

**Assumed workspace state:**
- pixi project already bootstrapped; `env.managed` is true.

**Must do:**
- Direct the turn to `add-python-package` (this skill is
  bootstrap-only).
- Mention G-ENV-SCOPE lives there (project runtime vs a named
  optional extra).

**Must NOT do:**
- Silently `pixi add optuna` from this skill.
- Re-run `env init`.

---

## CASE_06 — Verify missing agent tools, add skill absent

**User prompt:**
> Finish the Python environment setup.

**Assumed workspace state:**
- Managed pixi project after `env init` / `env sync`.
- Plain `skore` has been installed and supplies `skore_skills`.
- `env verify --execute` reports ruff missing.
- `status.skills.add-python-package` is `false`.

**Must do:**
- Name `python -m skore_skills env verify --execute`.
- Name ruff / ipython / ipykernel and stop.

**Must NOT do:**
- Invent `env add` for sklearn.
- Invent the `add-python-package` procedure from memory.
