"""
Phase 6: End-to-End System Integration Tests
--------------------------------------------
Verifies the unified interaction between:
1. Streamlit frontend chat flow
2. Conversational session memory
3. LunaCare Agent / Orchestrator
4. LangChain Menstrual Cycle Calculator Tool
5. Chroma Vector Database & RAG Retrieval
6. Gemini LLM & Structured Prompting
7. Multi-turn context resolution & Clear conversation
8. Non-regression of Phase 1–5 features
"""

from datetime import date
from unittest.mock import patch, MagicMock
import pytest
import chromadb

from config import (
    VECTOR_STORE_DIR,
    CHROMA_COLLECTION_NAME,
    MEMORY_WINDOW,
    DEFAULT_CYCLE_LENGTH,
)
from tools.cycle_calculator import calculate_menstrual_cycle, compute_cycle_projections
from services.agent_service import agent_service, LunaCareAgent, extract_cycle_parameters
from services.memory_service import (
    initialize_memory,
    add_message,
    get_recent_history,
    clear_memory,
    get_all_messages,
    INITIAL_GREETING,
)
from services.retrieval_service import retrieve_relevant_documents, format_retrieved_context
from services.gemini_service import GeminiService
from prompts.system_prompt import get_structured_prompt


# ==========================================
# TEST 1: Normal female-health question -> RAG + Gemini
# ==========================================

@patch("services.agent_service.generate_response")
def test_1_normal_health_question_rag_and_gemini(mock_generate):
    """
    TEST 1: Normal female-health question
    Verifies that a factual inquiry routes through RAG retrieval and invokes Gemini with context.
    """
    mock_generate.return_value = "PCOS is a common hormonal condition associated with irregular cycles."

    query = "What are common symptoms associated with PCOS?"
    session_storage = {}
    initialize_memory(session_storage)

    response = agent_service.process_query(query, conversation_history=[])

    assert "PCOS" in response
    mock_generate.assert_called_once()
    call_kwargs = mock_generate.call_args.kwargs
    # Context must be provided from RAG
    assert call_kwargs.get("context") is not None
    assert "pcos" in call_kwargs.get("context", "").lower() or len(call_kwargs.get("context", "")) > 0


# ==========================================
# TEST 2: Follow-up question -> Memory correctly supplies context
# ==========================================

@patch("services.agent_service.generate_response")
def test_2_conversational_follow_up_memory_supplies_context(mock_generate):
    """
    TEST 2: Follow-up question
    Verifies that multi-turn history is correctly passed to resolve pronoun references.
    """
    mock_generate.return_value = "A menstrual cycle usually lasts between 21 and 35 days."

    history = [
        {"role": "user", "content": "What is a menstrual cycle?"},
        {"role": "assistant", "content": "A menstrual cycle is a monthly biological process."},
    ]

    follow_up = "How long does it usually last?"
    response = agent_service.process_query(follow_up, conversation_history=history)

    assert "lasts between" in response
    mock_generate.assert_called_once()
    call_args = mock_generate.call_args
    passed_history = call_args.kwargs.get("conversation_history")
    assert passed_history == history
    assert len(passed_history) == 2


# ==========================================
# TEST 3: Cycle calculation question -> Cycle tool is invoked
# ==========================================

def test_3_cycle_calculation_invokes_cycle_tool():
    """
    TEST 3: Cycle calculation question
    Verifies that a deterministic cycle calculation query invokes the LangChain tool locally.
    Gemini is NOT asked to do arithmetic.
    """
    query = "My period started on March 1, 2026 and my cycle is 28 days. When is my next period?"
    response = agent_service.process_query(query, conversation_history=[])

    assert "March 29, 2026" in response
    assert "March 15, 2026" in response
    assert "March 10" in response
    assert "calendar-based estimates" in response


# ==========================================
# TEST 4: Cycle calculation with missing information
# ==========================================

def test_4_cycle_calculation_missing_info_prompts_user():
    """
    TEST 4: Cycle calculation with missing information
    Verifies that if dates/cycle length are missing, the system asks for them without guessing.
    """
    query = "When will my next period come?"
    response = agent_service.process_query(query, conversation_history=[])

    # System must prompt for the missing date and length
    assert "start date of your last period" in response.lower()
    assert "cycle length" in response.lower()
    # Must NOT invent a calculation without inputs
    assert "March 29" not in response


