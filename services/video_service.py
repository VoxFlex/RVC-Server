import os
import base64
from fastapi import UploadFile, HTTPException
from loguru import logger
from data.file_manager import create_video_output_folder, save_file
from data.rvc_manager import rvc
from utils.ffmpeg import (
    extract_audio,
    separate_vocals,
    merge_audio_video,
    noise_reduction,
    merge_audio,
    separate_vocals_video  # ✅ นำ merge_audio มาใช้ให้ถูกต้อง
)
from utils.cleaner import cleanup_files

MAX_VIDEO_SIZE_MB = 200

def convert_video_audio(file: UploadFile, is_music_video: bool = False):
    if not file.filename.endswith((".mp4", ".mov")):
        raise HTTPException(status_code=400, detail="Only .mp4 and .mov files are supported.")

    # ตรวจสอบขนาดไฟล์
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell() / (1024 * 1024)
    file.file.seek(0)

    if file_size > MAX_VIDEO_SIZE_MB:
        raise HTTPException(status_code=413, detail="❌ File too large.")

    # 🔹 Optimal RVC Settings
    rvc.set_params(
        f0method="rmvpe",
        f0up_key=0,
        index_rate=0.7 if is_music_video else 0.5,
        filter_radius=4,
        resample_sr=0,
        rms_mix_rate=1.1,
        protect=0.5 if is_music_video else 0.6
    )

    output_folder = create_video_output_folder()
    input_video_path = os.path.join(output_folder, file.filename)
    original_audio = os.path.join(output_folder, "original_audio.wav")
    converted_audio = os.path.join(output_folder, "converted_audio.wav")
    converted_vocals = os.path.join(output_folder, "converted_vocals.wav")
    accompaniment = os.path.join(output_folder, "accompaniment.wav")
    final_audio_path = os.path.join(output_folder, "merged_audio.wav")  # ✅ ใช้ไฟล์เสียงที่ merge
    final_video = os.path.join(output_folder, f"converted_{file.filename}")

    try:
        # 1️⃣ บันทึกไฟล์วิดีโอ
        save_file(file, input_video_path)

        # 2️⃣ ดึงเสียงจากวิดีโอ
        extract_audio(input_video_path, original_audio)

        # 3️⃣ แยกเสียงร้องออกจากดนตรี (ถ้าเป็น MV)
        if is_music_video:
            # ✅ ใช้ path ใหม่ที่ตรงกับโครงสร้างโฟลเดอร์ล่าสุด
            vocals, accompaniment, temp_folder = separate_vocals_video(original_audio, os.path.join(output_folder, "spleeter_output"))

            rvc.infer_file(vocals, converted_audio)

            # ✅ รวมเสียงร้องและดนตรีเป็นไฟล์ใหม่
            merge_audio(converted_audio, accompaniment, final_output=final_audio_path)

            # ✅ นำไฟล์เสียงที่ merge แล้วใส่กลับเข้าไปในวิดีโอ
            merge_audio_video(final_audio_path, input_video_path, final_video)

        else:
            rvc.infer_file(original_audio, converted_audio)
            merge_audio_video(converted_audio, input_video_path, final_video)

        if not os.path.exists(final_video):
            raise HTTPException(status_code=500, detail="❌ Final video not created.")

        # ✅ ตรวจสอบว่าไฟล์สุดท้ายที่แปลงแล้วถูกสร้างหรือไม่
        encoded_video = ""
        with open(final_video, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode()

        # cleanup_files(
        #     input_video_path,
        #     original_audio,
        #     converted_audio,
        #     final_audio_path,
        #     vocals if is_music_video else None,
        #     accompaniment if is_music_video else None,
        #     temp_folder if is_music_video else None
        # )

        return {
            "output_file": final_video,
            "model_name": rvc.current_model,
            "message": "✅ Video converted successfully.",
            "video_base64": encoded_video
        }

    except Exception as e:
        # cleanup_files(
        #     input_video_path,
        #     original_audio,
        #     converted_audio,
        #     final_audio_path,
        #     vocals if is_music_video else None,
        #     accompaniment if is_music_video else None,
        #     temp_folder if is_music_video else None
        # )
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")
