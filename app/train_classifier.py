﻿from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# 프로젝트 최상단 폴더를 기준으로 경로 설정
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "formality_train.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "formality_classifier.joblib"

def main():
    # 1. 데이터 불러오기
    df = pd.read_csv(DATA_PATH)

    # 2. 필수 컬럼 확인
    required_cols = {"text", "category", "target_role", "turn_type", "label"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"데이터셋에 다음 컬럼이 누락되었습니다: {missing}")

    X = df[["text", "category", "target_role", "turn_type"]]
    y = df["label"]

    # 3. 
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "text", 
                TfidfVectorizer(
                    ngram_range=(1, 1),       # 문장 구조 암기가 아닌, 핵심 단어 단품 검사
                    token_pattern=r"(?u)\b\w+\b"
                ), 
                "text"
            ),
            ("meta", OneHotEncoder(handle_unknown="ignore"), ["category", "target_role", "turn_type"]),
        ]
    )

    # 4. 
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier", 
                RandomForestClassifier(
                    n_estimators=200,       
                    max_depth=6,             
                    min_samples_leaf=1,      
                    class_weight='balanced', 
                    random_state=42         
                )
            ),
        ]
    )
    model.fit(X, y)

    # 5. 완성된 AI 모델을 파일로 저장
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ 정형 시나리오 최적화 모델 저장 완료: {MODEL_PATH}")

if __name__ == "__main__":
    main()
