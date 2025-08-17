from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .groq_client import groq_summarize
from .emailer import send_email
import os
from pathlib import Path

app = FastAPI()

# Enable CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://localhost:3000",
        "https://mongo-deskfront.vercel.app",  # Your frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the frontend directory
frontend_dir = Path(__file__).parent.parent.parent / "frontend"

# Mount the static files
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def read_root():
    return {"status": "API is running"}

class GenerateRequest(BaseModel):
    transcript: str
    prompt: str | None = None

class GenerateResponse(BaseModel):
    summary: str
    error: str | None = None

@app.post("/api/generate")
async def generate(req: GenerateRequest):
    try:
        if not req.transcript.strip():
            raise ValueError("Transcript cannot be empty")
        
        summary = groq_summarize(req.transcript, req.prompt or "")
        return GenerateResponse(summary=summary, error=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SendRequest(BaseModel):
    subject: str
    body: str
    recipients: list[str]

@app.post("/api/send")
async def send(req: SendRequest):
    try:
        if not req.recipients:
            raise ValueError("Recipients list cannot be empty")
        if not req.body.strip():
            raise ValueError("Email body cannot be empty")
            
        send_email(req.subject, req.body, req.recipients)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))