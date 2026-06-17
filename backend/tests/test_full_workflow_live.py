import asyncio
import sys
import uuid
import logging
from pathlib import Path

# Add backend dir to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")

from app.agents.workflow import start_workflow, resume_workflow, get_workflow_state

async def run_test():
    # Mock supabase to avoid DB pollution
    import app.services.supabase_client as db_client
    async def mock_pass(*args, **kwargs): return True
    async def mock_create_scene(*args, **kwargs): return uuid.uuid4()
    async def mock_get_scene_id_by_order(*args, **kwargs): return uuid.uuid4()
    async def mock_get_scenes(*args, **kwargs): return []
    
    db_client.update_video_status = mock_pass
    db_client.save_scenes = mock_pass
    db_client.update_scenes = mock_pass
    db_client.create_scene = mock_create_scene
    db_client.update_scene_code = mock_pass
    db_client.log_scene_error = mock_pass
    db_client.mark_scene_rendered = mock_pass
    db_client.get_scene_id_by_order = mock_get_scene_id_by_order
    db_client.set_final_video_url = mock_pass
    db_client.get_scenes = mock_get_scenes
    
    # Disable OpenRouter fallback
    import os
    os.environ["OPENROUTER_API_KEY"] = ""
    
    video_id = str(uuid.uuid4())
    print(f"\n--- STARTING LIVE WORKFLOW E2E TEST: {video_id} ---")
    
    print("\n[Starting workflow...]")
    state = await start_workflow(
        video_id=video_id,
        user_prompt="What is Linear Search?",
        syllabus_context=""
    )
    
    print("\n[Workflow paused for human review. Resuming...]")
    state = await resume_workflow(
        video_id=video_id,
        approved=True,
        feedback=""
    )
    
    print("\n--- WORKFLOW EXECUTION COMPLETE ---")
    err = state.get("last_render_error")
    
    scene_plans = state.get("scene_plans", [])
    storyboards = state.get("storyboards", [])
    scene_jsons = state.get("scene_jsons", [])
    positioned_jsons = state.get("positioned_jsons", [])
    generated_codes = state.get("generated_codes", [])
    
    print("\n=== DIAGNOSTIC COUNTS ===")
    print(f"scene_count: {len(scene_plans)}")
    print(f"storyboard_count: {len(storyboards)}")
    print(f"scene_json_count: {len(scene_jsons)}")
    print(f"positioned_json_count: {len(positioned_jsons)}")
    print(f"generated_code_count: {len(generated_codes)}")
    
    if err:
        print(f"\nWORKFLOW ABORTED WITH ERROR: {err}")
    else:
        print(f"\nWORKFLOW COMPLETED SUCCESSFULLY!")
        
    for name, arr in [("planner", scene_plans), ("storyboard", storyboards), ("scene_json", scene_jsons), ("layout", positioned_jsons), ("coder", generated_codes)]:
        if len(arr) == 0:
            print(f"\nFATAL: Node {name} returned 0 items!")
            print(f"State contents for {name}:\n{arr}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_test())
