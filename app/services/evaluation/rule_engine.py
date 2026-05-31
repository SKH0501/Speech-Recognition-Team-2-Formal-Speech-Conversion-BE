from typing import Any, Dict, List
import re

INFORMAL_PATTERNS = [
    "먹었어",
    "뭐 먹었어",
    "몇 살이야",
    "몇살이야",
    "이름이 뭐야",
    "생일 언제야",
    "너 ",
    "야?",
]


CATEGORY_RULES = {
    "food": {
        "plain_words": ["밥", "먹"],
        "honorific_words": ["식사", "진지", "드시", "드셨어", "잡수"],
        "topic_words": ["밥", "먹", "식사", "진지", "음식", "드셨", "드셨어", "잡수"],
    },
    "age": {
        "plain_words": ["나이", "몇 살", "몇살"],
        "honorific_words": ["연세"],
        "topic_words": ["나이", "몇 살", "몇살", "연세", "살"],
    },
    "name": {
        "plain_words": ["이름"],
        "honorific_words": ["성함", "존함"],
        "topic_words": ["이름", "성함", "존함"],
    },
    "birthday": {
        "plain_words": ["생일"],
        "honorific_words": ["생신"],
        "topic_words": ["생일", "생신", "선물", "축하"],
    },
}

STEP_INTENT_RULES = {
    "food_grandfather_ask_eat": {
        "intent_words": ["먹", "식사", "진지", "드셨어", "드셨", "잡수"],
        "question_required": True,
    },
    "food_grandfather_ask_menu": {
       "intent_words": ["뭐", "무엇", "무슨", "어떤", "음식", "메뉴", "드셨어", "드셨"],
        "question_required": True,
    },
    "food_grandfather_answer_eat": {
        "intent_words": ["네", "먹", "식사", "했어요", "했습니다"],
        "question_required": False,
    },
    "food_grandfather_answer_menu": {
    "intent_words": ["먹", "먹었", "먹었어요", "먹었습니다", "마셨", "마셨어요"],
    "question_required": False,
    },

    "age_grandfather_ask_age": {
        "intent_words": ["연세", "나이", "몇살", "몇 살"],
        "question_required": True,
    },
    "age_grandfather_answer_age": {
        "intent_words": ["저는", "살", "입니다", "이에요", "예요"],
        "question_required": False,
    },
    "age_friend_ask_age": {
        "intent_words": ["몇살", "몇 살", "나이"],
        "question_required": True,
    },
    "age_friend_answer_age": {
        "intent_words": ["나는", "나", "살", "이야"],
        "question_required": False,
    },

    "name_grandfather_ask_name": {
        "intent_words": ["성함", "존함", "이름"],
        "question_required": True,
    },
    "name_grandfather_answer_name": {
    "intent_words": ["제", "저는", "이름", "입니다", "예요", "이에요", "이요"],
    "question_required": False,
    },
    "name_friend_ask_name": {
        "intent_words": ["이름", "뭐야"],
        "question_required": True,
    },
    "name_friend_answer_name": {
        "intent_words": ["나는", "내", "이름", "이야"],
        "question_required": False,
    },

    "birthday_grandfather_ask_birthday": {
        "intent_words": ["생신", "생일", "언제"],
        "question_required": True,
    },
    "birthday_grandfather_give_gift": {
        "intent_words": ["생신", "선물", "축하", "드려요", "받으세요"],
        "question_required": False,
    },
    "birthday_grandfather_answer_birthday": {
        "intent_words": ["제", "저는", "생일", "월", "일", "이에요"],
        "question_required": False,
    },
    "birthday_grandfather_thank_gift": {
        "intent_words": ["감사", "고맙", "선물"],
        "question_required": False,
    },
}


POLITE_ENDINGS = ["요", "세요", "셨어요", "습니다", "습니까"]

def normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[?？!！.。]", "", text)
    text = re.sub(r"\s+", "", text)
    return text

def contains_any(text: str, words: List[str]) -> bool:
    return any(word.replace(" ", "") in text for word in words)

