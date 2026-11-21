"""
Integration and End-to-End API endpoint tests using FastAPI TestClient.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Simulated Demo Mode" in data["mode"] or "OpenAI" in data["mode"]
    assert "Educational demo only" in data["safety_disclaimer"]


def test_chat_general_flow():
    payload = {
        "message": "What is the difference between LDL and HDL cholesterol?",
        "session_id": "test-session-chat-1"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-chat-1"
    assert data["detected_route"] == "report_summary" or data["detected_route"] == "general_chat"
    assert "LDL" in data["message"] or "cholesterol" in data["message"].lower()
    assert data["safety"]["is_emergency"] is False


def test_chat_emergency_interception():
    payload = {
        "message": "Help, I am having severe crushing chest pain radiating to my left arm and jaw!",
        "session_id": "test-session-emergency"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_route"] == "emergency_triage"
    assert data["safety"]["is_emergency"] is True
    assert data["safety"]["emergency_category"] == "Cardiac / Acute Coronary"
    assert "911" in data["message"] or "EMERGENCY ALERT" in data["message"]


def test_symptom_check_endpoint():
    payload = {
        "symptoms": "I have had a mild dry cough and slight scratchy throat",
        "duration": "2 days",
        "severity": "mild",
        "additional_context": "No fever, seasonal allergy history",
        "session_id": "test-session-symptom"
    }
    response = client.post("/symptom-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "guidance" in data
    assert len(data["missing_context_questions"]) > 0
    assert len(data["potential_considerations"]) > 0
    assert len(data["when_to_seek_urgent_care"]) > 0


def test_specialist_recommend_endpoint():
    payload = {
        "health_concern": "I have persistent pain and swelling in my knee after running",
        "session_id": "test-session-specialist"
    }
    response = client.post("/specialist-recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    specialties = [s["specialty"] for s in data["suggestions"]]
    assert any("Primary Care" in s for s in specialties)
    assert any("Orthopedic" in s for s in specialties)


def test_report_summary_text_endpoint():
    payload = {
        "report_text": "Complete Blood Count: WBC 6.8 x10^3/uL, Hemoglobin 14.2 g/dL, Platelets 245 x10^3/uL. Lipid Panel: Total Cholesterol 208 mg/dL.",
        "session_id": "test-session-report-text"
    }
    response = client.post("/report-summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["key_findings_explained"]) > 0
    assert len(data["questions_for_doctor"]) > 0
    assert "Educational summary only" in data["limitations_note"]


def test_report_summary_pdf_upload():
    sample_pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "sample_data",
        "synthetic_blood_work_report.pdf"
    )
    assert os.path.exists(sample_pdf_path), "Sample PDF should exist"

    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/report-summary/upload",
            data={"session_id": "test-session-pdf-upload"},
            files={"file": ("synthetic_blood_work_report.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["key_findings_explained"]) > 0


def test_session_lifecycle():
    sess_id = "test-session-lifecycle"
    # Send a message
    client.post("/chat", json={"message": "Hello, how does hydration affect energy levels?", "session_id": sess_id})

    # Retrieve history
    hist_resp = client.get(f"/session/{sess_id}")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert hist["session_id"] == sess_id
    assert hist["message_count"] >= 2  # user + assistant

    # Clear session
    clear_resp = client.post(f"/session/{sess_id}/clear")
    assert clear_resp.status_code == 200

    # Retrieve history again, count should be 0
    hist_after = client.get(f"/session/{sess_id}").json()
    assert hist_after["message_count"] == 0


def test_empty_input_validation():
    response = client.post("/chat", json={"message": "   ", "session_id": "test-empty"})
    assert response.status_code == 422
