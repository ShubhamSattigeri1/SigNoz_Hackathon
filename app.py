import os
import threading
import uvicorn
import gradio as gr

def run_api():
    from backend.main import app
    uvicorn.run(app, host="0.0.0.0", port=7860)

threading.Thread(target=run_api, daemon=True).start()

with gr.Blocks(title="Agent-RCA Backend") as demo:
    gr.Markdown("### Agent Root-Cause Attribution")
    gr.Markdown("API server is running. Connect your Vercel frontend.")

demo.launch()
