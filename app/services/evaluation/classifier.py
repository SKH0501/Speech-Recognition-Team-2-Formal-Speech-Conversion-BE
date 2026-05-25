from pathlib import Path
import joblib
import pandas as pd

# train_classifier.py와 완전히 동일한 경로 메커니즘 적용
BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "models" / "formality_classifier.joblib"

class FormalityClassifier:
    def __init__(self):
       
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"\n❌ [오류] 학습된 모델 파일(.joblib)을 찾을 수 없습니다!\n"
                f"먼저 'train_classifier.py'를 실행하여 모델을 생성해주세요.\n"
                f"확인된 경로: {MODEL_PATH}"
            )
        
        # 저장된 완전히 학습된(Fitted) 모델 파이프라인 로드
        self.model = joblib.load(MODEL_PATH)

    def predict(self, text: str, category: str, target_role: str, turn_type: str):
        # 입력 데이터를 DataFrame 형태로 변환 (학습 때와 동일한 피처 구조)
        row = pd.DataFrame([{
            "text": text,
            "category": category,
            "target_role": target_role,
            "turn_type": turn_type
        }])
        
        # 예측 및 확신도 추출
        pred_label = self.model.predict(row)[0]
        proba = self.model.predict_proba(row)[0]
        confidence = float(proba.max())
        
        return {
            "label": pred_label,
            "confidence": confidence
        }

# 싱글톤 패턴으로 인스턴스 반환
_classifier_instance = None

def get_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FormalityClassifier()
    return _classifier_instance
