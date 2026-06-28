from typing import Any
"""
Domain Validator Node.

This node intercepts SceneJSON after Schema Validation and verifies
that the structural relationships are educationally accurate based on
the visualization strategy.
"""

import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def _validate_hierarchical(components: list) -> list[str]:
    errors = []
    if "HierarchyDiagram" not in components:
        errors.append("Hierarchical structure requires a HierarchyDiagram component.")
    return errors

def _validate_layered_network(components: list) -> list[str]:
    errors = []
    if "NetworkDiagram" not in components:
        errors.append("Layered network requires a NetworkDiagram component.")
    return errors

def _validate_coordinate_plot(components: list) -> list[str]:
    errors = []
    if "GraphPlot" not in components:
        errors.append("Coordinate plot requires a GraphPlot component.")
    return errors

def _validate_domain_logic(scene: Any, strategy: str) -> list[str]:
    components = scene.get("components", [])
    
    if strategy == "hierarchical_structure":
        return _validate_hierarchical(components)
    elif strategy == "layered_network":
        return _validate_layered_network(components)
    elif strategy == "coordinate_plot":
        return _validate_coordinate_plot(components)
        
    return []

def _validate_physical_phenomenon(scene: Any, topic: str, learning_goal: str) -> list[str]:
    errors = []
    text_to_check = (topic + " " + learning_goal).lower()
    
    physical_keywords = ["surface tension", "intermolecular forces", "cohesion", "adhesion", "droplet"]
    has_physics_keyword = any(kw in text_to_check for kw in physical_keywords)
    
    if has_physics_keyword:
        components = scene.get("components", [])
        if "GraphPlot" in components:
            errors.append("Generic GraphPlot is invalid for this physical phenomenon. Must use a specific physics/chemistry component like MoleculeDiagram, LiquidSurfaceDiagram, or ForceVectorDiagram.")
            
    return errors

async def validate_domain(state: AgentState) -> dict:
    logger.info("--- ENTERING DOMAIN_VALIDATOR NODE ---")
    scene_jsons = state.get("scene_jsons", [])
    strategy = str(state.get("visualization_strategy", "generic_concept"))
    topic = str(state.get("video_title", ""))
    
    if not scene_jsons:
        logger.info("--- EXITING DOMAIN_VALIDATOR NODE ---")
        return {}
        
    all_errors = []
    for i, scene in enumerate(scene_jsons):
        errors = _validate_domain_logic(scene, strategy)
        
        learning_goal = scene.get("learning_goal", "")
        phys_errors = _validate_physical_phenomenon(scene, topic, learning_goal)
        errors.extend(phys_errors)
        
        if errors:
            error_msg = f"Scene {i+1} failed: " + ", ".join(errors)
            all_errors.append(error_msg)
            
    if all_errors:
        final_msg = "[DIAGNOSTIC] FATAL ERROR: Domain validation failed: " + " | ".join(all_errors)
        logger.error(final_msg)
        return {"last_render_error": final_msg}
            
    logger.info("Domain validation checks complete.")
    logger.info("--- EXITING DOMAIN_VALIDATOR NODE ---")
    return {}
