"""
Symptom Guidance Service.
Gathers missing context, avoids definitive diagnosis, and provides structured clinical context.
"""

from typing import Dict, Any, List
from app.core.safety import check_emergency_red_flags, enforce_output_guardrails
from app.core.config import settings
from app.models.schemas import SymptomCheckResponse, SafetyNotice
from app.services.llm_client import llm_client


async def process_symptom_guidance(
    symptoms: str,
    session_id: str,
    duration: str = None,
    severity: str = None,
    additional_context: str = None,
) -> SymptomCheckResponse:
    """
    Evaluates reported symptoms, identifies missing context,
    and returns non-definitive health education guidance.
    """
    combined_text = f"{symptoms} {duration or ''} {severity or ''} {additional_context or ''}"

    # 1. Critical Emergency Check FIRST
    is_emergency, category, guidance_msg = check_emergency_red_flags(combined_text)
    if is_emergency:
        return SymptomCheckResponse(
            session_id=session_id,
            guidance=guidance_msg,
            missing_context_questions=[],
            potential_considerations=["Immediate emergency medical evaluation required."],
            when_to_seek_urgent_care=[
                "Seek immediate emergency medical care (call 911 / 999 / 112 or visit nearest Emergency Room)."
            ],
            safety=SafetyNotice(
                is_emergency=True,
                emergency_category=category,
                educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
                is_simulated=False,
            ),
        )

    # 2. Identify missing context questions to assist physician discussion
    missing_questions: List[str] = []
    if not duration:
        missing_questions.append("When did these symptoms first begin, and have they been constant or intermittent?")
    if not severity:
        missing_questions.append("On a scale from 1 to 10 (or mild/moderate/severe), how would you describe the intensity?")
    if not additional_context:
        missing_questions.append("Are there any known triggers, related symptoms, or relevant past medical conditions?")
    missing_questions.append("Are you currently taking any prescription medications or over-the-counter supplements?")

    # 3. Determine potential educational considerations (never definitive diagnoses)
    sym_lower = symptoms.lower()
    considerations: List[str] = []

    if any(k in sym_lower for k in ["cough", "fever", "throat", "congestion"]):
        considerations.extend([
            "Upper respiratory tract viral infections (e.g., common cold, influenza).",
            "Seasonal allergic rhinitis or environmental airway irritation.",
            "Bacterial respiratory conditions (which require clinician evaluation for targeted care).",
        ])
    elif any(k in sym_lower for k in ["headache", "migraine"]):
        considerations.extend([
            "Tension-type headaches related to stress, eye strain, or muscular tension.",
            "Migraine-related symptoms, often accompanied by sensitivity to light or sound.",
            "Dehydration, caffeine withdrawal, or sleep disturbances.",
        ])
    elif any(k in sym_lower for k in ["stomach", "nausea", "abdomen", "diarrhea"]):
        considerations.extend([
            "Acute gastroenteritis (viral or dietary intolerance).",
            "Gastric acid irritation, reflux, or dyspepsia.",
            "Digestive sensitivity or hydration imbalance.",
        ])
    elif any(k in sym_lower for k in ["knee", "joint", "back", "stiff"]):
        considerations.extend([
            "Musculoskeletal strain or ligamentous overexertion.",
            "Postural or ergonomic biomechanical stress.",
            "Inflammatory or degenerative joint considerations to evaluate with a clinician.",
        ])
    else:
        considerations.extend([
            "Symptoms often have multiple overlapping etiologies ranging from benign fatigue to mild infection.",
            "A physician will assess these symptoms alongside physical vital signs and personal medical history.",
        ])

    # 4. Standard 'When to seek urgent care' red flags
    when_to_seek = [
        "Difficulty breathing, persistent chest pain, or feeling faint.",
        "High fever not responding to fluids/rest or lasting longer than 72 hours.",
        "Sudden, severe neurological changes (confusion, slurred speech, one-sided weakness).",
        "Severe, worsening pain that prevents normal daily activities or sleep.",
    ]

    # 5. Formulate educational narrative
    system_prompt = (
        "You are an educational healthcare assistant. Provide supportive, non-definitive symptom guidance. "
        "Strict rules: Never diagnose disease, never prescribe medications or dosages, never suggest delaying care. "
        "Highlight that symptoms can have multiple causes and recommend discussing these points with a doctor."
    )
    user_prompt = (
        f"Symptoms reported: {symptoms}\n"
        f"Duration: {duration or 'Not specified'}\n"
        f"Severity: {severity or 'Not specified'}\n"
        f"Additional context: {additional_context or 'None'}"
    )

    llm_resp = await llm_client.generate_chat_completion(system_prompt, user_prompt)
    sanitized_guidance = enforce_output_guardrails(llm_resp["content"], is_emergency=False)

    return SymptomCheckResponse(
        session_id=session_id,
        guidance=sanitized_guidance,
        missing_context_questions=missing_questions,
        potential_considerations=considerations,
        when_to_seek_urgent_care=when_to_seek,
        safety=SafetyNotice(
            is_emergency=False,
            emergency_category=None,
            educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
            is_simulated=llm_resp["is_simulated"],
        ),
    )
