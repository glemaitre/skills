# Explore ML Data — Human notebook vs agent facts

`eda/eda.py` is for a person in Jupyter. Agent-only blobs go under
`scratch/eda/`. SKILL.md is the procedure; this file is the split.

## Human — `eda/eda.py`

Markdown cells describe **this dataset's analysis**, not the repo.
Last expressions are rich objects: the frame (`RAW`) and
`skrub.TableReport(...)`. `write_html` saves `eda/eda_<table>.html`
for `eda.md` to embed. Do not put `json()`, dict summaries, or
analyses TableReport already covers (dtypes, missingness,
cardinality, associations).

`python -m skore_skills cells run` captures `repr()`, so a last-line
`TableReport` looks empty in the digest. That is expected. Do not
put dicts back in the notebook to feed the agent.

## Agent — `scratch/eda/facts.py`

Copy `templates/facts.py` to `scratch/eda/facts.py` (gitignored).
Reuse the same `<LOAD_RAW_DATA>`. Write `scratch/eda/<table>.json`
from `report.json()`. Confirm keys with `api get`; parse with
`.get(...)`. If `eda/eda_<table>.html` is missing, `write_html`
there too.

Author `eda/eda.md` from that JSON plus the HTML (iframe + link).
Future figures: `![](eda/<name>.png)` beside the implication they
support.

## Substitutions

| Placeholder | Where |
|---|---|
| `<pkg>` | `from <pkg> import PROJECT_ROOT` |
| `<LOAD_RAW_DATA>` | pandas/polars load; the only library-specific line |
| `<table>` | slug for `eda_<table>.html` and `<table>.json` |
