from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse
import edge_tts
import uuid
import os
import torch
from TTS.api import TTS

app = FastAPI(title="Neural TTS API - Standard & Clone")

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- XTTS-v2 Initialization ---
# This loads the model into memory when the server starts
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading XTTS-v2 on {DEVICE}...")
# Note: This will download the model ( ~2GB) on first run
xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

def cleanup_file(filepath: str):
    """Safely deletes the file after the response is sent."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

@app.get("/voices")
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    selection = voices.find(Locale="en-ZA") + voices.find(Locale="en-US")
    return [{"name": v["ShortName"], "gender": v["Gender"]} for v in selection]

@app.post("/speak")
async def text_to_speech(
    text: str, 
    background_tasks: BackgroundTasks,
    voice: str = "en-ZA-LeahNeural"
):
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    file_id = str(uuid.uuid4())
    filepath = os.path.join(TEMP_DIR, f"{file_id}.mp3")

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
        background_tasks.add_task(cleanup_file, filepath)

        return FileResponse(path=filepath, media_type="audio/mpeg", filename="speech.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")

# --- New Clone Endpoint ---
@app.post("/clone")
async def clone_speech(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    voice_sample: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Clones a voice from an uploaded audio file and speaks the provided text.
    """
    file_id = str(uuid.uuid4())
    sample_path = os.path.join(TEMP_DIR, f"sample_{file_id}.wav")
    output_path = os.path.join(TEMP_DIR, f"clone_{file_id}.wav")

    try:
        # Save the uploaded reference sample
        with open(sample_path, "wb") as buffer:
            content = await voice_sample.read()
            buffer.write(content)

        # Generate speech using local XTTS model
        # This is a blocking call, but XTTS works best this way
        xtts_model.tts_to_file(
            text=text,
            speaker_wav=sample_path,
            language=language,
            file_path=output_path
        )

        # Cleanup both the sample and the output after sending
        background_tasks.add_task(cleanup_file, sample_path)
        background_tasks.add_task(cleanup_file, output_path)

        return FileResponse(path=output_path, media_type="audio/wav", filename="clone.wav")

    except Exception as e:
        if os.path.exists(sample_path): os.remove(sample_path)
        raise HTTPException(status_code=500, detail=f"Cloning Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)