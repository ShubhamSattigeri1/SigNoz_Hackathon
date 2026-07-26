import os
# Disable SSR (Node.js proxy) — must be set BEFORE gradio import
os.environ["GRADIO_SSR_MODE"] = "0"

import gradio as gr
from backend.main import app as fastapi_backend

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

# Merge Gradio into FastAPI — single server, single port
app = gr.mount_gradio_app(fastapi_backend, demo, path="/")