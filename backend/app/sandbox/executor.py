"""
Manim Executor - Docker sandbox for running Manim code.

This module provides the ManimExecutor class that executes Manim code
in an isolated Docker container with resource limits and security constraints.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


class ExecutionResult(TypedDict):
    """Result of a Manim code execution."""

    success: bool
    video_path: str | None
    error: str | None
    stdout: str


class ManimExecutor:
    """
    Executes Manim code in a Docker sandbox.

    The executor provides a secure, isolated environment for running
    untrusted Manim code with resource limits and network isolation.

    Attributes:
        storage_path: Base directory for render output storage.
        docker_image: Name of the Docker image to use.
        timeout_seconds: Maximum execution time per render.
    """

    def __init__(
        self,
        storage_path: str = "/app/storage",
        docker_image: str = "manim-sandbox",
        timeout_seconds: int = 120,
    ):
        """
        Initialize the ManimExecutor.

        Args:
            storage_path: Base directory for storing render outputs.
            docker_image: Docker image name for the Manim sandbox.
            timeout_seconds: Maximum time allowed for a render.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.docker_image = docker_image
        self.timeout_seconds = timeout_seconds

    async def execute(
        self,
        code: str,
        video_id: str,
        scene_index: int,
    ) -> ExecutionResult:
        """
        Execute Manim code in a Docker sandbox.

        Args:
            code: Python/Manim code to execute.
            video_id: UUID of the video record.
            scene_index: Index of the scene being rendered.

        Returns:
            ExecutionResult with success status, video path or error.
        """
        render_dir = self.storage_path / video_id / f"scene_{scene_index}"
        render_dir.mkdir(parents=True, exist_ok=True)

        # Write code to scene.py
        code_file = render_dir / "scene.py"
        code_file.write_text(code)

        logger.info(
            f"Executing Manim code for video {video_id}, "
            f"scene {scene_index}"
        )

        # Build Docker command with security constraints
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{render_dir.absolute()}:/render",
            "--memory=512m",      # Limit memory to 512MB
            "--cpus=1",           # Limit to 1 CPU core
            "--network=none",     # No network access (security)
            self.docker_image,
        ]

        try:
            # Run in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                ),
            )

            if result.returncode == 0:
                # Find the output video file
                video_files = list(
                    (render_dir / "media" / "videos").rglob("*.mp4")
                )
                if video_files:
                    video_path = str(video_files[0])
                    logger.info(
                        f"Render successful: {video_path}"
                    )
                    return ExecutionResult(
                        success=True,
                        video_path=video_path,
                        error=None,
                        stdout=result.stdout,
                    )
                else:
                    logger.warning(
                        f"Render completed but no video found "
                        f"for video {video_id}"
                    )
                    return ExecutionResult(
                        success=False,
                        video_path=None,
                        error="No video file generated",
                        stdout=result.stdout,
                    )

            else:
                logger.error(
                    f"Render failed for video {video_id}: {result.stderr}"
                )
                return ExecutionResult(
                    success=False,
                    video_path=None,
                    error=result.stderr,
                    stdout=result.stdout,
                )

        except subprocess.TimeoutExpired:
            logger.error(
                f"Render timed out for video {video_id}, "
                f"scene {scene_index}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error=f"Execution timed out after {self.timeout_seconds}s",
                stdout="",
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error during render for video {video_id}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error=str(e),
                stdout="",
            )

    def get_render_directory(
        self,
        video_id: str,
        scene_index: int,
    ) -> Path:
        """Get the render directory path for a specific scene."""
        return self.storage_path / video_id / f"scene_{scene_index}"

    def cleanup_render(self, video_id: str) -> None:
        """
        Clean up all render artifacts for a video.

        Args:
            video_id: UUID of the video to clean up.
        """
        import shutil

        video_dir = self.storage_path / video_id
        if video_dir.exists():
            shutil.rmtree(video_dir)
            logger.info(f"Cleaned up render directory for video {video_id}")
