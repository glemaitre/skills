"""Tests for the design-note approval context."""

from __future__ import annotations

from pathlib import Path

from skore_skills.gate_context import design_context

FILLED = """\
# 01_dummy

## Question / hypothesis

Does the loading and fit/predict path work end to end?

## Motivation

- **Sourcing strategy:** my-pick
- **Source(s):**
  <!-- One line is enough for most cases. -->
  - first modeling turn, no prior experiment
- **Why this matters:** a structural baseline unblocks the real pipeline.

## Method

- **Files touched:** `src/pkg/pipeline.py`, `experiments/01_dummy.py`
- **Change versus baseline (or previous experiment):** first pipeline; a
  DummyClassifier inside the skrub DataOps declaration
- **Cross-validation:** decided at the evaluation step
- **Pipeline:** <!-- results-embed: pipeline -->

## Risks / things that could invalidate the result

- the dummy adds no predictive value; it only proves the path
- a green smoke test says nothing about generalization
- a third risk that must not be returned

## Status

- **State:** planned
"""

TEMPLATE = """\
# <NN>_<short_name>

<!--
Design note for experiments/<NN>_<short_name>.py.
-->

## Question / hypothesis

<!-- One sentence. What are we trying to learn — not just "try X". -->

## Motivation

- **Sourcing strategy:** <user | my-pick | backlog:B<N>>
- **Source(s):**
  - <e.g. issue #42 / "Paper Title" (year) URL>
- **Why this matters:** <one or two sentences>

## Method

- **Files touched:** <e.g., `src/<pkg>/features.py`>
- **Change versus baseline (or previous experiment):** <prose>

## Risks / things that could invalidate the result

- <e.g., "ROC-AUC may improve via leakage">

## Status

- **State:** planned
"""


def _note(root: Path, stem: str, text: str) -> None:
    path = root / "journal" / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_filled_note_returns_every_field(tmp_path: Path) -> None:
    _note(tmp_path, "01_dummy", FILLED)

    context = design_context(tmp_path, "01_dummy")

    assert context == {
        "note": "journal/01_dummy.md",
        "question": "Does the loading and fit/predict path work end to end?",
        "source": "first modeling turn, no prior experiment",
        "files_touched": "`src/pkg/pipeline.py`, `experiments/01_dummy.py`",
        "change": (
            "first pipeline; a DummyClassifier inside the skrub DataOps declaration"
        ),
        "risks": [
            "the dummy adds no predictive value; it only proves the path",
            "a green smoke test says nothing about generalization",
        ],
    }


def test_unfilled_template_returns_empty_fields(tmp_path: Path) -> None:
    _note(tmp_path, "02_next", TEMPLATE)

    context = design_context(tmp_path, "02_next")

    assert context == {
        "note": "journal/02_next.md",
        "question": "",
        "source": "",
        "files_touched": "",
        "change": "",
        "risks": [],
    }


def test_missing_sections_return_empty_fields(tmp_path: Path) -> None:
    _note(tmp_path, "03_partial", "# 03_partial\n\n## Status\n\n- **State:** planned\n")

    context = design_context(tmp_path, "03_partial")

    assert context == {
        "note": "journal/03_partial.md",
        "question": "",
        "source": "",
        "files_touched": "",
        "change": "",
        "risks": [],
    }


def test_comment_only_question_is_not_prose(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "04_commented",
        "## Question / hypothesis\n\n<!-- One sentence. -->\n\n"
        "## Method\n\n- **Files touched:** `src/pkg/data.py`\n",
    )

    context = design_context(tmp_path, "04_commented")

    assert context["question"] == ""
    assert context["files_touched"] == "`src/pkg/data.py`"


def test_missing_note_returns_empty_context(tmp_path: Path) -> None:
    context = design_context(tmp_path, "09_absent")

    assert context == {
        "note": "",
        "question": "",
        "source": "",
        "files_touched": "",
        "change": "",
        "risks": [],
    }
