"""
Renderer Node - LangGraph node for executing Manim code and managing results.

This module provides the execute_and_check node function that:
1. Executes Manim code via the Docker sandbox
2. Uploads rendered videos to Supabase Storage
3. Updates scene records in the database
4. Returns updated state for workflow routing
"""

import logging
from pathlib import Path
from uuid import UUID

from app.agents.state import AgentState
from app.sandbox.executor import ManimExecutor
from app.services import supabase_client
from app.config import get_settings

logger = logging.getLogger(__name__)

# Global executor instance
_executor: ManimExecutor | None = None


def get_executor() -> ManimExecutor:
    """Get or create the ManimExecutor singleton."""
    global _executor
    if _executor is None:
        settings = get_settings()
        storage_path = getattr(settings, "storage_path", "/app/storage")
        _executor = ManimExecutor(storage_path=storage_path)
    return _executor


async def upload_to_storage(
    local_path: str,
    video_id: str,
    scene_index: int,
) -> str:
    """
    Upload a rendered video segment to Supabase Storage.

    Args:
        local_path: Path to the local video file.
        video_id: UUID of the video record.
        scene_index: Index of the scene.

    Returns:
        Public URL to the uploaded video.
    """
    client = supabase_client.get_supabase_client()
    settings = get_settings()

    # Read the video file
    file_path = Path(local_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {local_path}")

    file_content = file_path.read_bytes()

    # Generate storage path
    storage_path = f"videos/{video_id}/scene_{scene_index}.mp4"

    # Upload to Supabase Storage
    bucket_name = getattr(settings, "storage_bucket", "video-segments")

    try:
        # Try to upload (will fail if exists, then update)
        client.storage.from_(bucket_name).upload(
            storage_path,
            file_content,
            file_options={"content-type": "video/mp4"},
        )
    except Exception as e:
        if "Duplicate" in str(e) or "already exists" in str(e).lower():
            # File exists, update it
            client.storage.from_(bucket_name).update(
                storage_path,
                file_content,
                file_options={"content-type": "video/mp4"},
            )
        else:
            raise

    # Get public URL
    public_url = client.storage.from_(bucket_name).get_public_url(storage_path)

    logger.info(f"Uploaded video segment to {public_url}")
    return public_url


async def execute_and_check(state: AgentState) -> AgentState:
    """
    Execute Manim code and check the result.

    This is a LangGraph node that:
    1. Gets the most recently generated code from generated_codes
    2. Executes it via the Docker sandbox
    3. On success: uploads video and marks scene as rendered
    4. On failure: stores error for reflector node

    Args:
        state: Current agent state with generated_codes.

    Returns:
        Updated AgentState with render results.
    """
    generated_codes = state.get("generated_codes", [])

    # Validate we have code to execute
    if not generated_codes:
        logger.error("No generated codes available to render")
        return {
            **state,
            "all_scenes_done": True,
            "last_render_error": None,
        }

    # Render the most recently generated code
    # This is the last item in generated_codes list
    scene_index = len(generated_codes) - 1
    code = generated_codes[scene_index]
    video_id = state["video_id"]

    logger.info(
        f"Executing render for video {video_id}, scene {scene_index}"
    )

    # Execute the code
    executor = get_executor()
    result = await executor.execute(code, video_id, scene_index)

    if result["success"]:
        logger.info(
            f"Render successful for video {video_id}, scene {scene_index}"
        )

        try:
            # Upload to Supabase Storage
            video_url = await upload_to_storage(
                result["video_path"],
                video_id,
                scene_index,
            )

            # Get scene ID and update database
            # Scene order is 1-indexed in DB, scene_index is 0-indexed
            scene_id = await supabase_client.get_scene_id_by_order(
                UUID(video_id),
                scene_index + 1,
            )

            if scene_id:
                await supabase_client.mark_scene_rendered(scene_id, video_url)
                logger.info(f"Marked scene {scene_id} as rendered")
            else:
                logger.warning(
                    f"Could not find scene for video {video_id}, "
                    f"order {scene_index + 1}"
                )

        except Exception as e:
            logger.exception(f"Error uploading video: {e}")
            # Don't fail the whole render, just log the error
            # The video was rendered successfully

        # Check if all scenes are done
        scripts = state.get("scripts", [])
        all_done = scene_index >= len(scripts) - 1

        return {
            **state,
            "current_scene_index": scene_index + 1 if not all_done else scene_index,
            "all_scenes_done": all_done,
            "last_render_error": None,
            "retry_count": 0,  # Reset retry count on success
        }

    else:
        # Render failed
        error_msg = result.get("error", "Unknown error")
        logger.error(
            f"Render failed for video {video_id}, scene {scene_index}: "
            f"{error_msg}"
        )

        # Log error to database
        try:
            scene_id = await supabase_client.get_scene_id_by_order(
                UUID(video_id),
                scene_index + 1,
            )
            if scene_id:
                await supabase_client.log_scene_error(scene_id, error_msg)
        except Exception as e:
            logger.exception(f"Error logging scene error: {e}")

        return {
            **state,
            "last_render_error": error_msg,
        }
