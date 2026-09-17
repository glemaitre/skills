# `data/`

User-owned raw inputs. EDA reads from here (or another path you
choose) and never modifies the files. Do not write `eda.py` /
reports here — those live in `eda/`. Large local files can be
gitignored by pattern (`raw/`, `*.parquet`); do not ignore all of
`data/` if you want small samples committed.
