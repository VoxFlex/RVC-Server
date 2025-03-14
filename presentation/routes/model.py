from fastapi import APIRouter, File, UploadFile
from services.model_service import current_model, list_models, select_model, unload_voice_model, upload_model

router = APIRouter()

@router.get("/models")
def get_models():
    return list_models()

@router.get("/models/current_model")
def get_current_model():
    return current_model()

@router.post("/models/select")
def set_model(model_name: str):
    return select_model(model_name)

@router.post("/models/unload")
def unload_model_route():
    return unload_voice_model()

@router.post("/models/upload")
async def upload_model_route(file: UploadFile = File(...)):
    return upload_model(file)
