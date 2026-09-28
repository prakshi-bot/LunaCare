"""
LunaCare: Chat UI Helper Component
----------------------------------
Renders chat bubbles (User vs LunaCare assistant), starter suggested chips,
and the educational RAG source citation inspector.
"""

import streamlit as st
from config import SUGGESTED_QUESTIONS


def render_user_message(content: str):
    """Renders a clean, styled user message using Streamlit's native chat component."""
    with st.chat_message("user", avatar="👤"):
        st.markdown(content)


def render_assistant_message(content: str, sources: list = None, trace_info: dict = None):
    """
    Renders LunaCare's natural-language assistant response.
    
    NOTE: sources and trace_info are retained in the function parameters for
    backend data pipeline and future internal grounding, but are strictly NOT
    rendered in the frontend to keep the interface clean, calm, and consumer-facing.
    """
    with st.chat_message("assistant", avatar="🌙"):
        st.markdown(content)


def render_suggestion_chips(on_select_callback):
    """Renders clickable suggested questions to kickstart conversation."""
    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #4A3B4F; margin: 1rem 0 0.5rem 0;'>✨ Suggested Health Questions:</p>", unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    for idx, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[idx]:
            if st.button(question, key=f"sugg_chip_{idx}", use_container_width=True):
                on_select_callback(question)
