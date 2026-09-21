"""Command-line interface for ``skore_skills``."""

from __future__ import annotations

import os
from pathlib import Path

import click

from skore_skills import __version__
from skore_skills.api import get_symbol, package_version
from skore_skills.check import render_workspace_check
from skore_skills.model_choices import render_model_choices
from skore_skills.status import render_status


def _reexec_library_command(argv: list[str]) -> None:
    """Enter the composed project env for in-process library commands."""
    from skore_skills.env import reexec_in_dev

    code = reexec_in_dev(Path.cwd(), argv=argv)
    if code is not None:
        raise SystemExit(code)


@click.group()
@click.version_option(version=__version__, prog_name="skore-skills")
def cli() -> None:
    """Deterministic helpers for Probabl ML skills.

    Invoke as ``python -m skore_skills``.
    """


@cli.group("cells")
def cells_group() -> None:
    """Execute jupytext percent-format ``# %%`` files."""


@cells_group.command("run")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument(
    "dst",
    type=click.Path(dir_okay=False, path_type=Path),
    required=False,
)
def cells_run(src: Path, dst: Path | None) -> None:
    """Stream a markdown digest of each cell to stdout.

    When ``DST`` is given, also write the digest to that path.
    """
    from skore_skills.cells import run

    forwarded = ["cells", "run", os.fspath(src)]
    if dst is not None:
        forwarded.append(os.fspath(dst))
    _reexec_library_command(forwarded)
    run(src, dst)


@cli.group("notebook")
def notebook_group() -> None:
    """Convert percent-format ``# %%`` files into executed notebooks."""


@notebook_group.command("convert")
@click.argument("src", type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Destination .ipynb (default: same stem next to SRC).",
)
@click.option(
    "--html",
    is_flag=True,
    help="Also write <stem>.nb.html next to SRC.",
)
def notebook_convert(src: Path, out: Path | None, html: bool) -> None:
    """Execute SRC with nbclient and write an .ipynb with outputs."""
    from skore_skills.notebook import convert

    forwarded = ["notebook", "convert", os.fspath(src)]
    if out is not None:
        forwarded.extend(["--out", os.fspath(out)])
    if html:
        forwarded.append("--html")
    _reexec_library_command(forwarded)
    try:
        dest = convert(src, out, html=html)
    except (ImportError, FileNotFoundError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(str(dest))


@cli.group("site")
def site_group() -> None:
    """Initialize and build an offline MkDocs documentation site."""


@site_group.command("init")
@click.option(
    "--force",
    is_flag=True,
    help="Accepted for compatibility; init only updates .gitignore.",
)
def site_init(force: bool) -> None:
    """Ignore _build/ and html/. Does not write a user mkdocs.yml."""
    from skore_skills.site import init_site

    forwarded = ["site", "init"]
    if force:
        forwarded.append("--force")
    _reexec_library_command(forwarded)
    try:
        dest = init_site(Path.cwd(), force=force)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(str(dest))


@site_group.command("build")
def site_build() -> None:
    """Package Markdown and existing companions into ``html/``."""
    from skore_skills.site import build_site

    _reexec_library_command(["site", "build"])
    try:
        click.echo(build_site(Path.cwd()))
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.group("api")
def api_group() -> None:
    """Look up public symbols in the running interpreter."""


@api_group.command("get")
@click.argument("symbol")
def api_get(symbol: str) -> None:
    """Print a signature card and cache it under ``scratch/api/``."""
    _reexec_library_command(["api", "get", symbol])
    try:
        click.echo(get_symbol(symbol), nl=False)
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc
    except LookupError as exc:
        raise click.ClickException(str(exc)) from exc


@api_group.command("version")
@click.argument("package")
def api_version(package: str) -> None:
    """Print the installed version of ``PACKAGE``."""
    _reexec_library_command(["api", "version", package])
    try:
        click.echo(package_version(package))
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("status")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    show_default=True,
)
def status_cmd(fmt: str) -> None:
    """Print a read-only JSON snapshot of the current workspace."""
    click.echo(render_status(Path.cwd(), fmt.lower()), nl=False)


@cli.group("model")
def model_group() -> None:
    """Inspect deterministic model-workflow choices."""


@model_group.command("choices")
def model_choices_cmd() -> None:
    """Print the available model-entry choices as JSON."""
    click.echo(render_model_choices(Path.cwd()), nl=False)


