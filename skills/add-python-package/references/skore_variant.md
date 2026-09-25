# Skore package source and mode

Environment bootstrap installs plain `skore` early so
`skore_skills` is available as its mandatory dependency. Do not
construct a Skore requirement in a skill. After G-SKORE-MODE is
persisted, run:

```bash
python -m skore_skills env add-skore --mode <local|hub|mlflow> --execute
```

The CLI selects the package source from the manifest-detected
manager and upgrades the bootstrap installation when the selected
mode needs Hub or MLflow dependencies:

| Manager | local | hub | mlflow |
|---|---|---|---|
| pixi / conda | conda-forge `skore` | conda-forge `skore` | conda-forge `skore` + `mlflow>=3` |
| uv / poetry / hatch / pip-venv | PyPI `skore` | PyPI `skore[hub]` | PyPI `skore[mlflow]` + `mlflow>=3` |

The conda-forge package supports local and Hub use without PyPI
bracket extras. MLflow always gets the explicit `mlflow>=3`
constraint.

## Forbidden

- Sending `skore[hub]` or `skore[mlflow]` to pixi/conda.
- Forcing `--pypi` in a pixi project.
- Installing a PyPI wheel into a conda env because an extra appears
  in prose.
- Omitting `mlflow>=3` in MLflow mode.
- Using PATH or Skore CLI provenance to choose the package source.
  Only the project manager manifest selects it.

When the user changes mode, load `sync-ml-reports` if installed
(that skill owns `skore sync` and the policy/init rewrite). This
skill only reruns `env add-skore --mode <new-mode> --execute` when
that parent asks for the destination extra. Do not migrate reports
here.
