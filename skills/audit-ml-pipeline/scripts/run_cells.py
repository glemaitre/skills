#!/usr/bin/env python
"""Shim around ``skore_skills.cells`` for skill installs without the wheel.

Prefer the installed package. If it is missing, run the vendored
``_run_cells_impl.py`` next to this file. Argv is unchanged:
``python run_cells.py <src.py> [<dst.md>]``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_main():
    """Return ``main`` from the package or the vendored fallback."""
    try:
        from skore_skills.cells import main as cells_main
    except ImportError:
        impl = Path(__file__).resolve().parent / "_run_cells_impl.py"
        spec = importlib.util.spec_from_file_location("_run_cells_impl", impl)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load cell runner from {impl}") from None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.main
    return cells_main


if __name__ == "__main__":
    raise SystemExit(_load_main()())
