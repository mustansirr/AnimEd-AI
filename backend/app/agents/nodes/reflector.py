"""
Reflector Agent Node (Self-Correction).

This node analyzes failed Manim code and error messages,
then generates corrected code.
"""

import logging
from uuid import UUID

from app.services.llm_factory import create_llm

from app.agents.state import AgentState
from app.agents.prompts.coder_prompts import clean_code_response
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
7. Temporal Freeze / Transition errors: Add `ReplacementTransform`, `Transform`, `.animate`, or explicit `self.wait(T)` to fix static pacing.

DEBUGGING APPROACH:
- Read the error message carefully
- Identify the line that caused the error
- Check for typos in method/class names
- Verify all objects are created before use
- Ensure proper imports

CRITICAL CONSTRAINT FOR FIX_AGENT/REFLECTOR:
1. When patching code following a compilation or validation failure, you are STRICTLY FORBIDDEN from generating or calling custom testing/validation functions (e.g., 'validate_animation_interfaces()') inside the Manim python code payload. Every function execution must map strictly to real classes defined inside components.py or native Manim syntax.
2. DO NOT hallucinate custom animation methods on VGroups (e.g., do NOT use `obj.intro_animations()`). If a custom transition method does not exist, use standard Manim animations like `FadeIn(obj)`, `Write(obj)`, or `obj.animate...`.

OUTPUT: Return ONLY the fixed Python code.
Do not include explanations, just the corrected code.
"""


async def reflect_and_fix(state: AgentState) -> dict:
    """
    Analyze and fix broken Manim code.

    This node is called when the renderer encounters an error.
    It takes the broken code and error message, then generates
    a corrected version.

    GUARD: Certain errors are caused by pipeline configuration issues
    (wrong component, empty scene data) rather than fixable code bugs.
    The Reflector will refuse to attempt LLM repair for these cases,
    because the LLM would only hallucinate new component implementations.

    Args:
        state: Current agent state with last_render_error and generated_codes.

    Returns:
        Updated state dict with fixed code and incremented retry_count.
    """
    video_id = state["video_id"]
    retry_count = state.get("retry_count", 0)
    error = state.get("last_render_error", "")

    # ---- GUARD: Pipeline configuration errors are NOT code bugs ----
    # If the error is caused by an unsupported component, empty pipeline
    # data, or a fatal configuration issue, the Reflector cannot fix it
    # by rewriting Manim code. Attempting to do so causes hallucinations
    # (e.g., the Reflector inventing NeuralNetwork([4,3,2]) for a
    # Pythagoras theorem lesson).
    NON_FIXABLE_MARKERS = [
        "Unsupported component",
        "positioned_jsons is empty",
        "scene_jsons is empty",
        "FATAL ERROR",
        "Aborting workflow",
    ]
    if any(marker in str(error) for marker in NON_FIXABLE_MARKERS):
        logger.error(
            f"Reflector refusing to fix non-code error for video {video_id}: {error}"
        )
        return {
            "retry_count": retry_count + 1,
            "last_render_error": error,
        }

    generated_codes = state.get("generated_codes", [])
    if not generated_codes:
        logger.error("No code found to reflect on.")
        return {
            "retry_count": retry_count + 1,
            "last_render_error": "No code to fix",
        }
        
    # The coder already incremented current_scene_index, so the failing code is the last one in the list.
    scene_index = len(generated_codes) - 1

    broken_code = generated_codes[scene_index]
    error = state.get("last_render_error", "Unknown error")

    logger.info(
        f"Reflecting on error for video {video_id}, "
        f"scene {scene_index + 1}, attempt {retry_count + 1}"
    )

    # Log error to Supabase
    storyboards = state.get("storyboards", [])
    if storyboards and scene_index < len(storyboards):
        scene_order = storyboards[scene_index].get("scene_number", scene_index + 1)
        scene_id = await get_scene_id_by_order(UUID(video_id), scene_order)
        if scene_id:
            await log_scene_error(scene_id, error)

    # Initialize LLM for code reflection (provider configured via env vars)
    llm = create_llm("reflector", temperature=0.1)

    # Prevent LLM from truncating preamble by only sending the class definition
    if "class Scene1(Scene):" in broken_code:
        preamble, scene_class = broken_code.split("class Scene1(Scene):", 1)
        scene_class = "class Scene1(Scene):" + scene_class
    else:
        preamble = ""
        scene_class = broken_code

    # Create prompt with broken code and error
    prompt = f"""\
BROKEN CODE:
```python
{scene_class}
```

ERROR MESSAGE:
{error}

Fix the code to resolve this error. Return only the corrected Python code.
"""

    import tiktoken
    try:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    sys_tokens = len(encoding.encode(REFLECTOR_SYSTEM_PROMPT))
    user_tokens = len(encoding.encode(prompt))
    total_estimated = sys_tokens + user_tokens
    
    if total_estimated > 5000:
        logger.warning(f"[DIAGNOSTIC] Reflector prompt exceeds 5000 tokens ({total_estimated}). Truncating code and error.")
        # Truncate code to last 2000 chars, error to last 1000 chars
        trunc_code = broken_code[-2000:] if len(broken_code) > 2000 else broken_code
        trunc_error = str(error)[-1000:] if len(str(error)) > 1000 else str(error)
        
        prompt = f"""\
BROKEN CODE (Truncated):
```python
...
{trunc_code}
```

ERROR MESSAGE (Truncated):
...
{trunc_error}

Fix the code to resolve this error. Return only the corrected Python code.
"""

    try:
        # Call LLM
        response = await llm.ainvoke([
            {"role": "system", "content": REFLECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])

        # Clean response
        fixed_scene_class = clean_code_response(response.content)
        
        fixed_code = preamble + "\n" + fixed_scene_class
        
        # Update the code in the list
        new_codes = generated_codes.copy()
        new_codes[scene_index] = fixed_code

        # Update Supabase with fixed code
        if storyboards and scene_index < len(storyboards):
            scene_order = storyboards[scene_index].get("scene_number", scene_index + 1)
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
