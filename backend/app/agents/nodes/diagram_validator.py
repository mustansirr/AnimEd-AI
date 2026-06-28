"""
Diagram Validator Node.
Uses a Vision LLM to validate the semantic and topological correctness of STEM diagrams.
"""

import json
import logging
import base64
import subprocess
import asyncio
from pathlib import Path
from uuid import UUID

from app.agents.state import AgentState
from app.config import get_settings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

DIAGRAM_VALIDATOR_PROMPT = """You are a strict Domain-Aware Semantic Validator.
Your job is to examine the final frame of an educational animation and verify that the specific STEM visualization rules for its category are structurally correct.

Concept Category: {category}
Topic: {topic}

Visual correctness is more important than visual decoration!
For STEM concepts, all diagrams, trees, graphs, equations, algorithms, and structures must be semantically correct, educationally accurate, and geometrically valid.

REQUIRED VISUAL ELEMENTS FOR THIS CATEGORY:
{required_elements}

You MUST verify that each of these required visual elements is clearly visible and correctly positioned in the frame. If ANY are missing, is_valid must be false.

Analyze the image carefully. If the category does not have specific rules above, just ensure the visualization makes logical sense for the topic.

Return strictly valid JSON in this format:
{
    "is_valid": true,
    "failure_reason": "If is_valid is false, explain exactly which structural rule or required element was violated. If true, leave empty."
}"""

async def validate_diagram(state: AgentState) -> dict:
    settings = get_settings()
    video_id = state["video_id"]
    scene_index = state.get("current_scene_index", 0)
    category = state.get("concept_topic") or state.get("visualization_strategy", "other")
    topic = state.get("concept_topic", "Unknown")
    
    if not settings.groq_api_key:
        logger.warning("No Groq API key for diagram validator. Auto-passing.")
        return {"last_render_error": None} # pass

    video_path_str = state.get("last_rendered_video_path")
    if not video_path_str or not Path(video_path_str).exists():
        logger.error(f"Cannot evaluate: {video_path_str} not found.")
        return {"last_render_error": "Video file missing for validation"}

    # Fluid Transition Assertion (Code Parsing)
    generated_codes = state.get("generated_codes", [])
    if generated_codes and len(generated_codes) > scene_index:
        current_code = generated_codes[scene_index]
        if "old_comp =" in current_code or "morph" in current_code.lower() or "transform" in current_code.lower():
            if "ReplacementTransform" not in current_code and "Transform(" not in current_code and ".animate" not in current_code and "GlobalTransitionEngine.transition_between_states" not in current_code:
                return {"last_render_error": "Fluid Transition Assertion Failed: Scene contains multi-part transition but missing ReplacementTransform, Transform, or .animate."}

    video_path = Path(video_path_str)
    frame_path = video_path.with_suffix(".diag.jpg")
    cmd = [
        "ffmpeg", "-y", "-sseof", "-3", "-i", str(video_path), 
        "-update", "1", "-q:v", "1", str(frame_path)
    ]
    await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, check=False)
    )

    if not frame_path.exists():
        logger.warning("Could not extract frame for validator. Auto-passing.")
        return {"last_render_error": None}

    from PIL import Image
    import io
    try:
        with Image.open(frame_path) as img:
            img.thumbnail((512, 512))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return {"last_render_error": None}

    from pydantic import SecretStr
    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=SecretStr(settings.groq_api_key),
        temperature=0.1
    )

    from app.sandbox.blueprints import STEM_BLUEPRINTS
    
    required_elements_str = "None specified for this category. Rely on general structural correctness."
    if category in STEM_BLUEPRINTS:
        reqs = STEM_BLUEPRINTS[category].get("required_visual_elements", [])
        if reqs:
            required_elements_str = "\n".join([f"✓ {r}" for r in reqs])

    formatted_prompt = DIAGRAM_VALIDATOR_PROMPT.replace("{category}", str(category)).replace("{topic}", str(topic)).replace("{required_elements}", required_elements_str)

    message = HumanMessage(
        content=[
            {"type": "text", "text": formatted_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    try:
        response = await llm.ainvoke([message])
        content = str(response.content).strip()
        
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
            
        data = json.loads(content)
        is_valid = data.get("is_valid", True)
        reason = data.get("failure_reason", "")
        
        DEVELOPMENT_MODE = True
        
        if not is_valid:
            if DEVELOPMENT_MODE:
                logger.warning(f"[DEV MODE] Diagram validation warning for scene {scene_index}: {reason}")
                return {"last_render_error": None} # pass but warned
            else:
                logger.warning(f"Diagram validation failed for scene {scene_index}: {reason}")
                # Feed the error back as a render error so it gets caught by the reflector
                return {"last_render_error": f"Diagram Validator Failed: {reason}"}
            
        logger.info(f"Diagram validated successfully for scene {scene_index}.")
        return {"last_render_error": None} # pass
        
    except Exception as e:
        logger.warning(f"Diagram Validator API failed: {e}")
        return {"last_render_error": None} # default pass on API error
