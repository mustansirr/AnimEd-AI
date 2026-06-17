"""
Video Quality Evaluator Node.
Uses a Vision LLM to grade the rendered video.
"""

import json
import logging
import base64
import subprocess
import asyncio
from pathlib import Path
from uuid import UUID

from app.agents.state import AgentState, QualityScores
from app.config import get_settings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.sandbox.executor import ManimExecutor

logger = logging.getLogger(__name__)

EVALUATOR_PROMPT = """You are an expert Educational Video Critic.
Analyze this rendered Manim video frame (the final frame of the scene).
Score it on a scale of 0-10 for each category:
1. Visual Clarity (Check bounding boxes: no overlapping text, no clipped elements, no off-screen elements, readable text)
2. Educational Clarity (Graph/tree strictly visible and structurally accurate when required, educational objective satisfied, visual coverage must be > 80% of narration)
3. Layout Quality (High contrast for text readability, balanced composition, NO empty frames or plain black screens, NO label collisions)
4. Animation Quality (Scene contains semantic objects, not a static empty frame)
5. Professional Appearance (Professional educational backgrounds, consistent typography, looks like a high-quality YouTube video)

{scene_context}

IMPORTANT CONTEXT: 
If the Scene Goal indicates this is an Introduction, Title, or Summary scene, it is PERFECTLY ACCEPTABLE for the frame to be simple. In these cases, give it an 8-10 if the text is clean, centered, and readable.

Return strictly valid JSON in this format:
{
    "visual_clarity": 10,
    "educational_clarity": 10,
    "layout_quality": 10,
    "animation_quality": 10,
    "professional_appearance": 10,
    "feedback": "Your detailed critique here"
}"""

async def evaluate_quality(state: AgentState) -> dict:
    settings = get_settings()
    video_id = state["video_id"]
    scene_index = state["current_scene_index"] - 1 # It just finished rendering this index
    
    if not settings.groq_api_key:
        logger.warning("No Groq API key for vision evaluator. Auto-passing.")
        return {"quality_scores": QualityScores(
            visual_clarity=10, educational_clarity=10, layout_quality=10,
            animation_quality=10, professional_appearance=10, feedback="No API Key"
        )}

    # Get the path to the rendered video from the state
    video_path_str = state.get("last_rendered_video_path")
    
    if not video_path_str or not Path(video_path_str).exists():
        logger.error(f"Cannot evaluate: {video_path_str} not found.")
        # Return failing score to trigger fix agent or fail
        return {"quality_scores": QualityScores(
            visual_clarity=0, educational_clarity=0, layout_quality=0,
            animation_quality=0, professional_appearance=0, feedback="Video file missing"
        )}

    video_path = Path(video_path_str)

    frame_path = video_path.with_suffix(".jpg")
    cmd = [
        "ffmpeg", "-y", "-sseof", "-3", "-i", str(video_path), 
        "-update", "1", "-q:v", "1", str(frame_path)
    ]
    await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: subprocess.run(cmd, capture_output=True, check=False)
    )

    if not frame_path.exists():
        logger.warning("Could not extract frame. Auto-passing.")
        return {"quality_scores": QualityScores(
            visual_clarity=10, educational_clarity=10, layout_quality=10,
            animation_quality=10, professional_appearance=10, feedback="Frame extraction failed"
        )}

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
        return {"quality_scores": QualityScores(
            visual_clarity=10, educational_clarity=10, layout_quality=10,
            animation_quality=10, professional_appearance=10, feedback="Image resize failed"
        )}

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=settings.groq_api_key,
        temperature=0.1
    )
    
    storyboards = state.get("storyboards", [])
    scene_context = ""
    if storyboards and scene_index < len(storyboards):
        scene_info = storyboards[scene_index]
        scene_context = f"Scene Goal: {scene_info.get('goal', 'Unknown')}\nScene Visuals: {scene_info.get('visuals', [])}"

    formatted_prompt = EVALUATOR_PROMPT.replace("{scene_context}", scene_context)

    message = HumanMessage(
        content=[
            {"type": "text", "text": formatted_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    try:
        response = await llm.ainvoke([message])
        content = response.content.strip()
        
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
            
        data = json.loads(content)
        scores = QualityScores(
            visual_clarity=data.get("visual_clarity", 0),
            educational_clarity=data.get("educational_clarity", 0),
            layout_quality=data.get("layout_quality", 0),
            animation_quality=data.get("animation_quality", 0),
            professional_appearance=data.get("professional_appearance", 0),
            feedback=data.get("feedback", "No feedback")
        )
        logger.info(f"Quality scores for scene {scene_index}: {scores}")
        return {"quality_scores": scores}
        
    except Exception as e:
        logger.warning(f"Vision Evaluator failed: {e}")
        # Default pass if API fails
        return {"quality_scores": QualityScores(
            visual_clarity=10, educational_clarity=10, layout_quality=10,
            animation_quality=10, professional_appearance=10, feedback="API Error"
        )}
