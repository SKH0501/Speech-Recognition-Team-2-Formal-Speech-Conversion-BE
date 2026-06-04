from typing import List, Dict


ERROR_FEEDBACK = {
    # 기존 rule-engine 오류 타입
    "INFORMAL_ENDING": "문장 끝을 '-요' 형태로 바꾸면 더 공손해요.",
    "ROLE_MISMATCH": "어르신께는 반말보다 존댓말을 사용하는 것이 더 자연스러워요.",

    # classifier/evaluator 기반 오류 타입
    "CONTEXT_MISMATCH": "질문과 관련된 내용으로 다시 대답해 보세요.",
    "LOW_POLITENESS": "어르신께는 조금 더 공손한 표현을 사용하는 것이 좋아요.",
    "MEDIUM_POLITENESS": "존댓말은 사용했지만, 높임 표현을 쓰면 더 자연스러워요.",
    "LOW_NATURALNESS": "문장이 조금 어색해요. 더 자연스러운 표현으로 바꿔볼게요.",
    "MEDIUM_NATURALNESS": "의미는 전달되지만, 조금 더 자연스럽게 말할 수 있어요.",
}

DEFAULT_APPROPRIATE_FEEDBACK = "좋아요! 상황에 맞는 존댓말을 잘 사용했어요."
DEFAULT_INAPPROPRIATE_FEEDBACK = "조금 더 공손하고 자연스러운 표현으로 바꿔보면 좋아요."


def generate_feedback(label: str, error_types: List[str], used_honorific: bool) -> str:
    if label == "appropriate":
        if used_honorific:
            return "좋아요! 존댓말과 높임 표현을 자연스럽게 사용했어요."
        return DEFAULT_APPROPRIATE_FEEDBACK

    filtered_errors = [err for err in error_types if err != "NONE"]

    if filtered_errors:
        return " ".join(
            ERROR_FEEDBACK.get(err, DEFAULT_INAPPROPRIATE_FEEDBACK)
            for err in filtered_errors
        )

    return DEFAULT_INAPPROPRIATE_FEEDBACK


def recommend_answer(text: str, category: str, target_role: str) -> Dict[str, List[str] | str]:
    mapping = {
        ("food", "grandfather"): {
            "recommended": "식사하셨어요?",
            "alternatives": [
                "식사하셨어요?",
                "진지 잡수셨어요?",
                "밥 드셨어요?",
            ],
        },
        ("name", "grandfather"): {
            "recommended": "성함이 어떻게 되세요?",
            "alternatives": [
                "성함이 어떻게 되세요?",
                "이름이 어떻게 되세요?",
                "어떻게 불러드리면 될까요?",
            ],
        },
        ("home", "grandfather"): {
            "recommended": "댁이 어디세요?",
            "alternatives": [
                "댁이 어디세요?",
                "어디에 사세요?",
                "거주하시는 곳이 어디세요?",
            ],
        },
        ("age", "grandfather"): {
            "recommended": "연세가 어떻게 되세요?",
            "alternatives": [
                "연세가 어떻게 되세요?",
                "올해 연세가 어떻게 되세요?",
                "나이가 어떻게 되세요?",
            ],
        },
        ("birthday", "grandfather"): {
            "recommended": "생신이 언제세요?",
            "alternatives": [
                "생신이 언제세요?",
                "생신이 며칠이세요?",
                "생일이 언제세요?",
            ],
        },
    }

    return mapping.get(
        (category, target_role),
        {
            "recommended": "조금 더 공손한 표현으로 말씀해 보세요.",
            "alternatives": ["조금 더 공손한 표현으로 말씀해 보세요."],
        },
    )