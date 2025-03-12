import base64
from fastapi import UploadFile, HTTPException
from data.file_manager import create_output_folder, save_file
from data.rvc_manager import rvc
from utils.cleaner import cleanup_files
from utils.ffmpeg import noise_reduction  # Added noise reduction function

def convert_voice(file: UploadFile):
    if not file.filename.endswith((".wav", ".mp3")):
        raise HTTPException(status_code=400, detail="Only .wav and .mp3 files are supported.")

    # 🔹 Optimal RVC Settings for Speech
    rvc.set_params(
        f0method="rmvpe",      # RMVPE captures speech pitch accurately
        f0up_key=0,
        index_rate=0.5,        # Balanced voice blending for clarity
        filter_radius=3,
        resample_sr=0,
        rms_mix_rate=1.0,
        protect=0.6            # Preserves natural tone in speech
    )

    try:
        sub_output_dir = create_output_folder()
        input_path = sub_output_dir / file.filename
        output_path = sub_output_dir / f"converted_{file.filename}.wav"
        cleaned_output_path = sub_output_dir / f"cleaned_{file.filename}.wav"

        # Save the uploaded file
        save_file(file, str(input_path))

        # RVC Voice Conversion
        rvc.infer_file(str(input_path), str(output_path))

        # Noise Reduction (Optional for cleaner output)
        noise_reduction(str(output_path), str(cleaned_output_path))

        # Encode the audio in base64 for response
        with open(cleaned_output_path, "rb") as output_file:
            encoded_audio = base64.b64encode(output_file.read()).decode()

        # Clean temporary files
        cleanup_files(input_path, output_path, cleaned_output_path)

        print("rvc.protect: ", rvc.protect)
        print("rvc.f0up_key: ", rvc.f0up_key)
        print("rvc.filter_radius: ", rvc.filter_radius)
        print("rvc.rms_mix_rate: ", rvc.rms_mix_rate)

        return {
            "output_file": str(cleaned_output_path),
            "model_name": rvc.current_model,
            "audio_base64": encoded_audio,
        }

    except Exception as e:
        cleanup_files(input_path, output_path, cleaned_output_path)
        return {"error": str(e)}
