"""
Safety and Guardrails Module.
Critical safety checks run ahead of any model invocations or routing.
"""

import re
from typing import Tuple, Optional, Dict, Any, List


# Emergency Red-Flag Trigger Categories
EMERGENCY_PATTERNS: List[Dict[str, Any]] = [
    {
        "category": "Cardiac / Acute Coronary",
        "patterns": [
            r"\b(crushing|severe|squeezing)\s+(chest\s+pain|chest\s+pressure)\b",
            r"\bchest\s+pain\b.*\b(left\s+arm|jaw|back|sweat|shortness\s+of\s+breath)\b",
            r"\b(heart\s+attack|myocardial\s+infarction)\b",
            r"\bpain\s+radiating\s+(down|to)\s+(my\s+)?(left\s+arm|jaw)\b",
        ]
    },
    {
        "category": "Respiratory Distress",
        "patterns": [
            r"\b(can'?t\s+breathe|unable\s+to\s+breathe|gasping\s+for\s+air|suffocating)\b",
            r"\b(severe\s+shortness\s+of\s+breath|lips\s+turning\s+blue|cyanosis)\b",
            r"\bchoking\b",
            r"\bsevere\s+asthma\s+attack\s+not\s+responding\b",
        ]
    },
    {
        "category": "Neurological / Stroke (FAST)",
        "patterns": [
            r"\b(sudden\s+weakness|sudden\s+numbness)\s+(on\s+one\s+side|in\s+(my\s+)?(face|arm|leg))\b",
            r"\b(facial\s+droop|slurred\s+speech|cannot\s+speak|difficulty\s+speaking\s+suddenly)\b",
            r"\b(stroke|mini[- ]stroke|tia)\b",
            r"\b(worst\s+headache\s+of\s+my\s+life|thunderclap\s+headache|sudden\s+severe\s+headache)\b",
            r"\b(unconscious|passed\s+out|collapsed|unresponsive)\b",
        ]
    },
    {
        "category": "Anaphylaxis / Severe Allergy",
        "patterns": [
            r"\b(throat\s+(is\s+)?closing|swelling\s+of\s+(the\s+)?(tongue|throat|lips))\b",
            r"\b(anaphylaxis|anaphylactic\s+shock)\b",
            r"\bsevere\s+allergic\s+reaction\s+with\s+(trouble|difficulty)\s+breathing\b",
        ]
    },
    {
        "category": "Severe Hemorrhage / Trauma",
        "patterns": [
            r"\b(uncontrollable\s+bleeding|coughing\s+up\s+large\s+amounts\s+of\s+blood|vomiting\s+blood)\b",
            r"\b(severe\s+head\s+injury|major\s+trauma|compound\s+fracture)\b",
        ]
    },
    {
        "category": "Crisis / Self-Harm",
        "patterns": [
            r"\b(suicide|kill\s+myself|end\s+my\s+life|self[- ]harm|overdose\s+intentionally)\b",
            r"\bwant\s+to\s+die\b",
        ]
    },
    {
        "category": "Acute Poisoning / Overdose",
        "patterns": [
            r"\b(swallowed\s+poison|drank\s+bleach|took\s+too\s+many\s+pills|drug\s+overdose)\b",
        ]
    }
]

# Patterns that attempt prompt injection or rule override
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"override\s+(the\s+)?system\s+prompt",
    r"you\s+are\s+now\s+a\s+doctor",
    r"diagnose\s+me\s+definitively",
    r"act\s+as\s+an\s+unrestricted\s+ai",
    r"bypass\s+(safety|medical)\s+guidelines",
    r"jailbreak",
]


def check_emergency_red_flags(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Scans input for life-threatening emergency symptoms.
    Returns: (is_emergency, category, guidance_message)
    """
    if not text:
        return False, None, None

    normalized = text.lower()

    for item in EMERGENCY_PATTERNS:
        category = item["category"]
        for pattern in item["patterns"]:
            if re.search(pattern, normalized, re.IGNORECASE):
                guidance = (
                    "EMERGENCY ALERT: Your message contains indications of a potentially "
                    f"life-threatening emergency ({category}).\n\n"
                    "⚠️ STOP using this chatbot immediately and seek emergency medical care:\n"
                    "• Call emergency services right away: 911 (US/Canada), 999 (UK), 112 (Europe/India), or your local emergency line.\n"
                    "• If you are able to do so safely, go to the nearest hospital Emergency Room (ER).\n"
                    "• If this is a mental health crisis, contact the Suicide & Crisis Lifeline (call or text 988 in the US/Canada), or text HOME to 741741.\n\n"
                    "This educational tool cannot provide emergency triage or medical intervention."
                )
                return True, category, guidance

    return False, None, None


def sanitize_untrusted_input(text: str) -> str:
    """
    Sanitizes untrusted input (especially PDF extracted text or user messages).
    Neutralizes null bytes, control characters, and marks potential prompt injection.
    """
    if not text:
        return ""

    # Strip null bytes and non-printable control characters except tabs and newlines
    cleaned = "".join(ch for ch in text if ch in "\t\n\r" or (32 <= ord(ch) <= 126) or ord(ch) > 127)

    # Check for prompt injection attempts
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            cleaned = re.sub(pattern, "[FILTERED_INSTRUCTION_OVERRIDE_ATTEMPT]", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def enforce_output_guardrails(response_text: str, is_emergency: bool = False) -> str:
    """
    Post-processes generated text to ensure no definitive diagnoses, prescriptions,
    or dangerous certainty language is output.
    """
    if is_emergency:
        return response_text

    # Soften any accidental definitive diagnostic statements
    replacements = [
        (r"\bYou have ([A-Za-z ]+)\.", r"These symptoms could be consistent with \1, among other possibilities."),
        (r"\bI diagnose you with\b", "A clinician might consider"),
        (r"\bTake (\d+\s*(?:mg|ml|tablets?|pills?))\b", "Medication dosages must be determined by a licensed prescriber (dosage withheld)"),
        (r"\bDon't worry about seeing a doctor\b", "Please consult a healthcare professional"),
        (r"\bNo need to see a doctor\b", "Professional clinical evaluation is recommended"),
    ]

    result = response_text
    for pattern, repl in replacements:
        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)

    return result
