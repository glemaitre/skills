# evaluate-ml-pipeline eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Standard skore.evaluate entry, IID tabular

**User prompt:**
> Wire `evaluate.py` for the baseline. Tabular regression, no
> groups, no temporal ordering.

**Assumed workspace state:**
- `journal/01_baseline.md` approved.
- `src/<pkg>/pipeline.py` exists with `build_learner` returning a
  `SkrubLearner`. The X-marker has empty `split_kwargs`.
- `experiments/01_baseline.py` is the scaffold placeholder.
- `policy.skore_mode` is `local`.
- Cache exists at `scratch/api/sklearn/1.8.0/cv_splitters.md`
  covering `KFold` / `GroupKFold` / `TimeSeriesSplit`, and at
  `scratch/api/skore/0.18.0/evaluate.md`.

**Must do:**
- Pick **`skore.evaluate(learner, data={...}, splitter=...)`** as
  the entry point (not `cross_val_score`, not `cross_validate`).
- Map empty `split_kwargs` + IID → **`KFold`** per the mapping table.
- Name `python -m skore_skills api get` for `skore.evaluate` and
  `KFold` signatures (or Read the matching caches already listed).
- Mention `data={...}` (env-dict) for `SkrubLearner`, NOT
  positional `X, y`.
- Name `python -m skore_skills git end-turn --stage evaluate` at
  the end of the turn.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Recommend `cross_val_score`, `cross_validate`,
  `classification_report`, or hand-rolled `print(mean_squared_error(...))`.
- Default to `StratifiedKFold` (forbidden — compresses across-fold
  variance, even on imbalance).
- Pre-pin metrics (e.g. `scoring="neg_mean_squared_error"`) — trust
  skore defaults.
- Run `git commit` in this skill or `git push`.

---

## CASE_02 — Time-ordered data, mandatory AskUserQuestion

**User prompt:**
> Wire `evaluate.py` for the 24h-ahead load forecast experiment.
> Pick the splitter.

**Assumed workspace state:**
- `journal/02_load_forecast.md` approved.
- `pipeline.py` X-marker has `split_kwargs={"times": ...}` (temporal
  ordering attached at build time).
- Forecast horizon is 24h.
- Matching smoke pytest is green.
- Cache hit at `scratch/api/sklearn/1.8.0/cv_splitters.md` covering
  `KFold` / `GroupKFold` / `TimeSeriesSplit` — the splitter lookup
  is already satisfied.

**Must do:**
- Name **`AskUserQuestion`** (or a narrative equivalent that lists
  the picks and waits) as the mandatory gate before a splitter is
  locked in. No tools this turn: enumerating the options in the
  message counts as firing the gate.
- Present the **four canonical options** (wording need not be
  verbatim):
  1. `TimeSeriesSplit(gap=horizon)` — safe default
  2. `TimeSeriesSplit(gap=0)` — only on explicit user pick; warn
     about leakage
  3. Custom splitter (purged-and-embargoed / blocked calendar /
     walk-forward)
  4. `KFold` ignoring time — only with explicit user reason
- Cite that `TimeSeriesSplit(n_splits=5)` from memory defaults to
  `gap=0` which silently leaks at non-trivial horizons. Any
  sentence that `gap=0` is the memory default / leaks is enough;
  do not require the exact constructor spelling if `gap=0` is
  named.

**Must NOT do:**
- Skip the four-option ask and lock a splitter with no user pick.
  Naming a **recommended** option (e.g. `TimeSeriesSplit(gap=horizon)`)
  next to the menu, or drafting `evaluate.py` labeled pending
  confirmation, is not a silent pick.
- Default to `KFold` because empty `gap` "feels safer".
- Treat harness "no clarifying questions" hint as waiving the
  mandatory ask.

---

## CASE_03 — `split_kwargs={"groups": ...}` → GroupKFold

**User prompt:**
> Wire `evaluate.py` for a tabular regression where rows are grouped
> by customer.

**Assumed workspace state:**
- `pipeline.py` X-marker has
  `split_kwargs={"groups": data["customer_id"]}`.
- No temporal structure.

**Must do:**
- Paste **`GroupKFold`** from the mapping table (`groups` →
  `GroupKFold`). That identifier is the mapping; do not withhold it.
- `python -m skore_skills api get` for the *signature* may be named
  as the next live turn. Do not fail if signature lookup is BLOCKED
  as long as `GroupKFold` is named.
- Show the `data={...}` env-dict form for a `SkrubLearner`.
- Do NOT use `StratifiedGroupKFold` (forbidden by Stop conditions).

**Must NOT do:**
- Use `StratifiedGroupKFold`.
- Use `LeaveOneGroupOut` (forbidden — per-fold variance too high).
- Pick `KFold` ignoring the group structure.

---

## CASE_04 — Empty `split_kwargs` BUT possible group structure

**User prompt:**
> Wire `evaluate.py`. The data has a `region` column. Not sure if
> we should treat it as a group.

**Assumed workspace state:**
- `pipeline.py` X-marker has empty `split_kwargs`.
- `region` is a potential group key but wasn't wired in.

