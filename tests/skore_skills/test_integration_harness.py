"""Fake-harness tests for the integration scenario runner."""

from __future__ import annotations

import json
import os
import stat
import sys
from contextlib import suppress
from pathlib import Path

import pytest

from tools import integration_harness, integration_scenario
from tools.integration_harness import (
    CURSOR_WRAPPER,
    EXIT_INTERRUPT,
    EXIT_MISSING,
    EXIT_TIMEOUT,
    INITIAL_PROMPT,
    PI_DEFAULT_MODEL,
    PI_DEFAULT_PROVIDER,
    HarnessError,
    PreparedLaunch,
    _wait,
    build_launch,
    execute_launch,
)
from tools.integration_scenario import ensure_workspace, materialize, run_scenario


def _driver(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "SCENARIO.md"
    path.write_text("authorized choices\n", encoding="utf-8")
    return path


def _fake_which(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        integration_harness.shutil,
        "which",
        lambda name: f"/fake/{name}",
    )


def _launch(
    harness: str,
    directory: Path,
    *,
    interactive: bool,
    model: str | None,
    extra_args: list[str] | None = None,
):
    return build_launch(
        harness,
        workspace=directory,
        driver=_driver(directory),
        interactive=interactive,
        model=model,
        extra_args=extra_args,
    )


def test_claude_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_which(monkeypatch)
    headless = _launch("claude", tmp_path, interactive=False, model="sonnet")
    assert headless.argv == [
        "/fake/claude",
        "--append-system-prompt-file",
        str(tmp_path / "SCENARIO.md"),
        "--permission-mode",
        "auto",
        "-p",
        "--output-format",
        "stream-json",
        "--model",
        "sonnet",
        INITIAL_PROMPT,
    ]
    interactive = _launch("claude", tmp_path / "tty", interactive=True, model=None)
    assert "-p" not in interactive.argv
    assert interactive.argv[-1] == INITIAL_PROMPT


def test_opencode_command_and_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    launch = _launch("opencode", tmp_path, interactive=False, model=None)
    assert launch.argv[:5] == [
        "/fake/opencode",
        "run",
        "--auto",
        "--dir",
        str(tmp_path),
    ]
    assert "--format" in launch.argv
    assert "--interactive" not in launch.argv
    instructions = json.loads(launch.env["OPENCODE_CONFIG_CONTENT"])
    assert instructions == {"instructions": [str((tmp_path / "SCENARIO.md").resolve())]}
    shown = _launch("opencode", tmp_path / "tty", interactive=True, model="m")
    assert "--interactive" in shown.argv
    assert "--model" in shown.argv


def test_cursor_and_pi_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    cursor = _launch("cursor", tmp_path, interactive=False, model=None)
    assert cursor.argv[:6] == [
        "/fake/cursor-agent",
        "--workspace",
        str(tmp_path),
        "--force",
        "--print",
        "--output-format",
    ]
    assert "--trust" in cursor.argv
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == CURSOR_WRAPPER
    shown = _launch("cursor", tmp_path / "tty", interactive=True, model=None)
    assert "--print" not in shown.argv
    pi = _launch("pi", tmp_path / "pi", interactive=False, model="pair")
    assert pi.argv[:4] == [
        "/fake/pi",
        "--append-system-prompt",
        str(tmp_path / "pi" / "SCENARIO.md"),
        "--approve",
    ]
    assert pi.argv[4:6] == ["--mode", "json"]
    assert "--print" not in pi.argv
    assert pi.argv[pi.argv.index("--provider") + 1] == PI_DEFAULT_PROVIDER
    assert pi.argv[pi.argv.index("--model") + 1] == "pair"
    assert PI_DEFAULT_MODEL not in pi.argv


def test_pi_defaults_and_harness_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    default = _launch("pi", tmp_path / "default", interactive=True, model=None)
    assert default.argv[default.argv.index("--provider") + 1] == PI_DEFAULT_PROVIDER
    assert default.argv[default.argv.index("--model") + 1] == PI_DEFAULT_MODEL
    overridden = _launch(
        "pi",
        tmp_path / "extra",
        interactive=False,
        model=None,
        extra_args=["--provider", "other", "--model", "custom", "--thinking", "high"],
    )
    assert overridden.argv.count("--provider") == 1
    assert overridden.argv.count("--model") == 1
    assert overridden.argv[overridden.argv.index("--provider") + 1] == "other"
    assert overridden.argv[overridden.argv.index("--model") + 1] == "custom"
    assert "--thinking" in overridden.argv
    assert overridden.argv[-1] == INITIAL_PROMPT


def test_missing_executables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(integration_harness.shutil, "which", lambda _name: None)
    with pytest.raises(HarnessError, match="cursor-agent is not installed") as missing:
        _launch("cursor", tmp_path, interactive=False, model=None)
    assert missing.value.code == EXIT_MISSING
    with pytest.raises(HarnessError, match="pi is not installed"):
        _launch("pi", tmp_path / "pi", interactive=True, model=None)


def test_cursor_refuses_existing_instructions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    (tmp_path / "AGENTS.md").write_text("user instructions\n", encoding="utf-8")
    with pytest.raises(HarnessError, match="will not overwrite"):
        _launch("cursor", tmp_path, interactive=False, model=None)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "user instructions\n"


def test_cursor_wrapper_is_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    launch = _launch("cursor", tmp_path, interactive=True, model=None)

    def popen(*_args, **_kwargs):
        return _Ready()

    status = execute_launch(
        launch,
        interactive=True,
        timeout=5,
        stdout_path=tmp_path / "logs" / "stdout.txt",
        stderr_path=tmp_path / "logs" / "stderr.txt",
        popen=popen,
    )
    assert status == 0
    assert not (tmp_path / "AGENTS.md").exists()


def test_cleanup_runs_when_launch_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_which(monkeypatch)
    launch = _launch("cursor", tmp_path, interactive=False, model=None)

    def popen(*_args, **_kwargs):
        raise OSError("not launched")

    with pytest.raises(OSError, match="not launched"):
        execute_launch(
            launch,
            interactive=False,
            timeout=5,
            stdout_path=tmp_path / "logs" / "stdout.txt",
            stderr_path=tmp_path / "logs" / "stderr.txt",
            popen=popen,
        )
    assert not (tmp_path / "AGENTS.md").exists()


def test_headless_streams_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    launch = PreparedLaunch(
        argv=[
            sys.executable,
            "-c",
            "import sys; print('hello-out'); print('hello-err', file=sys.stderr)",
        ],
        cwd=tmp_path,
        env=os.environ.copy(),
        cleanup=lambda: None,
    )
    stdout_path = tmp_path / "logs" / "stdout.txt"
    stderr_path = tmp_path / "logs" / "stderr.txt"
    status = execute_launch(
        launch,
        interactive=False,
        timeout=5,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
    captured = capsys.readouterr()
    assert status == 0
    assert stdout_path.read_text(encoding="utf-8") == "hello-out\n"
    assert stderr_path.read_text(encoding="utf-8") == "hello-err\n"
    assert "hello-out" in captured.out
    assert "hello-err" in captured.err


def test_timeout_kills_the_process_group(tmp_path: Path) -> None:
    pids: list[int] = []

    def popen(argv, **kwargs):
        import subprocess

        process = subprocess.Popen(argv, **kwargs)
        pids.append(process.pid)
        return process

    launch = PreparedLaunch(
        argv=[sys.executable, "-c", "import time; time.sleep(60)"],
        cwd=tmp_path,
        env=os.environ.copy(),
        cleanup=lambda: None,
    )
    try:
        status = execute_launch(
            launch,
            interactive=False,
            timeout=0.2,
            stdout_path=tmp_path / "logs" / "stdout.txt",
            stderr_path=tmp_path / "logs" / "stderr.txt",
            popen=popen,
        )
        assert status == EXIT_TIMEOUT
        with pytest.raises(OSError):
            os.kill(pids[0], 0)
    finally:
        for pid in pids:
            with suppress(OSError):
                os.kill(pid, 9)


def test_interrupt_returns_130() -> None:
    killed: list[int] = []

    class _Stop(_Ready):
        def wait(self, timeout: float | None = None) -> int:
            self.calls += 1
            if self.calls == 1:
                raise KeyboardInterrupt
            return 0

    status = _wait(_Stop(), timeout=5, terminate=killed.append)
    assert status == EXIT_INTERRUPT
    assert killed == [7]


def test_materialize_copies_driver(tmp_path: Path) -> None:
    dest = tmp_path / "housing"
    materialize("california-housing", dest, force=False)
    text = (dest / "SCENARIO.md").read_text(encoding="utf-8")
    assert "California housing" in text
    assert "{{SKILLS_REPO}}" not in text
    assert "{{SKILLS_REPO_URI}}" not in text
    repo = integration_scenario.REPO_ROOT.resolve()
    assert str(repo) in text
    assert repo.as_uri() in text
    assert (dest / "DATA.md").is_file()


def test_reuse_workspace_rules(tmp_path: Path) -> None:
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("keep\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="reuse-workspace"):
        ensure_workspace("california-housing", occupied, reuse=False)
    ensure_workspace("california-housing", occupied, reuse=True)
    assert (occupied / "keep.txt").is_file()
    assert (occupied / "SCENARIO.md").is_file()
    assert not (occupied / "DATA.md").exists()


def test_run_records_check_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _script(tmp_path / "bin" / "claude", code=0)
    monkeypatch.setenv("PATH", f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(integration_scenario, "REPO_ROOT", tmp_path)
    workspace = tmp_path / "housing"
    status = run_scenario(
        "california-housing",
        harness="claude",
        workspace=workspace,
        interactive=False,
        model=None,
        timeout=5,
        reuse=False,
    )
    result = _result(tmp_path)
    assert status == 1
    assert result["exit_status"] == 1
    assert result["harness"] == "claude"
    assert result["mode"] == "headless"
    assert result["check_errors"]
    assert (workspace / "SCENARIO.md").is_file()


def test_run_skips_check_when_harness_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = tmp_path / "record.txt"
    _script(tmp_path / "bin" / "pi", code=3, record=record)
    monkeypatch.setenv("PATH", f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(integration_scenario, "REPO_ROOT", tmp_path)
    status = run_scenario(
        "california-housing",
        harness="pi",
        workspace=tmp_path / "housing",
        interactive=False,
        model=None,
        timeout=5,
        reuse=False,
    )
    result = _result(tmp_path)
    recorded = record.read_text(encoding="utf-8")
    assert status == 3
    assert result["check_errors"] == []
    assert "--approve" in recorded
    assert "--mode" in recorded
    assert "json" in recorded


def test_run_reports_missing_cursor_agent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setattr(integration_scenario, "REPO_ROOT", tmp_path)
    status = run_scenario(
        "california-housing",
        harness="cursor",
        workspace=tmp_path / "housing",
        interactive=False,
        model=None,
        timeout=5,
        reuse=False,
    )
    result = _result(tmp_path)
    assert status == EXIT_MISSING
    assert result["exit_status"] == EXIT_MISSING
    assert not (tmp_path / "housing" / "AGENTS.md").exists()


def test_run_refuses_nonempty_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "housing"
    workspace.mkdir()
    (workspace / "keep.txt").write_text("keep\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="reuse-workspace"):
        run_scenario(
            "california-housing",
            harness="claude",
            workspace=workspace,
            interactive=False,
            model=None,
            timeout=5,
            reuse=False,
        )


class _Ready:
    def __init__(self) -> None:
        self.pid = 7
        self.calls = 0

    def wait(self, timeout: float | None = None) -> int:
        self.calls += 1
        return 0


def _script(path: Path, *, code: int, record: Path | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["import sys", "from pathlib import Path"]
    if record is not None:
        lines.append(
            f"Path({str(record)!r}).write_text('\\n'.join(sys.argv[1:]) + '\\n')"
        )
    lines.append(f"raise SystemExit({code})")
    program = "\n".join(lines) + "\n"
    if os.name == "nt":
        source = path.with_suffix(".py")
        source.write_text(program, encoding="utf-8")
        path.with_suffix(".cmd").write_text(
            f'@echo off\r\n"{sys.executable}" "{source}" %*\r\n',
            encoding="utf-8",
        )
        return
    path.write_text(f"#!{sys.executable}\n{program}", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _result(root: Path) -> dict[str, object]:
    paths = list((root / ".transcripts").rglob("result.json"))
    assert len(paths) == 1
    return json.loads(paths[0].read_text(encoding="utf-8"))
