---
name: build-ml-pipeline
description: >
  Declare the pipeline from data source to predictor as a **skrub
  DataOps graph** (not as a bare `sklearn.Pipeline`). Every step is
  either a pure-Python function (stateless) attached via
  `.skb.apply_func`, or a sklearn-compatible estimator (stateful)
  attached via `.skb.apply`. Stops at the declared object — no fit,
  split, tuning, persistence, or evaluation.

  TRIGGER — any of:
  - Writing or editing code that declares any link in the chain
    *data source → predictor*: loaders, preprocessing, encoders /
    imputers / scalers, feature steps, composition objects
    (`Pipeline`, `ColumnTransformer`, skrub `tabular_pipeline`,
    `nn.Module`), or the final estimator.
  - A pure-Python data-processing function destined for the
    pipeline path (cleans / derives / reshapes) — whether wrapped
    via `FunctionTransformer`, `skrub.@deferred` / `skrub.var`,
    a custom `BaseEstimator` subclass, or just called in the
    training path before the estimator.
  - A step is added, removed, swapped, or reordered inside an
    existing pipeline declaration.
  - A bare `sklearn.Pipeline` / `make_pipeline` is being used as
    the top-level — fire to redirect into a skrub DataOps graph.
  - The user asks to build / declare / set up a pipeline /
    classifier / regressor for X.

  STOP when `python -m skore_skills status` shows no scaffold
  (`has_src` and `has_journal` both false), no approved design,
  or no data contract: explain the missing fact and send the user
  to setup/triage. Do not require `git`. After the declaration
  exists, load `smoke-test-ml-pipeline` and iterate on pytest;
  do not start CV here. This action does not cover fitting, CV,
  metrics, persistence, inference, pure exploratory data analysis,
  or abstract library choice. Smoke-test may be loaded as a
  sub-step; do not require other action skills to be installed.

  HOW TO USE: consult before the first declarative line and on
  every structural edit (added/swapped step, changed input columns,
  changed estimator family). Don't re-consult for cosmetic edits.
  **First, read the Stop conditions and emit the Pre-flight
  checklist as visible text before any code.** Always run
  `python -m skore_skills api get <dotted>` to confirm skrub /
  sklearn symbol names and signatures before typing.
---

# Build ML Pipeline (Declaration)

Declarative shape of a Python ML pipeline from data source to
predictor.

## Terms used in this skill

Read these once; they're referenced throughout.

- **X marker** — the `.skb.mark_as_X()` call that anchors the
  predict-time slice. Everything upstream runs identically at
  fit and predict; everything downstream is per-prediction work.
- **Predict grid** — the rows you want predictions for at predict
  time. For IID flat tables: the loaded frame itself. For
  time-series / panels: a `(group, time)` set.
- **Cold-start row** — a predict-grid row that has no in-slice
  history available (typical for lags at the start of the slice).
- **Predict-time replay** — re-binding the graph to a fresh source
  identifier at predict (e.g. `learner.predict({"data_dir": …})`).
- **Cross-row step** — a feature whose output for a row reads
  values from other rows (lag, rolling window, group aggregation,
  side-table join by time/group, drop_nulls on a shifted column).
- **Layers 1 / 2 / 3** — source / predict-grid + X-marker / features
  after the marker. Defined in Rule 2.

## Completion

Return the declared graph and its verified API evidence, then run
the smoke sub-step (pytest) and the design HITL. Do not start
`evaluate-ml-pipeline` before that ask. If a dependency or
workspace fact is missing, state it and send the user to
setup/triage.

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## After the declaration — pytest smoke, then HITL

`smoke-test-ml-pipeline` is a **sub-step of this skill**, not a
peer the caller picks. After `experiments/NN_*.py` exists with
the matching stem:

1. Load `smoke-test-ml-pipeline`. That skill **runs pytest** on
   `tests/smoke/test_NN_<short_name>.py` (write the test first if
   it is missing). Pytest is how the pipeline is modified: red
   means fix topology **here**, re-load smoke, re-run pytest.
   Do not loosen the assertion. Do not offer evaluate while
   pytest is red.
2. When pytest is green, **report the design** to the user:
   stem, journal Method / Status.headline, and what the learner
   is. Then **AskUserQuestion** (single choice), in this order:
   - **Evaluate (Recommended)** — go forward; say this runs
     **extensive computation on the full dataset**. If the
     caller is `model-ml-pipeline`, return there. Otherwise
     load `evaluate-ml-pipeline`.
   - **Modify** — edit the declaration or design; then smoke
     (pytest) again. Do not load evaluate.
   - **Stop** — end this skill. No `skore.evaluate`.

