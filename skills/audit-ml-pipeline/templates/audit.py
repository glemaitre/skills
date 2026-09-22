# %% [markdown]
# # Audit — <NN>_<short_name>: <what this experiment tested>
#
# Read-only review of the stored report below: its checks and metrics.

# %%
import skore

from <pkg> import PROJECT_ROOT

# %% [markdown]
# ## Open the project
#
# Open the same project the experiment wrote to. The init block below
# must match `experiments/<NN>_<short_name>.py` exactly — copy it from
# there rather than retyping it.

# %%
# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## List the available reports
#
# `project.summarize()` provides an overview of all reports in this
# Project — useful to confirm the experiment's report landed and to
# spot duplicate keys from accidental re-runs.

# %%
summary = project.summarize()
summary

# %% [markdown]
# ## Load the report
#
# **Hub mode** — `project.put()` prints the exact frontend URL.
#
# The report id is `skore:report:<type-singular>:<N>`.  The URL path
# segment is the plural; the id uses the singular (drop the trailing
# `s`).  Examples:
#
#   `.../cross-validations/42`  →  `skore:report:cross-validation:42`
#   `.../estimators/7`          →  `skore:report:estimator:7`
#
# Copy `<N>` and `<type-singular>` from the experiment's stdout and
# set `REPORT_ID` below — no `summarize()` traversal needed.
#
# **Local and MLflow modes** — read the `"id"` column value from the
# `summary` DataFrame above for the newest row whose `"key"` matches
# this experiment's stem, and set `REPORT_ID` to that value.

# %%
REPORT_ID = "skore:report:<type-singular>:<N>"  # hub: from put() URL (plural→singular); local/mlflow: newest matching summary["id"]

report = project.get(REPORT_ID)
_results = PROJECT_ROOT / "scratch" / "results" / "<NN>_<short_name>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
(_results / "locator.txt").write_text("<REPORT_LOCATOR>", encoding="utf-8")
report

# %% [markdown]
# ## Persisted report
#
# <REPORT_LOCATOR>

# %% [markdown]
# ## Checks summary
#
# `report.checks.summarize()` groups every check by severity
# (`issue` / `tip` / `passed` / not applicable). Each line carries a
# `code` (e.g. `SKD003` or a custom `CSTM001`) and, for the
# actionable ones, the documentation URL describing what the check
# tests and what to try next. Custom checks may have no URL.
#
# Available on `EstimatorReport` and `CrossValidationReport` in
# skore ≥ 0.18. Mute a noisy check via
# `report.checks.summarize(ignore=['<code>'])`.
#
# Docs: https://docs.skore.probabl.ai/0.18/user_guide/automated_checks.html

# %%
checks = report.checks.summarize()
_results = PROJECT_ROOT / "scratch" / "results" / "<NN>_<short_name>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "checks.html").write_text(checks._repr_html_(), encoding="utf-8")
checks

# %% [markdown]
# ## Metrics summary
#
# `report.metrics.summarize()` covers task-appropriate
# defaults in one call:
#
# - regression: RMSE / MAE / R² + fit/predict timings,
# - binary classification: accuracy / precision / recall / F1 /
#   ROC-AUC / log-loss + timings,
# - multiclass: macro / micro averages of the above.
#
# Same accessor on both `EstimatorReport` and
# `CrossValidationReport`; the latter additionally reports mean ±
# std across folds. This is the headline reading; the actionable
# findings come from the checks section above.

# %%
metrics = report.metrics.summarize()
_results = PROJECT_ROOT / "scratch" / "results" / "<NN>_<short_name>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "metrics.html").write_text(metrics._repr_html_(), encoding="utf-8")
metrics

# %% [markdown]
# ## Available report accessors
#
# `help()` prints one tree per namespace, ending in a `Displays`
# group. That printed tree is this turn's menu: Additional report
# view offers only names it lists, never a remembered Display
# catalogue. The list is task-dependent — a regression report has
# no `roc`. Namespaces missing on this report are skipped.

# %%
for _name in ("metrics", "checks", "inspection", "data"):
    _namespace = getattr(report, _name, None)
    if callable(getattr(_namespace, "help", None)):
        _namespace.help()

# %% [markdown]
# ## Core audit complete
#
# Checks and metrics above are the deterministic first pass.
# User-selected additional report views, queries, or plots are
# appended below and remain read-only. Discover names from the
# accessors tree; confirm each with `api get` before calling it.
