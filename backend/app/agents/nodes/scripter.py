"""
Scripter Agent Node.

This node uses an LLM to generate narration scripts and
visual descriptions for each scene in the video plan.
"""

import json
import logging
from typing import Any
from uuid import UUID
import re

from app.services.llm_factory import create_llm

from app.agents.state import AgentState, SceneScript
from app.agents.prompts.scripter_prompts import (
    SCRIPTER_SYSTEM_PROMPT,
    create_scripter_prompt,
)
from app.models.schemas import VideoStatus
from app.services.supabase_client import (
    create_scene,
    update_video_status,
)

logger = logging.getLogger(__name__)


import re

def _parse_json_response(content: str) -> dict[str, Any]:
    """Parse JSON from LLM response, handling markdown code blocks."""
    content = content.strip()

    # Try to extract JSON object if there's conversational filler
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group(0)

    # Fix unescaped backslashes often generated in LaTeX (e.g. \frac -> \\frac)
    # We replace any single \ that is NOT followed by " or \ with \\
    content = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', content)

    # strict=False allows unescaped literal control characters like newlines
    return json.loads(content, strict=False)


async def write_scripts(state: AgentState) -> dict:
    """
    Generate scripts for each scene using LLM.

    Iterates through scene_plans and generates narration + visual
    descriptions for each scene. Saves to Supabase as it goes.

    Args:
        state: Current agent state with scene_plans.

    Returns:
        Updated state dict with scripts list.
    """
    video_id = state["video_id"]
    scene_plans = state.get("scene_plans", [])
    video_title = state.get("video_title", "Educational Video")

    if not scene_plans:
        logger.warning(f"No scene plans found for video {video_id}")
        return {"scripts": []}

    # Initialize LLM for script writing (provider configured via env vars)
    llm = create_llm("scripter", temperature=0.7)

    scripts: list[SceneScript] = []

    for i, scene_plan in enumerate(scene_plans):
        # Create prompt for this scene
        prompt = create_scripter_prompt(
            scene_plan=scene_plan,
            scene_index=i,
            video_title=video_title,
        )

        try:
            # Call LLM
            response = await llm.ainvoke([
                {"role": "system", "content": SCRIPTER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])

            # Parse response
            script_data = _parse_json_response(response.content)

            script = SceneScript(
                scene_order=script_data.get("scene_order", i + 1),
                narration=script_data.get("narration", ""),
                visual_description=script_data.get("visual_description", ""),
                duration_estimate=script_data.get("duration_estimate", 60),
            )
            scripts.append(script)

            # Save to Supabase
            await create_scene(
                video_id=UUID(video_id),
                scene_order=script["scene_order"],
                narration_script=script["narration"],
                visual_plan=script["visual_description"],
            )

            logger.info(
                f"Generated script for scene {i + 1}/{len(scene_plans)} "
                f"of video {video_id}"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse scripter response for scene {i}: {e}")
            # Create a placeholder script
            placeholder = SceneScript(
                scene_order=i + 1,
                narration=f"Scene {i + 1}: {scene_plan.get('title', '')}",
                visual_description="Display title text",
                duration_estimate=60,
            )
            scripts.append(placeholder)
            
            # Save to Supabase to prevent missing scene errors downstream
            await create_scene(
                video_id=UUID(video_id),
                scene_order=placeholder["scene_order"],
                narration_script=placeholder["narration"],
                visual_plan=placeholder["visual_description"],
            )
        except Exception as e:
            logger.error(f"Scripter failed for scene {i}: {e}")
            raise

    # Update video status to waiting for approval
    await update_video_status(UUID(video_id), VideoStatus.WAITING_APPROVAL)

    logger.info(
        f"Completed {len(scripts)} scripts for video {video_id}, "
        "waiting for approval"
    )

    return {"scripts": scripts}
