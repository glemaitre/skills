"""Tests for ``skore_skills env detect`` / ``env add``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.env import install_argv, load_stack_policy

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "envs"


@pytest.mark.parametrize(
    ("name", "manager"),
    [
        ("pixi", "pixi"),
        ("uv", "uv"),
        ("poetry", "poetry"),
        ("hatch", "hatch"),
        ("conda", "conda"),
        ("pip-venv", "pip-venv"),
        ("none", "none"),
    ],
)
def test_env_detect_each_manager(
    name: str, manager: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each fixture maps to the documented manager (or none)."""
    monkeypatch.chdir(FIXTURES / name)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == manager
    assert payload["ambiguous"] is False
    assert payload["mismatch"] is False


def test_env_detect_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    """pixi.toml + conda env is ambiguous: JSON flag and non-zero exit."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ambiguous"] is True
    assert payload["env_manager"] is None
    assert payload["managers"] == ["pixi", "conda"]


def test_env_add_pixi_never_pip(monkeypatch: pytest.MonkeyPatch) -> None:
    """``env add`` on a pixi fixture prints ``pixi add``, never ``pip install``."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pixi add skrub"
    assert "pip install" not in result.output


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("uv", "uv add pandas"),
        ("poetry", "poetry add pandas"),
        ("conda", "conda install -c conda-forge pandas"),
        ("pip-venv", "pip install pandas"),
    ],
)
def test_env_add_command_per_manager(
    fixture: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Print-only add matches the env-manager command table."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_add_hatch_prints_edit_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hatch has no add command; print an edit hint and never pip."""
    monkeypatch.chdir(FIXTURES / "hatch")
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert "edit pyproject.toml" in result.output
    assert "pip install" not in result.output
    executed = CliRunner().invoke(cli, ["env", "add", "--execute", "pandas"])
    assert executed.exit_code != 0
    assert "pip install" not in executed.output


def test_env_add_forbidden_substitute(monkeypatch: pytest.MonkeyPatch) -> None:
    """Known substitutes are refused using python-stack.json."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "xgboost"])
    assert result.exit_code != 0
    assert "HistGradientBoosting" in result.output
    policy = load_stack_policy()
    assert "xgboost" in policy["forbidden_substitutes"]
    assert "ruff" in policy["mandatory"]


def test_env_add_ambiguous_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not install into an ambiguous workspace."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "multiple env managers" in result.output


def test_env_add_none_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nothing detected: do not invent pip."""
    monkeypatch.chdir(FIXTURES / "none")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "no env manager" in result.output
    assert "pip install" not in result.output


def test_env_add_requires_package() -> None:
    """``env add`` without packages is usage error."""
    result = CliRunner().invoke(cli, ["env", "add"])
    assert result.exit_code != 0


def test_env_add_execute_runs_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``--execute`` runs the printed command."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--execute", "skrub"])
    assert result.exit_code == 0, result.output
    assert seen == [["pixi", "add", "skrub"]]
    assert result.output.strip() == "pixi add skrub"


def test_install_argv_unknown_manager() -> None:
    """Unknown manager names are a programming error."""
    with pytest.raises(ValueError, match="unknown manager"):
        install_argv("pants", ["x"])


def test_add_packages_empty_list(tmp_path: Path) -> None:
    """Library callers still get a usage error for an empty package list."""
    from skore_skills.env import add_packages

    text, code = add_packages(tmp_path, [])
    assert code == 2
    assert "at least one package" in text


def test_env_add_feature_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """``--feature`` / ``--group`` map onto pixi and uv/poetry flags."""
    monkeypatch.chdir(FIXTURES / "pixi")
    pixi = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "ruff"])
    assert pixi.exit_code == 0, pixi.output
    assert pixi.output.strip() == "pixi add --feature agent ruff"
    monkeypatch.chdir(FIXTURES / "uv")
    uv = CliRunner().invoke(cli, ["env", "add", "--group", "agent", "ruff"])
    assert uv.exit_code == 0, uv.output
    assert uv.output.strip() == "uv add --group agent ruff"


def test_env_add_refuses_when_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """User-managed workspaces never emit an install command."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "user-managed" in result.output
    assert "pixi add" not in result.output


def test_env_detect_recommended_uses_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recorded ``env_manager`` leads the recommended list when none is visible."""
    from skore_skills.policy import empty_policy, save_policy

    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.env.shutil.which", lambda *_a, **_k: None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "uv"
    assert payload["mismatch"] is False
    assert payload["managed"] is None


def _write_fake_skore(tmp_path: Path, *parts: str) -> Path:
    path = tmp_path.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    path.chmod(0o755)
    return path


