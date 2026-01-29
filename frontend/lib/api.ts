/**
 * API client for backend communication.
 * Handles video generation and PDF upload endpoints.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// =============================================================================
// Types
// =============================================================================

export interface CreateVideoRequest {
  prompt: string;
  syllabus_doc_path?: string;
}

export interface CreateVideoResponse {
  video_id: string;
  status: string;
  message: string;
}

export interface UploadPdfResponse {
  video_id: string;
  chunks_stored: number;
  message: string;
}

export interface VideoStatusResponse {
  id: string;
  user_id: string;
  prompt: string;
  status: string;
  created_at: string;
  final_video_url?: string;
}

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Create a new video generation request.
 * This triggers the LangGraph workflow for planning and script generation.
 */
export async function createVideo(
  prompt: string,
  userId: string,
  syllabusDocPath?: string
): Promise<CreateVideoResponse> {
  const url = new URL(`${API_BASE_URL}/api/videos`);
  url.searchParams.set("user_id", userId);

  const response = await fetch(url.toString(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      syllabus_doc_path: syllabusDocPath,
    } as CreateVideoRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to create video");
  }

  return response.json();
}

/**
 * Upload a PDF file for RAG context.
 * The PDF is parsed, chunked, and stored as embeddings.
 */
export async function uploadPdf(
  file: File,
  videoId: string
): Promise<UploadPdfResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("video_id", videoId);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to upload PDF");
  }

  return response.json();
}

/**
 * Get the current status of a video request.
 */
export async function getVideoStatus(videoId: string): Promise<VideoStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to get video status");
  }

  return response.json();
}
