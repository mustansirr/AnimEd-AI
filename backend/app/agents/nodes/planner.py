"""
Planner Agent Node.

This node uses an LLM to create a structured video plan
based on the user's topic and syllabus context.
"""

import json
import logging
from typing import Any
from uuid import UUID

from langchain_groq import ChatGroq

from app.agents.state import AgentState, ScenePlan
from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    create_planner_prompt,
)
from app.config import get_settings
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

    return json.loads(content.strip())


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
    settings = get_settings()
    video_id = state["video_id"]

    # Update status to planning
    await update_video_status(UUID(video_id), VideoStatus.PLANNING)

    # Initialize Groq LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=settings.groq_api_key,
    )

    # Create prompt
    prompt = create_planner_prompt(
        user_prompt=state["user_prompt"],
        syllabus_context=state.get("syllabus_context", ""),
    )

    # Call LLM
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

        logger.info(
            f"Planned {len(scene_plans)} scenes for video {video_id}"
        )

        return {
            "video_title": plan.get("title", "Educational Video"),
            "topic_breakdown": plan.get("learning_objectives", []),
            "scene_plans": scene_plans,
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse planner response: {e}")
        raise ValueError(f"LLM returned invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Planner node failed: {e}")
        raise
