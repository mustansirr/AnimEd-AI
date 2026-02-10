# Docker Configuration

This directory contains Docker configuration for the Manim execution sandbox.

## Files

- `Dockerfile.sandbox` - Manim execution container with Python 3.10, FFmpeg, Cairo, and LaTeX
- `docker-compose.yml` - Local development services (Redis, API, sandbox)

## Building the Sandbox

```bash
# From the backend directory
docker build -t manim-sandbox -f docker/Dockerfile.sandbox .
```

## Testing the Sandbox

1. Create a test scene:
   ```bash
   mkdir -p /tmp/manim-test
   cat > /tmp/manim-test/scene.py << 'EOF'
   from manim import *
   class TestScene(Scene):
       def construct(self):
           self.play(Write(Text("Hello Manim!")))
           self.wait(1)
   EOF
   ```

2. Run the container:
   ```bash
   docker run --rm -v /tmp/manim-test:/render manim-sandbox
   ```

3. Check output:
   ```bash
   ls -la /tmp/manim-test/media/videos/scene/480p15/
   # Should contain TestScene.mp4
   ```

## Local Development

```bash
# Start all services (Redis + API)
docker-compose up -d

# Build sandbox image
docker-compose --profile sandbox build
```

## Resource Limits

When running in production, the executor applies these limits:
- Memory: 512MB
- CPU: 1 core
- Network: Disabled (security)
- Timeout: 2 minutes
