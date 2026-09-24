---
name: evaluate-ml-pipeline
description: >
  Methodology for evaluating a single sklearn-compatible learner (in
  particular, the `SkrubLearner` produced by `build-ml-pipeline`).
  Owns: which entry point to call (`skore.evaluate` first, the
  explicit report classes when needed), which cross-validator to pick
  from scikit-learn's catalogue, how to consume the structural
  metadata (`groups`, `times`, …) attached at build time via
  `.skb.mark_as_X(split_kwargs=...)`. Writes `skore.evaluate` and
  the persisted-report locator. When `model-ml-pipeline` dispatched
  this turn, return after the locator — the dispatcher owns
  `loop artifacts`, audit, record-outcome, convert, site, and git.
  Standalone also owns that evaluate-stage close. Defaults
  (metrics, plots, SKD checks) come from skore; only override
  metrics or add custom checks on explicit user request.

  TRIGGER when: code calls `cross_val_score`, `cross_validate`,
  `classification_report`, or any handwritten metric print
  (`print(mean_squared_error(...))`); code calls
  `.skb.cross_validate(...)` (route through skore for richer output);
  user asks how to score, evaluate, or compare a single learner;
  user asks how to pick a cross-validator; user asks to run
  evaluation / CV / metrics on a learner. Narrative reads of an
  already-persisted report belong to `audit-ml-pipeline`.

  STOP when `python -m skore_skills status` shows no scaffold
  (`has_src` and `has_journal` both false), no declared learner,
  no approved design, or smoke not green: explain the missing
  prerequisite and send the user to setup/triage or
  `build-ml-pipeline` (it owns pytest smoke). Do not require
  `git`. Do not write `skore.evaluate` while smoke is red or
  missing on a history-dependent pipeline. Also stop for
  hyperparameter search, final-model serving, or multi-run
  tracking. Do not require another action skill to be installed.

  HOW TO USE: invoke before any evaluation call. **First, resolve
  G-SKORE-MODE** (`status.policy.skore_mode`; ask local/hub/mlflow
  if unset, persist, then `add-python-package` for the matching
  skore extra). **Read the "Stop conditions" block and emit the
  Pre-flight checklist as visible text** before any evaluation
  code is written. Confirm all symbols with
  `python -m skore_skills api get`; don't guess names from memory.
---

# Evaluate ML Pipeline

Pick the entry point, pick the cross-validator, route the metadata,
read the report. The pipeline declaration is out of scope (see
`build-ml-pipeline`).

## Stop conditions — read before anything else

- **Workspace not scaffolded.** Run `python -m skore_skills status`
  first. If `has_src` and `has_journal` are both false, STOP and
  send the user to `setup-ml-project` / triage. Do not require
  `git`.
- **Smoke not green is a STOP.** For a pipeline with a backward
  shift, lag, rolling window, target shift, or join with side
  history: if `tests/smoke/test_NN_<short_name>.py` is missing, or
  pytest is red / not run, STOP. Do **not** write `skore.evaluate`.
  Do not include `skore.evaluate` / `project.put` in later-turn
  example fences. Route to `build-ml-pipeline` (it loads smoke and
  runs pytest).
  Documented n/a only when there is no history-dependent step.
  Direct "evaluate" requests use this same gate.
- **G-SKORE-MODE before `skore.evaluate`.** Read
  `status.policy.skore_mode`. If unset: ask local (recommended) /
  hub / mlflow. Persist `python -m skore_skills policy set
  skore_mode <mode>`. Keep a recorded mode. If the user asks to
  switch destination or migrate reports, load `sync-ml-reports`
  only if `status.skills.sync-ml-reports` is true; else one-line
  skip. Do not invent that skill's steps. If the mode is **local**
  (just persisted or already recorded), `mkdir reports` (`exist_ok`);
  do not write `reports/README.md`. If **hub** or **mlflow**, do not
  create `reports/`. Then load `add-python-package` only if
  `status.skills.add-python-package` is true, which runs
  `python -m skore_skills env add-skore --mode <mode> --execute`
  (conda-forge for pixi/conda, PyPI for other managers). Confirm
  the add; do not spell `skore[...]` in this skill. If that skill
  is not installed, name Skore for the recorded mode and stop. Do
  not invent that skill's steps. Do not run `env add` here. See
  `evaluate-ml-pipeline/references/g_skore_mode.md` and
  `add-python-package/references/skore_variant.md`.
  If mode is already recorded, do not re-ask.
