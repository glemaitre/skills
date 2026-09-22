"""Tests for ``skore_skills site init`` and ``site build``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills import site as site_mod
from skore_skills.cli import cli
from skore_skills.policy import empty_policy, save_policy


def _scaffold(tmp_path: Path, *, package: str = "claim_predictor") -> None:
    (tmp_path / "journal").mkdir()
    (tmp_path / "journal" / "JOURNAL.md").write_text(
        "# JOURNAL\n\n[report](../data_analysis/data_analysis.md)\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "{package}"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )


def test_site_title_uses_package_then_folder(tmp_path: Path) -> None:
    """Site title prefers ``[project].name``, then ``src/``, then the folder."""
    (tmp_path / "src").mkdir()
    assert site_mod.site_title(tmp_path) == tmp_path.name
    (tmp_path / "src" / "churnlab").mkdir()
    assert site_mod.site_title(tmp_path) == "churnlab"
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "claim_predictor"\n', encoding="utf-8"
    )
    assert site_mod.site_title(tmp_path) == "claim_predictor"


def _ok_mkdocs(tmp_path: Path):
    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(argv: list[str], **kwargs: object) -> Result:
        out = tmp_path / "html"
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text("<html></html>\n", encoding="utf-8")
        return Result()

    return fake_run


def test_site_init_writes_gitignore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Init ignores build dirs and does not write a user mkdocs.yml."""
    _scaffold(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "init"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "_build/" in text
    assert "html/" in text
    assert "claim_predictor.html" in text
    assert not (tmp_path / "mkdocs.yml").exists()


def test_site_init_force_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--force`` is accepted and does not write root mkdocs.yml."""
    (tmp_path / "src").mkdir()
    (tmp_path / "mkdocs.yml").write_text("hand-written\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "init", "--force"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "mkdocs.yml").read_text(encoding="utf-8") == "hand-written\n"


def test_site_init_refuses_unscaffolded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty trees cannot init a site."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "init"])
    assert result.exit_code != 0
    assert "not scaffolded" in result.output


def test_site_build_runs_mkdocs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Build stages docs then invokes mkdocs with the generated config."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# eda\n", encoding="utf-8"
    )
    (tmp_path / "mkdocs.yml").write_text("hand-written\n", encoding="utf-8")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> object:
        seen.append(list(argv))
        return _ok_mkdocs(tmp_path)(argv)

    monkeypatch.setattr(site_mod.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    assert seen == [
        ["mkdocs", "build", "--config-file", site_mod.GENERATED_CONFIG.as_posix()]
    ]
    assert (tmp_path / "mkdocs.yml").read_text(encoding="utf-8") == "hand-written\n"
    generated = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert 'site_name: "claim_predictor"' in generated
    assert "index.md" in generated
    assert "Home: index.md" in generated
    assert "font: false" in generated
    assert "assets/skore/skore.css" in generated
    assert "assets/skore/skore.js" in generated
    assert "assets/skore/iframe-worker.js" in generated
    assert generated.index("assets/skore/nav-data.js") < generated.index(
        "assets/skore/skore.js"
    )
    assert (tmp_path / "_build" / "docs" / "index.md").is_file()
    assets = tmp_path / "_build" / "docs" / "assets" / "skore"
    assert (assets / "skore.css").is_file()
    assert (assets / "skore.js").is_file()
    assert (assets / "nav-data.js").is_file()
    assert (assets / "skore-text.svg").is_file()
    assert (assets / "iframe-worker.js").is_file()
    assert (assets / "iframe-worker.LICENSE").is_file()
    assert (assets / "fonts" / "GeistVF.woff2").is_file()
    icons = assets / "icons"
    assert (icons / "square-caret-left-regular.svg").is_file()
    assert (icons / "square-caret-right-regular.svg").is_file()
    assert (icons / "FONT-AWESOME-NOTICE.txt").is_file()
    journal = (tmp_path / "_build" / "docs" / "index.md").read_text(encoding="utf-8")
    assert "](data_analysis.md)" in journal
    index = tmp_path / "html" / "index.html"
    assert index.is_file()
    launcher = tmp_path / "claim_predictor.html"
    assert launcher.is_file()
    assert "url=html/index.html" in launcher.read_text(encoding="utf-8")
    assert str(launcher) in result.output
    assert "claim_predictor.html" in (tmp_path / ".gitignore").read_text(
        encoding="utf-8"
    )


def test_site_build_groups_experiments_and_writes_top_nav(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Experiments form one ordered dropdown in desktop and mobile nav."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# eda\n", encoding="utf-8"
    )
    for name in ("01_baseline.md", "02_tuning.md"):
        (tmp_path / "journal" / name).write_text(f"# {name}\n", encoding="utf-8")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    generated = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert (
        "  - Experiments:\n"
        "      - 01_baseline: 01_baseline.md\n"
        "      - 02_tuning: 02_tuning.md\n"
    ) in generated
    script = (
        tmp_path / "_build" / "docs" / "assets" / "skore" / "nav-data.js"
    ).read_text(encoding="utf-8")
    payload = script.removeprefix("window.__SKORE_NAV__ = ").removesuffix(";\n")
    assert json.loads(payload) == [
        {"label": "Home", "href": "index.html"},
        {"label": "Exploratory data analysis", "href": "data_analysis.html"},
        {
            "label": "Experiments",
            "children": [
                {"label": "01_baseline", "href": "01_baseline.html"},
                {"label": "02_tuning", "href": "02_tuning.html"},
            ],
        },
    ]


def test_site_theme_has_trainhard_layout_contract() -> None:
    """Packaged CSS and JS keep the desktop shell accessibility contract."""
    css = (site_mod.SITE_ASSETS / "skore.css").read_text(encoding="utf-8")
    javascript = (site_mod.SITE_ASSETS / "skore.js").read_text(encoding="utf-8")
    assert "--skore-content-max: 1200px" in css
    assert "--skore-toc-width: 256px" in css
    assert "--skore-toc-rail-width: var(--numbers-48)" in css
    assert "font-size: 18px" in css
    assert (".md-typeset table:not([class]) {\n  font-size: inherit;\n") in css
    assert "max-height: calc(5 * var(--numbers-40))" in css
    assert "grid-template-columns: var(--skore-toc-width)" in css
    assert ".md-sidebar--secondary .md-nav__title {\n    display: none;" in css
    assert 'trigger.setAttribute("aria-haspopup", "menu")' in javascript
    assert 'button.setAttribute("aria-controls", sidebar.id)' in javascript
    assert 'document.createElement("img")' in javascript
    assert "button.append(icon, label)" in javascript
    assert "square-caret-left-regular.svg" in javascript
    assert "square-caret-right-regular.svg" in javascript
    assert 'event.key !== "Escape"' in javascript


def test_site_theme_uses_hub_sizing_scale() -> None:
    """Chrome sizing comes from the skore-hub ``--numbers-*`` scale."""
    css = (site_mod.SITE_ASSETS / "skore.css").read_text(encoding="utf-8")
    for token, value in (
        ("--numbers-4", "0.25rem"),
        ("--numbers-8", "0.5rem"),
        ("--numbers-12", "0.75rem"),
        ("--numbers-14", "0.875rem"),
        ("--numbers-40", "2.5rem"),
        ("--numbers-48", "3rem"),
        ("--numbers-56", "3.5rem"),
    ):
        assert f"{token}: {value};" in css
    assert "--stroke-width-md: 1px" in css
    assert "height: var(--numbers-40)" in css
    assert "border-radius: var(--numbers-8)" in css
    assert "border-radius: var(--numbers-12)" in css


def test_site_theme_flattens_and_numbers_contents() -> None:
    """Contents rows sit flush and collapse into numbered tiles."""
    css = (site_mod.SITE_ASSETS / "skore.css").read_text(encoding="utf-8")
    javascript = (site_mod.SITE_ASSETS / "skore.js").read_text(encoding="utf-8")
    assert "[dir] .md-sidebar--secondary .md-nav__list" in css
    assert "[dir] .md-sidebar--secondary .md-nav__item > .md-nav__link" in css
    assert "counter-reset: skore-toc" in css
    assert "counter-increment: skore-toc" in css
    # Numbers share the collapse icon's box and gap so the two columns line up.
    assert (
        ".md-sidebar--secondary .md-nav__link::before {\n"
        "    flex: 0 0 var(--numbers-20);\n"
        "    content: counter(skore-toc);"
    ) in css
    assert "flex: 0 0 var(--numbers-20);\n  opacity: 0.8;" in css
    assert "body.skore-toc-collapsed .skore-toc-label {\n    display: none;" in css
    assert "width: var(--numbers-40)" in css
    # Rows, tiles, and the collapse control all keep the compact row height.
    assert "min-height: var(--numbers-28)" in css
    assert "height: var(--numbers-28)" in css
    assert "heading-solid" not in css
    # The panel hugs its rows so the collapse control follows the last one.
    assert "flex: 0 1 auto" in css
    assert (
        "body.skore-toc-collapsed .md-sidebar--secondary .md-nav__item {\n"
        "    display: flex;\n"
        "    justify-content: center;"
    ) in css
    assert (
        "body.skore-toc-collapsed .skore-toc-footer {\n    padding: var(--numbers-6) 0;"
        in css
    )
    assert 'label.className = "skore-toc-label"' in javascript
    assert "link.title = label.textContent" in javascript


def test_site_theme_uses_trainhard_motion() -> None:
    """Transitions reuse trainhard timings and stay off until first paint."""
    css = (site_mod.SITE_ASSETS / "skore.css").read_text(encoding="utf-8")
    javascript = (site_mod.SITE_ASSETS / "skore.js").read_text(encoding="utf-8")
    assert "--skore-collapse-duration: 0.2s" in css
    assert "--skore-collapse-easing: ease-in-out" in css
    assert "--skore-hover-duration: 0.12s" in css
    assert "--skore-menu-duration: 0.15s" in css
    assert "transition: grid-template-columns var(--skore-collapse-duration)" in css
    assert "transform: translateY(-0.35rem)" in css
    assert "transform: rotate(180deg)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "display: none" not in css.split(".skore-topnav__menu {")[1].split("}")[0]
    assert 'classList.add("skore-motion-ready")' in javascript
    assert 'caret.className = "skore-topnav__caret"' in javascript


def test_site_build_mkdocs_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing mkdocs executable is a clear error."""
    _scaffold(tmp_path)

    def fake_run(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("mkdocs")

    monkeypatch.setattr(site_mod.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code != 0
    assert "mkdocs-material" in result.output


def test_site_build_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-zero mkdocs build is reported."""
    (tmp_path / "src").mkdir()

    class Result:
        returncode = 1
        stdout = ""
        stderr = "nav error\n"

    monkeypatch.setattr(site_mod.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code != 0
    assert "nav error" in result.output


def test_site_build_copies_data_analysis_html(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TableReport HTML next to data_analysis.md is copied into the staged docs."""
    (tmp_path / "src").mkdir()
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# report\n", encoding="utf-8"
    )
    (tmp_path / "data_analysis" / "data_analysis_adult.html").write_text(
        "<html><body>report</body></html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    staged = (tmp_path / "_build" / "docs" / "data_analysis_adult.html").read_text(
        encoding="utf-8"
    )
    assert "skore-embed-height" in staged
    assert staged.index("skore-embed-height") < staged.index("</body>")


def test_with_height_reporter_without_body() -> None:
    """A report fragment with no ``</body>`` still gets the reporter."""
    reported = site_mod.with_height_reporter("<table>rows</table>\n")
    assert reported.startswith("<table>rows</table>\n")
    assert "skore-embed-height" in reported


def test_site_build_autosizes_report_but_not_notebook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Report viewers fit their content; notebook viewers keep the fixed height."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        '<iframe src="data_analysis_adult.html" width="100%" height="640"></iframe>\n',
        encoding="utf-8",
    )
    (tmp_path / "data_analysis" / "data_analysis_adult.html").write_text(
        "<html><body>report</body></html>\n", encoding="utf-8"
    )
    (tmp_path / "data_analysis" / "data_analysis.nb.html").write_text(
        "<html><body>notebook</body></html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    staged = (docs / "data_analysis.md").read_text(encoding="utf-8")
    assert (
        '<iframe src="data_analysis_adult.html" title="Interactive report" '
        'loading="lazy" data-skore-autosize>' in staged
    )
    notebook_tag = staged[staged.index('<iframe src="data_analysis.nb.html"') :]
    notebook_tag = notebook_tag[: notebook_tag.index(">") + 1]
    assert "data-skore-autosize" not in notebook_tag
    assert (docs / "data_analysis.nb.html").read_text(encoding="utf-8") == (
        "<html><body>notebook</body></html>\n"
    )


def test_site_build_missing_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A successful mkdocs process without index.html is still an error."""
    (tmp_path / "journal").mkdir()

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(site_mod.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code != 0
    assert "index.html" in result.output
    assert not (tmp_path / f"{tmp_path.name}.html").exists()


def test_site_build_does_not_convert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Site build never executes paired scripts, even if notebooks are on."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# eda\n", encoding="utf-8"
    )
    (tmp_path / "data_analysis" / "data_analysis.py").write_text(
        "# %%\n1\n", encoding="utf-8"
    )
    policy = empty_policy()
    policy["notebooks"] = True
    save_policy(tmp_path, policy)
    called: list[str] = []

    def fake_convert(*args: object, **kwargs: object) -> Path:
        called.append("convert")
        raise AssertionError("site build must not convert")

    monkeypatch.setattr(site_mod, "convert", fake_convert, raising=False)
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    assert called == []
    staged = (tmp_path / "_build" / "docs" / "data_analysis.md").read_text(
        encoding="utf-8"
    )
    assert "## Notebook" not in staged
    assert not (tmp_path / "_build" / "docs" / "data_analysis.py").exists()
    assert not (tmp_path / "_build" / "docs" / "data_analysis.nb.html").exists()


def test_site_build_embeds_notebook_in_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """data_analysis.nb.html becomes a viewer in data_analysis.md, not a nav page."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# report\n", encoding="utf-8"
    )
    (tmp_path / "data_analysis" / "data_analysis.nb.html").write_text(
        "<html>notebook</html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    assert (docs / "data_analysis.nb.html").read_text(encoding="utf-8") == (
        "<html>notebook</html>\n"
    )
    staged = (docs / "data_analysis.md").read_text(encoding="utf-8")
    assert "## Notebook" in staged
    assert '<iframe src="data_analysis.nb.html"' in staged
    assert "data-skore-fullscreen" in staged
    assert "Open separately" in staged
    nav = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Exploratory data analysis notebook" not in nav


def test_site_build_pairs_experiment_notebook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """journal/NN.md embeds experiments/NN.nb.html when it exists."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text("# design\n", encoding="utf-8")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "01_x.nb.html").write_text(
        "<html>run</html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    assert (docs / "01_x.nb.html").is_file()
    assert '<iframe src="01_x.nb.html"' in (docs / "01_x.md").read_text(
        encoding="utf-8"
    )
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert staged.count("## Notebooks") == 1
    assert "### Evaluation notebook" in staged
    assert "### Audit notebook" not in staged
    nav = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert "01_x notebook" not in nav


def test_site_build_appends_audit_after_experiment_notebook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """audit/NN.nb.html continues the experiment notebook on the same page."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text("# design\n", encoding="utf-8")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "01_x.nb.html").write_text(
        "<html>run</html>\n", encoding="utf-8"
    )
    (tmp_path / "audit").mkdir()
    (tmp_path / "audit" / "01_x.nb.html").write_text(
        "<html>audit</html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    assert (docs / "01_x.audit.nb.html").read_text(encoding="utf-8") == (
        "<html>audit</html>\n"
    )
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert staged.index('<iframe src="01_x.nb.html"') < staged.index(
        '<iframe src="01_x.audit.nb.html"'
    )
    assert staged.count("## Notebooks") == 1
    assert staged.index("### Evaluation notebook") < staged.index("### Audit notebook")
    nav = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert "01_x audit" not in nav


