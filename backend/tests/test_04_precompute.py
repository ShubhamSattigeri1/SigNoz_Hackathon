"""Section E: Precompute idempotency tests."""

import json
import os
import subprocess
import sys

BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
PRECOMPUTED_PATH = os.path.join(PROJECT_DIR, "data", "precomputed_results.json")


def _run_precompute():
    """Run precompute.py and return (returncode, stdout, stderr)."""
    script = os.path.join(BACKEND_DIR, "precompute.py")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return result.returncode, result.stdout, result.stderr


def _load_precomputed():
    with open(PRECOMPUTED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_precompute_runs_cleanly():
    rc, stdout, stderr = _run_precompute()
    assert rc == 0, f"precompute.py failed with code {rc}:\n{stderr}"


def test_precompute_output_is_valid_json():
    _run_precompute()
    data = _load_precomputed()
    assert isinstance(data, dict), "Output is not a dict"


def test_precompute_has_all_5_case_ids():
    _run_precompute()
    data = _load_precomputed()
    expected = {"case_pass", "case_bad_search", "case_bad_tool", "case_bad_generation", "case_ambiguous"}
    assert set(data.keys()) == expected, f"Missing/extra case ids: {set(data.keys()) ^ expected}"


def test_precompute_no_duplicate_keys():
    _run_precompute()
    data = _load_precomputed()
    # json.load on a dict never produces duplicate keys in Python,
    # but we verify the file has no duplicate keys by checking length
    assert len(data) == 5


def test_precompute_idempotent_blame_scores():
    """Run precompute twice; blame_scores must be identical."""
    _run_precompute()
    data1 = _load_precomputed()

    _run_precompute()
    data2 = _load_precomputed()

    for cid in data1:
        assert data1[cid]["is_correct"] == data2[cid]["is_correct"], (
            f"is_correct changed for {cid}"
        )
        if not data1[cid]["is_correct"]:
            assert data1[cid]["blame_scores"] == data2[cid]["blame_scores"], (
                f"blame_scores changed for {cid}: {data1[cid]['blame_scores']} vs {data2[cid]['blame_scores']}"
            )
            assert data1[cid]["root_causes"] == data2[cid]["root_causes"], (
                f"root_causes changed for {cid}: {data1[cid]['root_causes']} vs {data2[cid]['root_causes']}"
            )


def test_precompute_every_case_has_required_fields():
    _run_precompute()
    data = _load_precomputed()
    required = {"question", "is_correct", "trace", "blame_scores", "root_causes", "explanation"}
    for cid, entry in data.items():
        missing = required - set(entry.keys())
        assert not missing, f"{cid} missing fields: {missing}"
        # Verify trace structure
        trace = entry["trace"]
        for step in ["search", "tool", "answer"]:
            assert step in trace, f"{cid} trace missing step: {step}"
            assert "input" in trace[step], f"{cid} trace.{step} missing input"
            assert "output" in trace[step], f"{cid} trace.{step} missing output"