- **Missing dependency.** If `import skore` raises in this project's
  env, STOP. Fire G-SKORE-MODE first if `policy.skore_mode` is
  unset, then load `add-python-package` only if
  `status.skills.add-python-package` is true. If it is not
  installed, name the package and stop. Surface the manager
  install line from that skill (or “install Skore with pixi/uv”),
  not the wrapper. Wait for confirmation if the env is unmanaged.
  **Do not drop back to `cross_val_score`, `cross_validate`,
  `classification_report`, or hand-rolled metric prints** — that
  silently rewrites this skill out of the project. See
  `choose-python-library` / `skore_skills/data/python-stack.json`
  for missing-dependency policy.
- **Symbol from memory is forbidden.** Any new `skore` entry point
  or sklearn splitter signature must come from
  `python -m skore_skills api get <dotted>` or a matching cache
  read **in this turn**.
  "I remember `KFold(n_splits=5)`" is not acceptable.
- **The rule-3 table is not a substitute for the lookup.** The
  mapping table below tells you *which* splitter the data calls
  for; `python -m skore_skills api get` tells you what it is called and how it is
  signed in the installed version. Naming `KFold(5)` because the
  table says so, with the lookup deferred, is the same violation as
  naming it from memory.
- **A hedge does not license the content.** "No tools this turn",
  "the live turn MUST run the lookup", a `[~]` box — none of these
  make an unconfirmed splitter safe to write. If the lookup cannot
  run, the box stays `[ ]` for the *signature*. Mapping-table
  identifiers (`groups` → `GroupKFold`) are already in this skill
  — paste `GroupKFold` anyway. Do not BLOCKED the identifier.
  The turn still ends with a single line for the signature probe:
  `BLOCKED: GroupKFold signature needs a API CLI lookup that
  cannot run this turn (<why>).`
- **`BLOCKED` is scoped to the lookup, not to the whole turn.** It
  withholds the splitter *name*; it does not excuse the rest of the
  work. The mandatory user gate still gets presented with its
  options spelled out, and the leakage reasoning still gets written.
  Propose a `skore.evaluate(...)` call fence **only after** consent
  is Evaluate or `evaluate consent` returned `proceed`. Naming
  `skore.evaluate` in a STOP sentence is fine. Blocking on one
  unresolvable fact and then declining everything else is a refusal
  wearing the banner of a safeguard. A cache hit for the symbol is a
  satisfied lookup, not a block.
- **First evaluation still needs the post-smoke HITL
  (`evaluate consent`).** Before G-CV-SPLITTER or any
  `skore.evaluate(...)` fence, run
  `python -m skore_skills evaluate consent --stem <stem>`. Treat
  JSON `action` as authoritative.
  - `ask` — no persisted report for this stem. Present
    **Evaluate (Recommended) / Modify / Stop** and **stop**. Do
    not write `skore.evaluate(...)`. "Run evaluation" / "evaluate
    it" is not consent on a first run. If this turn's user answer
    was already **Evaluate** from `build-ml-pipeline`'s post-smoke
    menu, do not re-prompt; continue to G-CV-SPLITTER / write.
  - `proceed` — History or the design note already has a real
    G-REPORT-LOCATOR. This is a **re-evaluation**; skip the
    post-smoke HITL, then G-CV-SPLITTER / `api get` / write.
  - `stop` — `tests/smoke/test_<stem>.py` is missing. Do not
    evaluate. Route to `build-ml-pipeline` (it loads smoke).
- **Splitter choice is data-driven, not default-driven
  (`G-CV-SPLITTER`).** This is the **G-CV-SPLITTER** gate — owned by
  this skill, fired **after** green pytest smoke and Evaluate
  consent (`evaluate consent` `action` is `proceed`, or the user
  answered **Evaluate** on `ask`), **after** the design note
  has passed `model-ml-pipeline`'s explicit approval gate, before
  evaluation is written into
  `experiments/NN_*.py`. The splitter
  is NOT pre-committed in the design note. Pick from the
  `split_kwargs` content at the X marker **and** time from EDA /
  the journal via the table in rule 3 — never reach for `KFold(5)`
  or `StratifiedKFold` out of habit. Empty `split_kwargs` plus
  possible **groups** → return to `build-ml-pipeline`. Empty
  `split_kwargs` plus **time** in the EDA/journal → fire the
  time-ordered AskUserQuestion (Pattern A if they pick
  `TimeSeriesSplit`); do not attach `times=` on `mark_as_X`.
  Wiring the chosen splitter is Pattern A or B
  (`references/metadata-routing.md`), not "always `splitter=`".
- **No `Stratified*` for class imbalance.** It compresses across-fold
  variance and produces over-confident error bars. Imbalance does
  not change the splitter choice.
