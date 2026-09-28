"""
LunaCare: Prompt Engineering Demonstrations
-------------------------------------------
Demonstrates core prompt engineering patterns from the Week 2 Syllabus:
1. Zero-shot Prompting: Prompting without exemplars.
2. Few-shot Prompting: Providing curated input/output demonstration pairs.
3. Role Prompting: Defining behavior through persona framing.
4. Structured Prompting: Multi-part prompt architecture with explicit constraints.
"""

from prompts.system_prompt import LUNACARE_SYSTEM_INSTRUCTION, get_structured_prompt

# Curated few-shot exemplars demonstrating desired tone, safety, and formatting
FEW_SHOT_EXEMPLARS = [
    {
        "user": "What causes menstrual cramps?",
        "assistant": (
            "Menstrual cramps (dysmenorrhea) are very common and can feel quite uncomfortable. "
            "They are primarily caused by the natural release of prostaglandins—hormone-like compounds "
            "produced by the uterine lining that prompt uterine muscles to contract and shed the endometrium.\n\n"
            "Key physiological factors include:\n"
            "- **Prostaglandin levels**: Higher concentrations are typically linked to more intense cramping.\n"
            "- **Muscle contractions**: These temporary contractions briefly reduce blood flow to the uterus, causing localized discomfort.\n\n"
            "**Gentle supportive practices:**\n"
            "- Applying a warm heating pad to your lower abdomen or lower back.\n"
            "- Gentle pelvic stretches such as Child's Pose or light walking.\n"
            "- Staying well hydrated with warm water or herbal teas (like ginger or chamomile).\n\n"
            "If cramps are severe, sudden, or prevent you from carrying out normal daily activities, "
            "it is always wise to consult a gynecologist or healthcare provider to explore potential underlying causes."
        ),
    },
    {
        "user": "I missed my period this month, am I sick?",
        "assistant": (
            "Missing a period can certainly feel stressful, but it does not automatically mean you are sick. "
            "Menstrual cycles are sensitive to many everyday physiological factors.\n\n"
            "Common reasons a cycle might be delayed or skipped include:\n"
            "- **Stress or anxiety**: Elevated cortisol can temporarily disrupt the hormonal signals that trigger ovulation.\n"
            "- **Recent lifestyle shifts**: Significant changes in diet, sleep patterns, intense athletic training, or travel across time zones.\n"
            "- **Hormonal conditions**: Such as Polycystic Ovary Syndrome (PCOS) or thyroid imbalances.\n"
            "- **Pregnancy**: If you are sexually active, a home pregnancy test is often a practical first step.\n\n"
            "Because an isolated missed cycle can occur for benign reasons, tracking your symptoms is helpful. "
            "However, if your period is absent for more than two or three consecutive cycles, or if you experience "
            "unusual pain, discussing this with your healthcare provider will give you personalized answers and peace of mind."
        ),
    },
]


def build_zero_shot_prompt(user_query: str) -> str:
    """
    Builds a Zero-Shot prompt: Direct task instruction without any prior demonstration pairs.
    """
    return (
        f"Answer the following female health question in a clear, educational, "
        f"and compassionate manner without providing medical diagnoses:\n\n"
        f"Question: {user_query}\n\n"
        f"Answer:"
    )


def build_few_shot_prompt(user_query: str) -> str:
    """
    Builds a Few-Shot prompt: Injects demonstration pairs to guide tone,
    structure, and clinical safety boundaries before the target query.
    """
    prompt_lines = [
        "Below are examples of how an empathetic, educational female health assistant responds:\n"
    ]
    for idx, ex in enumerate(FEW_SHOT_EXEMPLARS, 1):
        prompt_lines.append(f"Example {idx}:")
        prompt_lines.append(f"User: {ex['user']}")
        prompt_lines.append(f"Assistant: {ex['assistant']}\n")

    prompt_lines.append("Now respond to this user question with the same supportive, non-diagnostic style:")
    prompt_lines.append(f"User: {user_query}")
    prompt_lines.append("Assistant:")

    return "\n".join(prompt_lines)


def build_role_prompt(user_query: str) -> str:
    """
    Builds a Role-based prompt embedding LunaCare's persona directly into the user message.
    """
    return (
        f"{LUNACARE_SYSTEM_INSTRUCTION}\n\n"
        f"User Inquiry: {user_query}\n\n"
        f"LunaCare Response:"
    )
