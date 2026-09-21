"""
src/server.py

FastAPI backend server connecting the React Operations Dashboard directly
to the Telecom Copilot Inference Pipeline (powered by fine-tuned DoRA Flan-T5).

Endpoints:
  POST /chat            -> Runs full TelecomCopilot inference pipeline
  GET  /network-status  -> Returns real-time network status feed
  GET  /tickets         -> Returns logged customer support tickets
  GET  /health          -> Pipeline and model health check

Run:
    python -m src.server
    or: uvicorn src.server:app --host 0.0.0.0 --port 5000
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.pipeline.inference_pipeline import TelecomCopilot

app = FastAPI(
    title="Telecom Copilot API",
    description="Backend API powered by fine-tuned DoRA Flan-T5 generator",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite default is http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (loaded lazily on startup)
pipeline: Optional[TelecomCopilot] = None

@app.on_event("startup")
def startup_event():
    global pipeline
    print("\n[Server] Initializing Telecom Copilot with fine-tuned DoRA Flan-T5...")
    pipeline = TelecomCopilot()
    print("[Server] Telecom Copilot initialized successfully!\n")


class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, Any]]] = None


@app.get("/health")
def health_check():
    is_ready = pipeline is not None
    model_name = "DoRA Fine-Tuned Flan-T5" if (pipeline and pipeline.generator is not None) else "Not Loaded"
    return {
        "status": "healthy" if is_ready else "initializing",
        "generator": model_name,
        "device": pipeline.generator_device if pipeline else "unknown"
    }


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = pipeline.run(req.query, req.history or [])
    return result


@app.get("/network-status")
def get_network_status():
    feed_path = Path("data/raw/network_status.json")
    if feed_path.exists():
        with open(feed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Support both list and dict formats
            if isinstance(data, dict):
                regions = []
                for k, v in data.items():
                    if isinstance(v, dict):
                        item = dict(v)
                        item.setdefault("region", k.capitalize())
                        regions.append(item)
                    elif isinstance(v, list):
                        regions.extend(v)
                return regions if regions else list(data.values())
            return data
    return []


@app.get("/tickets")
def get_tickets():
    tickets_path = Path("data/processed/tickets.jsonl")
    tickets = []
    if tickets_path.exists():
        with open(tickets_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tickets.append(json.loads(line))
                    except Exception:
                        pass
    # Return newest tickets first
    tickets.reverse()
    return tickets


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
