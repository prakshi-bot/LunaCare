"""
LunaCare: Symptom Education Guide
---------------------------------
Allows users to explore educational context around symptoms (severity, duration).
STRICTLY NON-DIAGNOSTIC: Never diagnoses a condition; provides cautious,
evidence-grounded context and clinical triage guidance.
"""

import streamlit as st
from components.cards import render_disclaimer_banner


# Educational knowledge base for common female symptoms
EDUCATIONAL_SYMPTOM_MAP = {
    "cramps": {
        "associated_factors": [
            "Prostaglandin production during endometrial shedding (primary dysmenorrhea)",
            "Benign uterine fibroids or adenomyosis",
            "Endometriosis (implants of endometrial tissue outside the uterus)",
            "Pelvic inflammatory conditions",
        ],
        "comfort_measures": [
            "Gentle heat therapy (40°C heating pad applied to pelvic area)",
            "Magnesium-rich foods and adequate hydration to reduce muscle tension",
            "Gentle pelvic mobility exercises (cat-cow stretch, child's pose)",
        ],
        "urgent_signs": "Sudden severe pain, inability to keep food down, high fever, or pain accompanied by dizziness/fainting.",
    },
    "irregular": {
        "associated_factors": [
            "High chronic stress impacting the hypothalamic-pituitary-ovarian axis",
            "Polycystic Ovary Syndrome (PCOS)",
            "Thyroid gland dysregulation (hypothyroidism or hyperthyroidism)",
            "Significant changes in body weight or strenuous athletic training",
            "Perimenopause (for individuals in their 40s)",
        ],
        "comfort_measures": [
            "Consistent sleep and meal schedules to regulate circadian rhythms",
            "Cycle tracking to record flow duration, spotting, and symptom patterns",
            "Comprehensive hormonal blood panel evaluation by a healthcare provider",
        ],
        "urgent_signs": "Complete absence of menses for >90 days (not due to pregnancy), or continuous heavy bleeding for >10 days.",
    },
    "heavy": {
        "associated_factors": [
            "Hormonal imbalance causing an excessively thick endometrial lining",
            "Uterine fibroids or endometrial polyps",
            "Coagulation disorders or medications that alter clotting",
            "Adenomyosis",
        ],
        "comfort_measures": [
            "Iron and Vitamin C supplementation to protect ferritin reserves (after testing)",
            "Adequate electrolyte hydration during heavy flow days",
            "Logging the number of sanitary products used per hour for your doctor",
        ],
        "urgent_signs": "Soaking through 2+ pads/tampons per hour for 2 consecutive hours, passing blood clots larger than a quarter, or feeling lightheaded.",
    },
    "discharge": {
        "associated_factors": [
            "Normal physiological shifts across the menstrual cycle (clear/stretchy during ovulation)",
            "Bacterial vaginosis (overgrowth of anaerobic bacteria with distinct odor)",
            "Vulvovaginal candidiasis (yeast overgrowth, thick white discharge)",
            "Contact dermatitis from laundry detergents or soaps",
        ],
        "comfort_measures": [
            "Wearing loose, breathable cotton underwear",
            "Avoiding scented feminine washes, douching, and scented tampons",
            "Washing only the external vulva with mild warm water",
        ],
        "urgent_signs": "Discharge accompanied by pelvic pain, fever, burning with urination, or sores on the genital skin.",
    },
}


