import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import io
import asyncio
from pathlib import Path

# --- Imports from project ---
from app.services.rag_service import chunk_text
from app.sandbox.executor import ManimExecutor
from app.sandbox.stitcher import VideoStitcher
from app.agents.nodes.video_quality_evaluator import evaluate_quality
from app.agents.state import QualityScores

# ==============================================================================
# RAG Service Tests (chunk_text)
# ==============================================================================

def test_chunk_text_happy_path():
    """
    Test: chunk_text (Happy Path)
    Verifies that a large text is correctly split into chunks of the specified size and overlap.
    """
    # Create a string of 100 characters
    text = "A" * 100
    
    # Chunk with size 40 and overlap 10
    chunks = chunk_text(text, chunk_size=40, overlap=10)
    
    # Expected chunks calculation:
    # 1: 0-40 (length 40)
    # 2: 30-70 (length 40)
    # 3: 60-100 (length 40)
    assert len(chunks) == 3
    for chunk in chunks:
        assert len(chunk) <= 40

def test_chunk_text_edge_case_empty():
    """
    Test: chunk_text (Edge Case)
    Verifies that passing an empty string or a string smaller than chunk_size handles gracefully.
    """
    text = ""
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) == 0
    
    text_short = "Short"
    chunks_short = chunk_text(text_short, chunk_size=10, overlap=2)
    assert len(chunks_short) == 1
    assert chunks_short[0] == "Short"

# ==============================================================================
# Video Stitcher Tests (_validate_video_file)
# ==============================================================================

@patch("app.sandbox.stitcher.Path.exists")
@patch("app.sandbox.stitcher.Path.stat")
@patch("builtins.open", new_callable=mock_open, read_data=b"\x00\x00\x00\x18ftypmp42")
def test_validate_video_file_happy_path(mock_file, mock_stat, mock_exists):
    """
    Test: _validate_video_file (Happy Path)
    Verifies that a valid MP4 file with the correct 'ftyp' header and sufficient size returns True.
    """
    stitcher = VideoStitcher("/tmp")
    
    # Mock file exists and size is > 1KB
    mock_exists.return_value = True
    mock_stat.return_value = MagicMock(st_size=2048)
    
    result = stitcher._validate_video_file(Path("/fake/video.mp4"))
    assert result is True


@patch("app.sandbox.stitcher.Path.exists")
@patch("app.sandbox.stitcher.Path.stat")
@patch("builtins.open", new_callable=mock_open, read_data=b"<!DOCTYPE ht")
def test_validate_video_file_failure_case(mock_file, mock_stat, mock_exists):
    """
    Test: _validate_video_file (Failure Case)
    Verifies that a file that is too small, or contains HTML instead of video bytes, returns False.
    """
    stitcher = VideoStitcher("/tmp")
    
    # Mock file exists but size is small
    mock_exists.return_value = True
    mock_stat.return_value = MagicMock(st_size=500)
    
    result = stitcher._validate_video_file(Path("/fake/video.mp4"))
    assert result is False  # Fails size check
    
    # Mock size is OK, but it's HTML content
    mock_stat.return_value = MagicMock(st_size=2048)
    result_html = stitcher._validate_video_file(Path("/fake/video.mp4"))
    assert result_html is False  # Fails header check

# ==============================================================================
# Manim Executor Tests (_execute_subprocess)
# ==============================================================================

@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
@patch("app.sandbox.executor.Path.write_text")
@patch("app.sandbox.executor.ManimExecutor._find_video_result")
async def test_execute_subprocess_happy_path(mock_find_video, mock_write_text, mock_create_subprocess):
    """
    Test: ManimExecutor._execute_subprocess (Happy Path)
    Verifies that the executor correctly invokes manim as a subprocess and processes the result.
    """
    executor = ManimExecutor()
    executor.execution_mode = "subprocess"
    
    # Mock subprocess completion
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"stdout_log", b"stderr_log")
    mock_process.returncode = 0
    mock_create_subprocess.return_value = mock_process
    
    # Mock find_video to return a successful ExecutionResult
    from app.sandbox.executor import ExecutionResult
    mock_find_video.return_value = ExecutionResult(
        success=True, video_path="/tmp/output.mp4", error=None, stdout="stdout_log"
    )
    
    result = await executor._execute_subprocess("print('code')", "vid-123", 0)
    
    assert result.success is True
    assert result.video_path == "/tmp/output.mp4"
    mock_create_subprocess.assert_called_once()
    assert "manim" in mock_create_subprocess.call_args[0]


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_execute_subprocess_failure_case(mock_create_subprocess):
    """
    Test: ManimExecutor._execute_subprocess (Failure Case)
    Verifies that the executor properly catches exceptions (e.g. process failure) and returns a failed ExecutionResult.
    """
    executor = ManimExecutor()
    executor.execution_mode = "subprocess"
    
    # Mock subprocess throwing an exception
    mock_create_subprocess.side_effect = Exception("Manim failed to start")
    
    result = await executor._execute_subprocess("print('code')", "vid-123", 0)
    
    assert result.success is False
    assert result.video_path is None
    assert "Manim failed to start" in result.error

