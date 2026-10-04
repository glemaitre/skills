# Unfitted snapshot

After `build_learner` exists and before `smoke run`. No fit, no
`SkrubLearner.report`, no `full_report`, no `.skb.eval`.

Confirm `sklearn.utils.estimator_html_repr` (or the learner's
`_repr_html_`) with `python -m skore_skills api get`. Write
`scratch/results/<stem>/pipeline.html` from that HTML.

Ensure `journal/<stem>.md` Method contains
`<!-- results-embed: pipeline -->` (add the line if the note
predates the marker). Add or update `experiments/<stem>.py`:
markdown plus a code cell that builds the unfitted
`build_learner()`, writes the same HTML path, and leaves
`learner` as the last expression. Do not add `skore.evaluate` or
`project.put` here. Do not `notebook convert` this unfitted
snapshot if the experiment file already contains
`skore.evaluate`. That ban is only for this snapshot, before
the first evaluation. `model-ml-pipeline` and
`evaluate-ml-pipeline` still convert `experiments/<stem>.py`
at close.

`DataOp.skb.draw_graph()` to `pipeline.svg` is optional only
before the first draw, and only when `dot` is set. If `dot` is
null, or output contains `install Pydot and Graphviz` or
`Format: "svg" not recognized`, a finished `pipeline.html` does
not authorize a skip. Load `add-python-package` for `skrub`
once. That load is what runs `dot -c` (`env graphviz
--execute`). Then redraw once. Do not run `dot -c` or call
`env graphviz` from this skill. Do not `pip install graphviz`.
Skip only when that skill is missing, or when one redraw after
it returns still fails. Do not rewrite the pipeline.

If `policy.site` is true and `export-ml-site` is installed, run
`python -m skore_skills site build` after this snapshot and
before `smoke run` and the Evaluate question. Skipped or missing
EDA does not defer it. Skip in one line otherwise. If `site
build` errors with `mkdocs-material is required`, load
`add-python-package` for `mkdocs-material` (agent) and build
once more. Do not `pixi add` / `uv add`. If that skill is
missing, or the retry still fails, name the error in one line.
Name a build error; do not skip Evaluate.
