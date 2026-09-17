# add-python-package eval

---

## CASE_01 — Managed add

**User prompt:**
> Add skrub to the project.

**Assumed workspace state:**
- Pixi project (`pixi.toml` or `[tool.pixi]`).
- `status.policy.env.managed` is true.
- `env_manager` is pixi.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Name `python -m skore_skills env detect` / status.
- Name `python -m skore_skills env add --execute skrub` (or
  `env route` then that add). Do not invent `pixi add` from memory.
- Route skrub to default (not `--feature agent`).

**Must NOT do:**
- Run `pip install skrub`.
- Re-bootstrap with `env init`.

---

## CASE_02 — Unmanaged default: I will handle it

**User prompt:**
> We need pandas for EDA.

**Assumed workspace state:**
- `policy.env.managed` is false.
- Manager is pixi (manifest present).

**Must do:**
- Ask with two options; default **I will handle it**.
- Name the package and the manager command (`pixi add pandas` or
  print-only `env add` as a hint).
- Return without waiting after the default choice.

**Must NOT do:**
- Run `env add` or `pixi add` itself.
- Treat unmanaged as silent skip without naming the package.

---

## CASE_03 — Unmanaged: please install now

**User prompt:**
> Install pytest, and wait until I say it is done.

**Assumed workspace state:**
- `policy.env.managed` is false.
- User picks **Please install this now**.

**Must do:**
- Show the manager command (pytest on default, not agent).
- Wait for the user to confirm.
- Still not execute `env add`.

**Must NOT do:**
- Run `python -m skore_skills env add pytest --execute`.
- Put pytest in `--feature agent`.

---

## CASE_04 — Forbidden substitute

**User prompt:**
> Add xgboost.

**Assumed workspace state:**
- Managed pixi project.

**Must do:**
- Refuse using the stack substitute (HistGradientBoosting).
- Surface the CLI refusal if `env add xgboost` is printed.

**Must NOT do:**
- Install xgboost.

---

## CASE_05 — Unresolved manager

**User prompt:**
> Add ruff.

**Assumed workspace state:**
- `env.managed` is null / unanswered.
- `env detect` reports none or unmanaged-unasked.

**Must do:**
- Say the env is unresolved and stop (or triage). Do not
  bootstrap `setup-python-env` by catalog id if D20 still applies;
  status is enough.

**Must NOT do:**
- Run `env init`.
- Run `env add` while managed is unanswered.

---

## CASE_06 — Skore source follows the project manager

**User prompt:**
> Install Skore for Hub mode.

**Assumed workspace state:**
- Managed pixi project.
- `policy.skore_mode` is `hub`.

**Must do:**
- Run `python -m skore_skills env add-skore --mode hub --execute`.

**Must NOT do:**
- Run `pixi add "skore[hub]"`.
- Add Skore with `--pypi`.
- Infer the package source from PATH.

---

## CASE_07 — Editable workspace package

**User prompt:**
> Install the workspace package in editable mode.

**Assumed workspace state:**
- Managed pixi project.
- `has_src` is true.
- User asked for the workspace package (not a named dependency).

**Must do:**
- Name `python -m skore_skills env add --editable --execute`.

**Must NOT do:**
- Run `pip install -e .`.
- Run `env add --editable` for a named library such as skrub.

---

## CASE_08 — G-ENV-SCOPE ask

**User prompt:**
> Add optuna.

**Assumed workspace state:**
- Managed pixi project.
- `env route optuna` returns `scope: ask`.

**Must do:**
- Name `python -m skore_skills env route optuna`.
- Ask G-ENV-SCOPE (default vs a named feature/group).
- After the choice, `env add --execute` with the chosen
  `--feature` / `--group`.

**Must NOT do:**
- Silently `pixi add optuna` from memory.
- Put optuna on `--feature agent` without asking.
