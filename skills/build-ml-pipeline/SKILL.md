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
  to setup/triage. Do not require `git`.   After the declaration
  exists, load `smoke-test-ml-pipeline` only if
  `status.skills.smoke-test-ml-pipeline` is true and iterate on
  pytest; else one-line skip and do not invent the pytest file.
  Do not start CV here. This action does not cover fitting, CV,
  metrics, persistence, inference, or pure exploratory data
  analysis. Do not invent a missing action skill's steps.

  HOW TO USE: consult before the first declarative line and on
  every structural edit (added/swapped step, changed input columns,
  changed estimator family). Don't re-consult for cosmetic edits.
  **First, read the Stop conditions and emit the Pre-flight
  checklist as visible text before any code.** Always run
  `python -m skore_skills api get <dotted>` to confirm skrub /
  sklearn symbol names and signatures before typing.
---

# Build ML Pipeline (Declaration)

Declare a skrub DataOps graph from source to predictor. Then smoke
(pytest) and the design HITL. Do not fit, split, tune, persist, or
evaluate here.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Experiment markdown, design-note Method text, and `#` comments
describe **this** pipeline — not the skills framework, the CLI, or
the command that produced an output. `<!-- results-embed: … -->` is
a site marker. Authoring hints stay in this skill. `style` is ruff
only.

**Terms.** **X marker** = `.skb.mark_as_X()` (predict-time slice).
**Predict grid** = rows to score (IID: the loaded frame; panels:
`(group, time)`). **Cross-row step** = output for a row reads
other rows (lag, rolling, group-agg, side join, `drop_nulls` on a
shifted col). **Layers 1 / 2 / 3** = sources / grid + marker /
features after the marker.

## Before execution

After `design consent` is `proceed`, emit 1–3 natural sentences
immediately before the first declaration write. Say that this is
**local preparation**, not training or full evaluation: the turn
will write the skrub DataOps `build_learner`, update the
experiment Method cells, render an **unfitted** pipeline snapshot,
and then hand off to a real-data smoke test. Name the stem and the
main `src/<pkg>/`, `experiments/<stem>.py`, and
`scratch/results/<stem>/pipeline.html` outputs.

Describe cost from facts, not guesses. Declaration and unfitted
rendering should be distinguished from the later fit/predict
smoke and full-dataset cross-validation. Do not promise minutes
unless a measured duration is already available. Emit this
preview once; refresh it only when a structural edit materially
changes the work. If approval is pending, preview the possible
work but do not write model code.

Research or open design discussion is **LLM work**: say that it
will reason over the design / sources and stop for confirmation;
it does not fit or test a model.

## Gate context

Every question that gates work carries its own context. Before
asking, state in 2–4 lines what the answer authorizes, the facts
it rests on — echoed inline — and what each option does. A file
link is an addition, never the context.

`evaluate consent` `ask` returns a `context` with `question`,
`experiment`, `smoke`, and `persisted_report`: quote the design
question and what evaluation would now run on the full dataset
before the Evaluate / Modify / Stop menu. For the grouping and
research questions below, the facts are this turn's evidence —
the column names, the distilled finding — so name them in the
question instead of pointing at a file.

## Procedure

1. `python -m skore_skills status`. Missing scaffold → setup/triage
   (S0). Then `python -m skore_skills design consent --stem
   <stem>`. Treat JSON `action` as authoritative. `ask` / `stop`
   → do not declare the pipeline ("build it" is not approval).
   `proceed` continues. Missing data contract → S0.
2. Emit Before execution, then Pre-flight; tick only with
   evidence from this turn.
