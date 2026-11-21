/**
 * API client interacting with FastAPI backend via Vite reverse proxy (/api -> :8000)
 */

const API_BASE = '/api';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed (${res.status})`);
    return await res.json();
  } catch (err) {
    return {
      status: 'offline',
      mode: 'Backend Unreachable',
      error: err.message,
    };
  }
}

export async function sendChatMessage({ message, sessionId, forceRoute = null }) {
  const payload = {
    message,
    session_id: sessionId,
    force_route: forceRoute,
  };

  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function checkSymptoms({ symptoms, duration, severity, additionalContext, sessionId }) {
  const payload = {
    symptoms,
    duration,
    severity,
    additional_context: additionalContext,
    session_id: sessionId,
  };

  const res = await fetch(`${API_BASE}/symptom-check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function summarizeReportText({ reportText, sessionId }) {
  const payload = {
    report_text: reportText,
    session_id: sessionId,
  };

  const res = await fetch(`${API_BASE}/report-summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function uploadReportPdf({ file, sessionId, onProgress }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE}/report-summary/upload`);

    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (e) {
          reject(new Error('Invalid JSON response from server'));
        }
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          reject(new Error(err.detail || `Upload failed with status ${xhr.status}`));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    };

    xhr.onerror = () => reject(new Error('Network error during file upload'));
    xhr.send(formData);
  });
}

export async function recommendSpecialists({ healthConcern, sessionId }) {
  const payload = {
    health_concern: healthConcern,
    session_id: sessionId,
  };

  const res = await fetch(`${API_BASE}/specialist-recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function getSessionHistory(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) {
    throw new Error(`Failed to load session history: ${res.status}`);
  }
  return await res.json();
}

export async function clearSessionHistory(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/clear`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to clear session: ${res.status}`);
  }
  return await res.json();
}
