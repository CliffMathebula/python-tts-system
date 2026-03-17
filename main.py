import sys
import os

# --- COMPATIBILITY MONKEY PATCH ---
# This must run BEFORE importing TTS to fix the Transformers v5.0+ error
try:
    import transformers.pytorch_utils
    if not hasattr(transformers.pytorch_utils, "isin_mps_friendly"):
        def isin_mps_friendly(tensor):
            return False
        transformers.pytorch_utils.isin_mps_friendly = isin_mps_friendly
        print("🛠️ Applied Transformers v5.0 compatibility patch.")
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
import edge_tts
import time
import uuid
import torch
import shutil
import torchaudio
from TTS.api import TTS
from video_engine import generate_video_from_assets

app = FastAPI(
    title="Neural TTS API - Standard & Clone",
    description="Unified TTS API (Auto-detect GPU/CPU)",
    version="1.4.0"
)

# --- Directory Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")
SPEAKER_DIR = os.path.join(BASE_DIR, "speakers")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(SPEAKER_DIR, exist_ok=True)

# --- Device Detection ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Detected Hardware: {DEVICE.upper()}")
print(f"🚀 Loading XTTS-v2 model...")

# Initialize and move model to the detected device
xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

# --- Utility Functions ---
def cleanup_file(filepath: str):
    """Immediate cleanup for single files"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

def cleanup_assets_after_delay(paths: list, delay: int = 3600):
    """Wait for delay (1 hour) then delete multiple files (images, audio, video)"""
    time.sleep(delay)
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Cleaned up: {path}")
        except Exception as e:
            print(f"Cleanup error: {e}")

# --- Endpoints ---

@app.get("/voices", tags=["Voice Management"])
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    selection = voices.find(Locale="en-ZA") + voices.find(Locale="en-US")
    standard = [{"name": v["ShortName"], "gender": v["Gender"], "type": "standard"} for v in selection]
    
    cloned = [
        {"name": f.replace(".pth", ""), "type": "cloned"} 
        for f in os.listdir(SPEAKER_DIR) if f.endswith(".pth")
    ]
    return {"cloned": cloned, "standard": standard}

@app.post("/register-voice", tags=["Neural Clone Engine"])
async def register_voice(
    name: str = Form(..., description="Unique name for the voice profile"),
    voice_sample: UploadFile = File(..., description="10-15s clean audio sample")
):
    temp_path = os.path.join(TEMP_DIR, f"reg_{uuid.uuid4()}.wav")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(voice_sample.file, buffer)

        gpt_cond_latent, speaker_embedding = xtts_model.synthesizer.tts_model.get_conditioning_latents(audio_path=[temp_path])

        speaker_file = os.path.join(SPEAKER_DIR, f"{name}.pth")
        
        torch.save({
            "gpt_cond_latent": gpt_cond_latent.cpu(),
            "speaker_embedding": speaker_embedding.cpu(),
        }, speaker_file)

        return {"status": "success", "message": f"Voice '{name}' registered successfully."}
    except Exception as e:
        print(f"Detailed Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_file(temp_path)

@app.post("/speak", tags=["Synthesis Engine"])
async def text_to_speech(
    text: str, 
    background_tasks: BackgroundTasks,
    voice: str = Query("en-ZA-LeahNeural", description="Voice ID")
):
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    file_id = str(uuid.uuid4())
    speaker_file = os.path.join(SPEAKER_DIR, f"{voice}.pth")

    if os.path.exists(speaker_file):
        output_path = os.path.join(TEMP_DIR, f"cloned_{file_id}.wav")
        try:
            latents = torch.load(speaker_file, map_location=DEVICE, weights_only=False)
            print(f"🎙️ Synthesizing {voice} on {DEVICE.upper()}...")
            
            gpt_cond_latent = latents["gpt_cond_latent"].to(DEVICE)
            speaker_embedding = latents["speaker_embedding"].to(DEVICE)

            out = xtts_model.synthesizer.tts_model.inference(
                text=text,
                language="en",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=0.7,
                repetition_penalty=2.0,
            )
            
            wav_tensor = torch.tensor(out["wav"]).unsqueeze(0).cpu()
            torchaudio.save(output_path, wav_tensor, 24000)

            background_tasks.add_task(cleanup_file, output_path)
            return FileResponse(path=output_path, media_type="audio/wav", filename=f"{voice}_clone.wav")
        
        except Exception as e:
            print(f"❌ Synthesis Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        filepath = os.path.join(TEMP_DIR, f"{file_id}.mp3")
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filepath)
            background_tasks.add_task(cleanup_file, filepath)
            return FileResponse(path=filepath, media_type="audio/mpeg", filename=f"{voice}_standard.mp3")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Voice '{voice}' not found.")

@app.post("/generate-video", tags=["Video Engine"])
async def create_video(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="The script for the video"),
    voice: str = Form("en-ZA-LeahNeural", description="Voice ID"),
    images: list[UploadFile] = File(..., description="Upload multiple images")
):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    file_id = str(uuid.uuid4())
    audio_path = os.path.join(TEMP_DIR, f"audio_{file_id}.mp3")
    video_path = os.path.join(TEMP_DIR, f"video_{file_id}.mp4")
    
    # 1. Generate the TTS Audio
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Audio failed: {e}")

    # 2. Save uploaded images
    saved_image_paths = []
    for i, img in enumerate(images):
        img_ext = os.path.splitext(img.filename)[1]
        img_path = os.path.join(TEMP_DIR, f"img_{file_id}_{i}{img_ext}")
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
        saved_image_paths.append(img_path)

    # 3. Trigger Background Tasks (Video Generation + Auto-Cleanup)
    background_tasks.add_task(
        generate_video_from_assets, 
        audio_path, 
        saved_image_paths, 
        text, 
        video_path
    )
    
    # Cleanup all temp files after 1 hour
    background_tasks.add_task(
        cleanup_assets_after_delay, 
        saved_image_paths + [audio_path, video_path]
    )
    
    return {
        "status": "processing",
        "message": "Video rendering started.",
        "video_id": file_id,
        "download_url": f"/download-video/{file_id}"
    }

@app.get("/download-video/{file_id}", tags=["Video Engine"])
async def download_video(file_id: str):
    video_path = os.path.join(TEMP_DIR, f"video_{file_id}.mp4")
    if os.path.exists(video_path):
        return FileResponse(
            path=video_path, 
            media_type="video/mp4", 
            filename=f"generated_video_{file_id}.mp4"
        )
    raise HTTPException(status_code=404, detail="Video not found or still rendering.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)