- **CV is necessary but not sufficient for any pipeline with
  history-dependent features.** `skore.evaluate(...)` materializes
  the graph **once** with one env-dict and splits *indices* — it
  never exercises a different env-dict at predict time, which is
  exactly the binding shape production faces. A pipeline that
  loads-then-features-then-splits passes CV trivially and still
  silently drops cold-start rows when handed a fresh
  `learner.predict(env₂)`. The structural check that catches this
  is the smoke test owned by `smoke-test-ml-pipeline` (loaded
  from `build-ml-pipeline`, **run with**
  `python -m skore_skills smoke run --stem <stem>`) — required
  before CV for any pipeline that has a backward shift, lag,
  rolling window, target shift, or join with side history. If
  `smoke run` JSON is `stop` or the smoke file is missing for such a
  pipeline, STOP (see the smoke-not-green Stop condition).
  Do not produce a CV report "anyway".
- **All Python execution goes to `scratch/`.** Every Python
  command — version checks, signature lookups, walking the skore
  report's metrics accessors, extracting per-fold values,
  sanity-checking the splitter's fold geometry, multi-symbol
  `inspect.signature(...)` on skore / sklearn classes — lands in
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and runs with the
  composed-dev Python command reported by
  `python -m skore_skills env verify`. **Inline composed-dev
  `python -c "..."` is forbidden regardless of length**
  (see `python -m skore_skills api get` § Stop conditions). The previous "2-line
  inline cap" is removed.
- **Don't filter warnings.** No `warnings.filterwarnings(...)`
  around `skore.evaluate(...)` or the CV splitter unless the user
  explicitly asks. See `python -m skore_skills style` § Stop conditions.
- **Save a report snapshot under `scratch/results/<stem>/`.** In
  `experiments/NN_*.py`, after the bare `report` display and any
  requested `metrics.add` / `checks.add`, write
  `report._repr_html_()` to `scratch/results/<stem>/report.html`
  and `repr(report)` to `scratch/results/<stem>/report.txt` using
  `PROJECT_ROOT`. After forming G-REPORT-LOCATOR, write that exact
  string to `scratch/results/<stem>/locator.txt`. Confirm `_repr_html_` with
  `python -m skore_skills api get`. This is display output only —
  never `evaluate` or `put` from scratch. The `.html` is what site
  build embeds under the design note's Results section. The `.txt`
  exists because a script has no cell digest: it is what
  `manage-ml-backlog` summarizes when the audit is skipped. Never
  summarize by parsing the HTML.
- **Overwrite the Method pipeline snapshot from the fitted report.**
  After the report exists, write `scratch/results/<stem>/pipeline.html`
  from `sklearn.utils.estimator_html_repr` of a **fitted** estimator
  (confirm with `api get`). `EstimatorReport`: `report.estimator_`.
  `CrossValidationReport`: `report.reports_[0].estimator_` — not
  `report.estimator`, which is the original unfitted clone. Do not
  call `SkrubLearner.report` / `full_report` for this overwrite.
- **`skore.evaluate(...)` and `project.put(...)` live only in
  `experiments/NN_*.py`.** The experiment script is the sole
  producer of a report in the workspace's skore Project.
  Re-running `evaluate` from a `scratch/` probe, an `audit/` file,
  a notebook, or a one-off Python file in `src/` duplicates the
  report under the same `key` and pollutes `project.summarize()`
  — the cross-experiment metrics view the audit digest draws
  from. **Two read-only consumers** of the Project share
  the same `summarize()` → `get(id)` → `report.*` discipline:
  `scratch/<ts>_*.py` probes (owned by `setup-workspace`
  § "Scratch is read-only") and `audit/<stem>.py` files (owned by
  `audit-ml-pipeline`, executed via its bundled in-process IPython
  runner; output digest at `scratch/audit/<stem>/audit.md`).
  Neither calls `evaluate(...)` or `put(...)`. `review-ml-experiment`
  does not open the Project at all — it reads the audit digest as
  text and writes one idea file per candidate. The trap the two Project-side
  consumers share: `project.get(key)` raising `KeyError` reads as
  "the report is missing" but actually means "the lookup shape is
  wrong — `get` is by id, not
  by `key`". Never substitute by re-running `evaluate` + `put`.
  See `python -m skore_skills api get` § "Lookup failure ≠ artifact missing" for the
  general registry-lookup discipline.
