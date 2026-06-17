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

from app.agents.workflow import start_workflow, resume_workflow

async def run_test():
    # Mock supabase updates to avoid DB pollution
    import app.services.supabase_client as db_client
    
    async def mock_update_status(*args, **kwargs): pass
    async def mock_create_scene(*args, **kwargs): pass
    async def mock_update_scene_text(*args, **kwargs): pass
    async def mock_get_scene_id(*args, **kwargs): return "mocked-scene-id"
    async def mock_mark_rendered(*args, **kwargs): pass
    async def mock_update_scene_code(*args, **kwargs): pass
    
    db_client.update_video_status = mock_update_status
    db_client.create_scene = mock_create_scene
    db_client.update_scene_text = mock_update_scene_text
    db_client.get_scene_id_by_order = mock_get_scene_id
    db_client.mark_scene_rendered = mock_mark_rendered
    db_client.update_scene_code = mock_update_scene_code
    
    video_id = str(uuid.uuid4())
    print(f"\n--- STARTING TRACE TEST FOR VIDEO: {video_id} ---")
    
    # 1. Start the workflow (goes up to human review)
    await start_workflow(
        video_id=video_id,
        user_prompt="Explain Linear Regression to a high schooler",
        syllabus_context=""
    )
    
    # 2. Resume workflow (simulate user approval)
    print("\n--- SIMULATING USER APPROVAL ---")
    state = await resume_workflow(
        video_id=video_id,
        approved=True,
        feedback=""
    )
    
    print("\n--- WORKFLOW COMPLETE ---")

if __name__ == "__main__":
    class MockResponse:
        def __init__(self, content):
            self.content = content
            
    class MockLLM:
        async def ainvoke(self, messages, *args, **kwargs):
            # Check prompt to see if it's storyboard or scene json
            prompt = messages[-1]["content"] if isinstance(messages[-1], dict) else messages[-1].content
            sys_prompt = messages[0]["content"] if isinstance(messages[0], dict) else messages[0].content
            
            if "visuals" in sys_prompt.lower() or "storyboard" in sys_prompt.lower() or "narration" in sys_prompt.lower() or "scene_plans" in prompt:
                # Storyboard response
                return MockResponse("""{"storyboard": [{"scene_number": 1, "goal": "goal", "narration": "text", "objects": ["GraphPlot"], "animations": ["draw_axes"]}]}""")
            elif "Educational Video Reviewer" in sys_prompt or "educational video reviewer" in prompt.lower() or "is_valid" in prompt:
                return MockResponse("""{"is_valid": true, "reason": "Looks good"}""")
            elif "Semantic Scene" in sys_prompt or "scene_json" in sys_prompt.lower():
                # SceneJSON response
                return MockResponse("""{"scene_json": [{"schema_version": "v2", "scene_type": "linear_regression", "learning_goal": "goal", "components": ["GraphPlot"], "component_data": {"x_range": [0,10,1]}, "animation_sequence": ["draw_axes"]}]}""")
            elif "Classifies the user" in prompt or "classifying" in prompt.lower() or "STEM category" in prompt:
                # Classifier response
                return MockResponse("""{"topic": "test", "visualization_strategy": "generic_concept", "confidence": 0.9}""")
            else:
                # Planner response
                return MockResponse("""{"scenes": [
                    {"scene_number": 1, "title": "Intro", "key_concepts": [], "visual_type": "text", "duration_seconds": 10},
                    {"scene_number": 2, "title": "Body", "key_concepts": [], "visual_type": "text", "duration_seconds": 10},
                    {"scene_number": 3, "title": "Body", "key_concepts": [], "visual_type": "text", "duration_seconds": 10},
                    {"scene_number": 4, "title": "Body", "key_concepts": [], "visual_type": "text", "duration_seconds": 10},
                    {"scene_number": 5, "title": "Outro", "key_concepts": [], "visual_type": "text", "duration_seconds": 10}
                ]}""")
                
    def mock_create_llm(*args, **kwargs):
        return MockLLM()

    # Also mock sandbox execution so we don't actually spawn docker containers for rendering
    import app.sandbox.renderer as renderer
    async def mock_execute(*args, **kwargs):
        return {"success": True, "video_path": "/tmp/mock_video.mp4"}
    class MockExecutor:
        async def execute(self, *args, **kwargs):
            return await mock_execute(*args, **kwargs)
    renderer.get_executor = lambda: MockExecutor()
    renderer.upload_to_storage = mock_execute # type: ignore
    
    # Patch all the imports of create_llm across the nodes
    with patch("app.agents.nodes.planner.create_llm", side_effect=mock_create_llm), \
         patch("app.agents.nodes.concept_classifier.create_llm", side_effect=mock_create_llm), \
         patch("app.agents.nodes.storyboard_agent.create_llm", side_effect=mock_create_llm), \
         patch("app.agents.nodes.scene_json_generator.create_llm", side_effect=mock_create_llm), \
         patch("app.agents.nodes.educational_validator.create_llm", side_effect=mock_create_llm):
        asyncio.run(run_test())
