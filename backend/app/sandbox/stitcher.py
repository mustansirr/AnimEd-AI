"""
Video Stitcher - FFmpeg-based video assembly.

This module provides the VideoStitcher class that combines
all rendered scene segments into a final video using FFmpeg.
"""

import asyncio
import logging
import subprocess
from pathlib import Path
from uuid import UUID

import httpx

from app.services import supabase_client
from app.config import get_settings

logger = logging.getLogger(__name__)


class VideoStitcher:
    """
    Combines all scene videos into a final output using FFmpeg.

    Attributes:
        storage_path: Base directory for video storage.
    """

    def __init__(self, storage_path: str = "/app/storage"):
        """
        Initialize the VideoStitcher.

        Args:
            storage_path: Base directory for storing video files.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def download_file(self, url: str, local_path: Path) -> bool:
        """
        Download a file from URL to local path.

        Args:
            url: URL to download from.
            local_path: Local path to save the file.

        Returns:
            True if download was successful.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                local_path.write_bytes(response.content)
                logger.info(f"Downloaded {url} to {local_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False

    def _validate_video_file(self, file_path: Path) -> bool:
        """
        Validate that a downloaded file is actually a video (not an HTML error page).

        Checks file size and magic bytes to ensure it's a valid MP4/video file.
        """
        if not file_path.exists():
            return False

        # Check file size — a valid video should be more than 1KB
        file_size = file_path.stat().st_size
        if file_size < 1024:
            logger.warning(
                f"File too small to be a video ({file_size} bytes): {file_path}"
            )
            return False

        # Check magic bytes — MP4 files have 'ftyp' at offset 4
        # or start with common video signatures
        with open(file_path, "rb") as f:
            header = f.read(12)

        # Check for MP4 'ftyp' box
        if b"ftyp" in header:
            return True

        # Check if it looks like HTML (common when download fails silently)
        if header.startswith(b"<") or header.startswith(b"<!"):
            logger.warning(f"Downloaded file appears to be HTML, not video: {file_path}")
            return False

        # Allow other video formats (might be raw video data)
        logger.info(f"File header bytes: {header[:8].hex()}, assuming valid video")
        return True

    async def stitch_videos(self, video_id: str) -> str:
        """
        Combine all scene videos into a final video.

        Args:
            video_id: UUID of the video record.

        Returns:
            Public URL to the final stitched video.

        Raises:
            RuntimeError: If stitching fails.
        """
        logger.info(f"Starting video stitching for {video_id}")

        # Get all scenes from database
        scenes = await supabase_client.get_scenes(UUID(video_id))

        if not scenes:
            raise RuntimeError(f"No scenes found for video {video_id}")

        # Filter to only rendered scenes with video URLs
        rendered_scenes = [
            s for s in scenes
            if s.is_rendered and s.video_segment_url
        ]

        if not rendered_scenes:
            raise RuntimeError(
                f"No rendered scenes found for video {video_id}"
            )

        logger.info(
            f"Found {len(rendered_scenes)} rendered scenes to stitch"
        )

        # Create work directory
        work_dir = self.storage_path / video_id / "final"
        work_dir.mkdir(parents=True, exist_ok=True)

        # Download all segments and validate
        segment_paths = []
        for scene in sorted(rendered_scenes, key=lambda s: s.scene_order):
            local_path = work_dir / f"scene_{scene.scene_order}.mp4"

            logger.info(
                f"Downloading scene {scene.scene_order} from: "
                f"{scene.video_segment_url}"
            )

            success = await self.download_file(
                scene.video_segment_url,
                local_path,
            )

            if success and self._validate_video_file(local_path):
                file_size = local_path.stat().st_size
                logger.info(
                    f"Scene {scene.scene_order} downloaded OK "
                    f"({file_size} bytes)"
                )
                segment_paths.append(local_path)
            else:
                logger.warning(
                    f"Failed to download/validate scene {scene.scene_order}"
                )

        if not segment_paths:
            raise RuntimeError("No valid video segments could be downloaded")

        logger.info(
            f"Successfully downloaded {len(segment_paths)}/{len(rendered_scenes)} segments"
        )

        # If only one segment, skip concat and upload directly
        if len(segment_paths) == 1:
            logger.info("Only one segment, skipping FFmpeg concat")
            output_path = segment_paths[0]
        else:
            # Create FFmpeg concat file
            concat_file = work_dir / "concat.txt"
            with open(concat_file, "w") as f:
                for path in segment_paths:
                    # Use absolute paths and escape single quotes
                    escaped_path = str(path.absolute()).replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            logger.info(f"Concat file contents:")
            logger.info(concat_file.read_text())

            # Run FFmpeg to concatenate with re-encoding for robustness
            # -c copy only works if all inputs have identical codec params;
            # re-encoding handles different resolutions, framerates, etc.
            output_path = work_dir / "final_video.mp4"
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",    # Re-encode video for compatibility
                "-preset", "fast",     # Balance speed vs compression
                "-crf", "23",          # Quality (lower = better, 23 is default)
                "-c:a", "aac",         # Re-encode audio (if any)
                "-movflags", "+faststart",  # Enable streaming playback
                str(output_path),
            ]

            logger.info(f"Running FFmpeg: {' '.join(ffmpeg_cmd)}")

            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: subprocess.run(
                        ffmpeg_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minute timeout
                    ),
                )

                logger.info(f"FFmpeg stdout: {result.stdout[-500:] if result.stdout else '(empty)'}")
                logger.info(f"FFmpeg stderr (last 1000 chars): {result.stderr[-1000:] if result.stderr else '(empty)'}")

                if result.returncode != 0:
                    logger.error(f"FFmpeg failed with code {result.returncode}: {result.stderr}")
                    raise RuntimeError(f"FFmpeg failed: {result.stderr[-500:]}")

            except subprocess.TimeoutExpired:
                raise RuntimeError("FFmpeg timed out after 5 minutes")

        if not output_path.exists():
            raise RuntimeError("FFmpeg did not produce output file")

        output_size = output_path.stat().st_size
        logger.info(
            f"FFmpeg stitching complete: {output_path} ({output_size} bytes)"
        )

        # Upload final video to Supabase Storage
        final_url = await self._upload_final_video(output_path, video_id)

        # Update database with final URL
        await supabase_client.set_final_video_url(UUID(video_id), final_url)

        logger.info(f"Video stitching complete: {final_url}")

        return final_url

    async def _upload_final_video(
        self,
        local_path: Path,
        video_id: str,
    ) -> str:
        """
        Upload the final video to Supabase Storage.

        Args:
            local_path: Path to the local video file.
            video_id: UUID of the video record.

        Returns:
            Public URL to the uploaded video.
        """
        client = supabase_client.get_supabase_client()
        settings = get_settings()

        file_content = local_path.read_bytes()
        storage_path = f"videos/{video_id}/final.mp4"
        bucket_name = getattr(settings, "storage_bucket", "video-segments")

        try:
            client.storage.from_(bucket_name).upload(
                storage_path,
                file_content,
                file_options={"content-type": "video/mp4"},
            )
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                client.storage.from_(bucket_name).update(
                    storage_path,
                    file_content,
                    file_options={"content-type": "video/mp4"},
                )
            else:
                raise

        public_url = client.storage.from_(bucket_name).get_public_url(
            storage_path
        )

        return public_url


async def finalize_video(state: dict) -> dict:
    """
    LangGraph node to finalize video by stitching all scenes.

    Called when all_scenes_done is True in the workflow.

    Args:
        state: Current agent state.

    Returns:
        Updated state with final_video_url.
    """
    video_id = state["video_id"]

    logger.info(f"Finalizing video {video_id}")

    try:
        settings = get_settings()
        storage_path = getattr(settings, "storage_path", "/app/storage")
        stitcher = VideoStitcher(storage_path=storage_path)
        final_url = await stitcher.stitch_videos(video_id)

        return {
            **state,
            "final_video_url": final_url,
        }

    except Exception as e:
        logger.exception(f"Failed to finalize video {video_id}: {e}")
        return {
            **state,
            "final_video_url": None,
            "last_render_error": f"Stitching failed: {str(e)}",
        }