3. Declare `build_learner` under `src/<pkg>/` (Rule 1–3). Confirm
   new symbols with `python -m skore_skills api get`. After edits,
   `python -m skore_skills style`. Probes go to `scratch/` via the
   composed-dev Python from `env verify` (no inline `python -c`,
   no warning filters unless the user asks).
   Then snapshot the **unfitted** learner — no fit, no
   `SkrubLearner.report`, no `full_report`, no `.skb.eval`. Confirm
   `sklearn.utils.estimator_html_repr` (or the learner's
   `_repr_html_`) with `api get`. Write
   `scratch/results/<stem>/pipeline.html` from that HTML. Ensure
   `journal/<stem>.md` Method contains
   `<!-- results-embed: pipeline -->` (add the line if the note
   predates the marker). Add or update `experiments/<stem>.py`
   Method cells: markdown + a code cell that builds the unfitted
   `build_learner()`, writes the same HTML path, and leaves
   `learner` as the last expression. Do **not** add
   `skore.evaluate` / `project.put` here. Optional:
   `DataOp.skb.draw_graph()` to `pipeline.svg` only if
   `python -m skore_skills env graphviz` is healthy; otherwise
   skip Graphviz in one line. Missing or skipped EDA does not
   defer the site. If `policy.site` is true and
   `export-ml-site` is installed, run
   `python -m skore_skills site build` after this unfitted
   snapshot, before `smoke run` and before the Evaluate
   question, so Method shows the diagram. Skip in one line
   otherwise. Do not `notebook convert` if the experiment file
   already contains `skore.evaluate`.
4. When `experiments/NN_*.py` exists with the matching stem, load
   `smoke-test-ml-pipeline` only if
   `status.skills.smoke-test-ml-pipeline` is true. Missing skill →
   one-line skip; do not invent the pytest file. After the smoke
   file exists, run
   `python -m skore_skills smoke run --stem <stem>`. Treat JSON
   `action` as authoritative. `stop` / `red` / `smoke_missing` →
   fix topology here; do not loosen the assertion; do not
   evaluate. Do not claim pytest is green without this command.
5. `smoke run` `proceed`: User-facing close (checkpoint), then
   run `python -m skore_skills evaluate consent --stem <stem>`.
   Treat JSON `action` as authoritative.
   - `ask` — render that JSON `context` inline (§ Gate context),
     then **AskUserQuestion** (single choice), in order:
     **Evaluate (Recommended)** / **Modify** / **Stop**, then
     **stop**. Do not write `skore.evaluate(...)`. `smoke run`
     `proceed` is not Evaluate. If the user answers **Evaluate**, load
     `evaluate-ml-pipeline` only if
     `status.skills.evaluate-ml-pipeline` is true (or return to
     `model-ml-pipeline` if that is the caller). Missing skill →
     one-line skip. **Modify** — edit, then `smoke run` again.
     **Stop** — end this skill. No `skore.evaluate`.
   - `proceed` — skip the post-smoke menu; load evaluate / return
     to model for re-eval.
   - `stop` — smoke file missing; do not evaluate.

Do not load evaluate before Evaluate on `ask` (or `proceed`).
Re-emit Pre-flight with evidence before the final message.

### User-facing close

Checkpoint after `smoke run` `proceed`, before the Evaluate
menu. The user-facing message is a short story plus links. It
is not Pre-flight, not a dump of the design note, and not
stem/headline/learner alone.

1. **Narrative first** — 2–6 sentences: what was declared, that
   smoke is green, the learner. Ground in Method. Do not invent
   a CV metric. No Skore locator yet (`put` has not run).
2. **Open these** — resolved absolute paths. When `site build`
   ran this turn, link the site and not the design note:
   `[report.html](<workspace>/report.html)` and
   `html/<stem>.html` (Method diagram). Otherwise
   `[journal/<stem>.md](journal/<stem>.md)` and
   `[experiments/<stem>.py](experiments/<stem>.py)`.
3. **Normalized tokens second** — none (no G-REPORT-LOCATOR /
   G-AUDIT-FINDING).

This skill owns the checkpoint. `smoke-test-ml-pipeline` does
not narrate after green.

## Entry contracts

Implement the approved design; do not silently upgrade a choice.

- **Dummy** — `DummyClassifier` / `DummyRegressor` in the normal
  DataOps graph. Operational only. `api get` the exact Dummy.
- **Standard baseline** — skrub `tabular_pipeline` (or installed
  equivalent from `api get`) plus a traditional estimator. No EDA
  features, column recipes, or search.