Do not load evaluate before this ask.

## Model-entry pipeline contracts

The approved design note records which entry choice produced this
experiment. Implement that contract; do not silently upgrade one
choice into another.

- **Dummy predictor.** Use the task-appropriate sklearn
  `DummyClassifier` or `DummyRegressor` as the predictor in the
  normal skrub DataOps graph. Its purpose is operational: exercise
  the real loader, declaration, fit/predict, and pytest smoke path.
  Do not claim predictive value, add domain features, or substitute
  a stronger learner. Confirm the exact Dummy symbol with
  `python -m skore_skills api get`.
- **Standard baseline.** Use skrub's automatic tabular
  preprocessing (`tabular_pipeline`, or the installed-version
  equivalent confirmed by `api get`) with a task-appropriate
  traditional estimator. No EDA-specific feature engineering,
  hand-tuned column recipes, or hyperparameter search. The result
  is the first real comparison point.
- **EDA-backed proposal.** Implement only the EDA findings cited
  in the approved Method. Do not add uncited findings, re-run EDA,
  or turn observations into domain facts. If the proposal needs a
  choice that the EDA does not establish, stop and ask.
- **Backlog / discussion proposal.** Treat the approved Method as
  the boundary. A short Backlog item or chat is not permission to
  invent extra transforms.

## Canonical pipeline shape — IID flat-table

The 90% case. Copy + adapt; replace `TARGET_COL` and the regressor.

```python
import skrub
from sklearn.ensemble import HistGradientBoostingRegressor

from <pkg>.data import TARGET_COL, load_raw


def build_learner(data_dir_preview=None):
    """Return the unfit learner (skrub SkrubLearner)."""
    data_dir = (
        skrub.var("data_dir", value=str(data_dir_preview))
        if data_dir_preview is not None
        else skrub.var("data_dir")
    )

    # Layer 1 + 2: load + mark X / y on the source frame.
    # No cross-row feature steps → marker sits here.
    data = data_dir.skb.apply_func(load_raw)
    X = data.drop(columns=[TARGET_COL]).skb.mark_as_X()
    y = data[TARGET_COL].skb.mark_as_y()

    # Layer 3: estimator at the tail. Feature engineering (if any)
    # chains between mark_as_X and the final .skb.apply.
    predictions = X.skb.apply(
        HistGradientBoostingRegressor(random_state=0), y=y
    )
    return predictions.skb.make_learner()
```

For history-dependent / panel / cold-start cases (≠ IID):
→ `references/layer_examples.md` § history-dependent.

For loader-baked-shift counter-example (what NOT to do):
→ `references/layer_examples.md` § counter-example.

## Stop conditions — read before anything else

Each Stop condition: **rule → symptom → recovery**. Scan top to
bottom; any match means STOP.

### S0. Workspace not scaffolded

- **Rule:** run `python -m skore_skills status` first. If `has_src`
  and `has_journal` are both false, STOP. Do not require `git`.
- **Symptom:** empty folder, no `src/` and no `journal/`.
- **Recovery:** send the user to `setup-ml-project` / triage.
  Missing approved design or data contract: explain and stop
  the same way (scaffold `--journal --stem` when the stem is
  known and journal is the only gap).

### S1. Missing dependency

- **Rule:** `import skrub` or `import sklearn` raising means
  `add-python-package` is next, not a substitute library. Confirm
  then add `skrub` and `scikit-learn` (enforced). Do not reopen
  skrub DataOps vs bare `sklearn.Pipeline`.
- **Symptom:** `ModuleNotFoundError: No module named 'skrub'`
  or `sklearn`.
- **Recovery:** invoke `add-python-package` for `skrub` and
  `scikit-learn`. Do NOT substitute with `sklearn.Pipeline` /
  `make_pipeline` / `FunctionTransformer` — that silently rewrites
  this skill out of the project.

### S1b. DataOp graph needs Pydot and Graphviz

- **Rule:** skrub's HTML repr of a DataOp / learner (`<Apply …>`,
  "To display the DataOp graph, please install Pydot and
  Graphviz") is a missing-companion gap, not a pipeline rewrite.
