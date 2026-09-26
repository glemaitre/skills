from tests.eval.harness import MetricOutcome
from tests.eval.language import (
    is_language_prohibition,
    language_violations,
    merge_must_not,
    partition_language,
    score_user_facing_language,
)

LANGUAGE = (
    "The response does NOT: Put catalog skill ids, HITL, "
    "`G-PKG-NAME`, or `python -m skore_skills` / `env add` in "
    "user-facing questions or the close narrative."
)


def test_language_rule_is_partitioned_out_of_judge_items() -> None:
    language, rest = partition_language(
        (LANGUAGE, "The response does NOT: Invent `git init` procedure.")
    )
    assert language == (LANGUAGE,)
    assert rest == ("The response does NOT: Invent `git init` procedure.",)
    assert is_language_prohibition(LANGUAGE)


def test_internal_checklist_is_not_a_language_violation() -> None:
    text = """
## Data understanding — closed

The duplicate rows sit in two families. Open data_analysis/data_analysis.md.
AskUserQuestion: keep exploring or close.

### State at close
- [x] G-DATA-ANALYSIS: run
- [x] G-TABULAR + pandas + skrub

### Post-close mechanical steps
- `python -m skore_skills notebook convert data_analysis/data_analysis.py`
- `python -m skore_skills site build`

```bash
python -m skore_skills git end-turn --stage data_analysis
```

G-REPORT-LOCATOR
"""
    assert language_violations(text) == ()
    assert score_user_facing_language(text).passed is True


def test_procedure_names_and_plain_preflight_are_not_the_close() -> None:
    text = """
Pre-flight (evaluate-ml-pipeline):
- [ ] Smoke test status (per `smoke-test-ml-pipeline`)
- [ ] G-SKORE-MODE

## Stop
Return to `model-ml-pipeline` (first-run HITL). Do not write the call.
"""
    assert language_violations(text) == ()


def test_skill_id_in_the_close_fails() -> None:
    text = """
## Closed

Next, load explore-ml-data before writing the notebook.

### State at close
- [x] G-TABULAR
"""
    outcome = score_user_facing_language(text)
    assert outcome.passed is False
    assert outcome.score == 0.0
    assert "explore-ml-data" in outcome.reason
    assert "G-TABULAR" not in outcome.reason


def test_stretched_labels_are_not_catalog_ids() -> None:
    text = (
        "The build_learner function follows tree step 4. "
        "Then measure, declare, evaluate, and confirm the split."
    )
    assert language_violations(text) == ()


def test_hitl_in_prose_fails_and_command_lines_do_not() -> None:
    text = """
Ask the HITL gate before writing the notebook.

## Turn-closing commands
- `python -m skore_skills git end-turn --stage data_analysis`
- `env add skrub`

## Agent notes (internal — not for the user)
Install it with add-python-package.
"""
    violations = language_violations(text)
    assert "HITL" in violations
    assert "python -m skore_skills" not in violations
    assert "env add" not in violations
    assert "add-python-package" not in violations


def test_unmanaged_install_line_is_allowed() -> None:
    text = "pip install pytest\nuv add scikit-learn\npixi add skrub"
    assert language_violations(text) == ()


def test_merge_keeps_a_judge_error_and_a_language_miss() -> None:
    language = score_user_facing_language("Load triage-ml-task now.")
    judged = MetricOutcome(
        name="must_not",
        score=None,
        threshold=1.0,
        reason="judge error: timeout",
        passed=False,
        evaluation_cost=0.25,
    )
    merged = merge_must_not(language, judged)
    assert merged.passed is False
    assert merged.score is None
    assert merged.reason.startswith("judge error:")
    assert "triage-ml-task" in merged.reason
    assert merged.evaluation_cost == 0.25
