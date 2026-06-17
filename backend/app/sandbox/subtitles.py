"""
Subtitle Generation Utility.

Generates SRT format subtitles from narration text based on estimated
reading speed to sync with TTS audio.
"""

import math
from pathlib import Path

# Average speaking speed (words per second)
# 150 words per minute = 2.5 words per second
WORDS_PER_SECOND = 2.5


def format_time(seconds: float) -> str:
    """Format seconds into SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(text: str, output_path: str | Path) -> None:
    """
    Generate an SRT file from narration text.
    
    Splits text by sentences and estimates timing based on word count.

    Args:
        text: The narration text.
        output_path: Path to save the .srt file.
    """
    # Clean text and split by common sentence terminators
    text = text.replace('\n', ' ').strip()
    
    # Simple sentence splitting (could be improved with NLTK if needed)
    raw_sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    current_time = 0.0
    
    with open(output_path, "w", encoding="utf-8") as f:
        for i, sentence in enumerate(raw_sentences):
            # Calculate duration based on word count
            words = sentence.split()
            word_count = len(words)
            
            # Minimum 1.5 seconds per subtitle block for readability
            duration = max(1.5, word_count / WORDS_PER_SECOND)
            
            start_time = current_time
            end_time = current_time + duration
            
            # Write SRT block
            f.write(f"{i + 1}\n")
            f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            
            # Add back period since we stripped it during split
            f.write(f"{sentence}.\n\n")
            
            # Add a small 0.1s gap between subtitles
            current_time = end_time + 0.1
