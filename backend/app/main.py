"""
FastAPI application entry point.
Agentic AI Educational Video Generation Backend.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import upload, videos, webhooks
from app.config import get_settings

from dotenv import load_dotenv
load_dotenv(".env")

# Get application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Agentic AI Educational Video Generator",
    description="Backend API for AI-powered educational video generation using LangGraph agents",
    version="0.1.0",
)

# Configure CORS middleware
# Filter out empty strings to avoid CORS issues when FRONTEND_URL is not set
allowed_origins = [
    origin for origin in [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        os.environ.get("FRONTEND_URL", ""),  # Production frontend (e.g. https://animed-ai.vercel.app)
    ] if origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(upload.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Initializing blueprint semantic search embeddings...")
    from app.sandbox.stem_blueprint_dataset import registry
    try:
        await registry._initialize_embeddings()
        logger.info("Blueprint embeddings initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize blueprint embeddings: {e}")

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
