from fastapi import APIRouter, UploadFile, File
from services.song_service import convert_song

router = APIRouter()

@router.post("/song/convert")
async def convert_song_route(file: UploadFile = File(...)):
    return convert_song(file)
