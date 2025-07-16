import os
import openai
from openai import OpenAI

def translate_to_korean_summary_ai(title, content):
    """OpenAI API를 사용한 한글 요약"""
    try:
        # API 키 확인
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found, using basic summary")
            return None
        
        client = OpenAI(api_key=api_key)
        
        # 내용 길이 제한 (토큰 절약)
        content_preview = content[:1000] if len(content) > 1000 else content
        
        prompt = f"""다음 싱가포르 뉴스를 한국어로 요약해주세요:

제목: {title}
내용: {content_preview}

요구사항:
1. 3-4문장으로 핵심 내용만 요약
2. 중요한 숫자나 날짜는 포함
3. 싱가포르 관련 용어는 한글과 영문 병기 (예: 싱가포르(Singapore))
4. 이모지 사용: 📰 (제목), 📊 (숫자), 🔍 (핵심포인트)
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 싱가포르 뉴스를 한국 독자를 위해 요약하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3  # 일관성 있는 요약을 위해 낮은 온도
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI summary error: {e}")
        return None

def get_summary_with_fallback(title, content):
    """AI 요약 시도, 실패 시 기본 요약 사용"""
    # 먼저 AI 요약 시도
    ai_summary = translate_to_korean_summary_ai(title, content)
    
    if ai_summary:
        return ai_summary
    
    # AI 요약 실패 시 기존 방식 사용
    from scraper import translate_to_korean_summary
    return translate_to_korean_summary(title, content)