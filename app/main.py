from fastapi import FastAPI
from app.routers import voices, video

app = FastAPI(title="TTS Microservice Gateway", version="2.0.0")

app.include_router(voices.router)
app.include_router(video.router)

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Neural TTS Microservice is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)