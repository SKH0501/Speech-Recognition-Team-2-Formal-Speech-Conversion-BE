import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")


def generate_llm_feedback(
    text: str,
    category: str,
    target_role: str,
    context_match: bool,
    politeness_level: str,
    naturalness: str,
) -> Dict[str, Any]:
    """
    LLM에게 피드백, 교정 문장, 대체 표현을 요청한다.
    실패하면 예외를 발생시키므로 evaluator.py에서 fallback 처리하는 것을 권장.
    """

    system_prompt = """
너는 한국어 존댓말 학습 앱의 피드백 생성기다.
사용자는 한국어가 모국어가 아닌 학습자다.

반드시 JSON만 반환해라.
설명 문장, 마크다운, 코드블록은 절대 쓰지 마라.

반환 JSON 형식:
{
  "feedback": "짧고 친절한 한국어 피드백",
  "correctedText": "가장 적절한 교정 문장",
  "alternatives": ["대체 표현 1", "대체 표현 2", "대체 표현 3"]
}

조건:
- 피드백은 1~2문장으로 짧게 작성한다.
- 학습자를 비난하지 않는다.
- target_role이 grandfather이면 어르신께 말하는 상황으로 판단한다.
- category가 food이면 밥/식사 관련 표현을 우선한다.
- category가 name이면 이름/성함 관련 표현을 우선한다.
- category가 home이면 집/댁 관련 표현을 우선한다.
- category가 age이면 나이/연세 관련 표현을 우선한다.
- category가 birthday이면 생일/생신 관련 표현을 우선한다.
- correctedText는 실제로 바로 사용할 수 있는 자연스러운 문장이어야 한다.
"""

    user_prompt = {
        "userText": text,
        "category": category,
        "targetRole": target_role,
        "contextMatch": context_match,
        "politenessLevel": politeness_level,
        "naturalness": naturalness,
    }

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