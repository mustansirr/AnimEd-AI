"""
Pydantic models for request/response validation.
These models define the data structures used across the API.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Possible status values for a video generation request."""
    PLANNING = "planning"
    SCRIPTING = "scripting"
    WAITING_APPROVAL = "waiting_approval"
    GENERATING = "generating"
    RENDERING = "rendering"
    STITCHING = "stitching"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Video Models
# =============================================================================

class VideoCreate(BaseModel):
    """Request body for creating a new video generation request."""
    prompt: str = Field(..., min_length=10, description="The topic or concept to explain")
    syllabus_doc_path: Optional[str] = Field(
        None,
        description="Path to uploaded syllabus PDF in Supabase Storage"
    )


class VideoResponse(BaseModel):
    """Response model for video data."""
    id: UUID
    user_id: UUID
    prompt: str
    status: VideoStatus
    syllabus_doc_path: Optional[str] = None
    final_video_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoStatusUpdate(BaseModel):
    """Request body for updating video status."""
    status: VideoStatus


# =============================================================================
# Scene Models
# =============================================================================

class SceneCreate(BaseModel):
    """Request body for creating a new scene."""
    video_id: UUID
    scene_order: int = Field(..., ge=1, description="Order of this scene in the video")
    narration_script: Optional[str] = None
    visual_plan: Optional[str] = None


class SceneResponse(BaseModel):
    """Response model for scene data."""
    id: UUID
    video_id: UUID
    scene_order: int
    narration_script: Optional[str] = None
    visual_plan: Optional[str] = None
    manim_code: Optional[str] = None
    is_rendered: bool = False
    error_log: Optional[str] = None
    video_segment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SceneCodeUpdate(BaseModel):
    """Request body for updating scene Manim code."""
    manim_code: str


class SceneRenderUpdate(BaseModel):
    """Request body for marking scene as rendered."""
    video_segment_url: str


class SceneErrorLog(BaseModel):
    """Request body for logging scene errors."""
    error_log: str


# =============================================================================
# Approval Models
# =============================================================================

class ApprovalRequest(BaseModel):
    """Request body for script approval/rejection."""
    approved: bool
    feedback: Optional[str] = Field(
        None,
        description="Optional feedback if scripts are rejected"
    )
