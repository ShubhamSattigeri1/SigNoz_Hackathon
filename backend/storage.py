import json
import os

TRACES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "traces")

def save_trace(trace: dict):
    os.makedirs(TRACES_DIR, exist_ok=True)
    case_id = trace["case_id"]
    path = os.path.join(TRACES_DIR, f"{case_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

def load_trace(case_id: str) -> dict:
    path = os.path.join(TRACES_DIR, f"{case_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Trace not found for case: {case_id}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
