import uuid
from dataclasses import dataclass, field

from app.models.schemas import ResumeData, ChatMessage, InterviewType


@dataclass
class InterviewSession:
    session_id: str
    resume: ResumeData
    filename: str
    job_description: str = ""
    interview_type: InterviewType = InterviewType.MIXED
    questions_count: int = 6
    current_question: int = 0
    chat_history: list[ChatMessage] = field(default_factory=list)
    is_active: bool = False
    is_finished: bool = False


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    def create_session(self, resume: ResumeData, filename: str) -> InterviewSession:
        session_id = uuid.uuid4().hex[:12]
        session = InterviewSession(
            session_id=session_id,
            resume=resume,
            filename=filename,
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> InterviewSession | None:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[InterviewSession]:
        return list(self._sessions.values())


sessions = SessionManager()
