"""
General Health Chat Service.
Handles general wellness, biological concepts, and health education inquiries.
"""

from app.core.config import settings
from app.core.safety import check_emergency_red_flags, enforce_output_guardrails
from app.models.schemas import ChatResponse, SafetyNotice
from app.services.llm_client import llm_client


async def process_general_chat(
    message: str,
    session_id: str,
    detected_route: str = "general_chat",
    routing_reason: str = "General health education",
) -> ChatResponse:
    """
    Handles educational health Q&A adhering to strict safety rules.
    """
    # 1. Emergency Check First
    is_emergency, category, guidance_msg = check_emergency_red_flags(message)
    if is_emergency:
        return ChatResponse(
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

    system_prompt = (
        "You are an educational AI healthcare assistant. You provide evidence-informed, general health education. "
        "Strict rules: Never diagnose illness, never prescribe treatments or specific medication dosages, "
        "and never urge users to delay seeing a doctor. Maintain a helpful, empathetic, yet objective educational tone."
    )

    llm_resp = await llm_client.generate_chat_completion(system_prompt, message)
    content = enforce_output_guardrails(llm_resp["content"], is_emergency=False)

    return ChatResponse(
        session_id=session_id,
        message=content,
        detected_route=detected_route,
        routing_reason=routing_reason,
        safety=SafetyNotice(
            is_emergency=False,
            emergency_category=None,
            educational_disclaimer=settings.PERSISTENT_SAFETY_DISCLAIMER,
            is_simulated=llm_resp["is_simulated"],
        ),
        metadata={
            "model": llm_resp.get("model", "unknown"),
            "is_simulated": llm_resp["is_simulated"],
        },
    )
