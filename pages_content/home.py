"""
LunaCare: Landing Page (Home)
----------------------------
The introductory landing view establishing LunaCare's original visual identity,
hero value proposition, core feature highlights, 3-step RAG explanation,
privacy commitments, and medical safety disclaimers.
"""

import streamlit as st
from config import APP_NAME, APP_TAGLINE, APP_SUBTITLE, MEDICAL_DISCLAIMER
from components.cards import render_feature_card, render_step_card, render_disclaimer_banner
from components.navigation import navigate_to


def render_home_page():
    """Renders the complete LunaCare landing page."""
    
    # 1. Hero Section
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem 0 2.5rem 0;">
            <div class="brand-header-badge">
                <span>🌙</span> <span>Intelligent, Calm & Supportive Female Health</span>
            </div>
            <h1 class="brand-title-hero">
                Your space for <span class="brand-gradient-text">better-informed</span> health decisions.
            </h1>
            <p class="brand-subtitle" style="margin: 0 auto 2rem auto;">
                {APP_SUBTITLE} Grounded in verified medical knowledge with a calm, empathetic conversation flow.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hero Action Call-to-Action Buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 2, 1.5])
    with col_btn2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💬 Start Chatting", use_container_width=True, type="primary", key="hero_start_chat"):
                navigate_to("chat")
        with c2:
            if st.button("📚 Explore Health Topics", use_container_width=True, key="hero_explore_topics"):
                navigate_to("health_topics")

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 2. Feature Cards Section
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 1.8rem;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #B97988; text-transform: uppercase; letter-spacing: 0.08em;">
                Everything In One Place
            </div>
            <h2 style="font-size: 1.85rem; color: #B97988; margin-top: 4px;">
                Designed to Support Every Stage of Your Well-being
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        render_feature_card(
            title="Women's Health Topics",
            description="Verified educational insights across menstrual cycles, hygiene, PCOS, and reproductive anatomy.",
            icon="🩷",
            badge="Curated",
        )
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_feature_card(
            title="Mind & Wellness Center",
            description="Guided 4-7-8 breathing exercises, 5-4-3-2-1 sensory grounding, and mindful self-care practices.",
            icon="🧠",
            badge="Holistic",
        )

    with f_col2:
        render_feature_card(
            title="AI Health Chatbot",
            description="Conversational assistant with multi-turn memory that answers questions with calm empathy.",
            icon="💬",
            badge="Interactive",
        )
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_feature_card(
            title="Gentle Mood Tracker",
            description="Log daily emotional energy, recognize cyclic fluctuations, and view weekly trend graphs.",
            icon="📊",
            badge="Self-Reflection",
        )

    with f_col3:
        render_feature_card(
            title="RAG Knowledge Base",
            description="Responses strictly grounded in curated female-health literature to minimize hallucinations.",
            icon="📚",
            badge="Evidence-Based",
        )
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_feature_card(
            title="Educational Symptom Guide",
            description="Explore context around common symptoms without alarmist or misleading medical diagnosis.",
            icon="🩺",
            badge="Non-Diagnostic",
        )

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # 3. How LunaCare Works (3-Step Flow)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #B97988; text-transform: uppercase; letter-spacing: 0.08em;">
                Under The Hood
            </div>
            <h2 style="font-size: 1.85rem; color: #B97988; margin-top: 4px;">
                How LunaCare Generates Grounded Answers
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        render_step_card(
            step_num=1,
            title="1. Ask a Question",
            description="Submit your question about menstrual cycle, hygiene, PCOS, or daily wellness symptoms.",
            icon="💭",
        )
    with s2:
        render_step_card(
            step_num=2,
            title="2. RAG Knowledge Retrieval",
            description="Semantic search queries Chroma vector store to locate exact, verified female health document chunks.",
            icon="🔎",
        )
    with s3:
        render_step_card(
            step_num=3,
            title="3. Safe Grounded Generation",
            description="The LLM synthesizes an empathetic, cited educational response constrained by safety guidelines.",
            icon="✨",
        )

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 4. Privacy & Data Safety Commitment
    st.markdown(
        """
        <div class="luna-card" style="background: linear-gradient(135deg, #FFF8FB 0%, #F1E2E6 100%);">
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 0.8rem;">
                <div style="font-size: 1.8rem;">🔒</div>
                <div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #B97988;">Privacy & Dignity By Design</div>
                    <div style="font-size: 0.85rem; color: #B97988; font-weight: 600;">Your sensitive health inquiries belong to you</div>
                </div>
            </div>
            <div style="font-size: 0.92rem; color: #4A3B4F; line-height: 1.6;">
                LunaCare operates with a strict privacy-first architecture. All conversation memories and mood logs remain stored inside your active local session or device cache. We do not sell your personal data, profile your intimate health inquiries, or deploy intrusive cross-site tracking.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5. Medical Safety Disclaimer
    render_disclaimer_banner(MEDICAL_DISCLAIMER)

    # 6. Footer
    st.markdown(
        """
        <div class="luna-footer">
            <div style="font-weight: 700; color: #B97988; margin-bottom: 4px;">LunaCare • Female Health & Wellness Companion</div>
            <div>Empathetic Health & Wellness Information • Supporting Better-Informed Decisions</div>
            <div style="margin-top: 6px; font-size: 0.78rem; opacity: 0.8;">© 2026 LunaCare. Educational Health & Wellness Companion.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
