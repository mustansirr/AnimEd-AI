"""
Tests for the LangGraph agent workflow.

Tests cover:
- AgentState TypedDict structure
- Workflow creation
- Prompt generation functions
- Node functions with mocked LLM
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.state import (
    AgentState,
    SceneScript,
    ScenePlan,
    create_initial_state,
)
from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    create_planner_prompt,
)
from app.agents.prompts.scripter_prompts import (
    SCRIPTER_SYSTEM_PROMPT,
    create_scripter_prompt,
)


class TestAgentState:
    """Tests for AgentState TypedDict and helpers."""

    def test_create_initial_state(self):
        """Test initial state creation with required fields."""
        state = create_initial_state(
            video_id="test-video-123",
            user_prompt="Explain photosynthesis",
            syllabus_context="Biology curriculum context",
        )

        assert state["video_id"] == "test-video-123"
        assert state["user_prompt"] == "Explain photosynthesis"
        assert state["syllabus_context"] == "Biology curriculum context"
        assert state["user_approved"] is False
        assert state["scripts"] == []
        assert state["scene_plans"] == []
        assert state["retry_count"] == 0

    def test_create_initial_state_defaults(self):
        """Test initial state with default syllabus context."""
        state = create_initial_state(
            video_id="test-id",
            user_prompt="Test prompt",
        )

        assert state["syllabus_context"] == ""
        assert state["video_title"] == ""
        assert state["topic_breakdown"] == []

    def test_scene_script_structure(self):
        """Test SceneScript TypedDict structure."""
        script: SceneScript = {
            "scene_order": 1,
            "narration": "Welcome to the video",
            "visual_description": "Show title text",
            "duration_estimate": 60,
        }

        assert script["scene_order"] == 1
        assert "narration" in script
        assert "visual_description" in script

    def test_scene_plan_structure(self):
        """Test ScenePlan TypedDict structure."""
        plan: ScenePlan = {
            "scene_number": 1,
            "title": "Introduction",
            "key_concepts": ["concept1", "concept2"],
            "visual_type": "text_animation",
            "duration_seconds": 60,
        }

        assert plan["scene_number"] == 1
        assert len(plan["key_concepts"]) == 2


class TestPlannerPrompts:
    """Tests for planner prompt generation."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined and non-empty."""
        assert PLANNER_SYSTEM_PROMPT
        assert len(PLANNER_SYSTEM_PROMPT) > 100
        assert "JSON" in PLANNER_SYSTEM_PROMPT

    def test_create_planner_prompt_basic(self):
        """Test basic planner prompt creation."""
        prompt = create_planner_prompt(
            user_prompt="Explain matrix multiplication",
        )

        assert "Explain matrix multiplication" in prompt
        assert "JSON" in prompt

    def test_create_planner_prompt_with_context(self):
        """Test planner prompt with syllabus context."""
        prompt = create_planner_prompt(
            user_prompt="Explain derivatives",
            syllabus_context="Calculus I: Limits and Derivatives",
        )

        assert "Explain derivatives" in prompt
        assert "Calculus I" in prompt
        assert "Syllabus Context" in prompt


class TestScripterPrompts:
    """Tests for scripter prompt generation."""

    def test_scripter_system_prompt_exists(self):
        """Test that scripter system prompt is defined."""
        assert SCRIPTER_SYSTEM_PROMPT
        assert len(SCRIPTER_SYSTEM_PROMPT) > 100
        assert "narration" in SCRIPTER_SYSTEM_PROMPT.lower()

    def test_create_scripter_prompt(self):
        """Test scripter prompt creation."""
        scene_plan = {
            "scene_number": 1,
            "title": "Introduction to Vectors",
            "key_concepts": ["magnitude", "direction"],
            "visual_type": "diagram",
            "duration_seconds": 45,
        }

        prompt = create_scripter_prompt(
            scene_plan=scene_plan,
            scene_index=0,
            video_title="Understanding Vectors",
        )

        assert "Understanding Vectors" in prompt
        assert "Introduction to Vectors" in prompt
        assert "magnitude" in prompt
        assert "45" in prompt


class TestWorkflow:
    """Tests for workflow creation and structure."""

    def test_workflow_imports(self):
        """Test that workflow module can be imported."""
        from app.agents.workflow import (
            create_workflow,
            is_workflow_active,
        )
        assert create_workflow is not None
        assert is_workflow_active is not None

    def test_workflow_active_check(self):
        """Test is_workflow_active returns False for unknown IDs."""
        from app.agents.workflow import is_workflow_active

        assert is_workflow_active("nonexistent-id") is False

    def test_create_workflow_returns_compiled_graph(self):
        """Test that create_workflow returns a compiled graph."""
        from app.agents.workflow import create_workflow

        workflow = create_workflow()

        # Check it has the necessary attributes of a compiled graph
        assert workflow is not None
        assert hasattr(workflow, "ainvoke")


class TestAgentNodes:
    """Tests for individual agent nodes with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_context_node_with_existing_context(self):
        """Test context node skips retrieval when context exists."""
        from app.agents.nodes.context import retrieve_context_node

        state: AgentState = create_initial_state(
            video_id="test-123",
            user_prompt="Test prompt",
            syllabus_context="Existing context",
        )

        result = await retrieve_context_node(state)

        # Should return empty dict, not overwrite existing context
        assert result == {}

    @pytest.mark.asyncio
    async def test_context_node_handles_rag_failure(self):
        """Test context node gracefully handles RAG failures."""
        from app.agents.nodes.context import retrieve_context_node

        state: AgentState = create_initial_state(
            video_id="test-123",
            user_prompt="Test prompt",
        )

        # Mock RAG service to raise exception
        with patch(
            "app.agents.nodes.context.retrieve_context",
            new_callable=AsyncMock,
            side_effect=Exception("RAG failed"),
        ):
            result = await retrieve_context_node(state)

        # Should return empty context, not raise
        assert result == {"syllabus_context": ""}

    @pytest.mark.asyncio
    async def test_human_review_approved(self):
        """Test human review node with approval."""
        from app.agents.nodes.human_review import wait_for_approval

        state: AgentState = create_initial_state(
            video_id="550e8400-e29b-41d4-a716-446655440000",
            user_prompt="Test prompt",
        )
        state["user_approved"] = True
        state["scripts"] = [{"scene_order": 1}]  # type: ignore

        with patch(
            "app.agents.nodes.human_review.update_video_status",
            new_callable=AsyncMock,
        ):
            result = await wait_for_approval(state)

        assert result["current_scene_index"] == 0
        assert result["generated_codes"] == []
        assert result["all_scenes_done"] is False

    @pytest.mark.asyncio
    async def test_human_review_rejected(self):
        """Test human review node with rejection."""
        from app.agents.nodes.human_review import wait_for_approval

        state: AgentState = create_initial_state(
            video_id="550e8400-e29b-41d4-a716-446655440000",
            user_prompt="Test prompt",
        )
        state["user_approved"] = False
        state["user_feedback"] = "Please add more examples"

        with patch(
            "app.agents.nodes.human_review.update_video_status",
            new_callable=AsyncMock,
        ):
            result = await wait_for_approval(state)

        assert result["all_scenes_done"] is True  # Stop processing
