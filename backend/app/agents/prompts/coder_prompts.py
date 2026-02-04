"""
Coder prompts for Manim code generation.

This module provides prompts and utilities for the CodeGen agent
that generates Manim animation code from visual descriptions.
"""

from pathlib import Path
from typing import Optional


CODER_SYSTEM_PROMPT = """\
You are a Manim code expert. Generate Python code using the Manim library
to create educational animations.

RULES:
1. Always use a Scene class with construct() method
2. Use self.play() for animations, self.wait() for pauses
3. Import only from manim: `from manim import *`
4. Keep animations smooth - use appropriate run_time
5. End each major section with self.wait(1)

COMMON PATTERNS:
- Text: Text("content", font_size=36)
- Math: MathTex("latex_equation")
- Shapes: Circle(), Square(), Triangle()
- Arrows: Arrow(start, end)
- Groups: VGroup(obj1, obj2)

ANIMATION METHODS:
- Write(text) - for text appearing
- Create(shape) - for shapes appearing
- Transform(a, b) - morph a into b
- FadeIn/FadeOut - opacity transitions
- MoveTo(position) - move objects

POSITIONING:
- Use UP, DOWN, LEFT, RIGHT, ORIGIN constants
- Combine with shifts: obj.shift(UP * 2 + LEFT)
- Use .to_edge(UP), .next_to(other, DOWN)

OUTPUT FORMAT:
Return ONLY valid Python code. No markdown, no explanations.
Start with imports, define one Scene class.
"""


def get_few_shot_examples(snippets_dir: Optional[Path] = None) -> str:
    """
    Load all examples from the snippets/manim_examples/ folder.

    These examples are used for few-shot prompting to improve
    the quality of generated Manim code.

    Args:
        snippets_dir: Path to snippets directory. Defaults to
                      snippets/manim_examples/ relative to backend root.

    Returns:
        Concatenated string of all example files with headers.
    """
    if snippets_dir is None:
        # Default path relative to backend root
        snippets_dir = Path(__file__).parent.parent.parent.parent / \
            "snippets" / "manim_examples"

    examples = []
    if snippets_dir.exists():
        for file in sorted(snippets_dir.glob("*.py")):
            content = file.read_text()
            examples.append(f"# Example: {file.stem}\n{content}")

    return "\n\n".join(examples)


def create_coder_prompt(
    visual_description: str,
    narration: str,
    include_examples: bool = True
) -> str:
    """
    Create a prompt for the Manim CodeGen agent.

    Args:
        visual_description: What should appear on screen (from scripter).
        narration: The narration text (for timing reference).
        include_examples: Whether to include few-shot examples.

    Returns:
        Formatted prompt string for the LLM.
    """
    prompt_parts = []

    if include_examples:
        examples = get_few_shot_examples()
        if examples:
            prompt_parts.append("EXAMPLES OF GOOD MANIM CODE:")
            prompt_parts.append(examples)
            prompt_parts.append("\n---\n")

    prompt_parts.append("SCENE TO ANIMATE:")
    prompt_parts.append(f"Visual Description: {visual_description}")
    prompt_parts.append(f"Narration (for timing reference): {narration}")
    prompt_parts.append("\nGenerate the Manim code for this scene.")

    return "\n".join(prompt_parts)


def clean_code_response(response: str) -> str:
    """
    Remove markdown code blocks if present in LLM response.

    Args:
        response: Raw LLM response that may contain markdown formatting.

    Returns:
        Clean Python code string.
    """
    # Remove markdown code fences
    if response.startswith("```python"):
        response = response[9:]
    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    return response.strip()
