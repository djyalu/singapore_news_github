import os
import requests
import json
from googletrans import Translator
import google.generativeai as genai

def translate_to_korean_summary_gemini(title, content):
    """Google Gemini API를 사용한 무료 한글 요약"""
    try:
        # Gemini API 키 확인
        api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 내용 길이 제한
        content_preview = content[:1000] if len(content) > 1000 else content
        
        prompt = f"""다음 싱가포르 뉴스를 한국어로 요약해주세요:

제목: {title}
내용: {content_preview}

3-4문장으로 핵심 내용만 요약하고, 중요한 숫자나 날짜를 포함해주세요."""
        
        response = model.generate_content(prompt)
        return f"📰 {response.text}"
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def translate_to_korean_summary_googletrans(title, content):
    """googletrans 라이브러리를 사용한 무료 번역"""
    try:
        translator = Translator()
        
        # 제목 번역
        translated_title = translator.translate(title, dest='ko').text
        
        # 내용 요약 (첫 200자만)
        content_preview = content[:200] if len(content) > 200 else content
        translated_content = translator.translate(content_preview, dest='ko').text
        
        return f"📰 {translated_title}\n📝 {translated_content}..."
        
    except Exception as e:
        print(f"Google Translate error: {e}")
        return None

def enhanced_keyword_summary(title, content):
    """향상된 키워드 기반 요약 (API 없이)"""
    # 확장된 키워드 매핑
    keyword_mapping = {
        # 경제/금융
        'economy': '경제', 'gdp': 'GDP', 'growth': '성장', 'inflation': '인플레이션',
        'recession': '경기침체', 'recovery': '회복', 'investment': '투자', 'trade': '무역',
        'export': '수출', 'import': '수입', 'deficit': '적자', 'surplus': '흑자',
        
        # 정부/정치
        'government': '정부', 'minister': '장관', 'prime minister': '총리',
        'lee hsien loong': '리셴룽', 'parliament': '의회', 'election': '선거',
        'policy': '정책', 'law': '법률', 'regulation': '규제',
        
        # 부동산/건설
        'property': '부동산', 'hdb': 'HDB(공공주택)', 'condo': '콘도',
        'housing': '주택', 'rent': '임대료', 'price': '가격', 'construction': '건설',
        
        # 교통
        'transport': '교통', 'mrt': 'MRT(지하철)', 'bus': '버스', 'lta': '육상교통청',
        'coe': 'COE(차량소유권)', 'erp': 'ERP(전자도로요금)', 'traffic': '교통체증',
        
        # 기술/혁신
        'technology': '기술', 'digital': '디지털', 'innovation': '혁신',
        'startup': '스타트업', 'fintech': '핀테크', 'ai': 'AI', 'smart nation': '스마트네이션',
        
        # 교육
        'education': '교육', 'school': '학교', 'university': '대학', 'nus': '싱가포르국립대',
        'ntu': '난양공대', 'student': '학생', 'exam': '시험', 'psle': 'PSLE(초등졸업시험)',
        
        # 의료/건강
        'health': '건강', 'hospital': '병원', 'covid': '코로나', 'vaccine': '백신',
        'healthcare': '의료', 'doctor': '의사', 'patient': '환자', 'moh': '보건부',
        
        # 환경
        'climate': '기후', 'environment': '환경', 'sustainability': '지속가능성',
        'green': '친환경', 'carbon': '탄소', 'energy': '에너지', 'solar': '태양광',
        
        # 관광/엔터테인먼트
        'tourism': '관광', 'tourist': '관광객', 'hotel': '호텔', 'singapore airlines': '싱가포르항공',
        'changi airport': '창이공항', 'sentosa': '센토사', 'marina bay': '마리나베이',
        
        # 금융기관
        'mas': '통화청(MAS)', 'dbs': 'DBS은행', 'ocbc': 'OCBC은행', 'uob': 'UOB은행',
        'temasek': '테마섹', 'gic': 'GIC', 'cpf': 'CPF(중앙연금)',
        
        # 기업
        'singtel': '싱텔', 'starhub': '스타허브', 'grab': '그랩', 'sea': 'SEA그룹',
        'shopee': '쇼피', 'capitaland': '캐피탈랜드', 'keppel': '케펠',
        
        # 지역
        'singapore': '싱가포르', 'malaysia': '말레이시아', 'indonesia': '인도네시아',
        'thailand': '태국', 'asean': '아세안', 'china': '중국', 'india': '인도'
    }
    
    # 중요 동사 매핑
    action_mapping = {
        'increase': '증가', 'decrease': '감소', 'rise': '상승', 'fall': '하락',
        'launch': '출시', 'announce': '발표', 'plan': '계획', 'develop': '개발',
        'invest': '투자', 'build': '건설', 'open': '개장', 'close': '폐쇄'
    }
    
    import re
    
    # 숫자와 퍼센트 추출
    numbers = re.findall(r'\$?[\d,]+\.?\d*%?|\d+\s*(?:million|billion|trillion)', content[:500])
    
    # 날짜 추출
    dates = re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:, \d{4})?|\d{1,2}/\d{1,2}/\d{2,4}', content[:500])
    
    # 키워드 찾기
    found_keywords = []
    text_lower = (title + ' ' + content[:500]).lower()
    
    for eng, kor in sorted(keyword_mapping.items(), key=lambda x: len(x[0]), reverse=True):
        if eng.lower() in text_lower:
            found_keywords.append(f"{kor}({eng.upper() if len(eng) <= 4 else eng.title()})")
            text_lower = text_lower.replace(eng.lower(), '')  # 중복 방지
    
    # 동작 찾기
    found_actions = []
    for eng, kor in action_mapping.items():
        if eng in text_lower:
            found_actions.append(kor)
    
    # 요약 생성
    summary = f"📰 {title}\n"
    
    if found_keywords:
        summary += f"🔍 주요 키워드: {', '.join(found_keywords[:5])}\n"
    
    if found_actions:
        summary += f"📌 주요 동향: {', '.join(found_actions[:3])}\n"
    
    if numbers:
        summary += f"📊 주요 수치: {', '.join(numbers[:3])}\n"
    
    if dates:
        summary += f"📅 날짜: {', '.join(dates[:2])}\n"
    
    # 내용 미리보기
    content_preview = content[:150].strip()
    if len(content) > 150:
        content_preview += "..."
    summary += f"📝 {content_preview}"
    
    return summary

def get_free_summary(title, content):
    """무료 요약 방법들을 순차적으로 시도"""
    
    # 1. Gemini API 시도 (완전 무료)
    if os.environ.get('GOOGLE_GEMINI_API_KEY'):
        summary = translate_to_korean_summary_gemini(title, content)
        if summary:
            return summary
    
    # 2. googletrans 시도 (무료지만 제한 있음)
    summary = translate_to_korean_summary_googletrans(title, content)
    if summary:
        return summary
    
    # 3. 향상된 키워드 기반 요약 (항상 작동)
    return enhanced_keyword_summary(title, content)