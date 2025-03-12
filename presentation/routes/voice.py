from fastapi import APIRouter, UploadFile, File
from services.voice_service import convert_voice

router = APIRouter()

@router.post("/voice/convert")
async def convert_voice_route(file: UploadFile = File(...)):
    return convert_voice(file)
