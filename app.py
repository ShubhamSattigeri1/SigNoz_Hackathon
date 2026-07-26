import os
os.environ["GRADIO_SSR_MODE"] = "0"

import gradio as gr
from backend.main import app as backend_app

_blocks = gr.Blocks(title="Agent-RCA Backend")
with _blocks:
    gr.Markdown("### Agent Root-Cause Attribution")

app = gr.mount_gradio_app(backend_app, _blocks, path="/")

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
