"""
LunaCare: Sidebar Component
---------------------------
Renders the branded sidebar featuring quick navigation, conversation reset,
educational milestones, and persistent safety disclaimer badges.
"""

import streamlit as st
from config import APP_NAME, APP_VERSION, MEDICAL_DISCLAIMER
from components.navigation import PAGES, navigate_to


def render_sidebar():
    """Renders the custom branded LunaCare sidebar."""
    with st.sidebar:
        # Brand Wordmark & Moon Icon
        st.markdown(
            """
            <div style="text-align: center; padding: 0.5rem 0 1.2rem 0;">
                <div style="width: 56px; height: 56px; margin: 0 auto 0.8rem auto; border-radius: 16px; 
                            background: linear-gradient(135deg, #B97988 0%, #A86474 60%, #D9AEB8 100%); 
                            display: flex; align-items: center; justify-content: center; font-size: 1.8rem; 
                            box-shadow: 0 8px 20px rgba(185, 121, 136, 0.25);">
                    🌙
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #B97988; letter-spacing: -0.02em;">
                    LunaCare
                </div>
                <div style="font-size: 0.78rem; color: #B97988; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;">
                    Female Health Companion
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 1px; background: #E7C9D0; margin: 0.5rem 0 1rem 0;'></div>", unsafe_allow_html=True)

        # Action: New Chat
        if st.button("✨ Start New Chat", use_container_width=True, type="primary"):
            if "chat_history" in st.session_state:
                st.session_state.chat_history = []
            navigate_to("chat")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Navigation Links
        st.markdown("<p style='font-size: 0.78rem; font-weight: 700; color: #4A3B4F; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;'>Navigation</p>", unsafe_allow_html=True)
        
        for p in PAGES:
            is_active = st.session_state.get("current_page", "home") == p["id"]
            prefix = "● " if is_active else ""
            btn_label = f"{prefix}{p['icon']} {p['label']}"
            if st.button(btn_label, key=f"sidebar_nav_{p['id']}", use_container_width=True):
                navigate_to(p["id"])

        st.markdown("<div style='height: 1px; background: #E7C9D0; margin: 1.2rem 0 1rem 0;'></div>", unsafe_allow_html=True)

        # Wellness Companion Card
        st.markdown(
            f"""
            <div style="background: #FFF8FB; border-radius: 12px; padding: 0.85rem; border: 1px solid #E7C9D0; margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #B97988; display: flex; align-items: center; gap: 6px;">
                    <span>🌸</span> Holistic Care Companion
                </div>
                <div style="font-size: 0.78rem; color: #4A3B4F; margin-top: 4px; line-height: 1.4;">
                    Your evidence-informed companion for female cycle awareness and wellness.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Persistent Medical Disclaimer in Sidebar
        st.markdown(
            f"""
            <div style="background: #FFF8FB; border-radius: 10px; padding: 0.8rem; border-left: 3px solid #B97988; font-size: 0.74rem; color: #4A3B4F; line-height: 1.45; border: 1px solid #E7C9D0; border-left: 3px solid #B97988;">
                <strong style="color: #B97988;">⚠️ Medical Disclaimer:</strong><br>
                LunaCare is for educational purposes and is not a clinical substitute for medical advice.
            </div>
            """,
            unsafe_allow_html=True,
        )
