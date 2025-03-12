from fastapi import FastAPI
from presentation.routes import voice, song, model , video
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ควรกำหนดเฉพาะ Origin ที่ปลอดภัย
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(song.router)
app.include_router(model.router)
app.include_router(video.router)

@app.get("/")
def health_check():
    return {"status": "From RVC-Server API is running"}
