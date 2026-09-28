"""
LunaCare: Menstrual Cycle Calculator Tool
-----------------------------------------
Demonstrates Week 5 Syllabus Concepts:
- Deterministic Tool Execution: Performs exact calendar and arithmetic calculations locally
  in Python rather than asking an LLM to generate approximate math.
- LangChain Tool Interface: Uses @tool from langchain_core.tools with a structured Pydantic
  input schema for seamless agent binding.
- Safety & Non-Diagnostic Guardrails: Clearly labels results as calendar-based estimates,
  reinforces that individual cycles naturally fluctuate, and explicitly warns that calculations
  are not a method of contraception or fertility diagnosis.
"""

from datetime import date, timedelta
from typing import Dict, Any, Union
import dateutil.parser
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from config import DEFAULT_CYCLE_LENGTH, MIN_CYCLE_LENGTH, MAX_CYCLE_LENGTH

# Non-diagnostic educational disclaimer attached to all calculation outputs
CALCULATOR_DISCLAIMER = (
    "Please note: These calculations are calendar-based estimates based on typical cycle averages "
    "(assuming an approximate 14-day luteal phase) and are not guarantees. Menstrual cycles naturally "
    "fluctuate due to stress, hormonal shifts, sleep, and lifestyle factors. This tool is designed "
    "for educational awareness and self-knowledge only; it must not be used as a method of contraception "
    "or clinical fertility diagnosis."
)


def parse_date_input(date_val: Union[str, date]) -> date:
    """
    Robustly parses a date input into a datetime.date object.
    Supports datetime.date instances, ISO strings ('2026-03-01'),
    slash/dash formats ('03/01/2026'), and natural text ('March 1, 2026').
    """
    if isinstance(date_val, date):
        return date_val

    if not isinstance(date_val, str) or not date_val.strip():
        raise ValueError("Please provide a valid date for the start of your last period.")

    clean_str = date_val.strip()
    try:
        parsed_dt = dateutil.parser.parse(clean_str, fuzzy=True)
        return parsed_dt.date()
    except (ValueError, OverflowError, TypeError) as err:
        raise ValueError(
            f"Could not understand the date '{clean_str}'. "
            "Please use a format like 'YYYY-MM-DD', 'MM/DD/YYYY', or 'March 1, 2026'."
        ) from err


def compute_cycle_projections(
    last_period_date: Union[str, date],
    cycle_length_days: int = DEFAULT_CYCLE_LENGTH,
) -> Dict[str, Any]:
    """
    Pure deterministic calculation function for menstrual cycle projections.
    Shared between the UI cycle calculator (pages_content/cycle.py) and
    the LangChain tool (calculate_menstrual_cycle).

    Formula Rules (Calendar Method):
    - Next Period = last_period_date + cycle_length_days
    - Estimated Ovulation = next_period - 14 days
    - Fertile Window Start = estimated_ovulation - 5 days
    - Fertile Window End = estimated_ovulation
      (Represents the 6-day interval ending on the estimated ovulation day)

    Args:
        last_period_date: Date of first day of last menstrual period.
        cycle_length_days: Average cycle length in days (default: 28).

    Returns:
        Dict containing raw date objects, formatted strings, and safety disclaimer.
    """
    parsed_last_date = parse_date_input(last_period_date)

    try:
        cycle_length = int(cycle_length_days)
    except (ValueError, TypeError) as err:
        raise ValueError(f"Cycle length must be an integer number of days, got '{cycle_length_days}'.") from err

    # Validate against application input constraints (not a medical absolute)
    if cycle_length < MIN_CYCLE_LENGTH or cycle_length > MAX_CYCLE_LENGTH:
        raise ValueError(
            f"Cycle length ({cycle_length} days) is outside the supported application range "
            f"({MIN_CYCLE_LENGTH} to {MAX_CYCLE_LENGTH} days). Please check your input."
        )

    # 1. Next Period Date
    next_period = parsed_last_date + timedelta(days=cycle_length)

    # 2. Estimated Ovulation Date (approx 14 days before next period)
    estimated_ovulation = next_period - timedelta(days=14)

    # 3. Standard Calendar-Method Fertile Window (6-day interval ending on ovulation)
    fertile_window_start = estimated_ovulation - timedelta(days=5)
    fertile_window_end = estimated_ovulation

    return {
        "last_period_date": parsed_last_date,
        "cycle_length_days": cycle_length,
        "next_period_date": next_period,
        "estimated_ovulation_date": estimated_ovulation,
        "fertile_window_start": fertile_window_start,
        "fertile_window_end": fertile_window_end,
        "formatted_last_period": f"{parsed_last_date.strftime('%B')} {parsed_last_date.day}, {parsed_last_date.year}",
        "formatted_next_period": f"{next_period.strftime('%B')} {next_period.day}, {next_period.year}",
        "formatted_ovulation": f"{estimated_ovulation.strftime('%B')} {estimated_ovulation.day}, {estimated_ovulation.year}",
        "formatted_fertile_window": (
            f"{fertile_window_start.strftime('%B')} {fertile_window_start.day}–{fertile_window_end.day}, {fertile_window_end.year}"
            if fertile_window_start.month == fertile_window_end.month
            else f"{fertile_window_start.strftime('%B')} {fertile_window_start.day} – {fertile_window_end.strftime('%B')} {fertile_window_end.day}, {fertile_window_end.year}"
        ),
        "disclaimer": CALCULATOR_DISCLAIMER,
    }


class CycleCalculatorInput(BaseModel):
    """Input schema for the LangChain Menstrual Cycle Calculator tool."""

    last_period_date: str = Field(
        ...,
        description=(
            "The start date of the user's last menstrual period (e.g., '2026-03-01', 'March 1, 2026', '03/01/2026')."
        ),
    )
    cycle_length_days: int = Field(
        default=DEFAULT_CYCLE_LENGTH,
        description=(
            f"Average length of the menstrual cycle in days (default: 28). "
            f"Application accepts values between {MIN_CYCLE_LENGTH} and {MAX_CYCLE_LENGTH}."
        ),
    )


@tool(args_schema=CycleCalculatorInput)
def calculate_menstrual_cycle(
    last_period_date: str,
    cycle_length_days: int = DEFAULT_CYCLE_LENGTH,
) -> str:
    """
    Calculates estimated menstrual cycle milestones based on the user's last period date
    and average cycle length. Returns estimated next period date, estimated ovulation date,
    and estimated fertile window using standard calendar formulas.
    Performs deterministic local date arithmetic.
    """
    try:
        projections = compute_cycle_projections(
            last_period_date=last_period_date,
            cycle_length_days=cycle_length_days,
        )

        return (
            f"Based on a last period start date of **{projections['formatted_last_period']}** "
            f"and an average cycle length of **{projections['cycle_length_days']} days**, "
            f"here are your calendar-based estimates:\n\n"
            f"• **Estimated Next Period**: {projections['formatted_next_period']}\n"
            f"• **Estimated Ovulation Date**: {projections['formatted_ovulation']}\n"
            f"• **Estimated Fertile Window**: {projections['formatted_fertile_window']} "
            f"(the 6-day window ending on the estimated ovulation day)\n\n"
            f"*{projections['disclaimer']}*"
        )
    except Exception as exc:
        return f"Could not calculate cycle projections: {str(exc)}"
