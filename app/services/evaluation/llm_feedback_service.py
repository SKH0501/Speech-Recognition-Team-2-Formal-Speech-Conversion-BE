import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    return OpenAI(api_key=api_key)


def generate_llm_feedback(
    text: str,
    category: str,
    target_role: str,
    context_match: bool,
    politeness_level: str,
    naturalness: str,
    error_types: list[str] | None = None,
    step_id: str | None = None,
    prompt: str | None = None,
    recommended_answers: list[str] | None = None,
) -> Dict[str, Any]:
    """
    LLM에게 피드백, 교정 문장, 대체 표현을 요청한다.
    실패하면 예외를 발생시키고 evaluator.py에서 fallback 처리한다.
    """

    system_prompt = """
너는 한국어 존댓말 학습 앱의 피드백 생성기다.
사용자는 한국어가 모국어가 아닌 학습자다.

반드시 JSON만 반환해라.
설명 문장, 마크다운, 코드블록은 절대 쓰지 마라.
한국어로만 작성해라. 러시아어, 영어, 다른 언어를 절대 섞지 마라.
같은 문장을 반복하지 마라.
feedback은 최대 2문장으로 작성해라.
correctedText는 recommendedAnswers가 있으면 그중 가장 자연스러운 문장을 우선 사용해라.

반환 JSON 형식:
{
  "feedback": "짧고 친절한 한국어 피드백",
  "correctedText": "가장 적절한 교정 문장",
  "alternatives": ["대체 표현 1", "대체 표현 2", "대체 표현 3"]
}

판단 기준:
- errorTypes에 INFORMAL_SPEECH가 있으면 반말 표현을 존댓말로 바꾸라고 피드백한다.
- errorTypes에 MISSING_HONORIFIC_WORD가 있으면 높임 어휘를 사용하라고 피드백한다.
- errorTypes에 OVERLY_POLITE가 있으면 친구에게는 조금 더 자연스러운 반말 표현을 쓰라고 피드백한다.
- errorTypes에 STEP_MISMATCH가 있으면 현재 미션과 다른 표현이라고 피드백한다.
- target_role이 grandfather이면 어르신께 말하는 상황으로 판단한다.
- target_role이 friend이면 친구에게 자연스럽게 말하는 상황으로 판단한다.
- correctedText는 실제로 바로 사용할 수 있는 자연스러운 문장이어야 한다.
"""

    user_prompt = {
    "userText": text,
    "category": category,
    "targetRole": target_role,
    "stepId": step_id,
    "missionPrompt": prompt,
    "contextMatch": context_match,
    "politenessLevel": politeness_level,
    "naturalness": naturalness,
    "errorTypes": error_types or [],
    "recommendedAnswers": recommended_answers or [],
}

    client = _get_client()

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(user_prompt, ensure_ascii=False),
            },
        ],
    )

    raw_text = response.output_text.strip()
    parsed = json.loads(raw_text)

    return {
        "feedback": str(parsed.get("feedback", "")).strip(),
        "correctedText": str(parsed.get("correctedText", "")).strip(),
        "alternatives": _normalize_alternatives(parsed.get("alternatives", [])),
    }


def _normalize_alternatives(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []

    result = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())

    return result[:3]