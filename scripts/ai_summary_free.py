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
            print("Gemini API key not found")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 내용 길이 제한 및 정제
        content = content.strip()
        if not content:
            content = "내용 없음"
        content_preview = content[:800] if len(content) > 800 else content
        
        prompt = f"""다음 싱가포르 뉴스를 한국어로 정확하고 간결하게 요약해주세요.

제목: {title}
내용: {content_preview}

요구사항:
1. 제목을 먼저 한국어로 번역
2. 핵심 내용을 2-3문장으로 요약
3. 중요한 수치, 날짜, 인물명은 정확히 포함
4. 자연스러운 한국어 표현 사용
5. 응답 형식: "제목: [한국어 제목]\n내용: [요약 내용]"
6. 이모지나 특수 기호는 사용하지 말 것

예시:
제목: 싱가포르 정부, 새로운 주택 정책 발표
내용: 싱가포르 정부가 주택 가격 상승을 억제하기 위한 새로운 정책을 발표했습니다. 이 정책은 내년부터 시행될 예정입니다."""
        
        response = model.generate_content(prompt)
        if response and response.text:
            # 응답 텍스트 정제
            summary_text = response.text.strip()
            # 불필요한 마크다운 제거
            summary_text = summary_text.replace('**', '').replace('*', '').replace('#', '')
            
            # 응답 형식 확인 및 정제
            if '제목:' in summary_text and '내용:' in summary_text:
                return f"📰 {summary_text}"
            else:
                # 형식이 맞지 않으면 기본 형식으로 변환
                lines = summary_text.split('\n')
                clean_summary = ' '.join([line.strip() for line in lines if line.strip()])
                return f"📰 제목: {title}\n📝 내용: {clean_summary}"
        else:
            print("Gemini API returned empty response")
            return None
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return None

def translate_to_korean_summary_googletrans(title, content):
    """googletrans 라이브러리를 사용한 무료 번역"""
    try:
        translator = Translator()
        
        # 제목 번역
        translated_title = translator.translate(title, dest='ko').text
        
        # 내용에서 의미있는 문장만 추출
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20 and not is_menu_sentence(s.strip())]
        if sentences:
            # 첫 2문장만 번역
            content_to_translate = '. '.join(sentences[:2]) + '.'
            translated_content = translator.translate(content_to_translate, dest='ko').text
        else:
            translated_content = "상세 내용을 확인할 수 없습니다."
        
        return f"📰 제목: {translated_title}\n📝 내용: {translated_content}"
        
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
    
    # 제목 번역 시도
    korean_title = translate_title_intelligently(title, keyword_mapping, action_mapping)
    
    # 제목에서 찾은 키워드로 분류
    title_keywords = []
    title_lower = title.lower()
    for eng, kor in sorted(keyword_mapping.items(), key=lambda x: len(x[0]), reverse=True):
        if eng.lower() in title_lower:
            title_keywords.append(kor)
            title_lower = title_lower.replace(eng.lower(), '', 1)
    
    # 제목 생성
    if korean_title and korean_title != title:
        summary = f"📰 제목: {korean_title}\n"
    elif title_keywords:
        summary = f"📰 제목: {' '.join(title_keywords[:2])} 관련 뉴스\n"
    else:
        # 키워드를 못찾으면 일반적인 표현 사용
        if any(word in title.lower() for word in ['announce', 'launch', 'plan', 'report']):
            summary = f"📰 제목: 싱가포르 주요 발표/계획 뉴스\n"
        elif any(word in title.lower() for word in ['rise', 'increase', 'grow', 'up']):
            summary = f"📰 제목: 싱가포르 상승/성장 관련 뉴스\n"
        elif any(word in title.lower() for word in ['fall', 'decrease', 'drop', 'down']):
            summary = f"📰 제목: 싱가포르 하락/감소 관련 뉴스\n"
        else:
            summary = f"📰 제목: 싱가포르 최신 뉴스\n"
    
    if found_keywords:
        summary += f"🔍 주요 키워드: {', '.join(found_keywords[:5])}\n"
    
    if found_actions:
        summary += f"📌 주요 동향: {', '.join(found_actions[:3])}\n"
    
    if numbers:
        summary += f"📊 주요 수치: {', '.join(numbers[:3])}\n"
    
    if dates:
        summary += f"📅 날짜: {', '.join(dates[:2])}\n"
    
    # 내용을 한글로 요약
    content_summary = "📝 "
    
    # 내용에서 주요 정보 추출
    content_lower = content[:300].lower()
    
    # 주요 동작과 대상 조합
    main_points = []
    
    # 숫자와 관련 키워드 조합
    if numbers and found_keywords:
        main_points.append(f"{found_keywords[0]}이(가) {numbers[0]} 기록")
    
    # 동작과 키워드 조합
    if found_actions and found_keywords:
        main_points.append(f"{found_keywords[0] if len(found_keywords) > 0 else '싱가포르'}에서 {found_actions[0]}")
    
    # 날짜 정보 포함
    if dates:
        main_points.append(f"{dates[0]}부터 시행")
    
    if main_points:
        content_summary += " / ".join(main_points[:2])
    else:
        # 기본 요약
        if found_keywords:
            content_summary += f"{', '.join(found_keywords[:2])} 관련 소식"
        else:
            content_summary += "싱가포르 최신 동향"
    
    summary += content_summary
    
    return summary

