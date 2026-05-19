#!/usr/bin/env python3
"""Convert our prompts.md → skill-creator's evals.json schema.

Reads `eval/<skill>/prompts.md` for each skill listed and writes
`skills/<skill>/evals/evals.json` in the official skill-creator schema.

Mapping:
  CASE_NN heading      → eval id (parsed from NN)
  User prompt block    → prompt (prefixed with workspace state)
  Workspace state      → inlined into prompt
  Must do bullets      → expectations (verbatim)
  Must NOT do bullets  → expectations (negated form: "The response does NOT …")

Usage:
    python3 eval/convert_to_evals_json.py                 # all skills with eval/<name>/prompts.md
    python3 eval/convert_to_evals_json.py python-api …    # just the named skills
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()


def parse_prompts_md(text: str) -> list[dict]:
    """Return [{id, title, prompt, must_do, must_not}]."""
    cases = []
    for block in text.split("\n---\n"):
        head = re.search(r"^## CASE_(\d+) — (.+)$", block, re.MULTILINE)
        if not head:
            continue
        case_id = int(head.group(1))
        title = head.group(2).strip()

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

        must_do = _extract_bullets(block, r"\*\*Must do:?\*\*")
        must_not = _extract_bullets(block, r"\*\*Must NOT do:?\*\*")

        cases.append({
            "id": case_id,
            "title": title,
            "workspace_state": workspace_state,
            "user_prompt": user_prompt,
            "must_do": must_do,
            "must_not": must_not,
        })
    return cases


def _extract_bullets(block: str, header_re: str) -> list[str]:
    """Extract `- ` bullet items under a bolded header."""
    m = re.search(
        header_re + r"\s*\n((?:-[ \t].*(?:\n[ \t]+\S.*)*(?:\n|$))+)", block
    )
    if not m:
        return []
    raw = m.group(1)
    bullets = []
    current = None
    for line in raw.splitlines():
        if line.startswith("- "):
            if current is not None:
                bullets.append(current.strip())
            current = line[2:].strip()
        elif line.startswith("  ") and current is not None:
            current += " " + line.strip()
    if current is not None:
        bullets.append(current.strip())
    return bullets


def to_evals_json(skill_name: str, cases: list[dict]) -> dict:
    evals = []
    for case in cases:
        if case["workspace_state"]:
            prompt = (
                f"[Workspace state — read but do not narrate back:\n"
                f"{case['workspace_state']}]\n\n{case['user_prompt']}"
            )
        else:
            prompt = case["user_prompt"]

        # Expectations = Must do (positive) + negated Must NOT.
        expectations = list(case["must_do"])
        for n in case["must_not"]:
            expectations.append(f"The response does NOT: {n}")

        expected_output_lines = [
            f"Behavioural response satisfying:",
            *[f"- {m}" for m in case["must_do"][:3]],
        ]
        if case["must_not"]:
            expected_output_lines.append("It must NOT:")
            expected_output_lines.extend(f"- {n}" for n in case["must_not"][:3])
        expected_output = " ".join(expected_output_lines)

        evals.append({
            "id": case["id"],
            "prompt": prompt,
            "expected_output": expected_output,
            "files": [],
            "expectations": expectations,
        })
    return {"skill_name": skill_name, "evals": evals}


def convert_skill(skill: str) -> Path | None:
    prompts_path = REPO / "eval" / skill / "prompts.md"
    if not prompts_path.exists():
        print(f"  [skip] {skill}: no prompts.md")
        return None

    cases = parse_prompts_md(prompts_path.read_text())
    if not cases:
        print(f"  [skip] {skill}: no cases parsed")
        return None

    evals = to_evals_json(skill, cases)
    out_dir = REPO / "skills" / skill / "evals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "evals.json"
    out.write_text(json.dumps(evals, indent=2) + "\n")
    print(f"  [ok]   {skill}: {len(cases)} cases → {out.relative_to(REPO)}")
    return out


if __name__ == "__main__":
    requested = sys.argv[1:]
    if requested:
        skills = requested
    else:
        skills = sorted(
            p.name for p in (REPO / "eval").iterdir()
            if p.is_dir() and (p / "prompts.md").exists()
        )
    print(f"Converting {len(skills)} skill(s):")
    for s in skills:
        convert_skill(s)
