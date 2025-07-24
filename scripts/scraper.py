import json
import os
import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from urllib.parse import urljoin, urlparse
from ai_scraper import get_ai_scraper
from text_processing import TextProcessor
from deduplication import ArticleDeduplicator

# 디버그 모드 설정 (환경 변수로 제어) - BrokenPipeError 방지를 위해 기본값 False
DEBUG_MODE = os.environ.get('DEBUG_SCRAPER', 'false').lower() == 'true'
if DEBUG_MODE:
    print("[WARNING] DEBUG mode is enabled. This may cause BrokenPipeError in GitHub Actions.")

# KST 타임존 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간(KST) 반환"""
    return datetime.now(KST)

def get_kst_now_iso():
    """현재 한국 시간을 ISO 형식 문자열로 반환"""
    return get_kst_now().isoformat()

def extract_publish_date(soup, default_to_now=True):
    """
    HTML에서 기사 발행일 추출
    
    Returns:
        datetime: 발행일 (KST) 또는 None
    """
    # 메타 태그에서 발행일 찾기
    date_meta_names = [
        'article:published_time', 'article:published', 'publish_date',
        'publication_date', 'date', 'DC.date', 'sailthru.date',
        'parsely-pub-date', 'datePublished'
    ]
    
    for name in date_meta_names:
        meta = soup.find('meta', {'property': name}) or soup.find('meta', {'name': name})
        if meta and meta.get('content'):
            try:
                # ISO 형식 파싱 시도
                pub_date = datetime.fromisoformat(meta['content'].replace('Z', '+00:00'))
                # KST로 변환
                if pub_date.tzinfo is None:
                    pub_date = KST.localize(pub_date)
                else:
                    pub_date = pub_date.astimezone(KST)
                return pub_date
            except:
                pass
    
    # time 태그에서 찾기
    time_tag = soup.find('time', {'datetime': True})
    if time_tag:
        try:
            pub_date = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
            if pub_date.tzinfo is None:
                pub_date = KST.localize(pub_date)
            else:
                pub_date = pub_date.astimezone(KST)
            return pub_date
        except:
            pass
    
    # JSON-LD 구조화 데이터에서 찾기
    scripts = soup.find_all('script', {'type': 'application/ld+json'})
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if 'datePublished' in data:
                    pub_date = datetime.fromisoformat(data['datePublished'].replace('Z', '+00:00'))
                    if pub_date.tzinfo is None:
                        pub_date = KST.localize(pub_date)
                    else:
                        pub_date = pub_date.astimezone(KST)
                    return pub_date
        except:
            pass
    
    # 텍스트에서 날짜 패턴 찾기
    date_patterns = [
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # 2024-01-23 or 2024/01/23
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # 23-01-2024 or 23/01/2024
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',  # Jan 23, 2024
        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'  # 23 January 2024
    ]
    
    text = soup.get_text()[:2000]  # 처음 2000자만 검색
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                from dateutil import parser
                pub_date = parser.parse(match.group(0))
                pub_date = KST.localize(pub_date)
                # 미래 날짜는 무시
                if pub_date <= get_kst_now():
                    return pub_date
            except:
                pass
    
    return get_kst_now() if default_to_now else None

def load_settings():
    """
    서버에서 동적으로 설정을 불러오기
    
    Returns:
        dict: 애플리케이션 설정 딕셔너리
            - scrapTarget: 스크래핑 대상 (recent/important)
            - importantKeywords: 중요 키워드 목록
            - summaryOptions: 요약 옵션 설정
            - sendChannel: 전송 채널 (whatsapp)
            - whatsappChannel: WhatsApp 채널 ID
            - sendSchedule: 전송 스케줄 설정
            - blockedKeywords: 차단 키워드 목록
            - scrapingMethod: 스크래핑 방식 (traditional/ai/rss/hybrid)
            - monitoring: 모니터링 설정
    
    우선순위:
        1. Vercel API 서버에서 최신 설정 가져오기
        2. 로컬 settings.json 파일
        3. 하드코딩된 기본 설정
    """
    try:
        # 먼저 서버 API에서 최신 설정 시도
        api_url = "https://singapore-news-github.vercel.app/api/save-data?type=settings"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print("[SETTINGS] Loaded settings from server API")
                return result['data']
        
        print("[SETTINGS] Server API failed, using local file")
    except Exception as e:
        print(f"[SETTINGS] Server API error: {e}, using local file")
    
    # API 실패시 로컬 파일 사용
    try:
        with open('data/settings.json', 'r') as f:
            print("[SETTINGS] Loaded settings from local file")
            return json.load(f)
    except Exception as e:
        print(f"[SETTINGS] Local file error: {e}, using default settings")
        # 기본 설정 반환
        return {
            "scrapTarget": "recent",
            "importantKeywords": "",
            "summaryOptions": {"headline": True, "keywords": True, "content": True},
            "sendChannel": "whatsapp",
            "whatsappChannel": "",
            "sendSchedule": {"period": "daily", "time": "08:00", "weekdays": [], "date": "1"},
            "blockedKeywords": "",
            "scrapingMethod": "traditional",
            "scrapingMethodOptions": {
                "ai": {"provider": "gemini", "model": "gemini-1.5-flash", "fallbackToTraditional": True},
                "traditional": {"useEnhancedFiltering": True}
            },
            "monitoring": {"enabled": True}
        }

def load_sites():
    """
    서버에서 동적으로 사이트 설정을 불러오기
    
    Returns:
        list: 뉴스 사이트 설정 리스트
            각 사이트 딕셔너리 구조:
            - name: 사이트 이름
            - url: 사이트 URL
            - group: 카테고리 그룹 (News/Economy/Politics 등)
            - enabled: 활성화 여부
    
    우선순위:
        1. Vercel API 서버에서 최신 사이트 목록 가져오기
        2. 로컬 sites.json 파일
        3. 빈 리스트 반환 (오류 시)
    """
    try:
        # 먼저 서버 API에서 최신 사이트 설정 시도
        api_url = "https://singapore-news-github.vercel.app/api/save-data?type=sites"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                print("[SITES] Loaded sites from server API")
                return result['data']
        
        print("[SITES] Server API failed, using local file")
    except Exception as e:
        print(f"[SITES] Server API error: {e}, using local file")
    
    # API 실패시 로컬 파일 사용
    try:
        with open('data/sites.json', 'r') as f:
            print("[SITES] Loaded sites from local file")
            return json.load(f)
    except Exception as e:
        print(f"[SITES] Local file error: {e}, using empty sites list")
        return []

def is_recent_article(article_date):
    """
    기사가 최근 것인지 확인 (2일 이내)
    
    Args:
        article_date (datetime or str): 기사 발행일 (datetime 객체 또는 ISO 형식 문자열)
    
    Returns:
        bool: 2일 이내면 True, 아니면 False
              날짜가 없으면 True 반환 (보수적 접근)
    """
    if not article_date:
        return True
    
    # 문자열인 경우 datetime으로 변환
    if isinstance(article_date, str):
        try:
            # ISO 형식 문자열 파싱
            from datetime import datetime
            article_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # 파싱 실패 시 True 반환 (보수적 접근)
            return True
    
    # timezone-aware 날짜로 변환
    if article_date.tzinfo is None:
        import pytz
        kst = pytz.timezone('Asia/Seoul')
        article_date = kst.localize(article_date)
    
    return (get_kst_now() - article_date).days <= 2

def contains_keywords(text, keywords):
    """
    텍스트에 키워드가 포함되어 있는지 확인
    
    Args:
        text (str): 검색할 텍스트
        keywords (str or list): 키워드 리스트 또는 쉼표로 구분된 문자열
    
    Returns:
        bool: 키워드 중 하나라도 포함되어 있으면 True
    """
    if not text or not keywords:
        return False
    
    # 문자열인 경우 리스트로 변환
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]
    
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def is_blocked(text, blocked_keywords):
    """
    텍스트가 차단 키워드를 포함하는지 확인
    
    Args:
        text (str): 검사할 텍스트
        blocked_keywords (str or list): 차단 키워드 리스트 또는 쉼표로 구분된 문자열
    
    Returns:
        bool: 차단 키워드가 포함되어 있으면 True
    """
    if not text or not blocked_keywords:
        return False
    
    # 문자열인 경우 리스트로 변환
    if isinstance(blocked_keywords, str):
        blocked_keywords = [k.strip() for k in blocked_keywords.split(',') if k.strip()]
    
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in blocked_keywords)

def validate_article(article):
    """
    기사 데이터 구조 검증
    
    Args:
        article (dict): 검증할 기사 데이터
    
    Returns:
        bool: 유효한 기사면 True, 아니면 False
    """
    # 필수 필드 확인
    required_fields = ['title', 'url', 'site', 'group']
    
    # 모든 필수 필드가 있는지 확인
    if not all(field in article for field in required_fields):
        return False
    
    # 필드 값이 비어있지 않은지 확인
    for field in required_fields:
        value = article.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            return False
    
    # URL 형식 확인
    url = article.get('url', '')
    if not url.startswith(('http://', 'https://')):
        return False
    
    return True

def validate_scraped_data(data):
    """
    스크랩된 데이터 전체 구조 검증
    
    Args:
        data (dict): 검증할 스크랩 데이터
    
    Returns:
        bool: 유효한 데이터면 True, 아니면 False
    """
    # 필수 필드 확인
    required_fields = ['timestamp', 'articles', 'stats']
    return all(field in data for field in required_fields)

def sanitize_path(file_path, base_path):
    """
    경로 순회 공격 방지를 위한 경로 검증
    
    Args:
        file_path (str): 검증할 파일 경로
        base_path (str): 허용된 기본 경로
    
    Returns:
        str: 안전한 경로 또는 None
    """
    import os
    
    # 절대 경로로 변환
    abs_base = os.path.abspath(base_path)
    abs_file = os.path.abspath(os.path.join(abs_base, file_path))
    
    # 기본 경로 내에 있는지 확인
    if abs_file.startswith(abs_base):
        return abs_file
    else:
        return None

