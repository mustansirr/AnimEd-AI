"""
LangGraph Workflow for Video Generation.

This module defines the main StateGraph workflow that orchestrates
the agentic video generation process.
"""

import logging
from typing import Dict, Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState, create_initial_state
from app.agents.nodes.context import retrieve_context_node
from app.agents.nodes.planner import plan_scenes
from app.agents.nodes.scripter import write_scripts
from app.agents.nodes.human_review import wait_for_approval
from app.agents.nodes.coder import generate_code

logger = logging.getLogger(__name__)


# =============================================================================
# Active Workflow Storage
# =============================================================================

# Store active workflows in memory (use Redis for production scaling)
_active_workflows: Dict[str, tuple] = {}


# =============================================================================
# Workflow Graph Definition
# =============================================================================

def create_workflow():
    """
    Create and compile the LangGraph workflow.

    The workflow processes video generation through these stages:
    1. retrieve_info - Get syllabus context via RAG
    2. planner - Create structured scene plans
    3. scripter - Generate narration and visual descriptions
    4. human_review - Wait for user approval (INTERRUPT POINT)
    5. coder - Generate Manim code for each scene

    After coder, the workflow continues to rendering
    (implemented by Samruddhi).

    Returns:
        Compiled StateGraph with checkpointing enabled.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("retrieve_info", retrieve_context_node)
    workflow.add_node("planner", plan_scenes)
    workflow.add_node("scripter", write_scripts)
    workflow.add_node("human_review", wait_for_approval)
    workflow.add_node("coder", generate_code)

    # Define edges (linear flow for now)
    workflow.set_entry_point("retrieve_info")
    workflow.add_edge("retrieve_info", "planner")
    workflow.add_edge("planner", "scripter")
    workflow.add_edge("scripter", "human_review")

    # After human_review, route based on approval
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "approved": "coder",  # Go to code generation
            "rejected": END,
        }
    )

    # After coder, route based on scene completion
    workflow.add_conditional_edges(
        "coder",
        route_after_coder,
        {
            "next_scene": "coder",  # More scenes to generate
            "complete": END,  # All scenes done (will go to renderer later)
        }
    )

    # Compile with checkpointer for state persistence
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"],  # CRITICAL for HITL
    )


def route_after_review(state: AgentState) -> Literal["approved", "rejected"]:
    """
    Route workflow after human review.

    Args:
        state: Current agent state.

    Returns:
        "approved" or "rejected" based on user decision.
    """
    if state.get("user_approved", False):
        return "approved"
    return "rejected"


def route_after_coder(state: AgentState) -> Literal["next_scene", "complete"]:
    """
    Route workflow after code generation.

    Determines whether to continue generating code for more scenes
    or complete the code generation phase.

    Args:
        state: Current agent state.

    Returns:
        "next_scene" if more scenes to process, "complete" otherwise.
    """
    if state.get("all_scenes_done", False):
        return "complete"

    scripts = state.get("scripts", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(scripts):
        return "complete"

    return "next_scene"


# =============================================================================
# Workflow Control Functions
# =============================================================================

async def start_workflow(
    video_id: str,
    user_prompt: str,
    syllabus_context: str = ""
) -> AgentState:
    """
    Start a new video generation workflow.

    Called by POST /api/videos endpoint after creating the video record.
    The workflow runs until it hits the interrupt_before=["human_review"],
    then pauses and saves state.

    Args:
        video_id: UUID of the video record.
        user_prompt: User's topic/concept request.
        syllabus_context: Optional pre-fetched context.

    Returns:
        Current state when workflow pauses at human_review.
    """
    workflow = create_workflow()
    config = {"configurable": {"thread_id": video_id}}

    initial_state = create_initial_state(
        video_id=video_id,
        user_prompt=user_prompt,
        syllabus_context=syllabus_context,
    )

    logger.info(f"Starting workflow for video {video_id}")

    # Run until interrupt
    result = await workflow.ainvoke(initial_state, config)

    # Store for resumption
    _active_workflows[video_id] = (workflow, config)

    logger.info(f"Workflow paused at human_review for video {video_id}")

    return result


async def resume_workflow(
    video_id: str,
    approved: bool,
    feedback: str = None
) -> AgentState:
    """
    Resume a paused workflow after human review.

    Called by POST /api/videos/{id}/approve endpoint.
    Updates the state with approval decision and resumes execution.

    Args:
        video_id: UUID of the video record.
        approved: Whether the user approved the scripts.
        feedback: Optional feedback from the user.

    Returns:
        Final state after workflow completes.

    Raises:
        ValueError: If no active workflow exists for this video_id.
    """
    if video_id not in _active_workflows:
        raise ValueError(f"No active workflow found for video {video_id}")

    workflow, config = _active_workflows[video_id]

    logger.info(
        f"Resuming workflow for video {video_id}, "
        f"approved={approved}"
    )

    # Update state with approval
    await workflow.aupdate_state(
        config,
        {
            "user_approved": approved,
            "user_feedback": feedback,
        }
    )

    # Resume execution
    result = await workflow.ainvoke(None, config)

    # Clean up
    del _active_workflows[video_id]

    logger.info(f"Workflow completed for video {video_id}")

    return result


def get_workflow_state(video_id: str) -> AgentState | None:
    """
    Get the current state of an active workflow.

    Args:
        video_id: UUID of the video.

    Returns:
        Current AgentState or None if no active workflow.
    """
    if video_id not in _active_workflows:
        return None

    workflow, config = _active_workflows[video_id]
    return workflow.get_state(config).values


def is_workflow_active(video_id: str) -> bool:
    """Check if a workflow is currently active for a video."""
    return video_id in _active_workflows