def translate_title_intelligently(title, keyword_mapping, action_mapping):
    """지능적인 헤드라인 번역 함수"""
    title_lower = title.lower().strip()
    
    # 특수 케이스: 질문형 헤드라인 처리
    if title_lower.startswith('why') or title_lower.startswith('what') or title_lower.startswith('how'):
        return translate_question_headline(title, keyword_mapping, action_mapping)
    
    # 일반 헤드라인 번역
    translated_parts = []
    words = title_lower.split()
    
    i = 0
    while i < len(words):
        word = words[i].strip('.,!?:;"\'')
        
        # 2단어 조합 먼저 확인
        if i < len(words) - 1:
            two_words = f"{word} {words[i+1].strip('.,!?:;\"\'')}"  
            if two_words in keyword_mapping:
                translated_parts.append(keyword_mapping[two_words])
                i += 2
                continue
        
        # 단일 단어 확인
        if word in keyword_mapping:
            translated_parts.append(keyword_mapping[word])
        elif word in action_mapping:
            translated_parts.append(action_mapping[word])
        elif word.isdigit():
            translated_parts.append(word)
        elif word.startswith('$') or '%' in word:
            translated_parts.append(word)
        elif len(word) <= 3 and word.isupper():
            translated_parts.append(word)
        
        i += 1
    
    if len(translated_parts) >= 2:
        return ' '.join(translated_parts)
    else:
        return None

def translate_question_headline(title, keyword_mapping, action_mapping):
    """질문형 헤드라인 번역"""
    title_lower = title.lower()
    
    # 질문 단어 매핑
    question_mapping = {
        'why': '왜',
        'what': '무엇이',
        'how': '어떻게',
        'when': '언제',
        'where': '어디서',
        'who': '누가'
    }
    
    # 주요 키워드 찾기
    found_keywords = []
    for eng, kor in keyword_mapping.items():
        if eng in title_lower:
            found_keywords.append(kor)
    
    # 질문 단어 찾기
    question_word = None
    for eng, kor in question_mapping.items():
        if title_lower.startswith(eng):
            question_word = kor
            break
    
    if question_word and found_keywords:
        return f"{question_word} {found_keywords[0]}을/를"
    elif found_keywords:
        return f"{found_keywords[0]} 관련 질문"
    else:
        return "싱가포르 관련 질문"

def is_menu_sentence(sentence):
    """메뉴나 네비게이션 문장인지 확인"""
    menu_patterns = [
        'sign in', 'log in', 'my feed', 'edition menu', 'search menu',
        'singapore indonesia asia', 'lifestyle luxury', 'top stories',
        'latest news', 'live tv', 'podcasts', 'radio schedule',
        'news id', 'type landing_page', 'find out what',
        'get the best', 'sent to your inbox', 'newsletters',
        'cna explains', 'sustainability', 'documentaries & shows'
    ]
    
    sentence_lower = sentence.lower()
    return any(pattern in sentence_lower for pattern in menu_patterns)

def translate_title_simple(title, keyword_mapping, action_mapping):
    """백업용 간단 번역 함수"""
    return translate_title_intelligently(title, keyword_mapping, action_mapping)

def get_free_summary(title, content):
    """무료 요약 방법들을 순차적으로 시도"""
    
    # 1. Gemini API 시도 (완전 무료)
    api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
    if api_key:
        print(f"Gemini API key found: {api_key[:10]}...")
        summary = translate_to_korean_summary_gemini(title, content)
        if summary:
            print("Gemini API summary successful")
            return summary
        else:
            print("Gemini API failed, trying next method...")
    else:
        print("No Gemini API key found in environment")
    
    # 2. googletrans 시도 (무료지만 제한 있음)
    print("Trying googletrans...")
    summary = translate_to_korean_summary_googletrans(title, content)
    if summary:
        print("Googletrans summary successful")
        return summary
    
    # 3. 향상된 키워드 기반 요약 (항상 작동)
    print("Using keyword-based summary as fallback")
    return enhanced_keyword_summary(title, content)