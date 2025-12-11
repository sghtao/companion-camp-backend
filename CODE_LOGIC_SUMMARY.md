# Companion Camp 백엔드 - 보상 지급 워크플로우 구현 정리

## 📋 전체 아키텍처

```
POST /evaluation/analyze/{username}
    ↓
[오케스트레이션: evaluation.py]
    ↓
┌─────────────────────────────────────────┐
│  1. SocialService (소셜 데이터 수집)    │
│  2. SocialService (광고 검증)           │
│  3. AIService (정성 평가)               │
│  4. ContractService (보상 지급)         │
└─────────────────────────────────────────┘
```

---

## 🔄 6단계 보상 지급 프로세스

### **1단계: 데이터 수집** (`SocialService`)
```python
# app/api/evaluation.py (라인 65-66)
stats = await social_service.get_user_data(username)
tweets = await social_service.get_user_tweets(username, max_results=20)
```

**기능:**
- `get_user_data()`: 사용자 통계 데이터 반환 (Mock)
  - 팔로워: 15,200명
  - 평균 좋아요: 350개
  - 참여율: 4.5%
  - 파급력 점수: 8.5/10
- `get_user_tweets()`: 최근 트윗 목록 반환 (Mock, 광고 키워드 포함)

---

### **2단계: 광고 검증 (Ad Verification)** (`SocialService`)
```python
# app/api/evaluation.py (라인 74-99)
```

**기능:**
- `verify_ad_compliance()`: 트윗에 필수 키워드 포함 여부 확인
  - `required_keyword`가 있으면 해당 키워드 검색
  - 없으면 기본 키워드: `["광고", "홍보", "협찬", "제공", "sponsored", "ad", "promotion"]`
- `verify_banner_image()`: 배너 이미지 포함 여부 (Mock, 항상 `True`)
- 최근 5개 트윗에서 검증

---

### **3단계: 정량 데이터 확인** (`evaluation.py`)
```python
# app/api/evaluation.py (라인 101-109)
social_reach_score = stats.get("reach_score", 0.0)  # 0~10 점수
social_score = (social_reach_score / 10.0) * 100     # 0~100 점수로 변환
```

**기능:**
- `reach_score`(0~10)를 100점 만점으로 변환
- 예: `8.5 / 10 * 100 = 85점`

---

### **4단계: 정성 평가 (AI)** (`AIService`)
```python
# app/api/evaluation.py (라인 111-116)
ai_result = await ai_service.evaluate_content_quality(username, stats, tweets)
ai_score = ai_result.get("quality_score", 85)
```

**기능:**
- `evaluate_content_quality()`: Gemini AI로 콘텐츠 품질 평가
  - 입력: 사용자명, 통계, 트윗 목록
  - 출력: `quality_score` (0~100 정수)
- **평가 기준:**
  1. 콘텐츠 품질 (창의성, 유용성, 독창성)
  2. 작성 품질 (명확성, 길이, 가독성)
  3. 참여 유도 (팬덤과의 상호작용)
  4. 일관성 (브랜드 아이덴티티)
- **예외 처리:** API 제한/타임아웃 시 `quality_score=85` 반환

---

### **5단계: 최종 점수 산정 & 컨트랙트 전송** (`ContractService`)
```python
# app/api/evaluation.py (라인 118-131)
final_score = int((social_score * 0.4) + (ai_score * 0.6))
reward_result = await contract_service.execute_reward_transaction(
    wallet_address=wallet_address,
    score=final_score
)
```

**기능:**
- **점수 산식:**
  ```
  Final Score = (Social Score × 40%) + (AI Score × 60%)
  ```
- `ContractService.execute_reward_transaction()`:
  - 토큰 계산: `score * 10` (최소 100, 최대 10,000)
  - Mock 트랜잭션 해시 생성 (SHA256 기반)
  - 반환: `tx_hash`, `rewarded_amount`, `wallet_address`

---

### **6단계: 결과 반환** (`evaluation.py`)
```python
# app/api/evaluation.py (라인 133-152)
return {
    "username": username,
    "verification": {
        "is_ad_verified": is_ad_verified,
        "has_banner": has_banner
    },
    "scores": {
        "social_score": round(social_score, 2),
        "ai_score": ai_score,
        "final_score": final_score
    },
    "reward": {
        "tx_hash": reward_result.get("tx_hash"),
        "amount": reward_result.get("rewarded_amount"),
        "wallet_address": wallet_address
    }
}
```

---

## 🏗️ 주요 서비스 클래스

