import asyncio
from app.services.kling_service import kling_service

async def test_kling_handshake():
    print("testing_kling_api_dispatch")
    
    # Try a simple generation to see if the handshake task_id works
    image_url = "https://s16-def.ap4r.com/bs2/upload-ylab-stunt-sgp/kling/digital/image/Isabella.png"
    prompt = "A test video where she smiles at the camera."
    
    video_url = await kling_service.generate_kling_avatar(image_url, prompt, approval_granted=True)
    
    if video_url:
        print(f"kling_test_success: {video_url}")
    else:
        print("kling_test_failed")

if __name__ == "__main__":
    asyncio.run(test_kling_handshake())
