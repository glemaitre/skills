from tests.eval.harness import died_mid_deliverable


def test_dangling_checkbox_is_truncated() -> None:
    text = (
        "## Pre-flight (evaluate-ml-pipeline)\n"
        "- [x] Tier 1 mandatory libs importable\n"
        "- [x"
    )
    assert died_mid_deliverable(text) == "visible answer truncated mid-checklist"


def test_now_writing_without_body_is_truncated() -> None:
    text = (
        "Pre-flight checklist…\n"
        "- [ ] Pre-flight re-emitted — this block\n"
        "\n"
        "Now writing the artifacts:\n"
    )
    assert died_mid_deliverable(text) == "visible answer stopped before the deliverable"


def test_complete_checkbox_row_is_not_a_skip() -> None:
    text = (
        "Refuse to mark done. Smoke is red.\n"
        "- [x] Smoke test status: failing\n"
    )
    assert died_mid_deliverable(text) is None


def test_unclosed_fence_is_truncated() -> None:
    text = "Here is the Status block:\n```markdown\nState: done\n"
    assert died_mid_deliverable(text) == "visible answer has an unclosed code fence"


def test_empty_is_not_this_skip() -> None:
    assert died_mid_deliverable("") is None
    assert died_mid_deliverable("   ") is None