# ==============================================================================
# Quality Evaluator Tests (evaluate_quality)
# ==============================================================================

@pytest.mark.asyncio
@patch("app.agents.nodes.video_quality_evaluator.get_settings")
@patch("app.agents.nodes.video_quality_evaluator.Path.exists")
@patch("app.agents.nodes.video_quality_evaluator.subprocess.run")
@patch("app.agents.nodes.video_quality_evaluator.Image.open")
@patch("app.agents.nodes.video_quality_evaluator.ChatGroq")
async def test_evaluate_quality_happy_path(mock_chatgroq, mock_image_open, mock_run, mock_exists, mock_get_settings):
    """
    Test: evaluate_quality (Happy Path)
    Verifies that the evaluator correctly extracts a frame, sends it to the LLM, and parses the quality scores.
    """
    # Mock settings to have an API key
    mock_settings = MagicMock()
    mock_settings.groq_api_key = "test_key"
    mock_get_settings.return_value = mock_settings
    
    # Mock file existence for both video and extracted frame
    mock_exists.return_value = True
    
    # Mock PIL Image
    mock_img = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_img
    
    # Mock LLM Response
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='{"visual_clarity": 9, "educational_clarity": 8, "layout_quality": 9, "animation_quality": 8, "professional_appearance": 9, "feedback": "Good job"}'
    )
    mock_chatgroq.return_value = mock_llm_instance
    
    state = {
        "video_id": "vid-123",
        "current_scene_index": 1,
        "last_rendered_video_path": "/fake/video.mp4",
        "storyboards": [{"scene_goal": "Title sequence"}]
    }
    
    result = await evaluate_quality(state)
    
    assert "quality_scores" in result
    scores = result["quality_scores"]
    assert scores["visual_clarity"] == 9
    assert scores["educational_clarity"] == 8
    assert scores["feedback"] == "Good job"


@pytest.mark.asyncio
@patch("app.agents.nodes.video_quality_evaluator.get_settings")
async def test_evaluate_quality_missing_key(mock_get_settings):
    """
    Test: evaluate_quality (Edge Case - Missing API Key)
    Verifies that the evaluator automatically passes if there is no Groq API key available.
    """
    # Mock settings to NOT have an API key
    mock_settings = MagicMock()
    mock_settings.groq_api_key = None
    mock_get_settings.return_value = mock_settings
    
    state = {
        "video_id": "vid-123",
        "current_scene_index": 1,
        "last_rendered_video_path": "/fake/video.mp4"
    }
    
    result = await evaluate_quality(state)
    
    assert "quality_scores" in result
    scores = result["quality_scores"]
    assert scores["visual_clarity"] == 10
    assert scores["educational_clarity"] == 10
    assert scores["feedback"] == "No API Key"


@pytest.mark.asyncio
@patch("app.agents.nodes.video_quality_evaluator.get_settings")
@patch("app.agents.nodes.video_quality_evaluator.Path.exists")
async def test_evaluate_quality_missing_file(mock_exists, mock_get_settings):
    """
    Test: evaluate_quality (Failure Case - Missing Video File)
    Verifies that the evaluator returns 0 scores when the video file cannot be found.
    """
    mock_settings = MagicMock()
    mock_settings.groq_api_key = "test_key"
    mock_get_settings.return_value = mock_settings
    
    # Mock video file NOT existing
    mock_exists.return_value = False
    
    state = {
        "video_id": "vid-123",
        "current_scene_index": 1,
        "last_rendered_video_path": "/fake/missing.mp4"
    }
    
    result = await evaluate_quality(state)
    
    assert "quality_scores" in result
    scores = result["quality_scores"]
    assert scores["visual_clarity"] == 0
    assert scores["educational_clarity"] == 0
    assert scores["feedback"] == "Video file missing"
