import os
import shutil
import base64
from rvc_python.infer import RVCInference

# ตั้งค่าโฟลเดอร์เก็บไฟล์
INPUT_DIR = "input/"
OUTPUT_DIR = "output_voice_folder/"
MODEL_DIR = "voice_models/"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# โหลด RVC Model ครั้งแรก (Default Model)
rvc = RVCInference(models_dir=MODEL_DIR, device="cuda:0")
default_model = "NontTanont.pth"
rvc.load_model(os.path.join(MODEL_DIR, default_model))
rvc.set_params(f0up_key=2, protect=0.5)

# **ดูรายชื่อโมเดลที่มีอยู่**
def list_models():
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pth")]
    return {"available_models": models}

# **เลือกโมเดลที่ต้องการใช้**
def select_model(model_name: str):
    model_path = os.path.join(MODEL_DIR, model_name)
    
    if not os.path.exists(model_path):
        return {"error": f"Model '{model_name}' not found."}
    
    rvc.unload_model()
    rvc.load_model(model_path)
    return {"message": f"Model '{model_name}' selected successfully."}

def unload_voice_model():
    """ปิดการใช้งานโมเดล"""
    rvc.unload_model()
    return {"message": "Voice model unloaded"}

def current_model():
    """ปิดการใช้งานโมเดล"""
    return {"current_model": rvc.current_model}

def convert_voice(file):
    try:
        input_path = os.path.join(INPUT_DIR, file.filename)
        output_path = os.path.join(OUTPUT_DIR, f"converted_{file.filename}.wav")

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        rvc.infer_file(input_path, output_path)

        with open(output_path, "rb") as output_file:
            encoded_audio = base64.b64encode(output_file.read()).decode()
            
        os.remove(input_path)
        os.remove(output_path)

        return {"audio_base64": encoded_audio, "output_file": output_path,"model_name": rvc.current_model}
    except Exception as e:
        return {"error": str(e)}
