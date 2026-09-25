# %% [markdown]
# # Audit — <NN>_<short_name>: <what this experiment tested>
#
# Read-only review of the stored report: checks and metrics for this
# experiment.

# %%
import skore

from <pkg> import PROJECT_ROOT

# %% [markdown]
# ## Open the project

# %%
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## List the available reports

# %%
summary = project.summarize()
summary

# %% [markdown]
# ## Load the report

# %%
REPORT_ID = "skore:report:<type-singular>:<N>"

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
# Automated checks for this report: issues and tips that affect how
# to read the metrics below.

# %%
checks = report.checks.summarize()
_results = PROJECT_ROOT / "scratch" / "results" / "<NN>_<short_name>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "checks.html").write_text(checks._repr_html_(), encoding="utf-8")
checks

# %% [markdown]
# ## Metrics summary
#
# Headline scores for this experiment (task-appropriate defaults;
# cross-validation reports include mean ± std across folds).

# %%
metrics = report.metrics.summarize()
_results = PROJECT_ROOT / "scratch" / "results" / "<NN>_<short_name>"
_results.mkdir(parents=True, exist_ok=True)
(_results / "metrics.html").write_text(metrics._repr_html_(), encoding="utf-8")
metrics

# %% [markdown]
# ## Available report accessors

# %%
for _name in ("metrics", "checks", "inspection", "data"):
    _namespace = getattr(report, _name, None)
    if callable(getattr(_namespace, "help", None)):
        _namespace.help()

# %% [markdown]
# ## Core audit complete
#
# Checks and metrics above are the first pass. Further views stay
# read-only on this same report.
