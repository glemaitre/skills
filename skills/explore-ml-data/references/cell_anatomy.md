# Explore ML Data — Human notebook vs agent facts

`data_analysis/data_analysis.py` is for a person in Jupyter.
Agent-only blobs go under `scratch/data_analysis/`. SKILL.md is
the procedure; this file is the split.

## Human — `data_analysis/data_analysis.py`

Markdown cells describe **this dataset's analysis**, not the repo.
Last expressions are rich objects: the frame (`RAW`) and
`skrub.TableReport(...)`. `write_html` saves
`data_analysis/data_analysis_<table>.html` for
`data_analysis.md` to embed. Do not put `json()`, dict summaries,
or analyses TableReport already covers (dtypes, missingness,
cardinality, associations).

`python -m skore_skills cells run` captures `repr()`, so a last-line
`TableReport` looks empty in the digest. That is expected. Do not
put dicts back in the notebook to feed the agent.

## Agent — `scratch/data_analysis/facts.py`

Copy `templates/facts.py` to `scratch/data_analysis/facts.py`
(gitignored). Reuse the same `<LOAD_RAW_DATA>`. Write
`scratch/data_analysis/<table>.json` from `report.json()`. Confirm
keys with `api get`; parse with `.get(...)`. If
`data_analysis/data_analysis_<table>.html` is missing, `write_html`
there too.

Author `data_analysis/data_analysis.md` from that JSON plus the
HTML. The glance section is one iframe per table and nothing
else — no bullets restating the report. Figures:
`![](data_analysis/<name>.png)` beside the implication they
support, never in the glance.

## Substitutions

| Placeholder | Where |
|---|---|
| `<pkg>` | `from <pkg> import PROJECT_ROOT` |
| `<LOAD_RAW_DATA>` | pandas/polars load; the only library-specific line |
| `<table>` | slug for `data_analysis_<table>.html` and `<table>.json` |
