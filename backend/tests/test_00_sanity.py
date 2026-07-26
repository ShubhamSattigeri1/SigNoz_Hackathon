"""Section A: Environment sanity checks."""

import os
import subprocess
import sys

BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")

REQUIRED_FILES = [
    "backend/main.py",
    "backend/pipeline.py",
    "backend/tools.py",
    "backend/corpus.py",
    "backend/test_cases.py",
    "backend/attribution.py",
    "backend/explain.py",
    "backend/llm_client.py",
    "backend/storage.py",
    "backend/precompute.py",
    "frontend/src/App.jsx",
    "frontend/src/components/CaseSelector.jsx",
    "frontend/src/components/ExplanationPanel.jsx",
    "frontend/src/components/TraceTimeline.jsx",
    "frontend/src/api.js",
    "frontend/src/main.jsx",
    "data/precomputed_results.json",
    ".env.example",
    "README.md",
    "run.sh",
]


def test_all_required_files_exist():
    missing = []
    for rel_path in REQUIRED_FILES:
        full = os.path.join(PROJECT_DIR, rel_path)
        if not os.path.exists(full):
            missing.append(rel_path)
    assert missing == [], f"Missing files: {missing}"


def test_requirements_install_clean():
    req_file = os.path.join(BACKEND_DIR, "requirements.txt")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_file, "--dry-run"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"pip install --dry-run failed:\n{result.stderr}"


def test_npm_install_clean():
    lock_file = os.path.join(FRONTEND_DIR, "package-lock.json")
    assert os.path.exists(lock_file), "package-lock.json missing — run npm install first"
