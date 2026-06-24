import asyncio
import os
import sys
from uuid import uuid4

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

# Setup sys.path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app.agents.workflow import start_workflow, resume_workflow, get_workflow_state
from app.services.supabase_client import get_supabase_client, create_video

async def main():
    client = get_supabase_client()
    result = client.table("videos").select("user_id").limit(1).execute()
    if not result.data:
        print("❌ FAILED: No users found in videos table to use as user_id")
        sys.exit(1)
        
    user_id = result.data[0]["user_id"]
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "explain me friction with example"
    
    video_id = await create_video(user_id=user_id, prompt=topic)
    video_id = str(video_id)
    print(f"Starting test generation for video ID: {video_id} and topic: {topic}")
    
    # 1. Start workflow
    print("Running Planner -> Storyboard (waiting for human review)...")
    state = await start_workflow(
        video_id=video_id,
        user_prompt=topic,
    )
    
    # 2. Check if we hit the review step
    if "human_review" in state or not state.get("user_approved", False):
        print("Workflow paused for human review. Resuming with approval...")
        state = await resume_workflow(video_id=video_id, approved=True)
    
    # 3. Completion
    print("Workflow completed.")
    
    # 4. Verification
    video_path = state.get("last_rendered_video_path")
    if not video_path:
        print("FAILED: No video path found in state.")
        sys.exit(1)
        
    print(f"Video path: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"FAILED: Video file does not exist at {video_path}")
        sys.exit(1)
        
    size = os.path.getsize(video_path)
    if size < 10000:
        print(f"FAILED: Video file is too small ({size} bytes). Likely failed render.")
        sys.exit(1)
        
    print(f"SUCCESS: Video generated successfully! Size: {size} bytes")
    
if __name__ == "__main__":
    asyncio.run(main())
