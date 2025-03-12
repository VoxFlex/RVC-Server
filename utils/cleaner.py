import os
import shutil

def cleanup_files(*files):
    for file in files:
        if file and os.path.exists(file):
            os.remove(file)

def clean_temp_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"🧹 ลบไฟล์/โฟลเดอร์ชั่วคราว: {path}")
