"""
Tests for the videos API endpoints.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import VideoResponse, VideoStatus


client = TestClient(app)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_video_response():
    """Create a mock VideoResponse for testing."""
    return VideoResponse(
        id="12345678-1234-1234-1234-123456789012",
        user_id="87654321-4321-4321-4321-210987654321",
        prompt="Explain the Pythagorean theorem",
        status=VideoStatus.PLANNING,
        syllabus_doc_path=None,
        final_video_url=None,
        created_at="2026-01-20T10:00:00Z",
        updated_at="2026-01-20T10:00:00Z",
    )


# =============================================================================
# POST /api/videos Tests
# =============================================================================

def test_create_video_missing_user_id():
    """Test video creation fails without user_id."""
    response = client.post(
        "/api/videos",
        json={"prompt": "Explain quadratic equations"}
    )
    assert response.status_code == 422  # Validation error


def test_create_video_invalid_user_id():
    """Test video creation fails with invalid user_id."""
    response = client.post(
        "/api/videos?user_id=not-a-uuid",
        json={"prompt": "Explain quadratic equations"}
    )
    assert response.status_code == 400
    assert "Invalid user_id format" in response.json()["detail"]


def test_create_video_prompt_too_short():
    """Test video creation fails with too short prompt."""
    response = client.post(
        "/api/videos?user_id=12345678-1234-1234-1234-123456789012",
        json={"prompt": "short"}
    )
    assert response.status_code == 422  # Validation error


# =============================================================================
# GET /api/videos/{video_id} Tests
# =============================================================================

def test_get_video_invalid_id():
    """Test get video fails with invalid video_id format."""
    response = client.get("/api/videos/not-a-uuid")
    assert response.status_code == 400
    assert "Invalid video_id format" in response.json()["detail"]


@patch("app.api.routes.videos.get_video")
def test_get_video_not_found(mock_get_video):
    """Test get video returns 404 for non-existent video."""
    mock_get_video.return_value = None

    response = client.get(
        "/api/videos/12345678-1234-1234-1234-123456789012"
    )
    assert response.status_code == 404


@patch("app.api.routes.videos.get_video")
def test_get_video_success(mock_get_video, mock_video_response):
    """Test get video returns video details."""
    mock_get_video.return_value = mock_video_response

    response = client.get(
        "/api/videos/12345678-1234-1234-1234-123456789012"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "Explain the Pythagorean theorem"
    assert data["status"] == "planning"


# =============================================================================
# GET /api/videos/{video_id}/scenes Tests
# =============================================================================

@patch("app.api.routes.videos.get_video")
def test_get_scenes_video_not_found(mock_get_video):
    """Test get scenes returns 404 for non-existent video."""
    mock_get_video.return_value = None

    response = client.get(
        "/api/videos/12345678-1234-1234-1234-123456789012/scenes"
    )
    assert response.status_code == 404


@patch("app.api.routes.videos.get_scenes")
@patch("app.api.routes.videos.get_video")
def test_get_scenes_empty(mock_get_video, mock_get_scenes, mock_video_response):
    """Test get scenes returns empty list for video with no scenes."""
    mock_get_video.return_value = mock_video_response
    mock_get_scenes.return_value = []

    response = client.get(
        "/api/videos/12345678-1234-1234-1234-123456789012/scenes"
    )
    assert response.status_code == 200
    assert response.json() == []


# =============================================================================
# GET /api/videos Tests
# =============================================================================

def test_list_videos_missing_user_id():
    """Test list videos fails without user_id."""
    response = client.get("/api/videos")
    assert response.status_code == 422


def test_list_videos_invalid_user_id():
    """Test list videos fails with invalid user_id."""
    response = client.get("/api/videos?user_id=not-a-uuid")
    assert response.status_code == 400
