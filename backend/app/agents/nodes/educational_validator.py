"""
Educational Validator Node.

This node uses a lightweight LLM check to verify that the visuals
actually align with the narration and learning objective.
"""

import json
import logging
import re
from app.agents.state import AgentState
from app.services.llm_factory import create_llm

logger = logging.getLogger(__name__)

EDUCATIONAL_VALIDATOR_PROMPT = """You are an Educational Video Reviewer.
Your job is to determine if a video scene's visual elements successfully teach the intended learning objective.

Learning Objective: {objective}
Narration: {narration}
Visual Metaphor/Goal: {visual_goal}
Components: {components}
Animation Sequence: {animations}

Are the components and animations sufficient to teach this concept without being misleading or 'empty'?
Output ONLY a JSON object:
{{
    "is_valid": true,
    "reason": "Brief explanation"
}}
"""

async def validate_educational_quality(state: AgentState) -> dict:
    storyboards = state.get("storyboards", [])
    scene_jsons = state.get("scene_jsons", [])
    
    if not storyboards or not scene_jsons:
        return {}
        
    llm = create_llm("scripter", temperature=0.0)
    
    for i, (storyboard, scene) in enumerate(zip(storyboards, scene_jsons)):
        prompt = EDUCATIONAL_VALIDATOR_PROMPT.format(
            objective=storyboard.get("learning_objective", ""),
            narration=storyboard.get("narration", ""),
            visual_goal=scene.get("visual_metaphor", storyboard.get("visual_goal", "")),
            components=scene.get("components", []),
            animations=scene.get("animation_sequence", [])
        )
        
        try:
            response = await llm.ainvoke([
                {"role": "user", "content": prompt}
            ])
            
            content = response.content.strip()
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)
                
            data = json.loads(content)
            
            if not data.get("is_valid", True):
                error_msg = f"[DIAGNOSTIC] FATAL ERROR: Educational validation failed for scene {i+1}: {data.get('reason')}"
                logger.error(error_msg)
                return {"last_render_error": error_msg}
                
        except Exception as e:
            logger.warning(f"Educational validator LLM failed for scene {i+1}: {e}")
            
    logger.info("Educational validation passed for all scenes.")
    return {}
