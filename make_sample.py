import asyncio
import edge_tts

async def main():
    text = "This is a high quality recording used for voice cloning."
    # We use Luke because he has a very distinct, clear voice for cloning
    communicate = edge_tts.Communicate(text, "en-ZA-LukeNeural")
    await communicate.save("sample.wav")
    print("✅ sample.wav created successfully!")

if __name__ == "__main__":
    asyncio.run(main())
