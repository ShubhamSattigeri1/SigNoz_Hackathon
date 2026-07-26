# Agent Root-Cause Attribution System (Agent-RCA)

A demo system that runs a toy 3-step AI pipeline, logs structured traces, and performs root-cause analysis via ablation swap testing.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Groq API key (get one free at https://console.groq.com)

### Setup

1. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate    # Windows
   source venv/bin/activate   # Linux/Mac
   ```

2. Install backend dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

3. Set your Groq API key:
   ```
   Copy .env.example to .env and add your key
   ```

4. Precompute results (runs all 5 test cases offline):
   ```
   python backend/precompute.py
   ```

5. Start the backend (port 8000):
   ```
   uvicorn backend.main:app --reload
   ```

6. In a separate terminal, start the frontend (port 5173):
   ```
   cd frontend
   npm install
   npm run dev
   ```

7. Open http://localhost:5173 in your browser.

### Running everything at once
```
bash run.sh
```

## Architecture

- **Backend**: FastAPI + Uvicorn (Python 3.11+)
- **Frontend**: React 18 + Vite
- **LLM**: Groq API (`openai/gpt-oss-20b`) for explanations
- **Persistence**: Flat JSON files under `data/`
- **Observability**: OpenTelemetry + SigNoz Cloud (distributed tracing)

## SigNoz Observability

The project is instrumented with OpenTelemetry to export traces to [SigNoz Cloud](https://signoz.cloud).

### What gets traced

**Backend (Python / FastAPI)**:
- All HTTP routes (auto-instrumented via `FastAPIInstrumentor`)
- Each pipeline step as a manual span (`pipeline.search`, `pipeline.tool`, `pipeline.answer`)
- Full pipeline runs (`pipeline.full_run`) with case_id, rigging, and correctness
- Attribution diagnosis (`attribution.diagnose`) with ablation sub-spans (`attribution.ablation.search`, etc.)
- LLM calls (`llm.groq_call`) capturing prompt length, response length, and errors

**Frontend (React / Browser)**:
- Page load timing (`DocumentLoadInstrumentation`)
- All fetch calls to the backend (`FetchInstrumentation`) with trace propagation
- Case selection (`ui.select_case`) with case_id attribute
- Recompute button clicks (`ui.recompute_click`) with root_causes result


## Test Cases

| Case ID | Rigging | Expected Root Cause |
|---|---|---|
| case_pass | None | None (should pass) |
| case_bad_search | Wrong doc retrieved | search |
| case_bad_tool | Wrong tool selected | tool |
| case_bad_generation | Bug in answer generation | answer |
| case_ambiguous | Both doc and tool wrong | search + tool (tied) |
