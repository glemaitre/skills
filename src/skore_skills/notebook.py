"""Convert jupytext percent ``# %%`` files into executed notebooks."""

from __future__ import annotations

import os
from pathlib import Path

MISSING = "jupytext and nbclient are required; add them with add-python-package"
MISSING_NBCONVERT = "nbconvert is required; add it with add-python-package"
TEMPLATE_DIR = Path(__file__).with_name("site_assets")

try:
    import jupytext
    import nbformat
    from nbclient import NotebookClient
except ImportError:  # pragma: no cover - exercised by hiding modules in tests
    jupytext = None
    nbformat = None
    NotebookClient = None


def convert(src: Path, out: Path | None = None, *, html: bool = False) -> Path:
    """Read a percent-format ``.py``, execute it, and write ``.ipynb``.

    Parameters
    ----------
    src : pathlib.Path
        Jupytext percent-format source.
    out : pathlib.Path, optional
        Destination notebook. Defaults to the same stem next to ``src``.
    html : bool, optional
        When true, also write ``<stem>.nb.html`` next to ``src``.

    Returns
    -------
    pathlib.Path
        Path of the ``.ipynb`` written.

    Raises
    ------
    ImportError
        When jupytext, nbclient, or (if ``html``) nbconvert is not
        importable.
    FileNotFoundError
        When ``src`` is missing.
    """
    if jupytext is None or nbformat is None or NotebookClient is None:
        raise ImportError(MISSING)
    assert jupytext is not None
    assert nbformat is not None
    assert NotebookClient is not None
    if not src.is_file():
        raise FileNotFoundError(f"notebook source not found: {src}")
    dest = src.with_suffix(".ipynb") if out is None else out
    dest.parent.mkdir(parents=True, exist_ok=True)
    notebook = jupytext.read(src)
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": os.fspath(src.parent.resolve())}},
    )
    client.execute()
    nbformat.write(notebook, dest)
    if html:
        to_html(dest, src.with_name(f"{src.stem}.nb.html"))
    return dest


def to_html(src: Path, out: Path) -> Path:
    """Write a self-contained HTML rendering of an executed ``.ipynb``.

    Parameters
    ----------
    src : pathlib.Path
        Executed notebook.
    out : pathlib.Path
        Destination HTML file.

    Returns
    -------
    pathlib.Path
        Path written.

    Raises
    ------
    ImportError
        When nbconvert is not importable.
    FileNotFoundError
        When ``src`` is missing.
    """
    if not src.is_file():
        raise FileNotFoundError(f"notebook not found: {src}")
    try:
        from nbconvert import HTMLExporter
    except ImportError as exc:
        raise ImportError(MISSING_NBCONVERT) from exc
    exporter = HTMLExporter(
        template_name="lab",
        template_file=os.fspath(TEMPLATE_DIR / "skore_notebook.html.j2"),
    )
    exporter.embed_images = True
    body, _resources = exporter.from_filename(os.fspath(src))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    return out
