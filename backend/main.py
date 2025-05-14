# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router

app = FastAPI(title="Web Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(router)