def clean_text(text):
    """
    텍스트 정제 - HTML 태그, 특수문자, 공백 제거
    
    Args:
        text (str): 원본 텍스트
    
    Returns:
        str: 정제된 텍스트
            - HTML 태그 제거
            - 연속된 공백을 단일 공백으로
            - 앞뒤 공백 제거
            - 기본값은 빈 문자열
    """
    # None 또는 빈 값 처리
    if not text:
        return ''
    
    # 문자열로 변환
    text = str(text)
    
    # 위험한 태그와 내용 제거 (script, style, iframe 등)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # 나머지 HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # HTML 엔티티 디코드
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    
    # 줄바꿈을 공백으로 변경
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # 다중 공백을 단일 공백으로
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return text.strip()

def is_meaningful_content(text):
    """의미있는 기사 내용인지 확인 - 더 관대하게"""
    if len(text) < 20:
        return False
    
    # 메뉴 텍스트 체크 - 더 엄격하게 (확실한 메뉴만)
    if is_menu_text(text) and len(text) < 100:
        return False
    
    # 기본 구조 체크
    sentences = text.split('.')
    if len(sentences) < 2:
        return False
    
    # 단어 수 체크
    words = text.split()
    if len(words) < 30:
        return False
    
    # 진엄한 기사 내용 패턴 - 더 넓은 범위
    article_indicators = [
        'said', 'announced', 'reported', 'according to', 'in a statement',
        'the government', 'the ministry', 'officials', 'spokesperson',
        'singapore', 'minister', 'prime minister', 'parliament',
        'economic', 'policy', 'development', 'growth', 'investment',
        'will', 'would', 'can', 'could', 'should', 'may', 'might',
        'new', 'project', 'plan', 'programme', 'service', 'system',
        'million', 'billion', 'percent', 'year', 'month', 'week',
        'company', 'business', 'market', 'price', 'cost', 'budget',
        'people', 'public', 'residents', 'citizens', 'community'
    ]
    
    text_lower = text.lower()
    article_score = sum(1 for indicator in article_indicators if indicator in text_lower)
    
    # 문장 구조 체크 (마침표, 쉼표 등)
    punctuation_score = text.count('.') + text.count(',') + text.count(';')
    
    # 전체 길이 대비 의미있는 단어 비율
    meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
    
    if len(words) == 0:
        return False
    
    meaningful_ratio = len(meaningful_words) / len(words)
    
    # 점수 기반 판단 - 더 관대하게
    total_score = article_score + (punctuation_score * 0.3) + (meaningful_ratio * 5)
    
    return total_score > 2  # 점수 기준을 3에서 2로 낮춤

def post_process_article_content(article_data):
    """추출된 기사 내용 후처리 - 개선된 중복 제거"""
    if not article_data or not article_data.get('content'):
        return article_data
    
    content = article_data['content']
    
    # TextProcessor를 사용하여 깨끗한 문장 추출
    sentences = TextProcessor.extract_sentences(content, min_length=20)
    
    # 중복 제거 (정규화된 비교)
    unique_sentences = []
    seen_normalized = set()
    
    for sentence in sentences:
        # 메뉴 문장 필터링
        if is_menu_sentence(sentence):
            continue
            
        # 추가 정제
        cleaned_sentence = clean_menu_remnants(sentence)
        if not cleaned_sentence or len(cleaned_sentence) < 20:
            continue
            
        # 정규화하여 중복 체크
        normalized = cleaned_sentence.lower().strip()
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            unique_sentences.append(cleaned_sentence)
    
    # 안전하게 병합 및 자르기
    if unique_sentences:
        article_data['content'] = TextProcessor.merge_paragraphs(unique_sentences, max_length=1000)
    else:
        article_data['content'] = ''
    
    return article_data

def is_menu_sentence(sentence):
    """멤뉴 문장인지 더 엄격하게 판단"""
    sentence_lower = sentence.lower().strip()
    
    # 직접적인 메뉴 패턴
    direct_menu_patterns = [
        '내 피드 에디션 메뉴',
        'sign in account my feed',
        'edition menu edition',
        '싱가포르 인도네시아 아시아',
        'singapore indonesia asia',
        'cna 라이프 스타일 럭셔리',
        'cna lifestyle luxury',
        'top stories', 'latest news', 'live tv',
        'news id', 'type landing_page',
        'search menu search edition'
    ]
    
    # 직접 매칭
    if any(pattern in sentence_lower for pattern in direct_menu_patterns):
        return True
    
    # 패턴 기반 판단
    words = sentence_lower.split()
    
    # 진엄한 메뉴 단어 비율
    menu_words = [
        'feed', 'edition', 'menu', 'account', 'sign', 'search',
        'lifestyle', 'luxury', 'today', 'stories', 'news',
        'singapore', 'indonesia', 'asia', 'cna', 'cnar'
    ]
    
    if len(words) > 0:
        menu_word_ratio = sum(1 for word in words if word in menu_words) / len(words)
        if menu_word_ratio > 0.6:  # 60% 이상이 메뉴 단어
            return True
    
    # 진었단 나열 패턴 (a b c d e f...)
    if len(words) > 8 and len([w for w in words if len(w) < 4]) > 6:
        return True
    
    return False

def clean_menu_remnants(text):
    """남은 메뉴 잔여물 제거"""
    # 특정 메뉴 문구 제거
    menu_phrases_to_remove = [
        '내 피드 에디션 메뉴 에디션 계정',
        'Sign In Account My Feed Edition Menu',
        'Edition: Singapore Indonesia Asia',
        'CNAR 검색 메뉴 검색',
        'CNA Lifestyle Luxury TODAY',
        'News Id', 'Type landing_page'
    ]
    
    cleaned_text = text
    for phrase in menu_phrases_to_remove:
        cleaned_text = cleaned_text.replace(phrase, '')
        cleaned_text = cleaned_text.replace(phrase.lower(), '')
        cleaned_text = cleaned_text.replace(phrase.upper(), '')
    
    # 다중 공백 제거
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

def is_landing_page_content(content):
    """랜딩 페이지 또는 메뉴 페이지 콘텐츠인지 판단 - 더 관대하게"""
    if not content or len(content) < 20:
        return True
    
    content_lower = content.lower()
    
    # 확실한 랜딩 페이지 지표들만 체크
    definite_landing_indicators = [
        'sign in account my feed edition menu',
        'type landing_page',
        'news id 1822271 type landing_page',
        'top stories id 1821936 type landing_page',
        'latest news id 1822271 type landing_page'
    ]
    
    # 확실한 지표가 하나라도 있으면 랜딩 페이지
    if any(indicator in content_lower for indicator in definite_landing_indicators):
        return True
    
    # 메뉴 텍스트 패턴 확인 - 더 엄격하게
    menu_patterns = [
        r'id \d+ type landing_page',
        r'sign in account my feed edition menu',
        r'edition menu edition singapore indonesia asia'
    ]
    
    pattern_matches = sum(1 for pattern in menu_patterns if re.search(pattern, content_lower))
    
    # 패턴 매칭이 2개 이상이면 랜딩 페이지
    if pattern_matches >= 2:
        return True
    
    # 전체 단어 수 대비 메뉴 단어 비율 계산 - 더 관대하게
    words = content_lower.split()
    menu_words = [
        'sign', 'account', 'feed', 'edition', 'menu', 'search',
        'landing_page', 'landing', 'type'
    ]
    
    if len(words) > 0:
        menu_word_ratio = sum(1 for word in words if word in menu_words) / len(words)
        
        # 메뉴 단어 비율이 70% 이상이면 랜딩 페이지 (더 엄격하게)
        if menu_word_ratio > 0.7:
            return True
    
    # 실제 기사 내용의 지표 확인
    article_indicators = [
        'said', 'announced', 'reported', 'according to', 'minister', 'government',
        'policy', 'economic', 'business', 'investment', 'development', 'growth',
        'court', 'sentenced', 'charged', 'arrested', 'police', 'trial',
        'company', 'market', 'shares', 'profit', 'revenue', 'customers',
        'singapore', 'malaysian', 'indonesian', 'thai', 'vietnam'
    ]
    
    article_score = sum(1 for indicator in article_indicators if indicator in content_lower)
    
    # 기사 지표가 있으면 일단 기사로 판단
    if article_score > 0:
        return False
    
    # 기사 지표가 전혀 없고 메뉴 단어 비율이 50% 이상이면 랜딩 페이지
    if len(words) > 0:
        menu_word_ratio = sum(1 for word in words if word in menu_words) / len(words)
        if menu_word_ratio > 0.5:
            return True
    
    return False

def validate_final_article_content(article_data):
    """최종 기사 내용 유효성 검사 - 더 관대하게"""
    if not article_data or not article_data.get('title') or not article_data.get('content'):
        return False
    
    title = article_data['title'].strip()
    content = article_data['content'].strip()
    
    if DEBUG_MODE:
        print(f"[DEBUG] Final validation for: {title}")
    
    # 제목 검사 - 명백한 메뉴/네비게이션 제목들만
    invalid_titles = [
        'newsletters', 'breaking news', 'sign up', 'login', 'register',
        'share on whatsapp', 'yoursingapore story', 'featured',
        'menu', 'search', 'edition'
    ]
    
    if any(invalid in title.lower() for invalid in invalid_titles):
        if DEBUG_MODE:
            print(f"[DEBUG] Invalid title detected: {title}")
        return False
    
    # 내용 검사 - 실제 뉴스 기사의 특징 확인 (더 관대하게)
    news_indicators = [
        'said', 'announced', 'reported', 'according to', 'minister',
        'government', 'policy', 'singapore', 'parliament', 'court',
        'arrested', 'charged', 'sentenced', 'company', 'business',
        'economy', 'investment', 'market', 'development', 'residents',
        'citizens', 'public', 'authorities', 'officials', 'plan',
        'project', 'programme', 'service', 'system', 'will', 'would',
        'can', 'could', 'should', 'million', 'billion', 'percent',
        'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days'
    ]
    
    content_lower = content.lower()
    news_score = sum(1 for indicator in news_indicators if indicator in content_lower)
    
    # 뉴스 지표가 전혀 없으면 기사가 아님 (하지만 더 관대하게)
    if news_score == 0:
        # 기본적인 문서 구조가 있는지 확인
        sentences = content.split('.')
        if len(sentences) < 2 or len(content.split()) < 20:
            if DEBUG_MODE:
                print(f"[DEBUG] No news indicators and insufficient structure")
            return False
    
    # 메뉴 텍스트 확인 - 더 엄격하게 (확실한 메뉴만)
    if is_menu_text(content) and news_score == 0:
        if DEBUG_MODE:
            print(f"[DEBUG] Menu text detected in content")
        return False
    
    # 내용 길이 및 구조 확인 - 훨씬 더 관대하게
    sentences = content.split('.')
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]  # 10 -> 5로 완화
    
    if len(valid_sentences) < 1:  # 2 -> 1로 완화
        if DEBUG_MODE:
            print(f"[DEBUG] Insufficient valid sentences: {len(valid_sentences)}")
        return False
    
    # 단어 수 확인 - 훨씬 더 관대하게 (10단어 이상)
    words = content.split()
    if len(words) < 10:  # 20 -> 10으로 완화
        if DEBUG_MODE:
            print(f"[DEBUG] Content too short: {len(words)} words")
        return False
    
    if DEBUG_MODE:
        print(f"[DEBUG] Article validation passed - news_score: {news_score}, sentences: {len(valid_sentences)}, words: {len(words)}")
    return True

