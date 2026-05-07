from pydantic import BaseModel
from typing import List


class TextEvaluationRequest(BaseModel):
    text: str


class TextEvaluationResponseData(BaseModel):
    transcript: str
    judgement: str
    score: int
    feedback: str
    errorTypes: List[str]
    recommendedAnswer: str
    alternatives: List[str]
    nextAction: str
    nextQuestion: str | None = None