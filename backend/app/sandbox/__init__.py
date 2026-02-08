"""
Sandbox package for Manim code execution.

This package provides isolated Docker-based execution of Manim code
with security constraints and resource limits.
"""

from app.sandbox.executor import ManimExecutor, ExecutionResult
from app.sandbox.renderer import execute_and_check
from app.sandbox.stitcher import VideoStitcher, finalize_video

__all__ = [
    "ManimExecutor",
    "ExecutionResult",
    "execute_and_check",
    "VideoStitcher",
    "finalize_video",
]
