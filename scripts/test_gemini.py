import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경변수(.env)에서 키를 꺼내옵니다.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ 오류: .env 파일에 GEMINI_API_KEY가 없습니다!")
    exit()

# 2. Gemini 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-pro") 

# 3. 테스트 질문 던지기
print("🤖 Gemini에게 질문하는 중...")
try:
    response = model.generate_content("야야 소개해봐라 라라 라라라라라")
    print("\n✅ 응답 성공!")
    print("-" * 30)
    print(response.text)
    print("-" * 30)
except Exception as e:
    print(f"❌ 에러 발생: {e}")