- **Symptom:** notebook or chat shows that stub instead of a
  graph, including after `notebook convert`.
- **Recovery:** load `add-python-package` for `skrub` (pydot and
  conda Graphviz ride along; that skill owns `env graphviz` and
  `dot -c`). Do NOT `pip install graphviz`. Do NOT replace the
  DataOps graph with `sklearn.Pipeline`.

### S2. Symbol from memory is forbidden

- **Rule:** every new skrub / scikit-learn / skore name must come
  from `python -m skore_skills api get <dotted>` or an existing
  matching cache read *this turn*.
- **Symptom:** you type `tabular_learner` (renamed in 0.7+),
  `mark_as_y(col)` (signature dropped the positional in 0.9+), or
  any name "you remember".
- **Recovery:** run `api get`. Recognition is not a lookup; names
  drift between releases.

### S3. Splitter selection is out of scope

- **Rule:** no `train_test_split` and no `skore.evaluate` in
  pipeline code. Do not pick IID vs time splitters (`KFold`,
  `TimeSeriesSplit`) here. **Exception:** when `split_kwargs` is
  non-empty, pass `cv=<mapping-table splitter>()` on `mark_as_X`
  (skrub requires it). That is Pattern B — see
  `evaluate-ml-pipeline/references/metadata-routing.md`.
- **Symptom:** `from sklearn.model_selection import KFold` as an
  IID default, or `skore.evaluate` in `pipeline.py`.
- **Recovery:** kwargs-free CV is `evaluate-ml-pipeline` Pattern A
  (`splitter=`). Grouped metadata stays on the X marker.

### S4. `skrub.X(...)` / `skrub.y(...)` are not acceptable graph roots

- **Rule:** root on `skrub.var("<source>", value=preview)` instead.
- **Symptom:** code starts with `skrub.X(df)` / `skrub.y(s)`.
- **Recovery:** rewrite to `skrub.var("data_dir", value=...)` →
  `.skb.apply_func(load_fn)` → `.skb.mark_as_X()`. The shortcuts
  (1) bake the marker at the source — defeating Layer 1; (2)
  force a pre-loaded binding, breaking predict-time replay;
  (3) silently re-enable the late-`mark_as_X` bug for cross-row
  features.

**S4 copy this into the assistant message, then stop.** Do not
leave the refuse in a thinking channel. Do not add encoder /
predictor steps on the `skrub.X` skeleton.

```
Refuse: skrub.X / skrub.y are not graph roots (S4).
They bake the marker at the source and defeat Layer 1.

Alternative (refactor — ask before rewriting):
  data = skrub.var("data_dir", value=preview).skb.apply_func(load_raw)
  X = data.drop(columns=[TARGET_COL]).skb.mark_as_X()
  y = data[TARGET_COL].skb.mark_as_y()
```

### S5. Late `mark_as_X` is forbidden when any feature step is cross-row

- **Rule:** for any cross-row step (lag, rolling, group-agg,
  target shift, side-join, `drop_nulls` on shifted col), the
  X marker goes UPSTREAM of that step. The step references the
  cross-row source as an additional `apply_func` argument
  (Layer 1 source → Layer 3 feature, via the marker bypass).
- **Symptom:** the smoke test fails on `len(predictions) !=
  n_predict_grid_rows`; OR a `feature_steps=[]` toggle appears
  in `build_learner` "to make predict work for cold-start"; OR
  a temp-dir gymnastic at predict time to fake history; OR a
  wrapper estimator whose only job is to filter NaN rows the
  pipeline itself produced. (Don't be misled by syntax —
  `pl.col("x").shift(k)` IS cross-row.)
- **Recovery:** fix the graph topology via Rule 2's three-layer
  model. Don't loosen the smoke-test assertion. Don't wrap the
  predictor. Don't `feature_steps=[]`.
- **Proof:** smoke test (`smoke-test-ml-pipeline`) — pipeline
  with marker in the right place passes by construction.

### Loader-baked target shift — refuse immediately

When the user asks the loader to compute `y = col.shift(-H)` (or
equivalent) then `mark_as_X` on the result:

1. Refuse the loader-baked target shift.
2. Cite **late-`mark_as_X` is forbidden** (S5 — cross-row
   dependency) and **Layer 1 doesn't know the question** (S6 —
   the forecasting horizon is not a loader concern).
3. Propose the three-layer pattern: Layer 1 `history_source` +
   `predict_grid`; Layer 2 aligns into `{X, y}` and marks;
   Layer 3 features take X + history as references.

