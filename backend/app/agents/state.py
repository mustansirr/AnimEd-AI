"""
Agent State definitions for the LangGraph workflow.

This module defines the shared state that flows through all nodes
in the agentic video generation workflow.
"""

from typing import List, Optional, Annotated, Union
from typing_extensions import TypedDict

def merge_component_data(old_data: dict, new_data: dict) -> dict:
    return {} if not new_data else {**old_data, **new_data}


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
    visual_type: str
    duration_seconds: int


class StoryboardScene(TypedDict):
    """Storyboard output for a scene."""
    scene_number: int
    goal: str
    narration: str
    visuals: List[str]
    animations: List[str]
    duration: int


class SceneJSON(TypedDict):
    """Declarative JSON representing semantic scene specifications."""
    schema_version: str
    scene_type: str
    learning_goal: str
    visual_metaphor: str
    components: List[str]
    component_data: dict
    component_id: Optional[str]
    visual_state: Optional[dict]
    transition: Optional[dict]
    animation_sequence: List[Union[str, dict]]
    duration: int
    title: str
    caption: str
    focal_bounding_box: Optional[List[float]]


class PositionedJSON(TypedDict):
    """Scene JSON with abstract layout zones assigned."""
    scene_type: str
    learning_goal: str
    visual_metaphor: str
    components: List[str]
    component_id: Optional[str]
    visual_state: Optional[dict]
    transition: Optional[dict]
    animation_sequence: List[Union[str, dict]]
    duration: int
    title: str
    caption: str
    layout_zones: dict
    focal_bounding_box: Optional[List[float]]


class QualityScores(TypedDict):
    """Scores from the Video Quality Evaluator."""
    visual_clarity: int
    educational_clarity: int
    layout_quality: int
    animation_quality: int
    professional_appearance: int
    feedback: str


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
    # Concept Classification (from classifier node)
    # =========================================================================
    concept_topic: Optional[str]
    visualization_strategy: Optional[str]
    stem_blueprint: Optional[dict]

    # =========================================================================
    # Planning outputs (from planner node)
    # =========================================================================
    video_title: str
    topic_breakdown: List[str]  # Learning objectives
    scene_plans: List[ScenePlan]  # Detailed scene structure

    # =========================================================================
    # Scripts / Storyboard outputs
    # =========================================================================
    scripts: List[SceneScript]
    storyboards: List[StoryboardScene]

    # =========================================================================
    # Human review (set by webhook/resume)
    # =========================================================================
    user_approved: bool
    user_feedback: Optional[str]

    # =========================================================================
    # JSON Generation & Layout
    # =========================================================================
    visual_metaphor: Optional[str]
    suggested_component: Optional[str]
    component_data: Annotated[dict, merge_component_data]
    scene_jsons: List[SceneJSON]
    positioned_jsons: List[PositionedJSON]

    # =========================================================================
    # Code generation (Manim Generator)
    # =========================================================================
    current_scene_index: int
    generated_codes: List[str]

    # =========================================================================
    # Execution status & QA (Renderer, Evaluator, Fix Agent)
    # =========================================================================
    last_render_error: Optional[str]
    last_rendered_video_path: Optional[str]
    retry_count: int
    all_scenes_done: bool
    quality_scores: Optional[QualityScores]


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
        # Concept Classification
        concept_topic=None,
        visualization_strategy=None,
        visual_metaphor=None,
        suggested_component=None,
        stem_blueprint=None,
        component_data={},
        # Planning
        video_title="",
        topic_breakdown=[],
        scene_plans=[],
        # Scripts/Storyboard
        scripts=[],
        storyboards=[],
        # Human review
        user_approved=False,
        user_feedback=None,
        # JSON & Layout
        scene_jsons=[],
        positioned_jsons=[],
        # Code generation
        current_scene_index=0,
        generated_codes=[],
        # Execution & QA
        last_render_error=None,
        last_rendered_video_path=None,
        retry_count=0,
        all_scenes_done=False,
        quality_scores=None,
    )
