"""
Manim Generator Agent Node (formerly Coder).
Generates Manim code deterministically from Semantic Scene Specs.
"""

import asyncio
import logging
from pathlib import Path
from uuid import UUID

from app.agents.state import AgentState
from app.models.schemas import VideoStatus
from app.services.supabase_client import (
    get_scene_id_by_order,
    update_scene_code,
    update_video_status,
)
from app.config import get_settings

logger = logging.getLogger(__name__)

# Load our Visual Component Library
def get_components_lib() -> str:
    try:
        blueprints_path = Path(__file__).parent.parent.parent / "sandbox" / "blueprints.py"
        comp_path = Path(__file__).parent.parent.parent / "sandbox" / "components.py"
        
        with open(blueprints_path, "r", encoding="utf-8") as f:
            blueprints = f.read()
        with open(comp_path, "r", encoding="utf-8") as f:
            components = f.read()
            
        components = components.replace("from blueprints import STEM_BLUEPRINTS", "")
        return blueprints + "\n\n" + components
    except Exception as e:
        logger.error(f"Failed to load components.py: {e}")
        return ""

MANIM_PREAMBLE = ""

from app.sandbox.shared_animation_registry import SUPPORTED_COMPONENTS

def generate_animation_code(anim_info, comp_var: str, comp_name: str = "") -> str:
    """Map semantic animation intent to deterministic Manim code."""
    
    if isinstance(anim_info, dict):
        anim_name = anim_info.get("action", "intro")
        target = anim_info.get("target", None)
    else:
        anim_name = str(anim_info)
        target = None
        
    # Intelligent Fallbacks based on component capabilities
    intelligent_fallbacks = {
        "BinarySearchDiagram": {
            "split_dictionary": "highlight",
            "compare": "highlight",
            "move_pointers": "transform",
            "highlight_middle": "highlight",
            "split_array": "transform",
            "binary_search_step": "transform"
        },
        "GraphDiagram": {
            "bfs_step": "highlight",
            "dfs_step": "highlight",
            "traverse": "highlight",
            "visit_node": "highlight"
        },
        "TreeDiagram": {
            "traverse": "highlight",
            "search": "highlight"
        },
        "GeometryDiagram": {
            "draw_triangle": "intro",
            "show_squares": "intro",
            "prove_theorem": "explain"
        }
    }
    
    # Check if the animation is explicitly mapped for this component
    if comp_name in intelligent_fallbacks and anim_name in intelligent_fallbacks[comp_name]:
        fallback = intelligent_fallbacks[comp_name][anim_name]
        logger.warning(f"Animation '{anim_name}' unsupported by {comp_name}. Using fallback '{fallback}'.")
        anim_name = fallback
        
    def safe_anim(method_name, fallback_anim):
        if target:
            return (f"anim_method = getattr({comp_var}, '{method_name}', None)\n"
                    f"        if callable(anim_method):\n"
                    f"            try: self.play(*anim_method(target={repr(target)}))\n"
                    f"            except TypeError: self.play(*anim_method())\n"
                    f"        else: self.play({fallback_anim}({comp_var}))")
        else:
            return (f"anim_method = getattr({comp_var}, '{method_name}', None)\n"
                    f"        if callable(anim_method): self.play(*anim_method())\n"
                    f"        else: self.play({fallback_anim}({comp_var}))")

    # Component-driven animation templates
    if anim_name in ["intro", "show_diagram", "fade_in_array", "fade_in_flowchart", "fade_in_summary_diagram", "grow_tree", "draw_axes"]:
        return safe_anim("get_intro_animations", "FadeIn")
    elif anim_name in ["highlight", "highlight_node", "highlight_element", "highlight_step", "highlight_key_takeaways", "show_prediction"]:
        return safe_anim("get_highlight_animations", "Indicate")
    elif anim_name in ["transform", "animate_flow", "binary_search_step", "gradient_descent_step"]:
        return safe_anim("get_transformation_animations", "Wiggle")
    elif anim_name == "explain":
        return safe_anim("get_explanation_animations", "Indicate")
    elif anim_name == "focus":
        return safe_anim("get_focus_animations", "Circumscribe")
        
    # Fallbacks for specific legacy edge cases
    mapping = {
        "show_points": f"self.play(FadeIn(getattr({comp_var}, 'data_points', {comp_var})))",
        "fit_line": f"self.play(Create(getattr({comp_var}, 'line', {comp_var})))",
        "fade_in_title": f"pass # Handled by default FadeIn",
    }
    if anim_name not in mapping:
        fallback = "highlight" if target else "intro"
        logger.warning(f"Unsupported animation '{anim_name}' requested. Falling back to {fallback}.")
        if fallback == "highlight":
            return safe_anim("get_highlight_animations", "Indicate")
        return safe_anim("get_intro_animations", "FadeIn")
    return mapping[anim_name]

