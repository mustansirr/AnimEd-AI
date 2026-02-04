"""
Reflector Agent Node (Self-Correction).

This node analyzes failed Manim code and error messages,
then generates corrected code.
"""

import logging
from uuid import UUID

from langchain_groq import ChatGroq

from app.agents.state import AgentState
from app.agents.prompts.coder_prompts import clean_code_response
from app.config import get_settings
from app.services.supabase_client import (
    get_scene_id_by_order,
    update_scene_code,
    log_scene_error,
)

logger = logging.getLogger(__name__)


REFLECTOR_SYSTEM_PROMPT = """\
You are debugging Manim code that failed to execute.

Analyze the error and fix the code.

COMMON ERRORS AND FIXES:
1. NameError: Check imports are correct - use `from manim import *`
2. AttributeError: Verify Manim method names (e.g., Write not write)
3. TypeError: Check argument types and counts
4. "No Scene found": Ensure class inherits from Scene
5. Positioning errors: Use proper coordinate tuples (x, y, z)
6. Animation errors: Ensure objects are added before animating

DEBUGGING APPROACH:
- Read the error message carefully
- Identify the line that caused the error
- Check for typos in method/class names
- Verify all objects are created before use
- Ensure proper imports

OUTPUT: Return ONLY the fixed Python code.
Do not include explanations, just the corrected code.
"""


async def reflect_and_fix(state: AgentState) -> dict:
    """
    Analyze and fix broken Manim code.

    This node is called when the renderer encounters an error.
    It takes the broken code and error message, then generates
    a corrected version.

    Args:
        state: Current agent state with last_render_error and generated_codes.

    Returns:
        Updated state dict with fixed code and incremented retry_count.
    """
    settings = get_settings()
    video_id = state["video_id"]
    scene_index = state["current_scene_index"]
    retry_count = state.get("retry_count", 0)

    # Get the broken code and error
    generated_codes = state.get("generated_codes", [])
    if scene_index >= len(generated_codes):
        logger.error(f"No code found for scene {scene_index}")
        return {
            "retry_count": retry_count + 1,
            "last_render_error": "No code to fix",
        }

    broken_code = generated_codes[scene_index]
    error = state.get("last_render_error", "Unknown error")

    logger.info(
        f"Reflecting on error for video {video_id}, "
        f"scene {scene_index + 1}, attempt {retry_count + 1}"
    )

    # Log error to Supabase
    scripts = state.get("scripts", [])
    if scripts and scene_index < len(scripts):
        scene_order = scripts[scene_index].get("scene_order", scene_index + 1)
        scene_id = await get_scene_id_by_order(UUID(video_id), scene_order)
        if scene_id:
            await log_scene_error(scene_id, error)

    # Initialize Groq LLM with very low temperature for deterministic fixes
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=settings.groq_api_key,
    )

    # Create prompt with broken code and error
    prompt = f"""\
BROKEN CODE:
```python
{broken_code}
```

ERROR MESSAGE:
{error}

Fix the code to resolve this error. Return only the corrected Python code.
"""

    try:
        # Call LLM
        response = await llm.ainvoke([
            {"role": "system", "content": REFLECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])

        # Clean response
        fixed_code = clean_code_response(response.content)

        # Update the code in the list
        new_codes = generated_codes.copy()
        new_codes[scene_index] = fixed_code

        # Update Supabase with fixed code
        if scripts and scene_index < len(scripts):
            scene_order = scripts[scene_index].get("scene_order", scene_index + 1)
            scene_id = await get_scene_id_by_order(UUID(video_id), scene_order)
            if scene_id:
                await update_scene_code(scene_id, fixed_code)
                logger.info(
                    f"Updated scene {scene_id} with fixed code "
                    f"({len(fixed_code)} chars)"
                )

        return {
            "generated_codes": new_codes,
            "retry_count": retry_count + 1,
            "last_render_error": None,  # Clear error for fresh render
        }

    except Exception as e:
        logger.error(f"Reflector failed for scene {scene_index}: {e}")
        return {
            "retry_count": retry_count + 1,
            "last_render_error": str(e),
        }


def should_retry(state: AgentState, max_retries: int = 3) -> bool:
    """
    Determine if we should retry code generation.

    Args:
        state: Current agent state.
        max_retries: Maximum number of retry attempts.

    Returns:
        True if we should retry, False otherwise.
    """
    retry_count = state.get("retry_count", 0)
    has_error = state.get("last_render_error") is not None

    return has_error and retry_count < max_retries
