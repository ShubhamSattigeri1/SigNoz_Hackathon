import os
os.environ["GRADIO_SSR_MODE"] = "0"

import gradio as gr
from backend.main import app as backend_app

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

internal = demo.app
for route in backend_app.routes:
    internal.routes.append(route)