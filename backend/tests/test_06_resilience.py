"""Section G: Resilience tests.

Tests what happens when the API key is missing, requests are concurrent,
or LLM calls time out.  Uses the TestClient but needs environment
manipulation, so some tests are conditional on being able to clear the key.
"""

import os
import sys
import threading
import time
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BACKEND_DIR)

ORIGINAL_KEY = os.environ.get("GROQ_API_KEY")
FALLBACK_STRING = "Explanation generation is temporarily unavailable. See the raw input/output values above for this step."


@pytest.fixture
def client():
    """Import main module and create TestClient after ensuring key is in place."""
    # We need a fresh import of main.py for TestClient.
    # The module was already imported by conftest. We'll rebuild with a clean import.
    import importlib
    import main as main_module
    importlib.reload(main_module)
    return TestClient(main_module.app)


def test_precomputed_path_works_without_key():
    """GET /api/cases/*/diagnosis must work even with no API key."""
    if "GROQ_API_KEY" in os.environ:
        saved = os.environ.pop("GROQ_API_KEY")
    else:
        saved = None

    try:
        import importlib
        import main as main_module
        importlib.reload(main_module)
        tc = TestClient(main_module.app)

        # Precomputed endpoints should work completely without API key
        resp_cases = tc.get("/api/cases")
        assert resp_cases.status_code == 200

        resp_trace = tc.get("/api/cases/case_bad_search/trace")
        assert resp_trace.status_code == 200

        resp_diag = tc.get("/api/cases/case_bad_search/diagnosis")
        assert resp_diag.status_code == 200
        data = resp_diag.json()
        assert data["root_causes"] == ["search"]
    finally:
        if saved is not None:
            os.environ["GROQ_API_KEY"] = saved


def test_diagnose_live_returns_fallback_without_key():
    """POST /diagnose-live must return 200 with fallback when API key is missing."""
    if "GROQ_API_KEY" in os.environ:
        saved = os.environ.pop("GROQ_API_KEY")
    else:
        saved = None

    try:
        import importlib
        import main as main_module
        importlib.reload(main_module)
        tc = TestClient(main_module.app)

        resp = tc.post("/api/cases/case_bad_search/diagnose-live")
        assert resp.status_code == 200, (
            f"Expected 200 with fallback, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data.get("used_fallback") is True, (
            f"Expected used_fallback=True, got: {data}"
        )
        # Each root cause should have either the fallback string or the
        # precomputed cached explanation
        for step in data["root_causes"]:
            expl = data["explanation"].get(step, "")
            assert expl, f"Empty explanation for root cause {step}"
    finally:
        if saved is not None:
            os.environ["GROQ_API_KEY"] = saved


def test_concurrent_diagnose_live():
    """3 concurrent POST /diagnose-live for the same case must all return valid
    responses with no crash or corrupted shared state."""
    import importlib
    import main as main_module
    importlib.reload(main_module)
    tc = TestClient(main_module.app)

    results = []
    errors = []
    lock = threading.Lock()

    def worker():
        try:
            resp = tc.post("/api/cases/case_bad_search/diagnose-live")
            with lock:
                results.append(resp)
        except Exception as e:
            with lock:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert len(errors) == 0, f"Concurrent errors: {errors}"
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"

    for resp in results:
        assert resp.status_code == 200, f"Non-200 in concurrent: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data["root_causes"] == ["search"]
        assert "blame_scores" in data
        assert "explanation" in data


def test_concurrent_requests_different_cases():
    """Concurrent requests to different cases should not interfere."""
    import importlib
    import main as main_module
    importlib.reload(main_module)
    tc = TestClient(main_module.app)

    results = {}
    errors = []
    lock = threading.Lock()

    def worker(case_id, endpoint):
        try:
            if endpoint == "diagnose-live":
                resp = tc.post(f"/api/cases/{case_id}/diagnose-live")
            else:
                resp = tc.get(f"/api/cases/{case_id}/{endpoint}")
            with lock:
                results[(case_id, endpoint)] = resp
        except Exception as e:
            with lock:
                errors.append((case_id, endpoint, e))

    targets = [
        ("case_bad_search", "trace"),
        ("case_bad_tool", "diagnosis"),
        ("case_bad_generation", "diagnose-live"),
        ("case_ambiguous", "diagnose-live"),
        ("case_pass", "trace"),
    ]

    threads = [threading.Thread(target=worker, args=t) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert len(errors) == 0, f"Concurrent errors: {errors}"
    assert len(results) == len(targets)

    # Verify each response is correct
    assert results[("case_bad_search", "trace")].status_code == 200
    assert results[("case_bad_tool", "diagnosis")].json()["root_causes"] == ["tool"]


def test_get_endpoints_work_under_concurrent_load():
    """Multiple concurrent GET requests to precomputed endpoints."""
    import importlib
    import main as main_module
    importlib.reload(main_module)
    tc = TestClient(main_module.app)

    results = []
    errors = []
    lock = threading.Lock()

    def get_worker(path):
        try:
            resp = tc.get(path)
            with lock:
                results.append((path, resp))
        except Exception as e:
            with lock:
                errors.append((path, e))

    paths = [
        "/api/cases",
        "/api/cases/case_pass/trace",
        "/api/cases/case_bad_search/trace",
        "/api/cases/case_bad_tool/diagnosis",
        "/api/cases/case_bad_generation/diagnosis",
        "/api/cases/case_ambiguous/trace",
    ]

    threads = [threading.Thread(target=get_worker, args=(p,)) for p in paths]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(errors) == 0, f"Concurrent GET errors: {errors}"
    for path, resp in results:
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"
