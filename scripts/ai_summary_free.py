import os
import time

# Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[AI_SUMMARY] Gemini library not available")

def translate_to_korean_summary_gemini(title, content):
    """Google Gemini API를 사용한 무료 한글 요약"""
    if not GEMINI_AVAILABLE:
        print("[AI_SUMMARY] Gemini API not available")
        return None
    
    try:
        # Gemini API 키 확인
        api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        print(f"[AI_SUMMARY] Environment check - API key present: {bool(api_key)}")
        print(f"[AI_SUMMARY] Environment check - API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("[AI_SUMMARY] ERROR: Gemini API key not found in environment")
            print(f"[AI_SUMMARY] Available env vars: {list(os.environ.keys())[:10]}...")  # 첫 10개만
            return None
        
        print(f"[AI_SUMMARY] Attempting Gemini API summary for: {title[:50]}...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 프롬프트 최적화
        content_preview = content[:1000] if len(content) > 1000 else content
        
        prompt = f"""다음 싱가포르 뉴스를 한국어로 정확하고 간결하게 요약해주세요.

제목: {title}
내용: {content_preview}

요구사항:
1. 제목을 먼저 한국어로 번역
2. 핵심 내용을 2-3문장으로 요약
3. 중요한 수치, 날짜, 인물명은 정확히 포함
4. 자연스러운 한국어 표현 사용
5. 응답 형식: "제목: [한국어 제목]\\n내용: [요약 내용]"

한국어 요약:"""
        
        response = model.generate_content(prompt)
        
        if response.text:
            print(f"[AI_SUMMARY] Gemini summary successful")
            # "제목:" 또는 "📰"로 시작하지 않으면 기본 형식 추가
            summary = response.text.strip()
            if not summary.startswith("📰") and not summary.startswith("제목:"):
                summary = f"📰 {summary}"
            return summary
        else:
            print("[AI_SUMMARY] Gemini returned empty response")
            return None
            
    except Exception as e:
        print(f"[AI_SUMMARY] Gemini error: {type(e).__name__}: {str(e)}")
        return None

def translate_to_korean_summary_free(title, content):
    """무료 API를 사용한 한글 요약 (Gemini 전용)"""
    # Gemini 시도
    print(f"[AI_SUMMARY] Attempting Gemini translation for: {title[:50]}...")
    result = translate_to_korean_summary_gemini(title, content)
    if result:
        return {"summary": result, "extracted_by": "gemini"}
    
    # 실패 시 폴백
    print("[AI_SUMMARY] All translation methods failed, using fallback")
    return {"summary": f"📰 싱가포르 최신 뉴스\\n📢 {title[:50]}...", "extracted_by": "fallback"}

# 메인 함수
translate_to_korean_summary = translate_to_korean_summary_free