def matches_recommended_answer(text: str, step: Dict[str, Any]) -> bool:
    recommended_answers = step.get("recommendedAnswers", [])
    normalized_text = normalize(text)

    return any(
        normalized_text == normalize(answer)
        for answer in recommended_answers
    )

def has_informal_speech(original_text: str) -> bool:
    text = original_text.strip()
    text = text.rstrip(".?!。？！")
    normalized_text = normalize(text)

    informal_endings = [
        "먹었어",
        "뭐먹었어",
        "몇살이야",
        "이름이뭐야",
        "생일언제야",
        "뭐야",
        "이야",
    ]

    # "먹었어요", "뭐예요" 같은 존댓말은 반말로 보면 안 됨
    polite_exceptions = [
        "먹었어요",
        "뭐예요",
        "이에요",
        "예요",
        "했어요",
        "드셨어요",
    ]

    if any(normalized_text.endswith(exception) for exception in polite_exceptions):
        return False

    return any(normalized_text.endswith(pattern) for pattern in informal_endings)


def has_polite_ending(original_text: str) -> bool:
    text = original_text.strip()

    # 문장 끝의 마침펴, 물음표, 느낌표 제거
    text = text.rstrip(".?!。？！")

    return any(text.endswith(ending) for ending in POLITE_ENDINGS)

def has_question_form(original_text: str) -> bool:
    text = original_text.strip()
    text = text.rstrip(".?!。？！")
    normalized_text = normalize(text)

    # 1. 명확한 질문어가 들어가면 질문으로 인정
    question_words = [
        "뭐", "무엇", "무슨", "어떤", "언제", "어디", "누구", "몇", "어떻게"
    ]

    polite_endings = [
        "요", "세요", "셨어요", "습니까", "인가요", "예요", "이에요", "에요"
    ]

    has_question_word = contains_any(normalized_text, question_words)
    has_polite_ending = any(text.endswith(ending) for ending in polite_endings)

    if has_question_word and has_polite_ending:
        return True

    # 2. 질문형으로 자주 쓰이는 종결 표현
    question_endings = [
        "나요",
        "습니까",
        "세요",
        "셨어요",
        "드셨어요",
        "하셨어요",
        "잡수셨어요",
        "뭐야",
        "언제야",
        "몇살이야",
        "몇 살이야",
    ]

    return any(text.endswith(ending) for ending in question_endings)

def has_question_word(text: str) -> bool:
    normalized_text = normalize(text)

    question_words = [
        "뭐", "무엇", "무슨", "어떤", "언제", "어디", "누구"
    ]

    return contains_any(normalized_text, question_words)

def has_incomplete_ending(original_text: str) -> bool:
    text = original_text.strip()
    text = text.rstrip(".?!。？！")
    normalized_text = normalize(text)

    incomplete_endings = [
        "은", "는", "을", "를", "이", "가", "고", "면", "서", "던"
    ]

    return any(normalized_text.endswith(ending) for ending in incomplete_endings)

# 성함 예외처리 함수
def is_name_answer_for_grandfather(original_text: str) -> bool:
    text = original_text.strip()
    text = text.rstrip(".?!。？！")
    normalized_text = normalize(text)

    if not normalized_text:
        return False

    # 질문어가 있으면 답변이 아니라 질문에 가까움
    if has_question_word(original_text):
        return False

    # 반말이면 실패
    if has_informal_speech(original_text):
        return False

    # "신경현"처럼 이름만 말한 경우는 공손한 어미가 없으므로 실패
    if len(normalized_text) <= 3:
        return False

    polite_name_endings = [
        "입니다",
        "이에요",
        "예요",
        "이요",
        "요",
    ]

    return any(normalized_text.endswith(ending) for ending in polite_name_endings)

