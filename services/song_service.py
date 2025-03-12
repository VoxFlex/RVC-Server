import os
from fastapi import UploadFile, HTTPException
from loguru import logger
from data.file_manager import create_song_output_folder, save_file
from data.rvc_manager import rvc
from utils.ffmpeg import noise_reduction, separate_vocals, merge_audio
from utils.cleaner import clean_temp_files
import base64

MODEL_PATH = "./voice_models/TaylorSwift.pth"

def convert_song(file: UploadFile):
    if not file.filename.endswith((".wav", ".mp3")):
        raise HTTPException(status_code=400, detail="Only .wav and .mp3 files are supported.")
    
    # 🔹 ตั้งค่าพารามิเตอร์ที่เหมาะกับเสียงโทนต่ำ
    rvc.set_params(
        f0method="crepe",      # Crepe เหมาะกับเสียงร้องที่มีโทนสูง/ต่ำชัดเจน
        f0up_key=0,
        index_rate=0.7,
        filter_radius=4,
        resample_sr=0,
        rms_mix_rate=1.1,
        protect=0.5
    )

    try:
        # Step 1: เตรียมไฟล์และโฟลเดอร์ผลลัพธ์
        sub_output_folder = create_song_output_folder()
        input_path = os.path.join(sub_output_folder, file.filename)
        output_path = os.path.join(sub_output_folder, f"{file.filename}_converted.mp3")
        output_cleaned = os.path.join(sub_output_folder, f"{file.filename}_cleaned.mp3")

        # Step 2: บันทึกไฟล์ที่อัปโหลด
        save_file(file, input_path)

        # Step 3: แยกเสียงร้องและดนตรี
        vocals, accompaniment, temp_folder = separate_vocals(input_path, sub_output_folder)

        # Step 4: แปลงเสียงร้องด้วย RVC
        converted_vocals = os.path.join(sub_output_folder, f"converted_vocals.wav")
        rvc.infer_file(vocals, converted_vocals)

        # Step 5: รวมเสียงร้องกับดนตรี
        merge_audio(converted_vocals, accompaniment, output_path, vocal_volume=2.5, music_volume=0.9)

        # Step 6: ลด Noise และตัดเสียงแปลก ๆ ที่เกิดช่วงเงียบ
        noise_reduction(output_path, output_cleaned)

        # Step 7: ตรวจสอบว่าไฟล์สุดท้ายถูกสร้างหรือไม่
        if not os.path.exists(output_cleaned):
            raise HTTPException(status_code=500, detail="❌ Final output file not found after noise reduction.")

        # Step 8: แปลงไฟล์ที่เสร็จสมบูรณ์เป็น Base64
        encoded_audio = ""
        with open(output_cleaned, "rb") as output_file:
            encoded_audio = base64.b64encode(output_file.read()).decode()

        # Step 9: ทำความสะอาดไฟล์ชั่วคราว
        clean_temp_files(temp_folder, vocals, accompaniment, converted_vocals)
        print("rvc.protect: ",rvc.protect)
        print("rvc.f0up_key: ",rvc.f0up_key)
        print("rvc.filter_radius: ",rvc.filter_radius)
        print("rvc.rms_mix_rate: ",rvc.rms_mix_rate)
        return {
            "output_file": output_cleaned,
            "model_name": rvc.current_model,
            "message": "✅ Song converted successfully.",
            "audio_base64": encoded_audio,
        }

    except Exception as e:
        clean_temp_files(input_path, sub_output_folder)
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")
