from app.services.evaluation.classifier import get_classifier
from app.services.evaluation.rule_engine import detect_rule_errors 

from typing import Any, Dict

from app.services.evaluation.rule_engine import detect_rule_errors


def calculate_score(levels: Dict[str, str]) -> int:
    score_map = {
        "HIGH": 90,
        "MEDIUM": 65,
        "LOW": 30,
    }

    context_score = score_map.get(levels.get("context", "LOW"), 30)
    honorific_score = score_map.get(levels.get("honorific", "LOW"), 30)
    naturalness_score = score_map.get(levels.get("naturalness", "LOW"), 30)

    return int((context_score + honorific_score + naturalness_score) / 3)


def decide_judgement(levels: Dict[str, str], errors: list[str]) -> str:
    if "NO_INPUT" in errors or "UNCLEAR_INPUT" in errors:
        return "INAPPROPRIATE"

    if levels["context"] == "LOW":
        return "INAPPROPRIATE"

    if levels["honorific"] == "LOW":
        return "INAPPROPRIATE"

    if levels["naturalness"] == "LOW":
        return "INAPPROPRIATE"

    if "MEDIUM" in levels.values():
        return "INAPPROPRIATE"

    return "APPROPRIATE"

def evaluate_text(text: str, category: str, target_role: str, step: Dict[str, Any]) -> Dict[str, Any]:
    
    
    rule_result = detect_rule_errors(text=text, category=category, target_role=target_role, step=step)
    errors = rule_result["errors"]
    levels = rule_result["levels"]

   
    classifier_result = {"label": "appropriate", "confidence": 1.0}
    try:
        classifier = get_classifier()
        classifier_result = classifier.predict(text=text, category=category, target_role=target_role)
    except Exception as e:
        print(f"분류기 에러: {e}")

    
    if classifier_result["label"] == "inappropriate":
        if levels["naturalness"] == "HIGH":
            levels["naturalness"] = "MEDIUM"
        if levels["honorific"] == "HIGH":
            levels["honorific"] = "MEDIUM"
            
def generate_rule_feedback(errors: list[str], step: Dict[str, Any]) -> str:
    recommended = step.get("recommendedAnswers", [])
    recommended_text = recommended[0] if recommended else "더 공손한 표현으로 말해보세요."

    if "NO_INPUT" in errors:
        return "아직 음성이 인식되지 않았어요. 다시 한 번 말해보세요."

    if "UNCLEAR_INPUT" in errors:
        return "문장이 너무 짧거나 불분명해요. 조금 더 완전한 문장으로 말해보세요."

    if "STEP_MISMATCH" in errors:
        return f"현재 상황과 조금 다른 표현이에요. 이번에는 '{step['prompt']}'에 맞게 말해보세요. 예: “{recommended_text}”"

    if "INFORMAL_SPEECH" in errors:
        return f"반말 표현이 들어가 있어요. 상대에 맞게 더 공손하게 말해보세요. 예: “{recommended_text}”"

    if "MISSING_POLITE_ENDING" in errors:
        return f"문장 끝에 '-요'나 '-세요' 같은 공손한 어미를 붙여보세요. 예: “{recommended_text}”"

    if "MISSING_HONORIFIC_WORD" in errors:
        return f"의미는 전달되지만, 높임 표현을 쓰면 더 좋아요. 예: “{recommended_text}”"

    if "OVERLY_POLITE" in errors:
        return f"친구에게는 너무 높임 표현을 쓰지 않아도 괜찮아요. 예: “{recommended_text}”"

    return "좋아요. 상황에 맞는 표현이에요."


def evaluate_text(
    text: str,
    category: str,
    target_role: str,
    step: Dict[str, Any],
) -> Dict[str, Any]:
    rule_result = detect_rule_errors(
        text=text,
        category=category,
        target_role=target_role,
        step=step,
    )

    errors = rule_result["errors"]
    levels = rule_result["levels"]

    score = calculate_score(levels)
    judgement = decide_judgement(levels, errors)
    feedback = generate_rule_feedback(errors, step)

    recommended_answers = step.get("recommendedAnswers", [])
    recommended_answer = recommended_answers[0] if recommended_answers else None

    return {
        "transcript": text,
        "judgement": judgement,
        "score": score,
        "levels": levels,
        "feedback": feedback,
        "errorTypes": errors,
        "recommendedAnswer": recommended_answer,
        "alternatives": recommended_answers,
        "classifierResult": None,
    }
