from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    category: str
    targetRole: str
    language: str = "ko"


class StartSessionResponseData(BaseModel):
    sessionId: str
    prompt: str


class ApiResponse(BaseModel):
    success: bool
    data: dict