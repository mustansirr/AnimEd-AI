"""
Sandbox package for Manim code execution.

This package provides isolated Docker-based execution of Manim code
with security constraints and resource limits.
"""

from app.sandbox.executor import ManimExecutor, ExecutionResult

__all__ = ["ManimExecutor", "ExecutionResult"]
