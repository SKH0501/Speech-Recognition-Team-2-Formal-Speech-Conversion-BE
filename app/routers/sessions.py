from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.schemas.session import StartSessionRequest
from app.schemas.evaluation import TextEvaluationRequest
from app.services.evaluation.evaluator import evaluate_text


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


PROMPTS = {
    "food": "상대방이 밥을 먹었는지 물어보세요!",
    "name": "상대방의 이름을 공손하게 물어보세요!",
    "home": "상대방의 집이 어디인지 공손하게 물어보세요!",
}


@router.post("/start")
def start_session(request: StartSessionRequest):
    session = session_store.create_session(
        category=request.category,
        target_role=request.targetRole,
        language=request.language,
    )

    prompt = PROMPTS.get(request.category, "공손한 표현으로 대화를 시작해보세요.")

    return {
        "success": True,
        "data": {
            "sessionId": session["sessionId"],
            "prompt": prompt,
        }
    }


@router.post("/{session_id}/turns/text")
def evaluate_text_turn(session_id: str, request: TextEvaluationRequest):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["ended"]:
        raise HTTPException(status_code=400, detail="Session already ended")

    result = evaluate_text(
        text=request.text,
        category=session["category"],
        target_role=session["targetRole"],
    )

    # 데모용 nextAction 단순 처리
    next_action = "NEXT" if result["judgement"] == "APPROPRIATE" else "RETRY"

    session["turn"] += 1
    next_question = None
    if next_action == "NEXT" and session["turn"] >= 2:
        next_action = "END"

    return {
        "success": True,
        "data": {
            **result,
            "nextAction": next_action,
            "nextQuestion": next_question,
        }
    }


@router.post("/{session_id}/end")
def end_session(session_id: str):
    ok = session_store.end_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "success": True,
        "data": {
            "sessionId": session_id,
            "ended": True,
        }
    }