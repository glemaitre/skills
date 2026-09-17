# Skore package source and mode

Do not construct a Skore requirement in a skill. After
G-SKORE-MODE is persisted, run:

```bash
python -m skore_skills env add-skore --mode <local|hub|mlflow> --execute
```

The CLI selects the package source from the manifest-detected
manager:

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

When the user changes mode, reconfirm the migration and rerun
`env add-skore --mode <new-mode> --execute`. Existing reports remain
on their prior backend until manually migrated.
