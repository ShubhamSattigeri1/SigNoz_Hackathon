from opentelemetry import trace
from corpus import search_documents, get_doc
from tools import TOOL_MAP, route_tool
from llm_client import call_groq

tracer = trace.get_tracer(__name__)
WRONG_ANSWER_BUG = "The penalty for premature FD withdrawal is 5%."

def step1_search(question: str, doc_override: str | None = None) -> dict:
    with tracer.start_as_current_span("pipeline.search") as span:
        span.set_attribute("question", question)
        span.set_attribute("doc_override", str(doc_override))
        if doc_override is not None:
            doc = get_doc(doc_override)
        else:
            doc = search_documents(question)
        span.set_attribute("retrieved_doc_id", doc["doc_id"])
        return doc

def step2_pick_tool(question: str, doc: dict, tool_override: str | None = None) -> dict:
    with tracer.start_as_current_span("pipeline.tool") as span:
        span.set_attribute("question", question)
        span.set_attribute("tool_override", str(tool_override))
        if tool_override is not None:
            tool_name = tool_override
        else:
            tool_name = route_tool(question)

        tool_fn = TOOL_MAP[tool_name]
        tool_output = tool_fn(doc["text"])
        span.set_attribute("tool_name", tool_name)
        return {"tool_name": tool_name, "tool_output": tool_output}

def step3_answer(question: str, doc: dict, tool_result: dict, inject_bug: bool = False) -> str:
    with tracer.start_as_current_span("pipeline.answer") as span:
        span.set_attribute("question", question)
        span.set_attribute("inject_bug", str(inject_bug))
        if inject_bug:
            answer = WRONG_ANSWER_BUG
        else:
            answer = f"{tool_result['tool_output']}"
        span.set_attribute("answer_length", len(answer))
        return answer
