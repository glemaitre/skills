---
name: export-ml-notebook
description: >
  Convert a jupytext percent `# %%` Python file into an executed
  `.ipynb` with cell outputs. Pass `--html` when the notebook
  should also become a viewer on the site. Trigger on notebook,
  ipynb, HTML, or executed-report requests, or when export-ml-project
  dispatches notebooks.
---

# Export ML Notebook

Source of truth stays the `# %%` `.py`. This skill only writes
derived `.ipynb` (and optional `.nb.html`). Do not rewrite the
`.py` from the notebook. `cells run` is not a substitute.

While `policy.notebooks` is true, `explore-ml-data`,
`model-ml-pipeline`, and `audit-ml-pipeline` already convert the
percent file they wrote that turn. This skill owns on-demand
conversions, other sources, and the gate itself.

## Sequence

1. `python -m skore_skills status`. Read `policy.notebooks` and
   `skills`.
2. If `policy.notebooks` is `null`: AskUserQuestion executed
   notebooks on/off (default off). Persist `true`/`false`. If
   true, load `add-python-package` for `jupytext` and `nbclient`
   (agent). If false, stop.
3. If `policy.notebooks` is false: say the gate is off; offer to
   turn it on. Do not convert until it is true.
4. Convert the requested percent file (default `data_analysis/data_analysis.py` when
   the user did not name one):

   ```bash
   python -m skore_skills notebook convert data_analysis/data_analysis.py
   ```

   If the user wants the executed notebook on the site, load
   `add-python-package` for `nbconvert` (agent) and pass `--html`
   (writes a self-contained `<stem>.nb.html` next to the `.py`).
   The site embeds that file in the associated exploratory data
   analysis or design report
   with open-separately and fullscreen controls.

   Optional `--out path.ipynb`. Keep `*.ipynb` gitignored unless
   the user asks `setup-git` to track them.
5. After `--html`, if `policy.site` is true, `export-ml-site`
   is installed, run `python -m skore_skills site build` so the
   viewer is packaged. Convert without `--html` does not rebuild
   the site. Skip in one line otherwise. Name a build error; do
   not fail the convert.

## Stop conditions

- Do not `git commit` or `git end-turn`.
- Do not run `cells run` as a substitute for convert.
- Do not `pixi add` / `uv add`; load `add-python-package`.
- Missing skill or missing source → one-line skip.
