"""
Planner Agent Node.

This node uses an LLM to create a structured video plan
based on the user's topic and syllabus context.
"""

import json
import logging
from typing import Any
from uuid import UUID

from app.services.llm_factory import create_llm

from app.agents.state import AgentState, ScenePlan
from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    create_planner_prompt,
)
from app.models.schemas import VideoStatus
from app.services.supabase_client import update_video_status

logger = logging.getLogger(__name__)


def _parse_json_response(content: str) -> dict[str, Any]:
    """Parse JSON from LLM response, handling markdown code blocks."""
    content = content.strip()

    # Remove markdown code blocks if present
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()
    
    # Fix unescaped backslashes often generated in LaTeX
    import re
    content = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', content)

    return json.loads(content, strict=False)


async def plan_scenes(state: AgentState) -> dict:
    """
    Plan video scenes using LLM.

    Uses Groq's free tier with llama-3.3-70b-versatile model
    to generate a structured video plan.

    Args:
        state: Current agent state with user_prompt and syllabus_context.

    Returns:
        Updated state dict with video_title, topic_breakdown, scene_plans.
    """
    video_id = state["video_id"]

    # Update status to planning
    await update_video_status(UUID(video_id), VideoStatus.PLANNING)

    # Initialize LLM for planning (provider configured via env vars)
    llm = create_llm("planner", temperature=0.7)

    # Create prompt
    prompt = create_planner_prompt(
        user_prompt=state["user_prompt"],
        syllabus_context=state.get("syllabus_context", ""),
        stem_blueprint=state.get("stem_blueprint")
    )

    import tiktoken
    try:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")

    sys_tokens = len(encoding.encode(PLANNER_SYSTEM_PROMPT))
    user_tokens = len(encoding.encode(prompt))
    total_estimated = sys_tokens + user_tokens
    
    logger.info(f"[DIAGNOSTIC] Planner Prompt Token Estimate: System={sys_tokens}, User={user_tokens}, Total={total_estimated}")
    
    # Auto-truncate if too large (e.g. > 5000 tokens)
    if total_estimated > 5000:
        logger.warning(f"[DIAGNOSTIC] Planner prompt exceeds 5000 tokens ({total_estimated}). Truncating syllabus context.")
        # Re-build prompt without syllabus to save tokens
        prompt = create_planner_prompt(
            user_prompt=state["user_prompt"],
            syllabus_context="[TRUNCATED DUE TO LENGTH LIMITS]"
        )
        user_tokens = len(encoding.encode(prompt))
        total_estimated = sys_tokens + user_tokens
        logger.info(f"[DIAGNOSTIC] New Token Estimate after truncation: System={sys_tokens}, User={user_tokens}, Total={total_estimated}")

    # Call LLM with a loop to enforce >= 5 scenes
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = await llm.ainvoke([
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])

            # Parse response
            plan = _parse_json_response(response.content)

            # Extract scene plans
            scene_plans: list[ScenePlan] = []
            for scene in plan.get("scenes", []):
                scene_plans.append(ScenePlan(
                    scene_number=scene.get("scene_number", len(scene_plans) + 1),
                    title=scene.get("title", ""),
                    key_concepts=scene.get("key_concepts", []),
                    visual_type=scene.get("visual_type", "text_animation"),
                    duration_seconds=scene.get("duration_seconds", 60),
                ))
                
            if len(scene_plans) < 5:
                logger.warning(f"Planner generated only {len(scene_plans)} scenes. Regenerating to meet minimum of 5.")
                prompt += f"\n\nERROR: Your previous plan only had {len(scene_plans)} scenes. You MUST generate at least 5 scenes as an educational story."
                continue

            logger.info(
                f"Planned {len(scene_plans)} scenes for video {video_id}"
            )

            return {
                "video_title": plan.get("title", "Educational Video"),
                "topic_breakdown": plan.get("learning_objectives", []),
                "scene_plans": scene_plans,
            }

        except json.JSONDecodeError as e:
            if attempt == max_attempts - 1:
                logger.error(f"Failed to parse planner response: {e}")
                raise ValueError(f"LLM returned invalid JSON: {e}")
            continue
        except Exception as e:
            error_str = str(e).lower()
            if "413" in error_str or "too large" in error_str or "rate limit" in error_str:
                error_msg = f"[DIAGNOSTIC] FATAL ERROR: LLM Provider rejected request due to size or rate limits: {e}"
                logger.error(error_msg)
                try:
                    await update_video_status(UUID(video_id), VideoStatus.FAILED)
                except Exception as db_e:
                    logger.error(f"Failed to update video status to FAILED: {db_e}")
                return {"last_render_error": error_msg}
                
            if attempt == max_attempts - 1:
                logger.error(f"Planner node failed: {e}")
                raise
            continue
            
    # Hard Validation: If planner returns 0 scenes after regeneration attempts
    if len(scene_plans) == 0:
        error_msg = f"[DIAGNOSTIC] FATAL ERROR: Planner generated 0 scenes after {max_attempts} attempts. Aborting workflow."
        logger.error(error_msg)
        
        # Log raw response for debugging
        logger.error(f"[DIAGNOSTIC] Raw LLM Response that caused 0 scenes:\n{response.content}")
        
        try:
            await update_video_status(UUID(video_id), VideoStatus.FAILED)
        except Exception as db_e:
            logger.error(f"Failed to update video status to FAILED: {db_e}")
            
        logger.info("--- EXITING PLANNER NODE (ERROR) ---")
        return {"last_render_error": error_msg}
            
    logger.info("--- EXITING PLANNER NODE ---")
    return {
        "video_title": plan.get("title", "Educational Video"),
        "topic_breakdown": plan.get("learning_objectives", []),
        "scene_plans": scene_plans,
        "last_render_error": None
    }
