"""
API Endpoints for AI Medical Assistant.
Provides endpoints for Chat, Symptom Guidance, Report Summary, Specialist Finder, and Sessions.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from typing import Optional
import json

from app.core.config import settings
from app.core.safety import check_emergency_red_flags
from app.core.session import session_store
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SymptomCheckRequest,
    SymptomCheckResponse,
    ReportSummaryTextRequest,
    ReportSummaryResponse,
    SpecialistRequest,
    SpecialistResponse,
    SessionHistoryResponse,
    SessionMessageItem,
    SafetyNotice,
)
from app.services.router import classify_intent
from app.services.general_chat_service import process_general_chat
from app.services.symptom_service import process_symptom_guidance
from app.services.report_service import process_report_summary, extract_text_from_pdf_bytes
from app.services.specialist_service import recommend_specialists

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat entrypoint with automatic transparent intent classification and safety checks.
    Saves conversation turn to session history.
    """
    session_id = request.session_id
    user_msg = request.message

    # 1. Record user message in session
    session_store.add_message(session_id=session_id, role="user", content=user_msg)

    # 2. Critical Safety Check First
    is_emergency, category, guidance_msg = check_emergency_red_flags(user_msg)
    if is_emergency:
        response = ChatResponse(
            session_id=session_id,
            message=guidance_msg,
            detected_route="emergency_triage",
            routing_reason=f"Emergency red-flag detected: {category}",
            safety=SafetyNotice(
                is_emergency=True,
                emergency_category=category,
                educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
                is_simulated=False,
            ),
            metadata={"emergency": True},
        )
        session_store.add_message(
            session_id=session_id,
            role="assistant",
            content=response.message,
            route="emergency_triage",
            is_emergency=True,
            metadata={"category": category},
        )
        return response

    # 3. Transparent Intent Classification
    route, confidence, reason = classify_intent(user_msg, force_route=request.force_route)

    # 4. Route to specific feature handler
    if route == "symptom_guidance":
        symptom_res = await process_symptom_guidance(symptoms=user_msg, session_id=session_id)
        # Format structured symptom response for chat message
        content = symptom_res.guidance + "\n\n"
        if symptom_res.missing_context_questions:
            content += "**Helpful context questions for your doctor:**\n"
            content += "\n".join(f"• {q}" for q in symptom_res.missing_context_questions) + "\n\n"
        if symptom_res.potential_considerations:
            content += "**Potential educational considerations to discuss:**\n"
            content += "\n".join(f"• {c}" for c in symptom_res.potential_considerations)

        response = ChatResponse(
            session_id=session_id,
            message=content,
            detected_route=route,
            routing_reason=f"{reason} (confidence: {confidence:.2f})",
            safety=symptom_res.safety,
            metadata={"confidence": confidence, "missing_questions": symptom_res.missing_context_questions},
        )

    elif route == "specialist_recommend":
        specialist_res = recommend_specialists(health_concern=user_msg, session_id=session_id)
        content = specialist_res.guidance + "\n\n**Specialist Categories:**\n"
        for s in specialist_res.suggestions:
            badge = " [Recommended Initial Entry Point]" if s.is_primary_entry else ""
            content += f"• **{s.specialty}**{badge}:\n  {s.description}\n  *Relevance:* {s.relevance_reason}\n\n"

        response = ChatResponse(
            session_id=session_id,
            message=content,
            detected_route=route,
            routing_reason=f"{reason} (confidence: {confidence:.2f})",
            safety=specialist_res.safety,
            metadata={"confidence": confidence, "suggestions_count": len(specialist_res.suggestions)},
        )

    elif route == "report_summary":
        report_res = await process_report_summary(report_text=user_msg, session_id=session_id)
        content = report_res.summary + "\n\n"
        if report_res.key_findings_explained:
            content += "**Key Markers Explained in Plain Language:**\n"
            content += "\n".join(f"• {f}" for f in report_res.key_findings_explained) + "\n\n"
        if report_res.questions_for_doctor:
            content += "**Suggested Questions for Your Physician:**\n"
            content += "\n".join(f"• {q}" for q in report_res.questions_for_doctor)

        response = ChatResponse(
            session_id=session_id,
            message=content,
            detected_route=route,
            routing_reason=f"{reason} (confidence: {confidence:.2f})",
            safety=report_res.safety,
            metadata={"confidence": confidence},
        )

    else:
        # Default: General Chat
        response = await process_general_chat(
            message=user_msg,
            session_id=session_id,
            detected_route=route,
            routing_reason=f"{reason} (confidence: {confidence:.2f})",
        )

    # Record assistant message in session
    session_store.add_message(
        session_id=session_id,
        role="assistant",
        content=response.message,
        route=response.detected_route,
        is_emergency=response.safety.is_emergency,
        is_simulated=response.safety.is_simulated,
        metadata=response.metadata,
    )

    return response


