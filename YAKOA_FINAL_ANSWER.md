# Yakoa API - 최종 답변: X 게시물 IP DB 확인 가능 여부

## 🎯 질문
**"X에서 게시물을 가져왔을 때 그 게시물이 IP DB에 있는지 확인을 못한다는 말이야?"**

---

## ❌ 답변: 네, 확인할 수 없습니다

### 이유

Yakoa API는 **"역방향 콘텐츠 검색"** 기능을 제공하지 않습니다.

---

## 🔍 기술적 분석

### 1. Yakoa API의 실제 동작 방식

#### Register Token 엔드포인트 분석 (제공된 문서 기준)

```http
POST /{network}/token
{
  "id": "contract_address:token_id",  // 필수: 블록체인 식별자
  "registration_tx": {...},            // 필수: 트랜잭션 정보
  "creator_id": "...",                  // 필수: 크리에이터 ID
  "metadata": {...},                    // 필수: 메타데이터
  "media": [                            // 필수: 미디어 파일들
    {
      "media_id": "...",
      "url": "https://..."
    }
  ]
}
```

**동작 순서:**
1. 토큰 등록 (contract_address:token_id 필요)
2. 등록 후 자동으로 침해 검사 시작
3. 검사 결과는 GET 엔드포인트로 조회

### 2. Yakoa가 확인하는 것 vs 우리가 원하는 것

#### Yakoa가 확인하는 것 (Register Token 후)
```
"이 토큰이 다른 IP를 침해하는가?"
→ 다른 사람의 IP를 무단 사용했는지 확인
```

#### 우리가 원하는 것 (Register Token 전)
```
"이 콘텐츠가 이미 Yakoa DB에 등록되어 있는가?"
→ 중복 등록 방지 (이미 누군가가 이 콘텐츠를 IP로 등록했는지)
```

**→ 완전히 다른 질문입니다!**

---

## 🚨 핵심 문제점

### 문제 1: 역방향 검색 불가능

**시나리오:**
```
1. X에서 게시물 가져옴 (텍스트 + 이미지 URL)
2. "이 게시물이 Yakoa DB에 이미 있는가?" 확인하고 싶음
3. 하지만 Yakoa API는 이런 검색을 지원하지 않음
```

**Yakoa API가 제공하는 것:**
- ✅ `POST /token` - 토큰 등록 (contract_address 필요)
- ✅ `GET /token/{id}` - 특정 토큰의 침해 상태 조회 (contract_address 필요)
- ❌ `POST /search` - 콘텐츠로 검색 (존재하지 않음)
- ❌ `POST /check-content` - Raw content로 중복 확인 (존재하지 않음)

### 문제 2: 필수 파라미터 부재

**우리가 가진 것 (Step 4):**
- X 게시물 텍스트
- 이미지 URL
- 사용자명
- ❌ contract_address 없음
- ❌ token_id 없음

**Yakoa가 요구하는 것:**
- ✅ contract_address (필수)
- ✅ token_id (필수)
- ✅ media URLs (필수, 하지만 토큰 등록의 일부)

**→ contract_address와 token_id 없이는 API 호출 자체가 불가능**

---

## 📊 구체적인 예시

### 시나리오: X 게시물 중복 확인

```
Step 1: X에서 게시물 가져옴
  - 텍스트: "귀여운 강아지 사진입니다 🐶"
  - 이미지: https://pbs.twimg.com/media/abc123.jpg
  - 사용자: @pet_lover

Step 2: Yakoa DB 확인 시도
  ❌ 불가능: "이 이미지가 Yakoa DB에 있는가?"를 확인할 방법 없음
  
  가능한 것:
  ✅ Register Token (하지만 contract_address 필요)
  ✅ Get Token (하지만 contract_address 필요)
```

### 만약 Register Token을 호출한다면?

```python
# 시도해볼 수 있는 방법 (하지만 작동하지 않음)
response = await yakoa.register_token(
    id="0x0000:0",  # 더미 값
    registration_tx={...},
    creator_id="...",
    metadata={...},
    media=[{
        "media_id": "tweet_image",
        "url": "https://pbs.twimg.com/media/abc123.jpg"
    }]
)
```

**문제점:**
1. 더미 contract_address 사용 시 API가 거부할 수 있음
2. 등록은 되지만, 우리가 원하는 "중복 확인"이 아님
3. 등록 후 침해 검사는 "다른 IP 침해 여부"를 확인하는 것
4. "이 콘텐츠가 이미 등록되어 있는가?"는 확인하지 않음

---

## 🔬 Yakoa의 실제 검사 범위

### Yakoa가 검사하는 것 (문서 기준)

1. **In-Network Infringements**
   - 네트워크 내에 이미 등록된 토큰과의 중복
   - 하지만 이는 "등록된 토큰"과 비교하는 것

2. **External Infringements**
   - Brand IP (외부 IP 소유자)와의 침해
   - 잘 알려진 공개 IP와의 비교

### 우리가 확인하고 싶은 것

**"이 X 게시물의 콘텐츠가 이미 Yakoa에 등록된 IP인가?"**

**→ Yakoa는 이런 역방향 검색을 지원하지 않습니다.**

---

## ✅ 결론

### 질문: "X에서 게시물을 가져왔을 때 그 게시물이 IP DB에 있는지 확인을 못한다는 말이야?"

**답변: 네, 맞습니다. 확인할 수 없습니다.**

### 이유 요약:

1. **역방향 검색 기능 없음**
   - Yakoa API는 콘텐츠(이미지/텍스트)로 검색하는 엔드포인트가 없음
   - 오직 토큰 ID(contract_address:token_id)로만 조회 가능

2. **필수 파라미터 부재**
   - contract_address와 token_id가 필수
   - 민팅 전에는 이 값들이 존재하지 않음

3. **API 설계 철학**
   - Yakoa는 "토큰 등록 후 침해 검사"를 위한 시스템
   - "등록 전 중복 확인"을 위한 시스템이 아님

---

## 💡 대안

### Option 1: 자체 해시 기반 중복 검사 (권장)
```python
# 우리가 처리한 콘텐츠의 해시를 DB에 저장
def check_if_content_already_processed(image_url, text):
    content_hash = hash(image_url + text)
    # 우리 DB에서 확인
    return exists_in_our_db(content_hash)
```

### Option 2: 다른 서비스 활용
- **Google Vision API**: 이미지 유사도 검색
- **TinEye API**: 역방향 이미지 검색
- **자체 ML 모델**: 이미지 임베딩 기반 유사도 검사

### Option 3: Yakoa를 민팅 후에만 사용
- Step 7 (민팅 후)에서 Yakoa로 침해 검사
- 하지만 중복 방지 목적은 달성 불가

---

## 📝 최종 답변

**"X에서 게시물을 가져왔을 때 그 게시물이 IP DB에 있는지 확인을 못한다는 말이야?"**

**→ 네, Yakoa API로는 확인할 수 없습니다.**

**이유:**
- Yakoa는 역방향 콘텐츠 검색을 지원하지 않음
- contract_address:token_id 없이는 API 호출 불가
- 설계 목적이 "등록 전 중복 확인"이 아님

**권장사항:**
- 자체 해시 기반 중복 검사 구현
- 또는 다른 역방향 이미지 검색 서비스 활용