def extract_article_content_straits_times(url, soup):
    """The Straits Times 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # 제목 추출
    title_elem = soup.select_one('h1.headline, h1[data-testid="headline"], .article-headline h1, h1')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 전체 비필요 요소 먼저 제거
    remove_unwanted_elements(soup)
    
    # 본문 추출 - 더 정교한 선택자 사용
    content_elem = find_main_content_element(soup, [
        'div[data-testid="article-body"]',
        '.article-content',
        '.paywall-content', 
        '.story-content',
        'article',
        '.content-body'
    ])
    
    if content_elem:
        article['content'] = extract_pure_article_text(content_elem)
    
    # 날짜 추출
    date_elem = soup.select_one('time, .published-date, [data-testid="publish-date"]')
    if date_elem:
        try:
            if date_elem.get('datetime'):
                article['publish_date'] = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            else:
                article['publish_date'] = get_kst_now()
        except:
            article['publish_date'] = get_kst_now()
    
    return article

def extract_article_content_moe(url, soup):
    """Ministry of Education 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # 제목 추출
    title_elem = soup.select_one('h1, .page-title, .content-title')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 본문 추출 - MOE는 주로 div.content-area 사용
    content_elem = soup.select_one('.content-area, .page-content, main')
    if content_elem:
        # 네비게이션, 헤더, 푸터 제거
        for elem in content_elem.select('nav, header, footer, .breadcrumb, .sidebar'):
            elem.decompose()
        
        # 실제 콘텐츠 추출
        paragraphs = content_elem.find_all(['p', 'li'])
        content_parts = []
        for p in paragraphs:
            text = clean_text(p.get_text())
            if len(text) > 20:  # 짧은 텍스트 필터링
                content_parts.append(text)
        
        article['content'] = ' '.join(content_parts[:10])[:1000]
    
    # 날짜 추출
    date_text = soup.get_text()
    date_match = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', date_text)
    if date_match:
        try:
            date_str = f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}"
            article['publish_date'] = datetime.strptime(date_str, "%d %b %Y")
        except:
            pass
    
    return article

def extract_article_content_nac(url, soup):
    """National Arts Council 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # NAC는 주로 이벤트 정보
    title_elem = soup.select_one('h1, .event-title, .programme-title')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 이벤트 설명 추출
    content_elem = soup.select_one('.event-description, .programme-description, .content-main')
    if content_elem:
        article['content'] = clean_text(content_elem.get_text())[:1000]
    
    # 날짜는 이벤트 날짜로
    date_elem = soup.select_one('.event-date, .programme-date')
    if date_elem:
        article['publish_date'] = get_kst_now()  # 간단히 현재 날짜 사용
    
    return article

def extract_article_content_independent(url, soup):
    """The Independent Singapore 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # 제목 추출 - WordPress 기반
    title_elem = soup.select_one('h1.entry-title, h1.td-post-title, h1, .post-title h1')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 전체 비필요 요소 먼저 제거
    remove_unwanted_elements(soup)
    
    # 본문 추출 - WordPress 전용 선택자
    content_elem = find_main_content_element(soup, [
        '.td-post-content',            # TD Theme 콘텐츠
        '.entry-content',              # WordPress 기본
        '.post-content',               # 포스트 콘텐츠
        'div[itemprop="articleBody"]', # 시맨틱 마크업
        '.td-ss-main-content',         # TD 메인 콘텐츠
        '.content-inner',              # 내부 콘텐츠
        'article .content',            # article 내 콘텐츠
        '.article-content'             # 기사 콘텐츠
    ])
    
    if content_elem:
        article['content'] = extract_pure_article_text(content_elem)
    
    # 날짜 추출
    date_elem = soup.select_one('time, .td-post-date, .entry-date, .published')
    if date_elem:
        try:
            if date_elem.get('datetime'):
                article['publish_date'] = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            else:
                date_text = date_elem.get_text()
                # 간단한 날짜 파싱 시도
                article['publish_date'] = get_kst_now()
        except:
            article['publish_date'] = get_kst_now()
    
    return article

def extract_article_content_business_times(url, soup):
    """The Business Times 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # 제목 추출
    title_elem = soup.select_one('h1, .headline, .article-title')
    if title_elem:
        title_text = clean_text(title_elem.get_text())
        # 사이트 이름 제거
        if ' - ' in title_text:
            title_text = title_text.split(' - ')[0]
        article['title'] = title_text
    
    # 전체 비필요 요소 먼저 제거
    remove_unwanted_elements(soup)
    
    # 본문 추출 - Business Times 전용 선택자
    content_elem = find_main_content_element(soup, [
        '.article-content',
        '.story-content',
        '.content-body',
        'article',
        '.post-content',
        '.main-content'
    ])
    
    if content_elem:
        article['content'] = extract_pure_article_text(content_elem)
    
    return article

def extract_article_content_cna(url, soup):
    """Channel NewsAsia 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': get_kst_now()
    }
    
    # 제목 추출
    title_elem = soup.select_one('h1, .headline, .article-headline')
    if title_elem:
        title_text = clean_text(title_elem.get_text())
        # 사이트 이름 제거
        if ' - ' in title_text:
            title_text = title_text.split(' - ')[0]
        article['title'] = title_text
    
    # 전체 비필요 요소 먼저 제거
    remove_unwanted_elements(soup)
    
    # 본문 추출 - CNA 전용 선택자
    content_elem = find_main_content_element(soup, [
        '.text-long',
        '.article-content',
        '.story-content',
        'article',
        '.content-body',
        '.post-content'
    ])
    
    if content_elem:
        article['content'] = extract_pure_article_text(content_elem)
    
    return article

def is_menu_text(text):
    """메뉴나 네비게이션 텍스트인지 확인"""
    menu_indicators = [
        # 로그인/계정 관련
        'log in', 'sign in', 'account', 'my feed', 'manage account', 'log out',
        'subscribe', 'newsletter', 'subscription',
        
        # 메뉴/네비게이션
        'menu', 'search', 'share', 'edition', 'search menu', 'breadcrumb',
        'navigation', 'header', 'footer', 'sidebar',
        
        # 사이트 섹션
        'top stories', 'latest news', 'breaking news', 'live tv', 'podcasts', 
        'radio schedule', 'tv schedule', 'watch', 'listen',
        
        # 카테고리
        'business', 'sport', 'lifestyle', 'luxury', 'commentary', 'sustainability',
        'singapore', 'asia', 'world', 'insider', 'cna explains',
        
        # 기술적 요소
        'news id', 'type landing_page', 'type all_videos', 'type all_vod', 'type all_podcasts',
        'id 1822271', 'id 1821936', 'id 1821901', 'id 4310561', 'id 1821876',
        'id 1821886', 'id 1821896', 'id 3384986', 'id 1881506', 'id 1821906',
        'id 1821911', 'id 1821891', 'id 1431321', 'id 1822266', 'id 5197731',
        'id 2005266', 'id 5191361',
        
        # 기타 UI 요소
        'find out what', 'submitted by', 'anonymous', 'verified', 'newsletters',
        'get the best', 'select your', 'sent to your inbox', 'east asia',
        'us/uk', 'cnar', 'cna938', 'documentaries & shows', 'news reports'
    ]
    
    text_lower = text.lower().strip()
    
    # 직접 매칭
    if any(indicator in text_lower for indicator in menu_indicators):
        return True
    
    # 패턴 매칭
    import re
    
    # ID 패턴 (News Id 1234567, Type landing_page 등)
    if re.search(r'\b(id|type)\s+\d+|\b(id|type)\s+\w+_\w+', text_lower):
        return True
    
    # 진엄한 메뉴 패턴 (A B C D E... 나열)
    words = text_lower.split()
    if len(words) > 10 and len([w for w in words if len(w) < 4]) > 5:
        return True
    
    # 진엄한 선택자나 링크 나열
    if text_lower.count(':') > 3 or text_lower.count('|') > 2:
        return True
    
    # 진엄한 소문자 나열 (a b c d e f g...)
    if len(text) > 100 and len([c for c in text if c.isupper()]) < len(text) * 0.1:
        single_chars = [w for w in words if len(w) == 1]
        if len(single_chars) > 5:
            return True
    
    return False

def remove_unwanted_elements(soup):
    """전체 페이지에서 비필요 요소 제거"""
    # 제거할 선택자 목록
    unwanted_selectors = [
        # 네비게이션
        'nav', '.nav', '.navigation', '.navbar', '.menu', '.breadcrumb',
        # 헤더/푸터
        'header', 'footer', '.header', '.footer', '.page-header', '.page-footer',
        # 사이드바
        '.sidebar', '.side-bar', '.left-sidebar', '.right-sidebar', 'aside',
        # 소셜/공유
        '.social-share', '.share-buttons', '.social-links', '.social-media',
        # 메타데이터
        '.tags', '.tag-list', '.categories', '.meta', '.author-info',
        # 댓글
        '.comments', '.comment-section', '.discussion',
        # 광고
        '.advertisement', '.ads', '.banner', '.promo',
        # 기타
        'script', 'style', '.hidden', '.sr-only',
        # CNA 전용
        '.c-header', '.c-footer', '.c-nav', '.c-sidebar',
        # 일반적인 메뉴 클래스
        '.main-nav', '.primary-nav', '.secondary-nav'
    ]
    
    for selector in unwanted_selectors:
        for elem in soup.select(selector):
            elem.decompose()

