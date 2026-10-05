"""Launch a scenario workspace in Cursor, Claude Code, OpenCode, or Pi.

The adapters only build commands and a temporary Cursor instruction file.
They use each harness's existing authentication and do not install binaries.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

HARNESSES = ("cursor", "claude", "opencode", "pi")
INITIAL_PROMPT = (
    "Read SCENARIO.md and carry out that unattended journey. "
    "The choices in that file are already authorized. "
    "Stop if the workspace contradicts a choice instead of inventing another one."
)
CURSOR_INSTALL = (
    "cursor-agent is not installed. Install the Cursor Agent CLI from "
    "https://cursor.com/docs/cli. The cursor editor command cannot run this "
    "scenario."
)
CURSOR_MARKER = "<!-- integration-scenario-runner -->"
CURSOR_WRAPPER = (
    f"{CURSOR_MARKER}\n"
    "Follow `SCENARIO.md` in this workspace. Those choices are already authorized.\n"
)
EXIT_TIMEOUT = 124
EXIT_INTERRUPT = 130
EXIT_MISSING = 127
PI_DEFAULT_PROVIDER = "openrouter"
PI_DEFAULT_MODEL = "~deepseek/deepseek-flash-latest"
REPO_SRC = Path(__file__).resolve().parent.parent / "src"


class HarnessError(Exception):
    """A harness could not be launched."""

    def __init__(self, message: str, code: int = EXIT_MISSING) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PreparedLaunch:
    """One harness process and the files it temporarily owns."""

    argv: list[str]
    cwd: Path
    env: dict[str, str]
    cleanup: Callable[[], None]


def build_launch(
    harness: str,
    *,
    workspace: Path,
    driver: Path,
    interactive: bool,
    model: str | None,
    extra_args: list[str] | None = None,
    skill_paths: list[Path] | None = None,
) -> PreparedLaunch:
    """Return the command for ``harness`` without starting it."""
    if harness not in HARNESSES:
        known = ", ".join(HARNESSES)
        raise HarnessError(f"unknown harness {harness!r}; known: {known}", code=2)
    if not driver.is_file():
        raise HarnessError(f"scenario driver is missing: {driver}", code=1)
    executable = _require_executable(harness)
    prompt = INITIAL_PROMPT
    cleanup: Callable[[], None] = lambda: None
    extra_env: dict[str, str] = {}
    if harness == "claude":
        argv = [
            executable,
            "--append-system-prompt-file",
            str(driver),
            "--permission-mode",
            "auto",
        ]
        if not interactive:
            argv.extend(["-p", "--output-format", "stream-json"])
    elif harness == "opencode":
        argv = [executable, "run", "--auto", "--dir", str(workspace)]
        if interactive:
            argv.append("--interactive")
        else:
            argv.extend(["--format", "json"])
        extra_env["OPENCODE_CONFIG_CONTENT"] = json.dumps(
            {"instructions": [str(driver.resolve())]}
        )
    elif harness == "cursor":
        cleanup = install_cursor_instructions(workspace)
        argv = [executable, "--workspace", str(workspace), "--force"]
        if not interactive:
            argv.extend(["--print", "--output-format", "stream-json", "--trust"])
    else:
        argv = [
            executable,
            "--append-system-prompt",
            str(driver),
            "--approve",
        ]
        for path in skill_paths or []:
            argv.extend(["--skill", str(path)])
        if not interactive:
            argv.extend(["--mode", "json"])
    extra = list(extra_args or [])
    _append_model(argv, harness, model, extra)
    argv.extend(extra)
    argv.append(prompt)
    env = os.environ.copy()
    env.update(extra_env)
    current_pythonpath = env.get("PYTHONPATH")
    pythonpath = str(REPO_SRC)
    if current_pythonpath:
        pythonpath += os.pathsep + current_pythonpath
    env["PYTHONPATH"] = pythonpath
    return PreparedLaunch(argv=argv, cwd=workspace, env=env, cleanup=cleanup)


def _append_model(
    argv: list[str],
    harness: str,
    model: str | None,
    extra: list[str],
) -> None:
    """Add provider and model flags that ``extra`` did not already set."""
    if harness == "pi" and "--provider" not in extra:
        argv.extend(["--provider", PI_DEFAULT_PROVIDER])
    if "--model" in extra:
        return
    if model:
        argv.extend(["--model", model])
    elif harness == "pi":
        argv.extend(["--model", PI_DEFAULT_MODEL])


def install_cursor_instructions(workspace: Path) -> Callable[[], None]:
    """Write the runner's ``AGENTS.md`` wrapper and return its cleanup."""
    path = workspace / "AGENTS.md"
    if path.exists() and path.read_text(encoding="utf-8") != CURSOR_WRAPPER:
        raise HarnessError(
            f"{path} already exists; the runner will not overwrite it.",
            code=1,
        )
    path.write_text(CURSOR_WRAPPER, encoding="utf-8")

    def cleanup() -> None:
        if path.is_file() and path.read_text(encoding="utf-8") == CURSOR_WRAPPER:
            path.unlink()

    return cleanup


def _require_executable(harness: str) -> str:
    name = "cursor-agent" if harness == "cursor" else harness
    found = shutil.which(name)
    if found is not None:
        return found
    if harness == "cursor":
        raise HarnessError(CURSOR_INSTALL)
    raise HarnessError(f"{name} is not installed.")


def execute_launch(
    launch: PreparedLaunch,
    *,
    interactive: bool,
    timeout: float,
    stdout_path: Path,
    stderr_path: Path,
    popen: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    terminate: Callable[[int], None] | None = None,
) -> int:
    """Run ``launch`` until it exits, times out, or the user interrupts it."""
    if terminate is None:
        terminate = _terminate_process_group
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    spawned = _spawn_kwargs()
    try:
        if interactive:
            process = popen(
                launch.argv,
                cwd=launch.cwd,
                env=launch.env,
                text=True,
                **spawned,
            )
            return _wait(process, timeout=timeout, terminate=terminate)
        with stdout_path.open("w", encoding="utf-8") as stdout_file:
            with stderr_path.open("w", encoding="utf-8") as stderr_file:
                process = popen(
                    launch.argv,
                    cwd=launch.cwd,
                    env=launch.env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **spawned,
                )
                threads = (
                    _stream(process.stdout, stdout_file, sys.stdout),
                    _stream(process.stderr, stderr_file, sys.stderr),
                )
                status = _wait(process, timeout=timeout, terminate=terminate)
                for thread in threads:
                    thread.join()
                return status
    finally:
        launch.cleanup()


def _spawn_kwargs() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _stream(source: IO[str] | None, sink: IO[str], echo: IO[str]) -> threading.Thread:
    def copy() -> None:
        if source is None:
            return
        while True:
            line = source.readline()
            if line == "":
                break
            sink.write(line)
            sink.flush()
            echo.write(line)
            echo.flush()

    thread = threading.Thread(target=copy)
    thread.start()
    return thread


def _wait(
    process: subprocess.Popen[str],
    *,
    timeout: float,
    terminate: Callable[[int], None],
) -> int:
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate(process.pid)
        _reap(process)
        return EXIT_TIMEOUT
    except KeyboardInterrupt:
        terminate(process.pid)
        _reap(process)
        return EXIT_INTERRUPT


def _reap(process: subprocess.Popen[str]) -> None:
    try:
        process.wait(timeout=1)
    except (subprocess.TimeoutExpired, OSError):
        return


def _terminate_process_group(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return
