import os
from openai import OpenAI

class STTService:
    def __init__(self):
        # OpenAI API 키를 시스템 환경변수에서 가져옵니다.
        # 키가 없다면 직접 텍스트로 "your-api-key"를 넣어도 됩니다.
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️ 경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=self.api_key)

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        음성 파일을 입력받아 텍스트(transcript)로 변환합니다.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"음성 파일을 찾을 수 없습니다: {audio_file_path}")

        try:
            with open(audio_file_path, "rb") as audio_file:
                # 한국어(ko) 학습 시스템이므로 language="ko"를 명시하여 인식률을 극대화합니다.
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko"
                )
            return response.text
        except Exception as e:
            print(f"❌ STT 오류 발생: {e}")
            return ""

# 로컬 단독 테스트용 코드
if __name__ == "__main__":
    # 테스트하고 싶은 음성 파일 경로를 넣고 실행해보세요.
    stt = STTService()
    # test_text = stt.transcribe_audio("test.wav")
    # print("인식된 텍스트:", test_text)
