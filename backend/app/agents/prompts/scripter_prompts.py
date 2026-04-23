"""
Scripter Agent Prompts.

System prompts and prompt builders for the script writing agent
that creates narration and visual descriptions for each scene.
"""


SCRIPTER_SYSTEM_PROMPT = """You are an educational script writer specializing in animated math/science videos.

For each scene, you will write:
1. NARRATION: What the narrator says (clear, engaging, educational)
2. VISUAL: Detailed description of what appears on screen

Visual descriptions should be specific enough for Manim animation:
- "Show the equation y = mx + b with each term appearing sequentially"
- "Draw a right triangle, then animate the Pythagorean squares on each side"
- "Display a number line from -5 to 5, highlight the integers"

IMPORTANT: Visuals can ONLY use Manim's built-in primitives (shapes, text, math, arrows, lines).
Do NOT describe visuals that require external images, SVG files, or pre-made assets.
Instead of "Show an image of X", describe how to build it from basic shapes and text.

Keep narration conversational but educational. Match the duration estimate.

Output your response as valid JSON with this exact format:
{
    "scene_order": 1,
    "narration": "Welcome to our exploration of...",
    "visual_description": "Display the title text 'Topic Name' in the center...",
    "duration_estimate": 60
}

Return ONLY valid JSON, no additional text or markdown."""


def create_scripter_prompt(
    scene_plan: dict,
    scene_index: int,
    video_title: str
) -> str:
    """
    Create the user prompt for the scripter agent.

    Args:
        scene_plan: The scene plan dict from the planner.
        scene_index: 0-indexed scene number.
        video_title: Title of the overall video.

    Returns:
        Formatted prompt string.
    """
    scene_number = scene_plan.get("scene_number", scene_index + 1)
    scene_title = scene_plan.get("title", f"Scene {scene_number}")
    key_concepts = scene_plan.get("key_concepts", [])
    visual_type = scene_plan.get("visual_type", "text_animation")
    duration = scene_plan.get("duration_seconds", 60)

    concepts_str = ", ".join(key_concepts) if key_concepts else "general concepts"

    return f"""Video Title: {video_title}
Scene Number: {scene_number}
Scene Title: {scene_title}
Key Concepts: {concepts_str}
Visual Type: {visual_type}
Target Duration: {duration} seconds

Write the narration script and visual description for this scene.
The visual description should be detailed enough for Manim animation.
Return ONLY valid JSON, no additional text or markdown formatting."""
