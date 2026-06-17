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
    logger.info(f"Video {video_id} scripts approved, preparing next nodes")

    await update_video_status(UUID(video_id), VideoStatus.GENERATING)
    
    # CRITICAL FIX: Re-fetch scenes from Supabase because the user might have edited them in the frontend!
    from app.services.supabase_client import get_scenes
    updated_scenes = await get_scenes(UUID(video_id))
    
    storyboards = state.get("storyboards", [])
    
    # We must patch the state's storyboards with the new text from the UI
    for i, scene in enumerate(updated_scenes):
        if i < len(storyboards):
            # Update narration
            storyboards[i]["narration"] = scene.narration_script or storyboards[i]["narration"]
            # The UI updated visual_plan as a single string. 
            # We don't need to parse it back into goals/visuals/animations arrays 
            # because the next node (SceneJSON Generator) reads it as a string anyway!
            # Let's just override "visuals" with the raw text so the next prompt gets it.
            if scene.visual_plan:
                storyboards[i]["visuals"] = [scene.visual_plan]
                storyboards[i]["animations"] = [] # Clear out animations since they are now embedded in the string

    return {
        "storyboards": storyboards,
        "current_scene_index": 0,
        "generated_codes": [],
        "retry_count": 0,
        "all_scenes_done": False,
    }
