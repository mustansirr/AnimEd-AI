"""
Video API routes for CRUD operations.

Handles video creation, retrieval, and scene listing.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import (
    SceneResponse,
    VideoCreate,
    VideoResponse,
    VideoStatus,
)
from app.services.supabase_client import (
    create_video,
    get_video,
    get_scenes,
    get_completed_video_by_prompt,
    duplicate_scenes,
    set_final_video_url,
)


router = APIRouter(prefix="/videos", tags=["videos"])


# =============================================================================
# Helper Functions
# =============================================================================

def validate_uuid(value: str, field_name: str = "id") -> UUID:
    """Validate and parse a string to UUID."""
    try:
        return UUID(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Must be a valid UUID."
        )


async def get_video_or_404(video_id: UUID) -> VideoResponse:
    """Get a video by ID or raise 404."""
    video = await get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found."
        )
    return video


# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create video request",
    description="""
    Create a new video generation request.

    This endpoint only creates the video record. To start the workflow,
    call POST /api/videos/{id}/start after uploading any PDF context.
    """,
)
async def create_video_request(
    video: VideoCreate,
    user_id: str = Query(..., description="UUID of the authenticated user"),
):
    """Create a new video generation request."""
    # Validate user_id
    user_uuid = validate_uuid(user_id, "user_id")

    # Check for cached video if no syllabus
    if not video.syllabus_doc_path:
        cached_video = await get_completed_video_by_prompt(video.prompt)
        if cached_video:
            # Create a new video record for this user
            new_video_id = await create_video(
                user_id=user_uuid,
                prompt=video.prompt,
                syllabus_doc_path=None
            )
            # Mark it as completed and link URL
            await set_final_video_url(new_video_id, str(cached_video.final_video_url))
            # Duplicate scenes
            await duplicate_scenes(cached_video.id, new_video_id)
            
            return {
                "video_id": str(new_video_id),
                "status": VideoStatus.COMPLETED.value,
                "message": "Video retrieved from cache."
            }

    # Create video record (workflow is NOT started yet)
    video_id = await create_video(
        user_id=user_uuid,
        prompt=video.prompt,
        syllabus_doc_path=video.syllabus_doc_path
    )

    return {
        "video_id": str(video_id),
        "status": VideoStatus.PLANNING.value,
        "message": "Video created. Upload PDF context, then start the workflow."
    }


@router.post(
    "/{video_id}/start",
    response_model=dict,
    summary="Start video generation workflow",
    description="""
    Start the LangGraph workflow for a video.

    Call this AFTER uploading any PDF context so the planner
    can use the RAG embeddings. The workflow will run planning
    and scripting, then automatically bypass human review and render in the background.
    """,
)
async def start_video_workflow(video_id: str):
    """Start the generation workflow for a video."""
    video_uuid = validate_uuid(video_id, "video_id")

    # Verify video exists
    video = await get_video_or_404(video_uuid)

    # Start the LangGraph workflow
    from app.agents.workflow import start_workflow, resume_workflow
    import asyncio
    
    async def run_full_workflow():
        try:
            state = await start_workflow(
                video_id=str(video_uuid),
                user_prompt=video.prompt,
                syllabus_context=""  # retrieve_context_node will fetch from RAG
            )
            
            # The workflow will pause automatically at the human_review node
            # The frontend UI will call the /approve endpoint to resume it.
        except Exception as e:
            import logging
            from app.services.supabase_client import update_video_status
            logging.error(f"Workflow error for video {video_id}: {e}")
            try:
                await update_video_status(video_uuid, VideoStatus.FAILED)
            except Exception as status_err:
                logging.error(f"Failed to update status to FAILED: {status_err}")

    # Fire and forget the full workflow to prevent HTTP timeouts
    asyncio.create_task(run_full_workflow())

    return {
        "video_id": str(video_uuid),
        "status": VideoStatus.GENERATING.value,
        "message": "Workflow started and rendering in background"
    }


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    summary="Get video details",
    description="Retrieve the current status and details of a video request."
)
async def get_video_details(video_id: str):
    """Get video details and current status."""
    video_uuid = validate_uuid(video_id, "video_id")
    return await get_video_or_404(video_uuid)


@router.get(
    "/{video_id}/scenes",
    response_model=List[SceneResponse],
    summary="Get video scenes",
    description="""
    Retrieve all scenes for a video, ordered by scene_order.

    This endpoint is used by the frontend during the approval flow
    to display generated scripts for user review.
    """
)
async def get_video_scenes(video_id: str):
    """Get all scenes for a video."""
    video_uuid = validate_uuid(video_id, "video_id")

    # Verify video exists
    await get_video_or_404(video_uuid)

    # Get scenes
    scenes = await get_scenes(video_uuid)
    return scenes


@router.get(
    "",
    response_model=List[VideoResponse],
    summary="List user videos",
    description="List all videos for a specific user."
)
async def list_user_videos(
    user_id: str = Query(..., description="UUID of the user"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Max results"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination"),
):
    """List all videos for a user."""
    from app.services.supabase_client import get_supabase_client

    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()

    safe_limit = limit if limit is not None else 20
    safe_offset = offset if offset is not None else 0

    result = (
        client.table("videos")
        .select("*")
        .eq("user_id", str(user_uuid))
        .order("created_at", desc=True)
        .range(safe_offset, safe_offset + safe_limit - 1)
        .execute()
    )

    return [VideoResponse.model_validate(video) for video in result.data]


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a video",
    description="Delete a video and all its associated scenes.",
)
async def delete_video(video_id: str):
    """Delete a video and its scenes."""
    from app.services.supabase_client import get_supabase_client

    video_uuid = validate_uuid(video_id, "video_id")

    # Verify video exists
    await get_video_or_404(video_uuid)

    client = get_supabase_client()

    # Delete associated scenes first (foreign key dependency)
    client.table("scenes").delete().eq("video_id", str(video_uuid)).execute()

    # Delete the video record
    client.table("videos").delete().eq("id", str(video_uuid)).execute()

    return None
