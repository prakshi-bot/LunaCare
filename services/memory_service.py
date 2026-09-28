"""
LunaCare: Conversational Memory Service Layer
--------------------------------------------
Demonstrates Week 4 & Week 5 Conversational Context Management:
- Short-term session memory: Retains recent user questions and assistant responses
  during an active Streamlit browser session.
- Follow-up resolution: Enables natural pronouns ('it', 'these symptoms', 'that')
  to be understood by the LLM in multi-turn dialogues.
- Privacy-by-design: Strictly ephemeral in session state. No health dialogues
  are saved to disk, cloud storage, or persistent databases.
- Sliding memory window: Enforces MEMORY_WINDOW (default: 8 turns) to prevent
  token bloat while maintaining conversational continuity.
- Greeting isolation: The initial welcoming assistant greeting is kept visible
  in the UI but cleanly excluded from the LLM conversation history.
"""

import logging
from typing import List, Dict, Any, Optional
import streamlit as st

from config import MEMORY_WINDOW

logger = logging.getLogger("lunacare.memory_service")

# Session state key used to store chat messages
SESSION_MEMORY_KEY = "chat_history"

# Standard welcoming greeting shown to the user on application launch and reset
INITIAL_GREETING = (
    "Hello! I am **LunaCare**, your educational female health and wellness companion. 🌙\n\n"
    "I am here to help you understand your menstrual cycle, hygiene, PCOS concepts, "
    "and general wellness with clear, supportive information. "
    "How can I help you today?"
)

# In-memory dictionary fallback used when running outside of Streamlit runtime (e.g., pytest)
_test_fallback_storage: Dict[str, Any] = {}


def _resolve_storage(storage: Optional[Any] = None) -> Any:
    """
    Returns the appropriate storage dictionary:
    1. Explicitly provided storage object (e.g., in unit tests).
    2. Streamlit's st.session_state if running within Streamlit.
    3. Global test fallback dictionary if running in standalone test runner.
    """
    if storage is not None:
        return storage

    try:
        if hasattr(st, "session_state"):
            return st.session_state
    except Exception:
        pass

    return _test_fallback_storage


def initialize_memory(storage: Optional[Any] = None) -> List[Dict[str, str]]:
    """
    Initializes conversational memory in session state if not already present.
    
    Guarantees that:
    - If memory is empty/uninitialized, exactly one initial greeting is created.
    - If memory already contains messages, the greeting is NOT duplicated.
    
    Returns:
        List[Dict[str, str]]: Active message history.
    """
    store = _resolve_storage(storage)

    if SESSION_MEMORY_KEY not in store or not store[SESSION_MEMORY_KEY]:
        store[SESSION_MEMORY_KEY] = [
            {
                "role": "assistant",
                "content": INITIAL_GREETING,
            }
        ]
        logger.info("Initialized fresh conversational memory with initial greeting.")

    return store[SESSION_MEMORY_KEY]


def add_message(role: str, content: str, storage: Optional[Any] = None) -> Dict[str, str]:
    """
    Appends a new conversational message (user or assistant) to session memory.
    
    Stores only conversational content needed by Gemini, keeping session memory
    clean and free of internal RAG traces or debug tokens.
    
    Args:
        role: "user" or "assistant"
        content: Natural language message text
        storage: Optional custom storage dictionary
        
    Returns:
        Dict[str, str]: The newly appended message turn.
    """
    clean_role = role.strip().lower()
    if clean_role not in ("user", "assistant"):
        raise ValueError(f"Invalid message role '{role}'. Must be 'user' or 'assistant'.")

    clean_content = content.strip() if content else ""
    if not clean_content:
        raise ValueError("Cannot add an empty message to conversational memory.")

    store = _resolve_storage(storage)
    if SESSION_MEMORY_KEY not in store:
        initialize_memory(store)

    message = {
        "role": clean_role,
        "content": clean_content,
    }
    store[SESSION_MEMORY_KEY].append(message)
    return message


def get_recent_history(
    window_size: Optional[int] = None, storage: Optional[Any] = None
) -> List[Dict[str, str]]:
    """
    Retrieves the most recent conversational turns formatted for Gemini.
    
    CRITICAL BEHAVIOR:
    - Strictly EXCLUDES the initial introductory greeting from model context.
    - Limits history to `window_size` turns (defaults to MEMORY_WINDOW = 8).
    - Up to 8 recent user/assistant turns (e.g. 4 dialog exchanges) are returned.
    
    Args:
        window_size: Max number of turns to return (default: MEMORY_WINDOW).
        storage: Optional custom storage dictionary.
        
    Returns:
        List[Dict[str, str]]: Chronological list of recent conversation turns.
    """
    effective_window = window_size if window_size is not None else MEMORY_WINDOW
    store = _resolve_storage(storage)

    if SESSION_MEMORY_KEY not in store:
        return []

    all_msgs = store[SESSION_MEMORY_KEY]

    # Filter out initial greeting message so Gemini is not confused by its own welcome
    dialogue_turns = [
        {"role": m["role"], "content": m["content"]}
        for m in all_msgs
        if m.get("content") != INITIAL_GREETING
    ]

    # Apply sliding memory window to keep payload within token budget
    if effective_window > 0:
        return dialogue_turns[-effective_window:]
    return dialogue_turns


def clear_memory(storage: Optional[Any] = None) -> None:
    """
    Completely resets conversational memory.
    
    After clearing:
    - Any past conversation turns are discarded.
    - Exactly one clean initial greeting is restored for the UI.
    - The next question starts as a completely fresh conversation.
    """
    store = _resolve_storage(storage)
    store[SESSION_MEMORY_KEY] = [
        {
            "role": "assistant",
            "content": INITIAL_GREETING,
        }
    ]
    logger.info("Cleared conversation memory. Restored clean initial greeting.")


def get_all_messages(storage: Optional[Any] = None) -> List[Dict[str, str]]:
    """
    Returns all messages currently in session memory (including the initial greeting)
    for rendering the full conversation history in the Streamlit UI.
    """
    store = _resolve_storage(storage)
    if SESSION_MEMORY_KEY not in store:
        return initialize_memory(store)
    return list(store[SESSION_MEMORY_KEY])


def is_empty(storage: Optional[Any] = None) -> bool:
    """
    Returns True if no user dialogue turns have occurred yet in the current session.
    """
    turns = get_recent_history(storage=storage)
    return len(turns) == 0
