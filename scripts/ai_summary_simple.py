import os
import time

# Cohere API
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    print("[AI_SUMMARY] Cohere library not available")

# Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[AI_SUMMARY] Gemini library not available")

def translate_to_korean_summary_cohere(title, content):
    """Cohere API를 사용한 한글 요약"""
    if not COHERE_AVAILABLE:
        print("[AI_SUMMARY] Cohere not available")
        return None
    
    try:
        # API 키 확인
        api_key = os.environ.get('COHERE_API_KEY')
        if not api_key:
            print("[AI_SUMMARY] COHERE_API_KEY not found in environment")
            return None
        
        print("[AI_SUMMARY] Cohere API key found, initializing client...")
        co = cohere.Client(api_key)
        
        # 콘텐츠 길이 제한 (토큰 절약)
        content_preview = content[:600] if len(content) > 600 else content
        
        # 중국어 감지 (간단한 방법)
        is_chinese = any(ord(char) >= 0x4e00 and ord(char) <= 0x9fff for char in (title + content_preview)[:100])
        
        if is_chinese:
            prompt = f"""다음 중국어 싱가포르 뉴스를 한국어로 정확하고 간결하게 요약해주세요.
이것은 중국어로 된 뉴스입니다. 중국어를 정확히 이해하고 한국어로 번역해주세요.

제목: {title}
내용: {content_preview}

요구사항:
1. 중국어 제목을 한국어로 정확히 번역
2. 중국어 내용의 핵심을 한국어로 2-3문장 요약
3. 중요한 수치, 날짜, 인물명은 정확히 포함
4. 자연스러운 한국어 표현 사용
5. 응답 형식: "제목: [한국어 제목]\\n내용: [요약 내용]"

한국어 요약:"""
        else:
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
        
        print("[AI_SUMMARY] Calling Cohere API...")
        start_time = time.time()
        
        response = co.chat(
            model="command-r",
            message=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        api_time = time.time() - start_time
        print(f"[AI_SUMMARY] Cohere API response time: {api_time:.2f}s")
        
        if response and response.text:
            summary_text = response.text.strip()
            print(f"[AI_SUMMARY] Cohere SUCCESS: Got {len(summary_text)} chars")
            return f"📰 {summary_text}"
        else:
            print("[AI_SUMMARY] ERROR: Cohere API returned empty response")
            return None
            
    except Exception as e:
        print(f"[AI_SUMMARY] Cohere ERROR: {type(e).__name__}: {str(e)}")
        return None

def translate_to_korean_summary_gemini(title, content):
    """Google Gemini API를 사용한 무료 한글 요약"""
    if not GEMINI_AVAILABLE:
        print("[AI_SUMMARY] Gemini API not available")
        return None
    
    try:
        # Gemini API 키 확인
        api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            print("[AI_SUMMARY] GOOGLE_GEMINI_API_KEY not found in environment")
            return None
        
        print("[AI_SUMMARY] Configuring Gemini API...")
        genai.configure(api_key=api_key)
        
        # 콘텐츠 길이 제한
        content_preview = content[:600] if len(content) > 600 else content
        
        # 중국어 감지 (간단한 방법)
        is_chinese = any(ord(char) >= 0x4e00 and ord(char) <= 0x9fff for char in (title + content_preview)[:100])
        
        if is_chinese:
            prompt = f"""다음 중국어 싱가포르 뉴스를 한국어로 정확하고 간결하게 요약해주세요.
이것은 중국어로 된 뉴스입니다. 중국어를 정확히 이해하고 한국어로 번역해주세요.

제목: {title}
내용: {content_preview}

요구사항:
1. 중국어 제목을 한국어로 정확히 번역
2. 중국어 내용의 핵심을 한국어로 2-3문장 요약
3. 중요한 수치, 날짜, 인물명은 정확히 포함
4. 자연스러운 한국어 표현 사용
5. 응답 형식: "제목: [한국어 제목]\\n내용: [요약 내용]"

한국어 요약:"""
        else:
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
        
        print("[AI_SUMMARY] Calling Gemini API...")
        start_time = time.time()
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 300,
            }
        )
        
        api_time = time.time() - start_time
        print(f"[AI_SUMMARY] Gemini API response time: {api_time:.2f}s")
        
        if response and response.text:
            summary_text = response.text.strip()
            print(f"[AI_SUMMARY] Gemini SUCCESS: Got {len(summary_text)} chars")
            return f"📰 {summary_text}"
        else:
            print("[AI_SUMMARY] ERROR: Gemini API returned empty response")
            return None
            
    except Exception as e:
        print(f"[AI_SUMMARY] Gemini ERROR: {type(e).__name__}: {str(e)}")
        return None

def translate_to_korean_summary_fallback(title, content):
    """간단한 키워드 기반 폴백 요약"""
    keyword_mapping = {
        'singapore': '싱가포르', 'economy': '경제', 'government': '정부',
        'education': '교육', 'health': '보건', 'transport': '교통',
        'technology': '기술', 'business': '비즈니스', 'covid': '코로나',
        'minister': '장관', 'policy': '정책', 'development': '개발',
        'housing': '주택', 'hdb': 'HDB', 'growth': '성장',
        'investment': '투자', 'finance': '금융', 'market': '시장'
    }
    
    # 키워드 찾기
    keywords = []
    lower_content = (title + " " + content).lower()
    for eng, kor in keyword_mapping.items():
        if eng in lower_content:
            keywords.append(kor)
    
    if keywords:
        keyword_str = ', '.join(keywords[:3])
        return f"📰 {keyword_str} 관련 뉴스\\n📢 {title[:60]}..."
    else:
        return f"📰 싱가포르 최신 뉴스\\n📢 {title[:60]}..."