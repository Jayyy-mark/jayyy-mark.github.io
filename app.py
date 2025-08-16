from flask import Flask, Response, request, render_template
import asyncio
import websockets
import json
import base64
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Replace with your Gemini API key
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LIVE_API_URL = "wss://generativelanguage.googleapis.com/v1beta/live:connect?key=" + GEMINI_API_KEY

async def stream_from_gemini(text: str):
    async with websockets.connect(LIVE_API_URL) as ws:
        # 1. Send setup event (tell Gemini to use TTS)
        await ws.send(json.dumps({
            "setup": {
                "model": "gemini-2.5-flash-preview-tts",
                "voiceConfig": {
                    "voiceName": "Aoede"  # You can change to Kore, Puck, etc.
                }
            }
        }))

        # 2. Send the text we want to synthesize
        await ws.send(json.dumps({
            "input": {
                "text": text
            }
        }))

        # 3. Collect and stream back audio chunks
        async for message in ws:
            data = json.loads(message)
            if "audio" in data:
                audio_chunk = base64.b64decode(data["audio"]["data"])
                yield audio_chunk

@app.route("/")
def index():
    return render_template("test.html")

@app.route("/speak")
def speak():
    text = request.args.get("text", "Hello from Gemini Live API")

    async def generate_wav():
        audio_buffer = io.BytesIO()
        sample_rate = 24000  # Gemini TTS default
        num_channels = 1
        sampwidth = 2  # 16-bit PCM

        # Create a WAV file in memory
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)

            # Collect audio chunks
            async for chunk in stream_from_gemini(text):
                wf.writeframes(chunk)

        audio_buffer.seek(0)
        yield audio_buffer.read()

    return Response(generate_wav(), mimetype="audio/wav")


app.run(host="0.0.0.0", port=5000, debug=True)