def find_main_content_element(soup, selectors):
    """주 콘텐츠 요소 찾기"""
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            return elem
    return None

def extract_pure_article_text(content_elem):
    """순수 기사 텍스트만 추출 - 중복 제거 및 개선된 처리"""
    # 내부에서 추가 불필요 요소 제거
    unwanted_inner = [
        '.related-articles', '.related-content', '.see-also',
        '.advertisement', '.ads', '.banner', '.promo',
        '.social-share', '.share-buttons', '.tags', '.meta',
        '.author-bio', '.author-info', '.byline',
        '.comments', '.comment-form', '.discussion',
        '.newsletter-signup', '.subscription',
        '.breadcrumb', '.navigation',
        'script', 'style', 'noscript'
    ]
    
    for selector in unwanted_inner:
        for elem in content_elem.select(selector):
            elem.decompose()
    
    # 단락 추출 - p 태그 우선, div는 p가 없을 때만
    paragraphs = content_elem.find_all('p')
    if not paragraphs:
        paragraphs = content_elem.find_all('div')
    
    # 문장 단위로 수집하여 중복 제거
    all_sentences = []
    seen_sentences = set()
    
    for p in paragraphs:
        text = clean_text(p.get_text())
        
        # 진짜 기사 내용인지 확인
        if not is_real_article_content(text):
            continue
            
        # 메뉴 텍스트 제거
        text = TextProcessor.clean_menu_text(text)
        if not text:
            continue
            
        # 문장 단위로 분리
        sentences = TextProcessor.extract_sentences(text)
        
        for sentence in sentences:
            # 정규화된 문장으로 중복 체크
            normalized = sentence.lower().strip()
            if normalized not in seen_sentences and len(sentence) > 10:  # 20 -> 10으로 완화
                seen_sentences.add(normalized)
                all_sentences.append(sentence)
    
    # 문장들을 병합하되 안전하게 자르기
    if all_sentences:
        merged_content = TextProcessor.merge_paragraphs(all_sentences, max_length=1000)
        return merged_content
    
    return ''

def is_real_article_content(text):
    """진짜 기사 내용인지 판단 - 더 관대하게"""
    if len(text) < 20:  # 30 -> 20으로 완화
        return False
    
    # 메뉴 텍스트 체크 - 엄격한 경우만
    if is_menu_sentence(text) and len(text) < 50:
        return False
    
    # 진짜 기사 내용의 지표
    article_signals = [
        # 인용구
        'said', 'announced', 'reported', 'stated', 'explained', 'confirmed',
        'according to', 'in a statement', 'speaking to', 'told reporters',
        
        # 정부/기관
        'government', 'ministry', 'minister', 'prime minister', 'parliament',
        'official', 'spokesperson', 'department', 'agency',
        
        # 지역/국가
        'singapore', 'malaysian', 'indonesian', 'thai', 'asean',
        
        # 수치/날짜
        'percent', 'million', 'billion', 'year', 'month', 'week',
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        
        # 기사 내용
        'policy', 'economic', 'growth', 'development', 'investment',
        'business', 'market', 'industry', 'company', 'project'
    ]
    
    text_lower = text.lower()
    signal_count = sum(1 for signal in article_signals if signal in text_lower)
    
    # 기사 지표가 없으면 기본 문장 구조 체크
    if signal_count == 0:
        # 완전한 문장 구조를 가진 기사인지 확인
        sentences = text.split('.')
        complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]  # 10 -> 5로 완화
        
        if len(complete_sentences) < 1:  # 2 -> 1로 완화
            return False
        
        # 단어 길이 및 분포 체크 - 더 관대하게
        words = text_lower.split()
        if len(words) < 5:  # 최소 5단어
            return False
    
    return signal_count > 0 or len(text.split('.')) >= 2

def extract_article_content_generic(url, soup):
    """범용 콘텐츠 추출 (폴백)"""
    article = {
        'title': '',
        'content': '',
        'publish_date': None
    }
    
    # 발행일 추출 시도
    publish_date = extract_publish_date(soup, default_to_now=False)
    if publish_date:
        article['publish_date'] = publish_date
    else:
        article['publish_date'] = get_kst_now()
    
    # 제목 추출
    title_elem = soup.find('h1')
    if not title_elem:
        title_elem = soup.find('title')
    if title_elem:
        title_text = clean_text(title_elem.get_text())
        # 사이트 이름 제거
        if ' - ' in title_text:
            title_text = title_text.split(' - ')[0]
        article['title'] = title_text
    
    # 전체 비필요 요소 먼저 제거
    remove_unwanted_elements(soup)
    
    # 본문 추출 - 다양한 선택자 시도 (더 많은 선택자 추가)
    content_elem = find_main_content_element(soup, [
        'article',
        'main',
        '.article-content',
        '.post-content',
        '.content-body',
        '.story-content',
        '.entry-content',
        '.main-content',
        # 추가 선택자
        '.article-body',
        '.news-content',
        '.text-content',
        '#article-content',
        '.article-text',
        '.post-body',
        '.content',
        '.single-content',
        '.detail-content'
    ])
    
    if content_elem:
        article['content'] = extract_pure_article_text(content_elem)
    else:
        # 폴백: 가장 많은 p 태그를 가진 div 찾기
        best_div = None
        max_content_score = 0
        
        for div in soup.find_all('div'):
            paragraphs = div.find_all('p')
            content_score = 0
            
            for p in paragraphs:
                text = clean_text(p.get_text())
                if is_real_article_content(text):
                    content_score += len(text)
            
            if content_score > max_content_score:
                max_content_score = content_score
                best_div = div
        
        if best_div:
            article['content'] = extract_pure_article_text(best_div)
    
    return article

