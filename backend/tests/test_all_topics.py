import asyncio
import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.services.supabase_client import create_video, get_video
from app.agents.workflow import start_workflow, resume_workflow
import logging

logging.basicConfig(level=logging.INFO)

USER_ID = "2d4af829-7439-4d23-b56e-c8a9802a1bbb"
TOPICS = ["DNA Replication", "Quantum Entanglement", "Bubble Sort", "Black Holes", "TCP/IP Protocol"]

async def run_topic(topic: str):
    print(f"\n--- Testing Topic: {topic} ---")
    video_id = await create_video(uuid.UUID(USER_ID), topic)
    print(f"Created Video ID: {video_id}")
    
    print("Starting workflow...")
    state = await start_workflow(str(video_id), topic, "")
    
    print("Approving scripts...")
    state = await resume_workflow(str(video_id), True, "")
    
    err = state.get("last_render_error")
    if err:
        print(f"[{topic}] FAILED with error: {err}")
    else:
        print(f"[{topic}] SUCCESS!")
    return state

async def main():
    for topic in TOPICS:
        await run_topic(topic)
        
if __name__ == "__main__":
    asyncio.run(main())
