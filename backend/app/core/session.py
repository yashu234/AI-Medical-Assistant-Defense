"""
Thread-safe in-memory session storage.

MVP Session Security Notice:
- This is an in-memory session store designed for single-node educational demos.
- Sessions are isolated by a unique session_id (UUID string).
- In a production healthcare system, sessions must be authenticated, encrypted at rest,
  governed by HIPAA / GDPR compliance, and stored in an audited, encrypted persistent database.
"""

import threading
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = Field(default_factory=time.time)
    route: Optional[str] = None
    is_emergency: bool = False
    is_simulated: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionData(BaseModel):
    session_id: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    messages: List[ChatMessage] = Field(default_factory=list)


class SessionStore:
    """Thread-safe session storage manager with automatic history capping."""

    def __init__(self, max_history_per_session: int = 50):
        self._sessions: Dict[str, SessionData] = {}
        self._lock = threading.Lock()
        self.max_history = max_history_per_session

    def get_or_create(self, session_id: str) -> SessionData:
        """Retrieves an existing session or creates a new one."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionData(session_id=session_id)
            return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Gets a session by ID if it exists."""
        with self._lock:
            return self._sessions.get(session_id)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        route: Optional[str] = None,
        is_emergency: bool = False,
        is_simulated: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Appends a message to the specified session."""
        msg = ChatMessage(
            role=role,
            content=content,
            route=route,
            is_emergency=is_emergency,
            is_simulated=is_simulated,
            metadata=metadata or {},
        )
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionData(session_id=session_id)
            
            session = self._sessions[session_id]
            session.messages.append(msg)
            session.updated_at = time.time()
            
            # Cap message history to avoid unbounded memory growth
            if len(session.messages) > self.max_history:
                session.messages = session.messages[-self.max_history:]
                
        return msg

    def clear_session(self, session_id: str) -> bool:
        """Clears messages for a given session."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].messages = []
                self._sessions[session_id].updated_at = time.time()
                return True
            return False

    def list_active_session_ids(self) -> List[str]:
        """Returns list of active session IDs."""
        with self._lock:
            return list(self._sessions.keys())


# Singleton session store instance
session_store = SessionStore()
