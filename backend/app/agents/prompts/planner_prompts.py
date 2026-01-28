"""
Planner Agent Prompts.

System prompts and prompt builders for the curriculum planning agent
that creates structured video plans.
"""


PLANNER_SYSTEM_PROMPT = """You are a curriculum expert and educational video planner.

Given a topic and optional syllabus context, create a structured video plan with clear scenes.

Requirements:
- Each scene should be 30-90 seconds
- Start with fundamentals, build complexity gradually
- Include visual demonstrations for each concept
- Total video should be 3-5 minutes (4-8 scenes)
- Use clear, engaging educational language

Output your response as valid JSON with this exact format:
{
    "title": "Video Title",
    "learning_objectives": ["objective1", "objective2", ...],
    "scenes": [
        {
            "scene_number": 1,
            "title": "Introduction to X",
            "key_concepts": ["concept1", "concept2"],
            "visual_type": "text_animation|diagram|graph|equation",
            "duration_seconds": 60
        }
    ]
}

Visual types:
- text_animation: For introducing terms, definitions, titles
- diagram: For processes, relationships, structures
- graph: For functions, data, mathematical plots
- equation: For formulas, step-by-step math derivations"""


def create_planner_prompt(user_prompt: str, syllabus_context: str = "") -> str:
    """
    Create the user prompt for the planner agent.

    Args:
        user_prompt: The user's topic/concept request.
        syllabus_context: Optional RAG context from uploaded syllabus.

    Returns:
        Formatted prompt string.
    """
    context_section = ""
    if syllabus_context and syllabus_context.strip():
        context_section = f"""
Syllabus Context (use this to guide your planning):
---
{syllabus_context}
---

"""

    return f"""{context_section}User Request: {user_prompt}

Create a detailed video plan following the system instructions.
Return ONLY valid JSON, no additional text or markdown formatting."""
