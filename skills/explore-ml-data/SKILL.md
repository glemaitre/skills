---
name: explore-ml-data
description: >
  Owns data understanding BEFORE any model is designed. Places
  `data_analysis/data_analysis.py` (human notebook: TableReport /
  frames), runs `python -m skore_skills cells run`, dumps agent
  facts under `scratch/data_analysis/`, then writes
  `data_analysis/data_analysis.md` (HTML embeds + modelling
  implications) and JOURNAL § Data understanding. Never designs the
  model, never edits `src/<pkg>/`, never modifies raw data files.

  TRIGGER — any of:
  - The user asks to "explore the data", "do an EDA", "profile the
    dataset", "what does the data look like", "understand the data".
  - Triage sent the user here before modeling
    (`status.data_analysis` missing).
  - A new or changed data source needs (re-)understanding.

  STOP when `python -m skore_skills status` shows no scaffold or no
  data: explain and send the user to setup or triage. Also stop when
  the request is not raw-data exploration, or when exploratory data
  analysis is already recorded and no refresh was requested.

  HOW TO USE: G-TABULAR then add pandas/polars + skrub via
  `add-python-package`. Copy `templates/data_analysis.py`,
  `cells run`, copy `templates/facts.py` to scratch, author
  `data_analysis.md` with embeds. Resolve skrub / pandas / polars
  symbols via `api get`.
---

# Explore ML Data

One project-level exploratory data analysis: a notebook the user
can open, HTML reports, a short `data_analysis.md` that embeds
them, and a JOURNAL index row.

## Artifacts

| Path | Audience |
|---|---|
| raw data (anywhere) | User-owned, **read-only** |
| `data_analysis/data_analysis.py` | Human notebook — analysis markdown + rich displays |
| `data_analysis/data_analysis_<table>.html` | Human — TableReport page, embedded from `data_analysis.md` |
| `data_analysis/data_analysis.md` | Human + later modelling — TableReport iframes, implications |
| `scratch/data_analysis/<table>.json` | Agent — `TableReport.json()`; gitignored |
| JOURNAL § Data understanding | Index: status, 2–4 line summary, link |

Pattern: last expressions in `data_analysis.py` are `RAW` and
`report`. Agent-only JSON lives in scratch. Do not duplicate
TableReport (dtypes, missingness, cardinality, associations) in
extra cells.

Details: `references/cell_anatomy.md`.

## Next-step pointers

| You came here for… | → next |
|---|---|
| Triage sent you here before modeling | → return findings; they inform the baseline |
| User free-text ("explore the data") | → surface findings; no further dispatch unless asked to model |
| Changed data source | → overwrite `data_analysis/data_analysis.*`, refresh JOURNAL |

## Stop conditions

- **Read-only raw data.** Never clean, rewrite, or re-save the
  user's files. Cleaning belongs in `build-ml-pipeline`.
- **Deliverables under `data_analysis/`.** Raw load may point
  anywhere.
- **G-DATA-ANALYSIS run | skip.** AskUserQuestion. "Go fast" does
  not skip. Skip → JOURNAL Status row `skipped — <date>` and stop.
  Do not run `site build` on skip.
- **IPython on the run path.** Missing → `add-python-package` for
  `ipython` (`env route` agent). Decline → skip path. Do not
  `pixi add` / fabricate output.
- **G-TABULAR before `data_analysis/data_analysis.py`.**
  `status.policy.tabular`; else `choose-python-library` (recommend
  pandas) then `add-python-package` for that lib **and** `skrub`.
  No silent default. Do not install sklearn / skore / pytest here.
- **`api get` this turn** for symbols used (cache hits count).
  `TableReport.json()` keys drift — `.get(...)`.
- **One `data_analysis/data_analysis.py`.** Repeat the TableReport
  cell per table. Re-run overwrites in place.
- **Do not design the model.** Implications in
  `data_analysis.md` only.
- Do not gitignore `data_analysis/`. Ignore specific raw patterns
  via `setup-git` if the user asks (default: don't).

## Pre-flight

```
- [ ] Detect: status.data_analysis present|skipped|missing
- [ ] G-DATA-ANALYSIS: run | skip (skip → JOURNAL only, STOP)
- [ ] G-TABULAR + add frame lib + skrub (run path)
- [ ] IPython available or add-python-package
- [ ] Place data_analysis/data_analysis.py from
      templates/data_analysis.py; cells run
- [ ] scratch/data_analysis/facts.py → <table>.json; author
      data_analysis.md + JOURNAL
```

Tick, then run the matching step. Re-emit with evidence at end of turn.

## Procedure (run path)

1. Copy `templates/data_analysis.py` →
   `data_analysis/data_analysis.py`. Substitute `<pkg>`,
   `<LOAD_RAW_DATA>`, `<table>`. Markdown is about **this**
   analysis. `python -m skore_skills style` after the write.
2. `python -m skore_skills cells run
   data_analysis/data_analysis.py` — writes HTML. A useless
   TableReport `repr` in the digest is expected.
3. Copy `templates/facts.py` → `scratch/data_analysis/facts.py`
   with the same load; run it; read
   `scratch/data_analysis/<table>.json`.
4. Write `data_analysis/data_analysis.md` from
   `templates/data_analysis.md`: glance (one iframe per table and
   nothing else), modelling implications, open questions. Reports
   and figures are embedded, not linked; `![](<name>.png)` sits
   beside the implication it supports, never in the glance.
   Ground claims in the JSON and HTML. Do not invent columns.
5. JOURNAL § Data understanding table: Status `done — <date>`,
   short summary, Report
   `[data_analysis/data_analysis.md](../data_analysis/data_analysis.md)`.
   Skip path: Status row only.

Import failures → `add-python-package`, do not work around.

## Dispatch

Called from `triage-ml-task` (explore-the-data intent, or
explore-first on a modeling request while `data_analysis` is
missing) and user free-text.

Calls: `add-python-package`, `api get`, `choose-python-library` /
stack for G-TABULAR, `style` after `data_analysis.py`.

Need a package? Load `add-python-package` if installed; else name
it and stop. Do not `env add` here.

## End of turn

If `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build` after durable files are on
disk. Do not run `notebook convert`. Skip in one line otherwise.
Name a build error; do not fail the data-analysis turn.

`python -m skore_skills git end-turn --stage data_analysis`. If
`invoke`, load `persist-ml-git`. Then `triage-ml-task`. No
`git commit`.
