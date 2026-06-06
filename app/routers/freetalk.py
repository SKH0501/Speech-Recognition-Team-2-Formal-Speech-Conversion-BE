from fastapi import APIRouter, HTTPException
from app.core.session_store import session_store
from app.schemas.freetalk import FreeTalkRequest, FreeTalkResponse, FreeTalkResponseData
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/sessions", tags=["freetalk"])

# 1. 자유 대화 모드 시작 API
@router.post("/{session_id}/freetalk/start")
def start_freetalk_mode(session_id: str):
    ok = session_store.start_free_talk(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True, "message": "Free talk mode started"}

# 2. 자유 대화 턴(Turn) 진행 API
@router.post("/{session_id}/freetalk/text", response_model=FreeTalkResponse)
async def process_freetalk_text(session_id: str, request: FreeTalkRequest):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get("isFreeTalk"):
        raise HTTPException(status_code=400, detail="Not in free talk mode")

    target_role = session["targetRole"]
    scenario_history = session.get("scenarioHistory", [])
    free_talk_history = session.get("freeTalkHistory", [])

    # Groq LLM에 응답 요청
    ai_text = await LLMService.generate_free_talk_response(
        target_role=target_role,
        scenario_history=scenario_history,
        user_message=request.text,
        free_talk_history=free_talk_history
    )

    # 대화 기록 갱신 (기억 유지)
    session["freeTalkHistory"].append({"role": "user", "content": request.text})
    session["freeTalkHistory"].append({"role": "assistant", "content": ai_text})

    return FreeTalkResponse(
        success=True,
        data=FreeTalkResponseData(
            aiText=ai_text,
            targetRole=target_role
        )
    )
