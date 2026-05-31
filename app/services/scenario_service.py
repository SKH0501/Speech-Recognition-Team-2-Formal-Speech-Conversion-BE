from typing import Any, Dict, List


SCENARIOS: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "food": {
        "grandfather": [
            {
                "stepId": "food_grandfather_ask_eat",
                "turnType": "ask",
                "prompt": "할아버지에게 밥을 먹었는지 물어보세요.",
                "recommendedAnswers": ["식사하셨어요?", "진지 잡수셨어요?"],
            },
            {
                "stepId": "food_grandfather_ask_menu",
                "turnType": "ask",
                "prompt": "할아버지에게 밥으로 무엇을 드셨는지 물어보세요.",
                "recommendedAnswers": ["무엇을 드셨어요?", "어떤 음식을 드셨어요?"],
            },
            {
                "stepId": "food_grandfather_answer_eat",
                "turnType": "answer",
                "prompt": "할아버지가 밥을 먹었는지 물어봤습니다. 공손하게 대답해보세요.",
                "systemUtterance": "밥은 먹었니?",
                "recommendedAnswers": ["네, 밥을 먹었어요.", "네, 식사했습니다."],
            },
            {
                "stepId": "food_grandfather_answer_menu",
                "turnType": "answer",
                "prompt": "할아버지가 밥으로 무엇을 먹었는지 물어봤습니다. 공손하게 대답해보세요.",
                "systemUtterance": "밥으로 뭘 먹었니?",
                "recommendedAnswers": ["저는 김치찌개를 먹었어요.", "저는 돈가스를 먹었어요."],
            },
        ]
    },
    "age": {
        "grandfather": [
            {
                "stepId": "age_grandfather_ask_age",
                "turnType": "ask",
                "prompt": "할아버지에게 나이를 공손하게 물어보세요.",
                "recommendedAnswers": ["연세가 어떻게 되세요?", "혹시 연세가 어떻게 되세요?"],
            },
            {
                "stepId": "age_grandfather_answer_age",
                "turnType": "answer",
                "prompt": "할아버지가 나이를 물어봤습니다. 공손하게 대답해보세요.",
                "systemUtterance": "할아버지는 87살이란다. 학생은 몇 살이니?",
                "recommendedAnswers": ["저는 열세 살이에요.", "저는 13살입니다."],
            },
        ],
        "friend": [
            {
                "stepId": "age_friend_ask_age",
                "turnType": "ask",
                "prompt": "친구에게 나이를 물어보세요.",
                "recommendedAnswers": ["너 몇 살이야?", "몇 살이야?"],
            },
            {
                "stepId": "age_friend_answer_age",
                "turnType": "answer",
                "prompt": "친구가 나이를 물어봤습니다. 자연스럽게 대답해보세요.",
                "systemUtterance": "너 몇 살이야?",
                "recommendedAnswers": ["나는 열세 살이야.", "나 13살이야."],
            },
        ],
    },
    "name": {
        "grandfather": [
            {
                "stepId": "name_grandfather_ask_name",
                "turnType": "ask",
                "prompt": "할아버지에게 이름을 공손하게 물어보세요.",
                "recommendedAnswers": ["성함이 어떻게 되세요?", "존함이 어떻게 되세요?"],
            },
            {
                "stepId": "name_grandfather_answer_name",
                "turnType": "answer",
                "prompt": "할아버지가 이름을 물어봤습니다. 공손하게 대답해보세요.",
                "systemUtterance": "내 이름은 박찬수란다. 학생 이름이 뭐니?",
                "recommendedAnswers": ["제 이름은 김민수예요.", "저는 김민수입니다."],
            },
        ],
        "friend": [
            {
                "stepId": "name_friend_ask_name",
                "turnType": "ask",
                "prompt": "친구에게 이름을 물어보세요.",
                "recommendedAnswers": ["너 이름이 뭐야?", "이름이 뭐야?"],
            },
            {
                "stepId": "name_friend_answer_name",
                "turnType": "answer",
                "prompt": "친구가 이름을 물어봤습니다. 자연스럽게 대답해보세요.",
                "systemUtterance": "너 이름이 뭐야?",
                "recommendedAnswers": ["나는 김민수야.", "내 이름은 김민수야."],
            },
        ],
    },
    "birthday": {
        "grandfather": [
            {
                "stepId": "birthday_grandfather_ask_birthday",
                "turnType": "ask",
                "prompt": "할아버지에게 생일을 공손하게 물어보세요.",
                "recommendedAnswers": ["생신이 언제세요?", "할아버지 생신이 언제세요?"],
            },
            {
                "stepId": "birthday_grandfather_give_gift",
                "turnType": "ask",
                "prompt": "할아버지에게 생일 선물을 드리는 말을 해보세요.",
                "recommendedAnswers": ["생신 선물이에요.", "생신 축하드려요. 선물 받으세요."],
            },
            {
                "stepId": "birthday_grandfather_answer_birthday",
                "turnType": "answer",
                "prompt": "할아버지가 생일을 물어봤습니다. 공손하게 대답해보세요.",
                "systemUtterance": "학생 생일은 언제니?",
                "recommendedAnswers": ["제 생일은 5월 10일이에요.", "저는 5월 10일이 생일이에요."],
            },
            {
                "stepId": "birthday_grandfather_thank_gift",
                "turnType": "answer",
                "prompt": "할아버지가 생일 선물을 주셨습니다. 감사 인사를 해보세요.",
                "systemUtterance": "생일 선물이다. 받아라.",
                "recommendedAnswers": ["감사합니다, 할아버지.", "선물 감사합니다."],
            },
        ]
    },
}


def get_scenario(category: str, target_role: str) -> List[Dict[str, Any]]:
    return SCENARIOS.get(category, {}).get(target_role, [])


def get_step(category: str, target_role: str, step_index: int) -> Dict[str, Any] | None:
    scenario = get_scenario(category, target_role)

    if step_index < 0 or step_index >= len(scenario):
        return None

    return scenario[step_index]


def get_first_step(category: str, target_role: str) -> Dict[str, Any] | None:
    return get_step(category, target_role, 0)


def has_next_step(category: str, target_role: str, step_index: int) -> bool:
    scenario = get_scenario(category, target_role)
    return step_index + 1 < len(scenario)


def get_next_step(category: str, target_role: str, step_index: int) -> Dict[str, Any] | None:
    return get_step(category, target_role, step_index + 1)