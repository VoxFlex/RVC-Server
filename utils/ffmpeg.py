import os
import subprocess
from fastapi import HTTPException

def separate_vocals(input_song, output_folder):
    """
    แยกเสียงร้อง (Vocals) และดนตรี (Accompaniment) ออกจากไฟล์ต้นฉบับ
    """
    temp_folder = os.path.join(output_folder, "spleeter_output")
    os.makedirs(temp_folder, exist_ok=True)

    ffmpeg_command = [
        "spleeter", "separate",
        "-p", "spleeter:2stems",
        "-o", temp_folder,
        input_song
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"🔹 Spleeter Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Spleeter Error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"❌ Spleeter Error: {e.stderr}")

    # ตรวจสอบว่าไฟล์ vocals.wav และ accompaniment.wav มีอยู่หรือไม่
    extracted_folder = os.path.join(temp_folder, os.path.basename(input_song).replace(".mp3", ""))
    vocals_path = os.path.join(extracted_folder, "vocals.wav")
    accompaniment_path = os.path.join(extracted_folder, "accompaniment.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
        raise HTTPException(status_code=500, detail="❌ ไม่พบไฟล์ vocals.wav หรือ accompaniment.wav!")

    return vocals_path, accompaniment_path, temp_folder

def separate_vocals_video(input_song, output_folder):
    temp_folder = os.path.join(output_folder, "spleeter_output")
    os.makedirs(temp_folder, exist_ok=True)

    ffmpeg_command = [
        "spleeter", "separate",
        "-p", "spleeter:2stems",
        "-o", temp_folder,
        input_song
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"🔹 Spleeter Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Spleeter Error: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"❌ Spleeter Error: {e.stderr}")

    # ✅ เปลี่ยน path ให้ตรงกับโครงสร้างใหม่
    extracted_folder = os.path.join(temp_folder, "original_audio", "original_audio")
    vocals_path = os.path.join(extracted_folder, "vocals.wav")
    accompaniment_path = os.path.join(extracted_folder, "accompaniment.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
        raise HTTPException(status_code=500, detail="❌ ไม่พบไฟล์ vocals.wav หรือ accompaniment.wav!")

    print(f"📂 [INFO] vocals path: {vocals_path}")
    print(f"📂 [INFO] accompaniment path: {accompaniment_path}")
    print(f"📂 [INFO] temp_folder path: {temp_folder}")

    return vocals_path, accompaniment_path, temp_folder


def merge_audio(vocals_converted, accompaniment, final_output, vocal_volume=2.5, music_volume=1.0):
    print("🔹 กำลังรวมเสียงร้องกับดนตรีโดยใช้ FFmpeg CLI...")

    # ตรวจสอบขนาดไฟล์ก่อนทำงาน
    check_file_size(vocals_converted)
    check_file_size(accompaniment)

    ffmpeg_command = [
        "ffmpeg",
        "-i", accompaniment,
        "-i", vocals_converted,
        "-filter_complex",
        f"[1:a]volume={vocal_volume},highpass=f=100,lowpass=f=8000,adelay=0|0[louder_vocals];"
        f"[0:a]volume={music_volume}[softer_music];"
        f"[softer_music][louder_vocals]amix=inputs=2:duration=longest[out];"
        f"[out]loudnorm=I=-14:TP=-1.5:LRA=11[out_final]",
        "-map", "[out_final]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-y",
        final_output
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print("✅ ไฟล์สุดท้ายถูกสร้างสำเร็จ:", final_output)
    except subprocess.CalledProcessError as e:
        print("❌ เกิดข้อผิดพลาดในการรวมเสียง:", e)

def noise_reduction(input_file, output_file):
    print("🔹 ลด Noise และเสียงแปลก ๆ ที่เกิดช่วงเงียบ...")

    ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-af", "afftdn=nf=-25",  # FFT Noise Reduction
        "-y",
        output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print("✅ Noise Reduction เสร็จสมบูรณ์:", output_file)
    except subprocess.CalledProcessError as e:
        print("❌ เกิดข้อผิดพลาดในการลด Noise:", e)
 
def check_file_size(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise HTTPException(status_code=500, detail=f"❌ File {file_path} is missing or empty.")

def extract_audio(video_path, audio_output_path):
    command = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "44100",
        "-y", audio_output_path
    ]
    subprocess.run(command, check=True)

def merge_audio_video(audio_path, video_path, output_path):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        output_path
    ]
    subprocess.run(command, check=True)
