# 🎙️ Honorific Speech Trainer (Backend)

## 📌 Overview

이 프로젝트는 외국인 학습자를 위한 **존댓말 학습 음성 시스템**의 백엔드입니다.
사용자의 음성을 입력받아 이를 텍스트로 변환(STT)하고,
상황에 맞는 존댓말 표현을 평가 및 피드백을 제공합니다.

현재 단계는 **MVP (Minimum Viable Product)** 기준으로 설계되었으며,
DB 없이 **세션 기반 stateless 구조 + in-memory 저장 방식**을 사용합니다.

> ⚠️ 본 문서는 초기 설계 초안이며, 팀 논의를 통해 API 및 구조는 변경될 수 있습니다.

---

## 🧠 Core Flow

```text
사용자 음성 입력
→ STT (Speech-to-Text)
→ 텍스트 분석 (존댓말 평가)
→ 피드백 생성
→ 응답 반환 (텍스트 / 음성)
```

---

## 🚀 Features (MVP)

* 카테고리 기반 대화 시작 (밥, 나이, 집 등)
* 음성 입력 기반 문장 평가
* 존댓말 적절성 판단
* 교정 문장 및 피드백 제공
* 간단한 대화 흐름 (2~3 turn)

---

## 🧩 API 명세서

### 📍 Base URL

```text
http://localhost:8000/api
```

---

### 1. 서버 상태 확인

| 기능       | API       | Method |
| -------- | --------- | ------ |
| 서버 상태 확인 | `/health` | GET    |

---

### 2. 카테고리 리스트 조회

| 기능      | API           | Method |
| ------- | ------------- | ------ |
| 카테고리 조회 | `/categories` | GET    |

---

### 3. 대화 세션 시작

| 기능    | API               | Method |
| ----- | ----------------- | ------ |
| 세션 시작 | `/sessions/start` | POST   |

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

| 기능    | API                                  | Method |
| ----- | ------------------------------------ | ------ |
| 음성 평가 | `/sessions/{sessionId}/turns/speech` | POST   |

#### Content-Type

```
multipart/form-data
```

#### Request

* audio: 음성 파일

#### Response

```json
{
  "success": true,
  "data": {
    "transcript": "밥 먹었어?",
    "isCorrect": false,
    "feedback": "존댓말을 사용하는 것이 더 적절해요.",
    "recommendedAnswer": "식사 하셨어요?",
    "alternatives": [
      "식사 하셨어요?",
      "밥 드셨어요?"
    ],
    "nextAction": "RETRY",
    "nextQuestion": null
  }
}
```

---

### 5. 텍스트 기반 평가 (디버깅용)

| 기능     | API                                | Method |
| ------ | ---------------------------------- | ------ |
| 텍스트 평가 | `/sessions/{sessionId}/turns/text` | POST   |

#### Request

```json
{
  "text": "밥 먹었어?"
}
```

---

### 6. 대화 세션 종료

| 기능    | API                         | Method |
| ----- | --------------------------- | ------ |
| 세션 종료 | `/sessions/{sessionId}/end` | POST   |

---

### 7. TTS (피드백 음성 생성)

| 기능  | API    | Method |
| --- | ------ | ------ |
| TTS | `/tts` | POST   |

---

## 🔁 Conversation Flow

```text
1. 카테고리 선택
→ POST /sessions/start

2. 사용자 음성 입력
→ POST /sessions/{sessionId}/turns/speech

3. 평가 결과 반환
→ feedback + recommended sentence

4. 다음 행동
→ RETRY (다시 말하기)
→ NEXT (다음 질문)
→ END (종료)
```

---

## 🗂️ Project Structure

```text
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
│   ├── evaluation_service.py
│   └── tts_service.py
├── data/
│   └── scenarios.json
```

---

## ⚙️ Tech Stack (Planned)

* FastAPI
* Python 3.10+
* STT: Whisper (planned)
* NLP: GPT / rule-based
* TTS: gTTS or external API

---

## 🧪 Development Strategy

### Step 1 (현재)

* Fake pipeline (rule-based evaluation)
* API 구조 확정

### Step 2

* STT (Whisper) 연결

### Step 3

* GPT 기반 평가 로직 추가

### Step 4

* TTS 연결

---

## ▶️ How to Run

```bash
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

---

## 🤝 Collaboration Notes

* 본 프로젝트는 MVP 기준 설계입니다.
* API 및 구조는 팀 협의에 따라 변경될 수 있습니다.
* 우선은 해당 구조를 기준으로 개발을 진행하고, 이후 AI 모델 연결 시 개선합니다.

---

## 📌 Summary

이 백엔드는 단순 REST API가 아니라,
**음성 기반 대화형 학습 흐름을 관리하는 "세션 기반 대화 엔진"**입니다.
