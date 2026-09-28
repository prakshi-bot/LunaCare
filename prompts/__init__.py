"""
LunaCare Prompts Package
------------------------
Exports core system instructions, structured prompts, and prompt engineering utilities.
"""

from prompts.system_prompt import (
    LUNACARE_SYSTEM_INSTRUCTION,
    get_structured_prompt,
)
from prompts.prompt_examples import (
    build_zero_shot_prompt,
    build_few_shot_prompt,
    build_role_prompt,
    FEW_SHOT_EXEMPLARS,
)

__all__ = [
    "LUNACARE_SYSTEM_INSTRUCTION",
    "get_structured_prompt",
    "build_zero_shot_prompt",
    "build_few_shot_prompt",
    "build_role_prompt",
    "FEW_SHOT_EXEMPLARS",
]
