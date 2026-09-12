"""Load skill-creator evals.json cases and generate a single-turn response."""

from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
TRANSCRIPT_DIR = REPO_ROOT / ".transcripts"

DEFAULT_TARGET_MODEL = "openrouter/deepseek/deepseek-v4.1-flash"
DEFAULT_JUDGE_MODEL = "openrouter/deepseek/deepseek-v4.1-flash"
DEFAULT_PASS_RATIO = 0.7
MUST_NOT_PREFIX = "The response does NOT"
NO_TOOLS_NOTE = (
    "Harness note: this is a single-turn evaluation. You have no tools this "
    "turn - no shell, no file reads, no scratch scripts. Treat the workspace "
    "state described above as already verified. Do not emit tool calls or "
    "wait for results; give your complete final answer in this message, "
    "filling any checklist from the information given."
)

_PROVIDER_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "azure": "AZURE_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "vertex_ai": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


@dataclass(frozen=True)
class EvalCase:
    skill_name: str
    skill_md_path: Path
    case_id: int | str
    title: str
    prompt: str
    expectations: tuple[str, ...]

    @property
    def must_do(self) -> tuple[str, ...]:
        return split_expectations(self.expectations)[0]

    @property
    def must_not(self) -> tuple[str, ...]:
        return split_expectations(self.expectations)[1]


