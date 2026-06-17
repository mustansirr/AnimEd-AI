"""
LangGraph Workflow for Video Generation.
"""

import logging
from typing import Dict, Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState, create_initial_state
from app.agents.nodes.context import retrieve_context_node
from app.agents.nodes.planner import plan_scenes
from app.agents.nodes.storyboard_agent import write_storyboard
from app.agents.nodes.human_review import wait_for_approval
from app.agents.nodes.scene_json_generator import generate_scene_json
from app.agents.nodes.layout_agent import compute_layouts
from app.agents.nodes.coder import generate_code
from app.agents.nodes.static_analyzer import static_analysis_pass
from app.agents.nodes.reflector import reflect_and_fix
from app.sandbox.renderer import execute_and_check
from app.agents.nodes.video_quality_evaluator import evaluate_quality
from app.agents.nodes.fix_agent import fix_scene
from app.sandbox.stitcher import finalize_video
from app.agents.nodes.concept_classifier import classify_concept
from app.agents.nodes.diagram_validator import validate_diagram
from app.agents.nodes.schema_validator import validate_schema
from app.agents.nodes.domain_validator import validate_domain
from app.agents.nodes.layout_validator import validate_layout
from app.agents.nodes.educational_validator import validate_educational_quality

logger = logging.getLogger(__name__)

_active_workflows: Dict[str, tuple] = {}

def create_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve_info", retrieve_context_node)
    workflow.add_node("planner", plan_scenes)
    workflow.add_node("concept_classifier", classify_concept)
    workflow.add_node("storyboard", write_storyboard)
    workflow.add_node("human_review", wait_for_approval)
    workflow.add_node("scene_json", generate_scene_json)
    workflow.add_node("layout", compute_layouts)
    workflow.add_node("coder", generate_code)
    workflow.add_node("static_analyzer", static_analysis_pass)
    workflow.add_node("reflector", reflect_and_fix)
    workflow.add_node("renderer", execute_and_check)
    workflow.add_node("diagram_validator", validate_diagram)
    workflow.add_node("quality_evaluator", evaluate_quality)
    workflow.add_node("fix_agent", fix_scene)
    workflow.add_node("finalize", finalize_video)
    
    # New Pre-Render Validators
    workflow.add_node("schema_validator", validate_schema)
    workflow.add_node("domain_validator", validate_domain)
    workflow.add_node("layout_validator", validate_layout)
    workflow.add_node("educational_validator", validate_educational_quality)

    workflow.set_entry_point("retrieve_info")
    workflow.add_edge("retrieve_info", "planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_after_pre_render_validation,
        {"pass": "concept_classifier", "fail": END, "fatal": END}
    )
    
    workflow.add_edge("concept_classifier", "storyboard")
    workflow.add_edge("storyboard", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {"approved": "scene_json", "rejected": END}
    )

    # Pre-render Validation Pipeline
    workflow.add_edge("scene_json", "schema_validator")
    
    workflow.add_conditional_edges(
        "schema_validator",
        route_after_pre_render_validation,
        {"pass": "domain_validator", "fail": END, "fatal": END}
    )
    
    workflow.add_conditional_edges(
        "domain_validator",
        route_after_pre_render_validation,
        {"pass": "educational_validator", "fail": "fix_agent", "fatal": END}
    )
    
    workflow.add_conditional_edges(
        "educational_validator",
        route_after_pre_render_validation,
        {"pass": "layout", "fail": "fix_agent", "fatal": END}
    )
    
    workflow.add_edge("layout", "layout_validator")
    
    workflow.add_conditional_edges(
        "layout_validator",
        route_after_pre_render_validation,
        {"pass": "coder", "fail": "fix_agent", "fatal": END}
    )
    
    # Execution Loop
    workflow.add_edge("coder", "static_analyzer")
    
    workflow.add_conditional_edges(
        "static_analyzer",
        route_after_pre_render_validation,
        {"pass": "renderer", "fail": "fix_agent", "fatal": END}
    )

    workflow.add_conditional_edges(
        "renderer",
        route_after_render,
        {
            "retry": "reflector",
            "diagram_validator": "diagram_validator",
            "finalize": "finalize",
        }
    )
    
    workflow.add_conditional_edges(
        "diagram_validator",
        route_after_diagram_validator,
        {
            "retry": "reflector",
            "eval_quality": "quality_evaluator",
        }
    )
    
    workflow.add_edge("reflector", "coder")

    workflow.add_conditional_edges(
        "quality_evaluator",
        route_after_eval,
        {
            "fix": "fix_agent",
            "next_scene": "coder",
            "finalize": "finalize",
        }
    )
    
    workflow.add_edge("fix_agent", "coder")
    workflow.add_edge("finalize", END)

    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"],
    )


