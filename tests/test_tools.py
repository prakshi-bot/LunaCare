"""
Unit Tests: Menstrual Cycle Calculator Tool & Agent Layer (Phase 5)
-------------------------------------------------------------------
Tests the LangChain Menstrual Cycle Calculator tool locally and deterministically
without requiring external network requests or live Gemini API quota.
Verifies date arithmetic, calendar-method fertile window formulas, input validation,
non-diagnostic disclaimers, and Agent orchestration.
"""

from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pytest

from config import DEFAULT_CYCLE_LENGTH, MIN_CYCLE_LENGTH, MAX_CYCLE_LENGTH
from tools.cycle_calculator import (
    calculate_menstrual_cycle,
    compute_cycle_projections,
    parse_date_input,
    CycleCalculatorInput,
    CALCULATOR_DISCLAIMER,
)
from services.agent_service import (
    agent_service,
    detect_calculation_intent,
    extract_cycle_parameters,
)


# ==========================================
# 1. LangChain Tool Metadata Tests
# ==========================================

def test_langchain_tool_metadata():
    """Verifies that calculate_menstrual_cycle is a genuine LangChain tool."""
    assert calculate_menstrual_cycle.name == "calculate_menstrual_cycle"
    assert "menstrual cycle" in calculate_menstrual_cycle.description.lower()
    assert calculate_menstrual_cycle.args_schema is CycleCalculatorInput

    # Verify JSON Schema properties
    schema = calculate_menstrual_cycle.args_schema.model_json_schema()
    assert "last_period_date" in schema["properties"]
    assert "cycle_length_days" in schema["properties"]
    assert "last_period_date" in schema["required"]


# ==========================================
# 2. Deterministic Calculation Tests (March 1, 2026 + 28 days)
# ==========================================

def test_standard_28_day_cycle_calculation():
    """
    Verifies calculation for:
    last period = March 1, 2026, cycle length = 28
    Expected:
    - next period = March 29, 2026
    - estimated ovulation = March 15, 2026
    - estimated fertile window = March 10–15, 2026
    """
    projections = compute_cycle_projections(
        last_period_date="March 1, 2026",
        cycle_length_days=28,
    )

    # Date arithmetic
    assert projections["last_period_date"] == date(2026, 3, 1)
    assert projections["next_period_date"] == date(2026, 3, 29)
    assert projections["estimated_ovulation_date"] == date(2026, 3, 15)
    assert projections["fertile_window_start"] == date(2026, 3, 10)
    assert projections["fertile_window_end"] == date(2026, 3, 15)

    # Formatted strings
    assert projections["formatted_next_period"] == "March 29, 2026"
    assert projections["formatted_ovulation"] == "March 15, 2026"
    assert "March 10" in projections["formatted_fertile_window"]
    assert "15, 2026" in projections["formatted_fertile_window"]


def test_custom_cycle_lengths():
    """Verifies non-standard cycle lengths (e.g. 32 days, 24 days)."""
    # 32-day cycle: Next period is March 1 + 32 days = April 2, 2026.
    # Ovulation is April 2 - 14 days = March 19, 2026.
    # Fertile window: March 14 - March 19, 2026.
    proj_32 = compute_cycle_projections("2026-03-01", 32)
    assert proj_32["next_period_date"] == date(2026, 4, 2)
    assert proj_32["estimated_ovulation_date"] == date(2026, 3, 19)
    assert proj_32["fertile_window_start"] == date(2026, 3, 14)
    assert proj_32["fertile_window_end"] == date(2026, 3, 19)

    # 24-day cycle: Next period is March 1 + 24 days = March 25, 2026.
    # Ovulation is March 25 - 14 days = March 11, 2026.
    # Fertile window: March 6 - March 11, 2026.
    proj_24 = compute_cycle_projections("2026-03-01", 24)
    assert proj_24["next_period_date"] == date(2026, 3, 25)
    assert proj_24["estimated_ovulation_date"] == date(2026, 3, 11)
    assert proj_24["fertile_window_start"] == date(2026, 3, 6)
    assert proj_24["fertile_window_end"] == date(2026, 3, 11)


# ==========================================
# 3. Date Format & Parsing Tests
# ==========================================

def test_robust_date_format_parsing():
    """Verifies that multiple date representations parse to the exact same calendar date."""
    target_date = date(2026, 3, 1)
    formats = [
        "2026-03-01",
        "03/01/2026",
        "3/1/2026",
        "March 1, 2026",
        "March 1 2026",
        "1 March 2026",
        date(2026, 3, 1),
    ]
    for fmt in formats:
        parsed = parse_date_input(fmt)
        assert parsed == target_date, f"Failed for format: {fmt}"


