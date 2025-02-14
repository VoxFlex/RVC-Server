from fastapi import APIRouter, UploadFile, File
from api.services.voice_changer import current_model, list_models, select_model, convert_voice, unload_voice_model

router = APIRouter()

# ✅ **ดูรายชื่อโมเดลที่มีอยู่**
@router.get("/models")
def get_models():
    return list_models()

@router.get("/models/current_model")
def get_current_model():
    return current_model()

# ✅ **เลือกโมเดลที่ต้องการใช้**
@router.post("/models/select")
def set_model(model_name: str):
    return select_model(model_name)

# ✅ **แปลงเสียง**
@router.post("/voice/convert")
async def convert_voice_route(file: UploadFile = File(...)):
    return convert_voice(file)

@router.post("/models/unload")
def unload_model_route():
    return unload_voice_model()

# ✅ **Health Check**
@router.get("/")
def health_check():
    return {"status": "API is running"}

