# Companion Camp Backend - 코드베이스 분석 리포트

## 📋 개요

현재 코드베이스는 **FastAPI** 기반의 백엔드 서버로, 펫 IP 플랫폼의 핵심 기능을 구현하고 있습니다.

---

## 🎯 구현해야 할 핵심 기능

### 1. 밈코인 구매 (Meme Coin Purchase)
### 2. X 게시물 평가 및 보상 (Content Evaluation & Reward)

---

## ✅ 1. 밈코인 구매 기능 구현 상태

### 📁 관련 파일
- `app/api/coins.py` - 밈코인 관련 API 엔드포인트
- `app/services/coin_service.py` - 실시간 코인 가격 조회 서비스
- `app/db.py` - SQLite 데이터베이스 (구매 내역 저장)

### 🔍 구현 상세 분석

#### 1.1 코인 목록 조회 (`GET /coins`)
**위치**: `app/api/coins.py:36-65`
- **기능**: DexScreener API를 통해 실시간 Solana 밈코인 가격 조회
- **지원 코인**: BONK, WIF, POPCAT
- **데이터 소스**: 실제 API (`https://api.dexscreener.com/latest/dex/tokens/{addresses}`)
- **반환 데이터**:
  - `name`, `symbol`, `priceUsd`, `priceChange24h`
  - `imageUrl`, `address`, `volume24h`, `liquidity`
- **상태**: ✅ **완전 구현됨** (실제 데이터 사용)

#### 1.2 구매 트랜잭션 저장 (`POST /coins/purchase`)
**위치**: `app/api/coins.py:68-129`
- **기능**: 블록체인에서 실행된 구매 트랜잭션을 데이터베이스에 저장
- **입력 파라미터**:
  - `username`: 구매자 사용자명
  - `coin_symbol`: 코인 심볼 (BONK, WIF 등)
  - `amount`: 구매 수량
  - `tx_hash`: 블록체인 트랜잭션 해시
- **데이터베이스**: SQLite `purchases` 테이블에 저장
- **상태**: ✅ **완전 구현됨** (실제 DB 저장)

#### 1.3 구매 내역 조회 (`GET /coins/history/{username}`)
**위치**: `app/api/coins.py:132-172`
- **기능**: 특정 사용자의 모든 구매 내역 조회
- **데이터 소스**: SQLite 데이터베이스
- **반환 데이터**: 구매 ID, 코인 심볼, 수량, 트랜잭션 해시, 구매 시간
- **상태**: ✅ **완전 구현됨**

