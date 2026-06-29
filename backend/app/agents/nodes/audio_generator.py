"""
Audio Generator Node.

This LangGraph node generates TTS audio for the current scene
and records the precise audio duration into the state.
"""

import logging
from pathlib import Path

from app.agents.state import AgentState
from app.services.tts_service import generate_scene_audio
from app.config import get_settings

logger = logging.getLogger(__name__)


async def generate_audio_node(state: AgentState) -> AgentState:
    """
    Generate TTS audio and subtitles for the current scene.
    
    Args:
        state: Current agent state.
        
    Returns:
        Updated AgentState with scene_audio_durations.
    """
    scene_index = state.get("current_scene_index", 0)
    scripts = state.get("scripts", [])
    video_id = state.get("video_id")
    
    if not scripts or scene_index >= len(scripts):
        logger.error(f"No script found for scene {scene_index}")
        return state
        
    current_script = scripts[scene_index]
    narration_text = current_script.get("narration", "")
    
    settings = get_settings()
    storage_path = Path(getattr(settings, "storage_path", "/app/storage"))
    output_dir = storage_path / video_id / f"scene_{scene_index}"
    
    if not narration_text.strip():
        logger.warning(f"Empty narration for scene {scene_index}, duration is 0")
        durations = state.get("scene_audio_durations", {}).copy()
        durations[scene_index] = 0.0
        return {**state, "scene_audio_durations": durations}
        
    try:
        duration, audio_path, vtt_path = await generate_scene_audio(
            narration_text=narration_text,
            output_dir=output_dir,
            scene_index=scene_index
        )
        
        # Update state with the exact duration
        durations = state.get("scene_audio_durations", {}).copy()
        durations[scene_index] = duration
        
        logger.info(f"Audio generated for scene {scene_index}: {duration}s")
        return {**state, "scene_audio_durations": durations}
        
    except Exception as e:
        logger.exception(f"Failed to generate audio for scene {scene_index}: {e}")
        # In case of failure, provide a fallback duration estimate based on words
        words = len(narration_text.split())
        estimated_duration = max(3.0, words * 0.4)
        
        durations = state.get("scene_audio_durations", {}).copy()
        durations[scene_index] = estimated_duration
        
        logger.warning(f"Using fallback duration {estimated_duration}s for scene {scene_index}")
        return {**state, "scene_audio_durations": durations}