### **1. `SocialService`** (`app/services/social_service.py`)

**주요 메서드:**
- `get_user_data()`: Mock 사용자 통계 데이터 반환
- `get_user_tweets()`: Mock 트윗 목록 반환
- `verify_ad_compliance()`: 광고 키워드 검증
- `verify_banner_image()`: 배너 이미지 검증 (Mock, 항상 `True`)

**Mock 데이터:**
```python
{
    "username": username,
    "followers": 15200,
    "avg_likes": 350,
    "avg_retweets": 45,
    "avg_replies": 12,
    "engagement_rate": 4.5,
    "reach_score": 8.5,
    "has_promotion_content": True,
    "has_banner_image": True
}
```

---

### **2. `AIService`** (`app/services/ai_service.py`)

**주요 메서드:**
- `evaluate_content_quality()`: Gemini AI로 콘텐츠 품질 평가
  - 입력: `username`, `stats`, `tweets`
  - 출력: `{"quality_score": 0~100}`

**예외 처리:**
- API 제한(429), 타임아웃, JSON 파싱 실패 시 → `quality_score=85` 반환
- 데모가 멈추지 않도록 강력한 Mock 처리

---

### **3. `ContractService`** (`app/services/contract_service.py`)

**주요 메서드:**
- `execute_reward_transaction()`: Mock 트랜잭션 실행
  - 입력: `wallet_address`, `score`
  - 출력: `tx_hash`, `rewarded_amount`, `wallet_address`

**토큰 계산 로직:**
```python
rewarded_amount = max(100, min(10000, score * 10))
```

---

## 🎯 Mock 처리 전략

### **X API 제한 대응**
- `get_user_data()`: 실제 API 호출 코드 주석 처리, Mock 데이터 즉시 반환
- `get_user_tweets()`: Mock 트윗 목록 생성 (광고 키워드 포함)

### **Gemini API 제한 대응**
- 429/quota/timeout 에러 시 → `quality_score=85` 반환
- JSON 파싱 실패 시 → `quality_score=85` 반환

---

## 📡 API 엔드포인트

### **요청**
```
POST /evaluation/analyze/{username}
```

**Body:**
```json
{
  "wallet_address": "0x...",
  "required_keyword": "광고"  // 선택사항
}
```

### **응답**
```json
{
  "username": "BabyDoge",
  "verification": {
    "is_ad_verified": true,
    "has_banner": true
  },
  "scores": {
    "social_score": 85.0,
    "ai_score": 85,
    "final_score": 85
  },
  "reward": {
    "tx_hash": "0x...",
    "amount": 850,
    "wallet_address": "0x..."
  }
}
```

---

## ✨ 핵심 특징

1. **데모 안정성**: 모든 외부 API 호출에 Mock 처리 적용
2. **점수 체계**: 정량(40%) + 정성(60%) 가중치 적용
3. **광고 검증**: 키워드/배너 이미지 검증 로직
4. **예외 처리**: 모든 단계에서 실패 시 Mock 데이터로 대체

---

## 📁 파일 구조

```
app/
├── api/
│   └── evaluation.py          # 오케스트레이션 (6단계 프로세스)
├── services/
│   ├── social_service.py      # 소셜 데이터 수집 & 광고 검증
│   ├── ai_service.py          # AI 정성 평가
│   └── contract_service.py    # 스마트 컨트랙트 연동 (Mock)
└── main.py                    # FastAPI 앱 진입점
```

---

## 🔄 실행 흐름 다이어그램

```
[클라이언트 요청]
    ↓
POST /evaluation/analyze/{username}
    ↓
[1단계] SocialService.get_user_data() → Mock 통계 데이터
[1단계] SocialService.get_user_tweets() → Mock 트윗 목록
    ↓
[2단계] SocialService.verify_ad_compliance() → 키워드 검증
[2단계] SocialService.verify_banner_image() → 배너 검증 (항상 True)
    ↓
[3단계] 정량 데이터 확인 → social_score 계산 (0~100)
    ↓
[4단계] AIService.evaluate_content_quality() → ai_score 계산 (0~100)
    ↓
[5단계] 최종 점수 산정 → final_score = (social_score × 0.4) + (ai_score × 0.6)
[5단계] ContractService.execute_reward_transaction() → 토큰 지급 (Mock)
    ↓
[6단계] 결과 반환 → JSON 응답
```

---

## 📝 구현 날짜
2025-12-12
## 👥 작성자
Companion Camp 백엔드 팀