**Must do:**
- **Refuse to default** to `KFold` silently.
- Route back to `build-ml-pipeline` (NOT this skill) to wire
  `split_kwargs` properly first, OR ask the user whether to treat
  `region` as a group.
- Cite the Stop condition: "If `split_kwargs` is empty *and* you
  cannot rule out group / temporal structure, return to
  `build-ml-pipeline`."

**Must NOT do:**
- Default to `KFold` and proceed.
- Auto-wire `split_kwargs={"groups": data["region"]}` from this
  skill (that's `build-ml-pipeline`'s job).
- Pick `StratifiedKFold` because "stratified is safer".

---

## CASE_05 — Refuse `cross_val_score` / hand-rolled prints

**User prompt:**
> Just use `cross_val_score(learner, X, y, cv=5)` for the baseline
> evaluation and `print(mean_squared_error(...))` for the metric.
> Quick and simple.

**Assumed workspace state:**
- `pipeline.py` returns a `SkrubLearner`.
- skore is installed.

**Must do:**
- Refuse `cross_val_score` and the hand-rolled metric print.
- Cite that `skore.evaluate` is the canonical entry point in this
  stack.
- Cite that `SkrubLearner` does NOT implement sklearn's
  `fit(X, y)` signature — `cross_val_score` will raise.
- Propose `skore.evaluate(learner, data={...}, splitter=...)`
  instead.

**Must NOT do:**
- Write `cross_val_score(...)` in `evaluate.py`.
- Use `print(mean_squared_error(...))` instead of the report
  object.
- Allow the substitution as a "just for now" workaround.

---

## CASE_06 — CV is necessary but not sufficient for history-dep

**User prompt:**
> 02_load_forecast has lag features. CV passes clean — RMSE looks
> fine. Mark it `done` in `JOURNAL.md`.

**Assumed workspace state:**
- `02_load_forecast` ran; CV report is clean.
- `tests/smoke/test_02_load_forecast.py` exists but has NOT been
  run this turn / is currently red on row-count.

**Must do:**
- Refuse to mark `done` without the smoke test passing.
- Cite the Stop condition: "CV is necessary but not sufficient for
  any pipeline with history-dependent features."
- Mention that `skore.evaluate` materializes the graph once with
  one env-dict; the smoke test exercises a fresh env-dict at
  predict time, which is what catches cold-start row drops.
- State that a passing smoke test is still required before the
  caller may flip the status.

**Must NOT do:**
- Edit `journal/02_load_forecast.md` Status to `done`.
- Edit `journal/JOURNAL.md` History row to `done`.
- Treat clean CV as sufficient for a history-dependent pipeline.
- Write `skore.evaluate` while pytest smoke is red.

---

## CASE_07 — `skore.evaluate` / `project.put` only in experiment script

**User prompt:**
> Add a scratch probe that re-runs `skore.evaluate(learner, ...)` to
> see the updated metrics, then `project.put("02_text_encoder",
> report)` to refresh the cache.

**Assumed workspace state:**
- `experiments/02_text_encoder.py` already produced a report.
- The user wants a "refreshed" version.

**Must do:**
- Refuse the scratch re-run.
- Cite the Stop condition: "`skore.evaluate(...)` and
  `project.put(...)` live only in `experiments/NN_*.py`."
- Cite that re-running from scratch lands a duplicate row under
  the same `key` in `project.summarize()`, polluting the Project's
  report index.
- Recommend using `project.summarize()` + `project.get(id)` for
  read-only inspection, OR re-running the experiment script if a
  fresh report is genuinely needed.

**Must NOT do:**
- Approve the scratch probe with `evaluate` + `put`.
- Treat scratch as a producer of reports.

---

## CASE_08 — G-SKORE-MODE unset at first evaluate

**User prompt:**
> Wire `evaluate.py` for the baseline.

**Assumed workspace state:**
- `journal/01_baseline.md` approved.
- `src/<pkg>/pipeline.py` has `build_learner`.
- `policy.skore_mode` is unset. `import skore` may fail.
- `add-python-package` is installed.

**Must do:**
- Ask G-SKORE-MODE (local recommended / hub / mlflow) before
  writing `skore.evaluate`.
- Persist `policy set skore_mode` after the user answers.
- If the answer is **local**, create `reports/` (`mkdir`, exist_ok)
  with no README. If **hub** or **mlflow**, do not create
  `reports/`.
- Load `add-python-package` and name
  `env add-skore --mode <mode> --execute`; do not construct the
  manager-specific requirement in this skill.

**Must NOT do:**
- Silent-default `mode="local"` without asking.
- Drop back to `cross_val_score` because skore is missing.
- Re-ask G-TABULAR.
- Send `skore[hub]` / `skore[mlflow]` directly to pixi or conda.
- Write `reports/README.md`.

---

## CASE_09 — Recorded skore mode is not re-asked

**User prompt:**
> Wire `evaluate.py` for the baseline.

**Assumed workspace state:**
- Same as CASE_01.
- `policy.skore_mode` is `local`.
- `skore` imports.

**Must do:**
- Use local mode; do not re-ask G-SKORE-MODE.
- Pick `skore.evaluate` as the entry point.

