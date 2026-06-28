from typing import Any
"""
Schema Validator Node.

This node intercepts SceneJSON before it hits the layout engine.
It deterministically verifies that the JSON schema matches the new 
Semantic Scene Specification (v2).
"""

import json
import logging
import re
from uuid import UUID
from app.agents.state import AgentState
from app.models.schemas import VideoStatus
from app.services.supabase_client import update_video_status

logger = logging.getLogger(__name__)

def _validate_scene_schema(scene: Any) -> list[str]:
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
        
    # Strict Math Syntax Enforcement
    caret_pattern = re.compile(r"\^|\\wedge")
    
    def check_value(val, path=""):
        if isinstance(val, str):
            if caret_pattern.search(val):
                errors.append(f"Raw math caret or wedge detected at {path}: '{val}'. Must be routed exclusively through MathTex() or formatted correctly.")
        elif isinstance(val, dict):
            for k, v in val.items():
                check_value(v, f"{path}.{k}" if path else k)
        elif isinstance(val, list):
            for idx, item in enumerate(val):
                check_value(item, f"{path}[{idx}]" if path else f"[{idx}]")

    # Enforce checks on title, caption, and component_data
    if "title" in scene:
        check_value(scene["title"], "title")
    if "caption" in scene:
        check_value(scene["caption"], "caption")
    if "component_data" in scene:
        check_value(scene["component_data"], "component_data")
            
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
                await update_video_status(UUID(video_id), VideoStatus.FAILED)
            except Exception as e:
                logger.error(f"Failed to update video status to FAILED: {e}")
        logger.info("--- EXITING SCHEMA_VALIDATOR NODE (ERROR) ---")
        return {"last_render_error": error_msg}
        
    all_errors = []
    for i, scene in enumerate(scene_jsons):
        logger.info(f"Generated SceneJSON for scene {i+1}:\n{json.dumps(scene, indent=2)}")
        
        errors = _validate_scene_schema(scene)
        if errors:
            all_errors.extend([f"Scene {i+1}: {err}" for err in errors])
            
    if all_errors:
        error_msg = "Schema validation failed: " + "; ".join(all_errors)
        logger.warning(f"Validation Result: FAIL\n{error_msg}")
        logger.info("--- EXITING SCHEMA_VALIDATOR NODE (FAIL) ---")
        return {"last_render_error": error_msg}
        
    logger.info("Validation Result: PASS")
    logger.info("--- EXITING SCHEMA_VALIDATOR NODE ---")
    return {"last_render_error": None}
