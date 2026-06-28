"""
Fix Agent Node.
Handles feedback from the Video Quality Evaluator and routes back to Layout or SceneJSON.
"""

import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def fix_scene(state: AgentState) -> dict:
    video_id = state["video_id"]
    scores = state.get("quality_scores")
    
    retry_count = state.get("retry_count", 0)
    
    error_msg = state.get("last_render_error")
    feedback = scores.get("feedback", "") if scores else ""
    
    fix_reason = error_msg or feedback
    logger.warning(
        f"Fix Agent activated for video {video_id}. Feedback: {fix_reason}"
    )

    # Automated Fix Implementation: Hook up reflector critique to fix the Manim script
    if fix_reason and ("Temporal Freeze" in fix_reason or "Fluid Transition" in fix_reason):
        from app.services.llm_factory import create_llm
        llm = create_llm("coder", temperature=0.1)
        generated_codes = state.get("generated_codes", [])
        if generated_codes:
            scene_index = len(generated_codes) - 1
            bad_code = generated_codes[scene_index]
            
            # Prevent LLM from truncating preamble by only sending the class definition
            if "class Scene1(Scene):" in bad_code:
                preamble, scene_class = bad_code.split("class Scene1(Scene):", 1)
                scene_class = "class Scene1(Scene):" + scene_class
            else:
                preamble = ""
                scene_class = bad_code

            prompt = f"The following Manim code failed validation:\n{fix_reason}\n\nCode:\n```python\n{scene_class}\n```\nRewrite the code to fix the temporal freeze or transition issue. If it needs .animate, Transform, ReplacementTransform, or self.wait(T), add it.\nCRITICAL CONSTRAINT FOR FIX_AGENT: When patching code following a compilation or validation failure, you are STRICTLY FORBIDDEN from generating or calling custom testing/validation functions (e.g., 'validate_animation_interfaces()') inside the Manim python code payload. Every function execution must map strictly to real classes defined inside components.py or native Manim syntax.\nReturn only the raw python code for the Scene class."
            
            try:
                # Synchronous-like run for async env or just ainvoke
                response = await llm.ainvoke([{"role": "user", "content": prompt}])
                fixed_scene_class = response.content.replace("```python", "").replace("```", "").strip()
                
                if "class Scene1(Scene):" not in fixed_scene_class and preamble:
                     # Ensure class definition is preserved
                     pass # We assume the LLM returned it correctly or we could force it
                     
                fixed_code = preamble + "\n" + fixed_scene_class
                generated_codes[scene_index] = fixed_code
                logger.info(f"Fix agent applied self-correction to scene {scene_index}.")
                return {
                    "generated_codes": generated_codes,
                    "retry_count": retry_count + 1,
                    "last_render_error": None
                }
            except Exception as e:
                logger.error(f"Fix agent LLM failed: {e}")

    # Fallback if no LLM fix applied
    return {
        "retry_count": retry_count + 1,
        "last_render_error": f"Quality check failed: {fix_reason}"
    }
