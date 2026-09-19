# Explore ML Data — Human notebook vs agent facts

`data_analysis/data_analysis.py` is for a person in Jupyter.
Agent-only blobs go under `scratch/data_analysis/`. SKILL.md is
the procedure; this file is the split.

## Human — `data_analysis/data_analysis.py`

Markdown cells describe **this dataset's analysis**, not the repo.
Last expressions are rich objects or small summary frames: the
frame (`RAW`), `skrub.TableReport(...)`, duplicate/target/leakage
tables, bivariate column lists. `write_html` saves
`data_analysis/data_analysis_<table>.html` for
`data_analysis.md` to embed. Saved figures are PNG siblings under
`data_analysis/`. Do not put `json()`, dict dumps of TableReport,
or analyses TableReport already covers (dtypes, missingness,
cardinality, univariate histograms, pairwise associations).

`python -m skore_skills cells run` captures `repr()`, so a last-line
`TableReport` looks empty in the digest. That is expected. Do not
put TableReport dicts back in the notebook to feed the agent.

Substitutions: `<TARGET>` is `None` or `"column"`; `<TASK>` is
`classification`, `regression`, or `none`; `<OTHER_FRAME>` is
`None` unless a second table is already on disk.

## Agent — `scratch/data_analysis/facts.py`

Copy `templates/facts.py` to `scratch/data_analysis/facts.py`
(gitignored). Reuse the same `<LOAD_RAW_DATA>`, `<TARGET>`,
`<TASK>`. Build `TableReport(..., plot_distributions=False)` and
write `scratch/data_analysis/<table>.json` from `report.json()` so
that snapshot has statistics, not SVG. Also write
`scratch/data_analysis/extras.json` (duplicates, target, top
feature–target correlations, leakage flags, png paths). Confirm
keys with `api get`; parse both JSON files with `.get(...)`. If
`data_analysis/data_analysis_<table>.html` is missing, `write_html`
from a **plotting** TableReport — do not dump that report to JSON.

Author `data_analysis/data_analysis.md` from both JSON files plus
the HTML. The glance section is one iframe per table and nothing
else — no bullets restating the report. Figures:
`![](<name>.png)` beside the implication they support, never in
the glance.

Extra cells after the user picks extras: `references/extra_analyses.md`.

## Substitutions

| Placeholder | Where |
|---|---|
| `<pkg>` | `from <pkg> import PROJECT_ROOT` |
| `<LOAD_RAW_DATA>` | pandas/polars load; convert to pandas for seaborn cells |
| `<table>` | slug for `data_analysis_<table>.html` and `<table>.json` |
| `<TARGET>` | `None` or `"column"` |
| `<TASK>` | `classification` \| `regression` \| `none` |
| `<OTHER_FRAME>` | `None` or a second loaded frame |