def split_expectations(
    expectations: Sequence[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (must_do, must_not) using the prompts.md negation prefix."""
    must_do: list[str] = []
    must_not: list[str] = []
    for item in expectations:
        if item.startswith(MUST_NOT_PREFIX):
            must_not.append(item)
        else:
            must_do.append(item)
    return tuple(must_do), tuple(must_not)


def compose_user_prompt(prompt: str) -> str:
    return f"{prompt.rstrip()}\n\n{NO_TOOLS_NOTE}"


def slugify(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:max_len].rstrip("-") or "untitled")


def litellm_model_name(model: str) -> str:
    """Accept bare Anthropic/OpenAI ids as well as provider-qualified LiteLLM names."""
    if "/" in model:
        return model
    if model.startswith("claude"):
        return f"anthropic/{model}"
    if model.startswith(("gpt-", "o1", "o3", "o4")):
        return f"openai/{model}"
    if model.startswith("gemini"):
        return f"gemini/{model}"
    return model


def required_api_key_env(model: str) -> str | None:
    provider = litellm_model_name(model).split("/", 1)[0]
    return _PROVIDER_ENV.get(provider)


def load_eval_cases() -> list[EvalCase]:
    cases: list[EvalCase] = []
    for evals_path in sorted(SKILLS_DIR.glob("*/evals/evals.json")):
        skill_dir = evals_path.parent.parent
        data = json.loads(evals_path.read_text(encoding="utf-8"))
        skill_name = data.get("skill_name") or skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        for raw in data.get("evals") or []:
            expectations = tuple(str(item) for item in (raw.get("expectations") or []))
            case_id = raw["id"]
            cases.append(
                EvalCase(
                    skill_name=skill_name,
                    skill_md_path=skill_md,
                    case_id=case_id,
                    title=str(raw.get("title") or ""),
                    prompt=raw["prompt"],
                    expectations=expectations,
                )
            )
    return cases


EVAL_RESULTS: dict[str, list[tuple[str, object, str, bool, bool]]] = defaultdict(list)


def record_eval_result(
    *, mode: str, case: EvalCase, passed: bool, judge_error: bool = False
) -> None:
    EVAL_RESULTS[mode].append(
        (case.skill_name, case.case_id, case.title, passed, judge_error)
    )


def require_keys(*models: str) -> None:
    missing: list[str] = []
    seen: set[str] = set()
    for model in models:
        env_name = required_api_key_env(model)
        if env_name and env_name not in seen and not os.environ.get(env_name):
            missing.append(env_name)
            seen.add(env_name)
    if missing:
        pytest.skip("missing API key(s): " + ", ".join(missing))


def case_node_id(case: EvalCase, *, mode: str, model: str) -> str:
    slug = slugify(case.title)
    return f"{case.skill_name}-case{case.case_id}-{slug}-{mode}-{_short_model(model)}"


def _short_model(model: str) -> str:
    return model.rsplit("/", 1)[-1].replace(":", "_")


@dataclass(frozen=True)
class MetricOutcome:
    name: str
    score: float | None
    threshold: float
    reason: str
    passed: bool
    evaluation_cost: float | None = None


def format_eval_failure(
    *,
    case: EvalCase,
    target_model: str,
    skill_mode: str,
    actual: str,
    outcomes: Sequence[MetricOutcome],
    transcript: Path | None = None,
    extra: str = "",
) -> str:
    heading = f"{case.skill_name}  case {case.case_id}"
    if case.title:
        heading += f" — {case.title}"
    lines = [
        heading,
        f"mode: {skill_mode}  target: {target_model}",
    ]
    if outcomes:
        width = max(len(item.name) for item in outcomes)
        for item in outcomes:
            score_s = "n/a" if item.score is None else f"{item.score:.2f}"
            verdict = "ok" if item.passed else "FAIL"
            lines.append(
                f"{item.name:<{width}}  {score_s} (threshold {item.threshold:.2f})  {verdict}"
            )
        lines.append("")
        for item in outcomes:
            lines.append(f"{item.name} reason: {item.reason or '(no reason from judge)'}")
    else:
        lines.append("GEval: (not run)")
    if transcript is not None:
        lines.append(f"transcript: {transcript}")
        lines.append(f"transcript_md: {transcript.with_suffix('.md')}")
    if extra:
        lines += ["", extra]
    lines += ["", "Must do:"]
    if case.must_do:
        lines.extend(f"  - {item}" for item in case.must_do)
    else:
        lines.append("  (none)")
    lines += ["", "Must NOT:"]
    if case.must_not:
        lines.extend(f"  - {item}" for item in case.must_not)
    else:
        lines.append("  (none)")
    lines += ["", "--- Response ---", actual or "(empty)"]
    return "\n".join(lines)


@dataclass(frozen=True)
class GenerationResult:
    content: str
    reasoning: str
    finish_reason: str | None
    usage: dict[str, object] = field(default_factory=dict)


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_transcript_dirs(run_id: str | None = None) -> Path:
    """Create `.transcripts/` and, when ``run_id`` is set, `<run-id>/`.

    Per-skill directories are created lazily by ``write_transcript``.
    """
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    if run_id is None:
        return TRANSCRIPT_DIR
    session = TRANSCRIPT_DIR / run_id
    session.mkdir(parents=True, exist_ok=True)
    return session


def transcript_path(case: EvalCase, *, run_id: str, mode: str, model: str) -> Path:
    name = f"case{case.case_id}-{mode}-{_short_model(model)}.json"
    return TRANSCRIPT_DIR / run_id / case.skill_name / name


def write_transcript(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    path.with_suffix(".md").write_text(_format_transcript_md(payload), encoding="utf-8")
    return path


def _format_transcript_md(payload: dict) -> str:
    heading = f"{payload.get('skill', '')} case {payload.get('case_id', '')}"
    title = payload.get("title") or ""
    if title:
        heading += f" — {title}"
    lines = [
        f"# {heading}",
        "",
        f"- mode: {payload.get('mode')}",
        f"- target: {payload.get('target_model')}",
        f"- judge: {payload.get('judge_model')}",
        f"- finish_reason: {payload.get('finish_reason')}",
        f"- judged_from: {payload.get('judged_from')}",
        f"- usage: {payload.get('usage')}",
    ]
    if "passed" in payload:
        lines.append(f"- passed: {payload.get('passed')}")
    lines += ["", "## Prompt", "", str(payload.get("prompt") or "").rstrip(), ""]
    note = payload.get("harness_note")
    if note:
        lines += ["## Harness note", "", str(note).rstrip(), ""]
    user = payload.get("user")
    if user:
        lines += ["## User message", "", str(user).rstrip(), ""]
    must_do = payload.get("must_do")
    must_not = payload.get("must_not")
    if must_do is None and must_not is None:
        must_do, must_not = split_expectations(payload.get("expectations") or [])
    lines += ["## Must do", ""]
    if must_do:
        lines.extend(f"- {item}" for item in must_do)
    else:
        lines.append("(none)")
    lines += ["", "## Must NOT", ""]
    if must_not:
        lines.extend(f"- {item}" for item in must_not)
    else:
        lines.append("(none)")
    lines += ["", "## Response", "", str(payload.get("content") or "").rstrip() or "(empty)", ""]
    reasoning = str(payload.get("reasoning") or "").rstrip()
    if reasoning:
        lines += ["## Reasoning", "", reasoning, ""]
    metrics = payload.get("metrics") or []
    if metrics:
        lines += ["## Metrics", ""]
        for metric in metrics:
            score = metric.get("score")
            score_s = "n/a" if score is None else f"{float(score):.2f}"
            threshold = metric.get("threshold")
            threshold_s = "" if threshold is None else f"{float(threshold):.2f}"
            verdict = "ok" if metric.get("passed") else "FAIL"
            cost = metric.get("evaluation_cost")
            cost_s = "" if cost is None else f"  cost: {cost}"
            lines += [
                f"### {metric.get('name')}",
                "",
                f"score: {score_s} (threshold {threshold_s})  {verdict}{cost_s}",
                "",
                str(metric.get("reason") or "(no reason from judge)"),
                "",
            ]
    elif payload.get("geval_reason") or payload.get("geval_score") is not None:
        score = payload.get("geval_score")
        score_s = "n/a" if score is None else f"{float(score):.2f}"
        lines += [
            "## Metrics",
            "",
            f"score: {score_s}",
            "",
            str(payload.get("geval_reason") or "(no reason from judge)"),
            "",
        ]
    return "\n".join(lines) + "\n"


def visible_text(result: GenerationResult) -> tuple[str, str]:
    """Prefer assistant content; fall back to reasoning if content is empty."""
    content = (result.content or "").strip()
    if content:
        return content, "content"
    reasoning = (result.reasoning or "").strip()
    if reasoning:
        return reasoning, "reasoning"
    return "", "empty"


TARGET_TRANSPORT_TIMEOUT = 600.0
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = (1.0, 3.0, 9.0)


def call_with_retries(fn, *, attempts: int = RETRY_ATTEMPTS):
    """Retry ``fn`` on transient failures with exponential backoff."""
    last_exc: BaseException | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — provider SDKs raise many types
            last_exc = exc
            if attempt >= attempts - 1:
                break
            delay = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)]
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def generate_response(*, model: str, system: str, user: str) -> GenerationResult:
    """Call the target with no max_tokens cap so reasoning models can finish."""
    from litellm import completion

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    def _once():
        return completion(
            model=litellm_model_name(model),
            messages=messages,
            temperature=0,
            timeout=TARGET_TRANSPORT_TIMEOUT,
        )

    response = call_with_retries(_once)
    choice = response.choices[0]
    message = choice.message
    usage = getattr(response, "usage", None)
    usage_dict: dict[str, object] = {}
    if usage is not None:
        if hasattr(usage, "model_dump"):
            usage_dict = usage.model_dump()
        elif hasattr(usage, "__dict__"):
            usage_dict = {k: v for k, v in vars(usage).items() if not k.startswith("_")}
    return GenerationResult(
        content=message.content or "",
        reasoning=str(getattr(message, "reasoning_content", None) or ""),
        finish_reason=getattr(choice, "finish_reason", None),
        usage=usage_dict,
    )
