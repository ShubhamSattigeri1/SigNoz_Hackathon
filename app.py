import os
import gradio as gr

from backend.main import app as backend_app

demo = gr.Blocks(title="Agent-RCA Backend")

with demo:
    gr.Markdown("### Agent Root-Cause Attribution")
    gr.Markdown("API server is running.")

internal_app = demo.app  # Gradio 6.x internal FastAPI app
for route in backend_app.routes:
    internal_app.routes.append(route)