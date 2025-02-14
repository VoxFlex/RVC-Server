from rvc_python.infer import RVCInference

if __name__ == "__main__":
    rvc = RVCInference(models_dir="./voice_models",device="cuda:0")

    rvc.load_model("./voice_models/NontTanont.pth")
    rvc.set_params(f0up_key=2, protect=0.5)

    rvc.infer_file("input/Goodbye.mp3", "outputGoodbye.wav")

    rvc.unload_model()
