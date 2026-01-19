"""
RAG (Retrieval Augmented Generation) Service.

Handles PDF parsing, text chunking, embedding generation via Supabase Edge Functions,
and semantic similarity search for context retrieval.
"""

from typing import List
from uuid import UUID
import io
import re

import httpx
from PyPDF2 import PdfReader

from app.config import get_settings


# =============================================================================
# PDF Parsing
# =============================================================================

def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted text content as a single string.

    Raises:
        ValueError: If PDF cannot be parsed or is empty.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)

        if len(reader.pages) == 0:
            raise ValueError("PDF file has no pages")

        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValueError("PDF file contains no extractable text")

        # Clean up the text
        full_text = _clean_text(full_text)

        return full_text

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Split into lines to handle vertical whitespace separately
    lines = text.split('\n')

    cleaned_lines = []
    for line in lines:
        # Normalize horizontal whitespace within the line
        cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
        cleaned_lines.append(cleaned_line)

    # Rejoin with newlines
    text = '\n'.join(cleaned_lines)

    # Replace multiple newlines (3 or more) with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# =============================================================================
# Text Chunking
# =============================================================================

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks for embedding.

    Uses a simple character-based chunking strategy that tries to break
    at sentence boundaries when possible.

    Args:
        text: The full text to chunk.
        chunk_size: Target size for each chunk in characters.
        overlap: Number of characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    # If text is shorter than chunk_size, return as single chunk
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If this isn't the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence-ending punctuation near the end
            search_start = max(start + chunk_size - 100, start)
            search_end = min(start + chunk_size + 50, len(text))
            search_text = text[search_start:search_end]

            # Find the last sentence boundary in the search window
            best_break = -1
            for punct in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
                pos = search_text.rfind(punct)
                if pos > best_break:
                    best_break = pos

            if best_break > 0:
                end = search_start + best_break + 2  # Include the punctuation

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position, accounting for overlap
        if end >= len(text):
            break

        new_start = end - overlap
        if new_start <= start:
            # Prevent infinite loop if overlap is too large relative to chunk size and sentence splitting
            new_start = start + 1

        start = new_start

    return chunks


# =============================================================================
# Embedding Generation
# =============================================================================

async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text using Supabase Edge Function.

    Args:
        text: The text to generate embedding for.

    Returns:
        384-dimensional embedding vector.

    Raises:
        RuntimeError: If embedding generation fails.
    """
    settings = get_settings()

    # Construct the Edge Function URL
    # For local development: http://localhost:54321/functions/v1/embed
    # For production: {supabase_url}/functions/v1/embed
    base_url = settings.supabase_url.rstrip('/')
    embed_url = f"{base_url}/functions/v1/embed"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                embed_url,
                json={"input": text},
                headers={
                    "Authorization": f"Bearer {settings.supabase_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()
            embedding = data.get("embedding")

            if not embedding:
                raise RuntimeError("No embedding returned from Edge Function")

            return embedding

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Edge Function returned error {e.response.status_code}: "
                f"{e.response.text}"
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Failed to connect to Edge Function: {str(e)}")


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single request.

    Args:
        texts: List of texts to generate embeddings for.

    Returns:
        List of 384-dimensional embedding vectors.

    Raises:
        RuntimeError: If embedding generation fails.
    """
    if not texts:
        return []

    settings = get_settings()

    base_url = settings.supabase_url.rstrip('/')
    embed_url = f"{base_url}/functions/v1/embed"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                embed_url,
                json={"input": texts},
                headers={
                    "Authorization": f"Bearer {settings.supabase_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,  # Longer timeout for batch
            )
            response.raise_for_status()

            data = response.json()
            embeddings = data.get("embeddings")

            if not embeddings:
                raise RuntimeError("No embeddings returned from Edge Function")

            return embeddings

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Edge Function returned error {e.response.status_code}: "
                f"{e.response.text}"
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Failed to connect to Edge Function: {str(e)}")


# =============================================================================
# Storage & Retrieval
# =============================================================================

async def store_embeddings(
    video_id: UUID,
    chunks: List[str]
) -> int:
    """
    Generate embeddings for text chunks and store in database.

    Args:
        video_id: The UUID of the video this content belongs to.
        chunks: List of text chunks to embed and store.

    Returns:
        Number of chunks stored.

    Raises:
        RuntimeError: If embedding generation or storage fails.
    """
    from app.services.supabase_client import get_supabase_client

    if not chunks:
        return 0

    # Generate embeddings for all chunks
    embeddings = await generate_embeddings_batch(chunks)

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"Embedding count mismatch: got {len(embeddings)} "
            f"embeddings for {len(chunks)} chunks"
        )

    # Prepare records for insertion
    records = [
        {
            "video_id": str(video_id),
            "chunk_index": i,
            "content": chunk,
            "embedding": embedding,
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    # Insert into database
    client = get_supabase_client()
    result = client.table("document_chunks").insert(records).execute()

    return len(result.data)


async def retrieve_context(
    query: str,
    video_id: UUID,
    top_k: int = 5,
    threshold: float = 0.5
) -> str:
    """
    Retrieve relevant context for a query from stored document chunks.

    This is the key function used by the Planner Agent to get syllabus
    context for video planning.

    Args:
        query: The search query (usually the video prompt).
        video_id: The UUID of the video to search within.
        top_k: Maximum number of chunks to return.
        threshold: Minimum similarity threshold (0-1).

    Returns:
        Concatenated context string from relevant chunks.
    """
    from app.services.supabase_client import get_supabase_client

    # Generate embedding for the query
    query_embedding = await generate_embedding(query)

    # Search for similar chunks using RPC function
    client = get_supabase_client()
    result = client.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "target_video_id": str(video_id),
            "match_threshold": threshold,
            "match_count": top_k,
        }
    ).execute()

    if not result.data:
        return ""

    # Concatenate chunks with similarity scores as context
    context_parts = []
    for chunk in result.data:
        similarity = chunk.get("similarity", 0)
        content = chunk.get("content", "")
        context_parts.append(f"[Relevance: {similarity:.2f}]\n{content}")

    return "\n\n---\n\n".join(context_parts)


async def delete_video_chunks(video_id: UUID) -> int:
    """
    Delete all document chunks for a video.

    Args:
        video_id: The UUID of the video.

    Returns:
        Number of chunks deleted.
    """
    from app.services.supabase_client import get_supabase_client

    client = get_supabase_client()
    result = (
        client.table("document_chunks")
        .delete()
        .eq("video_id", str(video_id))
        .execute()
    )

    return len(result.data) if result.data else 0