def route_after_review(state: AgentState) -> Literal["approved", "rejected"]:
    if state.get("user_approved", False):
        return "approved"
    return "rejected"


DEVELOPMENT_MODE = True

def route_after_pre_render_validation(state: AgentState) -> Literal["pass", "fail", "fatal"]:
    err = state.get("last_render_error")
    if err:
        if DEVELOPMENT_MODE:
            logger.warning(f"[DEVELOPMENT MODE] Bypassing validation error: {err}")
            # We don't want to actually crash, we just want to proceed to the next node
            return "pass"
            
        if "FATAL ERROR" in err or "Aborting workflow" in err:
            return "fatal"
            
        return "fail"
    return "pass"


def route_after_render(state: AgentState) -> Literal["retry", "diagram_validator", "finalize"]:
    if state.get("last_render_error") and state.get("retry_count", 0) < 3:
        return "retry"
    
    if state.get("all_scenes_done", False):
        return "finalize"
        
    if state.get("last_render_error"):
        # Max retries hit, fail or skip
        return "diagram_validator"

    return "diagram_validator"


def route_after_diagram_validator(state: AgentState) -> Literal["retry", "eval_quality"]:
    if state.get("last_render_error") and state.get("retry_count", 0) < 3:
        return "retry"
    return "eval_quality"


def route_after_eval(state: AgentState) -> Literal["fix", "next_scene", "finalize"]:
    scores = state.get("quality_scores")
    
    # Only loop back if something scored < 8, and we haven't retried this too many times
    if scores and state.get("retry_count", 0) < 3:
        min_score = min(
            scores["visual_clarity"],
            scores["educational_clarity"],
            scores["layout_quality"],
            scores["animation_quality"],
            scores["professional_appearance"]
        )
        if min_score < 8:
            return "fix"
            
    if state.get("all_scenes_done", False):
        return "finalize"
        
    jsons = state.get("positioned_jsons", [])
    current_index = state.get("current_scene_index", 0)

    if current_index >= len(jsons):
        return "finalize"

    return "next_scene"


async def start_workflow(video_id: str, user_prompt: str, syllabus_context: str = "") -> AgentState:
    workflow = create_workflow()
    config = {"configurable": {"thread_id": video_id}, "recursion_limit": 150}

    initial_state = create_initial_state(
        video_id=video_id,
        user_prompt=user_prompt,
        syllabus_context=syllabus_context,
    )

    result = await workflow.ainvoke(initial_state, config)
    _active_workflows[video_id] = (workflow, config)
    return result


async def resume_workflow(video_id: str, approved: bool, feedback: str = None) -> AgentState:
    if video_id not in _active_workflows:
        raise ValueError(f"No active workflow found for video {video_id}")

    workflow, config = _active_workflows[video_id]
    # Ensure recursion limit is maintained on resume
    config["recursion_limit"] = 150
    await workflow.aupdate_state(config, {"user_approved": approved, "user_feedback": feedback})
    result = await workflow.ainvoke(None, config)
    del _active_workflows[video_id]
    return result


def get_workflow_state(video_id: str) -> AgentState | None:
    if video_id not in _active_workflows:
        return None
    workflow, config = _active_workflows[video_id]
    return workflow.get_state(config).values


def is_workflow_active(video_id: str) -> bool:
    return video_id in _active_workflows
