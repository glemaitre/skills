from __future__ import annotations

from collections.abc import Sequence

import pytest
from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase, SingleTurnParams

from tests.eval.harness import (
    EvalCase,
    MetricOutcome,
    NO_TOOLS_NOTE,
    call_with_retries,
    compose_user_prompt,
    format_eval_failure,
    generate_response,
    litellm_model_name,
    record_eval_result,
    require_keys,
    transcript_path,
    visible_text,
    write_transcript,
)
from tests.eval.tiers import skill_tier


def _judge_model(skill_judge_model: str) -> LiteLLMModel:
    return LiteLLMModel(model=litellm_model_name(skill_judge_model))


def _must_do_metric(items: Sequence[str], *, judge: LiteLLMModel, pass_ratio: float) -> GEval:
    return GEval(
        name="must_do",
        evaluation_steps=[
            "Read the actual output only. Do not reward implied intent.",
            *(f"The actual output must satisfy this expectation: {item}" for item in items),
            "Score = 10 x (fraction of the expectations above that are met), rounded to the nearest integer.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        rubric=[
            Rubric(
                score_range=(0, 0),
                expected_outcome="None of the Must-do expectations are met.",
            ),
            Rubric(
                score_range=(1, 4),
                expected_outcome="Fewer than half of the Must-do expectations are met.",
            ),
            Rubric(
                score_range=(5, 7),
                expected_outcome="Most Must-do expectations are met, with several misses.",
            ),
            Rubric(
                score_range=(8, 9),
                expected_outcome=(
                    "Almost all Must-do expectations are met; only minor misses remain."
                ),
            ),
            Rubric(
                score_range=(10, 10),
                expected_outcome="Every Must-do expectation is met.",
            ),
        ],
        threshold=pass_ratio,
        strict_mode=False,
        model=judge,
    )


def _must_not_metric(items: Sequence[str], *, judge: LiteLLMModel) -> GEval:
    return GEval(
        name="must_not",
        evaluation_steps=[
            "Read the actual output only. Do not reward implied intent.",
            *(f"The actual output must satisfy this prohibition: {item}" for item in items),
            "Score 1.0 only if every prohibition above is respected; otherwise score 0.0.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        threshold=1.0,
        strict_mode=True,
        model=judge,
    )


def _run_metric(metric: GEval, test_case: LLMTestCase) -> MetricOutcome:
    try:
        call_with_retries(lambda: metric.measure(test_case))
    except Exception as exc:
        if type(exc).__name__ == "MissingTestCaseParamsError":
            return MetricOutcome(
                name=metric.name,
                score=None,
                threshold=float(metric.threshold),
                reason=str(exc),
                passed=False,
            )
        return MetricOutcome(
            name=metric.name,
            score=None,
            threshold=float(metric.threshold),
            reason=f"judge error: {exc}",
            passed=False,
        )
    score = metric.score
    threshold = float(metric.threshold)
    if getattr(metric, "success", None) is not None:
        passed = bool(metric.success)
    else:
        passed = score is not None and score >= threshold
    cost = getattr(metric, "evaluation_cost", None)
    return MetricOutcome(
        name=metric.name,
        score=None if score is None else float(score),
        threshold=threshold,
        reason=str(metric.reason or ""),
        passed=passed,
        evaluation_cost=None if cost is None else float(cost),
    )


def _outcomes_payload(outcomes: Sequence[MetricOutcome]) -> list[dict]:
    return [
        {
            "name": item.name,
            "score": item.score,
            "threshold": item.threshold,
            "reason": item.reason,
            "passed": item.passed,
            "evaluation_cost": item.evaluation_cost,
        }
        for item in outcomes
    ]


@pytest.mark.eval
def test_skill_case(
    eval_case: EvalCase,
    target_model: str,
    skill_mode: str,
    skill_judge_model: str,
    skill_pass_ratio: float,
    eval_run_id: str,
) -> None:
    require_keys(target_model, skill_judge_model)

    if skill_mode == "with":
        if not eval_case.skill_md_path.is_file():
            pytest.skip(f"SKILL.md not found at {eval_case.skill_md_path}")
        system = eval_case.skill_md_path.read_text(encoding="utf-8")
    else:
        system = ""

    user = compose_user_prompt(eval_case.prompt)
    path = transcript_path(
        eval_case, run_id=eval_run_id, mode=skill_mode, model=target_model
    )
    payload: dict = {
        "skill": eval_case.skill_name,
        "case_id": eval_case.case_id,
        "title": eval_case.title,
        "mode": skill_mode,
        "tier": skill_tier(eval_case.skill_name),
        "target_model": target_model,
        "judge_model": skill_judge_model,
        "pass_ratio": skill_pass_ratio,
        "prompt": eval_case.prompt,
        "harness_note": NO_TOOLS_NOTE,
        "user": user,
        "expectations": list(eval_case.expectations),
        "must_do": list(eval_case.must_do),
        "must_not": list(eval_case.must_not),
    }

    result = generate_response(
        model=target_model,
        system=system,
        user=user,
    )
    actual, source = visible_text(result)
    payload.update(
        {
            "content": result.content,
            "reasoning": result.reasoning,
            "finish_reason": result.finish_reason,
            "usage": result.usage,
            "judged_from": source,
        }
    )
    write_transcript(path, payload)

    if not actual:
        record_eval_result(mode=skill_mode, case=eval_case, passed=False)
        pytest.fail(
            format_eval_failure(
                case=eval_case,
                target_model=target_model,
                skill_mode=skill_mode,
                actual="",
                outcomes=(),
                transcript=path,
                extra="The model returned neither content nor reasoning_content.",
            ),
            pytrace=False,
        )

    if not eval_case.expectations:
        record_eval_result(mode=skill_mode, case=eval_case, passed=True)
        payload["passed"] = True
        payload["metrics"] = []
        write_transcript(path, payload)
        return

    test_case = LLMTestCase(input=eval_case.prompt, actual_output=actual)
    judge = _judge_model(skill_judge_model)
    outcomes: list[MetricOutcome] = []
    if eval_case.must_do:
        outcomes.append(
            _run_metric(
                _must_do_metric(
                    eval_case.must_do, judge=judge, pass_ratio=skill_pass_ratio
                ),
                test_case,
            )
        )
    if eval_case.must_not:
        outcomes.append(
            _run_metric(_must_not_metric(eval_case.must_not, judge=judge), test_case)
        )

    payload["metrics"] = _outcomes_payload(outcomes)
    passed = all(item.passed for item in outcomes)
    judge_error = any(item.reason.startswith("judge error:") for item in outcomes)
    payload["passed"] = passed
    write_transcript(path, payload)

    if passed:
        record_eval_result(mode=skill_mode, case=eval_case, passed=True)
        return

    record_eval_result(
        mode=skill_mode, case=eval_case, passed=False, judge_error=judge_error
    )
    pytest.fail(
        format_eval_failure(
            case=eval_case,
            target_model=target_model,
            skill_mode=skill_mode,
            actual=actual,
            outcomes=outcomes,
            transcript=path,
        ),
        pytrace=False,
    )
