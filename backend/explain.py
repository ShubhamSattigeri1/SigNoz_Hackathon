from llm_client import call_groq

EXPLANATION_PROMPT = """An AI pipeline produced an incorrect answer. Testing showed that fixing the step below would have corrected the final answer.

Step name: {step_name}
What this step actually produced: {actual_output}
What it should have produced instead: {correct_output}
Question the pipeline was answering: {question}

In exactly 1-2 plain-English sentences, explain why this step's output likely caused the wrong final answer. Do not mention "SHAP," "ablation," or "ground truth." Do not restate the question.

EXPLANATION:"""

FALLBACK_MESSAGE = "Explanation generation is temporarily unavailable. See the raw input/output values above for this step."

def generate_explanation(step_name: str, actual_output: str, correct_output: str, question: str) -> str:
    prompt = EXPLANATION_PROMPT.format(
        step_name=step_name,
        actual_output=actual_output,
        correct_output=correct_output,
        question=question,
    )
    try:
        return call_groq(prompt, temperature=0, max_tokens=100, timeout_sec=10)
    except Exception:
        return FALLBACK_MESSAGE