# ==========================================
# TEST 5: Cycle calculation using information from previous conversation
# ==========================================

def test_5_cycle_calculation_using_information_from_previous_conversation():
    """
    TEST 5: Cycle calculation using information from previous conversation
    Turn 1: User says "My last period started March 1." -> System asks for cycle length.
    Turn 2: User says "28 days." -> System uses March 1 from memory + 28 days from current turn.
    """
    # Turn 1: User gives date only
    turn1_query = "My last period started March 1."
    turn1_resp = agent_service.process_query(turn1_query, conversation_history=[])
    assert "usual cycle length" in turn1_resp.lower() or "what is your" in turn1_resp.lower()

    # Conversation history after Turn 1
    session_history = [
        {"role": "user", "content": turn1_query},
        {"role": "assistant", "content": turn1_resp},
    ]

    # Turn 2: User replies with cycle length
    turn2_query = "28 days."
    turn2_resp = agent_service.process_query(turn2_query, conversation_history=session_history)

    # Memory + Tool work together to calculate projections!
    assert "March 29, 2026" in turn2_resp
    assert "March 15, 2026" in turn2_resp
    assert "March 10" in turn2_resp


# ==========================================
# TEST 6: Question requiring health explanation + cycle calculation
# ==========================================

@patch("services.agent_service.generate_response")
def test_6_question_requiring_health_explanation_and_calculation(mock_generate):
    """
    TEST 6: Question requiring health explanation + cycle calculation
    Verifies that both the LangChain cycle tool and RAG contribute to the response.
    """
    mock_generate.return_value = (
        "Based on your 28-day cycle starting March 1, your estimated ovulation is March 15, 2026, "
        "and your fertile window is March 10–15, 2026. The fertile window represents the days when "
        "conception is biologically possible, reflecting sperm viability and egg lifespan."
    )

    query = "My period started March 1 and my cycle is 28 days. When is ovulation and what is the fertile window?"
    response = agent_service.process_query(query, conversation_history=[])

    # Gemini must have been called with both RAG context and tool calculation
    mock_generate.assert_called_once()
    call_kwargs = mock_generate.call_args.kwargs
    assert call_kwargs.get("tool_result") is not None
    assert "March 15, 2026" in call_kwargs["tool_result"]
    assert call_kwargs.get("context") is not None

    assert "March 15, 2026" in response
    assert "fertile window" in response.lower()


# ==========================================
# TEST 7: Unsupported/out-of-domain question -> Safe fallback
# ==========================================

@patch("services.agent_service.generate_response")
def test_7_unsupported_out_of_domain_question_safe_fallback(mock_generate):
    """
    TEST 7: Unsupported/out-of-domain question
    Verifies that an unrelated query (e.g. capital of France) triggers RAG rejection
    and preserves safe insufficient-context fallback.
    """
    mock_generate.return_value = (
        "LunaCare's current curated knowledge base does not have verified documents "
        "on this specific question. Please consult a healthcare professional for personalized guidance."
    )

    query = "What is the capital of France?"
    response = agent_service.process_query(query, conversation_history=[])

    # Check that retrieval rejects with insufficient context
    retrieval_res = retrieve_relevant_documents(query)
    assert retrieval_res["is_sufficient"] is False
    assert retrieval_res["best_distance"] > 0.70

    assert "knowledge base" in response.lower() or "consult" in response.lower()


# ==========================================
# TEST 8: Gemini/API failure -> Application does not crash
# ==========================================

@patch("services.gemini_service.genai.Client")
def test_8_gemini_api_failure_graceful_recovery(mock_client_cls):
    """
    TEST 8: Gemini/API failure
    Verifies that when Gemini returns 429 quota or connection error, the app returns
    a friendly message and never crashes with an unhandled exception.
    """
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance
    mock_instance.models.generate_content.side_effect = RuntimeError("429 RESOURCE_EXHAUSTED")

    service = GeminiService(api_key="test-key")
    response = service.generate_response("Tell me about PCOS")

    assert "having trouble connecting" in response.lower()
    assert "Traceback" not in response
    assert "RuntimeError" not in response


# ==========================================
# TEST 9: Invalid cycle inputs -> Validation intact
# ==========================================