#### 1.4 데이터베이스 스키마
**위치**: `app/db.py:23-31`
```sql
CREATE TABLE purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    coin_symbol TEXT NOT NULL,
    amount REAL NOT NULL,
    tx_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
- **상태**: ✅ **완전 구현됨**

### 📊 밈코인 구매 워크플로우 구현 상태

| 단계 | 설명 | 구현 상태 |
|------|------|----------|
| 1. 밈코인 구매 요청 | 프론트엔드에서 구매 요청 | ✅ API 준비됨 |
| 2. 서명 | 지갑에서 서명 (프론트엔드) | ⚠️ 프론트엔드 영역 |
| 3. 컨트랙트 트랜잭션 전송 | 블록체인에 트랜잭션 전송 | ⚠️ 프론트엔드/컨트랙트 영역 |
| 4. 거래 결과 저장 | `POST /coins/purchase`로 결과 저장 | ✅ **완전 구현됨** |

**결론**: 밈코인 구매 기능은 **백엔드에서 완전히 구현됨**. 프론트엔드에서 트랜잭션 실행 후 결과만 백엔드로 전송하면 됩니다.

---

## ✅ 2. X 게시물 평가 및 보상 기능 구현 상태

### 📁 관련 파일
- `app/api/evaluation.py` - 평가 및 보상 워크플로우 API
- `app/services/social_service.py` - X API 데이터 수집
- `app/services/ai_service.py` - Gemini AI 품질 평가
- `app/services/contract_service.py` - 스마트 컨트랙트 연동
- `app/services/twitter_client.py` - X API 클라이언트

### 🔍 단계별 구현 상세 분석

#### 2.1 데이터 수집 (X API로 사용자 정보 + 게시물 크롤링)
**위치**: `app/services/social_service.py:14-120`
- **메서드**: `get_user_data()`, `get_user_tweets()`
- **기능**:
  - X API를 통해 사용자 정보 조회 (팔로워, 팔로잉, 트윗 수 등)
  - 최근 트윗 목록 조회 (최대 20개)
  - 평균 좋아요/리트윗/댓글 수 계산
  - 참여율(Engagement Rate) 계산
  - 파급력 점수(Reach Score) 계산
- **현재 상태**: ⚠️ **Mock 모드로 동작 중**
  - 실제 X API 호출 코드는 주석 처리됨 (429 에러 대응)
  - Mock 데이터를 반환하여 데모 가능
  - 실제 API 코드는 완전히 구현되어 있음 (주석 해제 시 사용 가능)
- **구현 완성도**: ✅ **코드 완전 구현됨** (현재 Mock 모드)

#### 2.2 광고 컨텐츠 포함 확인 (선택사항)
**위치**: `app/services/social_service.py:174-202`
- **메서드**: `verify_ad_compliance()`, `verify_banner_image()`
- **기능**:
  - 트윗 텍스트에서 광고 키워드 검색 (대소문자 무시)
  - 배너 이미지 포함 여부 확인 (현재 Mock: 항상 True)
- **상태**: ✅ **기본 구현 완료** (배너 이미지는 Mock)
- **사용 위치**: `app/api/evaluation.py:74-99`에서 호출

#### 2.3 정량 데이터 확인 (팔로워, 좋아요, 리포스트 등)
**위치**: `app/api/evaluation.py:101-109`
- **데이터 소스**: `social_service.get_user_data()` 반환값
- **확인 항목**:
  - 팔로워 수 (`followers`)
  - 참여율 (`engagement_rate`)
  - 평균 좋아요/리트윗/댓글 수
  - 소셜 점수 (`reach_score` → 0~100점으로 변환)
- **점수 계산**: `social_score = (reach_score / 10.0) * 100`
- **상태**: ✅ **완전 구현됨**

#### 2.4 AI로 게시물 품질 체크
**위치**: `app/services/ai_service.py:24-114`
- **메서드**: `evaluate_content_quality()`
- **AI 모델**: Google Gemini 2.0 Flash Lite
- **기능**:
  - 사용자 통계 데이터와 최근 트윗 5개를 분석
  - 콘텐츠 품질, 작성 품질, 참여 유도, 일관성 평가
  - 0~100점 정수로 품질 점수 반환
- **에러 처리**: API 제한/타임아웃 시 Mock 점수(85점) 반환
- **상태**: ✅ **완전 구현됨** (실제 Gemini API 사용)

#### 2.5 점수 산정 및 컨트랙트 전송
**위치**: `app/api/evaluation.py:118-131`
- **최종 점수 계산식**:
  ```python
  final_score = (social_score * 0.4) + (ai_score * 0.6)
  ```
  - 정량 점수(소셜): 40% 가중치
  - 정성 점수(AI): 60% 가중치
- **컨트랙트 전송**: `contract_service.execute_reward_transaction()`
- **상태**: ✅ **완전 구현됨**

#### 2.6 컨트랙트 서비스 (보상 토큰 계산 및 전송)
**위치**: `app/services/contract_service.py:17-52`
- **메서드**: `execute_reward_transaction()`
- **기능**:
  - 점수에 따라 토큰 양 계산: `rewarded_amount = max(100, min(10000, score * 10))`
  - 트랜잭션 해시 생성 (현재 Mock)
- **현재 상태**: ⚠️ **Mock 구현**
  - 실제 블록체인 연동은 미구현
  - Story Protocol Smart Contract 연동 필요
- **구현 완성도**: ⚠️ **Mock으로 동작** (실제 컨트랙트 연동 필요)

#### 2.7 결과 반환
**위치**: `app/api/evaluation.py:133-152`
- **반환 데이터**:
  ```json
  {
    "username": "사용자명",
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
- **상태**: ✅ **완전 구현됨**

### 📊 X 게시물 평가 및 보상 워크플로우 구현 상태

| 단계 | 설명 | 구현 상태 | 비고 |
|------|------|----------|------|
| 1. 데이터 수집 | X API로 사용자 정보 + 게시물 크롤링 | ✅ 구현됨 | 현재 Mock 모드 |
| 2. 광고 검증 | 게시물에 광고 컨텐츠 포함 확인 | ✅ 구현됨 | 선택사항 |
| 3. 정량 데이터 확인 | 팔로워, 좋아요, 리포스트 등 | ✅ 구현됨 | 완전 구현 |
| 4. AI 품질 평가 | Gemini로 게시물 품질 점수화 | ✅ 구현됨 | 실제 API 사용 |
| 5. 점수 산정 및 컨트랙트 전송 | 최종 점수 계산 후 컨트랙트 호출 | ✅ 구현됨 | 컨트랙트는 Mock |
| 6. 결과 반환 | 보상 토큰 개수 및 트랜잭션 해시 | ✅ 구현됨 | 완전 구현 |

**결론**: X 게시물 평가 및 보상 기능은 **백엔드 로직이 완전히 구현됨**. 다만:
- X API는 현재 Mock 모드 (실제 API 코드는 준비됨)
- 스마트 컨트랙트는 Mock 구현 (실제 Story Protocol 연동 필요)

---

## 📁 전체 파일 구조 및 역할

```
app/
├── main.py                          # FastAPI 앱 진입점, 라우터 등록, DB 초기화
├── db.py                            # SQLite 데이터베이스 (구매 내역 저장)
│
├── api/
│   ├── coins.py                     # 밈코인 구매 API (GET /coins, POST /coins/purchase, GET /coins/history)
│   ├── evaluation.py                # 게시물 평가 및 보상 API (POST /evaluation/analyze/{username})
│   └── advertisement.py             # 광고 추천 API (부가 기능)
│
└── services/
    ├── coin_service.py              # DexScreener API 연동 (실시간 코인 가격)
    ├── social_service.py            # X API 연동 (사용자 데이터, 트윗 수집)
    ├── ai_service.py                # Gemini AI 연동 (콘텐츠 품질 평가)
    ├── contract_service.py          # 스마트 컨트랙트 연동 (Mock)
    ├── twitter_client.py            # X API 클라이언트 (tweepy 래퍼)
    └── advertisement_service.py     # 광고 서비스 (부가 기능)
```

---

## 🔧 기술 스택

- **Backend Framework**: FastAPI
- **Database**: SQLite3
- **External APIs**:
  - DexScreener API (실시간 코인 가격)
  - X (Twitter) API v2 (사용자 데이터, 트윗)
  - Google Gemini API (AI 품질 평가)
- **Blockchain**: Story Protocol Smart Contract (Mock 구현)

---

## ⚠️ 현재 제한사항 및 개선 필요 사항

### 1. X API Mock 모드
- **현재**: Mock 데이터 반환 (데모용)
- **이유**: X API 무료 플랜 제한 (429 에러)
- **해결**: 실제 API 코드는 완전히 구현되어 있음 (주석 해제 가능)

### 2. 스마트 컨트랙트 Mock 구현
- **현재**: 가짜 트랜잭션 해시 생성
- **필요**: Story Protocol Smart Contract 실제 연동
- **위치**: `app/services/contract_service.py`

### 3. 광고 선택 기능 DB 저장 미구현
- **현재**: 메모리에만 저장 (프로그램 재시작 시 소실)
- **필요**: SQLite에 광고 선택 정보 저장
- **위치**: `app/api/advertisement.py:125-126` (TODO 주석)

---

## ✅ 구현 완료 요약

### 밈코인 구매 기능
- ✅ 코인 목록 조회 (실시간 가격)
- ✅ 구매 트랜잭션 저장 (DB)
- ✅ 구매 내역 조회 (DB)

### X 게시물 평가 및 보상 기능
- ✅ 데이터 수집 (X API - Mock 모드)
- ✅ 광고 검증 (키워드, 배너)
- ✅ 정량 데이터 확인 (팔로워, 참여율 등)
- ✅ AI 품질 평가 (Gemini API)
- ✅ 점수 산정 및 컨트랙트 전송 (Mock)
- ✅ 결과 반환

---

## 🎯 결론

**백엔드 개발자로서 구현해야 할 핵심 기능은 모두 구현되어 있습니다.**

1. **밈코인 구매**: 완전 구현됨 ✅
2. **X 게시물 평가 및 보상**: 로직 완전 구현됨 ✅ (외부 API는 Mock/준비됨)

**남은 작업**:
- Story Protocol Smart Contract 실제 연동 (현재 Mock)
- X API 실제 사용 (현재 Mock, 코드는 준비됨)
- 광고 선택 정보 DB 저장 (선택사항)

