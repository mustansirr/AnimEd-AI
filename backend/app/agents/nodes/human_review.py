"""
Human Review Node.

This node handles the interrupt/resume logic for human-in-the-loop
script approval before code generation begins.
"""

import logging
from uuid import UUID

from app.agents.state import AgentState
from app.models.schemas import VideoStatus
from app.services.supabase_client import update_video_status

logger = logging.getLogger(__name__)


async def wait_for_approval(state: AgentState) -> dict:
    """
    Handle state after human review interrupt resumes.

    This node is an INTERRUPT point in the workflow. When LangGraph
    hits this node with interrupt_before, execution pauses and state
    is saved.

    The frontend polls GET /api/videos/{id} and sees status='waiting_approval'.
    User reviews scripts in dashboard.

    When user clicks Approve/Reject:
    - POST /api/videos/{id}/approve is called
    - This resumes the graph with updated state (user_approved, user_feedback)
    - This node processes the approval decision

    Args:
        state: Current agent state with user_approved and user_feedback.

    Returns:
        Updated state dict preparing for code generation.
    """
    video_id = state["video_id"]
    user_approved = state.get("user_approved", False)
    user_feedback = state.get("user_feedback")

    if not user_approved:
        # Handle rejection
        logger.info(
            f"Video {video_id} scripts rejected. "
            f"Feedback: {user_feedback or 'No feedback provided'}"
        )

        # Update status to failed (for MVP - could route back to scripter)
        await update_video_status(UUID(video_id), VideoStatus.FAILED)

        return {
            "current_scene_index": 0,
            "all_scenes_done": True,  # Stop processing
        }

    # User approved - prepare for code generation
    logger.info(f"Video {video_id} scripts approved, starting code generation")

    await update_video_status(UUID(video_id), VideoStatus.GENERATING)

    return {
        "current_scene_index": 0,
        "generated_codes": [],
        "retry_count": 0,
        "all_scenes_done": False,
    }
