import os
os.environ["GRADIO_SSR_MODE"] = "0"

import gradio as gr
from backend.main import app as backend_app

class _Blocks(gr.Blocks):
    def queue(self, *a, **kw):
        return self
    def launch(self, *a, **kw):
        import uvicorn
        combined = gr.mount_gradio_app(backend_app, self, path="/")
        uvicorn.run(combined, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))

demo = _Blocks(title="Agent-RCA Backend")
with demo:
    gr.Markdown("### Agent Root-Cause Attribution")
