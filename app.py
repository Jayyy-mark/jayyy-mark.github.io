import io
import wave
from flask import Flask, Response, request, render_template
import asyncio
import websockets
import json
import base64
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LIVE_API_URL = "wss://generativelanguage.googleapis.com/v1beta/live:connect?key=" + GEMINI_API_KEY

async def stream_from_gemini(text: str):
    async with websockets.connect(LIVE_API_URL) as ws:
        await ws.send(json.dumps({
            "setup": {
                "model": "gemini-2.5-flash-preview-tts",
                "voiceConfig": {"voiceName": "Aoede"}
            }
        }))
        await ws.send(json.dumps({"input": {"text": text}}))

        async for message in ws:
            data = json.loads(message)
            if "audio" in data:
                yield base64.b64decode(data["audio"]["data"])

@app.route("/")
def index():
    return render_template("test.html")

@app.route("/speak")
def speak():
    text = request.args.get("text", "Hello from Gemini Live API")

    # Collect all chunks first
    async def generate_full_wav():
        audio_chunks = []
        async for chunk in stream_from_gemini(text):
            audio_chunks.append(chunk)

        audio_data = b"".join(audio_chunks)
        audio_buffer = io.BytesIO()

        # Create WAV in memory
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)

        audio_buffer.seek(0)
        return audio_buffer.read()

    # Flask cannot directly await, so run asyncio
    audio_bytes = asyncio.run(generate_full_wav())
    return Response(audio_bytes, mimetype="audio/wav")

app.run(host="0.0.0.0", port=5000, debug=True)