- **Record a backend locator after every successful `put`.**
  `Project.put(...)` returns `None`; never treat its return value as
  an id or URL. Preserve its stdout, then read
  `project.summarize().frame()`, select the matching key, and take
  the newest row by `date`. The selected report id and the recorded
  `policy.skore_mode` produce one normalized Markdown value:
  - local — `local workspace: [reports/](../reports/) · id: <id>`;
    also surface the resolved absolute `reports/` path to the user.
    Do not link a private serialized artifact.
  - hub — use the exact `Consult your report at …` URL emitted by
    `put`: `[Open report](<url>) · hub · id: <id>`. Do not construct
    a report URL from frontend path conventions. If the installed
    Skore emits no URL, use the Hub project landing page and label
    it `Open project`, not `Open report`.
  - mlflow — use an exact emitted `View run …` URL when present. If
    absent and `tracking_uri` is HTTP(S), use the standard
    `/#/experiments/<experiment-id>/runs/<run-id>` URL after
    resolving the experiment id. For `file:`, `sqlite:`,
    `databricks`, or any nonstandard URI without an emitted URL,
    record `mlflow · tracking: <uri> · experiment: <id> · run:
    <run-id>` without inventing a browser link.
  Never announce or write a locator before `put` succeeds. Include
  it in the standalone User-facing close (locator first among
  tokens, after the narrative) and hand the same value
  to `audit-ml-pipeline` / `manage-ml-backlog` record-outcome.
  Then run `python -m skore_skills loop locator --stem <stem>` and
  paste JSON `locator` verbatim — do not rephrase it. When
  `model-ml-pipeline` dispatched this turn, pass the locator up;
  do not write the full close — the dispatcher owns it.
- **The time-ordered splitter AskUserQuestion is non-skippable,
  even under harness-level "no clarifying questions"
  instructions.** When the data is temporal, the four-option
  pick from rule 3 is an operating-contract gate, not a
  clarifying question. The harness's "no clarifying questions"
  hint applies to agent-discretionary asks (ambiguous wording,
  unclear intent); it never overrides a gate a skill explicitly
  mandates. The same override rule applies to every other
  mandatory `AskUserQuestion` in this stack —
  `add-python-package` § "Where does the package belong?",
  `choose-python-library` (polars vs pandas; policy in
  `skore_skills/data/python-stack.json`),
  `manage-ml-backlog` (idea triage), `review-ml-experiment`
  (audit cost gate). When in doubt: the user's
  approval is the gate, not the harness's instruction text.

## Pre-flight — emit this checklist as visible text before any code

Before writing the evaluation call, output the following block
verbatim in your response. Each box must be backed by an actual
tool call or an explicit decision documented in the response.

```
Pre-flight (evaluate-ml-pipeline):
- [ ] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per `skore_skills/data/python-stack.json` stage libraries)
- [ ] API confirmed for skore symbols (evaluate /
      report classes): <symbols>
      Evidence: python -m skore_skills api get <dotted>
                | Read scratch/api/skore/<version>/<topic>.md (this turn)
                | Write scratch/api/skore/<version>/<topic>.md (this turn)
                | "n/a — no new skore symbol introduced this turn"
- [ ] Call site for `skore.evaluate(...)` / `project.put(...)`
      is `experiments/NN_*.py` (not `scratch/`, not a notebook,
      not `src/<pkg>/`). See Stop condition
      "`skore.evaluate(...)` and `project.put(...)` live only in
      `experiments/NN_*.py`".
      Evidence: Write experiments/<NN>_<name>.py (this turn) |
                "the call already lives in an existing experiments/ file"
- [ ] Post-put locator source: <local summary | exact Hub stdout |
      exact MLflow stdout | MLflow summary + HTTP tracking URI>
- [ ] API confirmed for sklearn splitter: <name>
      Evidence: python -m skore_skills api get <dotted>
                | Read scratch/api/sklearn/<version>/cv_splitters.md
                (or topic-matching file, this turn)
                | Write of the same (this turn)
                | "n/a — Pattern A splitter already in experiments/NN_*.py
                  with unchanged arguments, or Pattern B DataOp cv="
- [ ] split_kwargs at the X marker read: <groups | none>
      Time is a data fact (EDA / journal), not a split_kwargs key.
- [ ] Splitter chosen via rule 3 mapping table: <name + reason>
- [ ] Data-passing form picked: <X, y> | <data={...}>
- [ ] CV pattern: A (`splitter=` on evaluate) | B (DataOp cv +
      omit splitter=) — `references/metadata-routing.md`
- [ ] Smoke test status (per `smoke-test-ml-pipeline`, pytest):
        passing  — CV may proceed after Evaluate consent
                   (`evaluate consent` is `proceed`, or the user
                   answered Evaluate on `ask`);
        failing / missing (history-dependent) — STOP. Do not
                   write `skore.evaluate`. Route to
                   `build-ml-pipeline`;
        n/a      — pipeline has no history-dependent step (rare
                   for time-series / panel data; explain why in
                   the response).
- [ ] If a probe is needed in this turn (skore report walk,
      metric extraction, splitter fold inspection), the payload
      goes to `scratch/<ts>_<short>.py`, **not inline composed-dev
      `python -c "..."`**. No inline allowance — all Python
      execution goes to scratch.
```