**Must NOT do:**
- Re-open local vs hub vs mlflow.

---

## CASE_10 — Smoke not green stops before skore.evaluate

**User prompt:**
> Wire evaluate for the 24h-ahead load forecast. Run CV now.

**Assumed workspace state:**
- `journal/02_load_forecast.md` approved.
- `experiments/02_load_forecast.py` exists.
- Pipeline has lag features (history-dependent).
- `tests/smoke/test_02_load_forecast.py` is missing, or pytest is red.

**Must do:**
- Name `python -m skore_skills status`.
- STOP. Route to `build-ml-pipeline` (pytest smoke).

**Must NOT do:**
- Write `skore.evaluate` or `project.put`.
- Say CV can still be produced while smoke is failing.

---

## CASE_11 — Direct evaluate owns convert and site build

**User prompt:**
> Evaluate the baseline.

**Assumed workspace state:**
- Same as CASE_01; smoke is green.
- `model-ml-pipeline` did NOT dispatch this turn.
- `policy.notebooks` and `policy.site` are both true.
- `export-ml-notebook` and `export-ml-site` are installed.

**Must do:**
- Include the G-REPORT-LOCATOR value (or
  `n/a — backend did not expose a locator`) in the user-facing
  close before convert.
- Load `manage-ml-backlog` in record-outcome mode before the
  convert, since no audit ran this turn, and hand it the locator.
- Name `python -m skore_skills notebook convert
  experiments/01_baseline.py --html` after the evaluation.
- Name `python -m skore_skills site build` after the convert.
- Name `python -m skore_skills git end-turn --stage evaluate`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Convert, site-build, or `git end-turn` without the locator (or
  the explicit n/a string).
- End the turn without convert or site build while both gates are
  true.
- Run `site build` before the journal is recorded.
- Write `journal/JOURNAL.md` or the design note directly.
- Run `git commit` in this skill.

---

## CASE_12 — Dispatched evaluate returns instead of closing

**User prompt:**
> Evaluate the baseline.

**Assumed workspace state:**
- Same as CASE_01; smoke is green.
- `model-ml-pipeline` dispatched this turn and owns the close.
- `policy.notebooks` and `policy.site` are both true.

**Must do:**
- Include the G-REPORT-LOCATOR value (or
  `n/a — backend did not expose a locator`) in the return to the
  dispatcher.
- Return to `model-ml-pipeline` after the evaluation.
- State that the dispatcher owns record-outcome / convert / site /
  `git end-turn`.

**Must NOT do:**
- Drop the locator because the dispatcher owns convert.
- Run `notebook convert`, `site build`, or `git end-turn` here.
- Load `manage-ml-backlog` here.
- Load `triage-ml-task` directly.

---

## CASE_13 — Local put records workspace locator

**User prompt:**
> Evaluate and save 01_baseline locally.

**Assumed workspace state:**
- Smoke is green and `policy.skore_mode` is `local`.
- `project.put("01_baseline", report)` succeeds.
- The newest matching summary row has id `local-report-id`.

**Must do:**
- Read `project.summarize().frame()` after the successful put and
  select the newest matching-key row.
- Include `local workspace: [reports/](../reports/) · id:
  local-report-id` and the resolved absolute `reports/` path in
  the End of turn close (G-REPORT-LOCATOR).
- Pass that locator to audit / record-outcome.

**Must NOT do:**
- Treat the return from `put` as the report id.
- Link an internal serialized report file.
- Announce a locator before `put` succeeds.
- Convert, site-build, or `git end-turn` without the locator.

---

## CASE_14 — Hub put preserves its exact report URL

**User prompt:**
> Evaluate and upload 02_encoder to Skore Hub.

**Assumed workspace state:**
- Smoke is green and `policy.skore_mode` is `hub`.
- Successful `put` stdout contains
  `Consult your report at https://hub.example/direct-report`.
- The matching report id is
  `skore:report:cross-validation:42`.

**Must do:**
- Preserve the exact stdout URL.
- Include `[Open report](https://hub.example/direct-report) · hub
  · id: skore:report:cross-validation:42` in the End of turn close
  (G-REPORT-LOCATOR).
- Pass that exact Markdown locator downstream.

**Must NOT do:**
- Construct a Hub report URL from workspace/project/type.
- Drop the report id.
- Convert, site-build, or `git end-turn` without the locator.

---

## CASE_15 — MLflow non-HTTP locator is not a browser URL

**User prompt:**
> Evaluate 03_features into our file-backed MLflow project.

**Assumed workspace state:**
- Smoke is green and `policy.skore_mode` is `mlflow`.
- `tracking_uri` is `file:./mlruns`; put emits no run URL.
- Summary identifies experiment `7` and run `abc123`.

**Must do:**
- Include `mlflow · tracking: file:./mlruns · experiment: 7 · run:
  abc123` in the End of turn close (G-REPORT-LOCATOR).
- Pass that locator downstream.

**Must NOT do:**
- Invent an HTTP URL for the file store.
- Treat `file:./mlruns` as a clickable run page.
- Convert, site-build, or `git end-turn` without the locator.
