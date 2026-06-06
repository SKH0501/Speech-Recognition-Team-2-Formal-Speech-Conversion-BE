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
            "currentStepIndex": 0,
            "turn": 0,
            "ended": False,
            # 
            "scenarioHistory": [], 
            "isFreeTalk": False,
            "freeTalkHistory": [],
        }
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Dict[str, Any] | None:
        return self.sessions.get(session_id)

    def advance_step(self, session_id: str) -> Dict[str, Any] | None:
        session = self.sessions.get(session_id)
        if not session:
            return None

        session["currentStepIndex"] += 1
        session["turn"] += 1
        return session

    def increment_turn(self, session_id: str) -> Dict[str, Any] | None:
        session = self.sessions.get(session_id)
        if not session:
            return None

        session["turn"] += 1
        return session

    def end_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        session["ended"] = True
        return True

    def start_free_talk(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        session["isFreeTalk"] = True
        return True


session_store = SessionStore()