## Before execution

After smoke, Evaluate consent, G-SKORE-MODE, and G-CV-SPLITTER
are resolved, emit 1–3 natural sentences immediately before
writing or running `skore.evaluate`. Say that this is **local
model evaluation**: it fits across the full confirmed dataset
using the selected cross-validation scheme, computes report
metrics/checks, and persists the report with `project.put`.
Name the stem, splitter, fold / repeat count when known, and the
`experiments/<stem>.py` plus `scratch/results/<stem>/` outputs.

Describe cost from the known workload: full-data row count when
known, number of fits implied by folds/repeats, learner family,
and requested report materialization. Otherwise say timing
depends on those factors; do not invent minutes. If notebook
conversion will run, say separately that it re-executes the
experiment and may repeat the expensive evaluation.

Emit this preview once before the evaluation boundary, not before
every report accessor. If consent or splitter choice is pending,
preview the possible computation but stop at the mandated
AskUserQuestion. Splitter reasoning / methodology discussion is
**LLM work** until evaluation is approved; it does not itself fit
the model.

## Scope

- **In scope:** choosing the evaluation entry point, picking a
  cross-validator, wiring `split_kwargs` into the splitter, reading
  the report, deciding when to escalate to explicit report classes.
- **Out of scope:** pipeline declaration, hyperparameter search,
  persistence, serving, multi-run tracking.

## Core rules

1. **`skore.evaluate(...)` is the entry point.** It is a dispatcher
   that returns the right report for the task and `splitter`
   argument. **Never** hand-roll `cross_val_score` + manual metric
   prints, and don't drop back to bare sklearn for evaluation. If you
   see existing `cross_val_score` / `cross_validate` /
   `classification_report` / `mean_squared_error` calls in the diff,
   redirect them through `skore.evaluate`. Consult `python -m skore_skills api get` for
   the exact signature.

   **CV wiring is Pattern A or Pattern B** — see
   `references/metadata-routing.md`. `evaluate` has no `groups=`
   (or other `split()` kwargs).

   - **Pattern A** (kwargs-free splitter: `KFold`,
     `TimeSeriesSplit`, …): **always pass `splitter=`**. Omitted
     `splitter=` with no DataOp `cv` is a silent 80/20 holdout.
   - **Pattern B** (`split()` needs `groups` or other kwargs):
     those keys plus `cv=<that splitter>()` live on
     `.skb.mark_as_X`. **Omit `splitter=`** so skore reuses DataOp
     `cv` and `split_kwargs`. Passing `splitter=` **drops**
     `split_kwargs`.

   **Two data-passing forms — pick the one that matches the
   estimator:**

   - sklearn-style: `skore.evaluate(estimator, X, y, splitter=...)`
     for any estimator whose `fit` is `(X, y)`.
   - env-dict-style: `skore.evaluate(learner, data={...})` for a
     skrub `SkrubLearner` (its `fit` takes a single environment
     dict mapping `skrub.var(name=...)` names to values). Add
     `splitter=` for Pattern A; omit it for Pattern B. This is the
     right form for the pipelines produced by `build-ml-pipeline`.

   `X`/`y` and `data` are mutually exclusive. The same split applies
   to `CrossValidationReport(...)`; `EstimatorReport(...)` uses
   `train_data=` / `test_data=` for the env-dict equivalent of
   `X_train` / `y_train` / `X_test` / `y_test`. The full interop
   pattern (env-dict-style vs sklearn-style, how `data={...}` keys
   map to `skrub.var` roots, key conventions in the Project store)
   is in `evaluate-ml-pipeline/references/skrub_interop.md`; for exact
   signatures, run `python -m skore_skills api get` against the
   installed skore version.

2. **Escalate to explicit report classes only when `evaluate` is too
   coarse.** The escalation order:

   - `EstimatorReport` — single fit on a held-out set (no CV); use
     when CV is wasteful (e.g., evaluating the final model on all
     data after CV has already been done).
   - `CrossValidationReport` — k-fold over one learner with access
     to per-fold artifacts.
   - `ComparisonReport` — two or more learners side-by-side.

   See `references/reports.md` for the escalation table; defer all
   API details to `python -m skore_skills api get`.

3. **Pick the cross-validator from the structural facts of the data
   — not by default (the `G-CV-SPLITTER` gate).** The data tells you
   what splitter is correct.
   The structural facts arrive at the X marker through
   `split_kwargs` (set by `build-ml-pipeline` at declaration time)
   **or** from EDA / the journal for time (time is not a
   `split_kwargs` key). Mapping rules:

   | Fact | Splitter |
   |---|---|
   | `split_kwargs` has `groups` | `GroupKFold` (Pattern B) |
   | time-ordered rows (EDA / journal) | **ask the user** (see "Time-ordered data"; Pattern A if they pick `TimeSeriesSplit`) |
   | none | `KFold` (or `RepeatedKFold` for small / noisy data) — Pattern A |

