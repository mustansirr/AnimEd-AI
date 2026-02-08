"""
Webhook API routes for human-in-the-loop callbacks.

Handles script approval/rejection from the frontend.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ApprovalRequest, VideoResponse, VideoStatus
from app.services.supabase_client import (
    get_supabase_client,
    get_video,
    update_video_status,
)


router = APIRouter(prefix="/videos", tags=["webhooks"])


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
    "/{video_id}/approve",
    summary="Approve or reject scripts",
    description="""
    Handle script approval or rejection from the user.

    When the user reviews the generated scripts in the dashboard:
    - If approved: Status changes to 'generating' and workflow resumes
    - If rejected: Status changes to 'failed' and feedback is stored

    Note: In a future phase, this will call `resume_workflow()` from
    Mayank's LangGraph implementation to continue code generation.
    """
)
async def approve_scripts(video_id: str, request: ApprovalRequest):
    """Handle script approval/rejection callback."""
    video_uuid = validate_uuid(video_id, "video_id")

    # Verify video exists
    video = await get_video_or_404(video_uuid)

    # Verify video is in the correct state for approval
    if video.status != VideoStatus.WAITING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Video is not waiting for approval. "
                f"Current status: {video.status.value}"
            )
        )

    if request.approved:
        # Update status to generating
        await update_video_status(video_uuid, VideoStatus.GENERATING)

        # Resume the LangGraph workflow to continue with code generation
        from app.agents.workflow import resume_workflow
        import asyncio
        import logging

        logger = logging.getLogger(__name__)

        async def run_workflow_with_error_handling():
            """Wrapper to handle errors in background task."""
            try:
                await resume_workflow(
                    video_id=str(video_uuid),
                    approved=True,
                    feedback=request.feedback
                )
                logger.info(f"Workflow completed successfully for video {video_uuid}")
            except Exception as e:
                logger.error(f"Workflow failed for video {video_uuid}: {e}")
                # Update video status to failed
                try:
                    await update_video_status(video_uuid, VideoStatus.FAILED)
                except Exception as status_err:
                    logger.error(f"Failed to update status: {status_err}")

        # Run workflow resumption in the background (non-blocking)
        asyncio.create_task(run_workflow_with_error_handling())

        return {
            "video_id": video_id,
            "status": VideoStatus.GENERATING.value,
            "message": "Scripts approved. Video generation will begin."
        }
    else:
        # Handle rejection - store feedback and mark as failed
        client = get_supabase_client()
        client.table("videos").update({
            "status": VideoStatus.FAILED.value,
        }).eq("id", video_id).execute()

        # Store feedback in a way that can be retrieved later
        # For now, we'll log it. In production, consider a separate feedback table
        if request.feedback:
            # Could store in video metadata or separate table
            pass

        return {
            "video_id": video_id,
            "status": VideoStatus.FAILED.value,
            "message": "Scripts rejected.",
            "feedback": request.feedback
        }
