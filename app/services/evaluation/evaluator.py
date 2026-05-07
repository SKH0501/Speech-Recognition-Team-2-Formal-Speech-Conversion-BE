from typing import Dict, Any

from app.services.evaluation.classifier import get_classifier
from app.services.evaluation.rule_engine import detect_error_types, detect_honorific_usage
from app.services.evaluation.feedback_generator import generate_feedback, recommend_answer


def evaluate_text(text: str, category: str, target_role: str) -> Dict[str, Any]:
    classifier = get_classifier()
    clf_result = classifier.predict(text=text, category=category, target_role=target_role)

    label = clf_result["label"]  # appropriate / inappropriate
    confidence = clf_result["confidence"]

    error_types = detect_error_types(text, target_role=target_role)
    used_honorific = detect_honorific_usage(text)

    # confidence 기반 점수
    if label == "appropriate":
        score = int(confidence * 100)
        judgement = "APPROPRIATE"
    else:
        score = int((1 - confidence) * 100) if confidence is not None else 30
        judgement = "INAPPROPRIATE"

    # confidence가 너무 낮으면 rule-based 보조
    if 0.45 <= confidence <= 0.55 and error_types:
        judgement = "INAPPROPRIATE"
        label = "inappropriate"
        score = min(score, 45)

    feedback = generate_feedback(label, error_types, used_honorific)
    rec = recommend_answer(text, category, target_role)

    return {
        "transcript": text,
        "judgement": judgement,
        "score": score,
        "feedback": feedback,
        "errorTypes": error_types if error_types else ["NONE"],
        "recommendedAnswer": rec["recommended"],
        "alternatives": rec["alternatives"],
    }