When `split_kwargs` contains `groups`, the next token in the reply
is **`GroupKFold`**. The mapping table is the name source;
API CLI is only for the signature after the name.

   Imbalanced classification *does not* change the choice — use
   plain `KFold` / `GroupKFold`. See "Avoid by default" below.

   **Avoid by default:**
   - **Stratified variants** (`StratifiedKFold`,
     `StratifiedGroupKFold`, `StratifiedShuffleSplit`,
     `RepeatedStratifiedKFold`) — they reduce across-fold variance
     by construction, producing over-confident error bars on the
     score. Don't reach for them on imbalance.
   - **`LeaveOneOut` / `LeaveOneGroupOut` / `LeavePGroupsOut`** —
     high per-fold variance; aggregate hides the noise. Use
     `KFold` / `GroupKFold` with 5–10 splits instead.

   See `references/cross-validation.md` § "Avoid" for the reasoning.
   Wiring details: `references/metadata-routing.md`.

   **Time-ordered data — `AskUserQuestion` is mandatory.** When
   the data is temporal, fire `AskUserQuestion` *before* picking
   a splitter. Paste these **four options verbatim** — keep the
   token `gap=horizon` (do not substitute a numeric horizon such
   as `gap=24`) and keep the phrase "safe default" on option 1:

   1. **`TimeSeriesSplit(gap=horizon)`** — growing-window train,
      contiguous test, embargo equal to the forecast horizon.
      The safe default for any horizon-`h` forecasting task: it
      prevents the train tail from leaking into the test head
      by up to one horizon. Follow up to surface `n_splits` /
      `test_size` / `max_train_size`.
   2. **`TimeSeriesSplit(gap=0)`** — only on the user's explicit
      pick. Warn in the option description that with horizon
      `h > 0`, the last `h` rows of every training fold predict
      values whose target time is *inside* the test fold; the
      reported metric is optimistic.
   3. **Custom splitter** — purged-and-embargoed (finance),
      blocked calendar windows, walk-forward with refit
      cadence. Pick this when the time structure has more shape
      than `TimeSeriesSplit` captures. See
      `references/custom-splitter.md`.
   4. **`KFold` ignoring time** — only when the user confirms
      the temporal structure shouldn't drive splitting (e.g.
      the time column is a covariate but the task is treated
      as IID). The skill should *not* recommend this option on
      time-ordered data without an explicit user reason.

   **No silent default.** Even if the data looks "obviously
   `TimeSeriesSplit`", the user picks via `AskUserQuestion`.
   The gap parameter is the one most often wrong by default —
   `TimeSeriesSplit(n_splits=5)` from memory uses `gap=0`,
   which silently leaks for any non-trivial horizon. Paste that
   token in the reply (`TimeSeriesSplit(n_splits=5)` defaults
   to `gap=0`). The structured pick exists to make that visible.
   Ambiguous free text ("just pick something", "you decide")
   routes to a clarifying `AskUserQuestion`; don't infer.

   Separately, ask whether the time column should stay as a
   covariate or be dropped from the feature matrix (encoders
   can extract calendar patterns from a timestamp; the user's
   call). This is a follow-up question, not a substitute for
   the splitter pick.

   If `split_kwargs` is empty *and* you cannot confirm there's no
   **group** structure, return to `build-ml-pipeline` and ask.
   Time-ordered data with empty `split_kwargs` is expected; use the
   AskUserQuestion above, not a fake `times=` key.

4. **Trust skore's metric defaults; override only on explicit user
   request.** `skore.evaluate` picks task-appropriate metrics
   automatically (regression: MSE/RMSE/MAE/R²; binary: accuracy,
   precision, recall, F1, ROC-AUC; multiclass: macro/micro variants;
   multilabel: per-label + averages). Override only when the user
   says so — e.g., "use RMSE", "report ROC-AUC". Do not pass a
   `scoring=...` argument to `skore.evaluate`; it has no such
   parameter.

   On an explicit custom-metric request, use
   `references/custom-metrics.md`:

   - sklearn-style report metric → `skore.evaluate`, then
     `report.metrics.add(...)`, inspect with `metrics.summarize`;
   - `SkrubLearner` metric with DataOp-derived kwargs such as
     `sample_weight` → return to `build-ml-pipeline` to attach
     `.skb.with_scoring(...)` on the prediction node, then inspect
     with `report.metrics.score()`.

   Metric kwargs are not CV `split_kwargs`. Register and compute
   every requested metric **before** `project.put(...)`; the stored
   report is a snapshot. Use named functions rather than lambdas so
   Project persistence keeps a callable scoring function.

   On an explicit custom-check request, use
   `references/custom-checks.md`. Subclass `skore.Check` at module
   level in `experiments/NN_*.py`, then `report.checks.add(...)`
   after `evaluate` (and after any requested `metrics.add`) and
   **before** `project.put(...)`. Inspect with
   `report.checks.summarize()`. `add` extends SKD checks; it does
   not replace them. Do not invent checks. Do not register them
   from `audit/` (no `put` there). Confirm `Check`,
   `CheckNotApplicable`, and `checks.add` with
   `python -m skore_skills api get`.

