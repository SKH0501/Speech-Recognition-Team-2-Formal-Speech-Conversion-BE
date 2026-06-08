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
        
        # 1. 역할 정의 및 한국어 페르소나 극대화
        if target_role == "grandfather":
            role_name = "할아버지"
            user_name = "손주"
            persona_prompt = (
                "당신은 자상하고 다정한 한국의 70대 '할아버지'입니다. 사용자는 당신의 귀여운 '손주'입니다.\n"
                "반드시 친근하고 따뜻한 할아버지의 말투(~단다, ~했니?, 오냐, 허허)만 사용하세요.\n"
                "젊은이들이 쓰는 말투(~하더라구요, 식사를 했습니다, 어머)나 번역투는 절대 금지합니다.\n"
                "실제 한국 할아버지가 손주에게 말하듯 자연스럽고 구어체로 1~2문장 내외로만 짧게 대답하세요."
            )
        elif target_role == "friend":
            role_name = "친구"
            user_name = "친구"
            persona_prompt = (
                "당신은 사용자의 친한 동갑내기 '친구'입니다.\n"
                "반드시 요즘 한국 학생들이 친구끼리 편하게 쓰는 구어체 반말(~했어?, 진짜?, 대박)을 사용하세요.\n"
                "존댓말이나 딱딱한 문어체 문장은 절대 금지합니다.\n"
                "친근하고 발랄하게 1~2문장 내외로 짧게 대답하세요."
            )
        else:
            role_name = "AI 상대"
            user_name = "사용자"
            persona_prompt = "당신은 친절한 대화 상대입니다. 짧게 대답해주세요."

        # 2. 앞선 시나리오 대화 맥락 조립 (역할 동적 반영)
        context_prompt = "[앞선 상황 대화 내용 (상황 참고용)]\n"
        for msg in scenario_history:
            # 타겟 롤에 맞게 발화자 이름을 동적으로 변경
            display_role = f"{user_name}(사용자)" if msg["role"] == "user" else f"{role_name}(당신)"
            
            # 메타 가이드나 예시 텍스트가 대화에 섞여 들어오는 것을 방어하기 위한 필터링
            content = msg["content"]
            if "(예시:" in content or "물어보세요" in content:
                continue # 쓰레기 텍스트는 히스토리에서 제외
                
            context_prompt += f"- {display_role}: {content}\n"
        
        # 3. 마스터 시스템 프롬프트 완성 (AI에게 엄격한 규칙 부여)
        system_prompt = (
            f"{persona_prompt}\n\n"
            f"{context_prompt}\n"
            f"⚠️ [절대 규칙]\n"
            f"1. 위 '앞선 상황 대화 내용'의 흐름을 이어받아 자연스럽게 대화를 지속하세요.\n"
            f"2. 대화 내용 중 시스템 가이드라인, 괄호 예시, 번역문 등이 있다면 철저히 무시하고 오직 '진짜 대화'에만 집중하세요.\n"
            f"3. 억지로 문장을 꾸며내지 말고, 질문에 맞는 현실적인 답변만 간결하게 하세요."
        )

        # 4. 메시지 구조화
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(free_talk_history)
        messages.append({"role": "user", "content": user_message})

        # 5. Groq API 호출 (Llama 3.3 70B + 낮은 Temperature로 헛소리 차단)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=messages,
            temperature=0.3,  
            max_tokens=150
        )

        return response.choices[0].message.content
