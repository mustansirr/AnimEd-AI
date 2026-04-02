# AnimEd AI Backend — Production Dockerfile
# Installs Manim directly (no Docker-in-Docker) for Render deployment

FROM python:3.10-slim

WORKDIR /app

# Install Manim system dependencies directly
# - build-essential: C compiler for pycairo build
# - pkg-config: Library configuration for building native extensions
# - ffmpeg: Video encoding/decoding
# - libcairo2-dev: 2D graphics library for rendering
# - libpango1.0-dev: Text layout and rendering
# - texlive-latex-base + texlive-fonts-recommended: LaTeX math support (~200MB, not the 5GB full install)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    texlive-latex-base \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir manim==0.18.0

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p /tmp/manima-storage

# Expose port (Render injects $PORT)
EXPOSE 8000

# Start the server — use $PORT if provided by platform, default to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