Do not end on a generic three-layer sketch that terminates in an
estimator and omits `history_source` / `predict_grid`. The 24-hour
(or `H`) horizon belongs to **Layer 2**, not Layer 1 and not as a
Layer-3 estimator trick.

```
STOP — no wrapper estimator. Do not invent `_ShiftTargetHorizon`,
`ShiftedTarget`, `*Target*`, or any estimator whose `transform`
shifts / `dropna`s / `is_not_null`-filters. That is the
wrapper-that-filters-NaNs anti-pattern. Paste this pattern instead:

Layer 1: history_source + predict_grid (raw load only; no shift).
Layer 2: align into {X, y} and mark_as_X / mark_as_y (horizon lives here).
Layer 3: features take X + history as references.
```

### S6. Layer 1 doesn't know the question

- **Rule:** Layer 1 (sources + loaders) describes *what data
  exists*. Anything that requires knowing *which rows we want
  predictions for* — any horizon / lag / window / shift — belongs
  to Layer 2 or downstream, never Layer 1.
- **Symptom:** the loader's body contains a `target.shift(-HORIZON)`,
  a `drop_nulls("y")`, or any task-specific filter.
- **Recovery:** push the task-specific operation past Layer 1.
  The horizon / shift belongs to **Layer 2** (align
  `history_source` + `predict_grid` into `{X, y}` and mark). Do
  **not** implement the shift as a stateful `*Target*` estimator
  that filters NaN rows. Layer 3 is features that take X +
  history as references. The smoke test passes trivially when
  the bug is fused into Layer 1 — CV looks fine, and the
  structural debt only surfaces when the *next* experiment
  composes against the raw source.
- **Constructive test:** *would an external consumer — a SQL
  view, a feature store, a second model — derive this same
  output without knowing your task?* No → push it past the
  marker.

### S7. All Python execution goes to `scratch/`

- **Rule:** every Python command (version check, signature
  lookup, data inspection, loader sanity-check, anything) lands
  in `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and runs via
  the composed-dev Python command reported by
  `python -m skore_skills env verify`, replacing its import probe
  with `scratch/<ts>_<short>.py`.
- **Symptom:** you catch yourself typing an inline composed-dev
  `python -c`.
- **Recovery:** write the file first, then execute. **Inline is
  forbidden regardless of length** (see `python -m skore_skills api get` § Stop
  conditions). No 2-line carve-out.

### S8. Don't filter warnings

- **Rule:** no `warnings.filterwarnings(...)` in `pipeline.py` or
  scratch probes unless the user explicitly asks. See
  `python -m skore_skills style` § Stop conditions.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `tabular_learner` from memory | Renamed to `tabular_pipeline` in skrub 0.7+. Memory typed → ImportError on modern installs |
| `mark_as_y(target_column)` positional arg | Dropped in 0.9+. Use `.skb.select("...")` BEFORE the mark |
| `skrub.X(df)` / `skrub.y(s)` as roots | Forbidden (S4). Use `skrub.var("<source>", value=...)` |
| `value="data/train.parquet"` literal in `pipeline.py` | Resolves against CWD; breaks runs from non-root dirs. Expose `data_dir_preview` as kwarg; caller passes `PROJECT_ROOT / "data"` |
| `feature_steps=[]` toggle "to make predict work" | S5 symptom. Fix the graph, not the predict-time bypass |
| `skore.evaluate(learner, X, y, ...)` | SkrubLearner takes an env-dict. Use `data={"data_dir": ..., ...}` |
| `bare sklearn.Pipeline` as top-level | Rewrite as skrub DataOps graph (Rule 1) |
| Inline composed-dev `python -c "..."` | S7. Write to `scratch/<ts>_*.py` instead |

## Pre-flight — emit before any code

Each ticked box requires an actual tool call this turn. Empty
Evidence = unchecked.

```
Pre-flight (build-ml-pipeline):
- [ ] Tier 1 mandatory libs importable: sklearn, skrub, skore
      Evidence: scratch/<ts>_check_tier1.py + composed-dev Python output.
                **Inline `python -c` is NOT evidence.**
- [ ] Tabular library identified: pandas | polars
      Evidence: `status.policy.tabular` | user quote
                | "n/a — pandas already in loader signature"
