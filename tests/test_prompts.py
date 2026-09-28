"""
Unit Tests: Prompt Engineering System
-------------------------------------
Tests prompt construction, safety constraints, and few-shot/structured templates
without requiring a live API key or external network connection.
"""

import pytest
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


def test_system_prompt_defines_identity():
    """Verifies that the system prompt establishes LunaCare's core identity."""
    assert "LunaCare" in LUNACARE_SYSTEM_INSTRUCTION
    assert "female health" in LUNACARE_SYSTEM_INSTRUCTION.lower()
    assert "educational" in LUNACARE_SYSTEM_INSTRUCTION.lower()


def test_system_prompt_contains_safety_guardrails():
    """Verifies mandatory safety constraints in system instructions."""
    prompt_lower = LUNACARE_SYSTEM_INSTRUCTION.lower()
    
    # 1. Non-diagnostic constraint
    assert "never diagnose" in prompt_lower or "not a medical doctor" in prompt_lower
    
    # 2. Medical referral recommendation
    assert "healthcare provider" in prompt_lower or "doctor" in prompt_lower
    
    # 3. Emergency protocol
    assert "emergency" in prompt_lower


def test_zero_shot_prompt_construction():
    """Verifies zero-shot prompt embeds user query without prior examples."""
    query = "What is normal menstrual cycle length?"
    prompt = build_zero_shot_prompt(query)
    
    assert query in prompt
    assert "Question:" in prompt
    assert "Answer:" in prompt
    # Zero-shot must not contain exemplar demonstrations
    assert "Example 1:" not in prompt


def test_few_shot_prompt_construction():
    """Verifies few-shot prompt includes curated demonstration pairs and user query."""
    query = "What causes fatigue before a period?"
    prompt = build_few_shot_prompt(query)
    
    # Must contain exemplars
    assert len(FEW_SHOT_EXEMPLARS) >= 2
    assert "Example 1:" in prompt
    assert "Example 2:" in prompt
    assert query in prompt
    assert "Assistant:" in prompt


def test_structured_prompt_tags():
    """Verifies structured prompt separates ROLE, TASK, SAFETY RULES, and FORMAT."""
    query = "Explain PCOS symptoms"
    prompt = get_structured_prompt(query)
    
    assert "[ROLE]" in prompt
    assert "[TASK]" in prompt
    assert "[SAFETY RULES]" in prompt
    assert "[RESPONSE FORMAT]" in prompt
    assert query in prompt
