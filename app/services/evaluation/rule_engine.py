from typing import List


INFORMAL_PATTERNS = [
    "먹었어", "뭐야", "어디야", "했어", "왔어", "이름 뭐", "집 어디야"
]

HONORIFIC_WORDS = [
    "식사", "진지", "성함", "연세", "생신", "댁", "잡수"
]


def detect_error_types(text: str, target_role: str) -> List[str]:
    errors = []

    lowered = text.strip()

    if any(pat in lowered for pat in INFORMAL_PATTERNS):
        errors.append("INFORMAL_ENDING")

    if target_role == "grandfather" and "INFORMAL_ENDING" in errors:
        errors.append("ROLE_MISMATCH")

    return errors


def detect_honorific_usage(text: str) -> bool:
    return any(word in text for word in HONORIFIC_WORDS)