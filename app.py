import asyncio
import websockets
import json
import base64
import os
from fastapi import FastAPI, WebSocket,Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates folder
templates = Jinja2Templates(directory="templates")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LIVE_API_URL = f"wss://generativelanguage.googleapis.com/v1beta/live:connect?key={GEMINI_API_KEY}"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.websocket("/ws")
async def websocket_tts(websocket: WebSocket):
    await websocket.accept()
    text = websocket.query_params.get("text", "Hello from Gemini TTS!")

    async with websockets.connect(LIVE_API_URL) as ws_gemini:
        # Setup TTS
        await ws_gemini.send(json.dumps({
            "setup": {
                "model": "gemini-2.5-flash-preview-tts",
                "voiceConfig": {"voiceName": "Aoede"},
                "audioConfig": {"audioEncoding": "OGG_OPUS"}
            }
        }))

        # Send text
        await ws_gemini.send(json.dumps({"input": {"text": text}}))

        # Stream messages to frontend
        async for message in ws_gemini:
            data = json.loads(message)

            # Send JSON directly to frontend
            await websocket.send_json(data)

            # Optional: send audio bytes separately if you want
            # if "audio" in data:
            #     chunk = base64.b64decode(data["audio"]["data"])
            #     await websocket.send_bytes(chunk)

            if data.get("event") == "SESSION_DONE":
                break

    await websocket.close()
