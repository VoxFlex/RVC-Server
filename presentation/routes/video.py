from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from services.video_service import convert_video_audio

router = APIRouter()

@router.post("/video/convert")
async def convert_video(
    request: Request,
    file: UploadFile = File(...),
    is_music_video: str = Form("false")  # ✅ เพิ่ม `Form()` เพื่อรับค่าจาก `form-data`
):
    # Debug ข้อมูลที่ส่งเข้ามา
    body = await request.form()
    print("🔎 Full Request Body:", body)

    # แปลง `string` เป็น `boolean`
    is_music_video = is_music_video.lower() == "true"

    print("🔎 Raw is_music_video Value:", is_music_video)

    try:
        return convert_video_audio(file, is_music_video)
    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}