5. **Custom splitter — only when sklearn doesn't have it.** Examples
   that justify one: purged-and-embargoed time-series CV (finance),
   blocked spatial CV. The contract is small: `split` +
   `get_n_splits`. See `references/custom-splitter.md`. Otherwise,
   prefer the sklearn built-in.

## Decision flow

1. Is the goal to *score* one learner, or to *compare* ≥ 2?
   - One → `skore.evaluate(...)` (default), escalate to
     `CrossValidationReport` or `EstimatorReport` only if needed.
   - ≥ 2 → `ComparisonReport`.
2. Read `split_kwargs` at the X marker.
3. Map to a splitter using the table in rule 3.
4. Pick the data-passing form (rule 1): `data={"X": X, "y": y, ...}`
   for a `SkrubLearner`, positional `X, y` otherwise.
5. Wire the splitter (see `references/metadata-routing.md`):
   Pattern A → `splitter=` on `evaluate`; Pattern B → DataOp
   `cv=` + `split_kwargs`, **omit** `splitter=`.
6. Inspect the report; override metrics or add custom checks only
   on explicit user request (`references/custom-metrics.md`,
   `references/custom-checks.md`).
7. Register / compute requested custom metrics and checks, then
   `project.put(...)`. Never add them after persistence and assume
   the stored report changed.

## Companion skills

- **`python -m skore_skills api get`** — every skore symbol used here. Mandatory before
  naming `evaluate`, `EstimatorReport`, `CrossValidationReport`,
  `ComparisonReport`, and — on a custom-check path — `Check`,
  `CheckNotApplicable`, and `checks.add`. Don't guess from memory.
  **Cache hits first**: check `scratch/api/skore/<version>/` before
  WebSearching for narrative pages; cache new findings back
  there (per `python -m skore_skills api get` Shape 0/3).
- **`python -m skore_skills api get`** — every splitter used here. Mandatory before
  naming `KFold`, `GroupKFold`, `TimeSeriesSplit`, etc. **Cache
  hits first**: check `scratch/api/sklearn/<version>/` before
  WebSearching.
- **`build-ml-pipeline`** — upstream pipeline shape and where
  structural metadata is attached via `split_kwargs`. Return there
  if the metadata you need at evaluation time isn't wired in,
  *or* if the smoke test (below) fails on row count — that's a
  graph-topology bug owned by `build-ml-pipeline` (rule 2,
  early-`mark_as_X`).
- **`smoke-test-ml-pipeline`** — the structural check CV cannot
  do by construction: predict on a *different* env-dict from the
  one used at fit, assert the prediction count matches the
  predict-grid row count exactly. Required alongside CV for any
  pipeline with a history-dependent step. The CV report and the
  smoke test are independent artifacts — both must be in place
  before an experiment can flip to `done`.
- **`audit-ml-pipeline`** — read-only consumer of the report
  this skill's `skore.evaluate(...)` produced. The experiment
  script puts the report; the audit file loads it via
  `project.summarize()` → `project.get(id)` and renders a
  markdown digest for the agent (no `evaluate`, no `put`).
  Fires after successful evaluate and before record-outcome; its
  digest is an input to `manage-ml-backlog`.
- **`smoke-test-ml-pipeline`** — router for `tests/`. Owns layout and
  the stem pairing between an experiment and its smoke test.
- **`add-python-package`** — detection + install commands for the
  project's environment manager (pixi / uv / poetry / hatch / conda
  / pip+venv). **Invoke whenever** the Stop condition on
  `import skore` fires, or whenever any other dependency is missing
  from the env. Don't infer the manager or hand-craft the install
  command — that skill owns it.
- **`plot-ml-figure`** — load if installed before any custom
  figure cell that skore does not already plot. Do not hand-roll
  ROC/PR in matplotlib. Save PNG (or HTML) and leave the figure
  visible in a notebook; never `plt.close` there. Missing skill →
  one-line skip.
