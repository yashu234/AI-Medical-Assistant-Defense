# AI Medical Assistant – Agentic AI Healthcare Chatbot (MVP)

> **IMPORTANT SAFETY NOTICE:**  
> **Educational demo only. Not medical advice. For urgent or severe symptoms, contact local emergency services or a qualified healthcare professional.**  
> This system is an educational software demonstration developed for an engineering project showcase. It is **not** a certified medical device, does **not** provide definitive diagnoses, does **not** prescribe treatments or drug dosages, and must **never** be used for medical triage or emergency situations.

---

## 1. Overview & Architecture

The **AI Medical Assistant** is a modular, safety-first healthcare chatbot demonstrating agentic routing principles, multi-modal report ingestion, and healthcare guardrails.

### What Makes This a Modular Chatbot vs. an Autonomous Agent?
- **Current MVP (Modular Routing Chatbot):**  
  The system uses a transparent, deterministic routing layer that classifies user intent into distinct specialized services (`symptom_guidance`, `report_summary`, `specialist_recommend`, `general_chat`) ahead of model processing. Critical safety triage and emergency red-flag interceptors execute prior to routing.
- **Requirements for an Autonomous Agent:**  
  Transitioning from this modular pipeline to a fully autonomous clinical agent would require:
  1. **Dynamic Tool Calling & Action Loops:** Using tool-use protocols (e.g., function calling, ReAct) where the agent decides when and how many times to invoke external tools (e.g., medical knowledge bases, drug interaction databases, appointment schedulers).
  2. **Multi-Step Goal Planning & Reflection:** Decomposing complex inquiries into sub-goals, reflecting on intermediary results, and re-planning when new information is gathered.
  3. **Long-Term Clinical Memory & RAG:** Secure, HIPAA-compliant retrieval-augmented generation across verified clinical literature (PubMed, UpToDate) and patient health records.
  4. **Human-in-the-Loop Clinical Verification:** Requiring licensed physician approval gates before outputting clinical plans.

---

## 2. Key Features

1. **Safety Red-Flag Emergency Triage:**
   - Detects indicators of acute emergencies (severe chest pain, stroke signs/FAST, severe respiratory distress, anaphylaxis, uncontrollable bleeding, psychiatric crisis).
   - Immediately halts standard chatbot routing and returns urgent emergency guidance with direct hotline information (911 / 999 / 112 / 988 Crisis Line).
2. **Deterministic Intent Router:**
   - Categorizes user messages into dedicated feature modules with confidence scoring and routing explanations.
   - Supports user-directed manual override through mode chips in the UI.
3. **Symptom Guidance (Non-Diagnostic):**
   - Prompts users for missing clinical context (onset duration, severity scale, triggers, active medications).
   - Discusses general potential considerations while preserving clinical uncertainty.
4. **Medical Report & Lab Explainer (PDF & Text):**
   - Ingests laboratory reports via PDF upload or text paste using `pypdf`.
   - Treats document text as **untrusted input**, sanitizing against prompt injections and control characters.
   - Explains standard panels (CBC, CMP, Lipid Profile) in plain language, generates questions for the doctor, and notes laboratory reference-range variability.
5. **Specialist Category Finder:**
   - Maps symptoms to medical specialties (Cardiology, Dermatology, Orthopedics, Neurology, etc.).
   - Always emphasizes a **Primary Care Physician (PCP)** as the primary entry point for formal clinical evaluation and referral.
6. **Session-Based Isolation:**
   - Dedicated message history per session ID.
7. **Dual-Engine Architecture (Local Demo vs. Connected LLM):**
   - **Local Simulated Demo Mode:** Works out-of-the-box with **zero API keys**. Responses are deterministically generated from high-quality educational templates and clearly labeled `[Simulated Demo Mode - No API Key Configured]`.
   - **OpenAI-Compatible Mode:** When an `OPENAI_API_KEY` is configured in `.env`, the assistant communicates with OpenAI-compatible chat endpoints.

---