- [ ] API confirmed for skrub symbols this turn
      Evidence: python -m skore_skills api get <dotted>
                | Read scratch/api/skrub/<v>/<topic>.md (this turn)
                | "n/a — no new skrub symbol this turn"
- [ ] API confirmed for sklearn symbols this turn
      Evidence: python -m skore_skills api get <dotted>
                | Read scratch/api/sklearn/<v>/<topic>.md (this turn)
                | "n/a — no new sklearn symbol this turn"
- [ ] Source-binding pattern chosen
      Evidence: list each planned `skrub.var("<name>")` and state
                whether it's a source identifier (e.g. `data_dir`)
                or a predict-grid descriptor. IID: one `skrub.var`
                rooted on the loaded frame is enough.
- [ ] X-marker placement decided
      Evidence: name the DataOp node where `.skb.mark_as_X()` lands.
                IID: on the loaded source frame. Panel / cold-start:
                on the predict-grid node, BEFORE any history-dep step.
- [ ] (Cross-row pipelines only) Each cross-row step references the
      upstream history DataOp as an extra `apply_func` arg
      Evidence: name each step + its history-DataOp argument
                | "n/a — no cross-row steps"
- [ ] Layer 1 audit — every `apply_func` upstream of `mark_as_X`
      passes the constructive test (S6)
      Evidence: per-step "external consumer would derive this: yes/no"
- [ ] Preview value handling
      Evidence: `build_learner` exposes `data_dir_preview=None` kwarg;
                no relative-path literal baked into `pipeline.py`
- [ ] split_kwargs at the X marker decided: groups | time | none
      Evidence: name the column(s) wired OR "n/a — i.i.d., no group
                or time structure"
- [ ] Smoke test wired (`tests/smoke/test_NN_<short_name>.py`)
      Evidence: per `smoke-test-ml-pipeline`; trivial assertions if no
                history-dep
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## Scope

- **In scope:** how the pipeline *object* is composed — source
  wiring, preprocessing/feature steps, estimator at the tail.
- **Out of scope:** fitting, splitting, tuning, persisting,
  evaluating — those have their own skills.

## Core rules

### Rule 1 — Skrub DataOps is the pipeline entry point

Declare the pipeline as a skrub DataOps graph rooted at one or
more `skrub.var(...)` calls — **not** as a bare
`sklearn.Pipeline`. The `skrub.X(...)` / `skrub.y(...)` shortcuts
are not acceptable roots (see S4). Look up the underlying
signatures via `python -m skore_skills api get`.

**If the user asks for `sklearn.Pipeline` / `build_pipeline()`:**
do not `from sklearn.pipeline import Pipeline`. Redirect to
`skrub.var(...)` and a `build_learner` that returns
`predictions.skb.make_learner()`. Do not illustrate the refusal
with a `Pipeline([...])` constructor in a docstring.

Reference: https://skrub-data.org/stable/data_ops.html

→ next: Rule 2 (where the marker goes).

### Rule 2 — Mark X early; featurize after

The marker is the **shared-vs-predict-specific boundary**.

**One question to place the marker:** *does any feature step look
at rows other than the one currently being processed?*

| Answer | Placement | Pattern |
|---|---|---|
| **No** (per-row math, stateful encoders that learn at fit and apply per-row) | Marker on the loaded source frame | Canonical IID example above |
| **Yes** (lag / rolling / cross-row join / target-shift) | Marker UPSTREAM of every cross-row step | Three-layer model below |

**The three logical layers:**

- **Layer 1 — Sources.** One `skrub.var(...)` per input identifier:
  raw history file(s) / URL(s) / table name(s), side tables, and —
  for time-series / cold-start panels — the *predict-time-grid
  description* (`start`/`end` range, list of `(group_id, time)`).
  The loader for each source is its first `.skb.apply_func`.
  Loaders are pure functions of a single source identifier.
  **Do not load + featurize in one `apply_func`** — that fuses
  Layers 2 + 3 with the loader and breaks predict-time replay.

- **Layer 2 — Predict-time grid + X marker.** A DataOp whose
  rows are exactly the predict grid.
  - IID flat tables: this IS the loaded source frame.
  - Time-series / panel: the `(group, time)` grid derived from
    Layer 1's predict-time bounds.

  **`mark_as_X` and `mark_as_y` go here.** Target derivation that
  requires history (and `drop_nulls` on `y`) belongs to a small
  stateful `BaseEstimator` with `fit_transform → {X, y}` /
  `transform → {X, y=None}`, attached at this layer.

