from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import pytest

from .client import ClientError, call_model
from .judge import JudgeResult, judge_expectations

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_JUDGE_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_MODE = "with"
VALID_MODES = ("with", "without", "both")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("skill_eval", "Skill-eval plugin")
    group.addoption(
        "--skill-model",
        default=None,
        help=(
            "Model under test. Overrides `skill_eval_model` ini. "
            f"Default: {DEFAULT_MODEL}."
        ),
    )
    group.addoption(
        "--skill-judge-model",
        default=None,
        help="Judge model used to grade expectations.",
    )
    group.addoption(
        "--skill-mode",
        default=None,
        choices=VALID_MODES,
        help="with: SKILL.md as system prompt; without: empty system; both: parametrise each case.",
    )
    parser.addini(
        "skill_eval_model",
        default=DEFAULT_MODEL,
        help="Model under test (CLI --skill-model overrides).",
    )
    parser.addini(
        "skill_eval_judge_model",
        default=DEFAULT_JUDGE_MODEL,
        help="Judge model (CLI --skill-judge-model overrides).",
    )
    parser.addini(
        "skill_eval_mode",
        default=DEFAULT_MODE,
        help="One of: with, without, both (CLI --skill-mode overrides).",
    )


def _opt(config: pytest.Config, key: str) -> str:
    cli = config.getoption(f"--skill-{key.replace('_', '-')}")
    if cli:
        return str(cli)
    return str(config.getini(f"skill_eval_{key}"))


def pytest_configure(config: pytest.Config) -> None:
    _load_dotenv(config)
    config.stash[_RESULTS_KEY] = defaultdict(list)


def _load_dotenv(config: pytest.Config) -> None:
    """Load `.env` from rootdir; shell env vars win."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(str(config.rootpath)) / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


_RESULTS_KEY: pytest.StashKey[dict[str, list[tuple[str, int, bool]]]] = pytest.StashKey()


def pytest_collect_file(parent: pytest.Collector, file_path: Path):
    if file_path.name != "evals.json":
        return None
    if file_path.parent.name != "evals":
        return None
    return EvalsJsonFile.from_parent(parent, path=file_path)


class EvalsJsonFile(pytest.File):
    def collect(self):
        data = json.loads(self.path.read_text())
        skill_name = data.get("skill_name", self.path.parent.parent.name)
        mode_arg = _opt(self.config, "mode")
        if mode_arg not in VALID_MODES:
            raise pytest.UsageError(
                f"skill_eval_mode must be one of {VALID_MODES}, got {mode_arg!r}"
            )
        modes = ["with", "without"] if mode_arg == "both" else [mode_arg]
        skill_md_path = self.path.parent.parent / "SKILL.md"
        for case in data.get("evals", []):
            case_id = case.get("id")
            for mode in modes:
                yield EvalItem.from_parent(
                    self,
                    name=f"case-{case_id}-{mode}",
                    skill_name=skill_name,
                    case=case,
                    mode=mode,
                    skill_md_path=skill_md_path,
                )


class EvalItem(pytest.Item):
    def __init__(
        self,
        *,
        skill_name: str,
        case: dict,
        mode: str,
        skill_md_path: Path,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.skill_name = skill_name
        self.case = case
        self.mode = mode
        self.skill_md_path = skill_md_path

    def runtest(self) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        if self.mode == "with":
            if not self.skill_md_path.exists():
                pytest.skip(f"SKILL.md not found at {self.skill_md_path}")
            system = self.skill_md_path.read_text()
        else:
            system = ""

        model = _opt(self.config, "model")
        judge_model = _opt(self.config, "judge_model")

        try:
            response, _timing = call_model(
                model=model,
                system=system,
                user=self.case["prompt"],
                api_key=api_key,
            )
        except ClientError as exc:
            pytest.fail(f"Model call failed: {exc}", pytrace=False)

        expectations = self.case.get("expectations") or []
        if not expectations:
            assert response.strip(), "Empty model response and no expectations to judge"
            self._record(True)
            return

        results = judge_expectations(
            response=response,
            expectations=expectations,
            model=judge_model,
            api_key=api_key,
        )
        passed = all(r.verdict == "PASS" for r in results)
        self._record(passed)
        if not passed:
            self._raise_failure(results, response)

    def _record(self, passed: bool) -> None:
        bucket = self.config.stash[_RESULTS_KEY]
        bucket[self.mode].append((self.skill_name, self.case.get("id"), passed))

    def _raise_failure(self, results: list[JudgeResult], response: str) -> None:
        passed_count = sum(1 for r in results if r.verdict == "PASS")
        lines = [
            f"Judge verdict: {passed_count}/{len(results)} expectations passed",
            "",
        ]
        for r in results:
            marker = "PASS" if r.verdict == "PASS" else "FAIL"
            lines.append(f"  [{marker}] {r.expectation}")
            if r.verdict == "FAIL" and r.reason:
                lines.append(f"         reason: {r.reason}")
        lines += ["", "--- Response ---", response]
        pytest.fail("\n".join(lines), pytrace=False)

    def reportinfo(self):
        return self.path, 0, f"{self.skill_name}::{self.name}"


def pytest_terminal_summary(
    terminalreporter, exitstatus: int, config: pytest.Config
) -> None:
    bucket = config.stash.get(_RESULTS_KEY, None)
    if not bucket:
        return
    tr = terminalreporter
    tr.write_sep("=", "skill-eval summary")
    counts: dict[str, tuple[int, int]] = {}
    for mode, rows in bucket.items():
        passed = sum(1 for _, _, ok in rows if ok)
        total = len(rows)
        counts[mode] = (passed, total)
        pct = (100 * passed / total) if total else 0
        tr.write_line(f"  {mode:<8s} {passed}/{total} ({pct:.0f}%)")
    if "with" in counts and "without" in counts:
        wp, wt = counts["with"]
        op, ot = counts["without"]
        if wt and ot:
            delta_pp = (wp / wt - op / ot) * 100
            tr.write_line(f"  delta    {delta_pp:+.0f}pp")
