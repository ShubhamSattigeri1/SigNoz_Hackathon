import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from otel import init_otel

load_dotenv()

try:
    init_otel()
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    RequestsInstrumentor().instrument()
except Exception:
    pass  # OTel is optional; skip on Vercel serverless

app = FastAPI(title="Agent-RCA Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:7860",
        "https://*.hf.space",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRECOMPUTED_PATH = os.path.join(BASE_DIR, "..", "data", "precomputed_results.json")

def _load_precomputed() -> dict:
    if not os.path.exists(PRECOMPUTED_PATH):
        return {}
    with open(PRECOMPUTED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_case_by_id(case_id: str) -> dict:
    from test_cases import CASES
    for c in CASES:
        if c["id"] == case_id:
            return c
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.get("/api/cases")
def list_cases():
    precomputed = _load_precomputed()
    from test_cases import CASES
    result = []
    for c in CASES:
        pc = precomputed.get(c["id"], {})
        result.append({
            "id": c["id"],
            "question": c["question"],
            "is_correct": pc.get("is_correct", False),
        })
    return result

@app.get("/api/cases/{case_id}/trace")
def get_trace(case_id: str):
    precomputed = _load_precomputed()
    pc = precomputed.get(case_id)
    if pc is None:
        raise HTTPException(status_code=404, detail="Case not found in precomputed results")
    trace = pc.get("trace", {})
    return {
        "case_id": case_id,
        "question": pc["question"],
        "steps": trace,
        "final_answer": trace.get("answer", {}).get("output", ""),
        "is_correct": pc["is_correct"],
    }

@app.get("/api/cases/{case_id}/diagnosis")
def get_diagnosis(case_id: str):
    precomputed = _load_precomputed()
    pc = precomputed.get(case_id)
    if pc is None:
        raise HTTPException(status_code=404, detail="Case not found in precomputed results")
    return {
        "blame_scores": pc.get("blame_scores", {}),
        "root_causes": pc.get("root_causes", []),
        "explanation": pc.get("explanation"),
        "original_correct": pc["is_correct"],
    }

@app.post("/api/cases/{case_id}/diagnose-live")
def diagnose_live(case_id: str):
    case = _get_case_by_id(case_id)
    from attribution import run_pipeline, diagnose
    from explain import generate_explanation, FALLBACK_MESSAGE
    from test_cases import CASES
    import copy

    case_copy = copy.deepcopy(case)
    trace = run_pipeline(case_copy)
    precomputed = _load_precomputed()

    if trace["is_correct"]:
        return {
            "blame_scores": {},
            "root_causes": [],
            "original_correct": True,
            "explanation": None,
            "used_fallback": False,
        }

    diag = diagnose(case_copy)
    explanations = {}
    used_fallback = False
    for step in diag["root_causes"]:
        from corpus import get_doc
        from tools import TOOL_MAP
        if step == "search":
            actual_output = str(trace["steps"]["search"]["output"])
            doc = get_doc(case_copy["correct_doc"])
            correct_output = f"doc_id={doc['doc_id']}, text={doc['text']}"
        elif step == "tool":
            actual_output = str(trace["steps"]["tool"]["output"])
            doc = get_doc(case_copy["correct_doc"])
            tool_fn = TOOL_MAP[case_copy["correct_tool"]]
            tool_out = tool_fn(doc["text"])
            correct_output = f"tool_name={case_copy['correct_tool']}, tool_output={tool_out}"
        elif step == "answer":
            actual_output = str(trace["steps"]["answer"]["output"])
            correct_output = "Correct generation with inject_bug=False"
        else:
            actual_output = ""
            correct_output = ""

        expl = generate_explanation(step, actual_output, correct_output, case_copy["question"])
        if expl == FALLBACK_MESSAGE:
            used_fallback = True
            precomputed_expl = precomputed.get(case_id, {}).get("explanation", {})
            if step in precomputed_expl:
                expl = precomputed_expl[step]

        explanations[step] = expl

    return {
        "blame_scores": diag["blame_scores"],
        "root_causes": diag["root_causes"],
        "original_correct": False,
        "explanation": explanations,
        "used_fallback": used_fallback,
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return {"status": "ok"}

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)
except Exception:
    pass  # OTel is optional; skip on Vercel serverless

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
