import os
import shutil
import uuid
import torch
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from app.services.tts_engine import fetch_voices, xtts_model
from app.core.config import SPEAKER_DIR, TEMP_DIR

router = APIRouter(prefix="/voices", tags=["Voices"])

@router.get("/")
async def list_voices():
    std = await fetch_voices()
    cloned = [{"name": f.replace(".pth", ""), "type": "cloned"} for f in os.listdir(SPEAKER_DIR) if f.endswith(".pth")]
    return {"cloned": cloned, "standard": std}

@router.post("/register")
async def register(name: str = Form(...), voice_sample: UploadFile = File(...)):
    temp_path = os.path.join(TEMP_DIR, f"reg_{uuid.uuid4()}.wav")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(voice_sample.file, buffer)
        gpt, emb = xtts_model.synthesizer.tts_model.get_conditioning_latents(audio_path=[temp_path])
        torch.save({"gpt_cond_latent": gpt.cpu(), "speaker_embedding": emb.cpu()}, os.path.join(SPEAKER_DIR, f"{name}.pth"))
        return {"status": "success"}
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)