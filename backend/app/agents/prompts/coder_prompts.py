"""
DEPRECATED: Manim Generator Prompts (formerly Coder).

This file is no longer used for generation, but clean_code_response is kept 
here for backward compatibility with reflector.py which might still use LLM.
"""

import re

def clean_code_response(response: str) -> str:
    pattern = r"```[ \t]*(?:python|py)?[ \t]*\n(.*?)```"
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if "from manim import" in response:
        code_part = response[response.find("from manim import"):].strip()
        if "```" in code_part:
            code_part = code_part[:code_part.find("```")]
        return code_part.strip()
    return response.strip()
