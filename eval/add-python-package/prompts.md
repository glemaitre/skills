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
- Name `python -m skore_skills env detect` / status.
- Name `python -m skore_skills env add skrub` and the printed
  `pixi add skrub`.
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
