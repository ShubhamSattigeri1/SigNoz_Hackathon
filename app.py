import os
import gradio as gr

from backend.main import app as backend_app

demo = gr.Blocks(title="Agent-RCA Backend", ssr_mode=False)

with demo:
    gr.Markdown("### Agent Root-Cause Attribution")
    gr.Markdown("API server is running.")

internal = demo.app
for route in backend_app.routes:
    internal.routes.append(route)

if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))