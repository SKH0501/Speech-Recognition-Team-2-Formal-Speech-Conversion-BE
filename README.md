# 🎙️ Honorific Speech Trainer (Backend)

## 📌 Overview

이 프로젝트는 외국인 학습자를 위한 **존댓말 학습 음성 시스템의 백엔드**입니다.  
사용자의 음성을 입력받아 이를 텍스트로 변환(STT)하고,  
상황에 맞는 존댓말 표현을 평가하여 교정 및 피드백을 제공합니다.

본 시스템은 단순히 외부 AI 모델을 호출하는 구조가 아니라,  
**규칙 기반 NLP(rule-based)와 데이터 기반 분류 모델(classifier)을 결합한 하이브리드 구조**로 설계됩니다.

현재는 MVP(Minimum Viable Product) 단계로,  
외부 DB 없이 **서버 메모리 기반(in-memory)의 세션 관리 구조**를 사용합니다.

> ⚠️ 본 문서는 초기 설계 초안이며, 팀 논의를 통해 API 및 구조는 변경될 수 있습니다.

---

## 🧠 Core Flow

```
사용자 음성 입력
→ STT (Speech-to-Text)
→ 텍스트 분석 (NLP: 존댓말 평가)
→ 피드백 및 교정 문장 생성
→ (선택) TTS (Text-to-Speech)
→ 응답 반환 (텍스트 / 음성)
```

---

## 🚀 Features (MVP)

- 카테고리 기반 대화 시작 (밥, 나이, 집 등)
- 음성 입력 기반 문장 평가
- 존댓말 적절성 및 공손성 판단
- 교정 문장 및 피드백 제공
- 간단한 대화 흐름 (2~3 turn)
- 텍스트 기반 평가 API 제공 (NLP 디버깅용)

---

## 🧩 API 명세서

### 📍 Base URL
```
http://localhost:8000/api
```

---

### 1. 서버 상태 확인

| 기능 | API | Method |
|------|-----|--------|
| 서버 상태 확인 | `/health` | GET |

---

### 2. 카테고리 리스트 조회

| 기능 | API | Method |
|------|-----|--------|
| 카테고리 조회 | `/categories` | GET |

---

### 3. 대화 세션 시작

| 기능 | API | Method |
|------|-----|--------|
| 세션 시작 | `/sessions/start` | POST |

#### Request
```json
{
  "category": "food",
  "targetRole": "grandfather",
  "language": "ko"
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "sessionId": "session_001",
    "prompt": "상대방이 밥을 먹었는지 물어보세요!"
  }
}
```

---

### 4. 음성 응답 평가 (핵심 API)

| 기능 | API | Method |
|------|-----|--------|
| 음성 평가 | `/sessions/{sessionId}/turns/speech` | POST |

#### Content-Type
```
multipart/form-data
```

#### Request
```
audio: 음성 파일
```

#### Response
```json
{
  "success": true,
  "data": {
    "transcript": "밥 먹었어?",
    "judgement": "INAPPROPRIATE",
    "score": 28,
    "feedback": "어르신께는 반말보다 존댓말을 사용하는 것이 더 적절해요.",
    "errorTypes": [
      "INFORMAL_ENDING",
      "ROLE_MISMATCH"
    ],
    "recommendedAnswer": "식사하셨어요?",
    "alternatives": [
      "식사하셨어요?",
      "진지 잡수셨어요?"
    ],
    "nextAction": "RETRY",
    "nextQuestion": null
  }
}
```

---

### 5. 텍스트 기반 평가 (디버깅용)

| 기능 | API | Method |
|------|-----|--------|
| 텍스트 평가 | `/sessions/{sessionId}/turns/text` | POST |

#### Request
```json
{
  "text": "밥 먹었어?"
}
```

---

### 6. 대화 세션 종료

| 기능 | API | Method |
|------|-----|--------|
| 세션 종료 | `/sessions/{sessionId}/end` | POST |

---

### 7. TTS (피드백 음성 생성)

| 기능 | API | Method |
|------|-----|--------|
| TTS | `/tts` | POST |

---

## 🔁 Conversation Flow

```
1. 카테고리 선택
→ POST /sessions/start

2. 사용자 음성 입력
→ POST /sessions/{sessionId}/turns/speech

3. 평가 결과 반환
→ transcript + judgement + feedback + 추천 문장

4. 다음 행동
→ RETRY / NEXT / END
```

---

## 🧠 NLP Architecture

### Rule-based Evaluation
- 종결어미 분석
- 높임 어휘 사용 여부
- 금지 표현 탐지
- 대상(role) 기반 공손성 평가

### Classifier (Planned)
- 문장 공손성 분류

### Feedback Generator
- 오류 기반 피드백 생성
- 교정 문장 제공

---

## 🗂️ Project Structure

```
app/
├── main.py
├── core/
│   └── session_store.py
├── routers/
│   ├── categories.py
│   ├── sessions.py
│   └── tts.py
├── schemas/
│   ├── session.py
│   ├── evaluation.py
│   └── tts.py
├── services/
│   ├── scenario_service.py
│   ├── session_service.py
│   ├── stt_service.py
│   ├── tts_service.py
│   └── evaluation/
│       ├── evaluator.py
│       ├── rule_engine.py
│       ├── classifier.py
│       ├── feedback_generator.py
│       └── response_builder.py
```

---

## ▶️ How to Run

```bash
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

---

## 📌 Summary

이 백엔드는  
**음성 기반 학습을 위한 세션 중심 대화 엔진**이며,

👉 Rule-based + 학습 기반 NLP를 결합한  
👉 설명 가능한 존댓말 평가 시스템을 목표로 합니다.
