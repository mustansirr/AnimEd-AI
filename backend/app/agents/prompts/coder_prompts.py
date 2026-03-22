"""
Coder prompts for Manim code generation.

This module provides prompts and utilities for the CodeGen agent
that generates Manim animation code from visual descriptions.
"""

import re
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

CRITICAL COORDINATE RULES:
1. The screen center is (0,0).
2. The visible X-range is [-7, 7].
3. The visible Y-range is [-4, 4].
4. To place objects, visualize a 3x3 grid:
   - TOP-LEFT=(-4, 2.5), TOP-CENTER=(0, 2.5), TOP-RIGHT=(4, 2.5)
   - MID-LEFT=(-4, 0),   CENTER=(0, 0),       MID-RIGHT=(4, 0)
   - BOT-LEFT=(-4,-2.5), BOT-CENTER=(0,-2.5), BOT-RIGHT=(4,-2.5)
5. PREVENT OVERLAP: Always use `.next_to(object, DIRECTION, buff=0.5)` \
instead of absolute coordinates when stacking items.
6. When using `UP`, `DOWN`, `LEFT`, `RIGHT`, treat them as unit vectors \
of length 1.
7. Use `.to_edge(DIRECTION, buff=0.5)` to place items at screen edges.
8. Use `VGroup(...).arrange(DOWN, buff=0.4)` for vertical lists and \
`VGroup(...).arrange(RIGHT, buff=0.5)` for horizontal layouts.
9. Never place two objects at the same absolute coordinate.
10. Always scale text with `font_size=` to keep it within the visible frame.

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

OUTPUT RULES:
1. RETURN ONLY CODE.
2. DO NOT write "Here is the code", "In this scene", or any other \
conversational text.
3. DO NOT use markdown code blocks (```python). Just the raw code.
4. DO NOT import anything other than `from manim import *`.
5. IF you feel the need to explain, use Python comments `#` inside the code.
6. Start with imports, define one Scene class.
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
    Extract clean Manim Python code from an LLM response.

    Uses a multi-step approach:
    1. Try to extract code from markdown ```python fences.
    2. Fall back to finding the first `from manim import` line.
    3. Return the raw response as a last resort.

    Args:
        response: Raw LLM response that may contain markdown formatting
                  or conversational text.

    Returns:
        Clean Python code string.
    """
    # Step 1: Try to extract code inside markdown fences
    pattern = r"```(?:python)?\n(.*?)```"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Step 2: Find the first 'from manim import' and take everything after
    if "from manim import" in response:
        return response[response.find("from manim import"):].strip()

    # Step 3: Fallback — return as-is after stripping whitespace
    return response.strip()