def _patch_which(monkeypatch: pytest.MonkeyPatch, binary: Path | None) -> None:
    def which(name: str, path: str | None = None) -> str | None:
        if binary is not None and name in {"skore", "skore-cli"}:
            return str(binary)
        return None

    monkeypatch.setattr("skore_skills.env.shutil.which", which)


def test_env_detect_provenance_uv_when_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty root ranks ``uv`` from the ``skore`` install prefix."""
    binary = _write_fake_skore(tmp_path, "uv", "tools", "skore-cli", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "uv"
    assert payload["provenance"]["manager"] == "uv"
    assert payload["mismatch"] is False


def test_env_detect_default_when_no_skore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty root with no ``skore`` on PATH keeps the packaged default."""
    monkeypatch.chdir(tmp_path)
    _patch_which(monkeypatch, None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "pixi"
    assert payload["provenance"] == {"manager": None, "path": None}


def test_env_detect_policy_beats_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recorded policy ranks above a pixi-looking ``skore`` prefix."""
    from skore_skills.policy import empty_policy, save_policy

    binary = _write_fake_skore(tmp_path, ".pixi", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(root, policy)
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recommended"][0] == "uv"
    assert payload["provenance"]["manager"] == "pixi"
    assert payload["mismatch"] is False


def test_env_detect_manifest_beats_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A unique manifest wins over ``skore`` provenance."""
    binary = _write_fake_skore(tmp_path, "uv", "tools", "skore-cli", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    (root / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert payload["recommended"] == ["pixi"]
    assert payload["provenance"]["manager"] == "uv"
    assert payload["mismatch"] is False


def test_env_detect_policy_manifest_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Policy vs a different unique manifest is mismatch, not ambiguous."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    _patch_which(monkeypatch, None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert payload["ambiguous"] is False
    assert payload["mismatch"] is True
    assert payload["recommended"][0] == "uv"


def test_env_detect_ignores_pipx_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pipx ``skore`` install is too weak to rank a project manager."""
    binary = _write_fake_skore(
        tmp_path, ".local", "pipx", "venvs", "skore-cli", "bin", "skore"
    )
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recommended"][0] == "pixi"
    assert payload["provenance"]["manager"] is None
    assert payload["provenance"]["path"] == str(binary.resolve())


def test_env_detect_pixi_from_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``[tool.pixi]`` in pyproject.toml is pixi evidence."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pixi.workspace]\nchannels = ["conda-forge"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert "pyproject.toml:[tool.pixi]" in payload["evidence"]["pixi"]


def test_env_init_pixi_writes_agent_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pixi init merges ``[tool.pixi]`` and agent packages into pyproject."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pixi" in text
    assert "ipykernel" in text
    assert "ipython" in text
    assert "[tool.ruff]" in text
    assert not (tmp_path / "pixi.toml").exists()
    assert not (tmp_path / "src").exists()
    second = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert second.exit_code != 0
    assert "already present" in second.output


def test_env_init_uv_writes_dependency_groups(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """uv init writes PEP 735 agent groups."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "uv"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.uv]" in text
    assert "ipykernel" in text


def test_env_init_refuses_manager_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--manager`` must match an already-detected manager."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "uv"])
    assert result.exit_code != 0
    assert "does not match" in result.output


def test_env_init_refuses_pixi_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Refuse to add ``[tool.pixi]`` when ``pixi.toml`` already exists."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code != 0
    assert "pixi.toml already exists" in result.output


def test_env_init_refuses_when_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Init is skipped when the user opted out of env management."""
    from skore_skills.policy import empty_policy, save_policy

    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code != 0
    assert "user-managed" in result.output


def test_env_init_conda_writes_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Conda init writes sidecar YAML, not pyproject manager tables."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "conda"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "environment.yml").is_file()
    agent = (tmp_path / "environment-agent.yml").read_text(encoding="utf-8")
    assert "ipykernel" in agent
    assert "ipython" in agent
    second = CliRunner().invoke(cli, ["env", "init", "--manager", "conda"])
    assert second.exit_code != 0


def test_env_init_requires_manager() -> None:
    """``env init`` without ``--manager`` is a usage error."""
    result = CliRunner().invoke(cli, ["env", "init"])
    assert result.exit_code != 0


def test_env_init_unknown_manager_library(tmp_path: Path) -> None:
    """Library callers still reject unknown manager names."""
    from skore_skills.env import init_environment

    text, code = init_environment(tmp_path, "pants")
    assert code == 2
    assert "unknown manager" in text


def test_env_agent_removed() -> None:
    """LSP agent install is no longer a CLI command."""
    result = CliRunner().invoke(cli, ["env", "agent"])
    assert result.exit_code != 0
    result_check = CliRunner().invoke(cli, ["env", "check"])
    assert result_check.exit_code != 0
