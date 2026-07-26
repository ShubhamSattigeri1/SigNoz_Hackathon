import os
os.environ["GRADIO_SSR_MODE"] = "0"

import threading
import gradio as gr
from backend.main import app as backend_app

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")

combined = gr.mount_gradio_app(backend_app, demo, path="/")

demo.launch = lambda *a, **kw: None

import uvicorn
port = int(os.getenv("PORT", "7860"))
threading.Thread(target=uvicorn.run, args=(combined,), kwargs={"host": "0.0.0.0", "port": port}).start()
