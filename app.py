import os
os.environ["GRADIO_SSR_MODE"] = "0"

import gradio as gr
from backend.main import app as backend_app

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

# Copy backend routes into Gradio's built-in FastAPI app
internal = demo.app  # Gradio's internal FastAPI app
for route in backend_app.routes:
    internal.routes.append(route)