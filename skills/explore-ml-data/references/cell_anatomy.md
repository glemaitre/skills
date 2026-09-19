# Explore ML Data — Human notebook vs agent facts

`data_analysis/data_analysis.py` is for a person in Jupyter.
Agent-only blobs go under `scratch/data_analysis/`. SKILL.md is
the procedure; this file is the split.

## Human — `data_analysis/data_analysis.py`

Markdown cells describe **this dataset's analysis**, not the repo.
Last expressions are rich objects or small summary frames: the
frame (`RAW`), `skrub.TableReport(...)`, duplicate/target/leakage
tables, bivariate column lists, **and live figures**. `write_html`
saves `data_analysis/data_analysis_<table>.html` for
`data_analysis.md` to embed. Saved figures are PNG siblings under
`data_analysis/`, or Plotly HTML siblings (`<slug>.html`, never
`data_analysis_<table>.html`). Do not put `json()`, dict dumps of TableReport,
or analyses TableReport already covers (dtypes, missingness,
cardinality, univariate histograms, pairwise associations).

Start from `templates/data_analysis.py` if it fits, then **edit**.
Append `templates/target_regression.py` or
`templates/target_classification.py` after the target is known;
append `templates/datetime.py` / `templates/drift.py` only when
those data exist. Do not leave `if TARGET` / `if TASK` /
`OTHER = None` / empty datetime loops / “skip this cell” in the
notebook. Load `plot-ml-figure` before figure cells. Save each
PNG, then leave the figure/grid as the cell output — never
`plt.close`. Prefer seaborn figure-level (`displot`, `relplot`,
`catplot`, `pairplot`); do not `import matplotlib.pyplot` on the
normal path.

`python -m skore_skills cells run` captures `repr()`, so a last-line
`TableReport` looks empty in the digest. That is expected. Do not
put TableReport dicts back in the notebook to feed the agent.

## Agent — `scratch/data_analysis/facts.py`

Copy `templates/facts.py` to `scratch/data_analysis/facts.py`
(gitignored). Reuse the same `<LOAD_RAW_DATA>`, `<TARGET>`,
`<TASK>`. Build `TableReport(..., plot_distributions=False)` and
write `scratch/data_analysis/<table>.json` from `report.json()` so
that snapshot has statistics, not SVG. Also write
`scratch/data_analysis/extras.json` (duplicates, target, top
feature–target correlations, leakage flags, png and html paths). Confirm
keys with `api get`; parse both JSON files with `.get(...)`. If
`data_analysis/data_analysis_<table>.html` is missing, `write_html`
from a **plotting** TableReport — do not dump that report to JSON.

Author `data_analysis/data_analysis.md` from both JSON files plus
the HTML. The glance section is one iframe per table and nothing
else — no bullets restating the report. Figures:
`![](<name>.png)` or `<iframe src="<slug>.html">` beside the
implication they support, never in the glance.

Extra cells after the user picks extras: `references/extra_analyses.md`.

## Substitutions

| Placeholder | Where |
|---|---|
| `<pkg>` | `from <pkg> import PROJECT_ROOT` |
| `<LOAD_RAW_DATA>` | pandas/polars load; convert to pandas for seaborn cells |
| `<table>` | slug for `data_analysis_<table>.html` and `<table>.json` |
| `<TARGET>` | `"column"` in the notebook load cell when a target exists; facts.py may use `None` |
| `<TASK>` | `classification` \| `regression` \| `none` (facts.py; omit in the notebook when none) |
| `<OTHER_FRAME>` | only in `templates/drift.py` when a second table is on disk |