@router.post("/symptom-check", response_model=SymptomCheckResponse, status_code=status.HTTP_200_OK)
async def symptom_check_endpoint(request: SymptomCheckRequest):
    """
    Dedicated endpoint for structured symptom evaluation and context-gathering.
    """
    session_store.add_message(
        session_id=request.session_id,
        role="user",
        content=f"Symptom check: {request.symptoms}",
        route="symptom_guidance"
    )

    response = await process_symptom_guidance(
        symptoms=request.symptoms,
        session_id=request.session_id,
        duration=request.duration,
        severity=request.severity,
        additional_context=request.additional_context,
    )

    session_store.add_message(
        session_id=request.session_id,
        role="assistant",
        content=response.guidance,
        route="symptom_guidance",
        is_emergency=response.safety.is_emergency,
        is_simulated=response.safety.is_simulated,
    )

    return response


@router.post("/report-summary", response_model=ReportSummaryResponse, status_code=status.HTTP_200_OK)
async def report_summary_text_endpoint(request: ReportSummaryTextRequest):
    """
    Explains medical report text submitted as JSON.
    """
    session_store.add_message(
        session_id=request.session_id,
        role="user",
        content="[Submitted medical report text for summary]",
        route="report_summary"
    )

    response = await process_report_summary(
        report_text=request.report_text,
        session_id=request.session_id
    )

    session_store.add_message(
        session_id=request.session_id,
        role="assistant",
        content=response.summary,
        route="report_summary",
        is_emergency=response.safety.is_emergency,
        is_simulated=response.safety.is_simulated,
    )

    return response


@router.post("/report-summary/upload", response_model=ReportSummaryResponse, status_code=status.HTTP_200_OK)
async def report_summary_upload_endpoint(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Accepts PDF file upload, extracts digital text safely, and produces an educational summary.
    Validates file extension, MIME type, and size.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF documents (.pdf) are supported."
        )

    try:
        content_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}"
        )

    success, extracted_text, msg = extract_text_from_pdf_bytes(content_bytes, file.filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=msg
        )

    session_store.add_message(
        session_id=session_id,
        role="user",
        content=f"[Uploaded PDF report: {file.filename}]",
        route="report_summary"
    )

    response = await process_report_summary(report_text=extracted_text, session_id=session_id)

    session_store.add_message(
        session_id=session_id,
        role="assistant",
        content=f"Summary of {file.filename}:\n\n{response.summary}",
        route="report_summary",
        is_emergency=response.safety.is_emergency,
        is_simulated=response.safety.is_simulated,
    )

    return response


@router.post("/specialist-recommend", response_model=SpecialistResponse, status_code=status.HTTP_200_OK)
async def specialist_recommend_endpoint(request: SpecialistRequest):
    """
    Dedicated endpoint for suggesting medical specialties based on health concerns.
    """
    session_store.add_message(
        session_id=request.session_id,
        role="user",
        content=f"Specialist query: {request.health_concern}",
        route="specialist_recommend"
    )

    response = recommend_specialists(health_concern=request.health_concern, session_id=request.session_id)

    session_store.add_message(
        session_id=request.session_id,
        role="assistant",
        content=response.guidance,
        route="specialist_recommend",
        is_emergency=response.safety.is_emergency,
        is_simulated=response.safety.is_simulated,
    )

    return response


@router.get("/session/{session_id}", response_model=SessionHistoryResponse, status_code=status.HTTP_200_OK)
async def get_session_history(session_id: str):
    """
    Retrieves message history and metadata for a given session.
    """
    session_data = session_store.get_session(session_id)
    if not session_data:
        # Create fresh session container
        session_data = session_store.get_or_create(session_id)

    messages = [
        SessionMessageItem(
            role=m.role,
            content=m.content,
            timestamp=m.timestamp,
            route=m.route,
            is_emergency=m.is_emergency,
            is_simulated=m.is_simulated,
            metadata=m.metadata,
        )
        for m in session_data.messages
    ]

    security_notice = (
        "MVP Session Security Limitation: Sessions are kept in ephemeral in-memory storage for demo purposes. "
        "Session IDs act as partition keys. A production deployment requires cryptographic session tokens, "
        "user authentication (RBAC), and encrypted storage compliant with HIPAA / GDPR."
    )

    return SessionHistoryResponse(
        session_id=session_id,
        created_at=session_data.created_at,
        updated_at=session_data.updated_at,
        message_count=len(messages),
        messages=messages,
        security_notice=security_notice,
    )


@router.post("/session/{session_id}/clear", status_code=status.HTTP_200_OK)
async def clear_session_endpoint(session_id: str):
    """
    Clears conversation history for the specified session.
    """
    cleared = session_store.clear_session(session_id)
    return {"session_id": session_id, "cleared": cleared, "message": "Session history cleared."}


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check reporting service state and mode.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "Simulated Demo Mode" if settings.is_local_demo_mode else "OpenAI-Compatible Connected Mode",
        "active_sessions": len(session_store.list_active_session_ids()),
        "safety_disclaimer": settings.PERSISTENT_SAFETY_DISCLAIMER,
    }
