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
11. Call `.next_to()` ONLY on Mobjects (like `MathTex`), NEVER on Animations (like `Write`).
    WRONG: `self.play(Write(MathTex("...")).next_to(...))`
    CORRECT: `obj = MathTex("...").next_to(...)` then `self.play(Write(obj))`

FORBIDDEN — DO NOT USE:
1. SVGMobject() — no SVG files exist in the render environment.
2. ImageMobject() — no image files exist in the render environment.
3. Do NOT reference any external files (SVGs, PNGs, JPGs, audio, etc.).
4. Do NOT use file paths or filenames anywhere in the code.
5. Build ALL visuals using ONLY Manim's built-in primitives listed below.
6. If a scene calls for a complex diagram (e.g., an ant, a human body, a logo),
   approximate it using combinations of Circle, Ellipse, Rectangle, Line,
   Arc, Polygon, Arrow, Dot, CurvedArrow, and other built-in shapes.

COMMON PATTERNS:
- Text: Text("content", font_size=36)
- Math: MathTex("latex_equation")
- Shapes: Circle(), Square(), Triangle(), Ellipse(), Polygon(), Dot()
- Lines: Line(start, end), DashedLine(start, end), Arc()
- Arrows: Arrow(start, end), CurvedArrow(start, end)
- Groups: VGroup(obj1, obj2)
- Labels: BraceLabel(obj, "text"), Brace(obj, direction)

ANIMATION METHODS:
- Write(text) - for text appearing
- Create(shape) - for shapes appearing
- Transform(a, b) - morph a into b
- FadeIn/FadeOut - opacity transitions
- MoveTo(position) - move objects

OUTPUT RULES:
1. You may think and plan step-by-step before writing code, but your final python code MUST be enclosed in a single ```python ... ``` markdown block.
2. DO NOT split the code into multiple blocks. Provide the complete code in one block.
3. DO NOT import anything other than `from manim import *`.
4. IF you feel the need to explain inside the code, use Python comments `#`.
5. Inside the code block, start with imports, and define EXACTLY ONE Scene class.
6. Do not include markdown code blocks of anything else, except the generated code.
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
    pattern = r"```[ \t]*(?:python|py)?[ \t]*\n(.*?)```"
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Step 2: Find the first 'from manim import' and take everything after
    if "from manim import" in response:
        code_part = response[response.find("from manim import"):].strip()
        if "```" in code_part:
            code_part = code_part[:code_part.find("```")]
        return code_part.strip()

    # Step 3: Fallback — return as-is after stripping whitespace
    return response.strip()
