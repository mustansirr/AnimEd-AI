"""
Scene JSON Generator Prompts.
"""

from app.sandbox.shared_animation_registry import SUPPORTED_COMPONENTS, SUPPORTED_ANIMATIONS

from app.sandbox.shared_animation_registry import SUPPORTED_ANIMATIONS

def create_scene_json_system_prompt(allowed_components: list, suggested_component: str = None) -> str:
    component_enforcement = f"You MUST strictly use EXACTLY this component: {suggested_component}. Do not hallucinate." if suggested_component else f"STRICT COMPONENT ALLOWLIST: You must use EXACTLY one of: {allowed_components}. Do NOT hallucinate components."
    
    return f"""You are a Visual Metaphor Agent for an educational video pipeline.
Your job is to take a Storyboard Scene and convert it into a strictly structured Semantic Scene Specification (JSON).

Requirements:
- You DO NOT generate raw coordinates or Manim geometry classes (e.g., Circle, Line).
- Instead, you select from a pre-defined Visual Component Library and define the educational intent.
- Extract 'title' and 'caption' from the storyboard if text should be displayed on screen.
- {component_enforcement}
- STRICT ANIMATION ALLOWLIST: You must use ONLY these specific component animation templates: ["intro", "highlight", "transform", "explain", "focus"]. Do NOT use generic fade_in or uncreate.
- Define the `learning_goal` and `visual_metaphor` for the scene.
- Define `visual_intent` explaining what the visualization is trying to show.
- Use `component_data` to pass specific semantic data to the component.

RULE: component_data must always describe WHAT TO SHOW visually.
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
            "components": [
                "{suggested_component or 'TreeDiagram'}"
            ],
            "component_data": {{
                "root_label": "50",
                "children_labels": ["30", "70"]
            }},
            "animation_sequence": [
                "intro",
                "highlight"
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

SCENE CONTINUITY: 
- When transitioning between scenes, maintain visual continuity by reusing the same components (e.g., keeping an ArrayDiagram if the next scene continues explaining the array). 
- To show progression, modify `component_data` rather than switching components unnecessarily.

{s_str}
Return ONLY valid JSON."""

# Legacy constant for backwards compatibility
SCENE_JSON_SYSTEM_PROMPT = create_scene_json_system_prompt(list(SUPPORTED_COMPONENTS))