- **`python -m skore_skills style`** — **must be invoked** after
  writing or editing `experiments/NN_*.py` (and `src/<pkg>/evaluate.py`
  only if that stub holds a Pattern A splitter object; and, if a
  custom splitter is authored, the module that holds it). Running
  a manager-specific ruff command directly without invoking this skill
  silently drops the NumPyDoc docstring convention this stack
  expects: ruff's `D`-rules pass on a one-line summary, but only
  the skill body teaches the parameter-shape-in-type-slot,
  `Parameters` / `Returns` / `Yields` sections, and the imperative
  one-line summary.

## End of turn

**G-REPORT-LOCATOR.** After a successful `put`, this step is
mandatory and runs first — before returning to the dispatcher or
running a standalone close. Write
`scratch/results/<stem>/locator.txt`, then run
`python -m skore_skills loop locator --stem <stem>` and paste
JSON `locator` verbatim. Missing locator is the explicit
string `n/a — backend did not expose a locator`, never silence.
Do not invent a URL here — the after-`put` rule above is the
only source.

When `model-ml-pipeline` dispatched this turn, pass JSON
`locator` up and **return immediately**. Do not run
`loop artifacts`. Do not load `audit-ml-pipeline`. Do not run
record-outcome, convert, site, or `git end-turn`. The dispatcher
owns that close. Do not preview it.

Otherwise this skill owns the close. Run
`python -m skore_skills loop artifacts --stem <stem>`.
Treat JSON `action` as authoritative:
- `stop` / `evaluate_incomplete` — do not dispatch audit or
  record-outcome; name the missing file.
- `audit` — load `audit-ml-pipeline` when that skill is installed.
- `record` — skip audit; go to record-outcome.

Then run the block below.

### User-facing close

Standalone only (this skill owns End of turn). The user-facing
message is a short story plus links. It is not Pre-flight, not a
dump of `report.txt` / the design note, and not locator alone.

1. **Narrative first** — 2–6 sentences of the result, grounded in
   the user's headline and, if audit was skipped,
   `scratch/results/<stem>/report.txt`. Do not invent a metric.
   If audit ran this turn, ground the story in the digest
   (Checks + Metrics), not a paste of `audit.md`.
2. **Open these** — resolved absolute paths. When `site build`
   ran or is about to, link the site and not the design note:
   `[report.html](<workspace>/report.html)` and
   `html/<stem>.html`. Otherwise
   `[journal/<stem>.md](journal/<stem>.md)`.
3. **Normalized tokens second** — JSON `locator` verbatim first
   among tokens (local: also the absolute `reports/` path), then
   G-AUDIT-FINDING verbatim (`n/a — audit not run` when skipped).
   Index strings, not the narrative.

If `audit-ml-pipeline` ran this turn, wait for its Close audit
gate, then pass its digest and G-AUDIT-FINDING into
`manage-ml-backlog` **record-outcome mode** only if
`status.skills.manage-ml-backlog` is true. Otherwise call that
mode with the user's headline value, if any, and
G-AUDIT-FINDING=`n/a — audit not run`, so the run reaches
`journal/JOURNAL.md` History and the design-note Status block.
Missing `manage-ml-backlog` → one-line skip; do not write History
from this skill.
Without an audit digest, pass the user's headline value or skip in
one line — do not invent a metric, and never mark `done` while
smoke is red. This runs **before** convert and site build so the
updated journal files are on disk when the site is staged and
`git end-turn` stages the turn.

If `policy.notebooks` is true and `export-ml-notebook` is
installed, run `python -m skore_skills notebook convert
experiments/<stem>.py`, with `--html` when `policy.site` is also
true. Convert re-executes the script; say so when it is slow.
Missing jupytext / nbclient / nbconvert → one-line skip naming
`add-python-package`; do not fail the turn, do not `pixi add`.
When the site is built, evaluation and audit viewers live under
the matching design note's single `## Notebooks` section.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build`. Skip in one line otherwise.
Name a build error; do not fail the evaluate turn. Name
`report.html` (and `html/<stem>.html`) in the User-facing
close when the build ran. Do not also send the user to the
markdown.

Run `python -m skore_skills git end-turn --stage evaluate`. If JSON
`action` is `invoke`, load `persist-ml-git` only if
`status.skills.persist-ml-git` is true and stop; that skill
returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop. Do not run
`git commit` in this skill.

## Need a package?

When an import is missing, load `add-python-package` if
`status.skills.add-python-package` is true. That skill owns
`env add` and the unmanaged ask. Do not run `env add` here.
If the skill is not installed, name the package and stop.

## References

- `references/g_skore_mode.md` (G-SKORE-MODE table; this skill
  owns the gate)