## 친구와 이름 말하기
def is_name_answer_for_friend(original_text: str) -> bool:
    text = original_text.strip()
    text = text.rstrip(".?!。？！")
    normalized_text = normalize(text)

    if not normalized_text:
        return False

    # 질문어가 있으면 답변이 아니라 질문에 가까움
    if has_question_word(original_text):
        return False

    # 친구에게는 이름만 말해도 자연스러움
    # 예: "신경현", "민수"
    if len(normalized_text) >= 2 and not has_polite_ending(original_text):
        return True

    # 예: "신경현이야", "민수야"
    friend_name_endings = [
        "이야",
        "야",
    ]

    return any(normalized_text.endswith(ending) for ending in friend_name_endings)


def is_free_answer_step(step_id: str) -> bool:
    return step_id in [
        "name_grandfather_answer_name",
        "name_friend_answer_name",
    ]

def detect_rule_errors(
    text: str,
    category: str,
    target_role: str,
    step: Dict[str, Any],
) -> Dict[str, Any]:
    original_text = text.strip()
    normalized_text = normalize(text)

    errors: List[str] = []

    levels = {
        "context": "HIGH",
        "honorific": "HIGH",
        "naturalness": "HIGH",
    }

    if not original_text:
        return {
            "errors": ["NO_INPUT"],
            "levels": {
                "context": "LOW",
                "honorific": "LOW",
                "naturalness": "LOW",
            },
        }

    if len(normalized_text) <= 1:
        return {
            "errors": ["UNCLEAR_INPUT"],
            "levels": {
                "context": "LOW",
                "honorific": "LOW",
                "naturalness": "LOW",
            },
        }

    category_rule = CATEGORY_RULES.get(category, {})
    topic_words = category_rule.get("topic_words", [])
    honorific_words = category_rule.get("honorific_words", [])
    plain_words = category_rule.get("plain_words", [])

    # 1. 문맥 검사: 현재 카테고리 관련 단어가 있는가?
    # 단, 이름 답변처럼 사용자 이름이 자유 입력인 step은 topic_words 검사를 건너뛴다.
    step_id = step.get("stepId")

    if not is_free_answer_step(step_id):
        if topic_words and not contains_any(normalized_text, topic_words):
            errors.append("STEP_MISMATCH")
            levels["context"] = "LOW"

    # stepId 기반 문맥 검사
    step_context_result = evaluate_step_context(original_text, step)
    errors.extend(step_context_result["errors"])

    step_context_level = step_context_result["contextLevel"]
    if step_context_level == "LOW":
        levels["context"] = "LOW"
    elif step_context_level == "MEDIUM" and levels["context"] != "LOW":
        levels["context"] = "MEDIUM"


    # 2. 반말 검사
    if target_role == "grandfather":
        if has_informal_speech(original_text):
            errors.append("INFORMAL_SPEECH")
            levels["honorific"] = "LOW"

    # 3. 상대가 할아버지일 때 공손한 어미 검사
    if target_role == "grandfather":
        if not has_polite_ending(original_text):
            errors.append("MISSING_POLITE_ENDING")
            levels["honorific"] = "LOW"

    # 4. 할아버지에게 말할 때 카테고리별 높임 어휘 검사
    turn_type = step.get("turnType")

    if target_role == "grandfather" and turn_type == "ask":
        has_honorific_word = contains_any(normalized_text, honorific_words)
        has_plain_word = contains_any(normalized_text, plain_words)

        if has_plain_word and not has_honorific_word:
            if levels["honorific"] != "LOW":
                levels["honorific"] = "MEDIUM"
            errors.append("MISSING_HONORIFIC_WORD")

    # 5. 친구에게 지나치게 높은 표현 사용
    if target_role == "friend":
        if contains_any(normalized_text, honorific_words) or has_polite_ending(original_text):
            errors.append("OVERLY_POLITE")
            levels["honorific"] = "MEDIUM"

    # 6. 자연스러움 간단 검사
    if len(normalized_text) <= 3:
        if not (
            step_id == "name_grandfather_answer_name" and is_name_answer_for_grandfather(original_text)
        ) and not (
            step_id == "name_friend_answer_name" and is_name_answer_for_friend(original_text)
        ):
            errors.append("UNCLEAR_INPUT")
            levels["naturalness"] = "LOW"

    return {
        "errors": list(dict.fromkeys(errors)),
        "levels": levels,
    }

