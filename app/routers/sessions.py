from fastapi import APIRouter, HTTPException

from app.core.session_store import session_store
from app.schemas.session import StartSessionRequest
from app.schemas.evaluation import TextEvaluationRequest
from app.services.evaluation.evaluator import evaluate_text
from app.services.scenario_service import (
    get_first_step,
    get_step,
    get_next_step,
    has_next_step,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])



@router.post("/start")
def start_session(request: StartSessionRequest):
    first_step = get_first_step(request.category,request.targetRole)
    if not first_step:
        raise HTTPException(
            status_code = 400,
            detail = "Unsupported category or targetRole",
        )

    session = session_store.create_session(
        category=request.category,
        target_role=request.targetRole,
        language=request.language,
    )

    return {
        "success": True,
        "data": {
            "sessionId": session["sessionId"],
            "category": session["category"],
            "targetRole": session["targetRole"],
            "currentStepIndex": session["currentStepIndex"],
            "currentStepId": first_step["stepId"],
            "turnType": first_step["turnType"],
            "prompt": first_step["prompt"],
            "systemUtterance": first_step.get("systemUtterance"),
            "recommendedAnswers": first_step["recommendedAnswers"],
        }
    }


@router.post("/{session_id}/turns/text")
def evaluate_text_turn(session_id: str, request: TextEvaluationRequest):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["ended"]:
        raise HTTPException(status_code=400, detail="Session already ended")

    current_step = get_step(
        category=session["category"],
        target_role=session["targetRole"],
        step_index=session["currentStepIndex"],
    )

    if not current_step:
        session_store.end_session(session_id)
        raise HTTPException(status_code=400, detail="Scenario step not found")

    result = evaluate_text(
        text=request.text,
        category=session["category"],
        target_role=session["targetRole"],
        step=current_step,
    )

    is_appropriate = result["judgement"] == "APPROPRIATE"

    next_action = "RETRY"
    next_question = None
    next_step = None

    if is_appropriate:
        if has_next_step(
            category=session["category"],
            target_role=session["targetRole"],
            step_index=session["currentStepIndex"],
        ):
            session_store.advance_step(session_id)

            next_step = get_step(
                category=session["category"],
                target_role=session["targetRole"],
                step_index=session["currentStepIndex"],
            )

            next_action = "NEXT"
            next_question = next_step["prompt"]
        else:
            session_store.end_session(session_id)
            next_action = "END"
    else:
        session_store.increment_turn(session_id)

    session["scenarioHistory"].append({"role": "user", "content": request.text})
    if next_question:
        session["scenarioHistory"].append({"role": "assistant", "content": next_question})

    return {
    "success": True,
    "data": {
        "transcript": result["transcript"],
        "evaluation": {
            "judgement": result["judgement"],
            "score": result["score"],
            "levels": result["levels"],
            "errorTypes": result["errorTypes"],
        },
        "feedback": {
            "message": result["feedback"],
            "recommendedAnswer": result["recommendedAnswer"],
            "alternatives": result["alternatives"],
        },
        "scenario": {
            "currentStepId": current_step["stepId"],
            "turnType": current_step["turnType"],
            "prompt": current_step["prompt"],
            "recommendedAnswers": current_step["recommendedAnswers"],
            "nextAction": next_action,
            "nextQuestion": next_question,
            "nextStep": next_step,
        },
        "classifierResult": result.get("classifierResult"),
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
