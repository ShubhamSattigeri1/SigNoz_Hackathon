import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_cases import CASES
from attribution import run_pipeline, diagnose
from explain import generate_explanation

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
PRECOMPUTED_PATH = os.path.join(DATA_DIR, "precomputed_results.json")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    results = {}

    for case in CASES:
        case_id = case["id"]
        print(f"Processing {case_id}...")

        trace = run_pipeline(case)

        if trace["is_correct"]:
            results[case_id] = {
                "question": case["question"],
                "is_correct": True,
                "blame_scores": {},
                "root_causes": [],
                "explanation": None,
                "trace": {
                    "search": trace["steps"]["search"],
                    "tool": trace["steps"]["tool"],
                    "answer": trace["steps"]["answer"],
                },
            }
            print(f"  -> PASS (correct)")
        else:
            diag = diagnose(case)
            explanations = {}
            for step in diag["root_causes"]:
                step_name = step
                actual_output = str(trace["steps"][step]["output"])
                correct_step_output = _get_correct_output(case, step)
                explanations[step] = generate_explanation(
                    step_name, actual_output, correct_step_output, case["question"]
                )

            results[case_id] = {
                "question": case["question"],
                "is_correct": False,
                "blame_scores": diag["blame_scores"],
                "root_causes": diag["root_causes"],
                "explanation": explanations,
                "trace": {
                    "search": trace["steps"]["search"],
                    "tool": trace["steps"]["tool"],
                    "answer": trace["steps"]["answer"],
                },
            }
            print(f"  -> FAIL, root_causes={diag['root_causes']}, blame_scores={diag['blame_scores']}")

    with open(PRECOMPUTED_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nPrecomputed results written to {PRECOMPUTED_PATH}")
    print("\nSummary:")
    for case_id, data in results.items():
        status = "PASS" if data["is_correct"] else "FAIL"
        causes = data["root_causes"] if data["root_causes"] else "N/A"
        print(f"  {case_id}: {status}  root_causes={causes}")

def _get_correct_output(case: dict, step: str) -> str:
    from corpus import get_doc
    from tools import TOOL_MAP
    if step == "search":
        doc = get_doc(case["correct_doc"])
        return f"doc_id={doc['doc_id']}, text={doc['text']}"
    elif step == "tool":
        doc = get_doc(case["correct_doc"])
        tool_fn = TOOL_MAP[case["correct_tool"]]
        output = tool_fn(doc["text"])
        return f"tool_name={case['correct_tool']}, tool_output={output}"
    elif step == "answer":
        return "Correct generation with inject_bug=False"
    return ""

if __name__ == "__main__":
    main()
