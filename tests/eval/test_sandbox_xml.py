from pathlib import Path
from tempfile import TemporaryDirectory

from tests.eval.sandbox import (
    Sandbox,
    is_tool_xml_only,
    missing_tools,
    parse_xml_tool_calls,
    strip_tool_xml,
)


def test_strip_tool_xml_keeps_prose() -> None:
    raw = (
        "Refuse the loader shift.\n"
        "<minimax:tool_call>\n"
        '<invoke name="list_dir">\n'
        '<parameter name="path">scratch</parameter>\n'
        "</invoke>\n"
        "</minimax:tool_call>\n"
    )
    assert strip_tool_xml(raw) == "Refuse the loader shift."
    assert not is_tool_xml_only(raw)


def test_xml_only_tool_call() -> None:
    raw = """
<minimax:tool_call>
<invoke name="list_dir">
<parameter name="path">scratch</parameter>
</invoke>
<invoke name="list_dir">
<parameter name="path">references</parameter>
</invoke>
</minimax:tool_call>
"""
    assert is_tool_xml_only(raw)
    assert strip_tool_xml(raw) == ""
    assert len(parse_xml_tool_calls(raw)) == 2


def test_missing_tools_requires_trace_name() -> None:
    trace = [{"name": "list_dir", "arguments": {"path": "."}}]
    assert missing_tools(trace, ["AskUserQuestion"]) == ["AskUserQuestion"]
    assert missing_tools(
        [{"name": "AskUserQuestion", "arguments": {}}],
        ["AskUserQuestion"],
    ) == []


def test_ask_user_question_dispatch_does_not_answer() -> None:
    with TemporaryDirectory() as tmp:
        box = Sandbox(Path(tmp))
        result = box.dispatch(
            "AskUserQuestion",
            {
                "questions": [
                    {
                        "question": "G-PKG-NAME",
                        "options": [{"id": "ml_pricing", "label": "ml_pricing"}],
                    }
                ]
            },
        )
    assert "has not answered" in result
    assert "scaffold" in result.lower()
