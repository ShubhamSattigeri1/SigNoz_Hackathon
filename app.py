import os
os.environ["GRADIO_SSR_MODE"] = "0"

import uvicorn
import gradio as gr
from backend.main import app as backend_app

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

app = gr.mount_gradio_app(backend_app, demo, path="/")

port = int(os.getenv("PORT", "7860"))
uvicorn.run(app, host="0.0.0.0", port=port)