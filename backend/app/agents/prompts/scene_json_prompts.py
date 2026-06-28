"""
Scene JSON Generator Prompts.
"""

from app.sandbox.shared_animation_registry import SUPPORTED_COMPONENTS, SUPPORTED_ANIMATIONS

from app.sandbox.shared_animation_registry import SUPPORTED_ANIMATIONS

def create_scene_json_system_prompt(allowed_components: list, suggested_component: str = None, stem_blueprint: dict = None) -> str:
    component_enforcement = f"You MUST strictly use EXACTLY this component: {suggested_component}. Do not hallucinate." if suggested_component else f"STRICT COMPONENT ALLOWLIST: You must use EXACTLY one of: {allowed_components}. Do NOT hallucinate components."
    
    blueprint_section = ""
    if stem_blueprint:
        blueprint_section = f"""
BLUEPRINT CONSTRAINTS:
You must align your Scene JSON perfectly with this validated blueprint:
- Component: {stem_blueprint.get('primary_component', '')}
- Visual Metaphor: {stem_blueprint.get('visual_metaphor', '')}
- Required Visual Elements (Ensure these exist in component_data):
"""
        for ve in stem_blueprint.get("required_visual_elements", []):
            blueprint_section += f"  * {ve.get('name')} ({ve.get('element_type')}): {ve.get('description')}\n"
    
    return f"""You are a Visual Metaphor Agent for an educational video pipeline.
Your job is to take a Storyboard Scene and convert it into a strictly structured Semantic Scene Specification (JSON).

Requirements:
- You DO NOT generate raw coordinates or Manim geometry classes (e.g., Circle, Line).
- Instead, you select from a pre-defined Visual Component Library and define the educational intent.
- Extract 'title' and 'caption' from the storyboard if text should be displayed on screen.
- {component_enforcement}{blueprint_section}
- CAMERA CONTROL: You MUST include a strict 'focal_bounding_box' coordinate array of format [center_x, center_y, width, height] inside your output schema for every visual beat (e.g., [0.0, 0.0, 14.0, 8.0] for the default wide view). The camera will use this to smoothly pan and zoom to follow active elements.
- MACRO-TO-MICRO PRINCIPLE: Emphasize understanding by showing macro-to-micro relationships.
- CAUSE-AND-EFFECT VECTORS: Use vectors to show why things move.
- ACTIVE VARIABLE MORPHING: When equations update, use `ReplacementTransform` or `TransformMatchingTex` conceptually instead of deleting and recreating equations.
- STRICT DATA STRUCTURES RULE: DO NOT use 'TreeDiagram'. It has been deprecated. If mapping a chained or loop structure like a Linked List or Circular Linked List, you MUST use 'NetworkDiagram' and define the links using layer structures. For hierarchical data, use 'HierarchyDiagram'.
- STRICT ANIMATION ALLOWLIST: You must use ONLY these specific component animation templates: ["intro", "highlight", "transform", "explain", "focus", "morph", "shift_camera"]. Do NOT use generic fade_in or uncreate.
- SEMANTIC MORPHING DIRECTIVES: When transitioning scenes, do not use hard cuts. You must output scene transitions using abstract relational actions like `transition_type`: "morph", "transform", or `camera_action`: "shift_camera", "zoom". - Define the `learning_goal` and `visual_metaphor` for the scene.
- Define `visual_intent` explaining what the visualization is trying to show.
- Use `component_data` to pass specific semantic data to the component.

RULE: component_data must always describe WHAT TO SHOW visually.
For concepts involving microscopic interactions, particle-based visualizations are preferred.
For components like NetworkDiagram:
  layers = list of lists of node names (ALWAYS 2D array)
  layer_labels = list of layer names

For sequence components like ArrayDiagram:
  elements = list of actual values to display

For physics or chemistry components like MoleculeDiagram, ForceVectorDiagram:
  Use semantic properties fitting the diagram, e.g. 'molecules', 'forces', 'system_type'.

- PRESERVE the duration from the storyboard.

Output your response as valid JSON with this exact format:
{{
    "scene_json": [
        {{
            "schema_version": "v2",
            "scene_type": "binary_search_tree",
            "learning_goal": "Understand BST ordering",
            "visual_metaphor": "A tree with the root branching into smaller left nodes and larger right nodes",
            "visual_intent": "show the root node and its left and right children in a hierarchy",
            "title": "Binary Search Tree",
            "caption": "Smaller values go left, larger go right",
            "focal_bounding_box": [0.0, 0.0, 14.0, 8.0],
            "components": [
                "{suggested_component or 'HierarchyDiagram'}"
            ],
            "component_data": {{
                "root_label": "50",
                "children_labels": ["30", "70"]
            }},
            "animation_sequence": [
                {{"action": "intro"}},
                {{"action": "highlight", "target": "root_node"}}
            ],
            "duration": 10
        }}
    ]
}}

CRITICAL: Return ONLY valid JSON, no additional text or markdown."""

def create_scene_json_prompt(storyboards: list, visualization_strategy: str = "generic_concept") -> str:
    s_str = ""
    for s in storyboards:
        s_str += f"\\nScene {s['scene_number']}\\nGoal: {s.get('goal', '')}\\nVisuals: {s['visuals']}\\nAnimations: {s['animations']}\\nDuration: {s.get('duration', 5)}\\n"
        
    return f"""Convert the following storyboards into structured Semantic Scene Specs.
VISUALIZATION STRATEGY: {visualization_strategy}

SCENE CONTINUITY & CHRONOLOGICAL PROGRESSION:
- As the storyboard audio shifts contexts, distinct visual beats MUST be triggered. Static assets must not overstay their welcome.
- You can change components dynamically across scenes or completely clear old assets and introduce new components. Do not keep static components on screen if the narration has moved on to a new concept.
- MAXIMUM SCENE DURATION CEILING: No scene visual state may remain static for more than 7 seconds of narration text. If a paragraph is long, you MUST break it into smaller sub-scenes (e.g. intro -> highlight -> transform) to maintain visual momentum.

{s_str}
Return ONLY valid JSON."""

# Legacy constant for backwards compatibility
from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY
SCENE_JSON_SYSTEM_PROMPT = create_scene_json_system_prompt(list(COMPONENT_REGISTRY.keys()))
