"""
Pydantic Request and Response Schemas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# Common Safety Response Model
class SafetyNotice(BaseModel):
    is_emergency: bool = False
    emergency_category: Optional[str] = None
    educational_disclaimer: str
    is_simulated: bool = False


# Chat endpoint schemas
class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or message")
    session_id: str = Field(..., description="Unique session identifier (e.g. UUID)")
    force_route: Optional[str] = Field(
        None,
        description="Optional manual route override: 'general_chat', 'symptom_guidance', 'report_summary', 'specialist_recommend'"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty or whitespace only.")
        if len(trimmed) > 10000:
            raise ValueError("Message exceeds maximum allowed length (10,000 characters).")
        return trimmed

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Session ID cannot be empty.")
        return trimmed


class ChatResponse(BaseModel):
    session_id: str
    message: str
    detected_route: str
    routing_reason: str
    safety: SafetyNotice
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Symptom Check endpoint schemas
class SymptomCheckRequest(BaseModel):
    symptoms: str = Field(..., description="Description of symptoms experienced")
    session_id: str = Field(..., description="Session identifier")
    duration: Optional[str] = Field(None, description="How long symptoms have lasted (e.g., '2 days')")
    severity: Optional[str] = Field(None, description="Severity rating or description (e.g., 'mild', '6/10')")
    additional_context: Optional[str] = Field(None, description="Triggers, medical background, age, or medications")

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Symptoms description cannot be empty.")
        return trimmed


class SymptomCheckResponse(BaseModel):
    session_id: str
    guidance: str
    missing_context_questions: List[str]
    potential_considerations: List[str]
    when_to_seek_urgent_care: List[str]
    safety: SafetyNotice


# Report Summary endpoint schemas
class ReportSummaryTextRequest(BaseModel):
    report_text: str = Field(..., description="Extracted medical report text to summarize")
    session_id: str = Field(..., description="Session identifier")

    @field_validator("report_text")
    @classmethod
    def validate_report_text(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Report text cannot be empty.")
        return trimmed


class ReportSummaryResponse(BaseModel):
    session_id: str
    summary: str
    key_findings_explained: List[str]
    questions_for_doctor: List[str]
    limitations_note: str
    safety: SafetyNotice


# Specialist Recommendation endpoint schemas
class SpecialistRequest(BaseModel):
    health_concern: str = Field(..., description="Symptoms, condition, or question to match with medical specialties")
    session_id: str = Field(..., description="Session identifier")

    @field_validator("health_concern")
    @classmethod
    def validate_concern(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Health concern cannot be empty.")
        return trimmed


class SpecialistSuggestion(BaseModel):
    specialty: str
    description: str
    relevance_reason: str
    is_primary_entry: bool = False


class SpecialistResponse(BaseModel):
    session_id: str
    suggestions: List[SpecialistSuggestion]
    guidance: str
    safety: SafetyNotice


# Session History schemas
class SessionMessageItem(BaseModel):
    role: str
    content: str
    timestamp: float
    route: Optional[str] = None
    is_emergency: bool = False
    is_simulated: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionHistoryResponse(BaseModel):
    session_id: str
    created_at: float
    updated_at: float
    message_count: int
    messages: List[SessionMessageItem]
    security_notice: str