- **EDA-backed** — only Method-cited findings. Missing choice →
  stop and ask. Temporal grouping is Pattern B metadata (`cv=` +
  `split_kwargs`), not a license for three-layer / lag / `AlignXy`
  unless Method names those steps.
- **Backlog / discussion** — Method is the boundary.

## Canonical pipeline shape — IID flat-table

Copy + adapt. History-dependent / loader-baked Don't:
`references/layer_examples.md` (read it before proposing Layer 2).

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
    data = data_dir.skb.apply_func(load_raw)
    X = data.drop(columns=[TARGET_COL]).skb.mark_as_X()
    y = data[TARGET_COL].skb.mark_as_y()
    predictions = X.skb.apply(
        HistGradientBoostingRegressor(random_state=0), y=y
    )
    return predictions.skb.make_learner()
```

## Stop conditions

Scan top to bottom; any match means STOP.

### S0. Workspace not scaffolded

- **Rule:** `status` first. `has_src` and `has_journal` both false
  → STOP. Do not require `git`.
- **Recovery:** setup/triage. Missing design: run
  `python -m skore_skills design consent --stem <stem>`; `ask` /
  `stop` stop here (`scaffold --journal --stem` if the stem is
  known and journal is the only gap). Missing data contract:
  explain and stop.

### S1. Missing dependency

- **Rule:** `import skrub` / `sklearn` failure, or a DataOp HTML
  stub ("install Pydot and Graphviz"), is `add-python-package` —
  not a pipeline rewrite. Confirm then add `skrub` and
  `scikit-learn`. Graphviz rides with `skrub`; that skill owns
  `env graphviz` / `dot -c`.
- **Recovery:** load `add-python-package` if installed; else name
  the package and stop. Do not `env add` here. Do not
  `pip install graphviz`. Do not substitute `sklearn.Pipeline`.

### S2. Symbol from memory is forbidden

- **Rule:** every new skrub / sklearn / skore name from
  `python -m skore_skills api get <dotted>` or a matching cache
  read *this turn*.
- **Recovery:** run `api get`. Names drift (`tabular_learner`,
  positional `mark_as_y(col)`).

### S3. Splitter selection is out of scope

- **Rule:** no `train_test_split` and no `skore.evaluate` in
  pipeline code. Do not pick `KFold` vs `TimeSeriesSplit`.
  **Exception:** non-empty `split_kwargs` → Pattern B:
  `cv=<mapping-table splitter>()` on `mark_as_X` (skrub requires
  `cv=`). Integer `cv` is not a splitter. See
  `evaluate-ml-pipeline/references/metadata-routing.md`.
- **Recovery:** kwargs-free CV is evaluate Pattern A
  (`splitter=`). Grouped metadata stays on the X marker.

### S4. `skrub.X(...)` / `skrub.y(...)` are not acceptable graph roots

- **Rule:** root on `skrub.var("<source>", value=preview)`.
- **Recovery:** `skrub.var` → `.skb.apply_func(load_fn)` (if the
  source is a path) → `.skb.mark_as_X()`. Existing `skrub.X`
  graphs: surface the alternative and ask; do not auto-rewrite.
  Catalogue: `references/source-binding.md`.

**S4 copy this into the assistant message, then stop.**

```
Refuse: skrub.X / skrub.y are not graph roots (S4).
They bake the marker at the source and defeat Layer 1.

Alternative (refactor — ask before rewriting):
  data = skrub.var("data_dir", value=preview).skb.apply_func(load_raw)
  X = data.drop(columns=[TARGET_COL]).skb.mark_as_X()
  y = data[TARGET_COL].skb.mark_as_y()