## 3. Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application & CORS configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py               # API endpoints (Chat, Symptom, Report, Specialist, Session)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # Pydantic settings & environment configuration
│   │   │   ├── safety.py               # Red-flag emergency detection & guardrails
│   │   │   └── session.py              # Thread-safe in-memory session manager
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py              # Pydantic request and response schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── router.py               # Transparent intent classifier
│   │       ├── llm_client.py           # Dual-mode engine (OpenAI API + Local Demo)
│   │       ├── symptom_service.py      # Symptom guidance & context gathering
│   │       ├── report_service.py       # PDF parsing (pypdf) & plain-language summary
│   │       ├── specialist_service.py   # Specialist category recommendations
│   │       └── general_chat_service.py # General educational health Q&A
│   ├── sample_data/
│   │   ├── create_sample_pdf.py        # Generator for synthetic educational lab PDF
│   │   ├── synthetic_blood_work_report.pdf # Synthetic demo lab PDF report
│   │   └── synthetic_sample_report.txt # Synthetic lab test report text
│   ├── requirements.txt
│   └── tests/
│       ├── test_safety_and_routing.py  # Unit tests for red flags, routing, sanitization
│       └── test_api_endpoints.py       # Integration tests for all FastAPI endpoints
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                  # Vite configuration with reverse proxy to :8000
│   ├── tailwind.config.js              # Healthcare Navy & Teal palette configuration
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                     # Layout, session state, message handling
│       ├── index.css                   # Custom scrollbars & Tailwind base
│       ├── components/
│       │   ├── DisclaimerBanner.jsx    # Persistent emergency/educational disclaimer
│       │   ├── Header.jsx              # Session selector, New Session, Clear controls
│       │   ├── MessageItem.jsx         # Render messages with route badge & safety tag
│       │   ├── ChatInput.jsx           # Input box, mode selector chips, send controls
│       │   ├── PdfUploadModal.jsx      # PDF upload with progress, size check, sample loader
│       │   ├── QuickPrompts.jsx        # Clickable synthetic sample prompts
│       │   └── EmergencyAlert.jsx      # Urgent red-flag warning card
│       └── services/
│           └── api.js                  # Frontend API client
├── .env.example                        # Template for environment variables
├── .gitignore                          # Ignored files, virtual environments, .env
└── README.md                           # Complete documentation
```

---

## 4. Setup & Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **npm**

### Step 1: Environment Setup
Copy the example environment file:
```bash
cp .env.example .env
```
*(Optional)* To use an external OpenAI-compatible model, set `OPENAI_API_KEY` in `.env`. If left empty, the application runs automatically in **Local Simulated Demo Mode** without requiring any API keys or network calls.

### Step 2: Backend Setup
1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv backend/.venv
   source backend/.venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Generate the synthetic sample PDF:
   ```bash
   PYTHONPATH=backend python backend/sample_data/create_sample_pdf.py
   ```
4. Run automated test suite:
   ```bash
   PYTHONPATH=backend pytest backend/tests/
   ```
5. Start the FastAPI backend server:
   ```bash
   PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The backend will be running at `http://127.0.0.1:8000` (Interactive API docs at `http://127.0.0.1:8000/docs`).*

### Step 3: Frontend Setup
In a new terminal window:
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will be accessible at `http://127.0.0.1:5173`.*

---

## 5. API Reference & Examples

### `GET /health`
Returns service status, version, and operating mode.
```bash
curl http://127.0.0.1:8000/health
```

### `POST /chat`
Primary conversational endpoint with safety check and automatic intent classification.
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the difference between LDL and HDL cholesterol?",
    "session_id": "demo-session-1"
  }'
```

### Emergency Red-Flag Interception Example
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have crushing chest pain radiating to my left arm and jaw",
    "session_id": "demo-session-emergency"
  }'
```
*Response returns `is_emergency: true`, detected route `emergency_triage`, and emergency helpline guidance.*

### `POST /symptom-check`
Structured symptom evaluation with context gathering.
```bash
curl -X POST http://127.0.0.1:8000/symptom-check \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "Dry cough and mild scratchy throat",
    "duration": "2 days",
    "severity": "mild",
    "additional_context": "No fever, history of pollen allergy",
    "session_id": "demo-session-1"
  }'
```

### `POST /report-summary` & `/report-summary/upload`
- **JSON Text:**
  ```bash
  curl -X POST http://127.0.0.1:8000/report-summary \
    -H "Content-Type: application/json" \
    -d '{
      "report_text": "Complete Blood Count: WBC 6.8, Hemoglobin 14.2, Platelets 245. Total Cholesterol 208 mg/dL.",
      "session_id": "demo-session-1"
    }'
  ```
- **Multipart PDF Upload:**
  ```bash
  curl -X POST http://127.0.0.1:8000/report-summary/upload \
    -F "session_id=demo-session-1" \
    -F "file=@backend/sample_data/synthetic_blood_work_report.pdf"
  ```

### `POST /specialist-recommend`
Specialist category suggestions based on health concern.
```bash
curl -X POST http://127.0.0.1:8000/specialist-recommend \
  -H "Content-Type: application/json" \
  -d '{
    "health_concern": "Persistent clicking and swelling in my knee after running",
    "session_id": "demo-session-1"
  }'
```

### `GET /session/{session_id}`
Retrieves session message history.
```bash
curl http://127.0.0.1:8000/session/demo-session-1
```

### `POST /session/{session_id}/clear`
Clears session history.
```bash
curl -X POST http://127.0.0.1:8000/session/demo-session-1/clear
```

---

## 6. Security & Limitations

1. **MVP Session Security Limitation:**
   - Message sessions are stored in an in-memory dictionary for this demonstration.
   - In a production environment, sessions must be managed using authenticated cryptographic tokens (JWT/OAuth2), stored in an encrypted database (PostgreSQL with row-level security), and fully audited in compliance with HIPAA and GDPR regulations.
2. **Untrusted PDF Input:**
   - PDF files are parsed using `pypdf`. Embedded scripts and active elements are never executed. Text length is capped at 25,000 characters and filtered for prompt injection attempts.
   - Scanned image-only PDFs (lacking digital text) cannot be parsed by `pypdf` alone; optical character recognition (OCR) would be required in an expanded system.
3. **No Clinical Advice:**
   - Outputs are strictly educational and simulated when no API key is present. All example data provided in the repository is 100% synthetic.
