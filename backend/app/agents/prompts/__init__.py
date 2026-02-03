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
from app.agents.prompts.coder_prompts import (
    CODER_SYSTEM_PROMPT,
    create_coder_prompt,
    get_few_shot_examples,
    clean_code_response,
)

__all__ = [
    "PLANNER_SYSTEM_PROMPT",
    "create_planner_prompt",
    "SCRIPTER_SYSTEM_PROMPT",
    "create_scripter_prompt",
    "CODER_SYSTEM_PROMPT",
    "create_coder_prompt",
    "get_few_shot_examples",
    "clean_code_response",
]