```

### S5. Late `mark_as_X` is forbidden when any feature is cross-row

- **Rule:** marker UPSTREAM of every cross-row step. History is
  an extra `apply_func` argument, not fused into the loader.
- **Symptom:** smoke `len(predictions) != n_predict_grid_rows`;
  `feature_steps=[]`; temp-dir history gymnastics; a wrapper
  whose job is to filter NaNs the pipeline produced.
- **Recovery:** three-layer pattern in Rule 2 /
  `references/layer_examples.md`. Do not loosen smoke.

### Loader-baked target shift — refuse immediately

When the loader should compute `y = col.shift(-H)` then
`mark_as_X` on the result: refuse (S5 + S6). Horizon lives in
Layer 2. Do not invent `_ShiftTargetHorizon` / `*Target*`
estimators that `dropna`.

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

- **Rule:** loaders describe *what data exists*. Horizon / lag /
  window / task filter belongs to Layer 2+. Constructive test:
  would an external consumer derive this without knowing our
  task? No → push it past Layer 1.
- **Symptom:** `target.shift(-HORIZON)` or `drop_nulls("y")` in
  the loader. CV looks fine; the next experiment cannot compose
  against the raw source.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `tabular_learner` from memory | Renamed to `tabular_pipeline` in skrub 0.7+ |
| `mark_as_y(target_column)` positional | Dropped in 0.9+. Select the column first |
| `skrub.X(df)` / `skrub.y(s)` as roots | S4 |
| `value="data/train.parquet"` in `pipeline.py` | CWD-relative. Use `data_dir_preview` |
| `feature_steps=[]` at predict | S5. Fix the graph |
| `skore.evaluate(learner, X, y, ...)` | SkrubLearner takes `data={...}` |
| Bare `sklearn.Pipeline` as top-level | Rule 1 |
| Inline composed-dev `python -c` | Write `scratch/<ts>_*.py` |
| `learner.report(...)` / `full_report` / `.skb.eval` for Method | Those **fit**. Use `estimator_html_repr` / `_repr_html_` |

## Pre-flight — emit before any code

Each ticked box requires a tool call this turn.

```
Pre-flight (build-ml-pipeline):
- [ ] Tier 1 libs importable: sklearn, skrub, skore
      Evidence: scratch/<ts>_check_tier1.py + composed-dev output.
                **Inline `python -c` is NOT evidence.**
- [ ] Tabular library: pandas | polars
      Evidence: `status.policy.tabular` | user quote
                | "n/a — pandas already in loader signature"
- [ ] API confirmed for skrub symbols this turn
      Evidence: api get | Read scratch/api/skrub/... (this turn)
                | "n/a — no new skrub symbol"
- [ ] API confirmed for sklearn symbols this turn
      Evidence: api get | Read scratch/api/sklearn/... (this turn)
                | "n/a — no new sklearn symbol"
- [ ] Source-binding pattern chosen
      Evidence: each `skrub.var("<name>")` (source id vs predict-grid)
- [ ] X-marker placement decided
      Evidence: node for `.skb.mark_as_X()`. IID: loaded frame.
                Panel / cold-start: predict-grid, before history-dep.
- [ ] (Cross-row only) each cross-row step names its history DataOp
      Evidence: step + arg | "n/a — no cross-row steps"
- [ ] Layer 1 audit (S6 constructive test)
      Evidence: per upstream `apply_func`: external consumer yes/no
- [ ] Preview value handling
      Evidence: `data_dir_preview=None` kwarg; no path literal
- [ ] split_kwargs at the X marker: groups | none
      Evidence: column(s) wired OR "n/a — i.i.d., no group structure"
