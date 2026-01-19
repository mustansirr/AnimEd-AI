"""
Supabase client service for database operations.
Provides helper methods for CRUD operations on videos and scenes.
"""

from functools import lru_cache
from typing import Optional
from uuid import UUID

from supabase import Client, create_client

from app.config import get_settings
from app.models.schemas import (
    SceneResponse,
    VideoResponse,
    VideoStatus,
)


@lru_cache
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.

    Returns:
        Initialized Supabase client using service role key.

    Raises:
        ValueError: If Supabase credentials are not configured.
    """
    settings = get_settings()
    if not settings.is_supabase_configured:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_KEY environment variables."
        )
    return create_client(settings.supabase_url, settings.supabase_key)


# =============================================================================
# Video Operations
# =============================================================================

async def create_video(
    user_id: UUID,
    prompt: str,
    syllabus_doc_path: Optional[str] = None
) -> UUID:
    """
    Create a new video generation request.

    Args:
        user_id: The ID of the user creating the video.
        prompt: The topic/concept to explain in the video.
        syllabus_doc_path: Optional path to uploaded syllabus PDF.

    Returns:
        The UUID of the created video.
    """
    client = get_supabase_client()
    data = {
        "user_id": str(user_id),
        "prompt": prompt,
        "status": VideoStatus.PLANNING.value,
    }
    if syllabus_doc_path:
        data["syllabus_doc_path"] = syllabus_doc_path

    result = client.table("videos").insert(data).execute()
    return UUID(result.data[0]["id"])


async def get_video(video_id: UUID) -> Optional[VideoResponse]:
    """
    Get a video by its ID.

    Args:
        video_id: The UUID of the video.

    Returns:
        VideoResponse if found, None otherwise.
    """
    client = get_supabase_client()
    result = client.table("videos").select("*").eq("id", str(video_id)).execute()

    if not result.data:
        return None
    return VideoResponse(**result.data[0])


async def update_video_status(video_id: UUID, status: VideoStatus) -> bool:
    """
    Update the status of a video.

    Args:
        video_id: The UUID of the video.
        status: The new status value.

    Returns:
        True if update was successful, False otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("videos")
        .update({"status": status.value})
        .eq("id", str(video_id))
        .execute()
    )
    return len(result.data) > 0


async def set_final_video_url(video_id: UUID, final_video_url: str) -> bool:
    """
    Set the final video URL and mark as completed.

    Args:
        video_id: The UUID of the video.
        final_video_url: URL to the final stitched video.

    Returns:
        True if update was successful, False otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("videos")
        .update({
            "final_video_url": final_video_url,
            "status": VideoStatus.COMPLETED.value,
        })
        .eq("id", str(video_id))
        .execute()
    )
    return len(result.data) > 0


# =============================================================================
# Scene Operations
# =============================================================================

async def create_scene(
    video_id: UUID,
    scene_order: int,
    narration_script: Optional[str] = None,
    visual_plan: Optional[str] = None
) -> UUID:
    """
    Create a new scene for a video.

    Args:
        video_id: The UUID of the parent video.
        scene_order: Order of this scene (1-indexed).
        narration_script: The narration text for this scene.
        visual_plan: Description of visuals for Manim generation.

    Returns:
        The UUID of the created scene.
    """
    client = get_supabase_client()
    data = {
        "video_id": str(video_id),
        "scene_order": scene_order,
    }
    if narration_script:
        data["narration_script"] = narration_script
    if visual_plan:
        data["visual_plan"] = visual_plan

    result = client.table("scenes").insert(data).execute()
    return UUID(result.data[0]["id"])


async def get_scenes(video_id: UUID) -> list[SceneResponse]:
    """
    Get all scenes for a video, ordered by scene_order.

    Args:
        video_id: The UUID of the video.

    Returns:
        List of SceneResponse objects.
    """
    client = get_supabase_client()
    result = (
        client.table("scenes")
        .select("*")
        .eq("video_id", str(video_id))
        .order("scene_order")
        .execute()
    )
    return [SceneResponse(**scene) for scene in result.data]


async def get_scene(scene_id: UUID) -> Optional[SceneResponse]:
    """
    Get a scene by its ID.

    Args:
        scene_id: The UUID of the scene.

    Returns:
        SceneResponse if found, None otherwise.
    """
    client = get_supabase_client()
    result = client.table("scenes").select("*").eq("id", str(scene_id)).execute()

    if not result.data:
        return None
    return SceneResponse(**result.data[0])


async def update_scene_code(scene_id: UUID, manim_code: str) -> bool:
    """
    Update the Manim code for a scene.

    Args:
        scene_id: The UUID of the scene.
        manim_code: The generated Manim Python code.

    Returns:
        True if update was successful, False otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("scenes")
        .update({"manim_code": manim_code})
        .eq("id", str(scene_id))
        .execute()
    )
    return len(result.data) > 0


async def mark_scene_rendered(scene_id: UUID, video_segment_url: str) -> bool:
    """
    Mark a scene as rendered and store the video segment URL.

    Args:
        scene_id: The UUID of the scene.
        video_segment_url: URL to the rendered video segment.

    Returns:
        True if update was successful, False otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("scenes")
        .update({
            "is_rendered": True,
            "video_segment_url": video_segment_url,
            "error_log": None,  # Clear any previous errors
        })
        .eq("id", str(scene_id))
        .execute()
    )
    return len(result.data) > 0


async def log_scene_error(scene_id: UUID, error_log: str) -> bool:
    """
    Log an error for a scene (for self-correction agent feedback).

    Args:
        scene_id: The UUID of the scene.
        error_log: The error message from failed render.

    Returns:
        True if update was successful, False otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("scenes")
        .update({"error_log": error_log})
        .eq("id", str(scene_id))
        .execute()
    )
    return len(result.data) > 0


async def get_scene_id_by_order(video_id: UUID, scene_order: int) -> Optional[UUID]:
    """
    Get a scene ID by video ID and scene order.

    Args:
        video_id: The UUID of the video.
        scene_order: The order of the scene.

    Returns:
        Scene UUID if found, None otherwise.
    """
    client = get_supabase_client()
    result = (
        client.table("scenes")
        .select("id")
        .eq("video_id", str(video_id))
        .eq("scene_order", scene_order)
        .execute()
    )

    if not result.data:
        return None
    return UUID(result.data[0]["id"])
