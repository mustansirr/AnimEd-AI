"""
Tests for the main FastAPI application endpoints.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agentic AI Educational Video Generator API"}


def test_health_check():
    """Test health check endpoint returns status and configuration info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "supabase_configured" in data
    assert "llm_configured" in data