def build_deterministic_scene(scene_spec: dict) -> str:
    components_lib = get_components_lib()
    
    code = [
        "from manim import *",
        MANIM_PREAMBLE,
        components_lib,
        "",
        "class Scene1(Scene):",
        "    def construct(self):",
        "        self.camera.background_color = '#0F172A'",

        "        title_card = None",
        "        explanation_card = None",
        "        main_comp = VGroup()",
        ""
    ]
    
    layout = scene_spec.get("layout_zones", {})
    if layout.get("title") == "TitleZone":
        code.append(f"        title_card = TitleCard({repr(scene_spec.get('title'))}, {repr(scene_spec.get('caption'))})")
        
    comp_names = scene_spec.get("components", [])
    comp_name_val = ""
    if comp_names:
        comp_name_val = comp_names[0]
        comp_name = comp_names[0]
        comp_data = scene_spec.get("component_data", {})
        visual_intent = scene_spec.get("visual_intent", "")
        # Provide a default empty dict if None
        if comp_data is None:
            comp_data = {}
            
        logger.info(f"Coder Instantiating Component: {comp_name} with data: {comp_data}")
        
        # END-TO-END VERIFICATION LOG
        logger.info(f"Coder Component: {comp_name}")
        
        # Pass learning_goal to all components as a fallback
        if "learning_goal" not in comp_data:
            comp_data["learning_goal"] = scene_spec.get("learning_goal", "Understand the concept")
            
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in comp_data.items())
        
        # Dynamic dispatch: validate component and generate instantiation line.
        # Every component in SUPPORTED_COMPONENTS is defined in components.py
        # (which is embedded above), so a simple f-string is safe and correct.
        if comp_name not in SUPPORTED_COMPONENTS:
            raise ValueError(
                f"Unsupported component: '{comp_name}'. "
                f"Must be one of {sorted(SUPPORTED_COMPONENTS)}"
            )
        code.append(f"        main_comp = {comp_name}({kwargs_str})")
            
    code.append("        zones = LayoutZones.arrange_zones(title_zone=title_card, visualization_zone=main_comp)")
    
    animations = scene_spec.get("animation_sequence", [])
    if not animations:
        animations = ["show_diagram"]
        
    total_duration = max(5, scene_spec.get('duration', 5))
    # Distribute wait time across animations
    wait_per_anim = max(1.0, total_duration / max(1, len(animations)))
    
    code.append("        if title_card: self.play(FadeIn(title_card))")
    
    first_anim = animations[0] if animations else None
    first_anim_name = first_anim.get("action", "intro") if isinstance(first_anim, dict) else str(first_anim)
    
    revealing_anims = {"intro", "show_diagram", "fade_in_array", "fade_in_flowchart", "fade_in_summary_diagram", "grow_tree", "draw_axes"}
    if animations and first_anim_name not in revealing_anims:
        code.append("        self.play(FadeIn(main_comp))")
    
    for anim in animations:
        anim_code = generate_animation_code(anim, "main_comp", comp_name_val)
        code.append(f"        {anim_code}")
        code.append(f"        self.wait({wait_per_anim})")
        
    final_code = "\n".join(code)
    logger.info(f"Generated code: \n{final_code}")
    return final_code

async def generate_code(state: AgentState) -> dict:
    logger.info("--- ENTERING CODER NODE ---")
    video_id = state["video_id"]
    scene_index = state["current_scene_index"]
    positioned_jsons = state.get("positioned_jsons", [])

    # Diagnostic Log: Before Coder
    logger.info(f"[DIAGNOSTIC] Before Coder - number of positioned_jsons received: {len(positioned_jsons)}")

    if not positioned_jsons:
        error_msg = f"[DIAGNOSTIC] FATAL ERROR: positioned_jsons is empty in coder for video {video_id}. Workflow should not have routed to coder!"
        logger.error(error_msg)
        # Fail the workflow immediately by setting last_render_error
        # so route_after_pre_render_validation catches it.
        logger.info("--- EXITING CODER NODE (ERROR) ---")
        return {"last_render_error": error_msg}

    if scene_index >= len(positioned_jsons):
        logger.info(f"All scenes generated for video {video_id}")
        await update_video_status(UUID(video_id), VideoStatus.RENDERING)
        return {"all_scenes_done": True}

    scene_spec = positioned_jsons[scene_index]
    logger.info(f"Deterministically building code for scene {scene_index + 1}/{len(positioned_jsons)}")

    try:
        code = build_deterministic_scene(scene_spec)
        
        # Use storyboards to get scene order if available, else index + 1
        scene_order = scene_index + 1
        if state.get("storyboards") and len(state["storyboards"]) > scene_index:
            scene_order = state["storyboards"][scene_index].get("scene_number", scene_index + 1)
            
        scene_id = await get_scene_id_by_order(UUID(video_id), scene_order)

        if scene_id:
            await update_scene_code(scene_id, code)

        generated_codes = state.get("generated_codes", []).copy()
        generated_codes.append(code)

        logger.info("--- EXITING CODER NODE ---")
        return {
            "generated_codes": generated_codes,
            "current_scene_index": scene_index + 1,
            "last_render_error": None,
        }

    except Exception as e:
        logger.error(f"Failed to build deterministic scene: {e}")
        logger.info("--- EXITING CODER NODE (ERROR) ---")
        raise e
