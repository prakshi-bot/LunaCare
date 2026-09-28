"""
Unit Tests: Conversational Memory Layer (Phase 4)
------------------------------------------------
Tests session-based conversational memory initialization, greeting isolation,
message addition, sliding memory window enforcement, memory clearing,
and delivery of conversational turns to Gemini without live network requests.
"""

import pytest
from unittest.mock import MagicMock, patch

from config import MEMORY_WINDOW
from services.memory_service import (
    initialize_memory,
    add_message,
    get_recent_history,
    clear_memory,
    get_all_messages,
    is_empty,
    INITIAL_GREETING,
    SESSION_MEMORY_KEY,
)
from services.gemini_service import GeminiService


# ==========================================
# 1. Memory Initialization & Greeting Tests
# ==========================================

def test_memory_initialization_creates_single_greeting():
    """Verifies that an empty session is initialized with exactly one greeting."""
    storage = {}
    msgs = initialize_memory(storage)
    assert len(msgs) == 1
    assert msgs[0]["role"] == "assistant"
    assert msgs[0]["content"] == INITIAL_GREETING
    assert SESSION_MEMORY_KEY in storage


def test_greeting_not_duplicated_on_reinitialization():
    """Verifies that subsequent calls to initialize_memory do not duplicate the greeting."""
    storage = {}
    initialize_memory(storage)
    initialize_memory(storage)
    initialize_memory(storage)

    all_msgs = get_all_messages(storage)
    assert len(all_msgs) == 1
    assert all_msgs[0]["content"] == INITIAL_GREETING


# ==========================================
# 2. Message Addition & Validation Tests
# ==========================================

def test_add_user_and_assistant_messages():
    """Verifies adding user and assistant messages preserves order and roles."""
    storage = {}
    initialize_memory(storage)

    add_message("user", "What is a menstrual cycle?", storage=storage)
    add_message("assistant", "A menstrual cycle is a monthly sequence...", storage=storage)

    all_msgs = get_all_messages(storage)
    assert len(all_msgs) == 3
    assert all_msgs[0]["content"] == INITIAL_GREETING
    assert all_msgs[1]["role"] == "user"
    assert all_msgs[1]["content"] == "What is a menstrual cycle?"
    assert all_msgs[2]["role"] == "assistant"
    assert "monthly sequence" in all_msgs[2]["content"]


def test_add_message_validation_rejects_invalid_inputs():
    """Verifies that invalid roles or empty content raise ValueError."""
    storage = {}
    with pytest.raises(ValueError, match="Invalid message role"):
        add_message("system", "Test content", storage=storage)

    with pytest.raises(ValueError, match="Cannot add an empty message"):
        add_message("user", "   ", storage=storage)


# ==========================================
# 3. History Retrieval & Window Limiting Tests
# ==========================================

def test_get_recent_history_excludes_initial_greeting():
    """Verifies that get_recent_history excludes the initial greeting turn."""
    storage = {}
    initialize_memory(storage)

    # When only greeting exists, recent history for LLM should be empty
    assert get_recent_history(storage=storage) == []
    assert is_empty(storage) is True

    add_message("user", "Hello", storage=storage)
    add_message("assistant", "Hi! How can I help?", storage=storage)

    history = get_recent_history(storage=storage)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi! How can I help?"
    assert is_empty(storage) is False


def test_memory_window_sliding_limit():
    """Verifies that history is capped at window_size turns (default MEMORY_WINDOW=8)."""
    storage = {}
    initialize_memory(storage)

    # Add 12 turns (6 user, 6 assistant)
    for i in range(1, 7):
        add_message("user", f"User question {i}", storage=storage)
        add_message("assistant", f"Assistant answer {i}", storage=storage)

    # Total in UI should be 1 greeting + 12 turns = 13 messages
    assert len(get_all_messages(storage)) == 13

    # Default history should be capped at MEMORY_WINDOW (8)
    history = get_recent_history(storage=storage)
    assert len(history) == MEMORY_WINDOW
    assert history[0]["content"] == "User question 3"
    assert history[-1]["content"] == "Assistant answer 6"

    # Explicit custom window size
    history_4 = get_recent_history(window_size=4, storage=storage)
    assert len(history_4) == 4
    assert history_4[0]["content"] == "User question 5"
    assert history_4[-1]["content"] == "Assistant answer 6"


# ==========================================
# 4. Clear Memory Tests
# ==========================================

def test_clear_memory_resets_session():
    """Verifies clear_memory completely discards dialogue and restores one clean greeting."""
    storage = {}
    initialize_memory(storage)
    add_message("user", "What is ovulation?", storage=storage)
    add_message("assistant", "Ovulation is the release of an egg...", storage=storage)

    assert len(get_all_messages(storage)) == 3
    assert len(get_recent_history(storage=storage)) == 2

    clear_memory(storage)

    # After clearing: only 1 greeting in all messages, 0 in LLM history
    all_msgs = get_all_messages(storage)
    assert len(all_msgs) == 1
    assert all_msgs[0]["content"] == INITIAL_GREETING
    assert get_recent_history(storage=storage) == []
    assert is_empty(storage) is True


# ==========================================
# 5. Gemini Service History Delivery Tests
# ==========================================

@patch("services.gemini_service.genai.Client")
def test_conversation_history_reaches_gemini_client(mock_client_cls):
    """Verifies that previous conversation turns are correctly mapped to types.Content."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    mock_resp.text = "It usually lasts 28 days on average."
    mock_instance.models.generate_content.return_value = mock_resp

    service = GeminiService(api_key="test-valid-key")
    history = [
        {"role": "user", "content": "What is a menstrual cycle?"},
        {"role": "assistant", "content": "A menstrual cycle is a monthly biological sequence."},
    ]

    result = service.generate_response(
        user_message="How long does it usually last?",
        conversation_history=history,
    )

    assert "28 days" in result
    mock_instance.models.generate_content.assert_called_once()
    call_args = mock_instance.models.generate_content.call_args
    contents = call_args.kwargs.get("contents")

    # Contents should contain 3 turns: user turn 1, model turn 1, current user turn
    assert len(contents) == 3
    assert contents[0].role == "user"
    assert contents[0].parts[0].text == "What is a menstrual cycle?"
    assert contents[1].role == "model"
    assert "monthly biological sequence" in contents[1].parts[0].text
    assert contents[2].role == "user"
    assert contents[2].parts[0].text == "How long does it usually last?"


@patch("services.gemini_service.genai.Client")
def test_gemini_service_caps_history_at_memory_window(mock_client_cls):
    """Verifies that passing a history larger than MEMORY_WINDOW is safely capped."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    mock_resp.text = "Answer."
    mock_instance.models.generate_content.return_value = mock_resp

    service = GeminiService(api_key="test-valid-key")
    # Provide 16 history turns (8 user, 8 assistant)
    long_history = []
    for i in range(1, 9):
        long_history.append({"role": "user", "content": f"Old Q{i}"})
        long_history.append({"role": "assistant", "content": f"Old A{i}"})

    service.generate_response("Final question", conversation_history=long_history)

    call_args = mock_instance.models.generate_content.call_args
    contents = call_args.kwargs.get("contents")

    # contents should have MEMORY_WINDOW (8) history items + 1 current question = 9 items
    assert len(contents) == MEMORY_WINDOW + 1
    # Oldest turn should be from Q5 onwards, not Q1
    assert contents[0].parts[0].text == "Old Q5"
    assert contents[-1].parts[0].text == "Final question"
