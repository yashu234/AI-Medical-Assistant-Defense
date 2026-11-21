"""
Specialist Recommendation Service.
Suggests relevant medical specialties as possibilities rather than definitive referrals.
Always recommends Primary Care as the initial point of contact.
"""

from typing import List, Dict, Any
from app.core.config import settings
from app.core.safety import check_emergency_red_flags
from app.models.schemas import SpecialistResponse, SpecialistSuggestion, SafetyNotice


# Comprehensive catalog of medical specialties
SPECIALTY_CATALOG: List[Dict[str, Any]] = [
    {
        "specialty": "Primary Care Physician (PCP) / General Practitioner",
        "description": "Generalist physician specializing in comprehensive care, initial evaluation, preventive medicine, and coordinating specialty referrals.",
        "keywords": ["general", "routine", "checkup", "unclear", "first", "initial", "fatigue", "weight"],
        "is_primary": True,
        "default_relevance": "Recommended first point of clinical assessment for thorough physical exam, baseline lab work, and appropriate referral."
    },
    {
        "specialty": "Cardiologist",
        "description": "Specialist in the cardiovascular system, including the heart, blood vessels, and circulation.",
        "keywords": ["heart", "cardio", "palpitation", "arrhythmia", "murmur", "cholesterol", "hypertension", "blood pressure", "chest"],
        "is_primary": False,
        "default_relevance": "Evaluates cardiovascular symptoms, rhythm disturbances, and long-term heart health."
    },
    {
        "specialty": "Dermatologist",
        "description": "Specialist in conditions affecting the skin, hair, nails, and mucous membranes.",
        "keywords": ["skin", "rash", "mole", "acne", "eczema", "psoriasis", "itching", "lesion", "melanoma", "dermatitis"],
        "is_primary": False,
        "default_relevance": "Assesses and manages cutaneous lesions, chronic rashes, allergic skin reactions, and moles."
    },
    {
        "specialty": "Gastroenterologist",
        "description": "Specialist in the digestive system, including esophagus, stomach, intestines, liver, gallbladder, and pancreas.",
        "keywords": ["stomach", "digest", "acid", "reflux", "gerd", "bowel", "diarrhea", "constipation", "bloat", "colon", "liver", "gut"],
        "is_primary": False,
        "default_relevance": "Investigates persistent gastrointestinal complaints, abdominal pain, or changes in digestion."
    },
    {
        "specialty": "Neurologist",
        "description": "Specialist in disorders of the nervous system, brain, spinal cord, and peripheral nerves.",
        "keywords": ["nerve", "neuropathy", "headache", "migraine", "tingling", "numbness", "tremor", "seizure", "vertigo", "memory", "brain"],
        "is_primary": False,
        "default_relevance": "Specializes in assessing complex headaches, nerve sensations, balance issues, or cognitive symptoms."
    },
    {
        "specialty": "Orthopedic Specialist / Orthopedist",
        "description": "Specialist in bones, joints, ligaments, tendons, and musculoskeletal biomechanics.",
        "keywords": ["bone", "joint", "knee", "shoulder", "hip", "ankle", "spine", "fracture", "ligament", "sprain", "cartilage", "tendon"],
        "is_primary": False,
        "default_relevance": "Evaluates structural joint pain, mobility limitations, ligament injuries, and musculoskeletal wear."
    },
    {
        "specialty": "Otolaryngologist (Ear, Nose & Throat / ENT)",
        "description": "Specialist in the ear, nose, throat, sinuses, and related head/neck structures.",
        "keywords": ["ear", "nose", "throat", "sinus", "hearing", "tinnitus", "tonsil", "swallowing", "hoarse", "vocal", "congestion"],
        "is_primary": False,
        "default_relevance": "Evaluates chronic sinus congestion, ear discomfort, hearing changes, or persistent throat concerns."
    },
    {
        "specialty": "Endocrinologist",
        "description": "Specialist in endocrine glands, hormonal regulation, diabetes, and metabolic disorders.",
        "keywords": ["hormone", "thyroid", "diabetes", "metabolism", "adrenal", "testosterone", "estrogen", "insulin", "pituitary"],
        "is_primary": False,
        "default_relevance": "Addresses hormonal imbalances, thyroid function disorders, and complex glycemic management."
    },
    {
        "specialty": "Pulmonologist",
        "description": "Specialist in the respiratory system, lungs, airways, and breathing physiology.",
        "keywords": ["lung", "respiratory", "asthma", "copd", "bronchitis", "chronic cough", "wheeze", "breathing", "sleep apnea"],
        "is_primary": False,
        "default_relevance": "Investigates chronic respiratory symptoms, airway reactivity, and pulmonary function."
    },
    {
        "specialty": "Rheumatologist",
        "description": "Specialist in systemic autoimmune diseases, arthritis, and connective tissue disorders.",
        "keywords": ["arthritis", "autoimmune", "lupus", "rheumatoid", "joint swelling", "morning stiffness", "fibromyalgia"],
        "is_primary": False,
        "default_relevance": "Assesses systemic inflammatory conditions and multi-joint swelling or autoimmune markers."
    },
    {
        "specialty": "Psychiatrist / Licensed Mental Health Professional",
        "description": "Specialist in mental health, emotional wellness, mood regulation, and behavioral health.",
        "keywords": ["anxiety", "depression", "panic", "mental health", "mood", "stress", "trauma", "insomnia", "adhd", "ptsd"],
        "is_primary": False,
        "default_relevance": "Provides clinical evaluation, counseling, and therapeutic support for mental and emotional well-being."
    },
]


