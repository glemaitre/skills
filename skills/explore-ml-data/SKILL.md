---
name: explore-ml-data
description: >
  Owns data understanding BEFORE any model is designed. Places
  `eda/eda.py` (human notebook: TableReport / frames), runs
  `python -m skore_skills cells run`, dumps agent facts under
  `scratch/eda/`, then writes `eda/eda.md` (HTML embeds + modelling
  implications) and JOURNAL § Data understanding. Never designs the
  model, never edits `src/<pkg>/`, never modifies raw data files.

  TRIGGER — any of:
  - The user asks to "explore the data", "do an EDA", "profile the
    dataset", "what does the data look like", "understand the data".
  - Triage sent the user here before modeling (`status.eda` missing).
  - A new or changed data source needs (re-)understanding.

  STOP when `python -m skore_skills status` shows no scaffold or no
  data: explain and send the user to setup or triage. Also stop when
  the request is not raw-data EDA, or when EDA is already recorded
  and no refresh was requested.

  HOW TO USE: G-TABULAR then add pandas/polars + skrub via
  `add-python-package`. Copy `templates/eda.py`, `cells run`, copy
  `templates/facts.py` to scratch, author `eda.md` with embeds.
  Resolve skrub / pandas / polars symbols via `api get`.
---

# Explore ML Data

One project-level EDA: a notebook the user can open, HTML reports,
a short `eda.md` that embeds them, and a JOURNAL index line.

## Artifacts

| Path | Audience |
|---|---|
| raw data (anywhere) | User-owned, **read-only** |
| `eda/eda.py` | Human notebook — analysis markdown + rich displays |
| `eda/eda_<table>.html` | Human — TableReport page, embedded from `eda.md` |
| `eda/eda.md` | Human + later modelling — implications, iframe + link |
| `scratch/eda/<table>.json` | Agent — `TableReport.json()`; gitignored |
| JOURNAL § Data understanding | Index: status, 2–4 line summary, link |

Pattern: last expressions in `eda.py` are `RAW` and `report`.
Agent-only JSON lives in scratch. Do not duplicate TableReport
(dtypes, missingness, cardinality, associations) in extra cells.

Details: `references/cell_anatomy.md`.

## Next-step pointers

| You came here for… | → next |
|---|---|
| Triage sent you here before modeling | → return findings; they inform the baseline |
| User free-text ("explore the data") | → surface findings; no further dispatch unless asked to model |
| Changed data source | → overwrite `eda/eda.*`, refresh JOURNAL |

## Stop conditions

- **Read-only raw data.** Never clean, rewrite, or re-save the
  user's files. Cleaning belongs in `build-ml-pipeline`.
- **Deliverables under `eda/`.** Raw load may point anywhere.
- **G-EDA run | skip.** AskUserQuestion. "Go fast" does not skip.
  Skip → JOURNAL `Status: skipped — <date>` and stop.
- **IPython on the run path.** Missing → `add-python-package` for
  `ipython` (`env route` agent). Decline → skip path. Do not
  `pixi add` / fabricate output.
- **G-TABULAR before `eda/eda.py`.** `status.policy.tabular`; else
  `choose-python-library` (recommend pandas) then
  `add-python-package` for that lib **and** `skrub`. No silent
  default. Do not install sklearn / skore / pytest here.
- **`api get` this turn** for symbols used (cache hits count).
  `TableReport.json()` keys drift — `.get(...)`.
- **One `eda/eda.py`.** Repeat the TableReport cell per table.
  Re-run overwrites in place.
- **Do not design the model.** Implications in `eda.md` only.
- Do not gitignore `eda/`. Ignore specific raw patterns via
  `setup-git` if the user asks (default: don't).

## Pre-flight

```
- [ ] Detect: status.eda present|skipped|missing
- [ ] G-EDA: run | skip (skip → JOURNAL only, STOP)
- [ ] G-TABULAR + add frame lib + skrub (run path)
- [ ] IPython available or add-python-package
- [ ] Place eda/eda.py from templates/eda.py; cells run
- [ ] scratch/eda/facts.py → <table>.json; author eda.md + JOURNAL
```

Tick, then run the matching step. Re-emit with evidence at end of turn.

## Procedure (run path)

1. Copy `templates/eda.py` → `eda/eda.py`. Substitute `<pkg>`,
   `<LOAD_RAW_DATA>`, `<table>`. Markdown is about **this**
   analysis. `python -m skore_skills style` after the write.
2. `python -m skore_skills cells run eda/eda.py` — writes HTML.
   A useless TableReport `repr` in the digest is expected.
3. Copy `templates/facts.py` → `scratch/eda/facts.py` with the
   same load; run it; read `scratch/eda/<table>.json`.
4. Write `eda/eda.md` from `templates/eda.md`: glance, iframe +
   link to each HTML, modelling implications, open questions.
   Ground claims in the JSON and HTML. Do not invent columns.
5. JOURNAL § Data understanding: `Status: done — <date>`, short
   summary, `[eda/eda.md](../eda/eda.md)`. Skip path: Status line
   only.

Import failures → `add-python-package`, do not work around.

## Dispatch

Called from `triage-ml-task` (EDA intent, or EDA-first on a
modeling request while `eda` is missing) and user free-text.

Calls: `add-python-package`, `api get`, `choose-python-library` /
stack for G-TABULAR, `style` after `eda.py`.

Need a package? Load `add-python-package` if installed; else name
it and stop. Do not `env add` here.

## End of turn

`python -m skore_skills git end-turn --stage eda`. If `invoke`,
load `persist-ml-git`. Then `triage-ml-task`. No `git commit`.
