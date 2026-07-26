from opentelemetry import trace
from pipeline import step1_search, step2_pick_tool, step3_answer
from storage import save_trace

tracer = trace.get_tracer(__name__)

def is_correct(final_answer: str, expected_keywords: list[str]) -> bool:
    answer_lower = final_answer.lower()
    return all(kw.lower() in answer_lower for kw in expected_keywords)

def run_pipeline(case: dict, force_doc: str | None = None, force_tool: str | None = None, force_inject_bug: bool | None = None) -> dict:
    with tracer.start_as_current_span("pipeline.full_run") as span:
        span.set_attribute("case_id", case["id"])
        span.set_attribute("rigging", str(case.get("rigging", {})))

        question = case["question"]
        rigging = case.get("rigging", {})
        doc_override = rigging.get("doc_override") if force_doc is None else force_doc
        tool_override = rigging.get("tool_override") if force_tool is None else force_tool
        inject_bug = rigging.get("inject_bug", False) if force_inject_bug is None else force_inject_bug

        doc = step1_search(question, doc_override=doc_override)
        tool_result = step2_pick_tool(question, doc, tool_override=tool_override)
        answer = step3_answer(question, doc, tool_result, inject_bug=inject_bug)

        expected_keywords = case["expected_keywords"]
        correct = is_correct(answer, expected_keywords)
        span.set_attribute("is_correct", correct)

        trace = {
            "case_id": case["id"],
            "question": question,
            "steps": {
                "search": {
                    "input": f"question={question}, doc_override={doc_override}",
                    "output": doc,
                },
                "tool": {
                    "input": f"question={question}, doc_id={doc['doc_id']}, tool_override={tool_override}",
                    "output": tool_result,
                },
                "answer": {
                    "input": f"question={question}, doc_id={doc['doc_id']}, tool_name={tool_result['tool_name']}, inject_bug={inject_bug}",
                    "output": answer,
                },
            },
            "final_answer": answer,
            "is_correct": correct,
        }

        save_trace(trace)
        return trace

def _run_ablation(case: dict, force_doc=None, force_tool=None, force_inject_bug=None):
    trace = run_pipeline(case, force_doc=force_doc, force_tool=force_tool, force_inject_bug=force_inject_bug)
    return trace, trace["is_correct"]

def diagnose(case: dict) -> dict:
    with tracer.start_as_current_span("attribution.diagnose") as span:
        span.set_attribute("case_id", case["id"])
        original_trace = run_pipeline(case)
        original_correct = original_trace["is_correct"]
        span.set_attribute("original_correct", original_correct)

        if original_correct:
            return {
                "blame_scores": {},
                "root_causes": [],
                "original_correct": True,
            }

        scores = {}

        with tracer.start_as_current_span("attribution.ablation.search") as s:
            trace_fix1, c1 = _run_ablation(case, force_doc=case["correct_doc"])
            scores["search"] = int(c1) - int(original_correct)
            s.set_attribute("corrected", c1)

        with tracer.start_as_current_span("attribution.ablation.tool") as s:
            trace_fix2, c2 = _run_ablation(case, force_tool=case["correct_tool"])
            scores["tool"] = int(c2) - int(original_correct)
            s.set_attribute("corrected", c2)

        with tracer.start_as_current_span("attribution.ablation.answer") as s:
            trace_fix3, c3 = _run_ablation(case, force_inject_bug=False)
            scores["answer"] = int(c3) - int(original_correct)
            s.set_attribute("corrected", c3)

        positive = {k: max(v, 0) for k, v in scores.items()}
        total = sum(positive.values())

        if total > 0:
            normalized = {k: v / total for k, v in positive.items()}
            max_score = max(normalized.values())
            root_causes = [k for k, v in normalized.items() if (max_score - v) <= 0.15]
        else:
            t1, _ = _run_ablation(case, force_doc=case["correct_doc"])
            t2, _ = _run_ablation(case, force_tool=case["correct_tool"])
            t3, _ = _run_ablation(case, force_inject_bug=False)
            changed = {
                "search": t1["final_answer"] != original_trace["final_answer"],
                "tool": t2["final_answer"] != original_trace["final_answer"],
                "answer": t3["final_answer"] != original_trace["final_answer"],
            }
            n_changed = sum(1 for v in changed.values() if v)
            if n_changed > 0:
                normalized = {k: (1.0 / n_changed if v else 0) for k, v in changed.items()}
                root_causes = [k for k, v in normalized.items() if v > 0]
            else:
                normalized = {"search": 0, "tool": 0, "answer": 0}
                root_causes = []

        span.set_attribute("blame_scores", str(normalized))
        span.set_attribute("root_causes", str(root_causes))

        return {
            "blame_scores": normalized,
            "root_causes": root_causes,
            "original_correct": False,
        }
