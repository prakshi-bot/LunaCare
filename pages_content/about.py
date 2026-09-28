"""
LunaCare: About LunaCare
------------------------
Presents LunaCare's mission, philosophy, and foundational values:
compassionate, evidence-grounded female health education designed
to support better-informed conversations with healthcare providers.
"""

import streamlit as st
from config import APP_NAME, MEDICAL_DISCLAIMER
from components.cards import render_disclaimer_banner


def render_about_page():
    """Renders the About LunaCare page."""
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🌸</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">About {APP_NAME}</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                An AI-Powered RAG-Based Female Health & Wellness Assistant
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_disclaimer_banner(MEDICAL_DISCLAIMER)

    # Mission Statement Card
    st.markdown(
        """
        <div class="luna-card" style="margin-bottom: 2rem;">
            <h3 style="font-size: 1.3rem; color: #B97988; margin-bottom: 0.6rem;">Our Mission</h3>
            <p style="font-size: 0.95rem; color: #4A3B4F; line-height: 1.65;">
                Women's health issues—ranging from menstrual wellness and hormonal balance to prenatal care and emotional health—are 
                too often surrounded by social stigma, dismissal, or contradictory internet information. 
            </p>
            <p style="font-size: 0.95rem; color: #4A3B4F; line-height: 1.65; margin-bottom: 0;">
                <strong>LunaCare</strong> was created to offer a safe, calming, and evidence-informed space where anyone can explore 
                questions about their body with dignity. By combining curated female-health literature with an empathetic conversational 
                interface, LunaCare empowers you to feel informed, supported, and confident when speaking with your doctor.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Core Principles
    st.markdown("<h2 style='font-size: 1.45rem; color: #B97988; margin-bottom: 1.2rem;'>Our Guiding Principles</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="luna-card">
                <div class="luna-card-icon">📚</div>
                <div class="luna-card-title">Evidence-Informed Information</div>
                <div class="luna-card-text">
                    Our knowledge base is curated from reputable female-health literature, focusing on clinical accuracy, clear physiology, and practical self-care.
                </div>
            </div>
            <div style="height: 12px;"></div>
            <div class="luna-card">
                <div class="luna-card-icon">🔒</div>
                <div class="luna-card-title">Privacy & Confidentiality First</div>
                <div class="luna-card-text">
                    Your personal health inquiries, cycle inputs, and mood records remain completely private in your local session. We do not sell data or track personal health profiles.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="luna-card">
                <div class="luna-card-icon">🤍</div>
                <div class="luna-card-title">Empathetic & Non-Judgmental</div>
                <div class="luna-card-text">
                    Health questions should never be met with judgment or condescension. LunaCare communicates with warmth, validation, and calm clarity.
                </div>
            </div>
            <div style="height: 12px;"></div>
            <div class="luna-card">
                <div class="luna-card-icon">🩺</div>
                <div class="luna-card-title">Safety & Triage Transparency</div>
                <div class="luna-card-text">
                    LunaCare does not provide clinical diagnoses or prescribe treatments. When symptoms indicate potential concern, we always encourage prompt consultation with a medical professional.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
