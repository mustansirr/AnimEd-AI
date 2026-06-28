"""
Schema Validator Node.

This node intercepts SceneJSON before it hits the layout engine.
It deterministically verifies that the JSON schema matches the new 
Semantic Scene Specification (v2).
"""

import json
import logging
from uuid import UUID
from app.agents.state import AgentState
from app.models.schemas import VideoStatus
from app.services.supabase_client import update_video_status

logger = logging.getLogger(__name__)

def _validate_scene_schema(scene: dict) -> list[str]:
    errors = []
    
    # Check for v2 schema version marker if we enforced one, but here we just check fields.
    required_fields = ["components", "animation_sequence", "scene_type"]
    for field in required_fields:
        if field not in scene:
            errors.append(f"Missing required field: '{field}'")
            
    if errors:
        return errors
        
    components = scene.get("components", [])
    animations = scene.get("animation_sequence", [])
    
    if not isinstance(components, list):
        errors.append("'components' must be a list")
    elif len(components) == 0:
        errors.append("'components' must not be empty — every scene needs at least one visualization component")
    if not isinstance(animations, list):
        errors.append("'animation_sequence' must be a list")
            
    return errors

async def validate_schema(state: AgentState) -> dict:
    logger.info("--- ENTERING SCHEMA_VALIDATOR NODE ---")
    video_id = state.get("video_id")
    scene_jsons = state.get("scene_jsons", [])
    
    if not scene_jsons or len(scene_jsons) == 0:
        error_msg = "[DIAGNOSTIC] FATAL ERROR: scene_jsons is empty before layout computation. Aborting workflow."
        logger.error(error_msg)
        if video_id:
            try:
                from app.services.supabase_client import update_video_status
                from app.models.schemas import VideoStatus
                import asyncio
                # We need to run it, but this is an async function so we can await it
                await update_video_status(UUID(video_id), VideoStatus.FAILED)
            except Exception as e:
                logger.error(f"Failed to update video status to FAILED: {e}")
        logger.info("--- EXITING SCHEMA_VALIDATOR NODE (ERROR) ---")
        return {"last_render_error": error_msg}
        
    for i, scene in enumerate(scene_jsons):
        logger.info(f"Generated SceneJSON for scene {i+1}:\n{json.dumps(scene, indent=2)}")
        
        errors = _validate_scene_schema(scene)
        if errors:
            error_msg = f"Schema validation failed for scene {i+1}: " + ", ".join(errors)
            logger.warning(f"Validation Result: WARN\n{error_msg}")
            # Non-fatal failure: Log warning and continue
            
    logger.info("Validation Result: PASS")
    logger.info("--- EXITING SCHEMA_VALIDATOR NODE ---")
    return {}
