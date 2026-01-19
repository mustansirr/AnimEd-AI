"""
FastAPI application entry point.
Agentic AI Educational Video Generation Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

# Get application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Agentic AI Educational Video Generator",
    description="Backend API for AI-powered educational video generation using LangGraph agents",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Include API routers (Phase 4)
# from app.api.routes import videos, upload, webhooks
# app.include_router(videos.router, prefix="/api", tags=["videos"])
# app.include_router(upload.router, prefix="/api", tags=["upload"])
# app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])


@app.get("/")
def read_root():
    """Root endpoint returning welcome message."""
    return {"message": "Agentic AI Educational Video Generator API"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "supabase_configured": settings.is_supabase_configured,
        "llm_configured": settings.is_llm_configured,
    }
