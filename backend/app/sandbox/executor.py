"""
Manim Executor - Runs Manim as a subprocess or in a Docker sandbox.

Supports two modes:
- "subprocess": Runs Manim directly as a local subprocess (for deployed environments
  where Manim is installed in the same container, e.g. Render).
- "docker": Runs Manim in an isolated Docker container (for local development with
  Docker-in-Docker support).

The mode is controlled by the MANIM_EXECUTION_MODE environment variable.
Default is "docker" for backwards compatibility with local dev.
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)

# Determine execution mode from environment variable
EXECUTION_MODE = os.environ.get("MANIM_EXECUTION_MODE", "docker").lower()


class ExecutionResult(TypedDict):
    """Result of a Manim code execution."""

    success: bool
    video_path: str | None
    error: str | None
    stdout: str


class ManimExecutor:
    """
    Executes Manim code either as a subprocess or in a Docker sandbox.

    The executor provides an environment for running Manim code with
    resource limits and (in Docker mode) security constraints.

    Attributes:
        storage_path: Base directory for render output storage.
        docker_image: Name of the Docker image to use (Docker mode only).
        timeout_seconds: Maximum execution time per render.
        execution_mode: "subprocess" or "docker".
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
        self.execution_mode = EXECUTION_MODE

        logger.info(f"ManimExecutor initialized in '{self.execution_mode}' mode")

    async def execute(
        self,
        code: str,
        video_id: str,
        scene_index: int,
    ) -> ExecutionResult:
        """
        Execute Manim code.

        Routes to either subprocess or Docker execution based on the
        configured execution mode.

        Args:
            code: Python/Manim code to execute.
            video_id: UUID of the video record.
            scene_index: Index of the scene being rendered.

        Returns:
            ExecutionResult with success status, video path or error.
        """
        if self.execution_mode == "subprocess":
            return await self._execute_subprocess(code, video_id, scene_index)
        else:
            return await self._execute_docker(code, video_id, scene_index)

    async def _execute_subprocess(
        self,
        code: str,
        video_id: str,
        scene_index: int,
    ) -> ExecutionResult:
        """
        Execute Manim code as a local subprocess.

        Used in deployed environments (e.g. Render) where Manim is installed
        directly in the container. No Docker-in-Docker required.
        """
        render_dir = self.storage_path / video_id / f"scene_{scene_index}"
        render_dir.mkdir(parents=True, exist_ok=True)

        # Write code to scene.py
        code_file = render_dir / "scene.py"
        code_file.write_text(code)

        logger.info(
            f"Executing Manim (subprocess) for video {video_id}, "
            f"scene {scene_index}"
        )

        # Build Manim command: render at low quality (480p15) for speed
        # --media_dir ensures output goes to our render directory
        manim_cmd = [
            "manim", "render", "-ql",
            "--media_dir", str(render_dir / "media"),
            str(code_file),
        ]

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    manim_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                ),
            )

            if result.returncode == 0:
                return self._find_video_result(render_dir, video_id, result.stdout)
            else:
                logger.error(
                    f"Render failed (subprocess) for video {video_id}: {result.stderr}"
                )
                return ExecutionResult(
                    success=False,
                    video_path=None,
                    error=result.stderr,
                    stdout=result.stdout,
                )

        except subprocess.TimeoutExpired:
            logger.error(
                f"Render timed out for video {video_id}, scene {scene_index}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error=f"Execution timed out after {self.timeout_seconds}s",
                stdout="",
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error during subprocess render for video {video_id}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error=str(e),
                stdout="",
            )

    async def _execute_docker(
        self,
        code: str,
        video_id: str,
        scene_index: int,
    ) -> ExecutionResult:
        """
        Execute Manim code in a Docker sandbox.

        Used in local development where Docker is available. Provides
        security isolation via resource limits and network isolation.
        """
        render_dir = self.storage_path / video_id / f"scene_{scene_index}"
        render_dir.mkdir(parents=True, exist_ok=True)

        # Write code to scene.py
        code_file = render_dir / "scene.py"
        code_file.write_text(code)

        logger.info(
            f"Executing Manim (docker) for video {video_id}, "
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
                return self._find_video_result(render_dir, video_id, result.stdout)
            else:
                logger.error(
                    f"Render failed (docker) for video {video_id}: {result.stderr}"
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
                f"Unexpected error during docker render for video {video_id}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error=str(e),
                stdout="",
            )

    def _find_video_result(
        self,
        render_dir: Path,
        video_id: str,
        stdout: str,
    ) -> ExecutionResult:
        """Find the rendered video file and return the result."""
        video_files = list(
            (render_dir / "media" / "videos").rglob("*.mp4")
        )
        if video_files:
            video_path = str(video_files[0])
            logger.info(f"Render successful: {video_path}")
            return ExecutionResult(
                success=True,
                video_path=video_path,
                error=None,
                stdout=stdout,
            )
        else:
            logger.warning(
                f"Render completed but no video found for video {video_id}"
            )
            return ExecutionResult(
                success=False,
                video_path=None,
                error="No video file generated",
                stdout=stdout,
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
