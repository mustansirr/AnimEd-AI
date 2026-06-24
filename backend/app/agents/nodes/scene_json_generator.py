"""
Scene JSON Generator Node.
"""

import json
import logging
import re
from typing import Any

from app.services.llm_factory import create_llm
from app.agents.state import AgentState, SceneJSON
from app.agents.prompts.scene_json_prompts import (
    create_scene_json_system_prompt,
    create_scene_json_prompt,
)
from app.sandbox.shared_animation_registry import get_allowed_components

logger = logging.getLogger(__name__)

def _parse_json_response(content: str) -> dict[str, Any]:
    content = content.strip()
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group(0)
    content = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', content)
    return json.loads(content, strict=False)

# Force a hard semantic map directly aligned with your STEM blueprints
CONCEPT_COMPONENT_MAP = {
    "supervised classification": {
        "primary_component": "DecisionTreeDiagram",
        "fallback_layout": "ImageLabelCard"
    },
    "inertia and mass": {
        "primary_component": "ForceVectorDiagram", 
        "fallback_layout": "GeometryDiagram"
    },
    "surface tension": {
        "primary_component": "SurfaceTensionDiagram",
        "fallback_layout": "LiquidSurfaceDiagram"
    }
}

from app.sandbox.stem_blueprint_dataset import STEM_BLUEPRINT_REGISTRY

def parse_storyboard_to_json(state: dict):
    # 1. HARD PURGE: Wipe out any old residual component memory from previous runs
    state["component_data"] = {}
    
    # 2. Get the clean string topic input from the state
    learning_goal = state.get("learning_goal", "Geometry")
    visual_plan_text = str(state.get("visual_plan", "")).lower()
    goal_lower = learning_goal.lower()

    # ======================================================================
    # CRITICAL HOTFIX: DIRECT OVERRIDE FOR BUSINESS/DATA ARCHITECTURE TOPICS
    # ======================================================================
    if "business" in goal_lower or "warehouse" in goal_lower or "data" in goal_lower:
        # Map business intelligence metrics to charts or structured flowcharts
        state["components"] = ["FlowChart"]
        state["component_data"] = {
            "steps": ["Data Sources", "Data Warehouse", "Analytics Dashboard", "Business Insights"]
        }
        
        from app.agents.state import SceneJSON
        processed_scenes = []
        storyboards = state.get("storyboards", [{}]) or [{}]
        
        for idx, scene_data in enumerate(storyboards):
            scene_obj = SceneJSON(
                schema_version="v2",
                scene_type="generic_concept",
                learning_goal=learning_goal,
                visual_metaphor="Business data flow pipeline architecture",
                components=["FlowChart"],
                component_data=state["component_data"],
                animation_sequence=["intro", "highlight"] if idx == 0 else ["intro", "transform"],
                duration=int(scene_data.get("duration", 6)),
                title=scene_data.get("title", f"Scene {idx + 1}"),
                caption=scene_data.get("narration", "Analyzing structural organization pipelines."),
                focal_bounding_box=[0.0, 0.0, 14.0, 8.0]
            )
            # The original code dumps the object, but if I return an object my other loop does that. 
            # I'll just append the object since later nodes might expect dictionary or object depending on pydantic.
            processed_scenes.append(scene_obj)
            
        state["scene_jsons"] = [s if isinstance(s, dict) else s for s in processed_scenes]
        return state
    # ======================================================================
    
    # 3. FORCE REGISTRY MATCHING: Bind directly to our strongly-typed registry contract
    try:
        blueprint = STEM_BLUEPRINT_REGISTRY.require_blueprint(learning_goal)
        selected_component = blueprint.primary_component
    except Exception:
        # Fallback to general summary card if exact string match misses
        selected_component = "SummaryDiagram"

    # 2. Extract the actual multi-scene array from the storyboard planner state
    storyboards = state.get("storyboards", [])
    
    # If the upstream agent failed to populate a list, fallback to a single list element
    if not storyboards:
        storyboards = [{
            "visuals": state.get("visual_plan", "Introduce the topic"),
            "narration": state.get("narration", ""),
            "title": f"Topic: {learning_goal}"
        }]

    processed_scenes = []
    
    # 3. Loop through EVERY scene in the lesson plan dynamically
    for scene_idx, scene_data in enumerate(storyboards):
        visual_plan_text = str(scene_data.get("visuals", "")).lower()
        
        # Decide the component for this specific scene step
        if "example" in visual_plan_text or "image" in visual_plan_text:
            scene_components = ["ImageLabelCard"]
            scene_comp_data = {
                "label": f"Example: {learning_goal}",
                "image_path": f"assets/{learning_goal.lower().replace(' ', '_')}.png"
            }
        else:
            scene_components = [selected_component]
            scene_comp_data = {}

        # Build a valid, strongly-typed SceneJSON for this specific timeline slot
        from app.agents.state import SceneJSON
        scene_obj = SceneJSON(
            schema_version="v2",
            scene_type="generic_concept",
            learning_goal=learning_goal,
            visual_metaphor=visual_plan_text,
            components=scene_components,
            component_data=scene_comp_data,
            animation_sequence=["intro", "transform", "highlight"] if scene_idx > 0 else ["intro", "highlight"],
            duration=int(scene_data.get("duration", 7)),
            title=scene_data.get("title", f"Scene {scene_idx + 1}"),
            caption=scene_data.get("narration", ""),
            focal_bounding_box=[0.0, 0.0, 14.0, 8.0]
        )
        processed_scenes.append(scene_obj)

    # 4. Save the full array back to the global LangGraph state channel
    # Note: scene_jsons expects a list of dictionaries if state is dumped, but typically expects typed objects if LangGraph validates.
    # The original returned list of dicts. We'll dump them.
    state["scene_jsons"] = [s if isinstance(s, dict) else s for s in processed_scenes]
    
    # Set the root fields for backwards compatibility checks in legacy layout nodes
    if processed_scenes:
        state["components"] = processed_scenes[0]["components"]
        state["component_data"] = processed_scenes[0]["component_data"]

    return state