def test_site_build_without_audit_has_no_audit_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No ``audit/NN.nb.html`` leaves the experiment page unchanged."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text("# design\n", encoding="utf-8")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "01_x.nb.html").write_text(
        "<html>run</html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    assert not (docs / "01_x.audit.nb.html").exists()
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert "### Audit notebook" not in staged


def test_site_build_audit_without_experiment_notebook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An audit notebook is embedded even when the experiment has none."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text("# design\n", encoding="utf-8")
    (tmp_path / "audit").mkdir()
    (tmp_path / "audit" / "01_x.nb.html").write_text(
        "<html>audit</html>\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert '<iframe src="01_x.audit.nb.html"' in staged
    assert staged.count("## Notebooks") == 1
    assert "### Evaluation notebook" not in staged
    assert "### Audit notebook" in staged


def test_inject_notebooks_reuses_authored_section_and_is_idempotent(
    tmp_path: Path,
) -> None:
    """Authored notebook placeholders become one generated viewer section."""
    experiment = tmp_path / "01_x.nb.html"
    audit = tmp_path / "01_x.audit.nb.html"
    experiment.write_text("<html>run</html>\n", encoding="utf-8")
    audit.write_text("<html>audit</html>\n", encoding="utf-8")
    page = site_mod.Page(
        "01_x",
        tmp_path / "01_x.md",
        "01_x.md",
        experiment,
        "Experiments",
        audit,
    )
    source = (
        "# design\n\n## Notebooks\n\n### Evaluation notebook\n\n### Audit notebook\n"
    )

    once = site_mod.inject_notebook(source, page)
    twice = site_mod.inject_notebook(once, page)

    assert twice == once
    assert once.count("## Notebooks") == 1
    assert once.count("### Evaluation notebook") == 1
    assert once.count("### Audit notebook") == 1
    assert once.index("### Evaluation notebook") < once.index("### Audit notebook")


def test_inject_results_appends_embeds_after_prose_and_is_idempotent(
    tmp_path: Path,
) -> None:
    """Authored Results prose is kept; viewers are inserted once."""
    stem = "01_x"
    results = tmp_path / "scratch" / "results" / stem
    results.mkdir(parents=True)
    (results / "report.html").write_text("<html>report</html>\n", encoding="utf-8")
    (results / "checks.html").write_text("<html>checks</html>\n", encoding="utf-8")
    (results / "metrics.html").write_text("<html>metrics</html>\n", encoding="utf-8")
    page = site_mod.Page(
        stem,
        tmp_path / f"{stem}.md",
        f"{stem}.md",
        None,
        "Experiments",
        None,
    )
    source = (
        "# design\n\n## Results\n\n"
        "### Report overview\n\nThe CV report for Ridge.\n\n"
        "### Checks\n\nOne issue (SKD003).\n\n"
        "### Metrics\n\nMAE 3421.\n\n"
        "## Notebooks\n"
    )

    once = site_mod.inject_results(source, page, tmp_path)
    twice = site_mod.inject_results(once, page, tmp_path)

    assert twice == once
    assert "The CV report for Ridge." in once
    assert "One issue (SKD003)." in once
    assert "MAE 3421." in once
    assert once.index("The CV report for Ridge.") < once.index(
        '<iframe src="01_x.report.html"'
    )
    assert once.index("### Checks") < once.index("### Metrics")
    assert once.count('<iframe src="01_x.report.html"') == 1
    assert "data-skore-autosize" in once


def test_inject_results_skips_missing_section_and_missing_html(
    tmp_path: Path,
) -> None:
    """No Results heading stays unchanged; missing HTML leaves prose."""
    page = site_mod.Page(
        "01_x",
        tmp_path / "01_x.md",
        "01_x.md",
        None,
        "Experiments",
        None,
    )
    no_section = "# design\n\n## Notebooks\n"
    assert site_mod.inject_results(no_section, page, tmp_path) == no_section

    (tmp_path / "scratch" / "results" / "01_x").mkdir(parents=True)
    (tmp_path / "scratch" / "results" / "01_x" / "report.html").write_text(
        "<html>report</html>\n", encoding="utf-8"
    )
    source = (
        "# design\n\n## Results\n\n"
        "### Report overview\n\nThe CV report.\n\n"
        "### Checks\n\nOne issue.\n\n"
        "## Notebooks\n"
    )
    injected = site_mod.inject_results(source, page, tmp_path)
    assert '<iframe src="01_x.report.html"' in injected
    assert '<iframe src="01_x.checks.html"' not in injected
    assert "One issue." in injected


def test_inject_results_embeds_pipeline_under_method(tmp_path: Path) -> None:
    """Method ``results-embed: pipeline`` gets the construct-time snapshot."""
    stem = "01_x"
    results = tmp_path / "scratch" / "results" / stem
    results.mkdir(parents=True)
    (results / "pipeline.html").write_text("<html>pipeline</html>\n", encoding="utf-8")
    page = site_mod.Page(
        stem,
        tmp_path / f"{stem}.md",
        f"{stem}.md",
        None,
        "Experiments",
        None,
    )
    source = (
        "# design\n\n## Method\n\n"
        "Ridge on the skrub graph.\n"
        "<!-- results-embed: pipeline -->\n\n"
        "## Risks\n\nLeakage.\n"
    )
    once = site_mod.inject_results(source, page, tmp_path)
    twice = site_mod.inject_results(once, page, tmp_path)
    assert twice == once
    assert "Ridge on the skrub graph." in once
    assert once.index("Ridge on the skrub graph.") < once.index(
        '<iframe src="01_x.pipeline.html"'
    )
    assert once.count('<iframe src="01_x.pipeline.html"') == 1
    assert "data-skore-autosize" in once
    assert "## Risks" in once


def test_inject_results_skips_method_without_pipeline_marker(
    tmp_path: Path,
) -> None:
    """A pipeline.html file is not injected into Method without the marker."""
    stem = "01_x"
    results = tmp_path / "scratch" / "results" / stem
    results.mkdir(parents=True)
    (results / "pipeline.html").write_text("<html>pipeline</html>\n", encoding="utf-8")
    page = site_mod.Page(
        stem,
        tmp_path / f"{stem}.md",
        f"{stem}.md",
        None,
        "Experiments",
        None,
    )
    source = "# design\n\n## Method\n\nRidge.\n\n## Risks\n\nLeakage.\n"
    assert site_mod.inject_results(source, page, tmp_path) == source


def test_inject_results_embeds_extra_slug_from_comment(
    tmp_path: Path,
) -> None:
    """Extra Display HTML lands after the results-embed marker."""
    stem = "01_x"
    results = tmp_path / "scratch" / "results" / stem
    results.mkdir(parents=True)
    (results / "roc.html").write_text("<html>roc</html>\n", encoding="utf-8")
    page = site_mod.Page(
        stem,
        tmp_path / f"{stem}.md",
        f"{stem}.md",
        None,
        "Experiments",
        None,
    )
    source = (
        "# design\n\n## Results\n\n"
        "### Report overview\n\nThe CV report.\n\n"
        "### ROC curve\n<!-- results-embed: roc -->\n\n"
        "Fold 3 is weak.\n\n"
        "## Notebooks\n"
    )
    once = site_mod.inject_results(source, page, tmp_path)
    twice = site_mod.inject_results(once, page, tmp_path)
    assert twice == once
    assert "Fold 3 is weak." in once
    assert once.index("Fold 3 is weak.") < once.index('<iframe src="01_x.roc.html"')
    assert once.count('<iframe src="01_x.roc.html"') == 1
    assert "data-skore-autosize" in once


def test_inject_results_embeds_extra_slug_png(
    tmp_path: Path,
) -> None:
    """A matplotlib-style Display snapshot becomes a markdown image."""
    stem = "01_x"
    results = tmp_path / "scratch" / "results" / stem
    results.mkdir(parents=True)
    (results / "prediction_error.png").write_bytes(b"png")
    page = site_mod.Page(
        stem,
        tmp_path / f"{stem}.md",
        f"{stem}.md",
        None,
        "Experiments",
        None,
    )
    source = (
        "# design\n\n## Results\n\n"
        "### Prediction error\n<!-- results-embed: prediction_error -->\n\n"
        "Residuals fan out.\n\n"
        "## Notebooks\n"
    )
    injected = site_mod.inject_results(source, page, tmp_path)
    assert "![01_x prediction_error](01_x.prediction_error.png)" in injected
    assert injected.index("Residuals fan out.") < injected.index(
        "01_x.prediction_error.png"
    )


def test_inject_results_copies_unmarked_slug_without_injecting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scratch HTML without a results-embed comment is not injected."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text(
        "# design\n\n## Results\n\n"
        "### Report overview\n\nRidge CV report.\n\n"
        "## Notebooks\n",
        encoding="utf-8",
    )
    results = tmp_path / "scratch" / "results" / "01_x"
    results.mkdir(parents=True)
    (results / "report.html").write_text("<html>report</html>\n", encoding="utf-8")
    (results / "roc.html").write_text("<html>roc</html>\n", encoding="utf-8")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert '<iframe src="01_x.report.html"' in staged
    assert '<iframe src="01_x.roc.html"' not in staged
    assert (docs / "01_x.roc.html").is_file()


