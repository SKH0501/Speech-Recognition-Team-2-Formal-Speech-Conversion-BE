from typing import List, Dict


ERROR_FEEDBACK = {
    "INFORMAL_ENDING": "문장 끝을 '-요' 형태로 바꾸면 더 공손해요.",
    "ROLE_MISMATCH": "어르신께는 반말보다 존댓말을 사용하는 것이 더 자연스러워요.",
}

DEFAULT_APPROPRIATE_FEEDBACK = "좋아요! 상황에 맞는 존댓말을 잘 사용했어요."
DEFAULT_INAPPROPRIATE_FEEDBACK = "조금 더 공손한 표현으로 바꿔보면 좋아요."


def generate_feedback(label: str, error_types: List[str], used_honorific: bool) -> str:
    if label == "appropriate":
        if used_honorific:
            return "좋아요! 존댓말과 높임 표현을 자연스럽게 사용했어요."
        return DEFAULT_APPROPRIATE_FEEDBACK

    if error_types:
        return " ".join(ERROR_FEEDBACK.get(err, DEFAULT_INAPPROPRIATE_FEEDBACK) for err in error_types)

    return DEFAULT_INAPPROPRIATE_FEEDBACK


def recommend_answer(text: str, category: str, target_role: str) -> Dict[str, List[str] | str]:
    mapping = {
        ("food", "grandfather"): {
            "recommended": "식사하셨어요?",
            "alternatives": ["식사하셨어요?", "진지 잡수셨어요?"],
        },
        ("name", "grandfather"): {
            "recommended": "성함이 어떻게 되세요?",
            "alternatives": ["성함이 어떻게 되세요?", "이름이 어떻게 되세요?"],
        },
        ("home", "grandfather"): {
            "recommended": "댁이 어디세요?",
            "alternatives": ["댁이 어디세요?", "집이 어디세요?"],
        },
    }

    return mapping.get(
        (category, target_role),
        {
            "recommended": "조금 더 공손한 표현으로 말씀해 보세요.",
            "alternatives": ["조금 더 공손한 표현으로 말씀해 보세요."],
        },
    )