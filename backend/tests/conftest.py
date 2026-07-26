import os
import sys
import pytest

BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BACKEND_DIR)

from test_cases import CASES, get_case
from attribution import run_pipeline, diagnose, is_correct

@pytest.fixture(autouse=True)
def reset_traces_dir():
    """Ensure traces directory exists before each test."""
    traces_dir = os.path.join(os.path.dirname(BACKEND_DIR), "data", "traces")
    os.makedirs(traces_dir, exist_ok=True)
    yield

@pytest.fixture(params=CASES, ids=[c["id"] for c in CASES])
def each_case(request):
    return request.param

@pytest.fixture
def case_pass():
    return get_case("case_pass")

@pytest.fixture
def case_bad_search():
    return get_case("case_bad_search")

@pytest.fixture
def case_bad_tool():
    return get_case("case_bad_tool")

@pytest.fixture
def case_bad_generation():
    return get_case("case_bad_generation")

@pytest.fixture
def case_ambiguous():
    return get_case("case_ambiguous")
