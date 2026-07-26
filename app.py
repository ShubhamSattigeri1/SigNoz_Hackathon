import os
import uvicorn
import gradio as gr

from backend.main import app as fastapi_app

gr_app = gr.Blocks(title="Agent-RCA Backend")
with gr_app:
    gr.Markdown("### Agent Root-Cause Attribution")
    gr.Markdown("API server is running at `/api/`")
    gr.Markdown("Connect your Vercel frontend with `VITE_API_BASE` set to this Space URL.")

app = gr.mount_gradio_app(fastapi_app, gr_app, path="/")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