- **Layer 3 — Feature engineering.** `apply_func` chained on the
  X-branch **after** `mark_as_X`. History-dependent steps take the
  X DataOp as their first argument **and** the relevant Layer-1
  source DataOp(s) as additional arguments — history is
  *referenced*, not bound to X. The same history node materializes
  the full available history at fit and at predict, so a backward
  lag computed for a row in the predict grid sees real values from
  the train history — **no cold-start NaN**.

**Worked examples** (full code, IID + history-dependent +
counter-example): → `references/layer_examples.md`. Also see
`build-ml-pipeline/references/pre_mark_alignment.md` for the
production-style three-layer walkthrough drawn from this
workspace's 01_baseline.

**Preview value is a caller-supplied parameter, not a literal in
`pipeline.py`.** `value=` controls what `learner.skb.preview()`
sees during interactive iteration — nothing else. A literal like
`value="data/train.parquet"` resolves against CWD and silently
breaks runs not started from the project root. Expose the preview
as an optional kwarg on `build_learner` and leave it `None` for
production fit / cross-validate.

**Downstream evaluation contract.** A `SkrubLearner` does NOT
implement sklearn's `fit(X, y)` signature — it takes an
environment dict. Pair with
`skore.evaluate(learner, data={"data_dir": ..., ...})`, never
with `skore.evaluate(learner, X, y, ...)` (raises). Pass
`splitter=` only for Pattern A; omit it for Pattern B. See
`evaluate-ml-pipeline/references/metadata-routing.md`; confirm
signatures via `python -m skore_skills api get`.

**Cross-validation metadata at the X marker.** If the data has
group structure (subjects, sessions, customer IDs, repeated
measures), attach the group column at `.skb.mark_as_X` (Pattern B
below). **Ask the user** when you can't tell from data alone —
name suspect columns (anything ending in `_id`, `subject` /
`session` / `region`) and ask whether to wire them. Don't
silently leave `split_kwargs` empty when group structure is
plausible.

**Time ordering is not a `split_kwargs` key.** `TimeSeriesSplit`
needs rows already sorted and no extra `split()` kwargs (Pattern
A). Sort upstream; leave `split_kwargs` empty. Detect time from
EDA / the journal, not by putting `times=` on `mark_as_X`. Only
a **custom** splitter whose `split()` actually takes `times=`
(or similar) is Pattern B.

**Pattern B** (splitter `split()` needs kwargs `evaluate` cannot
take, typically `groups`): pass both `cv=` and `split_kwargs`.
skrub requires `cv=` whenever `split_kwargs` is set. Name the
mapping-table splitter (`GroupKFold` for `groups`) as a
constructor placeholder — `G-CV-SPLITTER` still owns the *choice*;
this is not picking `KFold` vs `TimeSeriesSplit`.

```python
from sklearn.model_selection import GroupKFold

X = data.drop(columns=[..., "customer_id"]).skb.mark_as_X(
    cv=GroupKFold(),
    split_kwargs={"groups": data["customer_id"]},
)
```

**Pattern A** (`KFold`, `TimeSeriesSplit`, …): do **not** set `cv=`
or `split_kwargs`. `evaluate-ml-pipeline` passes `splitter=`.

Do not write `skore.evaluate(...)` in this skill. Full table:
`evaluate-ml-pipeline/references/metadata-routing.md`.

Even when `customer_id` is already wired, still paste this ask
verbatim (the named-heuristic tokens are load-bearing):

```
AskUserQuestion: grouping intended? anything ending in `_id`,
columns called `subject` / `session` / `region`?
```

**When editing an existing pipeline that uses `skrub.X` /
`skrub.y` or binds materialized data:** do not auto-rewrite.
Surface the source-bound alternative and ask whether to refactor.
Full catalogue: → `references/source-binding.md`.

→ next: Rule 3 (attach mechanism).

### Rule 3 — Attach data modifications via `.skb`

Two attach points:

- `.skb.apply_func(fn)` — wraps a callable that transforms data.
- `.skb.apply(estimator)` — wraps any sklearn-compatible estimator
  (transformer in the middle, or the final predictor).

When to use `skrub.deferred` instead of `apply_func`: rare —
only when the callable must combine **multiple DataOps** at once
(e.g. a custom join over two tables). Even then, check whether a
skrub joiner (`Joiner` / `AggJoiner` / `MultiAggJoiner`) covers it
first. Default: `.skb.apply_func`. Details:
→ `references/source-binding.md`.

