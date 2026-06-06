import os
from groq import AsyncGroq


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = AsyncGroq(api_key=GROQ_API_KEY)

class LLMService:
    @staticmethod
    async def generate_free_talk_response(
        target_role: str, 
        scenario_history: list, 
        user_message: str, 
        free_talk_history: list
    ) -> str:
        
        # 1. 페르소나 (역할 부여)
        if target_role == "grandfather":
            system_prompt = (
                "당신은 인자하고 다정한 한국의 할아버지입니다. 사용자는 당신의 귀여운 손주입니다. "
                "반드시 부드럽고 따뜻한 할아버지의 말투(~단다, ~했니?, 허허)로 짧고 자연스럽게 대답하세요."
            )
        elif target_role == "friend":
            system_prompt = (
                "당신은 사용자의 13살 동갑내기 친구입니다. "
                "반드시 반말을 사용하고, 요즘 한국 학생들처럼 친근하고 발랄하게 1~2문장으로 짧게 대답해."
            )
        else:
            system_prompt = "당신은 친절한 대화 상대입니다. 짧게 대답해주세요."

        # 2. 방금 전까지 했던 시나리오 대화 요약 주입
        context_prompt = "앞선 상황 대화(참고용):\n"
        for msg in scenario_history:
            role = "손주(사용자)" if msg["role"] == "user" else "할아버지(당신)"
            context_prompt += f"- {role}: {msg['content']}\n"
        
        system_prompt += f"\n\n{context_prompt}\n이제 위 상황에 이어서 사용자와 자연스럽게 자유 대화를 이어가세요."

        # 3. 메시지 조립
        messages = [{"role": "system", "content": system_prompt}]
        
        # 이전 자유대화 기록(free_talk_history) 추가
        messages.extend(free_talk_history)
        
        # 이번에 유저가 한 말 추가
        messages.append({"role": "user", "content": user_message})

        # 4. Groq API 호출 (llama3-8b-8192 모델이 빠르고 한국어도 꽤 잘합니다)
        response = await client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        return response.choices[0].message.content
