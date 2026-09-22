# Audit ML Pipeline — Cell anatomy

Full anatomy of an audit-file cell: concrete right/wrong examples,
the core template sequence, and why a bare Display is the right
last expression. Cross-referenced from SKILL.md § "Audit file
contract — overview".

The template core is task-agnostic: persisted-report locator +
checks summary + metrics summary + a `help()` tree per namespace.
The rendered digest at `scratch/audit/<stem>/audit.md`
is what `iterate-from-skore` reads — only `## Checks summary`
and `## Metrics summary`. Do not name extra Display headings
like those two. Per-task accessors are appended after the user
picks Additional report view from names in the trees.

## Concrete cell examples — right vs wrong

A well-formed audit cell ends with a **bare expression**. A
malformed one wraps in `print()` or stores the value in a variable
that's never displayed.

### Right shapes

```python
# %% Right — bare expression auto-displays its repr
summary = project.summarize()
summary
```

```python
# %% Right — multiple statements, bare expression at the end
report = project.get(REPORT_ID)
_results = PROJECT_ROOT / "scratch" / "results" / "01_baseline"
_results.mkdir(parents=True, exist_ok=True)
(_results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
report
```

```python
# %% Right — statement-only is fine (no output expected)
REPORT_ID = "skore:report:cross-validation:42"
```

### Wrong shapes

```python
# %% WRONG — print() loses rich repr; clutters the human-reading view
report = project.get(REPORT_ID)
print(repr(report))  # ← drop the print, leave `report` as bare expr
```

```python
# %% WRONG — value computed but not displayed; cell shows no output
report = project.get(REPORT_ID)
metrics = report.metrics  # ← add `metrics` on its own line at the end
```

```python
# %% WRONG — never call evaluate or put from an audit file
report = skore.evaluate(learner, ...)        # ← read-only contract violated
project.put("01_baseline", report)           # ← duplicates the row; pollutes summarize()
```

### Cell-execution semantics (notebook-style)

- The **last expression** of a code cell is auto-displayed if it's
  a bare expression (no assignment, no statement keyword, no
  `print`).
- Rich `_repr_html_` is preferred over `__repr__` when both exist
  in JupyterLab / VS Code. **The runner does NOT request
  `_repr_html_`** — it captures `repr(result.result)` only. skore
  Displays define both, so one bare Display line serves the editor
  and the digest at once.
- Assignment-only / statement-only cells produce **no output and
  no error** — they execute silently. This is the right shape for
  setup cells (imports, `REPORT_ID = …`, etc.).

## The core template sequence

The template ships with this cell sequence. Core cells are
task-agnostic. Leave them as-is; append Display cells only after
the user picks a name from the `help()` trees.

1. **Module-level docstring (markdown cell).** What this file is,
   the read-only rule, where the digest lands. Verbatim from the
   template.

2. **Imports (code cell).** `import skore` and
   `from <pkg> import PROJECT_ROOT`. No statement-only branching
   here.

3. **Open the Project (code cell, bare expression at the end).**
   ```python
   project = skore.Project(...)
   project
   ```
   The cell's output is the Project's repr — useful for confirming
   the right project, the right workspace, the right mode.

4. **List the available reports (code cell, bare expression).**
   ```python
   summary = project.summarize()
   summary
   ```
   The cell's output is the cross-experiment table.

5. **Load the report (code cell, bare expression).**

   Set `REPORT_ID` to the id of this experiment's report, then load
   it. The id comes from different sources per skore mode:

   - **Hub mode**: `project.put()` prints the exact frontend URL.
     Preserve it as the report locator. The id is
     `skore:report:<type-singular>:<N>` — the URL path segment is
     plural; the id uses the singular. Examples:
     `cross-validations/42` →
     `skore:report:cross-validation:42`; `estimators/7` →
     `skore:report:estimator:7`. Copy `<N>` and `<type-singular>` from
     the put() stdout; hardcode as `REPORT_ID`; no `summarize()` needed.
   - **Local mode**: read `summary["id"]` from the `summarize()` cell
     above, filtering to the row where `key == "<NN>_<short_name>"`.
   - **MLflow mode**: same as local — read `summary["id"]` from the
     `summarize()` cell above, filtering to the newest row where
     `key == "<NN>_<short_name>"`. Preserve an emitted MLflow run URL
     when available; otherwise use the tracking URI + experiment id
     + run id locator contract.

   ```python
   REPORT_ID = "skore:report:<type-singular>:<N>"  # hub: from put() URL

   report = project.get(REPORT_ID)
   _results = PROJECT_ROOT / "scratch" / "results" / "<stem>"
   _results.mkdir(parents=True, exist_ok=True)
   (_results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
   report
   ```
   Confirm `_repr_html_` with `api get`. The HTML is for the site
   Results viewer; the digest's `repr(report)` is what the agent
   summarizes. The two report classes share the
   `checks` / `metrics` accessor API used by the next two cells,
   so the audit body is identical for both.

