import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def create_expanded_dataset():
    """진성 님이 기획하신 [대상별/턴별] 세분화 대화 흐름에 맞춘 확장 데이터셋 생성"""
    print("📊 새로운 대화 흐름 구조에 맞춘 'honorific_dataset.csv'를 생성합니다.")
    
    data = {
        "domain": [], "target": [], "turn_type": [], "transcript": [],
        "context": [], "honorific": [], "naturalness": []
    }
    
    # 데이터 추가를 위한 헬퍼 함수
    def add_data(domain, target, turn_type, text, c, h, n):
        data["domain"].append(domain)
        data["target"].append(target)
        data["turn_type"].append(turn_type)
        data["transcript"].append(text)
        data["context"].append(c)
        data["honorific"].append(h)
        data["naturalness"].append(n)

    # 1. 식사 (할아버지 관련 대화)
    add_data("식사", "할아버지", "질문", "할아버지 진지 잡수셨어요?", "HIGH", "HIGH", "HIGH")
    add_data("식사", "할아버지", "질문", "할아버지 밥 먹었어요?", "HIGH", "MEDIUM", "MEDIUM")
    add_data("식사", "할아버지", "질문", "너 밥 드셨어요?", "HIGH", "LOW", "LOW")
    add_data("식사", "할아버지", "질문", "할아버지 밥으로 뭐 먹었어?", "HIGH", "LOW", "LOW")
    add_data("식사", "할아버지", "대답", "할아버지가 진지 잡수셨냐고 물어보셨습니다.", "HIGH", "HIGH", "HIGH")
    add_data("식사", "할아버지", "대답", "할아버지가 밥 먹었냐고 물어봄", "HIGH", "LOW", "LOW")

    # 2. 나이 (할아버지 vs 친구)
    add_data("나이", "할아버지", "질문", "올해 연세가 어떻게 되십니까?", "HIGH", "HIGH", "HIGH")
    add_data("나이", "할아버지", "질문", "할아버지 몇 살이야?", "HIGH", "LOW", "LOW")
    add_data("나이", "친구", "질문", "너 몇 살이야?", "HIGH", "HIGH", "HIGH")
    add_data("나이", "친구", "질문", "올해 연세가 어떻게 되십니까?", "HIGH", "LOW", "MEDIUM") # 친구한테 연세는 어색함
    add_data("나이", "할아버지", "대답", "할아버지께서 제 나이를 물어보셨어요.", "HIGH", "HIGH", "HIGH")

    # 3. 이름 (할아버지 vs 친구)
    add_data("이름", "할아버지", "질문", "함자가 어떻게 되십니까?", "HIGH", "HIGH", "HIGH")
    add_data("이름", "할아버지", "질문", "할아버지 이름이 뭐야?", "HIGH", "LOW", "LOW")
    add_data("이름", "친구", "질문", "이름이 뭐야?", "HIGH", "HIGH", "HIGH")
    add_data("이름", "친구", "질문", "성함이 어떻게 되시나요?", "HIGH", "MEDIUM", "MEDIUM")

    # 4. 생일 (할아버지 관련 - 피피티 6페이지 예시 반영)
    add_data("생일", "할아버지", "질문", "할아버지 생신이 언제이신가요?", "HIGH", "HIGH", "HIGH")
    add_data("생일", "할아버지", "질문", "생일 축하해", "MEDIUM", "LOW", "MEDIUM") # PPT 6p 예시 
    add_data("생일", "할아버지", "대답", "할아버지가 제 생일을 물어보셨어요.", "HIGH", "HIGH", "HIGH")
    
    # 5. 동문서답 (문맥 오류용 데이터)
    add_data("이름", "할아버지", "질문", "할아버지 진지 드셨어요?", "LOW", "HIGH", "HIGH") # 이름 상황에 밥 얘기
    add_data("생일", "친구", "질문", "너 이름이 뭐야?", "LOW", "HIGH", "HIGH") # 생일 상황에 이름 얘기

    df = pd.DataFrame(data)
    df.to_csv("honorific_dataset.csv", index=False, encoding="utf-8-sig")
    print("✅ 'honorific_dataset.csv' 생성 완료!\n")

def train_multitask_model():
    if not os.path.exists("honorific_dataset.csv"):
        create_expanded_dataset()
        
    df = pd.read_csv("honorific_dataset.csv")
    
    # 메타 정보(도메인, 타겟, 턴)와 발화를 하나로 묶어서 패턴을 학습하게 만듭니다.
    df['meta_text'] = df['domain'] + " " + df['target'] + " " + df['turn_type'] + " " + df['transcript']
    X = df['meta_text']
    
    print("🧩 3대 지표(Context, Honorific, Naturalness) 멀티 레이블 벡터화 진행 중...")
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(1, 3))
    X_vec = vectorizer.fit_transform(X)
    
    # 3개의 차원을 각각 예측할 분류기 3개 학습
    clf_context = LogisticRegression(class_weight='balanced').fit(X_vec, df['context'])
    clf_honorific = LogisticRegression(class_weight='balanced').fit(X_vec, df['honorific'])
    clf_naturalness = LogisticRegression(class_weight='balanced').fit(X_vec, df['naturalness'])
    
    # 하나의 통합 딕셔너리로 묶어서 파일 하나로 저장
    model_assets = {
        "vectorizer": vectorizer,
        "clf_context": clf_context,
        "clf_honorific": clf_honorific,
        "clf_naturalness": clf_naturalness
    }
    
    joblib.dump(model_assets, 'honorific_model.pkl')
    print("🎉 완료! 3차원 평가가 가능한 'honorific_model.pkl' 자산이 성공적으로 빌드되었습니다.")

if __name__ == "__main__":
    train_multitask_model()
