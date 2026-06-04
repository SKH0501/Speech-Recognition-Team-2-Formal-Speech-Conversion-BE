from typing import List, Dict


ERROR_FEEDBACK = {
    # 입력/문장 문제
    "NO_INPUT": "아직 말이 입력되지 않았어요. 다시 한 번 말해보세요.",
    "UNCLEAR_INPUT": "문장이 너무 짧거나 불분명해요. 조금 더 완전한 문장으로 말해보세요.",

    # 문맥/단계 문제
    "STEP_MISMATCH": "현재 상황과 조금 다른 표현이에요. 주어진 상황에 맞게 다시 말해보세요.",
    "CONTEXT_MISMATCH": "질문과 관련된 내용으로 다시 대답해 보세요.",
    "MISSING_QUESTION_FORM": "질문하는 상황이에요. 질문하는 표현으로 말해보세요.",
    "MISSING_ANSWER_CONTENT": "대답에 필요한 내용이 부족해요. 질문에 맞는 내용을 넣어 말해보세요.",
    "INCOMPLETE_SENTENCE": "문장이 완성되지 않았어요. 끝까지 자연스럽게 말해보세요.",

    # 존댓말/반말 문제
    "INFORMAL_SPEECH": "반말 표현이 들어가 있어요. 어르신께는 존댓말로 말해보세요.",
    "INFORMAL_ENDING": "문장 끝을 '-요' 형태로 바꾸면 더 공손해요.",
    "ROLE_MISMATCH": "어르신께는 반말보다 존댓말을 사용하는 것이 더 자연스러워요.",
    "MISSING_POLITE_ENDING": "문장 끝을 '-요'나 '-습니다'처럼 공손하게 바꾸면 좋아요.",
    "MISSING_HONORIFIC_WORD": "의미는 전달되지만, 높임 표현을 쓰면 더 좋아요.",
    "OVERLY_POLITE": "친구에게는 조금 더 자연스러운 표현을 사용하는 것이 좋아요.",

    # classifier/evaluator 기반 오류 타입
    "LOW_POLITENESS": "상대에 맞는 말투로 다시 말해보세요.",
    "MEDIUM_POLITENESS": "의미는 전달되지만, 조금 더 상황에 맞는 말투로 바꿔보면 좋아요.",
    "LOW_NATURALNESS": "문장이 조금 어색해요. 더 자연스럽게 말해보세요.",
    "MEDIUM_NATURALNESS": "의미는 전달되지만, 조금 더 자연스럽게 말할 수 있어요.",
    "CLASSIFIER_INAPPROPRIATE": "현재 상황에 더 알맞은 표현으로 다시 말해보세요.",
}

DEFAULT_APPROPRIATE_FEEDBACK = "좋아요. 상황에 맞는 표현이에요."
DEFAULT_INAPPROPRIATE_FEEDBACK = "조금 더 상황에 맞는 표현으로 다시 말해보세요."


# 여러 오류가 동시에 들어와도 가장 중요한 오류 하나만 피드백하기 위한 우선순위
ERROR_PRIORITY = [
    "NO_INPUT",
    "UNCLEAR_INPUT",
    "STEP_MISMATCH",
    "CONTEXT_MISMATCH",
    "MISSING_ANSWER_CONTENT",
    "INCOMPLETE_SENTENCE",
    "INFORMAL_SPEECH",
    "INFORMAL_ENDING",
    "ROLE_MISMATCH",
    "MISSING_POLITE_ENDING",
    "MISSING_HONORIFIC_WORD",
    "OVERLY_POLITE",
    "MISSING_QUESTION_FORM",
    "LOW_POLITENESS",
    "MEDIUM_POLITENESS",
    "LOW_NATURALNESS",
    "MEDIUM_NATURALNESS",
    "CLASSIFIER_INAPPROPRIATE",
]


def generate_feedback(label: str, error_types: List[str], used_honorific: bool) -> str:
    if label == "appropriate":
        return DEFAULT_APPROPRIATE_FEEDBACK

    filtered_errors = [
        err for err in error_types
        if err and err != "NONE"
    ]

    if not filtered_errors:
        return DEFAULT_INAPPROPRIATE_FEEDBACK

    # 오류가 여러 개 있어도 한 문장만 반환해서 반복 피드백 방지
    for err in ERROR_PRIORITY:
        if err in filtered_errors:
            return ERROR_FEEDBACK.get(err, DEFAULT_INAPPROPRIATE_FEEDBACK)

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
                "존함이 어떻게 되세요?",
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
                "할아버지 생신이 언제세요?",
                "생신이 언제이신가요?",
            ],
        },

        ("name", "friend"): {
            "recommended": "너 이름이 뭐야?",
            "alternatives": [
                "너 이름이 뭐야?",
                "이름이 뭐야?",
                "넌 이름이 뭐야?",
            ],
        },
        ("age", "friend"): {
            "recommended": "너 몇 살이야?",
            "alternatives": [
                "너 몇 살이야?",
                "몇 살이야?",
                "나이가 어떻게 돼?",
            ],
        },
        ("birthday", "friend"): {
            "recommended": "너 생일 언제야?",
            "alternatives": [
                "너 생일 언제야?",
                "생일 언제야?",
                "네 생일은 언제야?",
            ],
        },
    }

    return mapping.get(
        (category, target_role),
        {
            "recommended": "상황에 맞게 다시 말해보세요.",
            "alternatives": ["상황에 맞게 다시 말해보세요."],
        },
    )