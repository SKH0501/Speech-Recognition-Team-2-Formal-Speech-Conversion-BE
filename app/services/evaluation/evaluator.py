from typing import Dict, Any

from app.services.evaluation.classifier import get_classifier
from app.services.evaluation.rule_engine import detect_error_types, detect_honorific_usage
from app.services.evaluation.feedback_generator import generate_feedback, recommend_answer
from app.services.evaluation.llm_feedback_service import generate_llm_feedback


def _map_politeness_level(label: str, used_honorific: bool) -> str:
    if label == "inappropriate":
        return "LOW"
    if used_honorific:
        return "HIGH"
    return "MEDIUM"


def _map_naturalness(score: int) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


def evaluate_text(text: str, category: str, target_role: str) -> Dict[str, Any]:
    classifier = get_classifier()
    clf_result = classifier.predict(text=text, category=category, target_role=target_role)

    label = clf_result["label"]
    confidence = clf_result["confidence"]

    error_types = detect_error_types(text, target_role=target_role)
    used_honorific = detect_honorific_usage(text)

    if label == "appropriate":
        score = int(confidence * 100)
        judgement = "APPROPRIATE"
    else:
        score = int((1 - confidence) * 100) if confidence is not None else 30
        judgement = "INAPPROPRIATE"

    if 0.45 <= confidence <= 0.55 and error_types:
        judgement = "INAPPROPRIATE"
        label = "inappropriate"
        score = min(score, 45)

    context_match = True
    politeness_level = _map_politeness_level(label, used_honorific)
    naturalness = _map_naturalness(score)

    try:
        llm_result = generate_llm_feedback(
            text=text,
            category=category,
            target_role=target_role,
            context_match=context_match,
            politeness_level=politeness_level,
            naturalness=naturalness,
        )

        feedback = llm_result["feedback"]
        recommended_answer = llm_result["correctedText"]
        alternatives = llm_result["alternatives"]

    except Exception:
        feedback = generate_feedback(label, error_types, used_honorific)
        rec = recommend_answer(text, category, target_role)
        recommended_answer = rec["recommended"]
        alternatives = rec["alternatives"]

    return {
        "transcript": text,
        "judgement": judgement,
        "score": score,
        "feedback": feedback,
        "errorTypes": error_types if error_types else ["NONE"],
        "recommendedAnswer": recommended_answer,
        "alternatives": alternatives,
    }