import os
import subprocess
import shutil
import time
from rvc_python.infer import RVCInference

# 🛠 ตั้งค่าต่างๆ
INPUT_SONG = "input/Goodbye.mp3"  # เพลงต้นฉบับ
OUTPUT_FOLDER = "output_song_folder"  # โฟลเดอร์สำหรับเก็บผลลัพธ์
MODEL_PATH = "./voice_models/kom.pth"  # โมเดลเสียงที่ต้องการใช้
DEVICE = "cuda:0"  # ใช้ GPU (ถ้ามี)

# 🛠 สร้างโฟลเดอร์ย่อยแบบไม่ซ้ำกัน ตาม timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")
song_name = os.path.splitext(os.path.basename(INPUT_SONG))[0]  # ดึงชื่อไฟล์โดยไม่เอานามสกุล
sub_output_folder = os.path.join(OUTPUT_FOLDER, f"{song_name}_{timestamp}")
os.makedirs(sub_output_folder, exist_ok=True)

# กำหนดไฟล์ผลลัพธ์
FINAL_OUTPUT = os.path.join(sub_output_folder, f"{song_name}_converted.mp3")

### 1️⃣ แยกเสียงร้องออกจากดนตรี (ใช้ Spleeter CLI)
def separate_vocals(input_song, output_folder):
    print("🔹 กำลังแยกเสียงร้องออกจากดนตรีโดยใช้ Spleeter CLI...")
    
    temp_folder = os.path.join(output_folder, "spleeter_output")
    os.makedirs(temp_folder, exist_ok=True)

    # รัน Spleeter
    ffmpeg_command = [
        "spleeter", "separate",
        "-p", "spleeter:2stems",  # ใช้โมเดล 2stems (vocals + accompaniment)
        "-o", temp_folder,
        input_song
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print("✅ แยกเสียงร้องสำเร็จ!")

        # หาไฟล์ vocals.wav และ accompaniment.wav
        extracted_folder = os.path.join(temp_folder, os.path.basename(input_song).replace(".mp3", ""))
        vocals_path = os.path.join(extracted_folder, "vocals.wav")
        accompaniment_path = os.path.join(extracted_folder, "accompaniment.wav")

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            raise FileNotFoundError("❌ ไม่พบไฟล์ vocals.wav หรือ accompaniment.wav!")

        return vocals_path, accompaniment_path, temp_folder

    except subprocess.CalledProcessError as e:
        print("❌ เกิดข้อผิดพลาดในการแยกเสียง:", e)
        return None, None, None

### 2️⃣ แปลงเสียงร้องด้วย RVC
def convert_vocals(vocals_path, output_path, model_path):
    print("🔹 กำลังแปลงเสียงร้องด้วย RVC...")

    try:
        rvc = RVCInference(models_dir="./rvc_models", device=DEVICE)
        rvc.load_model(model_path)
        rvc.set_params(f0method="rmvpe", f0up_key=0, index_rate=0.75, protect=0.5)

        rvc.infer_file(vocals_path, output_path)
        rvc.unload_model()

        print("✅ แปลงเสียงร้องสำเร็จ:", output_path)
        return output_path

    except Exception as e:
        print("❌ เกิดข้อผิดพลาดในการแปลงเสียง:", str(e))
        return None

### 3️⃣ รวมเสียงร้องที่แปลงแล้วกลับเข้ากับดนตรี (ใช้ FFmpeg CLI)
def merge_audio(vocals_converted, accompaniment, final_output):
    print("🔹 กำลังรวมเสียงร้องกับดนตรีโดยใช้ FFmpeg CLI...")

    vocals_stereo = vocals_converted.replace(".wav", "_stereo.wav")

    # แปลงเสียงร้อง mono เป็น stereo ก่อน
    ffmpeg_convert_mono_to_stereo = [
        "ffmpeg",
        "-i", vocals_converted,
        "-af", "pan=stereo|c0=c0|c1=c0",
        vocals_stereo
    ]

    try:
        subprocess.run(ffmpeg_convert_mono_to_stereo, check=True)
        print("✅ แปลงเสียงร้องเป็น Stereo สำเร็จ:", vocals_stereo)
    except subprocess.CalledProcessError as e:
        print("❌ เกิดข้อผิดพลาดในการแปลงเสียง mono -> stereo:", e)
        return

    # คำสั่งรวมเสียงร้องกับดนตรี
    ffmpeg_command = [
        "ffmpeg",
        "-i", accompaniment,
        "-i", vocals_stereo,
        "-filter_complex",
        "[1:a]volume=2.0,adelay=0|0[louder_vocals];"
        "[0:a][louder_vocals]amix=inputs=2:duration=longest:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[out]",
        "-map", "[out]",
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

### 4️⃣ ลบไฟล์ชั่วคราวหลังจากใช้งาน
def clean_temp_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)  # ลบโฟลเดอร์ทั้งหมด
            else:
                os.remove(path)  # ลบไฟล์เดียว
            print(f"🧹 ลบไฟล์/โฟลเดอร์ชั่วคราว: {path}")

try:
    vocals, accompaniment, temp_folder = separate_vocals(INPUT_SONG, sub_output_folder)

    if vocals and accompaniment:
        converted_vocals = os.path.join(sub_output_folder, f"{song_name}_converted.wav")

        converted_vocals = convert_vocals(vocals, converted_vocals, MODEL_PATH)
        if converted_vocals:
            merge_audio(converted_vocals, accompaniment, FINAL_OUTPUT)
            print("🎉 เสร็จสิ้น! ไฟล์เสียงที่เปลี่ยนเสียงร้องแล้ว:", FINAL_OUTPUT)

    # ทำความสะอาดไฟล์ชั่วคราว
    clean_temp_files(temp_folder, vocals, accompaniment, converted_vocals)

except Exception as e:
    print("❌ เกิดข้อผิดพลาด:", str(e))
    # ลบไฟล์ที่สร้างไว้หากเกิด error
    clean_temp_files(sub_output_folder)
