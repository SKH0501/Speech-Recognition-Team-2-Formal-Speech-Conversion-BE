from typing import Dict, Any
import uuid


class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, category: str, target_role: str, language: str) -> Dict[str, Any]:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = {
            "sessionId": session_id,
            "category": category,
            "targetRole": target_role,
            "language": language,
            "turn": 0,
            "ended": False,
        }
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Dict[str, Any] | None:
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        session["ended"] = True
        return True


session_store = SessionStore()