def test_site_build_embeds_eval_only_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Evaluation snapshots embed under Report overview only."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text(
        "# design\n\n## Results\n\n"
        "### Report overview\n\nRidge CV report.\n\n"
        "## Notebooks\n",
        encoding="utf-8",
    )
    results = tmp_path / "scratch" / "results" / "01_x"
    results.mkdir(parents=True)
    (results / "report.html").write_text("<html>report</html>\n", encoding="utf-8")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    docs = tmp_path / "_build" / "docs"
    staged = (docs / "01_x.md").read_text(encoding="utf-8")
    assert "Ridge CV report." in staged
    assert '<iframe src="01_x.report.html"' in staged
    assert "### Checks" not in staged
    assert "### Metrics" not in staged
    copied = (docs / "01_x.report.html").read_text(encoding="utf-8")
    assert "<html>report</html>" in copied
    assert "skore-embed-height" in copied


def test_site_build_embeds_audit_results_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Checks then metrics follow the report overview embed."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text(
        "# design\n\n## Results\n\n"
        "### Report overview\n\nRidge CV report.\n\n"
        "### Checks\n\nOne issue (SKD003).\n\n"
        "### Metrics\n\nMAE 3421.\n\n"
        "## Notebooks\n",
        encoding="utf-8",
    )
    results = tmp_path / "scratch" / "results" / "01_x"
    results.mkdir(parents=True)
    (results / "report.html").write_text("<html>report</html>\n", encoding="utf-8")
    (results / "checks.html").write_text("<html>checks</html>\n", encoding="utf-8")
    (results / "metrics.html").write_text("<html>metrics</html>\n", encoding="utf-8")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    staged = (tmp_path / "_build" / "docs" / "01_x.md").read_text(encoding="utf-8")
    assert staged.index("### Report overview") < staged.index("### Checks")
    assert staged.index("### Checks") < staged.index("### Metrics")
    assert staged.index("One issue (SKD003).") < staged.index(
        '<iframe src="01_x.checks.html"'
    )
    assert staged.index('<iframe src="01_x.checks.html"') < staged.index(
        '<iframe src="01_x.metrics.html"'
    )


