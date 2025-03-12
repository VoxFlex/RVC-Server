from data.rvc_manager import rvc, MODEL_DIR
import os

def list_models():
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pth")]
    return {"available_models": models}

def select_model(model_name: str):
    model_path = os.path.join(MODEL_DIR, model_name)
    
    if not os.path.exists(model_path):
        return {"error": f"Model '{model_name}' not found."}
    
    rvc.unload_model()
    rvc.load_model(model_path)
    return {"message": f"Model '{model_name}' selected successfully."}

def unload_voice_model():
    rvc.unload_model()
    return {"message": "Voice model unloaded"}

def current_model():
    return {"current_model": rvc.current_model}
