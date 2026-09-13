from tests.eval.sandbox import is_tool_xml_only, parse_xml_tool_calls, strip_tool_xml


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
