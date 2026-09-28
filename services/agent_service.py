"""
LunaCare: Agent & Tool Orchestration Service Layer
--------------------------------------------------
Demonstrates Week 5 Syllabus Concepts:
- Agent Architecture & Tool Usage: The AI Agent decides when external tools are needed
  to perform specialized computation (e.g., calendar arithmetic) rather than relying on
  the LLM to perform error-prone calculations.
- Exactly ONE LangChain Tool: Binds and invokes `calculate_menstrual_cycle` from the
  tools package (decorated with @tool and Pydantic schema).
- Separation of Computation & Language:
  * Deterministic Python math is executed locally via the LangChain tool.
  * Gemini interprets user intent, explains the results empathetically, and provides
    contextual education. Gemini is NEVER asked to perform the arithmetic.
- RAG & Conversational Memory Preservation: Retains Chroma vector store retrieval and
  ephemeral session-state memory without regressions.

Compatibility Disclosure (LangChain Agent API vs. Google GenAI SDK):
--------------------------------------------------------------------
In LangChain, high-level agent constructors like `create_agent` or `create_tool_calling_agent`
require the full `langchain` package and `langchain-google-genai` (which wraps the legacy
google-generativeai library). LunaCare is built on the modern, official Google GenAI SDK
(`google-genai` 2.23.0) and `langchain-core` (1.6.3).
To maintain architectural integrity without installing conflicting legacy wrappers, this
AgentService implements genuine tool-calling:
1. It exposes exactly ONE real LangChain tool (`calculate_menstrual_cycle`).
2. It detects tool requirement, extracts arguments, and executes the LangChain tool locally.
3. It integrates the tool output into Gemini's generation prompt (or fallback educator)
   while shielding Gemini from performing arithmetic.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import date, timedelta
import dateutil.parser

from config import DEFAULT_CYCLE_LENGTH, MIN_CYCLE_LENGTH, MAX_CYCLE_LENGTH
from tools.cycle_calculator import calculate_menstrual_cycle, parse_date_input
from services.retrieval_service import retrieve_relevant_documents, format_retrieved_context
from services.gemini_service import generate_response
from services.memory_service import get_recent_history

logger = logging.getLogger("lunacare.agent_service")

# Keywords indicating intent for menstrual cycle calculations
CALCULATION_INTENT_KEYWORDS = [
    "calculate",
    "calculator",
    "next period",
    "when is my next period",
    "when will my period",
    "when do i ovulate",
    "ovulation date",
    "fertile window",
    "cycle length",
    "track my cycle",
    "estimate my period",
    "estimate ovulation",
    "predict period",
    "cycle projection",
    "cycle day",
]

# Conceptual/educational question indicators that signal dual-intent (calculation + explanation)
EXPLANATION_INDICATORS = [
    "what is",
    "what are",
    "explain",
    "why",
    "how does",
    "tell me about",
    "symptoms",
    "meaning",
    "definition",
]


def detect_calculation_intent(query: str) -> bool:
    """
    Evaluates whether the user's inquiry requires cycle calculation.
    """
    clean_q = query.strip().lower()
    return any(keyword in clean_q for keyword in CALCULATION_INTENT_KEYWORDS)


def detect_combined_intent(query: str) -> bool:
    """
    Evaluates whether the query requests BOTH a cycle calculation AND a factual/educational health explanation.
    For example: "My period started March 1 and my cycle is 28 days. When is ovulation and what is the fertile window?"
    """
    clean_q = query.strip().lower()
    has_calc = detect_calculation_intent(clean_q)
    has_explanation = any(ind in clean_q for ind in EXPLANATION_INDICATORS)
    return has_calc and has_explanation


def has_explicit_cycle_length(text: str) -> bool:
    """Returns True if the text explicitly states a cycle length in days."""
    if not text:
        return False
    # Matches "28 days", "28 day cycle", "cycle of 28", "cycle is 28", "cycle length is 28", or plain "28" if in short answer
    pattern = (
        r"\b(\d{2})\s*(?:days?|day\s*cycle)\b|"
        r"\bcycle\s*(?:is|length|of|around|about)?\s*(\d{2})\b|"
        r"^\s*(\d{2})\s*(?:days?)?\.?\s*$"
    )
    return bool(re.search(pattern, text.strip(), re.IGNORECASE))


def extract_cycle_parameters(query: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[Optional[str], int]:
    """
    Extracts the last period date and cycle length from the user query
    and optional preceding conversational history turns.

    Returns:
        Tuple[Optional[str], int]: (date_string_or_None, cycle_length_days)
    """
    combined_text = query
    if history:
        # Include recent turns to allow follow-up questions
        prior_texts = [turn.get("content", "") for turn in history[-4:]]
        combined_text = " ".join(prior_texts + [query])

    # 1. Extract Cycle Length (e.g. "28 days", "cycle of 30", "30-day cycle", "cycle is 26", or standalone "28")
    cycle_length = DEFAULT_CYCLE_LENGTH
    cycle_match = re.search(r"\b(\d{2})\s*(?:days?|day\s*cycle)\b", combined_text, re.IGNORECASE)
    if not cycle_match:
        cycle_match = re.search(r"\bcycle\s*(?:is|length|of|around|about)?\s*(\d{2})\b", combined_text, re.IGNORECASE)
    if not cycle_match:
        # Check if query itself is just a number like "28" or "28 days"
        cycle_match = re.search(r"^\s*(\d{2})\s*(?:days?)?\.?\s*$", query.strip(), re.IGNORECASE)

    if cycle_match:
        try:
            matched_val = next(g for g in cycle_match.groups() if g is not None)
            parsed_len = int(matched_val)
            cycle_length = parsed_len
        except (ValueError, StopIteration):
            pass

    # 2. Extract Last Period Date
    extracted_date_str: Optional[str] = None

    # Pattern A: Month Name + Day (+ Year optional) e.g., "March 1, 2026", "March 1st", "1st of March 2026"
    month_regex = (
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december|"
        r"jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)"
        r"\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?\b"
    )
    date_match = re.search(month_regex, combined_text, re.IGNORECASE)

    # Pattern B: Numeric date format (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
    if not date_match:
        numeric_regex = r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b|\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b"
        date_match = re.search(numeric_regex, combined_text)

    # Pattern C: Relative phrases like "yesterday", "5 days ago"
    if not date_match:
        rel_match = re.search(r"\b(\d+)\s+days?\s+ago\b", combined_text, re.IGNORECASE)
        if rel_match:
            days_ago = int(rel_match.group(1))
            extracted_date_str = str(date.today() - timedelta(days=days_ago))
        elif "yesterday" in combined_text.lower():
            extracted_date_str = str(date.today() - timedelta(days=1))
        elif "today" in combined_text.lower():
            extracted_date_str = str(date.today())

    if date_match and not extracted_date_str:
        extracted_date_str = date_match.group(0)

    return extracted_date_str, cycle_length


class LunaCareAgent:
    """
    AI Agent that coordinates:
    1. Conversational intent analysis & Priority routing.
    2. Local tool execution for mathematical/calendar projections.
    3. Retrieval-Augmented Generation (RAG) for verified knowledge grounding.
    4. Multi-turn conversational memory integration.
    """

    def __init__(self):
        self.tool = calculate_menstrual_cycle

    def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Executes the unified agent decision loop:
        Priority A: Deterministic calculation request -> invoke LangChain cycle tool locally.
        Priority B: Factual/educational question -> retrieve from Chroma RAG and generate.
        Priority C: Follow-up question -> resolve context via conversational memory.
        Priority D: Combined calculation + explanation -> invoke tool + RAG and synthesize via Gemini.
        Priority E: Unsupported/out-of-domain -> safe fallback behavior.
        """
        clean_query = query.strip()
        if not clean_query:
            return "Please enter a health question or cycle details, and I'd be happy to help! 🌸"

        # Check if conversation history is passed or retrieve from session memory
        history = conversation_history if conversation_history is not None else get_recent_history()

        # Step 1: Evaluate calculation intent and parameters
        needs_calculation = detect_calculation_intent(clean_query)
        date_str, cycle_len = extract_cycle_parameters(clean_query, history=history)

        # Check if an explicit cycle length was ever mentioned in query or history
        has_explicit_len = has_explicit_cycle_length(clean_query) or (
            history and any(has_explicit_cycle_length(turn.get("content", "")) for turn in history[-4:])
        )

        # Check if user mentioned period start date directly (e.g. "My last period started March 1.")
        mentioned_period_start = bool(
            re.search(r"\b(?:period|menses|bleeding)\s*(?:started|was|began|on)?\b", clean_query, re.IGNORECASE)
            and re.search(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b", clean_query, re.IGNORECASE)
        )

        # Check if conversation history indicates an ongoing cycle inquiry (e.g., assistant asked for cycle length)
        history_has_cycle_context = bool(
            history and any(
                "cycle length" in turn.get("content", "").lower() or
                "last period" in turn.get("content", "").lower() or
                "period" in turn.get("content", "").lower()
                for turn in history[-2:]
            )
        )

        is_cycle_query = needs_calculation or mentioned_period_start or (history_has_cycle_context and (has_explicit_len or date_str))

        if is_cycle_query:
            logger.info("Agent processing cycle inquiry for query: '%s'", clean_query[:50])

            # Case 1: User asked for calculation but provided NEITHER date NOR cycle length
            if not date_str and not has_explicit_len:
                return (
                    "I would be happy to calculate your estimated cycle milestones! 🌸\n\n"
                    "To calculate your projected next period and fertile window, could you please share:\n"
                    "1. **The start date of your last period** (for example: *March 1, 2026* or *2026-03-01*).\n"
                    "2. **Your average cycle length** (typical cycles are around 28 days; our calculator supports 20–45 days).\n\n"
                    "*Once you share your dates, I will calculate your estimated next period, ovulation day, "
                    "and fertile window.*"
                )

            # Case 2: User shared date, but NO cycle length was provided in query or conversation history
            # (Matches Section 5: "My last period started March 1." -> "Got it. What is your usual cycle length?")
            if date_str and not has_explicit_len and not needs_calculation:
                return (
                    f"Got it! I see your last period started on **{date_str}**. "
                    "What is your usual cycle length in days? "
                    "(The average cycle is around 28 days; our calculator supports 20–45 days.)"
                )

            # Case 3: User stated cycle length, but NO date is available
            if not date_str and has_explicit_len:
                return (
                    f"Got it, a {cycle_len}-day cycle! "
                    "To calculate your estimated ovulation date, next period, and fertile window, "
                    "could you please share the start date of your last period? (for example: *March 1, 2026*)."
                )

            # Case 4: Both parameters are available (either explicitly or via calculation intent with default/extracted length)
            # Execute the LangChain tool LOCALLY (Gemini is NEVER asked to perform math)
            try:
                tool_output = self.tool.invoke({
                    "last_period_date": date_str,
                    "cycle_length_days": cycle_len,
                })
                logger.info("Executed calculate_menstrual_cycle tool successfully.")
            except Exception as err:
                logger.error("Error executing calculate_menstrual_cycle tool: %s", err)
                return f"I had difficulty processing those cycle dates: {str(err)}"

            # Priority D: Check if this is a Combined question (calculation + conceptual health explanation)
            if detect_combined_intent(clean_query):
                logger.info("Agent identified Combined query (calculation + health explanation).")
                try:
                    retrieval_res = retrieve_relevant_documents(clean_query)
                    context_text = format_retrieved_context(retrieval_res)
                    combined_resp = generate_response(
                        clean_query,
                        conversation_history=history,
                        context=context_text,
                        tool_result=tool_output,
                    )
                    # If Gemini returned a valid response (not fallback error), return it
                    if combined_resp and "trouble connecting" not in combined_resp.lower():
                        return combined_resp
                except Exception as err:
                    logger.warning("Error generating combined response via Gemini: %s", err)

                # Resilient fallback: return clean tool output directly without fabricating ungrounded text
                return tool_output

            # Priority A: Pure deterministic calculation request -> return tool output directly
            return tool_output

        # Priority B, C, E: Non-calculation health inquiries -> proceed with standard RAG retrieval and Gemini
        retrieval_res = retrieve_relevant_documents(clean_query)
        context_text = format_retrieved_context(retrieval_res)

        return generate_response(
            clean_query,
            conversation_history=history,
            context=context_text,
        )


# Default module-level agent instance
agent_service = LunaCareAgent()

