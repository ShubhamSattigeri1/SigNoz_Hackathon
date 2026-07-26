"""Section B: Unit tests for corpus.py and tools.py."""

import pytest
from corpus import DOCUMENTS, get_doc, search_documents
from tools import limit_lookup, fee_calculator, penalty_calculator, route_tool

EXPECTED_DOC_IDS = {"doc_upi", "doc_neft", "doc_atm", "doc_pmla", "doc_fd", "doc_closure"}


def test_corpus_has_exactly_6_documents():
    assert len(DOCUMENTS) == 6
    assert set(DOCUMENTS.keys()) == EXPECTED_DOC_IDS


def test_every_doc_has_non_empty_text():
    for doc_id, doc in DOCUMENTS.items():
        assert doc.get("text"), f"{doc_id} has empty text"
        assert len(doc["text"].strip()) > 0, f"{doc_id} has only whitespace text"


def test_every_doc_has_title():
    for doc_id, doc in DOCUMENTS.items():
        assert doc.get("title"), f"{doc_id} has empty title"


def test_get_doc_returns_correct_format():
    result = get_doc("doc_upi")
    assert result["doc_id"] == "doc_upi"
    assert "title" in result
    assert "text" in result
    assert "UPI" in result["text"]


def test_get_doc_unknown_raises():
    with pytest.raises(ValueError, match="Unknown document id"):
        get_doc("nonexistent")


def test_search_documents_upi_question():
    result = search_documents("What is the daily UPI transfer limit?")
    assert result["doc_id"] == "doc_upi"


def test_search_documents_fd_question():
    result = search_documents("What is the penalty for premature FD withdrawal?")
    assert result["doc_id"] == "doc_fd"


def test_search_documents_atm_question():
    result = search_documents("What is the ATM withdrawal limit per day?")
    assert result["doc_id"] == "doc_atm"


# ---- tool tests ----

def test_limit_lookup_on_doc_upi():
    text = DOCUMENTS["doc_upi"]["text"]
    result = limit_lookup(text)
    assert "2,00,000" in result, f"Expected '2,00,000' in limit_lookup result, got: {result}"
    assert "UPI" in result


def test_limit_lookup_on_doc_atm():
    text = DOCUMENTS["doc_atm"]["text"]
    result = limit_lookup(text)
    assert "40,000" in result, f"Expected '40,000' in limit_lookup result, got: {result}"


def test_fee_calculator_on_doc_neft():
    text = DOCUMENTS["doc_neft"]["text"]
    result = fee_calculator(text)
    assert "no fee" in result.lower(), f"Expected 'no fee' in result, got: {result}"
    assert "₹10,000" in result or "10,000" in result
    assert "₹25" in result or "25" in result.replace(",", "")


def test_fee_calculator_on_doc_atm():
    """ATM doc has no fee info, should return 'no specific fee information'."""
    text = DOCUMENTS["doc_atm"]["text"]
    result = fee_calculator(text)
    assert "no specific fee" in result.lower()


def test_penalty_calculator_on_doc_fd():
    text = DOCUMENTS["doc_fd"]["text"]
    result = penalty_calculator(text)
    assert "1%" in result, f"Expected '1%' in penalty_calculator result, got: {result}"
    assert "penalty" in result.lower()


def test_penalty_calculator_on_doc_upi():
    """UPI doc has no penalty info, should return 'no specific penalty'."""
    text = DOCUMENTS["doc_upi"]["text"]
    result = penalty_calculator(text)
    assert "no specific penalty" in result.lower()


def test_route_tool_limit_question():
    assert route_tool("What is the daily limit?") == "limit_lookup"


def test_route_tool_fee_question():
    assert route_tool("What fee applies?") == "fee_calculator"


def test_route_tool_penalty_question():
    assert route_tool("What is the penalty?") == "penalty_calculator"


def test_route_tool_default():
    assert route_tool("Some random question") == "limit_lookup"
