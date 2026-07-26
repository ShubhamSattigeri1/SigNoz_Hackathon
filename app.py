import os
import gradio as gr
import uvicorn

from backend.main import app as fastapi_app

def _make_blocks():
    with gr.Blocks(title="Agent-RCA Backend") as demo:
        gr.Markdown("### Agent Root-Cause Attribution")
    return demo

app = gr.mount_gradio_app(fastapi_app, _make_blocks(), path="/")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)