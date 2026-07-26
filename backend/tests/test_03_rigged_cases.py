"""Section D — CRITICAL: The 5 rigged cases.

This is the single most important test block. These define whether the
attribution engine works correctly.
"""

import pytest
from attribution import diagnose, run_pipeline


def _run_full_diagnosis(case_id, case_fixture):
    """Run pipeline -> diagnose for a single case and return structured results."""
    trace = run_pipeline(case_fixture)
    diag = diagnose(case_fixture)
    return {
        "case_id": case_id,
        "is_correct": trace["is_correct"],
        "root_causes": diag["root_causes"],
        "blame_scores": diag["blame_scores"],
        "original_correct": diag.get("original_correct", trace["is_correct"]),
    }


def test_case_pass(case_pass):
    result = _run_full_diagnosis("case_pass", case_pass)
    assert result["is_correct"] is True, f"Expected pass to be correct, got: {result}"
    assert result["root_causes"] == [], f"Expected empty root_causes, got: {result['root_causes']}"
    assert result["blame_scores"] == {}, f"Expected empty blame_scores, got: {result['blame_scores']}"


def test_case_bad_search(case_bad_search):
    result = _run_full_diagnosis("case_bad_search", case_bad_search)
    assert result["is_correct"] is False, f"Expected fail, got: {result}"
    assert result["root_causes"] == ["search"], (
        f"Expected root_causes=['search'], got: {result['root_causes']}"
    )
    assert result["blame_scores"].get("search", 0) > 0, (
        f"Search should have positive blame, got: {result['blame_scores']}"
    )


def test_case_bad_tool(case_bad_tool):
    result = _run_full_diagnosis("case_bad_tool", case_bad_tool)
    assert result["is_correct"] is False, f"Expected fail, got: {result}"
    assert result["root_causes"] == ["tool"], (
        f"Expected root_causes=['tool'], got: {result['root_causes']}"
    )
    assert result["blame_scores"].get("tool", 0) > 0, (
        f"Tool should have positive blame, got: {result['blame_scores']}"
    )


def test_case_bad_generation(case_bad_generation):
    result = _run_full_diagnosis("case_bad_generation", case_bad_generation)
    assert result["is_correct"] is False, f"Expected fail, got: {result}"
    assert result["root_causes"] == ["answer"], (
        f"Expected root_causes=['answer'], got: {result['root_causes']}"
    )
    assert result["blame_scores"].get("answer", 0) > 0, (
        f"Answer should have positive blame, got: {result['blame_scores']}"
    )


def test_case_ambiguous(case_ambiguous):
    result = _run_full_diagnosis("case_ambiguous", case_ambiguous)
    assert result["is_correct"] is False, f"Expected fail, got: {result}"
    assert "search" in result["root_causes"], (
        f"Expected search in root_causes, got: {result['root_causes']}"
    )
    assert "tool" in result["root_causes"], (
        f"Expected tool in root_causes, got: {result['root_causes']}"
    )
    assert result["blame_scores"].get("search", 0) > 0, (
        f"Search should have positive blame, got: {result['blame_scores']}"
    )
    assert result["blame_scores"].get("tool", 0) > 0, (
        f"Tool should have positive blame, got: {result['blame_scores']}"
    )


def test_diagnosis_determinism(case_bad_search, case_bad_tool, case_bad_generation, case_ambiguous):
    """Run diagnose() twice on each failing case; root_causes must be identical."""
    cases = [case_bad_search, case_bad_tool, case_bad_generation, case_ambiguous]
    for case in cases:
        d1 = diagnose(case)
        d2 = diagnose(case)
        assert d1["root_causes"] == d2["root_causes"], (
            f"Non-deterministic root_causes for {case['id']}: {d1['root_causes']} vs {d2['root_causes']}"
        )
        assert d1["blame_scores"] == d2["blame_scores"], (
            f"Non-deterministic blame_scores for {case['id']}: {d1['blame_scores']} vs {d2['blame_scores']}"
        )
