import os
from pathlib import Path
import time

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output_voice_folder")
OUTPUT_SONG_DIR = Path("output_song_folder")
OUTPUT_VIDEO_DIR = Path("output_video_folder")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_SONG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

def create_output_folder():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sub_output_dir = OUTPUT_DIR / timestamp
    sub_output_dir.mkdir(parents=True, exist_ok=True)
    return sub_output_dir

def create_song_output_folder():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sub_output_dir = OUTPUT_SONG_DIR / timestamp
    sub_output_dir.mkdir(parents=True, exist_ok=True)
    return sub_output_dir

def create_video_output_folder():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sub_output_dir = OUTPUT_VIDEO_DIR / timestamp
    sub_output_dir.mkdir(parents=True, exist_ok=True)
    return sub_output_dir

def save_file(file, save_path):
    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())
