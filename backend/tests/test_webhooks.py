"""
Tests for the webhooks API endpoints.
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
def mock_video_waiting_approval():
    """Create a mock VideoResponse in waiting_approval status."""
    return VideoResponse(
        id="12345678-1234-1234-1234-123456789012",
        user_id="87654321-4321-4321-4321-210987654321",
        prompt="Explain the Pythagorean theorem",
        status=VideoStatus.WAITING_APPROVAL,
        syllabus_doc_path=None,
        final_video_url=None,
        created_at="2026-01-20T10:00:00Z",
        updated_at="2026-01-20T10:00:00Z",
    )


@pytest.fixture
def mock_video_planning():
    """Create a mock VideoResponse in planning status."""
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
# POST /api/videos/{video_id}/approve Tests
# =============================================================================

def test_approve_invalid_video_id():
    """Test approve fails with invalid video_id format."""
    response = client.post(
        "/api/videos/not-a-uuid/approve",
        json={"approved": True}
    )
    assert response.status_code == 400
    assert "Invalid video_id format" in response.json()["detail"]


@patch("app.api.routes.webhooks.get_video")
def test_approve_video_not_found(mock_get_video):
    """Test approve returns 404 for non-existent video."""
    mock_get_video.return_value = None

    response = client.post(
        "/api/videos/12345678-1234-1234-1234-123456789012/approve",
        json={"approved": True}
    )
    assert response.status_code == 404


@patch("app.api.routes.webhooks.get_video")
def test_approve_wrong_status(mock_get_video, mock_video_planning):
    """Test approve fails for video not in waiting_approval status."""
    mock_get_video.return_value = mock_video_planning

    response = client.post(
        "/api/videos/12345678-1234-1234-1234-123456789012/approve",
        json={"approved": True}
    )
    assert response.status_code == 400
    assert "not waiting for approval" in response.json()["detail"]


@patch("app.api.routes.webhooks.update_video_status")
@patch("app.api.routes.webhooks.get_video")
def test_approve_success(
    mock_get_video, mock_update_status, mock_video_waiting_approval
):
    """Test successful approval updates status to generating."""
    mock_get_video.return_value = mock_video_waiting_approval
    mock_update_status.return_value = True

    response = client.post(
        "/api/videos/12345678-1234-1234-1234-123456789012/approve",
        json={"approved": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "generating"
    assert "approved" in data["message"].lower()


@patch("app.api.routes.webhooks.update_video_status")
@patch("app.api.routes.webhooks.get_supabase_client")
@patch("app.api.routes.webhooks.get_video")
def test_reject_success(
    mock_get_video, mock_supabase, mock_update_status, mock_video_waiting_approval
):
    """Test successful rejection with feedback updates status to planning."""
    mock_get_video.return_value = mock_video_waiting_approval
    mock_update_status.return_value = True
    mock_client = mock_supabase.return_value
    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = None  # noqa: E501

    response = client.post(
        "/api/videos/12345678-1234-1234-1234-123456789012/approve",
        json={"approved": False, "feedback": "Need more detail in scene 2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "planning"
    assert data["feedback"] == "Need more detail in scene 2"


def test_approve_missing_approved_field():
    """Test approve fails without approved field."""
    response = client.post(
        "/api/videos/12345678-1234-1234-1234-123456789012/approve",
        json={}
    )
    assert response.status_code == 422  # Validation error
