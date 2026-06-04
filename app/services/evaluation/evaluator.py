from typing import Dict, Any, List, Optional

from app.services.evaluation.classifier import get_classifier
from app.services.evaluation.rule_engine import detect_rule_errors
from app.services.evaluation.feedback_generator import generate_feedback, recommend_answer
from app.services.evaluation.llm_feedback_service import generate_llm_feedback


CLASSIFIER_DECISION_THRESHOLD = 0.80


def _safe_level(value: Any, default: str = "MEDIUM") -> str:
    if value in ["LOW", "MEDIUM", "HIGH"]:
        return value
    return default


def _levels_to_score(levels: Dict[str, str], confidence: Optional[float] = None) -> int:
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

    if confidence < 0.55:
        return min(base, 60)

    return base


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

    return errors


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


def _predict_classifier(
    text: str,
    category: str,
    target_role: str,
    turn_type: str,
) -> Optional[Dict[str, Any]]:
    try:
        classifier = get_classifier()

        try:
            return classifier.predict(
                text=text,
                category=category,
                target_role=target_role,
                turn_type=turn_type,
            )
        except TypeError:
            return classifier.predict(
                text=text,
                category=category,
                target_role=target_role,
            )

    except Exception:
        return None


def _extract_classifier_levels(clf_result: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not clf_result:
        return {
            "context": "MEDIUM",
            "honorific": "MEDIUM",
            "naturalness": "MEDIUM",
        }

    raw_label = clf_result.get("label")

    if isinstance(raw_label, dict):
        context_match = bool(raw_label.get("contextMatch", True))
        politeness_level = _safe_level(raw_label.get("politenessLevel"), "MEDIUM")
        naturalness = _safe_level(raw_label.get("naturalness"), "MEDIUM")

        return {
            "context": "HIGH" if context_match else "LOW",
            "honorific": politeness_level,
            "naturalness": naturalness,
        }

    if raw_label == "appropriate":
        return {
            "context": "HIGH",
            "honorific": "HIGH",
            "naturalness": "HIGH",
        }

    if raw_label == "inappropriate":
        return {
            "context": "LOW",
            "honorific": "LOW",
            "naturalness": "MEDIUM",
        }

    return {
        "context": "MEDIUM",
        "honorific": "MEDIUM",
        "naturalness": "MEDIUM",
    }


def _classifier_says_inappropriate(clf_result: Optional[Dict[str, Any]]) -> bool:
    if not clf_result:
        return False

    raw_label = clf_result.get("label")

    if isinstance(raw_label, dict):
        context_match = bool(raw_label.get("contextMatch", True))
        politeness_level = _safe_level(raw_label.get("politenessLevel"), "MEDIUM")
        naturalness = _safe_level(raw_label.get("naturalness"), "MEDIUM")

        return (
            not context_match
            or politeness_level == "LOW"
            or naturalness == "LOW"
        )

    return raw_label == "inappropriate"


def evaluate_text(
    text: str,
    category: str,
    target_role: str,
    step: Dict[str, Any],
) -> Dict[str, Any]:
    turn_type = step.get("turnType", "ask")

    # 1. Rule Engine 평가
    rule_result = detect_rule_errors(
        text=text,
        category=category,
        target_role=target_role,
        step=step,
    )

    rule_error_types = rule_result.get("errors", [])
    rule_levels = rule_result.get(
        "levels",
        {
            "context": "MEDIUM",
            "honorific": "MEDIUM",
            "naturalness": "MEDIUM",
        },
    )

    # 2. Classifier 평가
    clf_result = _predict_classifier(
        text=text,
        category=category,
        target_role=target_role,
        turn_type=turn_type,
    )

    confidence = None
    if clf_result:
        confidence = clf_result.get("confidence")

    classifier_levels = _extract_classifier_levels(clf_result)

    # 3. 최종 판정
    # 1순위: rule engine hard error
    if rule_error_types:
        judgement = "INAPPROPRIATE"
        levels = rule_levels
        error_types = rule_error_types

    # 2순위: rule은 통과했지만 classifier가 높은 확신도로 부적절하다고 판단한 경우
    elif (
        confidence is not None
        and confidence >= CLASSIFIER_DECISION_THRESHOLD
        and _classifier_says_inappropriate(clf_result)
    ):
        judgement = "INAPPROPRIATE"
        levels = classifier_levels
        error_types = _errors_from_levels(classifier_levels)

        if not error_types:
            error_types = ["CLASSIFIER_INAPPROPRIATE"]

    # 3순위: rule 통과 + classifier 확신 낮음 또는 적절 판단
    else:
        judgement = "APPROPRIATE"
        levels = rule_levels
        error_types = []

    score = _levels_to_score(levels, confidence)

    # 4. LLM 피드백 생성
    try:
        llm_result = generate_llm_feedback(
            text=text,
            category=category,
            target_role=target_role,
            context_match=levels.get("context") != "LOW",
            politeness_level=levels.get("honorific", "MEDIUM"),
            naturalness=levels.get("naturalness", "MEDIUM"),
        )

        feedback = llm_result.get("feedback") or ""
        recommended_answer = llm_result.get("correctedText") or ""
        alternatives = llm_result.get("alternatives") or []

        if not feedback or not recommended_answer:
            raise ValueError("LLM feedback result is incomplete")

    except Exception:
        rec = _fallback_recommendation(text, category, target_role, step)
        fallback_label = "appropriate" if judgement == "APPROPRIATE" else "inappropriate"

        feedback = generate_feedback(
            fallback_label,
            error_types,
            levels.get("honorific") == "HIGH",
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