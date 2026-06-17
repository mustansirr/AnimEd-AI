"""
Fix Agent Node.
Handles feedback from the Video Quality Evaluator and routes back to Layout or SceneJSON.
"""

import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def fix_scene(state: AgentState) -> dict:
    video_id = state["video_id"]
    scores = state.get("quality_scores")
    
    if not scores:
        return {}
        
    logger.warning(
        f"Fix Agent activated for video {video_id}. Feedback: {scores.get('feedback')}"
    )
    
    # In a fully realized implementation, this agent would:
    # 1. Analyze the feedback
    # 2. Re-prompt the Layout Agent or Scene JSON Generator
    # 3. Modify the specific JSON that failed
    
    # For now, we will clear the positioned JSON to force a re-generation of layout
    # or clear the generated_codes to force the Coder to re-try.
    
    # Simple fix: decrement scene index so the Manim Generator (Coder) retries,
    # and increment retry count.
    
    current_index = state.get("current_scene_index", 1)
    retry_count = state.get("retry_count", 0)
    
    # We step back to re-render the scene.
    # The workflow logic will route back to `manim_generator`.
    
    return {
        "current_scene_index": max(0, current_index - 1),
        "retry_count": retry_count + 1,
        "last_render_error": f"Quality check failed: {scores.get('feedback')}"
    }