- [ ] Pre-flight re-emitted with evidence before final message.
```

## Core rules

### Rule 1 — Skrub DataOps is the pipeline entry point

Root at `skrub.var(...)`, not a bare `sklearn.Pipeline`.
`skrub.X` / `skrub.y` are not roots (S4). Look up signatures
with `api get`.

**If the user asks for `sklearn.Pipeline` / `build_pipeline()`:**
do not `from sklearn.pipeline import Pipeline`, even as an inner
estimator. Redirect to `skrub.var(...)` and `build_learner`
returning `predictions.skb.make_learner()`. Attach `StandardScaler`
then `Ridge` with separate `.skb.apply` calls, or
`skrub.tabular_pipeline` plus a regressor. Do not illustrate the
refusal with a `Pipeline([...])` constructor in a docstring,
heading, or “what I did not write” fence.

https://skrub-data.org/stable/data_ops.html

### Rule 2 — Mark X early; featurize after

*Does any feature look at rows other than the current one?*

| Answer | Placement |
|---|---|
| **No** (per-row math, fit-time encoders) | Marker on the loaded source frame |
| **Yes** (lag / rolling / join / target-shift) | Marker UPSTREAM of every cross-row step |

Three layers when **Yes** (code: `references/layer_examples.md`):

- **Layer 1 — Sources.** One `skrub.var` per identifier. Loaders
  are pure functions of that identifier. No load+featurize in one
  `apply_func`.
- **Layer 2 — Predict grid + marker.** IID: the loaded frame.
  Panels: `(group, time)` grid. `mark_as_X` / `mark_as_y` here.
  Target derivation that needs history is a small `BaseEstimator`
  (`fit_transform → {X, y}` / `transform → {X, y=None}`).
- **Layer 3 — Features after the marker.** History-dependent
  steps take X **and** the Layer-1 history DataOp.

`value=` is preview only. Expose `data_dir_preview=None` on
`build_learner`; never bake a relative path into `pipeline.py`.

**CV metadata at the X marker.** Groups (subjects, sessions,
customer IDs): Pattern B — `cv=` **and** `split_kwargs`. skrub
requires `cv=` whenever `split_kwargs` is set; `cv=<int>` is not
a splitter. `G-CV-SPLITTER` still owns KFold vs time; this is
only the mapping-table placeholder for `groups`.

```python
from sklearn.model_selection import GroupKFold