def recommend_specialists(health_concern: str, session_id: str) -> SpecialistResponse:
    """
    Identifies relevant medical specialties for a given health concern.
    Always includes Primary Care and frames suggestions as possibilities.
    """
    # 1. Emergency Check First
    is_emergency, category, guidance_msg = check_emergency_red_flags(health_concern)
    if is_emergency:
        return SpecialistResponse(
            session_id=session_id,
            suggestions=[
                SpecialistSuggestion(
                    specialty="Emergency Medicine Physician",
                    description="Physicians specialized in acute, life-saving resuscitation and emergency department care.",
                    relevance_reason="Immediate emergency medical evaluation is necessary.",
                    is_primary_entry=True,
                )
            ],
            guidance=guidance_msg,
            safety=SafetyNotice(
                is_emergency=True,
                emergency_category=category,
                educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
                is_simulated=False,
            ),
        )

    norm = health_concern.lower()
    matched_specialties: List[SpecialistSuggestion] = []

    # Always add Primary Care Physician as the foundational entry point
    pcp = SPECIALTY_CATALOG[0]
    matched_specialties.append(
        SpecialistSuggestion(
            specialty=pcp["specialty"],
            description=pcp["description"],
            relevance_reason=pcp["default_relevance"],
            is_primary_entry=True,
        )
    )

    # Check other specialties against keywords
    for item in SPECIALTY_CATALOG[1:]:
        if any(kw in norm for kw in item["keywords"]):
            matched_specialties.append(
                SpecialistSuggestion(
                    specialty=item["specialty"],
                    description=item["description"],
                    relevance_reason=item["default_relevance"],
                    is_primary_entry=False,
                )
            )

    # If no specific secondary specialty was matched, provide common complementary examples
    if len(matched_specialties) == 1:
        matched_specialties.append(
            SpecialistSuggestion(
                specialty="Internal Medicine Specialist",
                description="Physicians focused on adult medicine, complex multi-system conditions, and chronic disease diagnostics.",
                relevance_reason="Useful when symptoms are generalized or involve multiple body systems.",
                is_primary_entry=False,
            )
        )

    guidance = (
        "These specialist categories are possibilities for your consideration and discussion. "
        "They are not formal clinical referrals. In most healthcare systems, starting with your "
        "Primary Care Physician (PCP) is the most efficient and recommended step: they can conduct "
        "an initial physical examination, order baseline testing, and guide you to the exact subspecialist if required."
    )

    return SpecialistResponse(
        session_id=session_id,
        suggestions=matched_specialties,
        guidance=guidance,
        safety=SafetyNotice(
            is_emergency=False,
            emergency_category=None,
            educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
            is_simulated=False,
        ),
    )
