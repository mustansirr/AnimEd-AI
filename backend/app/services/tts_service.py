"""
TTS Service using edge-tts.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Tuple

from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)


async def generate_scene_audio(
    narration_text: str,
    output_dir: Path,
    scene_index: int,
    voice: str = "en-US-AriaNeural"
) -> Tuple[float, Path, Path]:
    """
    Generate TTS audio and subtitles for a scene.

    Args:
        narration_text: The text to be spoken.
        output_dir: Directory to save the outputs.
        scene_index: The index of the scene.
        voice: The edge-tts voice to use.

    Returns:
        Tuple containing (duration_in_seconds, audio_path, subtitle_path)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audio_path = output_dir / f"scene_{scene_index}.mp3"
    vtt_path = output_dir / f"scene_{scene_index}.vtt"
    
    # Run edge-tts via subprocess
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", narration_text,
        "--write-media", str(audio_path),
        "--write-subtitles", str(vtt_path)
    ]
    
    logger.info(f"Generating TTS for scene {scene_index}...")
    
    try:
        # Run in executor to avoid blocking the event loop
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
        )
        
        if result.returncode != 0:
            logger.error(f"edge-tts failed: {result.stderr}")
            raise RuntimeError(f"TTS generation failed: {result.stderr}")
            
        if not audio_path.exists():
            raise FileNotFoundError(f"edge-tts did not create {audio_path}")
            
        # Use mutagen to get the exact duration of the MP3
        audio = MP3(str(audio_path))
        duration = float(audio.info.length)
        
        logger.info(f"TTS generated for scene {scene_index}, duration: {duration:.3f}s")
        
        return duration, audio_path, vtt_path
        
    except subprocess.TimeoutExpired:
        logger.error(f"edge-tts timed out for scene {scene_index}")
        raise RuntimeError("TTS generation timed out")
    except Exception as e:
        logger.exception(f"Error during TTS generation: {e}")
        raise
