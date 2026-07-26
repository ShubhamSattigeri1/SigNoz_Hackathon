import os
import gradio as gr

from backend.main import app as backend_app

demo = gr.Blocks(title="Agent-RCA Backend")

with demo:
    gr.Markdown("### Agent Root-Cause Attribution")
    gr.Markdown("API server is running.")

# Gradio 6.x: demo.app IS the internal FastAPI app already
internal_app = demo.app
for route in backend_app.routes:
    internal_app.routes.append(route)
for key, handler in backend_app.exception_handlers.items():
    internal_app.exception_handlers[key] = handler