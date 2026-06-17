import asyncio
import sys
import uuid
import logging
from pathlib import Path
from unittest.mock import patch

# Add backend dir to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")

from app.agents.nodes.planner import plan_scenes
from app.agents.state import create_initial_state

async def run_test():
    # Mock supabase updates to avoid DB pollution
    import app.services.supabase_client as db_client
    async def mock_update_status(*args, **kwargs): pass
    db_client.update_video_status = mock_update_status
    
    # Disable OpenRouter fallback to avoid import error
    import os
    os.environ["OPENROUTER_API_KEY"] = ""
    
    video_id = str(uuid.uuid4())
    print(f"\n--- STARTING LIVE PLANNER DIAGNOSTIC TEST ---")
    
    state = create_initial_state(
        video_id=video_id,
        user_prompt="What is Linear Search?",
        syllabus_context=""
    )
    
    print("\n[Executing Planner Node with real LLM]")
    try:
        result = await plan_scenes(state)
        print("\n--- PLANNER EXECUTION COMPLETE ---")
        print(f"\nFinal state returned:\n{result}")
        if result.get("last_render_error"):
            print(f"\nERROR REPORTED: {result['last_render_error']}")
        else:
            print(f"\nSUCCESS: Generated {len(result.get('scene_plans', []))} scenes.")
            
    except Exception as e:
        print(f"\nEXCEPTION RAISED: {e}")

if __name__ == "__main__":
    # We do NOT mock the LLM here! We only mock the DB.
    # The planner will hit the Groq API.
    asyncio.run(run_test())
