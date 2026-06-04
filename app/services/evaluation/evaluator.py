from typing import Dict, Any, List

from app.services.evaluation.classifier import get_classifier
from app.services.evaluation.feedback_generator import generate_feedback, recommend_answer
from app.services.evaluation.llm_feedback_service import generate_llm_feedback


def _safe_level(value: Any, default: str = "MEDIUM") -> str:
    if value in ["LOW", "MEDIUM", "HIGH"]:
        return value
    return default


def _levels_to_score(levels: Dict[str, str], confidence: float | None) -> int:
    level_score = {
        "LOW": 35,
        "MEDIUM": 65,
        "HIGH": 90,
    }

    base = int(
        level_score.get(levels.get("context", "MEDIUM"), 65) * 0.4
        + level_score.get(levels.get("honorific", "MEDIUM"), 65) * 0.4
        + level_score.get(levels.get("naturalness", "MEDIUM"), 65) * 0.2
    )

    if confidence is None:
        return base

    # 모델 확신도가 낮으면 점수를 살짝 보수적으로 낮춤
    if confidence < 0.55:
        return min(base, 60)

    return base


def _judge_from_levels(levels: Dict[str, str]) -> str:
    if levels.get("context") == "LOW":
        return "INAPPROPRIATE"

    if levels.get("honorific") == "LOW":
        return "INAPPROPRIATE"

    if levels.get("naturalness") == "LOW":
        return "INAPPROPRIATE"

    return "APPROPRIATE"


def _errors_from_levels(levels: Dict[str, str]) -> List[str]:
    errors: List[str] = []

    if levels.get("context") == "LOW":
        errors.append("CONTEXT_MISMATCH")

    if levels.get("honorific") == "LOW":
        errors.append("LOW_POLITENESS")
    elif levels.get("honorific") == "MEDIUM":
        errors.append("MEDIUM_POLITENESS")

    if levels.get("naturalness") == "LOW":
        errors.append("LOW_NATURALNESS")
    elif levels.get("naturalness") == "MEDIUM":
        errors.append("MEDIUM_NATURALNESS")

    return errors or ["NONE"]


def _fallback_recommendation(
    text: str,
    category: str,
    target_role: str,
    step: Dict[str, Any],
) -> Dict[str, Any]:
    recommended_answers = step.get("recommendedAnswers") or []

    if recommended_answers:
        return {
            "recommended": recommended_answers[0],
            "alternatives": recommended_answers[:3],
        }

    return recommend_answer(text, category, target_role)


def evaluate_text(
    text: str,
    category: str,
    target_role: str,
    step: Dict[str, Any],
) -> Dict[str, Any]:
    classifier = get_classifier()

    turn_type = step.get("turnType", "ask")

    clf_result = classifier.predict(
        text=text,
        category=category,
        target_role=target_role,
        turn_type=turn_type,
    )

    confidence = clf_result.get("confidence")
    raw_label = clf_result.get("label")

    # 현재 classifier 라벨이 dict 형태든 문자열 형태든 둘 다 대응
    if isinstance(raw_label, dict):
        context_match = bool(raw_label.get("contextMatch", True))
        politeness_level = _safe_level(raw_label.get("politenessLevel"), "MEDIUM")
        naturalness = _safe_level(raw_label.get("naturalness"), "MEDIUM")
    else:
        # label이 appropriate/inappropriate 같은 예전 형식일 때 fallback
        is_appropriate = raw_label == "appropriate"
        context_match = is_appropriate
        politeness_level = "HIGH" if is_appropriate else "LOW"
        naturalness = "HIGH" if is_appropriate else "MEDIUM"

    levels = {
        "context": "HIGH" if context_match else "LOW",
        "honorific": politeness_level,
        "naturalness": naturalness,
    }

    judgement = _judge_from_levels(levels)
    score = _levels_to_score(levels, confidence)
    error_types = _errors_from_levels(levels)

    try:
        llm_result = generate_llm_feedback(
            text=text,
            category=category,
            target_role=target_role,
            context_match=context_match,
            politeness_level=politeness_level,
            naturalness=naturalness,
        )

        feedback = llm_result.get("feedback") or ""
        recommended_answer = llm_result.get("correctedText") or ""
        alternatives = llm_result.get("alternatives") or []

        if not feedback or not recommended_answer:
            raise ValueError("LLM feedback result is incomplete")

    except Exception:
        # LLM 실패 시 기존 고정 피드백으로 fallback
        rec = _fallback_recommendation(text, category, target_role, step)
        fallback_label = "appropriate" if judgement == "APPROPRIATE" else "inappropriate"

        feedback = generate_feedback(
            fallback_label,
            [] if error_types == ["NONE"] else error_types,
            politeness_level == "HIGH",
        )
        recommended_answer = rec["recommended"]
        alternatives = rec["alternatives"]

    return {
        "transcript": text,
        "judgement": judgement,
        "score": score,
        "levels": levels,
        "errorTypes": error_types,
        "feedback": feedback,
        "recommendedAnswer": recommended_answer,
        "alternatives": alternatives,
        "classifierResult": clf_result,
    }