X = data.drop(columns=[..., "customer_id"]).skb.mark_as_X(
    cv=GroupKFold(),
    split_kwargs={"groups": data["customer_id"]},
)
```

Evaluate omits `splitter=` so skore reuses this `cv` + `groups`
(`evaluate-ml-pipeline/references/metadata-routing.md`).

**Time is not a `split_kwargs` key.** Sort upstream; leave
`split_kwargs` empty. Pattern A (`TimeSeriesSplit`) is evaluate.
Only a custom splitter whose `split()` takes `times=` is Pattern B.
Refuse integer `cv` and unsupported time metadata in prose. Do not
paste forbidden `mark_as_X(...)` / `cv=5` / `times=` into headings
or “what I did not write” fences.

Ask when grouping is plausible (load-bearing tokens), naming the
columns that triggered the question and what grouping would change
(§ Gate context):

```
AskUserQuestion: grouping intended? anything ending in `_id`,
columns called `subject` / `session` / `region`?
```

Do not write `skore.evaluate(...)` here.

### Rule 3 — Attach: stateless function, stateful estimator

- `.skb.apply_func(fn)` — callable, output depends only on the
  current row and constants.
- `.skb.apply(estimator)` — sklearn-compatible; learns on
  training, reapplies on test.
- `skrub.deferred` — rare; only when combining **multiple
  DataOps** and no skrub joiner fits. Default: `apply_func`.
  Details: `references/source-binding.md`.

**Litmus:** would the output change on the training subset vs the
whole frame? Yes → stateful → `.skb.apply`. Means, medians,
quantiles, vocabularies, target distribution, target encoding,
quantile imputation / binning, full-data `OrdinalEncoder` /
`LabelEncoder`, TF-IDF / IDF: all stateful.

```
STOP — target encoding / apply_func. When the user asks for
`def target_encode` + `.skb.apply_func`: refuse. Do not paste
the leaky function body "as requested" and then the fix. Cite
statelessness + leakage. Propose sklearn TargetEncoder (or
BaseEstimator + TransformerMixin) via `.skb.apply`. Mention
API CLI for the TargetEncoder signature.
```

## Reproducibility

`done` History rows must stay runnable. When touching
`src/<pkg>/`, default behavior preserves prior experiments.
Details: `references/reproducibility_mechanics.md`.

- **Option 1** — parametrize with a default-preserving flag
  (small append). Example:
  `include_calendar_features: bool = False`.
- **Option 2** — new function called only from the new experiment.
- **Option 3** — branch the module (last resort).

Tripwires: 3+ flags or unreadable branching → Option 2. A flag
that changes an existing caller's default → STOP. After the
change, pytest **all** of `tests/smoke/`.

## Common patterns

Look up symbols with `api get`. Code: `references/common_patterns.md`.

1. Heterogeneous columns — skrub `cols=` on `.skb.apply`, not
   `ColumnTransformer`.
2. Tabular default — `skrub.tabular_pipeline` / `TableVectorizer`
   first; specialize only when that is not enough.
3. Multi-table — one `skrub.var` per table; `Joiner` /
   `AggJoiner` / `MultiAggJoiner` via `.skb.apply`.
4. Meta-estimator at the tail — wrap the predictor, then
   `.skb.apply`.
5. Hyperparameter knobs — `skrub.choose_*` / `optional` in the
   declaration. Do not import `GridSearchCV` here.
6. Custom transformer — only if no built-in and the op is
   stateful (`BaseEstimator` + `TransformerMixin`). Stateless →
   `apply_func`.
7. Custom DataOp scoring — on explicit request, attach
   `.skb.with_scoring(...)` after prediction and before
   `.skb.make_learner()`. Derive row-aligned metric kwargs from the
   marked X DataOp; keep chained `with_scoring` calls adjacent at
   the graph tail. Evaluate owns `metrics.score()` inspection and
   `Project.put` persistence; see evaluate's
   `references/custom-metrics.md`.

## Companion skills

| Skill | Relationship |
|---|---|
| `python -m skore_skills api get` | Symbol lookup; cache hits first |
| `evaluate-ml-pipeline` | `skore.evaluate` and CV choice after `smoke run` `proceed` + `evaluate consent` (Evaluate HITL on `ask`). Pattern A/B: `references/metadata-routing.md` |
| `smoke-test-ml-pipeline` | Sub-step. Load only if `status.skills.smoke-test-ml-pipeline` is true. Writes `tests/smoke/test_NN_*.py`. Missing skill → one-line skip; do not invent the pytest file |
| `python -m skore_skills smoke run` | After the smoke file exists. JSON `proceed` / `stop` is the only green/red signal |
| `add-python-package` | Missing `skrub` / sklearn / Graphviz companions |
| `research-ml-practice` | Load if installed on FE / transform / leakage. Abstract the **problem class**, not the table name. Summarize `scratch/research/<slug>.md`. AskUserQuestion `allow_multiple` on **`declare`** rows that do not violate stops. `measure` → revisit EDA; do not edit `data_analysis.py`. Declaring id handling does **not** wire Pattern B — no `cv=` / `split_kwargs` / `GroupKFold` until grouping is an approved Method choice. `evaluate` → name `evaluate-ml-pipeline`. `confirm` → ask the user. Missing skill → one-line skip |
| `python -m skore_skills style` | After writing/editing `pipeline.py` / `features.py` / `data.py` |
| `python -m skore_skills env graphviz` | Optional DataOp SVG via `draw_graph`; not required for Method HTML |
| `python -m skore_skills site build` | After the unfitted `pipeline.html` snapshot, before smoke and the Evaluate HITL, when `policy.site` (preview-before-MD-HITL; see `export-ml-site`). Skipped EDA does not defer it |

## References (load on demand)

- `references/layer_examples.md` — IID, loader-baked Don't,
  history-dependent JOIN / AlignXy. Read before proposing Layer 2.
- `references/source-binding.md` — identifier vs materialized
  roots; `apply_func` vs `deferred`.
- `references/reproducibility_mechanics.md` — Option 1 / 2 / 3.
- `references/common_patterns.md` — tabular shapes with code.
- `evaluate-ml-pipeline/references/metadata-routing.md` — Pattern
  A vs B (where `splitter=` vs DataOp `cv=` + `split_kwargs`).
- `evaluate-ml-pipeline/references/custom-metrics.md` — report
  registry vs DataOp scoring, metric kwargs, and persistence order.