def evaluate_step_context(text: str, step: Dict[str, Any]) -> Dict[str, Any]:
    original_text = text.strip()
    normalized_text = normalize(text)

    step_id = step.get("stepId")
    step_rule = STEP_INTENT_RULES.get(step_id)

    if not step_rule:
        return {
            "errors": [],
            "contextLevel": "HIGH",
        }

    errors: List[str] = []
    context_level = "HIGH"

    matched_recommended = matches_recommended_answer(original_text, step)

    # 이름 답변 단계 전용 예외 처리
    if step_id == "name_grandfather_answer_name":
        if is_name_answer_for_grandfather(original_text):
            return {
                "errors": [],
                "contextLevel": "HIGH",
            }

    if step_id == "name_friend_answer_name":
        if is_name_answer_for_friend(original_text):
            return {
                "errors": [],
                "contextLevel": "HIGH",
            }

    # 기본 step intent 검사
    intent_words = step_rule.get("intent_words", [])

    if intent_words and not contains_any(normalized_text, intent_words):
        if not matched_recommended:
            errors.append("STEP_MISMATCH")
            context_level = "LOW"

    # 질문형 검사
    question_required = step_rule.get("question_required", False)

    if question_required and not has_question_form(original_text):
        if not matched_recommended:
            errors.append("MISSING_QUESTION_FORM")
            if context_level != "LOW":
                context_level = "MEDIUM"

    # 음식 대답 단계 전용 검사
    if step_id == "food_grandfather_answer_menu":
        if has_question_word(original_text):
            errors.append("MISSING_ANSWER_CONTENT")
            if context_level != "LOW":
                context_level = "MEDIUM"

        if has_incomplete_ending(original_text):
            errors.append("INCOMPLETE_SENTENCE")
            context_level = "LOW"

    return {
        "errors": errors,
        "contextLevel": context_level,
    }
    original_text = text.strip()
    normalized_text = normalize(text)

    step_id = step.get("stepId")
    step_rule = STEP_INTENT_RULES.get(step_id)

    if not step_rule:
        return {
            "errors": [],
            "contextLevel": "HIGH",
        }

    errors: List[str] = []
    context_level = "HIGH"

    matched_recommended = matches_recommended_answer(original_text, step)

    # 1. 이름 답변 단계 전용 예외 처리
    # 예: "신경현이요", "민수요", "제 이름은 신경현입니다" 통과
    if step_id == "name_grandfather_answer_name":
        if is_name_answer_for_grandfather(original_text):
            return {
                "errors": [],
                "contextLevel": "HIGH",
            }
    # 친구인 경우
    if step_id == "name_friend_answer_name":
        if is_name_answer_for_friend(original_text):
            return {
                "errors": [],
                "contextLevel": "HIGH",
            }
        
    
    # 2. 기본 step intent 검사
    intent_words = step_rule.get("intent_words", [])

    if intent_words and not contains_any(normalized_text, intent_words):
        if not matched_recommended:
            errors.append("STEP_MISMATCH")
            context_level = "LOW"

    # 3. 질문형 검사
    question_required = step_rule.get("question_required", False)

    if question_required and not has_question_form(original_text):
        if not matched_recommended:
            errors.append("MISSING_QUESTION_FORM")
            if context_level != "LOW":
                context_level = "MEDIUM"

    # 4. 음식 대답 단계 전용 검사
    if step_id == "food_grandfather_answer_menu":
        if has_question_word(original_text):
            errors.append("MISSING_ANSWER_CONTENT")
            if context_level != "LOW":
                context_level = "MEDIUM"

        if has_incomplete_ending(original_text):
            errors.append("INCOMPLETE_SENTENCE")
            context_level = "LOW"
    # 친구 이름 답변 예외 추가
    if step_id == "name_friend_answer_name":
        if is_name_answer_for_friend(original_text):
            return {
                "errors": [],
                "contextLevel": "HIGH",
            }

    return {
        "errors": errors,
        "contextLevel": context_level,
    }