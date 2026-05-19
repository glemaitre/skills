#!/usr/bin/env python3
"""Run a skill eval against Claude Haiku 4.5.

Usage:
    ANTHROPIC_API_KEY=... python3 eval/run.py <skill-name> <label> [skill-path | --no-skill]

Examples:
    python3 eval/run.py python-api baseline
    python3 eval/run.py python-api refactored skills/python-api/SKILL_v2.md
    python3 eval/run.py python-api without_skill --no-skill

Reads cases from `eval/<skill-name>/prompts.md`, sends each through
Haiku 4.5 with the chosen `SKILL.md` loaded as the system prompt, writes
one transcript per case under `eval/<skill-name>/transcripts/<label>/`.

`--no-skill` runs with an empty system prompt — the without-skill
baseline. Compares against the with-skill runs to measure what value the
skill actually adds (per agentskills.io's recommended eval pattern).

Each transcript embeds timing: `duration_ms`, `input_tokens`,
`output_tokens`, `total_tokens`. Lets you measure cost-benefit
(higher pass rate vs more tokens) across iterations.

Stdlib only (no SDK dep) so it runs anywhere with Python 3.11+.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "claude-haiku-4-5-20251001"
API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MAX_TOKENS = 4096

REPO = Path(__file__).parent.parent.resolve()


def parse_cases(text: str) -> list[tuple[str, str, str, str]]:
    """Return [(case_id, title, user_prompt, workspace_state)] from prompts.md."""
    cases = []
    for block in text.split("\n---\n"):
        head = re.search(r"^## (CASE_\d+) — (.+)$", block, re.MULTILINE)
        if not head:
            continue
        case_id, title = head.group(1), head.group(2).strip()

        up = re.search(
            r"\*\*User prompt:\*\*\s*\n((?:>[ \t]?.*(?:\n|$))+)", block
        )
        if not up:
            continue
        user_prompt = "\n".join(
            line.removeprefix("> ").removeprefix(">").rstrip()
            for line in up.group(1).strip().splitlines()
        )

        ws = re.search(
            r"\*\*Assumed workspace state:\*\*\s*\n((?:[-\s].*(?:\n|$))+?)\n\*\*",
            block,
        )
        workspace_state = ws.group(1).strip() if ws else ""

        cases.append((case_id, title, user_prompt, workspace_state))
    return cases


def call_haiku(
    system: str, user_msg: str, api_key: str
) -> tuple[str, dict[str, int]]:
    """Return (response_text, timing_dict).

    timing_dict has duration_ms, input_tokens, output_tokens, total_tokens.
    """
    body_dict = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": user_msg}],
    }
    # An empty system prompt confuses some routes; only include when set.
    if system:
        body_dict["system"] = system

    body = json.dumps(body_dict).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
    )
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"HTTP {exc.code} from Anthropic API:\n{exc.read().decode('utf-8')}"
        )
    duration_ms = int((time.monotonic() - start) * 1000)

    text = "".join(
        block["text"] for block in payload["content"] if block["type"] == "text"
    )
    usage = payload.get("usage", {})
    in_tok = usage.get("input_tokens", 0)
    out_tok = usage.get("output_tokens", 0)
    timing = {
        "duration_ms": duration_ms,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": in_tok + out_tok,
    }
    return text, timing


def run(skill_name: str, label: str, skill_path: Path | None) -> None:
    """Run eval. skill_path=None → without-skill mode (empty system prompt)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set in environment")

    here = REPO / "eval" / skill_name
    prompts_path = here / "prompts.md"
    if not prompts_path.exists():
        raise SystemExit(f"prompts.md not found at {prompts_path}")

    if skill_path is None:
        skill_text = ""
        skill_label = "<no skill — without-skill baseline>"
        skill_lines = 0
    else:
        if not skill_path.exists():
            raise SystemExit(f"SKILL.md not found at {skill_path}")
        skill_text = skill_path.read_text()
        skill_label = str(skill_path.relative_to(REPO))
        skill_lines = len(skill_text.splitlines())

    cases = parse_cases(prompts_path.read_text())
    if not cases:
        raise SystemExit(f"No cases parsed from {prompts_path}")

    out_dir = here / "transcripts" / label
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"Running {len(cases)} cases against {MODEL}, "
        f"skill={skill_label} ({skill_lines} lines), label={label!r}"
    )
    totals = {"duration_ms": 0, "input_tokens": 0, "output_tokens": 0}
    for case_id, title, user_prompt, workspace_state in cases:
        user_msg = (
            f"[Workspace state — read but do not narrate back:\n"
            f"{workspace_state}]\n\n{user_prompt}"
        )
        print(f"  {case_id}: {title} ...", end="", flush=True)
        response, timing = call_haiku(skill_text, user_msg, api_key)
        for k in ("duration_ms", "input_tokens", "output_tokens"):
            totals[k] += timing[k]
        out = out_dir / f"{case_id}.md"
        out.write_text(
            f"# {case_id} — {title}\n\n"
            f"**Model:** `{MODEL}`  \n"
            f"**Label:** `{label}`  \n"
            f"**Skill:** `{skill_label}` ({skill_lines} lines)  \n"
            f"**Timing:** "
            f"{timing['duration_ms']/1000:.1f}s, "
            f"{timing['input_tokens']:,} in + "
            f"{timing['output_tokens']:,} out = "
            f"{timing['total_tokens']:,} tokens\n\n"
            f"## Input (user message)\n\n```\n{user_msg}\n```\n\n"
            f"## Response\n\n{response}\n"
        )
        print(
            f" → {out.relative_to(REPO)} "
            f"[{timing['duration_ms']/1000:.1f}s, {timing['total_tokens']:,}tok]"
        )

    print(
        f"\nTotals across {len(cases)} cases: "
        f"{totals['duration_ms']/1000:.1f}s wall, "
        f"{totals['input_tokens']:,} in + "
        f"{totals['output_tokens']:,} out = "
        f"{totals['input_tokens']+totals['output_tokens']:,} tokens"
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(
            "Usage: python3 eval/run.py <skill-name> <label> "
            "[skill-path | --no-skill]"
        )
    skill_name = sys.argv[1]
    label = sys.argv[2]
    skill_arg = sys.argv[3] if len(sys.argv) > 3 else None

    if skill_arg == "--no-skill":
        skill_path = None
    elif skill_arg:
        skill_path = Path(skill_arg).resolve()
    else:
        skill_path = REPO / "skills" / skill_name / "SKILL.md"
    run(skill_name, label, skill_path)