def extract_article_content(url):
    """URL에 따라 적절한 추출 방법 선택"""
    try:
        # 더 나은 헤더 사용
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Mothership의 경우 추가 헤더
        if 'mothership' in url.lower():
            headers['Referer'] = 'https://www.google.com/'
        
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 도메인에 따라 다른 추출 방법 사용
        domain = urlparse(url).netloc.lower()
        
        article_data = None
        if 'straitstimes.com' in domain:
            article_data = extract_article_content_straits_times(url, soup)
        elif 'businesstimes.com.sg' in domain:
            article_data = extract_article_content_business_times(url, soup)
        elif 'channelnewsasia.com' in domain or 'cna.com.sg' in domain:
            article_data = extract_article_content_cna(url, soup)
        elif 'moe.gov.sg' in domain:
            article_data = extract_article_content_moe(url, soup)
        elif 'nac.gov.sg' in domain or 'catch.sg' in domain:
            article_data = extract_article_content_nac(url, soup)
        elif 'theindependent.sg' in domain:
            article_data = extract_article_content_independent(url, soup)
        else:
            article_data = extract_article_content_generic(url, soup)
        
        # 추출된 데이터 후처리
        if article_data:
            article_data = post_process_article_content(article_data)
        
        return article_data
            
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def is_valid_article_url(url, domain):
    """유효한 기사 URL인지 판단 - 더 유연한 접근"""
    url_lower = url.lower()
    if DEBUG_MODE:
        print(f"[DEBUG] Checking URL: {url}")
    
    # 제외할 패턴들 - 핵심적인 것들만
    exclude_patterns = [
        'javascript:', 'mailto:', 'tel:', '#', 'wa.me', 'whatsapp',
        '.pdf', '.jpg', '.png', '.gif', '.mp4', '.css', '.js',
        'subscribe', 'login', 'register', 'sign-up', 'newsletter-signup',
        'privacy-policy', 'terms-of-service', 'contact-us', 'about-us',
        '/search', '/tag/', '/topic/', '/category/', '/author/'
    ]
    
    # 제외 패턴 체크
    if any(pattern in url_lower for pattern in exclude_patterns):
        if DEBUG_MODE:
            print(f"[DEBUG] URL excluded by pattern: {url}") 
        return False
    
    # 사이트별 기사 URL 패턴 - 더 유연하게
    if 'channelnewsasia.com' in domain or 'cna.com.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking CNA URL patterns for: {url}")
        
        # CNA 기사 패턴 - 더 유연하게
        cna_patterns = [
            r'/singapore/[a-z0-9-]{5,}',          # 싱가포르 섹션 + 짧은 제목도 허용
            r'/asia/[a-z0-9-]{5,}',               # 아시아 섹션
            r'/world/[a-z0-9-]{5,}',              # 월드 섹션
            r'/business/[a-z0-9-]{5,}',           # 비즈니스 섹션
            r'/sport/[a-z0-9-]{5,}',              # 스포츠 섹션
            r'/lifestyle/[a-z0-9-]{5,}',          # 라이프스타일 섹션
            r'/commentary/[a-z0-9-]{5,}',         # 논평 섹션
            r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]{5,}', # 날짜 패턴
            r'/[a-z0-9-]{10,}-\d+$'               # 긴 제목-숫자 패턴
        ]
        
        # 섹션 루트 페이지는 제외 (정확히 매칭)
        url_path = urlparse(url).path.rstrip('/')
        if url_path in ['/singapore', '/asia', '/world', '/business', '/sport', '/lifestyle', '/commentary']:
            if DEBUG_MODE:
                print(f"[DEBUG] CNA section root page excluded: {url_path}")
            return False
        
        matched = any(re.search(pattern, url) for pattern in cna_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] CNA URL pattern match: {matched}")
        return matched
    
    elif 'straitstimes.com' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking ST URL patterns for: {url}")
        
        # Straits Times 기사 패턴 - 대소문자 모두 허용하고 더 유연하게
        st_patterns = [
            r'/singapore/[a-zA-Z0-9-]{5,}',          # 싱가포르 섹션
            r'/asia/[a-zA-Z0-9-/]{5,}',              # 아시아 섹션
            r'/world/[a-zA-Z0-9-/]{5,}',             # 월드 섹션
            r'/business/[a-zA-Z0-9-/]{5,}',          # 비즈니스 섹션
            r'/sport/[a-zA-Z0-9-/]{5,}',             # 스포츠 섹션
            r'/life/[a-zA-Z0-9-/]{5,}',              # 라이프 섹션
            r'/opinion/[a-zA-Z0-9-]{5,}',            # 오피니언 섹션
            r'/tech/[a-zA-Z0-9-]{5,}',               # 기술 섹션
            r'/politics/[a-zA-Z0-9-]{5,}',           # 정치 섹션
            r'/\d{4}/\d{2}/\d{2}/[a-zA-Z0-9-]{5,}', # 날짜 패턴
            r'/[a-zA-Z]{2,}/[a-zA-Z0-9-]{5,}',       # 두 글자 섹션
            r'/[a-zA-Z0-9-]{10,}'                     # 일반 기사 패턴 (더 유연하게)
        ]
        
        # ST 특별 페이지들만 제외
        if any(exclude in url_lower for exclude in ['/multimedia/', '/graphics/', '/180']):
            if DEBUG_MODE:
                print(f"[DEBUG] ST special page excluded")
            return False
            
        matched = any(re.search(pattern, url) for pattern in st_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] ST URL pattern match: {matched}")
        return matched
    
    elif 'businesstimes.com.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking BT URL patterns for: {url}")
        
        # Business Times 기사 패턴 - 더 유연하게
        bt_patterns = [
            r'/economy/[a-z0-9-]{5,}',            # 경제 섹션
            r'/companies/[a-z0-9-]{5,}',          # 기업 섹션
            r'/banking-finance/[a-z0-9-]{5,}',    # 금융 섹션
            r'/asean/[a-z0-9-]{5,}',              # 아세안 섹션
            r'/tech/[a-z0-9-]{5,}',               # 기술 섹션
            r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]{5,}', # 날짜 패턴
            r'/[a-z0-9-]{15,}$'                   # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in bt_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] BT URL pattern match: {matched}")
        return matched
    
    elif 'sbr.com.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking SBR URL patterns for: {url}")
        
        # Singapore Business Review 기사 패턴
        sbr_patterns = [
            r'/economy/[a-z0-9-]{5,}',                # 경제 섹션
            r'/companies/[a-z0-9-]{5,}',              # 기업 섹션
            r'/banking/[a-z0-9-]{5,}',                # 금융 섹션
            r'/real-estate/[a-z0-9-]{5,}',            # 부동산 섹션
            r'/technology/[a-z0-9-]{5,}',             # 기술 섹션
            r'/startups/[a-z0-9-]{5,}',               # 스타트업 섹션
            r'/sustainability/[a-z0-9-]{5,}',         # 지속가능성 섹션
            r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]{5,}',     # 날짜 패턴
            r'/[a-z0-9-]{10,}$'                       # 기사 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in sbr_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] SBR URL pattern match: {matched}")
        return matched
    
    elif 'moe.gov.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking MOE URL patterns for: {url}")
        
        # Ministry of Education 페이지 패턴
        moe_patterns = [
            r'/news/[a-z0-9-]{5,}',                   # 뉴스
            r'/press-releases/[a-z0-9-]{5,}',         # 보도자료
            r'/parliamentary-replies/[a-z0-9-]{5,}',  # 국회 답변
            r'/speeches/[a-z0-9-]{5,}',               # 연설
            r'/initiatives/[a-z0-9-]{5,}',            # 이니셔티브
            r'/policies/[a-z0-9-]{5,}',               # 정책
            r'/programmes/[a-z0-9-]{5,}',             # 프로그램
            r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]{5,}',     # 날짜 패턴
            r'/[a-z0-9-]{10,}$'                       # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in moe_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] MOE URL pattern match: {matched}")
        return matched
    
    elif 'nac.gov.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking NAC URL patterns for: {url}")
        
        # National Arts Council 페이지 패턴
        nac_patterns = [
            r'/whatson/[a-z0-9-]{5,}',                # 행사/프로그램
            r'/engage/[a-z0-9-]{5,}',                 # 참여 프로그램
            r'/news/[a-z0-9-]{5,}',                   # 뉴스
            r'/press-releases/[a-z0-9-]{5,}',         # 보도자료
            r'/events/[a-z0-9-]{5,}',                 # 이벤트
            r'/programmes/[a-z0-9-]{5,}',             # 프로그램
            r'/grants/[a-z0-9-]{5,}',                 # 보조금 정보
            r'/initiatives/[a-z0-9-]{5,}',            # 이니셔티브
            r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]{5,}',     # 날짜 패턴
            r'/[a-z0-9-]{10,}$'                       # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in nac_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] NAC URL pattern match: {matched}")
        return matched
    
    # Yahoo Singapore
    elif 'yahoo.com' in domain and 'sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking Yahoo SG URL patterns for: {url}")
        
        yahoo_patterns = [
            r'/[a-zA-Z0-9-]+-\d+\.html',           # Yahoo 기사 패턴 (제목-숫자.html)
            r'/news/[a-zA-Z0-9-]+',                 # 뉴스 섹션
            r'/singapore/[a-zA-Z0-9-]+',            # 싱가포르 섹션
            r'/finance/[a-zA-Z0-9-]+',              # 금융 섹션
            r'/lifestyle/[a-zA-Z0-9-]+',            # 라이프스타일 섹션
            r'/[a-zA-Z0-9-]{15,}'                   # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in yahoo_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] Yahoo URL pattern match: {matched}")
        return matched
    
    # Mothership
    elif 'mothership.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking Mothership URL patterns for: {url}")
        
        mothership_patterns = [
            r'/\d{4}/\d{2}/[a-zA-Z0-9-]+',         # 날짜 기반 URL
            r'/[a-zA-Z0-9-]+-[a-zA-Z0-9-]+',       # 하이픈이 포함된 URL
            r'/[a-zA-Z0-9-]{10,}'                   # 긴 제목 URL
        ]
        
        # Mothership 제외 패턴
        if any(exclude in url_lower for exclude in ['/category/', '/tag/', '/author/']):
            return False
            
        matched = any(re.search(pattern, url) for pattern in mothership_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] Mothership URL pattern match: {matched}")
        return matched
    
    # The Independent Singapore
    elif 'theindependent.sg' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking Independent SG URL patterns for: {url}")
        
        independent_patterns = [
            r'/\d{4}/\d{2}/\d{2}/[a-zA-Z0-9-]+',  # 날짜 기반 URL
            r'/[a-zA-Z0-9-]+-[a-zA-Z0-9-]+',       # 하이픈이 포함된 URL
            r'/[a-zA-Z0-9-]{15,}'                   # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in independent_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] Independent URL pattern match: {matched}")
        return matched
    
    # TODAY Online
    elif 'todayonline.com' in domain:
        if DEBUG_MODE:
            print(f"[DEBUG] Checking TODAY URL patterns for: {url}")
        
        today_patterns = [
            r'/singapore/[a-zA-Z0-9-]+',            # 싱가포르 섹션
            r'/world/[a-zA-Z0-9-]+',                # 월드 섹션
            r'/commentary/[a-zA-Z0-9-]+',           # 논평 섹션
            r'/lifestyle/[a-zA-Z0-9-]+',            # 라이프스타일 섹션
            r'/[a-zA-Z0-9-]+-\d+',                 # 제목-숫자 패턴
            r'/[a-zA-Z0-9-]{15,}'                   # 긴 제목 URL
        ]
        
        matched = any(re.search(pattern, url) for pattern in today_patterns)
        if DEBUG_MODE:
            print(f"[DEBUG] TODAY URL pattern match: {matched}")
        return matched
    
    # 기본 패턴 (모든 사이트용) - 매우 관대하게
    general_patterns = [
        r'/20\d{2}/\d{2}/\d{2}/[a-z0-9-]{3,}',   # 날짜 + 제목 패턴 (더 짧은 제목도 허용)
        r'/articles?/[a-z0-9-]{3,}',             # 기사 URL
        r'/news/[a-z0-9-]{3,}',                  # 뉴스 URL
        r'/story/[a-z0-9-]{3,}',                 # 스토리 URL
        r'/post/[a-z0-9-]{3,}',                  # 포스트 URL
        r'/press-releases/[a-z0-9-]{3,}',        # 보도자료 URL
        r'/events?/[a-z0-9-]{3,}',               # 이벤트 URL
        r'/programmes?/[a-z0-9-]{3,}',           # 프로그램 URL
        r'/initiatives?/[a-z0-9-]{3,}',          # 이니셔티브 URL
        r'/policies/[a-z0-9-]{3,}',              # 정책 URL
        r'/speeches/[a-z0-9-]{3,}',              # 연설 URL
        r'/singapore/[a-z0-9-]{3,}',             # 싱가포르 섹션
        r'/asia/[a-z0-9-]{3,}',                  # 아시아 섹션
        r'/world/[a-z0-9-]{3,}',                 # 월드 섹션
        r'/business/[a-z0-9-]{3,}',              # 비즈니스 섹션
        r'/economy/[a-z0-9-]{3,}',               # 경제 섹션
        r'/technology/[a-z0-9-]{3,}',            # 기술 섹션
        r'/[a-z0-9-]{10,}$',                     # 긴 제목 URL (10자 이상)
        r'/[a-z0-9-]+-\d+$',                     # 제목-숫자 패턴
        r'/[a-z0-9-]+/[a-z0-9-]{5,}',           # 카테고리/제목 패턴
        r'\w+://[^/]+/[^?#]+[a-zA-Z0-9-]{5,}'   # 일반적인 콘텐츠 URL (쿼리/앵커 제외)
    ]
    
    # URL이 최소 길이 요건을 만족하는지 확인
    if len(url) < 30:  # 너무 짧은 URL은 기사가 아닐 가능성
        if DEBUG_MODE:
            print(f"[DEBUG] URL too short: {url}")
        return False
    
    matched = any(re.search(pattern, url) for pattern in general_patterns)
    if DEBUG_MODE:
        print(f"[DEBUG] General URL pattern match: {matched} for {url}")
    return matched

def get_article_links_straits_times(soup, base_url):
    """The Straits Times 전용 링크 추출"""
    links = []
    domain = urlparse(base_url).netloc.lower()
    
    # ST의 기사 링크 셀렉터들 - 더 구체적으로
    article_selectors = [
        'a[href*="/singapore/"][href*="-"]',  # 싱가포르 섹션 기사
        'a[href*="/asia/"][href*="-"]',       # 아시아 섹션 기사
        'a[href*="/world/"][href*="-"]',      # 월드 섹션 기사
        'a[href*="/business/"][href*="-"]',   # 비즈니스 섹션 기사
        'a[href*="/life/"][href*="-"]',       # 라이프 섹션 기사
        'a[href*="/sport/"][href*="-"]',      # 스포츠 섹션 기사
        'a[href*="/opinion/"][href*="-"]',    # 오피니언 섹션 기사
        'h3 a[href]',                           # 헤드라인 링크
        'h2 a[href]',                           # 서브헤드라인 링크
        '.card-title a[href]',                  # 카드 제목 링크
        '.headline a[href]',                    # 헤드라인 클래스 링크
        'a[data-article-link]'                  # 기사 링크 속성
    ]
    
    for selector in article_selectors:
        for a in soup.select(selector):
            href = a.get('href', '')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            
            # 텍스트가 있는 링크만 (빈 링크 제외)
            link_text = a.get_text(strip=True)
            if not link_text or len(link_text) < 10:
                continue
            
            # 유효한 기사 URL인지 확인
            if is_valid_article_url(full_url, domain):
                links.append(full_url)
                if DEBUG_MODE:
                    print(f"[DEBUG] ST article found: {link_text[:50]}... -> {full_url}")
    
    # 중복 제거
    unique_links = list(set(links))
    if DEBUG_MODE:
        print(f"[DEBUG] ST total unique links found: {len(unique_links)}")
    
    return unique_links[:10]  # 최대 10개까지

def get_article_links_moe(soup, base_url):
    """MOE 전용 링크 추출"""
    links = []
    domain = urlparse(base_url).netloc.lower()
    
    # MOE는 주로 press-releases와 news 섹션
    for a in soup.select('a[href*="press-releases"], a[href*="/news/"]'):
        href = a.get('href', '')
        full_url = urljoin(base_url, href)
        
        # 유효한 기사 URL인지 확인
        if is_valid_article_url(full_url, domain):
            links.append(full_url)
    
    return list(set(links))[:10]

def get_article_links_independent(soup, base_url):
    """The Independent Singapore 전용 링크 추출"""
    links = []
    domain = urlparse(base_url).netloc.lower()
    
    # Independent는 WordPress 기반, 특정 셀렉터 사용
    article_selectors = [
        '.td-module-title a',          # 메인 기사 모듈
        '.entry-title a',              # 엔트리 제목
        'h3.entry-title a',            # h3 제목
        '.td_module_wrap h3 a',        # TD 모듈 래퍼
        '.td-big-grid-post .entry-title a',  # 큰 그리드 포스트
        '.td_module_1 h3 a',           # TD 모듈 1
        '.td_module_2 h3 a',           # TD 모듈 2
        '.td_module_3 h3 a',           # TD 모듈 3
        '.td_module_4 h3 a',           # TD 모듈 4
        '.td_module_5 h3 a',           # TD 모듈 5
        'article h3 a',                # article 내의 h3
        '.post-title a'                # 포스트 제목
    ]
    
    for selector in article_selectors:
        for a in soup.select(selector):
            href = a.get('href', '')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            link_text = a.get_text(strip=True)
            
            # 텍스트가 있고 충분히 긴 링크만
            if link_text and len(link_text) > 10:
                # Independent의 기사 URL 패턴 확인
                if ('/news/' in full_url or 
                    '/singapore/' in full_url or 
                    '/politics/' in full_url or 
                    '/lifestyle/' in full_url or 
                    re.search(r'/\d{4}/\d{2}/\d{2}/', full_url)):
                    links.append(full_url)
                    if DEBUG_MODE:
                        print(f"[DEBUG] Independent article found: {link_text[:50]}... -> {full_url}")
    
    # 중복 제거
    unique_links = list(set(links))
    if DEBUG_MODE:
        print(f"[DEBUG] Independent total unique links found: {len(unique_links)}")
    
    return unique_links[:10]

def get_article_links_generic(soup, base_url):
    """범용 링크 추출 - 개선된 버전"""
    links = []
    domain = urlparse(base_url).netloc.lower()
    if DEBUG_MODE:
        print(f"[DEBUG] Generic link extraction for domain: {domain}")
    
    # 일반적인 기사 링크 셀렉터들
    article_selectors = [
        'article a[href]',                      # article 태그 내의 링크
        'h1 a[href]', 'h2 a[href]', 'h3 a[href]',  # 헤드라인 링크
        '.headline a[href]',                    # headline 클래스
        '.title a[href]',                       # title 클래스
        '.post-title a[href]',                  # post-title 클래스
        '.entry-title a[href]',                 # entry-title 클래스
        '.news-title a[href]',                  # news-title 클래스
        '.article-title a[href]',               # article-title 클래스
        'a[href][title]',                       # title 속성이 있는 링크
        '.content a[href]',                     # content 영역의 링크
        '.main a[href]'                         # main 영역의 링크
    ]
    
    # 모든 링크를 수집하되, 더 똑똑한 필터링 적용
    all_links = []
    
    # 셀렉터별로 링크 수집
    for selector in article_selectors:
        for a in soup.select(selector):
            href = a.get('href', '')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            link_text = a.get_text(strip=True)
            
            # 링크가 기본 조건을 만족하는지 확인
            if len(full_url) > 30 and link_text and len(link_text) > 10:  # 링크와 충분한 텍스트
                all_links.append({
                    'url': full_url,
                    'text': link_text,
                    'domain': urlparse(full_url).netloc.lower()
                })
    
    # 일반 a 태그도 확인 (위 셀렉터에서 놓친 경우)
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        if not href:
            continue
            
        full_url = urljoin(base_url, href)
        link_text = a.get_text(strip=True)
        
        # 링크가 기사처럼 보이는지 확인 (텍스트 길이, URL 패턴 등)
        if (len(full_url) > 50 and link_text and len(link_text) > 20 and 
            '-' in full_url and  # 대부분의 기사 URL은 하이픈 포함
            not any(exclude in full_url.lower() for exclude in ['login', 'register', 'subscribe'])):
            all_links.append({
                'url': full_url,
                'text': link_text,
                'domain': urlparse(full_url).netloc.lower()
            })
    
    if DEBUG_MODE:
        print(f"[DEBUG] Found {len(all_links)} total potential article links")
    
    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique_links = []
    for link in all_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    # 도메인 내 링크만 필터링
    same_domain_links = [link for link in unique_links if domain in link['domain']]
    if DEBUG_MODE:
        print(f"[DEBUG] Found {len(same_domain_links)} unique same-domain links")
    
    # 각 링크를 URL 패턴으로 검증
    for link in same_domain_links:
        if is_valid_article_url(link['url'], domain):
            links.append(link['url'])
            if DEBUG_MODE:
                print(f"[DEBUG] Added valid link: {link['text'][:50]}... -> {link['url']}")
            
            # 최대 15개까지만 수집
            if len(links) >= 15:
                break
    
    if DEBUG_MODE:
        print(f"[DEBUG] Final link count for {domain}: {len(links)}")
    return list(set(links))[:10]  # 중복 제거 후 최대 10개

def create_summary(article_data, settings):
    """설정에 따른 요약 생성"""
    # 설정에서 AI 옵션 확인
    ai_options = settings.get('scrapingMethodOptions', {}).get('ai', {})
    provider = ai_options.get('provider', 'gemini')
    
    if DEBUG_MODE:
        print(f"[SUMMARY] AI provider: {provider}")
        print(f"[SUMMARY] Gemini API key available: {bool(os.environ.get('GOOGLE_GEMINI_API_KEY'))}")
    
    # Gemini API 사용 시도
    if provider == 'gemini' and os.environ.get('GOOGLE_GEMINI_API_KEY'):
        try:
            if DEBUG_MODE:
                print(f"[SUMMARY] Attempting Gemini API translation for: {article_data['title'][:50]}...")
            from ai_summary_free import translate_to_korean_summary_gemini
            gemini_summary = translate_to_korean_summary_gemini(
                article_data['title'], 
                article_data['content']
            )
            if gemini_summary:
                if DEBUG_MODE:
                    print(f"[SUMMARY] Gemini API success: {gemini_summary[:100]}...")
                return gemini_summary
            else:
                if DEBUG_MODE:
                    print(f"[SUMMARY] Gemini API returned empty result")
        except Exception as e:
            if DEBUG_MODE:
                print(f"[SUMMARY] Gemini API 오류, 키워드 요약으로 대체: {str(e)}")
    else:
        if DEBUG_MODE:
            print(f"[SUMMARY] Gemini API not available - provider: {provider}, key: {bool(os.environ.get('GOOGLE_GEMINI_API_KEY'))}")
    
    # Gemini 실패시 향상된 키워드 기반 요약 사용
    print(f"[SUMMARY] Using enhanced keyword-based summary")
    try:
        from ai_summary_free import enhanced_keyword_summary
        return enhanced_keyword_summary(article_data['title'], article_data['content'])
    except Exception as e:
        print(f"[SUMMARY] Enhanced summary failed, using basic: {str(e)}")
        return create_keyword_summary(article_data['title'], article_data['content'])

def create_keyword_summary(title, content):
    """향상된 키워드 기반 한글 요약"""
    # 정확한 키워드 매핑
    keywords = {
        # 기본 키워드
        'singapore': '싱가포르', 'economy': '경제', 'government': '정부',
        'education': '교육', 'health': '보건', 'transport': '교통',
        'technology': '기술', 'business': '비즈니스', 'covid': '코로나',
        'minister': '장관', 'policy': '정책', 'development': '개발',
        
        # 교통 관련
        'train': '교통', 'mrt': '교통', 'lrt': '교통', 'bus': '교통',
        'transport': '교통', 'traffic': '교통', 'airport': '공항', 'changi': '창이',
        
        # 교육 및 사회
        'school': '교육', 'student': '교육', 'university': '교육',
        'employment': '취업', 'job': '취업', 'work': '취업', 'salary': '취업',
        'mom': '취업', 'manpower': '취업', 'worker': '취업',
        
        # 부동산 및 주택
        'housing': '주택', 'hdb': '주택', 'condo': '부동산',
        'property': '부동산', 'condominium': '부동산',
        
        # 법률 및 범죄
        'police': '법률', 'court': '법률', 'law': '법률', 'crime': '범죄',
        'jail': '범죄', 'sentenced': '법률', 'trial': '법률',
        
        # 경제 및 금융
        'market': '경제', 'stock': '경제', 'bank': '금융', 'finance': '금융',
        'investment': '경제', 'trade': '경제', 'gdp': '경제',
        
        # 음식 및 문화
        'food': '음식', 'restaurant': '음식', 'hawker': '음식',
        'culture': '문화', 'arts': '문화', 'festival': '문화',
        
        # 정치 및 선거
        'election': '정치', 'parliament': '정치', 'voting': '선거',
        'prime': '정치', 'president': '정치',
        
        # 환경 및 기후
        'climate': '환경', 'environment': '환경', 'green': '환경',
        'carbon': '환경', 'sustainability': '환경',
        
        # 기술 및 혁신
        'startup': '기술', 'innovation': '기술', 'digital': '기술',
        'ai': '기술', 'artificial': '기술', 'data': '기술', 'cyber': '기술',
        
        # 관광 및 여행
        'tourism': '관광', 'tourist': '관광', 'travel': '관광',
        'visitor': '관광', 'hotel': '관광',
        
        # 국제 관계
        'malaysia': '국제', 'indonesia': '국제', 'thailand': '국제',
        'china': '국제', 'india': '국제', 'japan': '국제', 'korea': '국제',
        'asean': '국제', 'asia': '국제', 'global': '국제'
    }
    
    # 제목과 내용에서 핵심 키워드 추출
    found_keywords = []
    text_lower = (title + ' ' + content).lower()
    
    for eng, kor in keywords.items():
        if eng in text_lower:
            found_keywords.append(kor)
    
    # 중복 제거
    found_keywords = list(dict.fromkeys(found_keywords))
    
    # 요약 생성
    if found_keywords:
        summary = f"📰 {', '.join(found_keywords[:3])} 관련 뉴스"
    else:
        summary = f"📰 싱가포르 최신 뉴스"
    
    # 제목만 포함 (원문 내용 제외)
    summary += f"\n📢 {title[:80]}{'...' if len(title) > 80 else ''}"
    
    return summary

def scrape_news_ai():
    """AI 기반 향상된 뉴스 스크랩 함수"""
    settings = load_settings()
    sites = load_sites()
    articles_by_group = defaultdict(list)
    
    blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
    important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
    
    for site in sites:
        try:
            print(f"AI Scraping {site['name']}...")
            
            # AI 스크래퍼로 사이트 분석
            ai_scraper = get_ai_scraper()
            site_result = ai_scraper.scrape_with_ai(site['url'])
            
            if site_result['type'] == 'error':
                print(f"[ERROR] Failed to scrape {site['name']}: {site_result['error']}")
                continue
            
            # 링크 페이지인 경우 - 기사 링크들 추출
            if site_result['type'] == 'link_page':
                links = site_result.get('links', [])
                print(f"[AI] Found {len(links)} article links from {site['name']}")
                
                # 각 링크에 대해 기사 추출 (최적화)
                # 우선순위 사이트는 더 많이, 낮은 우선순위는 적게
                priority_limits = {
                    'The Straits Times': 4,
                    'Channel NewsAsia': 4,
                    'The Business Times': 3,
                    'Yahoo Singapore News': 3,
                    'Mothership': 3
                }
                max_links = priority_limits.get(site['name'], 2)  # 기본값 2개
                
                # 링크가 없으면 건너뛰기
                if not links:
                    print(f"[AI] No links to process for {site['name']}")
                    continue
                    
                for idx, article_url in enumerate(links[:max_links]):
                    try:
                        print(f"[AI] Processing article {idx+1}/{min(len(links), max_links)}: {article_url}")
                        
                        # AI로 기사 추출
                        ai_scraper = get_ai_scraper()
                        article_result = ai_scraper.scrape_with_ai(article_url)
                        
                        if article_result['type'] != 'article':
                            print(f"[AI] Skipping: not an article - {article_result['type']}")
                            continue
                        
                        # 기사 데이터 검증
                        if not article_result.get('title') or not article_result.get('content'):
                            print(f"[AI] Skipping: missing title or content")
                            continue
                        
                        if len(article_result['content']) < 50:
                            print(f"[AI] Skipping: content too short ({len(article_result['content'])} chars)")
                            continue
                        
                        # 키워드 필터링
                        full_text = f"{article_result['title']} {article_result['content']}"
                        
                        if is_blocked(full_text, blocked_keywords):
                            print(f"[AI] Skipping: blocked by keywords")
                            continue
                        
                        if settings['scrapTarget'] == 'important' and not contains_keywords(full_text, important_keywords):
                            print(f"[AI] Skipping: no important keywords")
                            continue
                        
                        print(f"[AI] Article passed validation: {article_result['title']}")
                        
                        # 기사 HTML에서 발행일 추출 시도
                        publish_date = None
                        if article_result.get('html'):
                            try:
                                soup = BeautifulSoup(article_result['html'], 'html.parser')
                                publish_date = extract_publish_date(soup, default_to_now=True)
                            except:
                                pass
                        
                        if not publish_date:
                            publish_date = get_kst_now()
                        
                        # 요약 생성
                        article_data = {
                            'title': article_result['title'],
                            'content': article_result['content'],
                            'publish_date': publish_date
                        }
                        summary = create_summary(article_data, settings)
                        print(f"[AI] Generated summary: {summary[:100]}...")
                        
                        # 그룹별로 기사 수집
                        articles_by_group[site['group']].append({
                            'site': site['name'],
                            'title': article_result['title'],
                            'url': article_url,
                            'summary': summary,
                            'content': article_result['content'],
                            'publish_date': publish_date.isoformat() if isinstance(publish_date, datetime) else publish_date,
                            'extracted_by': article_result.get('extracted_by', 'ai'),
                            'ai_classification': article_result.get('classification', {})
                        })
                        
                    except Exception as e:
                        print(f"[ERROR] Error processing article {article_url}: {e}")
                        continue
            
            # 직접 기사인 경우
            elif site_result['type'] == 'article':
                print(f"[AI] Direct article found from {site['name']}")
                
                if site_result.get('title') and site_result.get('content'):
                    full_text = f"{site_result['title']} {site_result['content']}"
                    
                    # 필터링
                    if not is_blocked(full_text, blocked_keywords):
                        if settings['scrapTarget'] != 'important' or contains_keywords(full_text, important_keywords):
                            
                            # 발행일 추출 시도
                            publish_date = None
                            if site_result.get('html'):
                                try:
                                    soup = BeautifulSoup(site_result['html'], 'html.parser')
                                    publish_date = extract_publish_date(soup, default_to_now=True)
                                except:
                                    pass
                            
                            if not publish_date:
                                publish_date = get_kst_now()
                            
                            article_data = {
                                'title': site_result['title'],
                                'content': site_result['content'],
                                'publish_date': publish_date
                            }
                            summary = create_summary(article_data, settings)
                            
                            articles_by_group[site['group']].append({
                                'site': site['name'],
                                'title': site_result['title'],
                                'url': site['url'],
                                'summary': summary,
                                'content': site_result['content'],
                                'publish_date': publish_date.isoformat() if isinstance(publish_date, datetime) else publish_date,
                                'extracted_by': site_result.get('extracted_by', 'ai'),
                                'ai_classification': site_result.get('classification', {})
                            })
                            
                            print(f"[AI] Direct article processed: {site_result['title']}")
                        else:
                            print(f"[AI] Direct article filtered by keywords")
                    else:
                        print(f"[AI] Direct article blocked by keywords")
                else:
                    print(f"[AI] Direct article missing title or content")
                    
        except Exception as e:
            print(f"[ERROR] Error scraping {site['name']}: {e}")
            continue
    
    # 그룹별로 기사 통합
    consolidated_articles = []
    
    for group, group_articles in articles_by_group.items():
        if not group_articles:
            continue
            
        # 중복 제거 (제목 기준)
        unique_articles = []
        seen_titles = set()
        for article in group_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        # 각 그룹에서 최대 3개의 주요 기사만 선택
        selected_articles = unique_articles[:3]
        
        # 그룹별 통합 기사 생성
        group_summary = {
            'group': group,
            'articles': selected_articles,
            'article_count': len(selected_articles),
            'sites': list(set(article['site'] for article in selected_articles)),
            'timestamp': get_kst_now_iso(),
            'scraping_method': 'ai_enhanced'
        }
        
        consolidated_articles.append(group_summary)
    
    # 결과 저장 (KST 기준)
    now_kst = get_kst_now()
    timestamp = now_kst.strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_articles, f, ensure_ascii=False, indent=2)
    
    # latest.json 파일 업데이트 (KST 기준)
    latest_info = {
        'lastUpdated': now_kst.isoformat(),
        'latestFile': f'news_{timestamp}.json',
        'scrapingMethod': 'ai_enhanced'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    print(f"\n[AI] Scraped {total_articles} articles from {len(consolidated_articles)} groups")
    return output_file

def scrape_news():
    """메인 스크랩 함수 - 설정에 따라 방식 선택"""
    settings = load_settings()
    scraping_method = settings.get('scrapingMethod', 'traditional')
    
    print(f"[SCRAPER] Selected method: {scraping_method}")
    
    # AI 스크래퍼 초기화 (지연 초기화)
    ai_scraper = get_ai_scraper()
    print(f"[SCRAPER] AI model status: {ai_scraper.model is not None}")
    print(f"[SCRAPER] AI API key: {bool(ai_scraper.api_key)}")
    
    # AI 사용량 통계 출력
    if ai_scraper.model:
        stats = ai_scraper.get_usage_stats()
        print(f"[AI_SCRAPER] Usage stats: {stats['requests_last_minute']}/{stats['remaining_quota']} quota, caches: {stats['cache_sizes']}")
        
        # 오래된 캐시 정리
        ai_scraper.clear_old_cache()
    
    if scraping_method == 'ai':
        if ai_scraper.model:
            print("[AI_SCRAPER] ========== STARTING AI-ENHANCED SCRAPING ==========")
            print(f"[AI_SCRAPER] Model: {ai_scraper.model.model_name if hasattr(ai_scraper.model, 'model_name') else 'gemini-1.5-flash'}")
            print(f"[AI_SCRAPER] Rate limit: {ai_scraper.max_requests_per_minute} requests/min")
            print(f"[AI_SCRAPER] Batch size: {ai_scraper.batch_size}")
            try:
                return scrape_news_ai()
            except Exception as e:
                print(f"[AI_SCRAPER] ========== AI SCRAPING FAILED ==========")
                print(f"[AI_SCRAPER] Error: {e}")
                import traceback
                print(f"[AI_SCRAPER] Traceback: {traceback.format_exc()}")
                if settings.get('scrapingMethodOptions', {}).get('ai', {}).get('fallbackToTraditional', True):
                    print("Falling back to traditional scraping with AI summaries...")
                    return scrape_news_traditional()
                else:
                    raise
        else:
            print("AI scraping requested but AI model not available. Using traditional scraping with AI summaries...")
            return scrape_news_traditional()
    elif scraping_method == 'rss':
        print("Using RSS feed scraping...")
        try:
            from scraper_rss import scrape_news_rss
            return scrape_news_rss()
        except Exception as e:
            print(f"RSS scraping failed: {e}")
            print("Falling back to traditional scraping...")
            return scrape_news_traditional()
    elif scraping_method == 'hybrid':
        print("Using hybrid scraping (RSS + Traditional)...")
        try:
            from scraper_hybrid import scrape_news_hybrid
            return scrape_news_hybrid()
        except Exception as e:
            print(f"Hybrid scraping failed: {e}")
            import traceback
            print(f"Hybrid scraping traceback:\n{traceback.format_exc()}")
            print("Falling back to traditional scraping...")
            return scrape_news_traditional()
    else:
        print("Using traditional scraping...")
        return scrape_news_traditional()

def scrape_news_traditional():
    """기존 방식의 스크랩 함수 (AI 없이)"""
    settings = load_settings()
    sites = load_sites()
    articles_by_group = defaultdict(list)
    
    blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
    important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
    
    # 더 나은 User-Agent 헤더들
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    ]
    
    for site in sites:
        try:
            print(f"\n[SCRAPER] === Scraping {site['name']} ({site['url']}) ===")
            
            # 사이트별로 다른 헤더 사용
            headers = {
                'User-Agent': user_agents[hash(site['name']) % len(user_agents)],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Mothership의 경우 추가 헤더
            if 'mothership' in site['url'].lower():
                headers['Referer'] = 'https://www.google.com/'
            
            response = requests.get(site['url'], timeout=10, headers=headers)
            
            print(f"[SCRAPER] HTTP Status: {response.status_code}")
            if response.status_code != 200:
                print(f"[SCRAPER] Failed to access {site['name']}: HTTP {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 사이트별 링크 추출
            domain = urlparse(site['url']).netloc.lower()
            print(f"[SCRAPER] Domain: {domain}")
            
            if 'straitstimes.com' in domain:
                print(f"[SCRAPER] Using Straits Times specific extractor")
                links = get_article_links_straits_times(soup, site['url'])
            elif 'moe.gov.sg' in domain:
                print(f"[SCRAPER] Using MOE specific extractor")
                links = get_article_links_moe(soup, site['url'])
            elif 'theindependent.sg' in domain:
                print(f"[SCRAPER] Using Independent specific extractor")
                links = get_article_links_independent(soup, site['url'])
            else:
                print(f"[SCRAPER] Using generic extractor")
                links = get_article_links_generic(soup, site['url'])
            
            print(f"[SCRAPER] Found {len(links)} article links for {site['name']}")
            if len(links) == 0:
                print(f"[SCRAPER] WARNING: No links found for {site['name']} - site may have changed structure")
                # 페이지 타이틀 확인
                title = soup.title.string if soup.title else "No title"
                print(f"[SCRAPER] Page title: {title[:100]}")
                continue
            
            # 기사별 처리
            # 우선순위별 링크 수 설정
            priority_limits = {
                'The Straits Times': 3,
                'Channel NewsAsia': 3,
                'The Business Times': 2,
                'Yahoo Singapore News': 2,
                'Mothership': 2
            }
            max_links = priority_limits.get(site['name'], 1)  # 기본값 1개
            
            for article_url in links[:max_links]:
                try:
                    if DEBUG_MODE:
                        print(f"[DEBUG] Processing article: {article_url}")
                    article_data = extract_article_content(article_url)
                    
                    if not article_data or not article_data['title']:
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: no title or data")
                        continue
                        
                    if len(article_data['content']) < 30:
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: content too short ({len(article_data['content'])} chars)")
                        continue
                    
                    # 제목부터 메뉴/네비게이션 페이지 확인
                    if is_menu_text(article_data['title']):
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: menu title detected - {article_data['title']}")
                        continue
                    
                    # 랜딩 페이지 또는 메뉴 페이지인지 확인
                    if is_landing_page_content(article_data['content']):
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: landing page content detected")
                        continue
                        
                    # 의미있는 기사 내용인지 확인
                    if not is_meaningful_content(article_data['content']):
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: not meaningful content")
                        continue
                    
                    # 카테고리 페이지 필터링 (제목 기반)
                    category_page_titles = [
                        'features', 'big read', 'top stories', 'latest news',
                        'breaking news', 'world news', 'asia news', 'business news',
                        'opinion', 'lifestyle', 'sports', 'technology',
                        'property', 'investment', 'markets', 'commentary',
                        'learning minds', 'newsletter', 'subscribe', 'health',
                        'politics', 'science', 'culture', 'entertainment'
                    ]
                    
                    if any(cat.lower() == article_data['title'].lower().strip() for cat in category_page_titles):
                        if DEBUG_MODE:
                            print(f"[DEBUG] Skipping: category page title detected - {article_data['title']}")
                        continue
                    
                    full_text = f"{article_data['title']} {article_data['content']}"
                    
                    # 필터링
                    if is_blocked(full_text, blocked_keywords):
                        print(f"[DEBUG] Skipping: blocked by keywords")
                        continue
                    
                    if settings['scrapTarget'] == 'recent' and not is_recent_article(article_data['publish_date']):
                        print(f"[DEBUG] Skipping: not recent article")
                        continue
                    
                    if settings['scrapTarget'] == 'important' and not contains_keywords(full_text, important_keywords):
                        print(f"[DEBUG] Skipping: no important keywords")
                        continue
                    
                    # 최종 유효성 검사 - 실제 기사 내용인지 재확인
                    if not validate_final_article_content(article_data):
                        print(f"[DEBUG] Skipping: failed final validation")
                        continue
                    
                    print(f"[DEBUG] Article passed all validations: {article_data['title']}")
                    
                    # 요약 생성
                    summary = create_summary(article_data, settings)
                    print(f"[DEBUG] Generated summary: {summary[:100]}...")
                    
                    # 그룹별로 기사 수집
                    articles_by_group[site['group']].append({
                        'site': site['name'],
                        'title': article_data['title'],
                        'url': article_url,
                        'summary': summary,
                        'content': article_data['content'],
                        'publish_date': article_data['publish_date'].isoformat() if article_data['publish_date'] else None
                    })
                    
                except Exception as e:
                    print(f"[ERROR] Error processing article {article_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"[SCRAPER] ERROR scraping {site['name']}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 그룹별로 기사 통합
    consolidated_articles = []
    
    for group, group_articles in articles_by_group.items():
        if not group_articles:
            continue
            
        # 중복 제거 (제목 기준)
        unique_articles = []
        seen_titles = set()
        for article in group_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        # 각 그룹에서 최대 3개의 주요 기사만 선택
        selected_articles = unique_articles[:3]
        
        # 그룹별 통합 기사 생성
        # KST 타임존 생성
        kst = pytz.timezone('Asia/Seoul')
        now_kst = datetime.now(kst)
        
        group_summary = {
            'group': group,
            'articles': selected_articles,
            'article_count': len(selected_articles),
            'sites': list(set(article['site'] for article in selected_articles)),
            'timestamp': now_kst.isoformat(),
            'scraping_method': 'traditional',
            'execution_type': 'scheduled' if os.environ.get('GITHUB_EVENT_NAME') == 'schedule' else 'manual'
        }
        
        consolidated_articles.append(group_summary)
    
    # 결과 저장 (KST 기준)
    now_kst = get_kst_now()
    timestamp = now_kst.strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_articles, f, ensure_ascii=False, indent=2)
    
    # GitHub Actions 환경변수로 배치 실행 여부 확인
    is_scheduled = os.environ.get('GITHUB_EVENT_NAME') == 'schedule'
    
    # latest.json 파일 업데이트 (KST 기준)
    latest_info = {
        'lastUpdated': now_kst.isoformat(),
        'latestFile': f'news_{timestamp}.json',
        'scrapingMethod': 'traditional',
        'executionType': 'scheduled' if is_scheduled else 'manual'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    print(f"\nScraped {total_articles} articles from {len(consolidated_articles)} groups")
    return output_file

if __name__ == "__main__":
    import sys
    from monitoring import create_execution_summary, check_and_send_notification, save_monitoring_log
    
    try:
        # 스크래핑 실행
        output_file = scrape_news()
        
        # 실행 결과 요약 생성
        summary = create_execution_summary(scraped_file=output_file)
        
        # 모니터링 로그 저장
        save_monitoring_log(summary)
        
        # 알림 전송
        check_and_send_notification(summary['status'], summary)
        
        # 성공 종료
        sys.exit(0)
        
    except Exception as e:
        print(f"Scraping failed with error: {e}")
        
        # 오류 요약 생성
        summary = create_execution_summary(error=e)
        
        # 모니터링 로그 저장
        save_monitoring_log(summary)
        
        # 오류 알림 전송
        check_and_send_notification('failure', summary)
        
        # 오류 종료
        sys.exit(1)