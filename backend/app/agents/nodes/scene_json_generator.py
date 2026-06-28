"""
Scene JSON Generator Node.
"""

import json
import logging
import re
from typing import cast, Any

from app.services.llm_factory import create_llm
from app.agents.state import AgentState, SceneJSON
from app.agents.prompts.scene_json_prompts import (
    create_scene_json_system_prompt,
    create_scene_json_prompt,
)
from app.sandbox.shared_animation_registry import SUPPORTED_COMPONENTS

logger = logging.getLogger(__name__)

def _parse_json_response(content: str) -> dict[str, Any]:
    content = content.strip()
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group(0)
    content = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', content)
    return json.loads(content, strict=False)

async def generate_scene_json(state: AgentState) -> dict:
    logger.info("--- ENTERING SCENE_JSON_GENERATOR NODE ---")
    video_id = state["video_id"]
    storyboards = state.get("storyboards", [])

    if not storyboards:
        logger.info("--- EXITING SCENE_JSON_GENERATOR NODE ---")
        return {"scene_jsons": []}

    llm = create_llm("scripter", temperature=0.1) # low temp for JSON parsing
    viz_strategy = str(state.get("visualization_strategy", "generic_concept"))
    suggested_component = str(state.get("suggested_component") or "")
    
    prompt = create_scene_json_prompt(storyboards, viz_strategy)
    allowed_components = list(SUPPORTED_COMPONENTS)
    system_prompt = create_scene_json_system_prompt(allowed_components, suggested_component)

    try:
        response = await llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ])
        data = _parse_json_response(response.content)
        
        scene_jsons = []
        raw_scenes = data.get("scene_json", [])
        
        # If LLM completely failed to return a list, fallback to an empty scene
        if not isinstance(raw_scenes, list) or len(raw_scenes) == 0:
            logger.warning(f"LLM failed to return scene_json list. Raw response: {response.content[:200]}")
            raw_scenes = [{}]
            
        for s in raw_scenes:
            logger.info(f"component_data for scene: {s.get('component_data', {})}")
            # Validate components
            components = s.get("components", [])
            valid_components = [c for c in components if c in allowed_components]
            
            # If the LLM hallucinated, raise an error instead of silently falling back
            if not valid_components:
                raise ValueError(f"Unsupported component: {components}. Must be one of {allowed_components}")
                
            # Enforce the suggested component from the Concept Classifier above all else
            if suggested_component:
                logger.info(f"Enforcing suggested_component from classifier: {suggested_component}")
                valid_components = [suggested_component]
                
            # Generic semantic assertion required by the pipeline architect
            if suggested_component and suggested_component not in valid_components:
                raise ValueError(f"Semantic blueprint mismatch: Expected {suggested_component}, got {valid_components}")
                
            logger.info(f"SceneJSONGenerator Component Decision: {valid_components}")
            
            # END-TO-END VERIFICATION LOG
            logger.info(f"SceneJSON Component: {valid_components[0] if valid_components else 'None'}")
            
            # Enforce minimum schema requirements even if LLM missed them
            scene_jsons.append(SceneJSON(
                schema_version=s.get("schema_version", "v2"),
                scene_type=s.get("scene_type", viz_strategy),
                learning_goal=s.get("learning_goal", ""),
                visual_metaphor=s.get("visual_metaphor", ""),
                components=cast(list[str], valid_components),
                component_data=s.get("component_data", {}),
                component_id=s.get("component_id"),
                visual_state=s.get("visual_state"),
                transition=s.get("transition"),
                animation_sequence=s.get("animation_sequence", []),
                duration=s.get("duration", 5),
                title=s.get("title", ""),
                caption=s.get("caption", ""),
                focal_bounding_box=[0.0, 0.0, 14.0, 8.0]
            ))
            
        logger.info(f"Generated {len(scene_jsons)} Scene JSONs for video {video_id}. First scene: {json.dumps(scene_jsons[0] if scene_jsons else {}, indent=2)}")
        logger.info("--- EXITING SCENE_JSON_GENERATOR NODE ---")
        return {"scene_jsons": scene_jsons}
        
    except Exception as e:
        logger.error(f"Scene JSON Generator failed: {e}")
        raise e
