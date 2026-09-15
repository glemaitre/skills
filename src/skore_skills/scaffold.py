"""Copy organize-ml-workspace templates into a project tree."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

ALREADY_SCAFFOLDED = (
    "refusing to overwrite an existing layout; pass --force to replace files"
)
INVALID_PACKAGE = "package name must be a Python identifier (snake_case)"
MISSING_TEMPLATE = "packaged scaffold templates are missing"

SRC_TEMPLATES = {
    "src___init__.py": "__init__.py",
    "src_data.py": "data.py",
    "src_features.py": "features.py",
    "src_pipeline.py": "pipeline.py",
    "src_evaluate.py": "evaluate.py",
}


def template_root() -> Path:
    """Return the packaged copy of organize-ml-workspace templates."""
    return Path(str(files("skore_skills").joinpath("templates")))


def render_template(text: str, package: str, *, pyproject: bool = False) -> str:
    """Substitute ``<pkg>`` and related placeholders."""
    kebab = package.replace("_", "-")
    if pyproject:
        text = text.replace('name = "<pkg>"', f'name = "{kebab}"')
    return (
        text.replace("<pkg>", package)
        .replace("<SKORE_PROJECT_INIT>", "")
        .replace("<project-name>", kebab)
        .replace("<experiment-key>", "01_baseline")
        .replace("<short title>", "baseline")
    )


def layout_exists(root: Path) -> bool:
    """Return True if a scaffolded layout is already present."""
    return (
        (root / "src").exists()
        or (root / "pyproject.toml").is_file()
        or (root / "experiments").exists()
    )


def scaffold(root: Path, package: str, *, force: bool = False) -> list[Path]:
    """Write the template tree under ``root``.

    Parameters
    ----------
    root : pathlib.Path
        Destination workspace.
    package : str
        Snake-case import name (``src/<package>/``).
    force : bool, optional
        Replace files when a layout already exists.

    Returns
    -------
    list of pathlib.Path
        Paths written, relative to ``root``.

    Raises
    ------
    ValueError
        Invalid package name, existing layout without ``force``, or
        missing packaged templates.
    """
    if not package.isidentifier():
        raise ValueError(INVALID_PACKAGE)
    if layout_exists(root) and not force:
        raise ValueError(ALREADY_SCAFFOLDED)
    templates = template_root()
    if not templates.is_dir():
        raise ValueError(MISSING_TEMPLATE)

    written: list[Path] = []

    def write(rel: Path, body: str) -> None:
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        written.append(rel)

    for src_name, dest_name in SRC_TEMPLATES.items():
        raw = (templates / src_name).read_text(encoding="utf-8")
        write(Path("src") / package / dest_name, render_template(raw, package))

    for name, dest in (
        ("pyproject.toml", Path("pyproject.toml")),
        (".gitignore", Path(".gitignore")),
        ("experiment.py", Path("experiments") / "01_baseline.py"),
    ):
        raw = (templates / name).read_text(encoding="utf-8")
        write(dest, render_template(raw, package, pyproject=name == "pyproject.toml"))

    ruff = files("skore_skills").joinpath("data/ruff.toml")
    write(Path("ruff.toml"), ruff.read_text(encoding="utf-8"))
    write(Path("journal") / "JOURNAL.md", "# Journal\n")
    return written
