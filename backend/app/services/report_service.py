"""
Medical Document and PDF Report Summary Service.
Uses pypdf for secure, sandboxed PDF text extraction.
Treats all extracted text as untrusted user input.
"""

import io
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader
from app.core.config import settings
from app.core.safety import sanitize_untrusted_input, check_emergency_red_flags, enforce_output_guardrails
from app.models.schemas import ReportSummaryResponse, SafetyNotice
from app.services.llm_client import llm_client


def extract_text_from_pdf_bytes(file_bytes: bytes, filename: str) -> Tuple[bool, str, str]:
    """
    Safely extracts digital text from PDF bytes.
    Validates size, format, and handles image-only or unreadable PDFs gracefully.
    Returns: (success: bool, extracted_text_or_error: str, message: str)
    """
    # 1. Size validation
    max_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return False, "", f"File exceeds maximum allowed size of {settings.MAX_PDF_SIZE_MB}MB."

    if not file_bytes:
        return False, "", "The uploaded file is empty (0 bytes)."

    # 2. Extract text using pypdf
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            return False, "", "The uploaded PDF is password-protected or encrypted. Please upload an unprotected file."

        num_pages = len(reader.pages)
        if num_pages == 0:
            return False, "", "The PDF file contains no pages."

        extracted_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_parts.append(page_text)

        raw_text = "\n".join(extracted_parts).strip()

        # Check for scanned / image-only PDFs
        if len(raw_text) < 20:
            return (
                False,
                "",
                "Notice: No readable digital text could be extracted from this PDF. "
                "The document may be a scanned image or photo without an embedded text layer. "
                "For this demonstration, please upload a digital PDF with selectable text or "
                "paste the report values directly."
            )

        # Enforce character truncation limit
        if len(raw_text) > settings.MAX_EXTRACTED_CHARS:
            raw_text = raw_text[:settings.MAX_EXTRACTED_CHARS]

        # Sanitize untrusted input (remove prompt injection / control chars)
        sanitized = sanitize_untrusted_input(raw_text)
        return True, sanitized, f"Successfully extracted text from {num_pages} page(s)."

    except Exception as e:
        return False, "", f"Failed to parse PDF document: {str(e)}. Please ensure it is a valid PDF."


async def process_report_summary(report_text: str, session_id: str) -> ReportSummaryResponse:
    """
    Produces a plain-language summary of medical report text.
    Preserves uncertainty and highlights that reference ranges vary by laboratory.
    """
    # 1. Check for emergency content in text
    is_emergency, category, guidance_msg = check_emergency_red_flags(report_text)
    if is_emergency:
        return ReportSummaryResponse(
            session_id=session_id,
            summary=guidance_msg,
            key_findings_explained=["Urgent or critical findings detected in text."],
            questions_for_doctor=["Seek immediate emergency evaluation."],
            limitations_note="Emergency override: please contact emergency medical care immediately.",
            safety=SafetyNotice(
                is_emergency=True,
                emergency_category=category,
                educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
                is_simulated=False,
            ),
        )

    # 2. Identify common educational lab markers in text
    norm = report_text.lower()
    findings_explained = []

    if "hemoglobin" in norm or "hgb" in norm:
        findings_explained.append(
            "Hemoglobin: An iron-rich protein in red blood cells that carries oxygen from the lungs throughout the body. "
            "Values can reflect hydration, nutritional status, or red cell production."
        )
    if "wbc" in norm or "white blood cell" in norm:
        findings_explained.append(
            "White Blood Cells (WBC): Cells of the immune system that defend against infections. Counts may temporarily fluctuate "
            "due to physical stress, viral or bacterial exposure, or inflammation."
        )
    if "platelet" in norm:
        findings_explained.append(
            "Platelets: Small cell fragments essential for normal blood clotting and tissue repair."
        )
    if "cholesterol" in norm or "lipid" in norm or "triglyceride" in norm:
        findings_explained.append(
            "Lipid Panel (Cholesterol / Triglycerides): Assesses fats circulating in the bloodstream. "
            "Helps clinicians assess long-term cardiovascular profile alongside lifestyle and family history."
        )
    if "creatinine" in norm or "egfr" in norm:
        findings_explained.append(
            "Creatinine / eGFR: Markers related to muscle breakdown and kidney filtration efficiency. "
            "Can temporarily shift based on hydration, muscle mass, or intense exercise."
        )
    if "glucose" in norm or "hba1c" in norm:
        findings_explained.append(
            "Glucose / HbA1c: Reflects circulating blood sugar (fasting or a ~3-month average via HbA1c). "
            "Interpreted alongside diet, fasting state, and metabolic history."
        )

    if not findings_explained:
        findings_explained.append(
            "General Diagnostic Report Text: The document contains general clinical or diagnostic notes. "
            "Specific abbreviations and numerical figures require clinical context for accurate evaluation."
        )

    questions_for_doctor = [
        "How do these specific test results compare with my previous baseline lab work?",
        "Do any values outside the standard reference range require follow-up testing or lifestyle adjustments?",
        "Were any of these results influenced by recent diet, fasting duration, or current medications?",
        "What next steps or repeat tests do you recommend based on this report?",
    ]

    limitations_note = (
        "Educational summary only. Laboratory reference ranges differ between testing facilities, instruments, "
        "and individual clinical baselines. This summary may be incomplete and is not clinical interpretation "
        "or diagnostic validation."
    )

    # Generate summary through LLM / local demo engine
    system_prompt = (
        "You are an educational medical text explainer. Summarize the provided laboratory or clinical report in clear, "
        "approachable language. Preserve uncertainty: clearly state that reference ranges vary, findings must be discussed "
        "with the ordering physician, and do not declare definitive diagnoses or clinical certainties."
    )
    user_prompt = f"Please explain the following extracted medical report text in plain language:\n\n{report_text[:4000]}"

    llm_resp = await llm_client.generate_chat_completion(system_prompt, user_prompt)
    summary_text = enforce_output_guardrails(llm_resp["content"], is_emergency=False)

    return ReportSummaryResponse(
        session_id=session_id,
        summary=summary_text,
        key_findings_explained=findings_explained,
        questions_for_doctor=questions_for_doctor,
        limitations_note=limitations_note,
        safety=SafetyNotice(
            is_emergency=False,
            emergency_category=None,
            educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
            is_simulated=llm_resp["is_simulated"],
        ),
    )
