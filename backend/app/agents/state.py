"""
Agent State definitions for the LangGraph workflow.

This module defines the shared state that flows through all nodes
in the agentic video generation workflow.
"""

from typing import List, Optional
from typing_extensions import TypedDict


class SceneScript(TypedDict):
    """Individual scene script with narration and visual description."""

    scene_order: int
    narration: str
    visual_description: str
    duration_estimate: int  # seconds


class ScenePlan(TypedDict):
    """Scene plan from the planner agent."""

    scene_number: int
    title: str
    key_concepts: List[str]
    visual_type: str  # text_animation | diagram | graph | equation
    duration_seconds: int


class AgentState(TypedDict):
    """
    Shared state for the LangGraph video generation workflow.

    This TypedDict flows through all nodes and accumulates
    results from each stage of processing.
    """

    # =========================================================================
    # Input (set at workflow start)
    # =========================================================================
    video_id: str
    user_prompt: str
    syllabus_context: str

    # =========================================================================
    # Planning outputs (from planner node)
    # =========================================================================
    video_title: str
    topic_breakdown: List[str]  # Learning objectives
    scene_plans: List[ScenePlan]  # Detailed scene structure

    # =========================================================================
    # Script outputs (from scripter node)
    # =========================================================================
    scripts: List[SceneScript]

    # =========================================================================
    # Human review (set by webhook/resume)
    # =========================================================================
    user_approved: bool
    user_feedback: Optional[str]

    # =========================================================================
    # Code generation (for Sanika's coder node)
    # =========================================================================
    current_scene_index: int
    generated_codes: List[str]

    # =========================================================================
    # Execution status (for Samruddhi's renderer node)
    # =========================================================================
    last_render_error: Optional[str]
    retry_count: int
    all_scenes_done: bool


def create_initial_state(
    video_id: str,
    user_prompt: str,
    syllabus_context: str = ""
) -> AgentState:
    """
    Create an initial AgentState for starting a new workflow.

    Args:
        video_id: UUID of the video record in Supabase.
        user_prompt: User's topic/concept request.
        syllabus_context: Optional RAG context from uploaded PDF.

    Returns:
        Initialized AgentState with default values.
    """
    return AgentState(
        # Input
        video_id=video_id,
        user_prompt=user_prompt,
        syllabus_context=syllabus_context,
        # Planning
        video_title="",
        topic_breakdown=[],
        scene_plans=[],
        # Scripts
        scripts=[],
        # Human review
        user_approved=False,
        user_feedback=None,
        # Code generation
        current_scene_index=0,
        generated_codes=[],
        # Execution
        last_render_error=None,
        retry_count=0,
        all_scenes_done=False,
    )
