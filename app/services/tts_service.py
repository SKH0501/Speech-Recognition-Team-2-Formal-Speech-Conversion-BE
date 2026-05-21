import os
from gtts import gTTS

class TTSService:
    def __init__(self):
        # 결과 음성 파일들을 임시로 저장할 폴더 생성
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_speech(self, text: str, filename: str = "output.mp3") -> str:
        """
        텍스트를 음성(MP3) 파일로 변환하고 저장된 파일 경로를 반환합니다.
        """
        if not text:
            return ""

        try:
            file_path = os.path.join(self.output_dir, filename)
            
            # 한국어(ko) 음성 생성
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(file_path)
            
            print(f"🔊 TTS 파일 생성 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ TTS 오류 발생: {e}")
            return ""

# 로컬 단독 테스트용 코드
if __name__ == "__main__":
    tts = TTSService()
    # tts.generate_speech("할아버지 진지 잡수셨어요?", "grandfather_ask.mp3")
