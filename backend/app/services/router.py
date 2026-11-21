"""
Transparent Intent Routing Layer.
Classifies user queries into discrete healthcare assistance features.
"""

import re
from typing import Tuple


ROUTES = {
    "symptom_guidance": "Symptom Guidance (analyzing symptoms and gathering context)",
    "report_summary": "Medical Report Summary (explaining lab results or medical documents)",
    "specialist_recommend": "Specialist Suggestion (identifying relevant medical specialties)",
    "general_chat": "General Health Education (health concepts, wellness, preventative care)",
}

# Regex patterns for deterministic classification
SPECIALIST_PATTERNS = [
    r"\b(what|which)\s+(kind\s+of\s+)?(doctor|physician|specialist)\b",
    r"\bwho\s+should\s+i\s+(see|consult|visit|go\s+to)\b",
    r"\b(need|recommend)\s+a\s+specialist\b",
    r"\b(specialist|referral|specialty)\b",
    r"\bdo\s+i\s+need\s+a\s+(cardiologist|dermatologist|neurologist|gastroenterologist|orthopedic|ent|psychiatrist|endocrinologist|rheumatologist)\b",
]

REPORT_PATTERNS = [
    r"\b(lab\s+report|blood\s+test|test\s+results?|lab\s+results?|medical\s+records?)\b",
    r"\b(pdf|document|biopsy|mri|ct\s+scan|ultrasound|x-?ray|echocardiogram)\b",
    r"\b(cbc|hemoglobin|platelets?|wbc|rbc|creatinine|alt|ast|cholesterol|triglycerides|fasting\s+glucose|hba1c)\b",
    r"\bwhat\s+does\s+my\s+(report|result|lab)\s+mean\b",
    r"\bexplain\s+(this|my)\s+(report|result|test)\b",
]

SYMPTOM_PATTERNS = [
    r"\b(i\s+have|i'?m\s+having|i\s+feel|i\s+am\s+experiencing)\s+.*\b(pain|ache|fever|cough|sore|fatigue|nausea|vomit|dizzy|dizziness|rash|swelling|cramp|diarrhea|headache|chills|burning)\b",
    r"\b(my\s+(head|throat|chest|stomach|back|knee|foot|arm|leg|ear|eye|neck|abdomen|joint)\s+(hurts|aches|is\s+sore|is\s+stiff|is\s+swollen))\b",
    r"\b(symptom|symptoms)\b",
    r"\bhow\s+to\s+treat\s+(my\s+)?(fever|cough|headache|cold|flu|rash|burn)\b",
    r"\bwhy\s+does\s+my\s+.*\s+(hurt|ache|burn|itch)\b",
]


def classify_intent(message: str, force_route: str = None) -> Tuple[str, float, str]:
    """
    Classifies a user query into one of the four supported healthcare features.
    Returns: (route_name, confidence, reason)
    """
    if force_route and force_route in ROUTES:
        return force_route, 1.0, f"User explicitly selected route: {ROUTES[force_route]}"

    normalized = message.lower().strip()

    # Check for Specialist Referral intent
    for pattern in SPECIALIST_PATTERNS:
        if re.search(pattern, normalized):
            return "specialist_recommend", 0.95, "Matched specialist referral query pattern"

    # Check for Medical Report / Lab Test intent
    for pattern in REPORT_PATTERNS:
        if re.search(pattern, normalized):
            return "report_summary", 0.92, "Matched medical report/lab result terminology"

    # Check for Symptom Guidance intent
    for pattern in SYMPTOM_PATTERNS:
        if re.search(pattern, normalized):
            return "symptom_guidance", 0.90, "Matched personal symptom description pattern"

    # Secondary check: general mentions of symptoms without first-person
    if any(k in normalized for k in ["fever", "cough", "headache", "stomachache", "nausea", "rash", "congestion"]):
        return "symptom_guidance", 0.75, "Detected symptom keywords in query"

    # Secondary check: report terms
    if any(k in normalized for k in ["lab", "result", "ranges", "mg/dl", "mmol/l"]):
        return "report_summary", 0.75, "Detected medical report units or keywords"

    # Default to General Health Chat
    return "general_chat", 0.80, "Classified as general health or educational inquiry"