@cli.group("check")
def check_group() -> None:
    """Yes/no checks over workspace facts."""


@check_group.command("workspace")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    show_default=True,
)
def check_workspace(fmt: str) -> None:
    """Exit 1 if the tree is not scaffolded (no ``src/`` and no ``journal/``)."""
    text, code = render_workspace_check(Path.cwd(), fmt.lower())
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@cli.command("scaffold")
@click.option(
    "--package", "package_name", help="Snake-case import name for a full scaffold."
)
@click.option(
    "--journal",
    is_flag=True,
    help="Initialize JOURNAL.md instead of the full workspace.",
)
@click.option(
    "--stem",
    help="With --journal, also create journal/NN_short_name.md.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite files owned by the selected scaffold mode.",
)
def scaffold_cmd(
    package_name: str | None,
    journal: bool,
    stem: str | None,
    force: bool,
) -> None:
    """Copy full-workspace or journal templates into the current directory."""
    from skore_skills.scaffold import scaffold, scaffold_journal

    if (package_name is None) == (not journal):
        raise click.UsageError("choose exactly one of --package or --journal")
    if stem is not None and not journal:
        raise click.UsageError("--stem requires --journal")

    try:
        if journal:
            written = scaffold_journal(Path.cwd(), stem=stem, force=force)
        else:
            assert package_name is not None
            written = scaffold(Path.cwd(), package_name, force=force)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    for path in written:
        click.echo(str(path))


@cli.command("style")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(path_type=Path),
)
@click.option(
    "--init",
    "initialize",
    is_flag=True,
    help="Write [tool.ruff] into pyproject.toml when it is missing.",
)
def style_cmd(paths: tuple[Path, ...], initialize: bool) -> None:
    """Run ruff check --fix then format on defaults or PATHS.

    Default globs: ``src/``, ``experiments/``, ``audit/``, ``data_analysis/``,
    top-level ``*.py``. ``--init`` without PATHS only writes ``[tool.ruff]``.
    """
    from skore_skills.style import initialize_style, run_style

    forwarded = ["style"]
    if initialize:
        forwarded.append("--init")
    forwarded.extend(os.fspath(path) for path in paths)
    _reexec_library_command(forwarded)
    if initialize:
        created = initialize_style(Path.cwd())
        click.echo(
            "wrote [tool.ruff] in pyproject.toml"
            if created
            else "ruff already configured"
        )
        if not paths:
            return

    def warn(message: str) -> None:
        click.echo(message, err=True)

    try:
        code = run_style(Path.cwd(), paths, warn=warn)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    if code:
        raise SystemExit(code)


@cli.group("env")
def env_group() -> None:
    """Detect the env manager and print install commands."""


@env_group.command("detect")
def env_detect() -> None:
    """Print JSON evidence; exit non-zero when two managers are visible."""
    import json

    from skore_skills.env import detect

    payload = detect(Path.cwd())
    click.echo(json.dumps(payload, indent=2))
    if payload["ambiguous"]:
        raise SystemExit(1)


@env_group.command("add")
@click.argument("packages", nargs=-1, required=False)
@click.option(
    "--execute",
    is_flag=True,
    help="Run the install command instead of printing it.",
)
@click.option(
    "--feature",
    "--group",
    "feature",
    help="Manager feature/group (pixi --feature, uv/poetry --group).",
)
@click.option(
    "--editable",
    is_flag=True,
    help="Editable install of the workspace package (src/).",
)
def env_add(
    packages: tuple[str, ...],
    execute: bool,
    feature: str | None,
    editable: bool,
) -> None:
    """Print (or run) the manager-specific add command."""
    from skore_skills.env import add_packages

    text, code = add_packages(
        Path.cwd(),
        list(packages),
        execute=execute,
        feature=feature,
        editable=editable,
    )
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("add-skore")
@click.option(
    "--mode",
    required=True,
    type=click.Choice(["local", "hub", "mlflow"], case_sensitive=True),
)
@click.option(
    "--execute",
    is_flag=True,
    help="Run the install command instead of printing it.",
)
def env_add_skore(mode: str, execute: bool) -> None:
    """Print or run the manager-aware Skore install command."""
    from skore_skills.env import add_skore

    text, code = add_skore(Path.cwd(), mode, execute=execute)
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("sync")
@click.option(
    "--execute",
    is_flag=True,
    help="Run the sync command instead of printing it.",
)
def env_sync(execute: bool) -> None:
    """Print (or run) the post-init install/sync command."""
    from skore_skills.env import sync_environment

    text, code = sync_environment(Path.cwd(), execute=execute)
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("route")
@click.argument("package")
def env_route(package: str) -> None:
    """Print JSON scope for a package (default, agent, ask, or refuse)."""
    import json

    from skore_skills.env import route_package

    payload = route_package(package)
    if payload["scope"] == "refuse":
        click.echo(payload["message"])
        raise SystemExit(1)
    click.echo(json.dumps(payload, indent=2))


