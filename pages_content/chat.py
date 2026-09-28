"""
LunaCare: AI Health Chat Assistant Interface
-------------------------------------------
Provides a clean, conversational chat interface featuring:
- Session-based conversation state
- Distinct message bubbles (User vs LunaCare)
- One-click suggested question chips
- Expandable RAG source citations inspector
- Reset/Clear conversation action
"""

import streamlit as st
from config import SUGGESTED_QUESTIONS, MEDICAL_DISCLAIMER
from components.chat_ui import (
    render_user_message,
    render_assistant_message,
    render_suggestion_chips,
)
from components.cards import render_disclaimer_banner


from services.agent_service import agent_service
from services.memory_service import (
    initialize_memory,
    add_message,
    get_recent_history,
    clear_memory,
    get_all_messages,
)


def init_chat_state():
    """Initializes conversational memory in session state if not present."""
    initialize_memory()


def process_user_query(query_text: str):
    """
    Executes the conversational Agent pipeline:
    1. Validates the question.
    2. Fetches recent conversation memory (excluding initial greeting).
    3. Stores the current user question in memory.
    4. Passes query and history to LunaCare Agent (which delegates calculations
       to the LangChain cycle calculator tool locally, or retrieves from RAG/Chroma).
    5. Stores the clean assistant response in conversational memory.
    """
    if not query_text or not query_text.strip():
        return

    clean_query = query_text.strip()

    # 1. Fetch prior conversation history before appending the current turn
    previous_history = get_recent_history()

    # 2. Add current user question to memory
    add_message("user", clean_query)

    # 3. Process via Agent (deterministic tool calculation or RAG retrieval + Gemini)
    with st.spinner("LunaCare is thinking..."):
        ai_response = agent_service.process_query(
            clean_query,
            conversation_history=previous_history,
        )

    # 4. Add assistant response to conversational memory
    add_message("assistant", ai_response)


def render_chat_page():
    """Renders the main Chat Assistant page."""
    init_chat_state()

    # Top Header
    c_title, c_actions = st.columns([7, 3])
    with c_title:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.3rem;">
                <span style="font-size: 1.8rem;">💬</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">LunaCare Health Chat</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.92rem; margin-top: 0;">
                Empathetic, evidence-informed guidance for female health and wellness.
            </p>
            """,
            unsafe_allow_html=True,
        )
    with c_actions:
        st.write("")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            clear_memory()
            st.rerun()

    # Medical Disclaimer callout
    render_disclaimer_banner()

    # Suggested Chips
    def handle_chip_click(question: str):
        process_user_query(question)
        st.rerun()

    render_suggestion_chips(handle_chip_click)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Chat Conversation History
    chat_container = st.container()
    with chat_container:
        for msg in get_all_messages():
            if msg["role"] == "user":
                render_user_message(msg["content"])
            else:
                render_assistant_message(content=msg["content"])

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Chat Input Box
    user_input = st.chat_input("Ask a health or wellness question (e.g., 'What causes menstrual cramps?')...")
    if user_input:
        process_user_query(user_input)
        st.rerun()
