from gradio_main import block
from fastapi import FastAPI
import gradio as gr
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=[''],
        allow_headers=['']
    )
]

app = FastAPI(middleware=middleware)

app = gr.mount_gradio_app(app, block, path='/')
