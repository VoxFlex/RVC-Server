import os
from rvc_python.infer import RVCInference

MODEL_DIR = "voice_models"
DEFAULT_MODEL = "NontTanont.pth"

rvc = RVCInference(models_dir=MODEL_DIR, device="cuda:0",version="v2")
rvc.load_model(os.path.join(MODEL_DIR, DEFAULT_MODEL))
rvc.set_params(f0up_key=2, protect=0.5)
