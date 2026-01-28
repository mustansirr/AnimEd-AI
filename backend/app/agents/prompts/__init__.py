"""
Agent prompts for LLM calls.
"""

from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    create_planner_prompt,
)
from app.agents.prompts.scripter_prompts import (
    SCRIPTER_SYSTEM_PROMPT,
    create_scripter_prompt,
)

__all__ = [
    "PLANNER_SYSTEM_PROMPT",
    "create_planner_prompt",
    "SCRIPTER_SYSTEM_PROMPT",
    "create_scripter_prompt",
]
