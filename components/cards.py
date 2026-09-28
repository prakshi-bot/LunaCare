"""
LunaCare: Reusable Visual Cards & UI Elements
---------------------------------------------
Provides consistent, elegant card elements matching LunaCare's
moon and wellness aesthetic (rounded borders, subtle shadows, gentle gradients).
"""

import streamlit as st
from config import MEDICAL_DISCLAIMER


def render_disclaimer_banner(custom_text: str = None):
    """Renders the standard medical safety disclaimer banner."""
    text = custom_text or MEDICAL_DISCLAIMER
    st.markdown(
        f"""
        <div class="disclaimer-banner">
            <div style="font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                <span>⚠️</span> <span>Important Educational Notice</span>
            </div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(title: str, description: str, icon: str, badge: str = None):
    """Renders a feature card for the landing page."""
    badge_html = f'<div class="luna-badge">{badge}</div>' if badge else ""
    st.markdown(
        f"""
        <div class="luna-card">
            <div class="luna-card-icon">{icon}</div>
            <div class="luna-card-title">{title}</div>
            <div class="luna-card-text">{description}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_card(step_num: int, title: str, description: str, icon: str):
    """Renders an architectural step card explaining how LunaCare works."""
    st.markdown(
        f"""
        <div class="step-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div class="step-number">{step_num}</div>
                <div style="font-size: 1.6rem;">{icon}</div>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #B97988; margin-bottom: 0.5rem;">
                {title}
            </div>
            <div style="font-size: 0.92rem; color: #4A3B4F; line-height: 1.55;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topic_card(topic: dict):
    """Renders a health topic card with preview and category badge."""
    st.markdown(
        f"""
        <div class="luna-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div class="luna-card-icon">{topic['icon']}</div>
                <span class="luna-badge">{topic.get('badge', 'Health')}</span>
            </div>
            <div class="luna-card-title">{topic['title']}</div>
            <div class="luna-card-text">{topic['summary']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