→ next: Rule 4 (function vs estimator).

### Rule 4 — Stateless → function. Stateful → estimator.

The *only* decision rule for picking `apply_func` vs `apply`:

- **Stateless** — output for a row depends only on that row (and
  constants). No info borrowed across rows.
- **Stateful** — needs statistics / vocabulary / learned
  parameters fit on **training** data and re-applied unchanged to
  **test** data.

```python
# Stateless — pure function + apply_func
import numpy as np

X = X.skb.apply_func(lambda df: df.assign(log_price=np.log1p(df["price"])))

# Stateful — estimator + apply
from sklearn.preprocessing import StandardScaler

X = X.skb.apply(StandardScaler())
```

If a step would silently learn from the test set when called as
a plain function, it is stateful — promote it.

→ next: Rule 5 (leakage check).

### Rule 5 — Leakage rule

Any computation using statistics learned from the data (means,
medians, quantiles, vocabularies, target distribution) MUST be
stateful. Calling such a computation as a plain function over the
whole frame leaks test into training.

```python
# WRONG — pct rank fits on the full frame, leaks test into training
X = X.skb.apply_func(lambda df: df.assign(p=df["x"].rank(pct=True)))

# RIGHT — quantile transformer learns on training fold only
from sklearn.preprocessing import QuantileTransformer

X = X.skb.apply(QuantileTransformer(output_distribution="uniform"))
```

Classic traps by name:

- target encoding (must `fit` on training y only),
- target-aware or quantile-based imputation,
- quantile binning / `KBinsDiscretizer(strategy="quantile")`,
- `OrdinalEncoder` / `LabelEncoder` whose categories come from
  the full dataset rather than `fit` on training only,
- vocabulary-building text tokenizers, TF-IDF, IDF weights.

**Litmus test:** would this output change if I called it on the
training subset alone vs the whole frame? If yes → stateful →
`.skb.apply` with an estimator, never `.skb.apply_func`.

```
STOP — target encoding / apply_func. When the user asks for
`def target_encode` + `.skb.apply_func`: refuse. Do not paste
the leaky function body "as requested" and then the fix. Cite
statelessness + leakage. Propose sklearn TargetEncoder (or
BaseEstimator + TransformerMixin) via `.skb.apply`. Mention
API CLI for the TargetEncoder signature.
```

→ next: Decision flow.

## Decision flow for a new step

1. Does the operation only need the current row (and constants)?
   → **stateless** → pure Python function + `.skb.apply_func`.
2. Otherwise it must learn from training data and reapply on test.
   → **stateful** → sklearn-compatible estimator + `.skb.apply`.

→ next: Reproducibility (when touching shared modules).

## Reproducibility — extending without breaking prior experiments

`manage-ml-backlog` enforces a hard rule: every `done` row in
`JOURNAL.md` History must stay runnable on `main` and produce the
same result. When touching a shared module under `src/<pkg>/`,
**default behavior must preserve prior experiments' shape**.

**Three options, picked by judgment** (full procedures + worked
examples: → `references/reproducibility_mechanics.md`):

- **Option 1 — parametrize the existing function** (with a
  default-preserving flag). Pick when the change is small and
  scoped: a step appended at the end, a single conditional, a
  stateless transform that adds columns without reshaping
  existing ones. **The flag's default mirrors prior behavior.**
  Show it annotated:
  `include_calendar_features: bool = False`. Mention
  `tests/smoke/` (run **all** smoke tests) as the cheap check
  that prior experiments still pass.
- **Option 2 — add a new function called only from the new
  experiment.** Pick when the change doesn't fit cleanly behind a
  flag: new estimator at the tail, a step that reshapes the
  graph, or Option 1 would grow ugly internal branching.
- **Option 3 — branch the module.** Last resort. Only when the
  change touches enough internal structure that Options 1 and 2
  would obscure the diff. Usually a signal of a deeper layering
  issue worth surfacing to the user.

### Tripwires (load-bearing)

- **3+ flags in one function** → parametrization is leaking;
  reach for Option 2 next.
- **Visible branching in the function body** that makes it hard
  to read → reach for Option 2.
- **A flag changes default behavior of an existing caller** →
  STOP. Rule broken. Either keep the default preserving, or use
  Option 2.

### Cheap executable check

