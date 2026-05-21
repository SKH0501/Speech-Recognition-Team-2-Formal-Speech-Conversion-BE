from typing import Any, Dict, List


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
        "intent_words": ["뭐", "무엇", "어떤", "음식", "메뉴", "드셨어", "드셨"],
        "question_required": True,
    },
    "food_grandfather_answer_eat": {
        "intent_words": ["네", "먹", "식사", "했어요", "했습니다"],
        "question_required": False,
    },
    "food_grandfather_answer_menu": {
        "intent_words": ["먹", "밥", "김치", "찌개", "돈가스", "라면", "먹었어요"],
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
        "intent_words": ["제", "저는", "이름", "입니다", "예요"],
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
    return text.strip().replace(" ", "")


def contains_any(text: str, words: List[str]) -> bool:
    return any(word.replace(" ", "") in text for word in words)


def has_polite_ending(original_text: str) -> bool:
    text = original_text.strip()

    # 문장 끝의 마침펴, 물음표, 느낌표 제거
    text = text.rstrip(".?!。？！")

    return any(text.endswith(ending) for ending in POLITE_ENDINGS)

def has_question_form(original_text: str) -> bool:
    text = original_text.strip()
    return text.endswith("?") or text.endswith("요?") or text.endswith("세요?") or text.endswith("습니까?")

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
    if contains_any(normalized_text, INFORMAL_PATTERNS):
        errors.append("INFORMAL_SPEECH")
        levels["honorific"] = "LOW"

    # 3. 상대가 할아버지일 때 공손한 어미 검사
    if target_role == "grandfather":
        if not has_polite_ending(original_text):
            errors.append("MISSING_POLITE_ENDING")
            levels["honorific"] = "LOW"

    # 4. 할아버지에게 말할 때 카테고리별 높임 어휘 검사
    if target_role == "grandfather":
        has_honorific_word = contains_any(normalized_text, honorific_words)
        has_plain_word = contains_any(normalized_text, plain_words)

        if has_plain_word and not has_honorific_word:
            if levels["honorific"] != "LOW":
                levels["honorific"] = "MEDIUM"
            errors.append("MISSING_HONORIFIC_WORD")

    # 5. 친구에게 지나치게 높은 표현 사용
    if target_role == "friend":
        if contains_any(normalized_text, honorific_words):
            errors.append("OVERLY_POLITE")
            levels["honorific"] = "MEDIUM"

    # 6. 자연스러움 간단 검사
    if len(normalized_text) <= 3:
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

    intent_words = step_rule.get("intent_words", [])
    if intent_words and not contains_any(normalized_text, intent_words):
        errors.append("STEP_MISMATCH")
        context_level = "LOW"

    question_required = step_rule.get("question_required", False)
    if question_required and not has_question_form(original_text):
        errors.append("MISSING_QUESTION_FORM")
        if context_level != "LOW":
            context_level = "MEDIUM"

    return {
        "errors": errors,
        "contextLevel": context_level,
    }