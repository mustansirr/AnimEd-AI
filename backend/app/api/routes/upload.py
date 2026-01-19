"""
Upload API routes for PDF processing and RAG.

Handles file uploads, PDF parsing, embedding generation, and storage.
"""

from typing import Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.services import rag_service
from app.services.supabase_client import get_video


router = APIRouter(prefix="/upload", tags=["upload"])


# =============================================================================
# Response Models
# =============================================================================

class UploadResponse(BaseModel):
    """Response after successful PDF upload and processing."""
    video_id: str
    chunks_stored: int
    message: str


class UploadStatusResponse(BaseModel):
    """Response for checking upload status."""
    video_id: str
    has_context: bool
    chunk_count: int


# =============================================================================
# Helper Functions
# =============================================================================

def validate_uuid(video_id: str) -> UUID:
    """Validate and parse a video_id string to UUID."""
    try:
        return UUID(video_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video_id format. Must be a valid UUID."
        )


async def validate_video_exists(video_uuid: UUID, video_id: str) -> None:
    """Verify that a video exists in the database."""
    video = await get_video(video_uuid)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with id {video_id} not found."
        )


async def read_and_validate_pdf(file: UploadFile) -> Tuple[bytes, str]:
    """Read and validate a PDF file upload."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Parse PDF
    try:
        text_content = rag_service.parse_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    return file_bytes, text_content


# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF for RAG",
    description="""
    Upload a PDF syllabus file for a video.

    The PDF will be:
    1. Parsed to extract text content
    2. Split into overlapping chunks
    3. Embedded using Supabase Edge Function (gte-small model)
    4. Stored in the database for semantic search

    This context can then be retrieved by the Planner Agent.
    """
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    video_id: str = Form(..., description="UUID of the video this content belongs to"),
    chunk_size: Optional[int] = Form(500, description="Size of text chunks"),
    overlap: Optional[int] = Form(50, description="Overlap between chunks"),
):
    """Upload and process a PDF file for RAG context."""
    # Validate inputs
    video_uuid = validate_uuid(video_id)
    await validate_video_exists(video_uuid, video_id)

    # Read and parse PDF
    _, text_content = await read_and_validate_pdf(file)

    # Chunk text
    chunks = rag_service.chunk_text(
        text_content,
        chunk_size=chunk_size or 500,
        overlap=overlap or 50
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text content could be extracted from the PDF."
        )

    # Delete existing chunks for this video (in case of re-upload)
    await rag_service.delete_video_chunks(video_uuid)

    # Generate embeddings and store
    try:
        chunks_stored = await rag_service.store_embeddings(video_uuid, chunks)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding generation failed: {str(e)}"
        )

    return UploadResponse(
        video_id=video_id,
        chunks_stored=chunks_stored,
        message=f"Successfully processed PDF. Stored {chunks_stored} chunks for RAG."
    )


@router.get(
    "/{video_id}/context",
    summary="Retrieve RAG context",
    description="Retrieve relevant context from stored document chunks for a query."
)
async def get_context(
    video_id: str,
    query: str,
    top_k: int = 5,
    threshold: float = 0.5,
):
    """
    Retrieve relevant context for a query.

    This endpoint is primarily used by the Planner Agent to get
    syllabus context for video planning.
    """
    video_uuid = validate_uuid(video_id)

    # Retrieve context
    try:
        context = await rag_service.retrieve_context(
            query=query,
            video_id=video_uuid,
            top_k=top_k,
            threshold=threshold
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Context retrieval failed: {str(e)}"
        )

    return {
        "video_id": video_id,
        "query": query,
        "context": context,
        "has_context": bool(context),
    }


@router.delete(
    "/{video_id}/chunks",
    summary="Delete document chunks",
    description="Delete all stored document chunks for a video."
)
async def delete_chunks(video_id: str):
    """Delete all document chunks for a video."""
    video_uuid = validate_uuid(video_id)
    deleted_count = await rag_service.delete_video_chunks(video_uuid)

    return {
        "video_id": video_id,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} document chunks."
    }