def test_site_build_without_results_section_skips_scratch_html(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Template notes without Results do not gain a Results heading."""
    _scaffold(tmp_path)
    (tmp_path / "journal" / "01_x.md").write_text(
        "# design\n\n## Notebooks\n", encoding="utf-8"
    )
    results = tmp_path / "scratch" / "results" / "01_x"
    results.mkdir(parents=True)
    (results / "report.html").write_text("<html>report</html>\n", encoding="utf-8")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    staged = (tmp_path / "_build" / "docs" / "01_x.md").read_text(encoding="utf-8")
    assert "## Results" not in staged
    assert '<iframe src="01_x.report.html"' not in staged
    assert (tmp_path / "_build" / "docs" / "01_x.report.html").is_file()


def test_site_build_embeds_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Figures render inline and each report HTML gets one iframe."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "- Report: [data_analysis_adult.html](data_analysis_adult.html)\n"
        "- Views: [spatial](plot.png) - [again](plot.png)\n",
        encoding="utf-8",
    )
    (tmp_path / "data_analysis" / "data_analysis_adult.html").write_text(
        "<html></html>\n", encoding="utf-8"
    )
    (tmp_path / "data_analysis" / "plot.png").write_bytes(b"png")
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    staged = (tmp_path / "_build" / "docs" / "data_analysis.md").read_text(
        encoding="utf-8"
    )
    assert "![spatial](plot.png)" in staged
    assert "![again](plot.png)" in staged
    assert staged.count('<iframe src="data_analysis_adult.html"') == 1
    assert "[data_analysis_adult.html](data_analysis_adult.html)" in staged
    assert 'class="skore-embed"' in staged


def test_site_build_keeps_authored_iframe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An authored iframe is upgraded to one styled viewer."""
    _scaffold(tmp_path)
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        '<iframe src="data_analysis_adult.html" width="100%" height="640"></iframe>\n\n'
        "[Open the report](data_analysis_adult.html)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    staged = (tmp_path / "_build" / "docs" / "data_analysis.md").read_text(
        encoding="utf-8"
    )
    assert staged.count('src="data_analysis_adult.html"') == 1
    assert 'class="skore-embed"' in staged


def test_site_build_stub_index_in_nav(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When JOURNAL is missing, stub index.md is listed in nav."""
    (tmp_path / "src").mkdir()
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# eda\n", encoding="utf-8"
    )
    monkeypatch.setattr(site_mod.subprocess, "run", _ok_mkdocs(tmp_path))
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code == 0, result.output
    nav = (tmp_path / "_build" / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Home: index.md" in nav
    assert "Exploratory data analysis: data_analysis.md" in nav
    assert (tmp_path / "_build" / "docs" / "index.md").is_file()


def test_site_build_unscaffolded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty trees cannot build a site."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["site", "build"])
    assert result.exit_code != 0
    assert "not scaffolded" in result.output