@env_group.command("graphviz")
@click.option(
    "--execute",
    is_flag=True,
    help="Install conda Graphviz when possible and run dot -c.",
)
def env_graphviz(execute: bool) -> None:
    """Print JSON for Graphviz; optionally install and rebuild the plugin cache."""
    from skore_skills.env import ensure_graphviz

    text, code = ensure_graphviz(Path.cwd(), execute=execute)
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("verify")
@click.argument("packages", nargs=-1, required=False)
@click.option(
    "--execute",
    is_flag=True,
    help="Run the import check instead of printing JSON only.",
)
def env_verify(packages: tuple[str, ...], execute: bool) -> None:
    """Print (or run) an agent-env import check."""
    import json

    from skore_skills.env import verify_environment

    payload, code = verify_environment(
        Path.cwd(), list(packages) if packages else None, execute=execute
    )
    click.echo(json.dumps(payload, indent=2))
    if code:
        raise SystemExit(code)


@env_group.command("init")
@click.option(
    "--manager",
    required=True,
    type=click.Choice(
        ["pixi", "uv", "poetry", "hatch", "conda", "pip-venv"],
        case_sensitive=True,
    ),
)
@click.option(
    "--force",
    is_flag=True,
    help="Replace conda environment files if they already exist.",
)
def env_init(manager: str, force: bool) -> None:
    """Write manager and agent tables into pyproject.toml (or conda YAML)."""
    from skore_skills.env import init_environment

    text, code = init_environment(Path.cwd(), manager, force=force)
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@cli.group("policy")
def policy_group() -> None:
    """Read and write the ``workspace`` section of ``.skore``."""


@policy_group.command("set")
@click.argument("key")
@click.argument("value")
def policy_set(key: str, value: str) -> None:
    """Set one dotted workspace policy key and print the section JSON."""
    import json

    from skore_skills.policy import set_policy_value

    try:
        payload = set_policy_value(Path.cwd(), key, value)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(payload, indent=2))


@cli.group("git")
def git_group() -> None:
    """Merge ignore rules and print the end-of-turn persist hook."""


@git_group.command("ignore-merge")
@click.option(
    "--keep",
    "keep_paths",
    multiple=True,
    help="Force-track a hidden path after the user decides to keep it.",
)
@click.option(
    "--decide",
    is_flag=True,
    help="Record this as the hidden-path answer: --keep tracked, the rest ignored.",
)
def git_ignore_merge_cmd(keep_paths: tuple[str, ...], decide: bool) -> None:
    """Union packaged ignore rules into ``.gitignore``. No git commands."""
    from skore_skills.git import render_git_json, run_ignore_merge

    try:
        payload, code = run_ignore_merge(Path.cwd(), keep=keep_paths, decide=decide)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(render_git_json(payload), nl=False)
    if code:
        raise SystemExit(code)


@git_group.command("end-turn")
@click.option(
    "--stage",
    required=True,
    type=click.Choice(
        ["setup", "data_analysis", "implement", "evaluate", "backlog"],
        case_sensitive=True,
    ),
    help="Loop stage that just finished.",
)
def git_end_turn_cmd(stage: str) -> None:
    """Print whether to load ``persist-ml-git``. Never commits."""
    from skore_skills.git import render_git_json, run_end_turn

    try:
        payload, code = run_end_turn(Path.cwd(), stage)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(render_git_json(payload), nl=False)
    if code:
        raise SystemExit(code)


def main() -> None:
    """Run the CLI (``python -m skore_skills`` / console script)."""
    cli()
