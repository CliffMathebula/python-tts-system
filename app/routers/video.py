import os
import uuid
import shutil
from fastapi import APIRouter, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from app.services.tts_engine import generate_audio
from app.services.video_engine import generate_video
from app.core.config import TEMP_DIR, SPEAKER_DIR

router = APIRouter(prefix="/video", tags=["Video"])

@router.post("/generate")
async def create_video(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="Script segments separated by '|'"),
    voice: str = Form("en-ZA-LeahNeural"),
    images: list[UploadFile] = File(...),
    width: int = Form(1920, description="Target video width"),
    height: int = Form(1080, description="Target video height")
):
    file_id = str(uuid.uuid4())
    # Identify if the voice is a local clone or cloud voice
    is_cloned = os.path.exists(os.path.join(SPEAKER_DIR, f"{voice}.pth"))
    audio_ext = "wav" if is_cloned else "mp3"
    
    audio_path = os.path.join(TEMP_DIR, f"aud_{file_id}.{audio_ext}")
    video_path = os.path.join(TEMP_DIR, f"vid_{file_id}.mp4")

    # 1. Generate the Speech first
    try:
        await generate_audio(text, voice, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
    
    # 2. Save uploaded images locally
    img_paths = []
    for i, img in enumerate(images):
        ext = os.path.splitext(img.filename)[1]
        p = os.path.join(TEMP_DIR, f"img_{file_id}_{i}{ext}")
        with open(p, "wb") as b: 
            shutil.copyfileobj(img.file, b)
        img_paths.append(p)

    # 3. Queue the Video Generation with custom sizes
    background_tasks.add_task(
        generate_video, 
        audio_path, 
        img_paths, 
        text, 
        video_path, 
        width, 
        height
    )
    
    return {
        "status": "processing",
        "video_id": file_id, 
        "dimensions": f"{width}x{height}",
        "download_url": f"/video/download/{file_id}"
    }

@router.get("/download/{file_id}")
async def download(file_id: str):
    path = os.path.join(TEMP_DIR, f"vid_{file_id}.mp4")
    if os.path.exists(path): 
        return FileResponse(path, media_type="video/mp4", filename=f"video_{file_id}.mp4")
    raise HTTPException(status_code=404, detail="Video is still rendering or does not exist.")