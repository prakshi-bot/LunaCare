"""
LunaCare: Mind & Wellness Center
--------------------------------
Provides calming, non-diagnostic holistic wellness activities:
- Interactive 4-7-8 Breathing Orb Animation
- 5-4-3-2-1 Sensory Grounding Technique
- Hormonal Stress Check-in
- Gentle Mindful Self-Care Practices
"""

import textwrap
import streamlit as st


def render_wellness_page():
    """Renders the Mind & Wellness page."""
    st.markdown(
        textwrap.dedent("""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🧘‍♀️</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">Mind & Wellness Center</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                Gentle somatic grounding, vagus nerve breathing, and restorative self-care practices.
            </p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["🌬️ Guided Breathing", "🌱 5-4-3-2-1 Grounding", "✨ Stress & Cycle Care"])

    with tab1:
        breathing_html = textwrap.dedent("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="font-size: 1.3rem; color: #B97988; margin-bottom: 0.5rem;">The 4-7-8 Vagal Calming Breath</h3>
            <p style="color: #4A3B4F; max-width: 540px; margin: 0 auto 1.5rem auto; font-size: 0.92rem; line-height: 1.6;">
                Synchronize your breathing with the glowing moon orb below: Inhale deeply for 4 seconds, 
                hold gently for 7 seconds, and exhale smoothly through your mouth for 8 seconds.
            </p>
            <div class="breathing-orb"></div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 16px; font-weight: 700; font-size: 0.9rem; color: #B97988; margin-top: 1.5rem;">
                <span>1. Inhale (4s)</span>
                <span>•</span>
                <span>2. Hold (7s)</span>
                <span>•</span>
                <span>3. Exhale (8s)</span>
            </div>
        </div>
        """).strip()

        st.markdown(breathing_html, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.info("💡 **Why this works:** Extending the exhale activates the parasympathetic nervous system via the vagus nerve, immediately signaling physical safety and lowering cortisol.")

    with tab2:
        grounding_intro = textwrap.dedent("""
        <div class="luna-card">
            <h3 style="font-size: 1.25rem; color: #B97988; margin-bottom: 0.5rem;">5-4-3-2-1 Somatic Grounding Exercise</h3>
            <p style="color: #4A3B4F; font-size: 0.92rem; line-height: 1.6;">
                When stress, PMS overwhelm, or sensory fatigue arises, this sensory technique reconnects your mind with your immediate physical environment.
            </p>
        </div>
        """).strip()
        st.markdown(grounding_intro, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            st.checkbox("👁️ **5 things you can SEE** (a painting, shadows on the wall, a window, trees, your hands)")
            st.checkbox("✋ **4 things you can TOUCH** (the fabric of your sleeve, your desk, a cool stone, your hair)")
            st.checkbox("👂 **3 things you can HEAR** (birds outside, the hum of an appliance, distant traffic)")
        with g2:
            st.checkbox("👃 **2 things you can SMELL** (coffee, fresh air, scented candle, your lotion)")
            st.checkbox("👅 **1 thing you can TASTE** (a sip of herbal tea, mint, or the lingering taste of fruit)")
            st.markdown(
                textwrap.dedent("""
                <div style="margin-top: 1rem; padding: 0.8rem; background: #FFF8FB; border: 1px solid #E7C9D0; border-radius: 10px; font-size: 0.85rem; color: #4A3B4F;">
                    Take a deep breath once all five senses are anchored. You are safe in this present moment.
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

    with tab3:
        st.markdown("<h3 style='font-size: 1.25rem; color: #B97988;'>Restorative Practices by Phase</h3>", unsafe_allow_html=True)
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown(
                textwrap.dedent("""
                <div class="luna-card">
                    <div style="font-size: 1.3rem;">🩸</div>
                    <div style="font-weight: 700; color: #B97988; margin-top: 4px;">Menstrual Phase (Days 1–5)</div>
                    <div style="font-size: 0.88rem; color: #4A3B4F; margin-top: 4px; line-height: 1.5;">
                        Energy levels are naturally introverted. Prioritize warm broths, ginger tea, gentle stretching, extra sleep, and boundary-setting.
                    </div>
                </div>
                <div style="height: 10px;"></div>
                <div class="luna-card">
                    <div style="font-size: 1.3rem;">✨</div>
                    <div style="font-weight: 700; color: #B97988; margin-top: 4px;">Follicular Phase (Days 6–12)</div>
                    <div style="font-size: 0.88rem; color: #4A3B4F; margin-top: 4px; line-height: 1.5;">
                        Estrogen rises, bringing sharper mental focus and creative vitality. Great time for learning new skills, outdoor walks, and social connection.
                    </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )
        with c_col2:
            st.markdown(
                textwrap.dedent("""
                <div class="luna-card">
                    <div style="font-size: 1.3rem;">☀️</div>
                    <div style="font-weight: 700; color: #B97988; margin-top: 4px;">Ovulatory Phase (Days 13–16)</div>
                    <div style="font-size: 0.88rem; color: #4A3B4F; margin-top: 4px; line-height: 1.5;">
                        Peak communication confidence and energy. Support this window with vibrant leafy greens, hydration, and moderate strength training.
                    </div>
                </div>
                <div style="height: 10px;"></div>
                <div class="luna-card">
                    <div style="font-size: 1.3rem;">🌙</div>
                    <div style="font-weight: 700; color: #B97988; margin-top: 4px;">Luteal Phase (Days 17–28)</div>
                    <div style="font-size: 0.88rem; color: #4A3B4F; margin-top: 4px; line-height: 1.5;">
                        Progesterone dominates. Magnesium, dark chocolate, chamomile, warm baths, and slowing down support PMS symptom mitigation.
                    </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )
