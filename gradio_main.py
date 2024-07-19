import gradio as gr

from chatbot import get_llm_resposne

with gr.Blocks() as block:
    gr.ChatInterface(fn=get_llm_resposne, multimodal=True, fill_height=False)

    # hello