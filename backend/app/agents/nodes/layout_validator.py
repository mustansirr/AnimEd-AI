"""
Layout Validator Node.

Intercepts PositionedJSON from the Layout Engine and ensures
that calculated coordinates are strictly within the Manim 16:9 frame.
Rejects any scene that will cause text clipping or off-screen drawing.
"""

import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

FRAME_X_MIN = -7.11
FRAME_X_MAX = 7.11
FRAME_Y_MIN = -4.0
FRAME_Y_MAX = 4.0

def _validate_bounds(objects: list) -> list[str]:
    errors = []
    
    for i, obj in enumerate(objects):
        pos = obj.get("position")
        if pos and len(pos) >= 2:
            x, y = pos[0], pos[1]
            if x < FRAME_X_MIN or x > FRAME_X_MAX:
                errors.append(f"Object {obj.get('id', i)} exceeds X bounds ({x})")
            if y < FRAME_Y_MIN or y > FRAME_Y_MAX:
                errors.append(f"Object {obj.get('id', i)} exceeds Y bounds ({y})")
                
    return errors

async def validate_layout(state: AgentState) -> dict:
    positioned_jsons = state.get("positioned_jsons", [])
    
    if not positioned_jsons or len(positioned_jsons) == 0:
        error_msg = "[DIAGNOSTIC] FATAL ERROR: positioned_jsons is empty before coder. Aborting workflow."
        logger.error(error_msg)
        try:
            from app.services.supabase_client import update_video_status
            from app.models.schemas import VideoStatus
            import asyncio
            video_id = state.get("video_id")
            if video_id:
                await update_video_status(video_id, VideoStatus.FAILED) # type: ignore
        except Exception as e:
            logger.error(f"Failed to update video status: {e}")
        return {"last_render_error": error_msg}
        
    for i, scene in enumerate(positioned_jsons):
        errors = _validate_bounds(scene.get("objects", []))
        if errors:
            error_msg = f"Layout validation failed for scene {i+1}: " + ", ".join(errors)
            logger.error(error_msg)
            return {"last_render_error": error_msg}
            
    # Fluid Transition Assertion (Code Parsing check if generated_codes exists)
    generated_codes = state.get("generated_codes", [])
    if generated_codes:
        for current_code in generated_codes:
            if "old_comp =" in current_code or "morph" in current_code.lower() or "transform" in current_code.lower():
                if "ReplacementTransform" not in current_code and "Transform(" not in current_code and ".animate" not in current_code and "GlobalTransitionEngine.transition_between_states" not in current_code:
                    return {"last_render_error": "Fluid Transition Assertion Failed: Scene contains multi-part transition but missing ReplacementTransform, Transform, or .animate."}

    logger.info("Layout validation passed for all scenes.")
    return {}
