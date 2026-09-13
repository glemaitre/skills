"""Command-line interface for ``skore_skills``."""

from __future__ import annotations

import click

from skore_skills import __version__


@click.group()
@click.version_option(version=__version__, prog_name="skore-skills")
def cli() -> None:
    """Deterministic helpers for Probabl ML skills.

    Subcommands land in later releases. Invoke as ``python -m skore_skills``.
    """


def main() -> None:
    """Run the CLI (``python -m skore_skills`` / console script)."""
    cli()
