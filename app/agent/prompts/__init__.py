"""
Prompts used by the claim adjudication agent.
"""

from .system_prompt import SYSTEM_PROMPT
from .adjudication_prompt import ADJUDICATION_PROMPT
from .fraud_prompt import FRAUD_PROMPT

__all__ = [
    "SYSTEM_PROMPT",
    "ADJUDICATION_PROMPT",
    "FRAUD_PROMPT",
]