def test_9_invalid_cycle_inputs_validation():
    """
    TEST 9: Invalid cycle inputs
    Verifies that unparseable dates or cycle lengths outside 20–45 return clean error notices.
    """
    query_bad_date = "My period started on invalid-date-xyz and cycle is 28 days. When is my next period?"
    resp_date = agent_service.process_query(query_bad_date, conversation_history=[])
    # When date is invalid or unparseable, LunaCare prompts for a valid start date
    assert "could you please share the start date" in resp_date.lower() or "difficulty processing" in resp_date.lower()

    # When cycle length is outside 20-45 days, LunaCare returns the calibration constraint notice
    query_bad_cycle = "My period started on March 1, 2026 and cycle length is 60 days."
    resp_cycle = agent_service.process_query(query_bad_cycle, conversation_history=[])
    assert "outside the supported application range" in resp_cycle or "difficulty processing" in resp_cycle.lower()

    # Direct function call raises ValueError for unparseable date
    with pytest.raises(ValueError, match="Could not understand the date"):
        compute_cycle_projections("invalid-date-xyz", cycle_length_days=28)

    # Direct function call raises ValueError for out-of-range cycle lengths
    with pytest.raises(ValueError, match="outside the supported application range"):
        compute_cycle_projections("2026-03-01", cycle_length_days=55)

    with pytest.raises(ValueError, match="outside the supported application range"):
        compute_cycle_projections("2026-03-01", cycle_length_days=10)


# ==========================================
# TEST 10: Conversation clear/reset -> Memory resets correctly
# ==========================================

def test_10_conversation_clear_resets_memory():
    """
    TEST 10: Conversation clear/reset
    Verifies that clear_memory completely wipes conversation history, leaving only
    one clean initial greeting for the UI and 0 history turns for the LLM.
    """
    storage = {}
    initialize_memory(storage)
    add_message("user", "What causes menstrual cramps?", storage=storage)
    add_message("assistant", "Cramps are caused by prostaglandins.", storage=storage)

    assert len(get_all_messages(storage)) == 3
    assert len(get_recent_history(storage=storage)) == 2

    clear_memory(storage)

    all_after = get_all_messages(storage)
    history_after = get_recent_history(storage=storage)

    assert len(all_after) == 1
    assert all_after[0]["content"] == INITIAL_GREETING
    assert len(history_after) == 0


# ==========================================
# TEST 11: Existing RAG vector store remains intact
# ==========================================

def test_11_existing_rag_vector_store_remains_intact():
    """
    TEST 11: Existing RAG vector store remains intact
    Verifies that the Chroma collection 'lunacare_health' exists and has exactly 379 chunks.
    """
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    collection = client.get_collection(CHROMA_COLLECTION_NAME)
    assert collection.count() == 379, f"Expected 379 chunks, found {collection.count()}"


# ==========================================
# TEST 12: Existing Phase 1–5 functionality still works
# ==========================================

def test_12_existing_phase_1_to_5_functionality_works():
    """
    TEST 12: Existing Phase 1–5 functionality still works
    Verifies:
    - LangChain cycle tool is real and executable
    - Pure cycle calculation matches March 1, 2026 + 28 days -> March 29 next period, March 15 ovulation
    - Memory window sliding limit (MEMORY_WINDOW=8)
    - RAG document formatting
    """
    # Phase 5 tool
    tool_output = calculate_menstrual_cycle.invoke({
        "last_period_date": "March 1, 2026",
        "cycle_length_days": 28,
    })
    assert "March 29, 2026" in tool_output
    assert "March 15, 2026" in tool_output
    assert "March 10" in tool_output

    # Phase 4 memory sliding window
    storage = {}
    initialize_memory(storage)
    for i in range(6):
        add_message("user", f"Q{i}", storage=storage)
        add_message("assistant", f"A{i}", storage=storage)
    history = get_recent_history(storage=storage)
    assert len(history) == MEMORY_WINDOW

    # Phase 3 RAG context formatting
    rag_res = retrieve_relevant_documents("menstrual hygiene")
    assert rag_res["is_sufficient"] is True
    formatted = format_retrieved_context(rag_res)
    assert "EXCERPT" in formatted
    assert "Topic: menstrual_hygiene" in formatted
    prompt_str = get_structured_prompt(user_query="What is menstrual hygiene?", context=formatted)
    assert "[CONTEXT]" in prompt_str
    assert "Topic: menstrual_hygiene" in prompt_str
