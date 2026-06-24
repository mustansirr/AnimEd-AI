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
        # Assuming components.py is in backend/app/sandbox/components.py
        comp_path = Path(__file__).parent.parent.parent / "sandbox" / "components.py"
        with open(comp_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load components.py: {e}")
        return ""

MANIM_PREAMBLE = """
class EducationalBackground(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grid = NumberPlane(
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 1,
                "stroke_opacity": 0.0
            }
        )
        grid.axes.set_opacity(0.0)
        self.add(grid)
"""

from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY, COMPONENT_ALIASES

def generate_animation_code(anim_name: str, comp_var: str) -> str:
    """Map semantic animation intent to deterministic Manim code."""
    
    def safe_anim(method_name, fallback_anim):
        return (f"try:\n"
                f"            anim = {comp_var}.{method_name}()\n"
                f"            self.play(*anim) if isinstance(anim, (list, tuple)) else self.play(anim)\n"
                f"        except AttributeError:\n"
                f"            self.play({fallback_anim}({comp_var}))")

    # Component-driven animation templates
    if anim_name in ["intro", "show_diagram", "fade_in_array", "fade_in_flowchart", "fade_in_summary_diagram", "grow_tree", "draw_axes"]:
        return safe_anim("get_intro_animations", "FadeIn")
    elif anim_name in ["highlight", "highlight_node", "highlight_element", "highlight_step", "highlight_key_takeaways", "show_prediction"]:
        return safe_anim("get_highlight_animations", "Indicate")
    elif anim_name in ["transform", "morph", "animate_flow", "binary_search_step", "gradient_descent_step"]:
        return (f"old_comp = {comp_var}.copy()\n"
                f"        try:\n"
                f"            anim = {comp_var}.get_transformation_animations()\n"
                f"            self.play(*anim) if isinstance(anim, (list, tuple)) else self.play(anim)\n"
                f"        except AttributeError:\n"
                f"            self.play(GlobalTransitionEngine.transition_between_states(old_comp, {comp_var}))")
    elif anim_name == "explain":
        return safe_anim("get_explanation_animations", "Indicate")
    elif anim_name == "focus":
        return safe_anim("get_focus_animations", "Circumscribe")
    elif anim_name == "shift_camera":
        return (f"target_coordinates = {comp_var}.get_center()\n"
                f"        target_width = {comp_var}.width + 2.0\n"
                f"        self.play(\n"
                f"            self.camera.frame.animate.move_to(target_coordinates).set(width=target_width),\n"
                f"            run_time=1.5\n"
                f"        )")
        
    # Fallbacks for specific legacy edge cases
    mapping = {
        "show_points": f"self.play(FadeIn(getattr({comp_var}, 'points', {comp_var})))",
        "fit_line": f"self.play(Create(getattr({comp_var}, 'line', {comp_var})))",
        "fade_in_title": f"pass # Handled by default FadeIn",
    }
    if anim_name not in mapping:
        logger.warning(f"Unsupported animation '{anim_name}' requested. Falling back to intro.")
        return safe_anim("get_intro_animations", "FadeIn")
    return mapping[anim_name]

def build_deterministic_scene(scene_spec: dict, prev_scene_spec: dict = None) -> str:
    components_lib = get_components_lib()
    
    # Explicit naming alias intercept
    comp_names = scene_spec.get("components", [])
    if comp_names:
        legacy_alias_map = {
            "TreeDiagram": "HierarchyDiagram",
            "LinkedListDiagram": "NetworkDiagram"
        }
        scene_spec["components"] = [legacy_alias_map.get(c, c) for c in comp_names]
        
    learning_goal = scene_spec.get("learning_goal", "")
    from app.sandbox.stem_blueprint_dataset import STEM_BLUEPRINT_REGISTRY
    blueprint = STEM_BLUEPRINT_REGISTRY.require_blueprint(learning_goal)
    comp_data = scene_spec.get("component_data", {})
    if comp_data is None:
        comp_data = {}
        
    comp_names = scene_spec.get("components", [])
    
    # Check if the scene JSON explicitly requested an ImageLabelCard override
    if comp_names and comp_names[0] == "ImageLabelCard":
        comp_name = "ImageLabelCard"
    elif blueprint:
        comp_name = blueprint.primary_component
        logger.info(f"STRICT REGISTRY BINDING: Mapped '{learning_goal}' to {comp_name}")
        # Enforce required visual elements in component_data
        for ve in blueprint.required_visual_elements:
            if ve.is_required and ve.name not in comp_data:
                comp_data[ve.name] = ve.description
    else:
        comp_name = comp_names[0] if comp_names else "SummaryDiagram"
        logger.warning(f"No strict blueprint found for '{learning_goal}', falling back to {comp_name}")
        
    # Explicit mapping for Inertia per guidelines
    if "inertia" in learning_goal.lower() or "mass" in learning_goal.lower():
        comp_name = "ForceVectorDiagram"
        
    code = [
        "from manim import *",
        MANIM_PREAMBLE,
        components_lib,
        "",
        "class Scene1(MovingCameraScene):",
        "    def construct(self):",
        "        self.add(EducationalBackground())",
        "        title_card = None",
        "        explanation_card = None",
        "        main_comp = VGroup()",
        ""
    ]
    
    # Initial camera framing based on focal_bounding_box
    focal_box = scene_spec.get("focal_bounding_box", [0.0, 0.0, 14.0, 8.0])
    if focal_box and len(focal_box) == 4:
        cx, cy, w, h = focal_box
        code.append(f"        self.camera.frame.move_to(np.array([{cx}, {cy}, 0.0]))")
        code.append(f"        self.camera.frame.set(width={w})")
        
    layout = scene_spec.get("layout_zones", {})
    if layout.get("title") == "TitleZone":
        code.append(f"        title_card = TitleCard({repr(scene_spec.get('title'))}, {repr(scene_spec.get('caption'))})")
        
    from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY, COMPONENT_ALIASES
    comp_name = COMPONENT_ALIASES.get(comp_name, comp_name)
    
    if comp_name in COMPONENT_REGISTRY:
        impl_class_name = COMPONENT_REGISTRY[comp_name]
        
        # Pass learning_goal to all components as a fallback
        if "learning_goal" not in comp_data:
            comp_data["learning_goal"] = scene_spec.get("learning_goal", "Understand the concept")
            
        animations = scene_spec.get("animation_sequence", [])
        if not animations:
            animations = ["show_diagram"]
            
        is_transform = any(anim in ["transform", "morph"] for anim in animations)
        
        if is_transform:
            # Create start component with initial parameters
            start_data = comp_data.copy()
            if "show_squares" in start_data:
                start_data["show_squares"] = False
            start_kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in start_data.items())
            
            # Create target component with target parameters
            target_data = comp_data.copy()
            if "show_squares" in target_data:
                target_data["show_squares"] = True
            target_kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in target_data.items())
            
            code.append(f"        main_comp = {impl_class_name}({start_kwargs_str})")
            code.append(f"        main_comp_target = {impl_class_name}({target_kwargs_str})")
        else:
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in comp_data.items())
            code.append(f"        main_comp = {impl_class_name}({kwargs_str})")
            
    else:
        raise ValueError(f"Unsupported component: '{comp_name}'. Must be one of {list(COMPONENT_REGISTRY.keys())}")
        
    code.append("        zones = LayoutZones.arrange_zones(title_zone=title_card, visualization_zone=main_comp)")
    
    if prev_scene_spec:
        prev_comp_names = prev_scene_spec.get("components", [])
        prev_comp_name = prev_comp_names[0] if prev_comp_names else "SummaryDiagram"
        prev_comp_name = COMPONENT_ALIASES.get(prev_comp_name, prev_comp_name)
        if prev_comp_name in COMPONENT_REGISTRY:
            prev_impl_class_name = COMPONENT_REGISTRY[prev_comp_name]
            prev_comp_data = prev_scene_spec.get("component_data", {})
            if prev_comp_data is None: prev_comp_data = {}
            if "learning_goal" not in prev_comp_data:
                prev_comp_data["learning_goal"] = prev_scene_spec.get("learning_goal", "Understand the concept")
            prev_kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in prev_comp_data.items())
            code.append(f"        prev_comp = {prev_impl_class_name}({prev_kwargs_str})")
            code.append("        LayoutZones.arrange_zones(visualization_zone=prev_comp)")
            code.append("        self.add(prev_comp)")
    
    total_duration = max(5, scene_spec.get('duration', 5))
    # Distribute wait time across animations
    wait_per_anim = max(1.0, total_duration / max(1, len(animations)))
    
    code.append("        if title_card: self.play(FadeIn(title_card))")
    
    revealing_anims = {"show_diagram", "fade_in_array", "fade_in_flowchart", "fade_in_summary_diagram", "grow_tree", "draw_axes"}
    if prev_scene_spec:
        code.append("        self.play(ReplacementTransform(prev_comp, main_comp, run_time=1.5))")
    elif animations and animations[0] not in revealing_anims:
        code.append("        self.play(FadeIn(main_comp))")
        
    estimated_anim_time = 0
    for anim in animations:
        if anim in ["transform", "morph"]:
            code.append("        try:")
            code.append("            self.play(*main_comp.get_transformation_animations(), run_time=1.5)")
            code.append("        except AttributeError:")
            code.append("            if hasattr(main_comp, 'is_math_component') and main_comp.is_math_component:")
            code.append("                self.play(TransformMatchingTex(main_comp, main_comp_target, run_time=1.5))")
            code.append("            else:")
            code.append("                self.play(ReplacementTransform(main_comp, main_comp_target, run_time=1.5))")
            code.append("        main_comp = main_comp_target")
            estimated_anim_time += 1.5
        elif anim == "shift_camera":
            focal_box = scene_spec.get('focal_bounding_box')
            if focal_box and len(focal_box) == 4:
                cx, cy, w, h = focal_box
                code.append("        self.play(")
                code.append(f"            self.camera.frame.animate.move_to(np.array([{cx}, {cy}, 0.0])).set(width={w}),")
                code.append("            run_time=1.5")
                code.append("        )")
            else:
                code.append("        target_coordinates = main_comp.get_center()")
                code.append("        target_width = main_comp.width + 2.0")
                code.append("        self.play(")
                code.append("            self.camera.frame.animate.move_to(target_coordinates).set(width=target_width),")
                code.append("            run_time=1.5")
                code.append("        )")
            estimated_anim_time += 1.5
        else:
            anim_code = generate_animation_code(anim, "main_comp")
            code.append(f"        {anim_code}")
            estimated_anim_time += 1.5
            
    # Animation-to-Audio Time Sync
    remaining_time = max(0.5, total_duration - estimated_anim_time)
    code.append(f"        # Synchronize visual hold with audio duration")
    code.append(f"        self.wait({remaining_time})")
    
    code.append("        self.clear()")
    
    final_code = "\n".join(code)
    logger.info(f"Generated code: \n{final_code}")
    return final_code


async def generate_code(state: AgentState) -> dict:
    logger.info("--- ENTERING CODER NODE ---")
    video_id = state["video_id"]
    scene_index = state["current_scene_index"]
    positioned_jsons = state.get("positioned_jsons", [])
    
    stem_blueprint = state.get("stem_blueprint")
    if stem_blueprint:
        logger.info(f"\n--- Blueprint Propagation Log ---")
        logger.info(f"Node: Coder")
        logger.info(f"Enforcing Component: {stem_blueprint.get('primary_component')}")
        logger.info(f"---------------------------------\n")

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
    prev_scene_spec = positioned_jsons[scene_index - 1] if scene_index > 0 else None
    
    logger.info(f"Deterministically building code for scene {scene_index + 1}/{len(positioned_jsons)}")

    try:
        code = build_deterministic_scene(scene_spec, prev_scene_spec)
        
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
