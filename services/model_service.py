import tempfile
import zipfile
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from data.rvc_manager import rvc, MODEL_DIR
import os

def list_models():
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pth")]
    return {"available_models": models}

def select_model(model_name: str):
    """
    เลือกโมเดลที่ต้องการใช้งาน
    """
    model_path = os.path.join(MODEL_DIR, model_name)
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"❌ Model '{model_name}' not found.")

    rvc.unload_model()
    rvc.load_model(model_path)
    return {"message": f"✅ Model '{model_name}' selected successfully."}
    
def unload_voice_model():
    rvc.unload_model()
    return {"message": "Voice model unloaded"}

def current_model():
    return {"current_model": rvc.current_model}

def upload_model(file: UploadFile):
    """
    อัปโหลดไฟล์ ZIP ที่มีไฟล์ .pth อยู่ด้านในโดยตรง
    """
    try:
        # ตรวจสอบไฟล์นามสกุล
        if not file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only .zip files are supported.")

        # 🔹 สร้างไฟล์ชั่วคราวเพื่อเก็บ .zip ที่อัปโหลด
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            contents = file.file.read()
            tmp_file.write(contents)
            zip_path = tmp_file.name  # path ของไฟล์ zip ชั่วคราว

        # 🔹 แตกไฟล์ .zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extracted_files = zip_ref.namelist()
            
            # 🔎 ตรวจสอบว่ามีไฟล์ .pth อยู่ใน zip หรือไม่
            pth_files = [f for f in extracted_files if f.endswith('.pth')]
            if not pth_files:
                raise HTTPException(status_code=400, detail="❌ No .pth file found in the uploaded ZIP.")

            # 🔹 Extract และย้ายไปเก็บใน voice_models
            zip_ref.extractall(MODEL_DIR)

        # 🔹 รายชื่อไฟล์ที่ถูกเพิ่ม
        added_models = [os.path.basename(f) for f in pth_files]

        # 🔹 โหลดรายชื่อโมเดลใหม่
        rvc.models = rvc._load_available_models()

        return JSONResponse(content={
            "message": "✅ Model uploaded and extracted successfully.",
            "uploaded_models": added_models
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 🔹 ลบไฟล์ zip ชั่วคราวเมื่อเสร็จ
        if os.path.exists(zip_path):
            os.remove(zip_path)
