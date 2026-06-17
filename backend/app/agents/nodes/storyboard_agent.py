"""
Storyboard Agent Node.
"""

import json
import logging
import re
from typing import Any
from uuid import UUID

from app.services.llm_factory import create_llm
from app.agents.state import AgentState, StoryboardScene
from app.agents.prompts.storyboard_prompts import (
    STORYBOARD_SYSTEM_PROMPT,
    create_storyboard_prompt,
)
from app.models.schemas import VideoStatus
from app.services.supabase_client import update_video_status

logger = logging.getLogger(__name__)

def _parse_json_response(content: str) -> dict[str, Any]:
    content = content.strip()
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group(0)
    content = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', content)
    return json.loads(content, strict=False)

async def write_storyboard(state: AgentState) -> dict:
    logger.info("--- ENTERING STORYBOARD NODE ---")
    video_id = state["video_id"]
    scene_plans = state.get("scene_plans", [])
    video_title = state.get("video_title", "Educational Video")

    if not scene_plans:
        logger.info("--- EXITING STORYBOARD NODE ---")
        return {"storyboards": []}

    llm = create_llm("scripter", temperature=0.7)
    viz_strategy = state.get("visualization_strategy", "generic_concept")
    metaphor = state.get("visual_metaphor", "A clear educational explanation")
    
    prompt = create_storyboard_prompt(
        scene_plans=scene_plans,
        video_title=video_title,
        visualization_strategy=viz_strategy,
        visual_metaphor=metaphor
    )

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = await llm.ainvoke([
                {"role": "system", "content": STORYBOARD_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            data = _parse_json_response(response.content)
            
            storyboards = []
            valid = True
            for s in data.get("storyboard", []):
                scene_number = s.get("scene_number", 1)
                goal = s.get("learning_objective", s.get("goal", ""))
                visual_goal = s.get("visual_goal", "")
                narration = s.get("narration", "")
                objects = s.get("objects", s.get("visuals", []))
                animations = s.get("animations", [])
                
                if not objects or not animations:
                    valid = False
                    break
                    
                # Format visual_plan so the frontend can display it neatly without needing schema changes
                visual_plan_str = f"Goal: {goal}\nVisual Goal: {visual_goal}\n\nObjects: {', '.join(objects)}\nAnimations: {', '.join(animations)}"
                
                storyboards.append(StoryboardScene(
                    scene_number=scene_number,
                    goal=goal,
                    narration=narration,
                    visuals=objects,
                    animations=animations,
                    duration=s.get("duration", 5)
                ))
            
            if not valid or not storyboards:
                logger.warning(f"Storyboard validation failed (empty objects/animations). Regenerating...")
                prompt += "\n\nERROR: A scene was generated with empty objects or animations. EVERY scene MUST have a non-empty objects array and non-empty animations array."
                continue
                
            # If we succeed, save to supabase
            from app.services.supabase_client import create_scene, update_video_status
            from app.models.schemas import VideoStatus
            
            # Update status to reviewing so the frontend knows to show the review UI
            await update_video_status(UUID(video_id), VideoStatus.WAITING_APPROVAL)
            
            for sb in storyboards:
                # Need to construct the string again for the db
                visual_plan_str = f"Goal: {sb['goal']}\n\nObjects: {', '.join(sb['visuals'])}\nAnimations: {', '.join(sb['animations'])}"
                await create_scene(
                    video_id=UUID(video_id),
                    scene_order=sb['scene_number'],
                    narration_script=sb['narration'],
                    visual_plan=visual_plan_str,
                )
                
            logger.info(f"Generated and saved storyboard with {len(storyboards)} scenes for video {video_id}")
            logger.info("--- EXITING STORYBOARD NODE ---")
            return {"storyboards": storyboards}
            
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Storyboard Agent failed: {e}")
                logger.info("--- EXITING STORYBOARD NODE ---")
                raise
            continue
            
    logger.info("--- EXITING STORYBOARD NODE ---")
    raise ValueError("Storyboard agent failed to generate valid coverage after maximum attempts.")
