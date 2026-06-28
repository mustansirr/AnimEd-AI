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

MANIM_PREAMBLE = """
class EducationalBackground(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grid = NumberPlane(
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 1,
                "stroke_opacity": 0.2
            }
        )
        self.add(grid)
"""

from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY, COMPONENT_ALIASES

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
        return (f"anim_method = getattr({comp_var}, '{method_name}', None)\n"
                f"        if callable(anim_method): self.play(*anim_method())\n"
                f"        else: self.play({fallback_anim}({comp_var}))")

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
        "        self.camera.background_color = '#0F172A'",

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
        
    comp_names = scene_spec.get("components", [])
    if comp_names:
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
        
        if comp_name == "GraphPlot":
            code.append(f"        main_comp = GraphPlot({kwargs_str})")
        elif comp_name == "FlowChart":
            code.append(f"        main_comp = FlowChart({kwargs_str})")
        elif comp_name == "HierarchyDiagram":
            code.append(f"        main_comp = HierarchyDiagram({kwargs_str})")
        elif comp_name == "NetworkDiagram":
            code.append(f"        main_comp = NetworkDiagram({kwargs_str})")
        elif comp_name == "TimelineDiagram":
            code.append(f"        main_comp = TimelineDiagram({kwargs_str})")
        elif comp_name == "ArrayDiagram":
            code.append(f"        main_comp = ArrayDiagram({kwargs_str})")
        elif comp_name == "SummaryDiagram":
            code.append(f"        main_comp = SummaryDiagram({kwargs_str})")
        elif comp_name == "NumberLineDiagram":
            code.append(f"        main_comp = NumberLineDiagram({kwargs_str})")
        elif comp_name == "FunctionPlot":
            code.append(f"        main_comp = FunctionPlot({kwargs_str})")
        elif comp_name == "VectorArrow":
            code.append(f"        main_comp = VectorArrow({kwargs_str})")
        elif comp_name == "MatrixDisplay":
            code.append(f"        main_comp = MatrixDisplay({kwargs_str})")
        elif comp_name == "GeometryDiagram":
            code.append(f"        main_comp = GeometryDiagram({kwargs_str})")
        elif comp_name == "BarChartDiagram":
            code.append(f"        main_comp = BarChartDiagram({kwargs_str})")
        elif comp_name == "BinarySearchDiagram":
            code.append(f"        main_comp = BinarySearchDiagram({kwargs_str})")
        elif comp_name == "GradientDescentPlot":
            code.append(f"        main_comp = GradientDescentPlot({kwargs_str})")
        elif comp_name == "SurfaceTensionDiagram":
            code.append(f"        main_comp = SurfaceTensionDiagram({kwargs_str})")
        elif comp_name == "NeuralNetworkDiagram":
            code.append(f"        main_comp = NeuralNetworkDiagram({kwargs_str})")
        else:
            raise ValueError(f"Unsupported component: '{comp_name}'. Must be one of {list(SUPPORTED_COMPONENTS)}")
            
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
    if animations and animations[0] not in revealing_anims:
        code.append("        self.play(FadeIn(main_comp))")
        
    estimated_anim_time = 0
    for anim in animations:
        anim_code = generate_animation_code(anim, "main_comp")
        code.append(f"        {anim_code}")
        code.append(f"        self.wait({wait_per_anim})")
        
    code.append("        self.play(FadeOut(zones))")
    
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
