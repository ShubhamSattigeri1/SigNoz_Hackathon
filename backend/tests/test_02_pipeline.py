"""Section C: Unit tests for pipeline steps."""

import pytest
from pipeline import step1_search, step2_pick_tool, step3_answer
from corpus import DOCUMENTS


def test_step1_search_no_override_returns_upi():
    result = step1_search("What is the daily UPI transfer limit?")
    assert result["doc_id"] == "doc_upi"


def test_step1_search_with_override_returns_atm():
    result = step1_search("What is the daily UPI transfer limit?", doc_override="doc_atm")
    assert result["doc_id"] == "doc_atm"


def test_step1_search_override_ignores_question():
    """Even a completely unrelated question should respect the override."""
    result = step1_search("What is the meaning of life?", doc_override="doc_fd")
    assert result["doc_id"] == "doc_fd"


def test_step2_pick_tool_on_upi_returns_limit_lookup():
    doc = {"doc_id": "doc_upi", "text": DOCUMENTS["doc_upi"]["text"]}
    result = step2_pick_tool("What is the daily UPI limit?", doc)
    assert result["tool_name"] == "limit_lookup"


def test_step2_pick_tool_on_neft_returns_fee_calculator():
    doc = {"doc_id": "doc_neft", "text": DOCUMENTS["doc_neft"]["text"]}
    result = step2_pick_tool("What fee applies to NEFT?", doc)
    assert result["tool_name"] == "fee_calculator"


def test_step2_pick_tool_tool_override():
    doc = {"doc_id": "doc_upi", "text": DOCUMENTS["doc_upi"]["text"]}
    result = step2_pick_tool("What is the daily UPI limit?", doc, tool_override="penalty_calculator")
    assert result["tool_name"] == "penalty_calculator"


def test_step2_pick_tool_override_ignores_question():
    doc = {"doc_id": "doc_neft", "text": DOCUMENTS["doc_neft"]["text"]}
    result = step2_pick_tool("What fee applies to NEFT?", doc, tool_override="limit_lookup")
    assert result["tool_name"] == "limit_lookup"


def test_step2_pick_tool_returns_tool_output():
    doc = {"doc_id": "doc_upi", "text": DOCUMENTS["doc_upi"]["text"]}
    result = step2_pick_tool("What is the daily UPI limit?", doc)
    assert "tool_output" in result
    assert isinstance(result["tool_output"], str)
    assert len(result["tool_output"]) > 0


def test_step3_answer_returns_tool_output():
    doc = {"doc_id": "doc_upi", "text": DOCUMENTS["doc_upi"]["text"]}
    tool_result = {"tool_name": "limit_lookup", "tool_output": "daily limit is 2,00,000"}
    answer = step3_answer("What is the daily UPI limit?", doc, tool_result)
    assert answer == tool_result["tool_output"]


def test_step3_answer_inject_bug_returns_wrong_value():
    """When inject_bug=True, the answer should NOT contain the correct keywords."""
    doc = {"doc_id": "doc_fd", "text": DOCUMENTS["doc_fd"]["text"]}
    tool_result = {"tool_name": "penalty_calculator", "tool_output": "Penalty information: penalty of 1%"}
    answer = step3_answer("What is the penalty for premature FD withdrawal?", doc, tool_result, inject_bug=True)
    # The bug should replace the correct output with a wrong one (5%)
    assert "5%" in answer, f"Expected 5% in bug-injected answer, got: {answer}"
    assert "1%" not in answer, f"Bug-injected answer should not contain 1%, got: {answer}"


def test_step3_answer_inject_bug_no_correct_keywords():
    """Even with correct doc/tool, inject_bug=True should make the answer wrong."""
    doc = {"doc_id": "doc_fd", "text": DOCUMENTS["doc_fd"]["text"]}
    tool_result = {"tool_name": "penalty_calculator", "tool_output": "Penalty information: penalty of 1%"}
    answer = step3_answer("What is the penalty for premature FD withdrawal?", doc, tool_result, inject_bug=True)
    from attribution import is_correct
    expected_kw = ["1%", "penalty"]
    assert not is_correct(answer, expected_kw), (
        f"Bug-injected answer '{answer}' should not match keywords {expected_kw}"
    )