6. **Persisted report (markdown cell).**

   Substitute `<REPORT_LOCATOR>` with evaluate's normalized
   Markdown value. A direct audit derives it from the selected id
   and backend contract: local workspace link, exact Hub put URL,
   or MLflow run/tracking locator. Missing authoritative data is
   `n/a — backend did not expose a locator`; never guess.

7. **Checks summary (code cell, bare Display last).**
   ```python
   checks = report.checks.summarize()
   _results = PROJECT_ROOT / "scratch" / "results" / "<stem>"
   _results.mkdir(parents=True, exist_ok=True)
   (_results / "checks.html").write_text(checks._repr_html_(), encoding="utf-8")
   checks
   ```
   The repr opens with the severity counts, then lists issues,
   tips, passed, and not-applicable checks with codes like
   `SKD003`. Actionable lines end with the documentation URL that
   `iterate-from-skore` follows to draft Backlog rows.
   Verified on `CrossValidationReport` and `EstimatorReport`.

8. **Metrics summary (code cell, bare Display last).**
   ```python
   metrics = report.metrics.summarize()
   _results = PROJECT_ROOT / "scratch" / "results" / "<stem>"
   _results.mkdir(parents=True, exist_ok=True)
   (_results / "metrics.html").write_text(metrics._repr_html_(), encoding="utf-8")
   metrics
   ```
   Repr is the metric table with task-appropriate defaults:
   - **regression**: RMSE / MAE / R² + fit/predict timings.
   - **binary classification**: accuracy / precision / recall / F1
     / ROC-AUC / log-loss + timings.
   - **multiclass**: macro/micro averages.

9. **Available report accessors (code cell, printed trees).**
   `help()` prints its tree and returns `None`, so the runner
   captures it as stdout — there is nothing to leave as a last
   expression and nothing to write to disk.
   ```python
   for _name in ("metrics", "checks", "inspection", "data"):
       _namespace = getattr(report, _name, None)
       if callable(getattr(_namespace, "help", None)):
           _namespace.help()
   ```
   Each tree ends in a `Displays` group; Additional report view
   labels are exactly those names. The group is task-dependent — a
   regression report offers `prediction_error` and no `roc`. Do not
   remember Display class names from docs. `available()` is a
   different thing: it lists metric or check *names* and only
   exists on `metrics` and `checks`.

That's the core template. Deeper accessors are appended after
`## Core audit complete` only when the user picks Additional
report view (or a Custom query that is still a report accessor).
Confirm the method with `api get`, then snapshot:

```python
# %% [markdown]
# ## <human title>
#
# Heading must not be Checks summary or Metrics summary.

# %%
disp = report.<namespace>.<slug>()  # <slug> from this turn's Displays group
_results = PROJECT_ROOT / "scratch" / "results" / "<stem>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "<slug>.html").write_text(disp._repr_html_(), encoding="utf-8")
disp
```

Plot Displays carry `_repr_html_` too. Only when one does not,
save `<slug>.png` instead. Failed probes stay under `scratch/` and
do not become Results subsections. Re-run `style` + `cells run`
after each append.

## Digest-to-finding contract

G-AUDIT-FINDING is derived after every digest run:

1. Collect checks under `Issues:`, then under `Tips:`, preserving
   their order within each section. Codes are `[SKD003]` tokens.
2. Report counts and each code/severity:
   `<I> issue(s), <T> tip(s) — <CODE> (issue), <CODE> (tip)`.
3. Append a short headline metric clause only when that value is
   present in the metrics summary.
4. With no `Issues:` / `Tips:` lines, use
   `0 issues, 0 tips — automated checks surfaced no actionable finding`.
5. With a missing or errored digest, use
   `n/a — audit digest unavailable`.

The finding is not the headline result. It is handed separately to
record-outcome and copied verbatim into the design note's Status
block. Extra Display cells do not change G-AUDIT-FINDING.

## Why the bare Display is the right last expression

Every skore Display — `ChecksSummaryDisplay`,
`MetricsSummaryDisplay`, and the plot ones like
`PredictionErrorDisplay` — defines **both** `_repr_html_` and a
`__repr__` that renders the underlying values as text. Pinned by
`tests/skore_skills/test_skore_display_repr.py`.

That makes one line serve both audiences. A human opening the
audit `.py` as a notebook gets the rich HTML; the runner captures
`repr(result.result)` and the digest gets the text. `.frame()` is
not needed for either, and on checks it is a downgrade: the frame
drops the severity grouping and buries the messages in a column.

The only thing neither path produces is a *standalone* per-item
HTML file, because the converted notebook is one document. That is
the sole reason cells write `scratch/results/<stem>/<slug>.html` —
the site embeds those under `## Results`. Agents never read them;
they summarize from the digest.

## Statement-only cells are fine

Don't pad them with `print(repr(...))` to "force" output. The
template's "Imports" cell and the `REPORT_ID = ...` setup line
are statement-only by design; they produce no output section in
the digest. That's the right shape.