def test_invalid_date_error_handling():
    """Verifies that unparseable date strings raise clear ValueErrors."""
    with pytest.raises(ValueError, match="Please provide a valid date"):
        parse_date_input("")

    with pytest.raises(ValueError, match="Could not understand the date"):
        parse_date_input("not-a-valid-date-string-12345")


# ==========================================
# 4. Application Constraints Validation
# ==========================================

def test_cycle_length_application_constraints():
    """Verifies cycle length validation against application constraints (20 to 45 days)."""
    # Below minimum application constraint (20)
    with pytest.raises(ValueError, match="outside the supported application range"):
        compute_cycle_projections("2026-03-01", 18)

    # Above maximum application constraint (45)
    with pytest.raises(ValueError, match="outside the supported application range"):
        compute_cycle_projections("2026-03-01", 50)

    # Non-integer cycle length
    with pytest.raises(ValueError, match="must be an integer"):
        compute_cycle_projections("2026-03-01", "invalid_length")


# ==========================================
# 5. Non-Diagnostic Safety & Disclaimer Tests
# ==========================================

def test_non_diagnostic_safety_disclaimer():
    """Verifies that calculations contain explicit non-diagnostic disclaimers."""
    projections = compute_cycle_projections("2026-03-01", 28)
    disclaimer = projections["disclaimer"]

    assert "calendar-based estimates" in disclaimer
    assert "not guarantees" in disclaimer
    assert "not be used as a method of contraception" in disclaimer
    assert "fertility diagnosis" in disclaimer


# ==========================================
# 6. Direct LangChain Tool Invocation Test
# ==========================================

def test_langchain_tool_invoke_standard():
    """Verifies invoking the LangChain tool via .invoke({...})."""
    output = calculate_menstrual_cycle.invoke({
        "last_period_date": "March 1, 2026",
        "cycle_length_days": 28,
    })

    assert isinstance(output, str)
    assert "March 29, 2026" in output
    assert "March 15, 2026" in output
    assert "March 10" in output
    assert "15, 2026" in output
    assert "calendar-based estimates" in output


# ==========================================
# 7. Agent Intent Detection & Orchestration Tests
# ==========================================

def test_agent_intent_detection():
    """Verifies calculation intent detection."""
    assert detect_calculation_intent("When is my next period?") is True
    assert detect_calculation_intent("Calculate my ovulation date") is True
    assert detect_calculation_intent("Estimate fertile window for my cycle") is True
    assert detect_calculation_intent("What causes menstrual cramps?") is False
    assert detect_calculation_intent("What are symptoms of PCOS?") is False


def test_agent_parameter_extraction():
    """Verifies extracting date and cycle length from query strings."""
    date_str, cycle_len = extract_cycle_parameters(
        "My last period was on March 1, 2026 and my cycle is 30 days"
    )
    assert date_str == "March 1, 2026"
    assert cycle_len == 30

    date_iso, cycle_default = extract_cycle_parameters(
        "Last period started 2026-03-01"
    )
    assert date_iso == "2026-03-01"
    assert cycle_default == 28


def test_agent_missing_parameters_prompts_user():
    """Verifies that asking for a calculation without dates prompts the user for details."""
    response = agent_service.process_query("Can you calculate my next period?")
    assert "start date of your last period" in response.lower()
    assert "cycle length" in response.lower()


def test_agent_executes_tool_locally_without_gemini_math():
    """Verifies that the agent executes the LangChain tool locally without calling Gemini for math."""
    query = "My last period was March 1, 2026 and my cycle is 28 days. When is my next period and ovulation?"
    response = agent_service.process_query(query)

    # Verified deterministic numbers from tool
    assert "March 29, 2026" in response
    assert "March 15, 2026" in response
    assert "March 10" in response
    assert "calendar-based estimates" in response


@patch("services.agent_service.retrieve_relevant_documents")
@patch("services.agent_service.generate_response")
def test_agent_non_calculation_routes_to_rag_and_gemini(mock_generate, mock_retrieve):
    """Verifies that non-calculation queries route to RAG and Gemini generation as in Phase 3/4."""
    mock_retrieve.return_value = {
        "query": "What causes menstrual cramps?",
        "is_sufficient": True,
        "best_distance": 0.55,
        "documents": [],
        "distances": [],
    }
    mock_generate.return_value = "Empathetic educational explanation of menstrual cramps."

    query = "What causes menstrual cramps?"
    history = [{"role": "user", "content": "Hello"}]
    response = agent_service.process_query(query, conversation_history=history)

    assert "menstrual cramps" in response
    mock_retrieve.assert_called_once_with(query)
    mock_generate.assert_called_once()
