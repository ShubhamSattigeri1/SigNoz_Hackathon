import os
os.environ["GRADIO_SSR_MODE"] = "0"

import uvicorn
import gradio as gr
from backend.main import app as backend_app

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

original_launch = demo.launch
def patched_launch(*args, **kwargs):
    combined = gr.mount_gradio_app(backend_app, demo, path="/")
    uvicorn.run(combined, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
demo.launch = patched_launch
