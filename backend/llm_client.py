import os
from groq import Groq
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def call_groq(prompt: str, temperature: float = 0, max_tokens: int = 200, timeout_sec: int = 15) -> str:
    with tracer.start_as_current_span("llm.groq_call") as span:
        span.set_attribute("model", "openai/gpt-oss-20b")
        span.set_attribute("prompt_length", len(prompt))
        span.set_attribute("temperature", temperature)
        span.set_attribute("max_tokens", max_tokens)

        client = get_groq_client()
        if client is None:
            span.set_status(Status(StatusCode.ERROR, "GROQ_API_KEY not set"))
            raise RuntimeError("GROQ_API_KEY not set")

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout_sec,
            )
            msg = response.choices[0].message
            content = msg.content or msg.reasoning or ""
            span.set_attribute("response_length", len(content))
            span.set_attribute("success", True)
            return content.strip()
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise RuntimeError(f"Groq API call failed: {e}")