The post-build smoke gate runs **all** of
`tests/smoke/`, not just the new one. A prior smoke test going
red after a change = default behavior not preserved. Fix before
declaring the new experiment ready.

→ next: Common patterns (for recurring shapes).

## Common patterns

Short catalogue. Look up exact symbols with
`python -m skore_skills api get`. Full
catalogue with code: → `references/common_patterns.md`.

1. **Heterogeneous columns** — skrub column selectors with `cols=`
   on `.skb.apply` (one apply per group), not `ColumnTransformer`.
2. **Default starting point for tabular data** — reach for
   `skrub.tabular_pipeline(...)` or `TableVectorizer` + estimator
   first; specialize column-by-column only when default is
   insufficient.
3. **Multi-table inputs** — one `skrub.var(...)` per table; join
   with skrub `Joiner` / `AggJoiner` / `MultiAggJoiner` via
   `.skb.apply(...)`.
4. **Meta-estimator at the tail** — `StackingClassifier`,
   `CalibratedClassifierCV`, `TransformedTargetRegressor`. Wrap
   the predictor first, then attach via `.skb.apply` as the final
   step.
5. **Mark hyperparameter knobs in place** — wrap with
   `skrub.choose_from` / `choose_int` / `choose_float` /
   `optional` inside the declaration. Don't import `GridSearchCV`
   here; the tuning skill owns search.
6. **Custom sklearn transformer** — author only when (a) no
   built-in fits and (b) the operation is stateful. Subclass
   `BaseEstimator` + `TransformerMixin`. For a stateless op,
   write a function and use `.skb.apply_func`.

## Companion skills

| Skill | Relationship |
|---|---|
| `python -m skore_skills api get` | Authoritative lookup of sklearn / skrub / skore. Invoke whenever picking a symbol; cache hits first (Shape 0) |
| `evaluate-ml-pipeline` | Owns `skore.evaluate`, CV selection, metric defaults. Load only after green pytest and the Evaluate HITL pick. Consumes the `split_kwargs` wired at the X marker |
| `smoke-test-ml-pipeline` | **Sub-step.** Writes `tests/smoke/test_NN_*.py` and **runs pytest**. Red pytest → stay here and fix topology; do not loosen the assertion |
| `add-python-package` | Detection + install commands. Invoke when `import skrub` raises |
| `research-ml-practice` | Literature worker. Load if installed on a FE / transform / leakage concern; distill below. Missing → one-line skip |
| `python -m skore_skills style` | **Must be invoked** after writing or editing `pipeline.py` / `features.py` / `data.py`. Direct manager-specific ruff commands drop the NumPyDoc convention |

## Literature distillation

On a FE / transform / leakage concern, load `research-ml-practice`
if installed; pass the concern and stage `model`. Abstract the
**problem class** (domain, task, phenomenon) — do not pass
`fetch_california_housing` or the table’s proper name. Summarize
`scratch/research/<slug>.md` in chat; do not dump the note.
**AskUserQuestion** `allow_multiple` on **`declare`** rows that
do not violate stop conditions (no fit, no mutate `data/`, no
silent learner). Picks: `.skb.apply` / `apply_func` after design
approval, `api get`, `style`, record in the design note — not
`data_analysis.md`. `measure` → revisit EDA / open question; do
not edit `data_analysis.py`. `evaluate` → name
`evaluate-ml-pipeline`; do not invent CV. `confirm` → ask the
user.

## Need a package?

When an import is missing, load `add-python-package` if
`status.skills.add-python-package` is true. That skill owns
`env add` and the unmanaged ask. Do not run `env add` here.
If the skill is not installed, name the package and stop.

## References (load on demand)

- `references/source-binding.md` — full catalogue of source-binding
  patterns (encouraged / discouraged / OK-but-offer-upgrade) +
  the `apply_func` vs `deferred` decision.
- `references/layer_examples.md` — worked code for the IID
  flat-table case, the loader-baked-shift counter-example, and
  the history-dependent three-layer pattern.
- `references/reproducibility_mechanics.md` — full Option 1 / 2 /
  3 procedures with code, plus the tripwire criterion.
- `references/common_patterns.md` — full catalogue of recurring
  pipeline shapes with code snippets.

> **Companion skill (planned): `review-ml-pipeline`** —
> methodological review of an existing declaration (leakage audit,
> statelessness check, step ordering, scope creep). When it flags
> a problem, return here to fix.
