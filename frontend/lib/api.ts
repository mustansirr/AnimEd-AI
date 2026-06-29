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
 * Start the video generation workflow.
 * Call this AFTER uploading any PDF context so the planner
 * can use the RAG embeddings.
 */
export async function startWorkflow(
  videoId: string
): Promise<CreateVideoResponse> {
  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to start workflow");
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

/**
 * Scene data from the backend.
 */
export interface SceneResponse {
  id: string;
  video_id: string;
  scene_order: number;
  narration_script: string | null;
  visual_plan: string | null;
  manim_code: string | null;
  is_rendered: boolean;
  error_log: string | null;
  video_segment_url: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Get all scenes for a video.
 */
export async function getScenes(videoId: string): Promise<SceneResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/scenes`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to get scenes");
  }

  return response.json();
}

/**
 * Response from script approval endpoint.
 */
export interface ApprovalResponse {
  video_id: string;
  status: string;
  message: string;
  feedback?: string;
}

/**
 * Approve or reject scripts for a video.
 */
export async function approveScripts(
  videoId: string,
  approved: boolean,
  feedback?: string
): Promise<ApprovalResponse> {
  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      approved,
      feedback,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to submit approval");
  }

  return response.json();
}

/**
 * List all videos for a user.
 */
export async function listUserVideos(userId: string): Promise<VideoStatusResponse[]> {
  const url = new URL(`${API_BASE_URL}/api/videos`);
  url.searchParams.set("user_id", userId);

  const response = await fetch(url.toString());

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to list videos");
  }

  return response.json();
}

/**
 * Delete a video and all its associated scenes.
 */
export async function deleteVideo(videoId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to delete video");
  }
}

/**
 * Send a chat message to ask questions about a video.
 */
export async function sendChatMessage(
  videoId: string,
  userId: string,
  message: string
): Promise<{ answer: string }> {
  const url = new URL(`${API_BASE_URL}/api/videos/${videoId}/chat`);
  url.searchParams.set("user_id", userId);

  const response = await fetch(url.toString(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to send message");
  }

  return response.json();
}

// =============================================================================
// Flashcards API
// =============================================================================

export interface FlashcardDeck {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  created_at: string;
}

export interface Flashcard {
  id: string;
  deck_id: string;
  user_id: string;
  front: string;
  back: string;
  next_review_date: string;
  interval: number;
  ease_factor: number;
  repetitions: number;
}

export async function getDecks(userId: string): Promise<FlashcardDeck[]> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString());
  if (!response.ok) throw new Error("Failed to fetch decks");
  return response.json();
}

export async function createDeck(userId: string, title: string, description?: string): Promise<FlashcardDeck> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description })
  });
  if (!response.ok) throw new Error("Failed to create deck");
  return response.json();
}

export async function updateDeck(userId: string, deckId: string, title: string, description?: string): Promise<FlashcardDeck> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks/${deckId}`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description })
  });
  if (!response.ok) throw new Error("Failed to update deck");
  return response.json();
}

export async function deleteDeck(userId: string, deckId: string): Promise<void> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks/${deckId}`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "DELETE"
  });
  if (!response.ok) throw new Error("Failed to delete deck");
}

export async function getDeckCards(deckId: string): Promise<Flashcard[]> {
  const response = await fetch(`${API_BASE_URL}/api/flashcards/decks/${deckId}/cards`);
  if (!response.ok) throw new Error("Failed to fetch cards");
  return response.json();
}

export async function createCard(userId: string, deckId: string, front: string, back: string): Promise<Flashcard> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks/${deckId}/cards`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ front, back })
  });
  if (!response.ok) throw new Error("Failed to create card");
  return response.json();
}

export async function reviewCard(cardId: string, rating: number): Promise<Flashcard> {
  const response = await fetch(`${API_BASE_URL}/api/flashcards/${cardId}/review`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating })
  });
  if (!response.ok) throw new Error("Failed to review card");
  return response.json();
}

export async function generateCards(userId: string, deckId: string, topic: string, count: number = 5): Promise<Flashcard[]> {
  const url = new URL(`${API_BASE_URL}/api/flashcards/decks/${deckId}/generate`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, count })
  });
  if (!response.ok) throw new Error("Failed to generate cards");
  return response.json();
}

// ============================================================================
// Quizzes API
// ============================================================================

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation?: string;
  user_answer_index?: number;
  created_at: string;
}

export interface Quiz {
  id: string;
  user_id: string;
  title: string;
  topic: string;
  difficulty: string;
  score: number | null;
  total_questions: number;
  created_at: string;
  questions?: QuizQuestion[];
}

export async function getQuizzes(userId: string): Promise<Quiz[]> {
  const url = new URL(`${API_BASE_URL}/api/quizzes`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString());
  if (!response.ok) throw new Error("Failed to fetch quizzes");
  return response.json();
}

export async function generateQuiz(userId: string, topic: string, count: number, difficulty: string): Promise<Quiz> {
  const url = new URL(`${API_BASE_URL}/api/quizzes/generate`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, count, difficulty })
  });
  if (!response.ok) throw new Error("Failed to generate quiz");
  return response.json();
}

export async function getQuizById(userId: string, quizId: string): Promise<Quiz> {
  const url = new URL(`${API_BASE_URL}/api/quizzes/${quizId}`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString());
  if (!response.ok) throw new Error("Failed to fetch quiz");
  return response.json();
}

export async function submitQuiz(userId: string, quizId: string, answers: Record<string, number>): Promise<Quiz> {
  const url = new URL(`${API_BASE_URL}/api/quizzes/${quizId}/submit`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers })
  });
  if (!response.ok) throw new Error("Failed to submit quiz");
  return response.json();
}

export async function deleteQuiz(userId: string, quizId: string): Promise<void> {
  const url = new URL(`${API_BASE_URL}/api/quizzes/${quizId}`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "DELETE"
  });
  if (!response.ok) throw new Error("Failed to delete quiz");
}

export async function retakeQuiz(userId: string, quizId: string): Promise<Quiz> {
  const url = new URL(`${API_BASE_URL}/api/quizzes/${quizId}/retake`);
  url.searchParams.set("user_id", userId);
  const response = await fetch(url.toString(), {
    method: "POST"
  });
  if (!response.ok) throw new Error("Failed to reset quiz");
  return response.json();
}
