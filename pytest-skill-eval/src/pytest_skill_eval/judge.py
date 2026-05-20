from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .client import call_model

JUDGE_SYSTEM = """\
You evaluate whether an AI response satisfies a list of expectations.

For each expectation, decide PASS or FAIL based ONLY on what the response says.
Be strict but fair: an expectation passes if the response substantively meets it.

Output a single JSON object with this exact shape, and nothing else:
{
  "verdicts": [
    {"id": 1, "verdict": "PASS", "reason": "<one short sentence>"},
    {"id": 2, "verdict": "FAIL", "reason": "<one short sentence>"}
  ]
}
"""


@dataclass
class JudgeResult:
    expectation: str
    verdict: str
    reason: str


def judge_expectations(
    *,
    response: str,
    expectations: list[str],
    model: str,
    api_key: str,
) -> list[JudgeResult]:
    numbered = "\n".join(f"{i}. {e}" for i, e in enumerate(expectations, 1))
    user_msg = (
        "# Response to evaluate\n"
        f"<response>\n{response}\n</response>\n\n"
        "# Expectations\n"
        f"{numbered}\n"
    )
    raw, _ = call_model(
        model=model,
        system=JUDGE_SYSTEM,
        user=user_msg,
        api_key=api_key,
    )
    data = _extract_json(raw)
    by_id = {v.get("id"): v for v in data.get("verdicts", []) if isinstance(v, dict)}
    results: list[JudgeResult] = []
    for i, exp in enumerate(expectations, 1):
        v = by_id.get(i)
        if not v:
            results.append(
                JudgeResult(
                    expectation=exp,
                    verdict="FAIL",
                    reason="judge omitted this expectation",
                )
            )
            continue
        verdict = str(v.get("verdict", "FAIL")).upper()
        if verdict not in ("PASS", "FAIL"):
            verdict = "FAIL"
        results.append(
            JudgeResult(
                expectation=exp,
                verdict=verdict,
                reason=str(v.get("reason", "")),
            )
        )
    return results


def _extract_json(text: str) -> dict:
    """Best-effort: pull the first {...} JSON object from the judge response."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"verdicts": []}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"verdicts": []}
