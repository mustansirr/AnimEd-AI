"""
Quick script to re-trigger video stitching for a specific video ID.
Usage: source venv/bin/activate && python scripts/restitch.py <video_id>
"""
import asyncio
import importlib.util
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load stitcher.py directly from file to avoid the circular import in __init__.py
spec = importlib.util.spec_from_file_location(
    "stitcher",
    os.path.join(backend_dir, "app", "sandbox", "stitcher.py"),
    submodule_search_locations=[]
)
stitcher_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stitcher_mod)

VideoStitcher = stitcher_mod.VideoStitcher


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/restitch.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    print(f"Re-stitching video: {video_id}")

    from app.config import get_settings
    settings = get_settings()
    storage_path = getattr(settings, "storage_path", "/app/storage")
    stitcher = VideoStitcher(storage_path=storage_path)

    try:
        final_url = await stitcher.stitch_videos(video_id)
        print(f"✅ Success! Final video URL: {final_url}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
