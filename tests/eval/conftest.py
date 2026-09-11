from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.eval.harness import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_PASS_RATIO,
    DEFAULT_TARGET_MODEL,
    EVAL_RESULTS,
    case_node_id,
    ensure_transcript_dirs,
    load_eval_cases,
    new_run_id,
)

VALID_MODES = ("with", "without", "both")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("skill_eval", "Skill evaluations (DeepEval)")
    group.addoption(
        "--skill-model",
        action="append",
        default=None,
        help=(
            "Target model under test (LiteLLM name, repeatable). "
            "Overrides SKILL_EVAL_MODELS. "
            f"Default: {DEFAULT_TARGET_MODEL}."
        ),
    )
    group.addoption(
        "--skill-judge-model",
        default=None,
        help=(
            "Judge model for GEval (LiteLLM name). "
            "Overrides SKILL_EVAL_JUDGE_MODEL. "
            f"Default: {DEFAULT_JUDGE_MODEL}."
        ),
    )
    group.addoption(
        "--skill-mode",
        default=None,
        choices=VALID_MODES,
        help=(
            "with: SKILL.md as system prompt; without: empty system; "
            "both: parametrise each case. Overrides SKILL_EVAL_MODE."
        ),
    )
    group.addoption(
        "--skill-pass-ratio",
        default=None,
        help=(
            "Must-do GEval threshold in [0, 1]. Must-NOT stays all-or-nothing. "
            "Overrides SKILL_EVAL_PASS_RATIO. "
            f"Default: {DEFAULT_PASS_RATIO}."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
    os.environ.setdefault("DEEPEVAL_UPDATE_WARNING_OPT_OUT", "YES")
    config.addinivalue_line(
        "markers",
        "eval: LLM-backed skill evaluations (opt-in; requires provider API keys)",
    )
    _load_dotenv(config)
    EVAL_RESULTS.clear()
    ensure_transcript_dirs()


@pytest.fixture(scope="session")
def eval_run_id() -> str:
    return new_run_id()


def _load_dotenv(config: pytest.Config) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(str(config.rootpath)) / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _target_models(config: pytest.Config) -> list[str]:
    cli = config.getoption("--skill-model")
    if cli:
        return list(cli)
    env = os.environ.get("SKILL_EVAL_MODELS", "").strip()
    if env:
        return [part.strip() for part in env.split(",") if part.strip()]
    return [DEFAULT_TARGET_MODEL]


def _judge_model(config: pytest.Config) -> str:
    cli = config.getoption("--skill-judge-model")
    if cli:
        return str(cli)
    return os.environ.get("SKILL_EVAL_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)


def _modes(config: pytest.Config) -> list[str]:
    raw = config.getoption("--skill-mode") or os.environ.get(
        "SKILL_EVAL_MODE", "with"
    )
    if raw not in VALID_MODES:
        raise pytest.UsageError(
            f"skill mode must be one of {VALID_MODES}, got {raw!r}"
        )
    return ["with", "without"] if raw == "both" else [raw]


def _pass_ratio(config: pytest.Config) -> float:
    raw = config.getoption("--skill-pass-ratio")
    if raw is None:
        raw = os.environ.get("SKILL_EVAL_PASS_RATIO", DEFAULT_PASS_RATIO)
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise pytest.UsageError(
            f"skill pass ratio must be a float in [0, 1], got {raw!r}"
        ) from exc
    if not 0.0 <= value <= 1.0:
        raise pytest.UsageError(
            f"skill pass ratio must be in [0, 1], got {value}"
        )
    return value


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "eval_case" not in metafunc.fixturenames:
        return
    cases = load_eval_cases()
    models = _target_models(metafunc.config)
    modes = _modes(metafunc.config)
    params = [
        (case, model, mode)
        for case in cases
        for model in models
        for mode in modes
    ]
    metafunc.parametrize(
        "eval_case,target_model,skill_mode",
        params,
        ids=[
            case_node_id(case, mode=mode, model=model)
            for case, model, mode in params
        ],
    )


@pytest.fixture(scope="session")
def skill_judge_model(pytestconfig: pytest.Config) -> str:
    return _judge_model(pytestconfig)


@pytest.fixture(scope="session")
def skill_pass_ratio(pytestconfig: pytest.Config) -> float:
    return _pass_ratio(pytestconfig)


def pytest_terminal_summary(
    terminalreporter, exitstatus: int, config: pytest.Config
) -> None:
    if not EVAL_RESULTS:
        return
    terminalreporter.write_sep("=", "skill-eval summary")
    counts: dict[str, tuple[int, int]] = {}
    for mode, rows in EVAL_RESULTS.items():
        passed = sum(1 for _, _, _, ok in rows if ok)
        total = len(rows)
        counts[mode] = (passed, total)
        pct = (100 * passed / total) if total else 0
        terminalreporter.write_line(f"  {mode:<8s} {passed}/{total} ({pct:.0f}%)")
    if "with" in counts and "without" in counts:
        with_p, with_t = counts["with"]
        without_p, without_t = counts["without"]
        if with_t and without_t:
            delta_pp = (with_p / with_t - without_p / without_t) * 100
            terminalreporter.write_line(f"  delta    {delta_pp:+.0f}pp")
    failed = [
        (mode, skill, case_id, title)
        for mode, rows in EVAL_RESULTS.items()
        for skill, case_id, title, ok in rows
        if not ok
    ]
    if failed:
        terminalreporter.write_line("  failed:")
        for mode, skill, case_id, title in failed:
            suffix = f" — {title}" if title else ""
            terminalreporter.write_line(
                f"    [{mode}] {skill} case {case_id}{suffix}"
            )
