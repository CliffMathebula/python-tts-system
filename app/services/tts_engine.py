import os
import torch
import torchaudio
import edge_tts
import asyncio
# 1. Import config FIRST to trigger the monkey patch from app.core.config
from app.core.config import DEVICE, SPEAKER_DIR

# 2. It is now safe to import TTS after the patch is applied
try:
    from TTS.api import TTS
except ImportError as e:
    print(f"❌ Failed to import TTS: {e}")
    raise

# --- Global Model Initialization ---
print(f"🚀 Loading XTTS-v2 model on {DEVICE.upper()}...")
# Using the multilingual XTTS-v2 model
xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

async def fetch_voices():
    """
    Fetches the list of available voices from Edge-TTS.
    Filters for South African and US English by default.
    """
    try:
        print("📡 Fetching standard voice list from Edge-TTS...")
        voices_manager = await edge_tts.VoicesManager.create()
        selection = voices_manager.find(Locale="en-ZA") + voices_manager.find(Locale="en-US")
        
        return [
            {"name": v["ShortName"], "gender": v["Gender"], "type": "standard"} 
            for v in selection
        ]
    except Exception as e:
        print(f"⚠️ Error fetching Edge-TTS voices: {e}")
        return []

async def generate_audio(text: str, voice: str, output_path: str):
    """
    Logic to determine if a voice is 'Cloned' (local .pth file) 
    or 'Standard' (Edge-TTS) and generate the corresponding audio file.
    """
    speaker_file = os.path.join(SPEAKER_DIR, f"{voice}.pth")

    # Path A: Cloned Voice Synthesis (XTTS-v2)
    if os.path.exists(speaker_file):
        try:
            print(f"🎙️ Synthesizing Cloned Voice: '{voice}' using {DEVICE.upper()}...")
            
            # Load the pre-computed latents
            latents = torch.load(speaker_file, map_location=DEVICE, weights_only=False)
            
            gpt_cond_latent = latents["gpt_cond_latent"].to(DEVICE)
            speaker_embedding = latents["speaker_embedding"].to(DEVICE)

            # Perform inference
            out = xtts_model.synthesizer.tts_model.inference(
                text=text,
                language="en",
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=0.7,
                repetition_penalty=2.0,
            )
            
            # Save as WAV (XTTS default)
            wav_tensor = torch.tensor(out["wav"]).unsqueeze(0).cpu()
            torchaudio.save(output_path, wav_tensor, 24000)
            return "audio/wav"
            
        except Exception as e:
            print(f"❌ XTTS Synthesis Error: {e}")
            raise Exception(f"Cloned TTS engine failed: {str(e)}")

    # Path B: Standard Voice Synthesis (Edge-TTS)
    else:
        try:
            print(f"🎙️ Synthesizing Standard Voice: '{voice}' via Edge-TTS...")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return "audio/mpeg"
            
        except Exception as e:
            print(f"❌ Edge-TTS Error: {e}")
            raise Exception(f"Standard voice '{voice}' failed or does not exist.")