def render_symptoms_page():
    """Renders the non-diagnostic Symptom Guide interface."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8rem;">🩺</span>
                <h1 style="margin: 0; font-size: 1.8rem; color: #B97988;">Symptom Education Guide</h1>
            </div>
            <p style="color: #4A3B4F; font-size: 0.95rem; margin-top: 4px;">
                Educational exploration of common female health sensations and when to seek medical evaluation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_disclaimer_banner(
        "LunaCare does not provide medical diagnoses. This tool offers general educational context. "
        "Every body is unique; always consult a licensed healthcare professional for individual care."
    )

    col1, col2 = st.columns([5, 6])

    with col1:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Describe Your Symptoms</h3>", unsafe_allow_html=True)
        
        symptom_category = st.selectbox(
            "Primary Symptom Area:",
            [
                "Menstrual Cramps & Pelvic Discomfort",
                "Irregular or Missed Periods",
                "Heavy Menstrual Bleeding (Menorrhagia)",
                "Unusual Vaginal Discharge or Irritation",
                "Fatigue & Premenstrual Mood Swings",
                "Other Specific Symptom",
            ],
            key="symptom_cat_select",
        )

        duration = st.selectbox(
            "How long have you noticed this?",
            [
                "Just started today",
                "A few days (current cycle)",
                "1 to 2 weeks",
                "Several cycles / months",
                "Chronic / Ongoing for over 6 months",
            ],
            key="symptom_duration_select",
        )

        severity = st.select_slider(
            "Severity Level:",
            options=["Mild (Noticeable but does not interrupt tasks)", "Moderate (Uncomfortable, interferes slightly)", "Severe (Debilitating, prevents daily activities)"],
            value="Mild (Noticeable but does not interrupt tasks)",
            key="symptom_severity_slider",
        )

        notes = st.text_area(
            "Additional context (optional):",
            placeholder="e.g., occurs mostly 2 days before bleeding, accompanied by lower back stiffness...",
            key="symptom_notes",
        )

        submitted = st.button("🔍 Explore Educational Context", use_container_width=True, type="primary")

    with col2:
        st.markdown("<h3 style='font-size: 1.2rem; color: #B97988;'>Educational Perspective</h3>", unsafe_allow_html=True)

        if not submitted:
            st.info("👈 Fill out the details on the left and click 'Explore Educational Context' to view curated health considerations.")
        else:
            # Map selection to educational info
            cat_key = "cramps"
            if "Irregular" in symptom_category:
                cat_key = "irregular"
            elif "Heavy" in symptom_category:
                cat_key = "heavy"
            elif "Discharge" in symptom_category:
                cat_key = "discharge"

            info = EDUCATIONAL_SYMPTOM_MAP.get(cat_key, EDUCATIONAL_SYMPTOM_MAP["cramps"])

            st.markdown(
                f"""
                <div class="luna-card" style="border-left: 4px solid #B97988;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #B97988; margin-bottom: 8px;">
                        Educational Insights for: {symptom_category}
                    </div>
                    <div style="font-size: 0.85rem; color: #B97988; font-weight: 600; margin-bottom: 12px;">
                        Reported Severity: {severity.split(' ')[0]} • Duration: {duration}
                    </div>
                    <div style="font-size: 0.92rem; color: #4A3B4F; line-height: 1.6;">
                        In medical literature, sensations like this <em>can sometimes be associated with</em>:
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            for factor in info["associated_factors"]:
                st.markdown(f"- 🌿 **{factor}**")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("**Evidence-Informed Comfort Measures:**")
            for measure in info["comfort_measures"]:
                st.markdown(f"- ✨ {measure}")

            if "Severe" in severity:
                st.markdown(
                    """
                    <div style="background: #FFF3F0; border-radius: 10px; padding: 1rem; border-left: 4px solid #E0876A; margin-top: 1rem;">
                        <strong style="color: #A23E2A;">⚠️ High Severity Notice:</strong><br>
                        Because you marked this symptom as severe, self-care alone is not advised. Please reach out to your gynecologist or primary care physician for a formal clinical examination.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div style="background: #FFF8FB; border-radius: 10px; padding: 0.8rem; border: 1px solid #E7C9D0; margin-top: 1rem; font-size: 0.85rem; color: #4A3B4F;">
                    <strong style="color: #B97988;">🚩 Red Flag Warnings:</strong><br>
                    {info['urgent_signs']}
                </div>
                """,
                unsafe_allow_html=True,
            )
