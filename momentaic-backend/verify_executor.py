
import asyncio
from app.agents.launch_executor_agent import launch_executor_agent, ExecutionMode
import os

async def verify_screenshots():
    print("Initializing browser...")
    await launch_executor_agent.initialize()
    
    product_info = {
        "name": "Test Product",
        "tagline": "A test tagline for automation",
        "url": "https://example.com",
        "description": "This is a test description for verifying browser automation.",
        "email": "test@example.com"
    }
    
    print("Executing dry run...")
    # Use a platform that doesn't require login and has a simple structure
    # startupbase is defined in platform_actions.py
    job = await launch_executor_agent.execute_launch(
        product_info=product_info,
        platforms=["startupbase"], 
        mode=ExecutionMode.DRY_RUN
    )
    
    print(f"Job Status: {job.status}")
    print(f"Results: {len(job.results)}")
    
    if job.results:
        result = job.results[0]
        print(f"Platform: {result.platform_name}")
        print(f"Status: {result.status}")
        print(f"Screenshot URL: {result.screenshot_path}")
        print(f"Latest Screenshot: {job.latest_screenshot}")
        
        # Verify file exists
        if result.screenshot_path:
            filename = result.screenshot_path.replace("/static/screenshots/", "")
            full_path = f"/root/momentaic/momentaic-backend/app/static/screenshots/{filename}"
            if os.path.exists(full_path):
                print(f"SUCCESS: Screenshot file exists at {full_path}")
                print(f"Size: {os.path.getsize(full_path)} bytes")
            else:
                print(f"FAILURE: Screenshot file missing at {full_path}")
    
    await launch_executor_agent.close()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify_screenshots())
