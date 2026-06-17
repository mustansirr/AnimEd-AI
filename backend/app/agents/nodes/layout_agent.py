"""
Layout Agent Node.
Assigns components and text to semantic layout zones for deterministic arrangement.
"""

import logging
from app.agents.state import AgentState, PositionedJSON

logger = logging.getLogger(__name__)

def _assign_zones(scene_json: dict) -> dict:
    """
    Map semantic scene spec to abstract layout zones.
    """
    layout_zones = {
        "title": None,
        "visualization": [],
        "explanation": None,
        "subtitle": None
    }
    
    if scene_json.get("title"):
        layout_zones["title"] = "TitleZone"
        
    if scene_json.get("caption"):
        layout_zones["explanation"] = "ExplanationZone"
        
    # All visual components go to the visualization zone
    components = scene_json.get("components", [])
    if components:
        logger.info(f"LayoutAgent Processing Components: {components}")
        layout_zones["visualization"] = "VisualizationZone"
        
    # END-TO-END VERIFICATION LOG
    logger.info(f"Layout Component: {components[0] if components else 'None'}")
        
    positioned = {
        "scene_type": scene_json.get("scene_type", "generic"),
        "learning_goal": scene_json.get("learning_goal", ""),
        "visual_metaphor": scene_json.get("visual_metaphor", ""),
        "components": components,
        "animation_sequence": scene_json.get("animation_sequence", []),
        "duration": scene_json.get("duration", 5),
        "title": scene_json.get("title", ""),
        "caption": scene_json.get("caption", ""),
        "layout_zones": layout_zones
    }
    
    return positioned


async def compute_layouts(state: AgentState) -> dict:
    video_id = state["video_id"]
    scene_jsons = state.get("scene_jsons", [])

    logger.info("--- ENTERING LAYOUT NODE ---")
    
    # Diagnostic Log: Before Layout
    schema_version = scene_jsons[0].get("schema_version", "unknown") if scene_jsons else "none"
    logger.info(f"[DIAGNOSTIC] Before Layout - scene count: {len(scene_jsons)}, schema version: {schema_version}")

    if not scene_jsons:
        logger.warning("[DIAGNOSTIC] scene_jsons is empty before layout computation!")
        logger.info("--- EXITING LAYOUT NODE ---")
        return {"positioned_jsons": []}

    positioned_jsons = []
    for scene in scene_jsons:
        pos_json = _assign_zones(scene)
        
        # Ensure component_data is preserved through layout
        if "component_data" in scene:
            pos_json["component_data"] = scene["component_data"]
            
        positioned_jsons.append(PositionedJSON(**pos_json))
        
    # Diagnostic Log: After Layout
    import json
    first_sample = json.dumps(positioned_jsons[0], indent=2) if positioned_jsons else "None"
    logger.info(f"[DIAGNOSTIC] After Layout - positioned_jsons count: {len(positioned_jsons)}")
    logger.info(f"[DIAGNOSTIC] First positioned_json sample:\n{first_sample}")

    logger.info(f"Assigned layout zones for {len(positioned_jsons)} scenes for video {video_id}")
    logger.info("--- EXITING LAYOUT NODE ---")
    return {"positioned_jsons": positioned_jsons}
