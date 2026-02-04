"""
Coder Agent Node.

This node uses an LLM to generate Manim code from scene scripts
created by the scripter node.
"""

import logging
from typing import Optional
from uuid import UUID

from langchain_groq import ChatGroq

from app.agents.state import AgentState
from app.agents.prompts.coder_prompts import (
    CODER_SYSTEM_PROMPT,
    create_coder_prompt,
    clean_code_response,
)
from app.config import get_settings
from app.models.schemas import VideoStatus
from app.services.supabase_client import (
    get_scene_id_by_order,
    update_scene_code,
    update_video_status,
)

logger = logging.getLogger(__name__)


async def generate_code(state: AgentState) -> dict:
    """
    Generate Manim code for the current scene.

    Uses Groq's free tier with llama-3.3-70b-versatile model
    to generate Manim animation code based on scene scripts.

    Args:
        state: Current agent state with scripts and current_scene_index.

    Returns:
        Updated state dict with generated_codes and incremented scene index.
    """
    settings = get_settings()
    video_id = state["video_id"]
    scene_index = state["current_scene_index"]
    scripts = state.get("scripts", [])

    # Validate we have scripts to process
    if not scripts:
        logger.warning(f"No scripts found for video {video_id}")
        return {
            "all_scenes_done": True,
        }

    # Check if all scenes are done
    if scene_index >= len(scripts):
        logger.info(f"All scenes generated for video {video_id}")
        return {
            "all_scenes_done": True,
        }

    # Update status to rendering on first scene
    if scene_index == 0:
        await update_video_status(UUID(video_id), VideoStatus.RENDERING)

    # Get current scene script
    scene = scripts[scene_index]
    visual_description = scene.get("visual_description", "")
    narration = scene.get("narration", "")

    logger.info(
        f"Generating code for video {video_id}, "
        f"scene {scene_index + 1}/{len(scripts)}"
    )

    # Initialize Groq LLM with lower temperature for code
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=settings.groq_api_key,
    )

    # Create prompt with few-shot examples
    prompt = create_coder_prompt(
        visual_description=visual_description,
        narration=narration,
        include_examples=True,
    )

    try:
        # Call LLM
        response = await llm.ainvoke([
            {"role": "system", "content": CODER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])

        # Clean response
        code = clean_code_response(response.content)

        # Get scene ID from Supabase
        scene_order = scene.get("scene_order", scene_index + 1)
        scene_id = await get_scene_id_by_order(UUID(video_id), scene_order)

        if scene_id:
            # Update scene with generated code
            await update_scene_code(scene_id, code)
            logger.info(
                f"Updated scene {scene_id} with generated code "
                f"({len(code)} chars)"
            )

        # Update state
        generated_codes = state.get("generated_codes", []).copy()
        generated_codes.append(code)

        return {
            "generated_codes": generated_codes,
            "current_scene_index": scene_index + 1,
            "last_render_error": None,
        }

    except Exception as e:
        logger.error(f"Code generation failed for scene {scene_index}: {e}")
        raise


async def get_scene_for_index(
    video_id: str,
    scene_index: int
) -> Optional[UUID]:
    """
    Helper to get scene ID for a given index.

    Args:
        video_id: The video UUID string.
        scene_index: 0-based scene index.

    Returns:
        Scene UUID if found, None otherwise.
    """
    scene_order = scene_index + 1  # Convert to 1-based
    return await get_scene_id_by_order(UUID(video_id), scene_order)
