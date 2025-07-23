import os
import re
import json
import time
import hashlib
from datetime import datetime
import pytz
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

# KST 타임존 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간(KST) 반환"""
    return datetime.now(KST)

def get_kst_now_iso():
    """현재 한국 시간을 ISO 형식 문자열로 반환"""
    return get_kst_now().isoformat()

class AIScraper:
    def __init__(self):
        """AI 기반 스크래퍼 초기화"""
        self.api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        print(f"[AI_SCRAPER] Initializing... API key present: {bool(self.api_key)}")
        print(f"[AI_SCRAPER] API key length: {len(self.api_key) if self.api_key else 0}")
        if self.api_key:
            # API 키 앞뒤 5자만 표시 (보안)
            key_preview = f"{self.api_key[:5]}...{self.api_key[-5:]}" if len(self.api_key) > 10 else "KEY_TOO_SHORT"
            print(f"[AI_SCRAPER] API key preview: {key_preview}")
        
        self.model = None
        if self.api_key:
            try:
                print("[AI_SCRAPER] Configuring Gemini API...")
                genai.configure(api_key=self.api_key)
                print("[AI_SCRAPER] Creating GenerativeModel...")
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print(f"[AI_SCRAPER] Gemini model initialized successfully")
                print(f"[AI_SCRAPER] Model type: {type(self.model)}")
            except Exception as e:
                print(f"[AI_SCRAPER] ERROR: Failed to initialize Gemini model")
                print(f"[AI_SCRAPER] Error type: {type(e).__name__}")
                print(f"[AI_SCRAPER] Error message: {str(e)}")
                import traceback
                print(f"[AI_SCRAPER] Traceback:\n{traceback.format_exc()}")
                self.model = None
        else:
            print("[AI_SCRAPER] ERROR: GOOGLE_GEMINI_API_KEY not found in environment")
            print("[AI_SCRAPER] Available env vars:", list(os.environ.keys())[:10], "...")  # 처음 10개만
        
        # Rate limiting for free tier (15 requests per minute)
        self.last_request_time = 0
        self.request_delay = 4.2  # 14 requests per minute (조금 더 빠르게)
        
        # 요청 카운터와 윈도우 관리 (1분 단위)
        self.request_timestamps = []
        self.max_requests_per_minute = 14  # 15개 제한에 가깝게 설정
        
        # 배치 처리를 위한 URL 큐
        self.url_queue = []
        self.batch_size = 5  # 한 번에 5개씩 처리 (효율성 향상)
        
        # 캐시 시스템 강화
        self.url_cache = {}  # {url: is_valid}
        self.content_cache = {}  # {url: classification}
        self.summary_cache = {}  # {content_hash: summary}

    def _rate_limit(self):
        """Rate limiting to avoid quota errors with sliding window"""
        current_time = time.time()
        
        # 슬라이딩 윈도우: 1분 이전의 요청들을 제거
        cutoff_time = current_time - 60  # 60초 전
        self.request_timestamps = [t for t in self.request_timestamps if t > cutoff_time]
        
        # 현재 윈도우에 최대 요청 수 초과 시 대기
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            oldest_request = min(self.request_timestamps)
            wait_time = 60 - (current_time - oldest_request) + 1  # 1초 여유
            if wait_time > 0:
                print(f"[AI_SCRAPER] Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                current_time = time.time()
        
        # 기존 지연 로직도 유지 (추가 안전 장치)
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            print(f"[AI_SCRAPER] Rate limiting: waiting {sleep_time:.1f}s between requests")
            time.sleep(sleep_time)
        
        # 요청 시점 기록
        self.last_request_time = time.time()
        self.request_timestamps.append(self.last_request_time)
    
    def get_usage_stats(self) -> Dict[str, any]:
        """배치 AI 사용량 통계 반환"""
        current_time = time.time()
        cutoff_time = current_time - 60
        recent_requests = [t for t in self.request_timestamps if t > cutoff_time]
        
        return {
            'total_requests_sent': len(self.request_timestamps),
            'requests_last_minute': len(recent_requests),
            'remaining_quota': max(0, self.max_requests_per_minute - len(recent_requests)),
            'cache_sizes': {
                'url_cache': len(self.url_cache),
                'content_cache': len(self.content_cache),
                'summary_cache': len(self.summary_cache)
            },
            'api_key_present': bool(self.api_key),
            'model_available': bool(self.model)
        }
    
    def clear_old_cache(self, max_age_minutes: int = 60):
        """오래된 캐시 항목 제거"""
        # 실제 사용에서는 캐시에 타임스탬프를 추가해야 하지만
        # 지금은 간단하게 전체 삭제
        if len(self.url_cache) > 1000:
            self.url_cache.clear()
            print("[AI_SCRAPER] Cleared URL cache (size limit reached)")
        
        if len(self.content_cache) > 500:
            self.content_cache.clear()
            print("[AI_SCRAPER] Cleared content cache (size limit reached)")
            
        if len(self.summary_cache) > 200:
            self.summary_cache.clear()
            print("[AI_SCRAPER] Cleared summary cache (size limit reached)")
    
    def _get_content_hash(self, content: str) -> str:
        """콘텐츠의 해시값 생성"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _should_use_ai(self, priority: str = 'medium') -> bool:
        """AI 사용 여부 결정 (rate limiting 고려)"""
        if not self.model:
            return False
        
        # 현재 분당 요청 수 확인
        current_time = time.time()
        cutoff_time = current_time - 60
        recent_requests = [t for t in self.request_timestamps if t > cutoff_time]
        
        # 우선순위별 임계값 (더 관대하게 설정)
        thresholds = {
            'high': 14,    # 중요한 작업은 거의 항상 AI 사용 (limit까지)
            'medium': 10,  # 중간 우선순위는 10개까지
            'low': 6       # 낮은 우선순위는 6개까지
        }
        
        threshold = thresholds.get(priority, 8)
        can_use_ai = len(recent_requests) < threshold
        
        if not can_use_ai:
            print(f"[AI_SCRAPER] Skipping AI for {priority} priority task (quota: {len(recent_requests)}/{self.max_requests_per_minute})")
        
        return can_use_ai
    
    def is_valid_article_url_ai(self, url: str, page_title: str = "", link_text: str = "") -> bool:
        """AI를 사용해 URL이 유효한 기사 링크인지 판단 (개선된 버전)"""
        # 캐시 확인
        if url in self.url_cache:
            return self.url_cache[url]
            
        # 1단계: 먼저 패턴 기반 필터링으로 명백한 비기사 URL 제거
        if not self._fallback_url_validation(url):
            self.url_cache[url] = False
            return False
            
        # 2단계: 패턴을 통과한 URL만 AI로 검증 (AI 호출 최소화)
        if not self.model:
            self.url_cache[url] = True
            return True  # 패턴 검증을 통과했으면 기사로 간주
        
        try:
            # 우선순위 기반 AI 사용 결정
            if not self._should_use_ai('normal'):
                # AI 요청 수 제한 초과 시 패턴 기반 판단만 사용
                is_valid = self._is_obvious_article_url(url)
                self.url_cache[url] = is_valid
                return is_valid
            
            # URL이 명백히 기사 패턴이면 AI 검증 스킵
            if self._is_obvious_article_url(url):
                self.url_cache[url] = True
                return True
                
            self._rate_limit()  # Apply rate limiting
            prompt = f"""
다음 URL이 뉴스 기사 링크인지 판단해주세요:

URL: {url}
페이지 제목: {page_title}
링크 텍스트: {link_text}

다음 기준으로 판단:
1. 실제 뉴스 기사로 이어지는 링크인가?
2. 메뉴, 네비게이션, 광고 링크는 아닌가?
3. PDF, 이미지, 비디오 파일은 아닌가?
4. 로그인, 구독, 검색 페이지는 아닌가?

답변을 정확히 "YES" 또는 "NO"로만 해주세요.
"""
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                result = response.text.strip().upper()
                is_valid = result == "YES"
                self.url_cache[url] = is_valid
                return is_valid
            else:
                print(f"[AI_SCRAPER] WARNING: Empty response from AI for URL validation")
                return self._fallback_url_validation(url)
                
        except Exception as e:
            print(f"[AI_SCRAPER] ERROR in URL validation for {url}")
            print(f"[AI_SCRAPER] Error type: {type(e).__name__}")
            print(f"[AI_SCRAPER] Error message: {str(e)}")
            if hasattr(e, 'status_code'):
                print(f"[AI_SCRAPER] Status code: {e.status_code}")
            return self._fallback_url_validation(url)

    def _fallback_url_validation(self, url: str) -> bool:
        """AI 실패 시 폴백 URL 검증 - 더 관대한 버전"""
        url_lower = url.lower()
        
        # 기본 제외 패턴 (명백히 기사가 아닌 것들만)
        exclude_patterns = [
            'javascript:', 'mailto:', 'tel:', 'wa.me', 'whatsapp',
            '.pdf', '.jpg', '.png', '.gif', '.mp4', '.css', '.js',
            '/login', '/register', '/sign-up',  # /subscribe와 /newsletter는 제거 (뉴스레터 페이지일 수도 있음)
            '/search?', '/tag/', '/author/',  # /about-us, /contact-us는 제거 (정부 사이트에서는 뉴스일 수도)
            '/privacy-policy', '/terms-of-service', '/sitemap'
        ]
        
        # 앙커 링크는 허용 (단, #만 있는 경우는 제외)
        if url.endswith('#') or url == '#':
            return False
            
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # 도메인 확인
        domain = urlparse(url).netloc.lower()
        
        # 뉴스 사이트 도메인 체크
        news_domains = [
            'straitstimes.com', 'businesstimes.com.sg', 'channelnewsasia.com', 
            'cna.com.sg', 'moe.gov.sg', 'nac.gov.sg', 'sbr.com.sg', 'catch.sg',
            'todayonline.com', 'mothership.sg', 'ricemedia.co', 'theindependent.sg'
        ]
        
        # 도메인 체크 - 더 유연하게
        domain_matched = False
        for news_domain in news_domains:
            if news_domain in domain or domain.endswith('.gov.sg'):
                domain_matched = True
                break
                
        if not domain_matched:
            return False
            
        # 섹션 페이지 체크 - 더 자세히
        path = urlparse(url).path.rstrip('/')
        if path:
            # 단순 섹션인지 확인
            simple_sections = ['/singapore', '/asia', '/world', '/business', '/sport', '/lifestyle', '/politics', '/tech']
            for section in simple_sections:
                if path == section:
                    return False  # 단순 섹션 페이지
                elif path.startswith(section + '/'):
                    # 섹션 하위에 뭔가 있으면 기사일 가능성
                    remaining_path = path[len(section):]
                    if len(remaining_path) > 5:  # 최소 길이
                        return True
        
        # 긍정적 패턴 (이런 패턴이 있으면 기사일 가능성 높음)
        positive_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # 날짜 패턴
            r'-\d{5,}',  # 숫자 ID 패턴
            r'/[a-z0-9-]{20,}',  # 긴 slug 패턴
            r'/singapore/[a-z0-9-]+',  # 섹션 + 기사 제목
            r'/asia/[a-z0-9-]+',
            r'/world/[a-z0-9-]+',
            r'/business/[a-z0-9-]+',
            r'/news/', r'/article/', r'/story/', r'/post/',
            r'/press-releases/', r'/events/', r'/programmes/',
            r'/media-releases/', r'/announcements/', r'/updates/',
            r'\.html$', r'\.htm$', r'\.aspx'  # 특정 확장자
        ]
        
        # 긍정적 패턴이 하나라도 있으면 통과
        if any(re.search(pattern, url_lower) for pattern in positive_patterns):
            return True
        
        # URL 길이와 구조 체크 - 더 관대하게
        path = urlparse(url).path
        if len(path) > 15 and path.count('/') >= 1:  # 기준 완화
            return True
            
        # 기본적으로 거부
        return False
    
    def _is_obvious_article_url(self, url: str) -> bool:
        """명백한 기사 URL 패턴인지 확인 (AI 호출 절약용)"""
        url_lower = url.lower()
        
        # 매우 명확한 기사 URL 패턴
        obvious_patterns = [
            r'/\d{4}/\d{2}/\d{2}/[\w-]+',  # /2024/01/15/article-title
            r'/article/\d+',  # /article/12345
            r'/story/\d+',  # /story/12345
            r'/news/\d{4}/\d{2}/\d{2}/',  # /news/2024/01/15/
            r'-\d{6,}\.',  # -123456.html
            r'/[\w-]+-ar\d+\.',  # /title-ar123456.html
            r'/singapore/[\w-]+-\d{7}',  # CNA pattern
            r'/asia/[\w-]+-\d{7}',
            r'/world/[\w-]+-\d{7}',
            r'/business/[\w-]+-\d{7}'
        ]
        
        return any(re.search(pattern, url_lower) for pattern in obvious_patterns)

    def classify_content_ai(self, html_content: str, url: str) -> Dict[str, any]:
        """AI를 사용해 HTML 콘텐츠를 분류 (캐시 기능 추가)"""
        if not self.model:
            return self._fallback_content_classification(html_content)
        
        # 콘텐츠 캐시 확인
        content_hash = self._get_content_hash(html_content[:1000])  # 처음 1000자로 해시 생성
        if content_hash in self.content_cache:
            return self.content_cache[content_hash]
        
        # AI 사용 여부 결정
        if not self._should_use_ai('high'):  # 콘텐츠 분류는 중요하므로 high priority
            print(f"[AI_SCRAPER] Skipping AI classification due to rate limit, using fallback")
            fallback_result = self._fallback_content_classification(html_content)
            self.content_cache[content_hash] = fallback_result
            return fallback_result
        
        try:
            self._rate_limit()  # Apply rate limiting
            # HTML을 텍스트로 변환 (처음 1500자로 축소)
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()[:1500]  # 요청 사이즈 축소
            
            prompt = f"""
다음 웹페이지 콘텐츠를 분석해서 분류해주세요:

URL: {url}
콘텐츠 (처음 2000자): {text_content}

다음 중 어떤 종류의 페이지인지 판단해주세요:
1. NEWS_ARTICLE - 실제 뉴스 기사
2. MENU_PAGE - 메뉴나 카테고리 페이지
3. LANDING_PAGE - 홈페이지나 섹션 메인 페이지
4. ADVERTISEMENT - 광고 페이지
5. ERROR_PAGE - 에러 페이지나 접근 불가 페이지

판단 기준:
- 실제 뉴스 기사: 제목, 본문, 날짜가 명확하고 구체적인 사건이나 정보를 다룸
- 메뉴 페이지: 링크 목록, 네비게이션, 카테고리 분류가 주요 내용
- 랜딩 페이지: 여러 기사 링크나 개요 정보가 나열됨
- 광고 페이지: 상품 판매, 서비스 홍보가 주요 내용
- 에러 페이지: 404, 접근 거부, 로그인 필요 등의 메시지

정확히 위의 5개 중 하나만 답해주세요.
"""
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                classification = response.text.strip().upper()
                result = {
                    'type': classification,
                    'is_article': classification == 'NEWS_ARTICLE',
                    'confidence': 'high' if classification in ['NEWS_ARTICLE', 'MENU_PAGE', 'LANDING_PAGE'] else 'low'
                }
                # 성공한 결과를 캐시에 저장
                self.content_cache[content_hash] = result
                return result
            else:
                print(f"[AI_SCRAPER] WARNING: Empty response from AI for content classification")
                fallback_result = self._fallback_content_classification(html_content)
                self.content_cache[content_hash] = fallback_result
                return fallback_result
                
        except Exception as e:
            print(f"[AI_SCRAPER] ERROR in content classification")
            print(f"[AI_SCRAPER] Error type: {type(e).__name__}")
            print(f"[AI_SCRAPER] Error message: {str(e)}")
            if hasattr(e, 'status_code'):
                print(f"[AI_SCRAPER] Status code: {e.status_code}")
            fallback_result = self._fallback_content_classification(html_content)
            self.content_cache[content_hash] = fallback_result
            return fallback_result

    def _fallback_content_classification(self, html_content: str) -> Dict[str, any]:
        """AI 실패 시 폴백 콘텐츠 분류 - 개선된 버전"""
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text().lower()
        
        # 기사 지표들
        article_indicators = [
            'said', 'announced', 'reported', 'according to', 'minister',
            'government', 'singapore', 'police', 'court', 'company'
        ]
        
        # 메뉴/랜딩 페이지 지표들
        menu_indicators = [
            'sign in', 'log in', 'menu', 'search', 'newsletter',
            'latest news', 'top stories', 'breaking news'
        ]
        
        # 점수 계산
        article_score = sum(1 for indicator in article_indicators if indicator in text)
        menu_score = sum(1 for indicator in menu_indicators if indicator in text)
        
        # h1, h2 태그 체크 (기사는 보통 명확한 제목이 있음)
        headings = soup.find_all(['h1', 'h2'])
        has_clear_title = False
        for h in headings:
            h_text = h.get_text().strip()
            if len(h_text) > 10 and not any(menu in h_text.lower() for menu in ['menu', 'search', 'sign']):
                has_clear_title = True
                break
        
        # 단락 수 체크
        paragraphs = soup.find_all('p')
        content_paragraphs = [p for p in paragraphs if len(p.get_text().strip()) > 50]
        
        # 분류 결정
        if article_score >= 3 and has_clear_title and len(content_paragraphs) >= 2:
            return {'type': 'NEWS_ARTICLE', 'is_article': True, 'confidence': 'medium'}
        elif menu_score >= 2 or text.count('http') > 20:  # 많은 링크는 메뉴/랜딩 페이지
            return {'type': 'MENU_PAGE', 'is_article': False, 'confidence': 'medium'}
        else:
            return {'type': 'LANDING_PAGE', 'is_article': False, 'confidence': 'low'}

    def extract_article_ai(self, html_content: str, url: str) -> Dict[str, str]:
        """AI를 사용해 HTML에서 기사 제목과 본문 추출"""
        if not self.model:
            return self._fallback_article_extraction(html_content, url)
        
        try:
            self._rate_limit()  # Apply rate limiting
            # HTML을 정리해서 텍스트로 변환
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 불필요한 요소 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # 텍스트 추출 (처음 5000자)
            text_content = soup.get_text()[:5000]
            
            prompt = f"""
다음 웹페이지에서 뉴스 기사의 제목과 본문을 추출해주세요:

URL: {url}
웹페이지 콘텐츠: {text_content}

다음 형식으로 정확히 답해주세요:
TITLE: [기사 제목]
CONTENT: [기사 본문 - 첫 500자 정도]

요구사항:
1. 제목은 실제 뉴스 기사 제목만 (사이트명, 메뉴명 제외)
2. 본문은 실제 기사 내용만 (광고, 메뉴, 네비게이션 제외)
3. 제목과 본문이 명확하지 않으면 "TITLE: NOT_FOUND" 및 "CONTENT: NOT_FOUND"로 응답
4. 한 줄씩 구분해서 작성
"""
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                result = self._parse_ai_extraction_result(response.text)
                return result
            else:
                print(f"[AI_SCRAPER] WARNING: Empty response from AI for article extraction")
                return self._fallback_article_extraction(html_content, url)
                
        except Exception as e:
            print(f"[AI_SCRAPER] ERROR in article extraction for {url}")
            print(f"[AI_SCRAPER] Error type: {type(e).__name__}")
            print(f"[AI_SCRAPER] Error message: {str(e)}")
            if hasattr(e, 'status_code'):
                print(f"[AI_SCRAPER] Status code: {e.status_code}")
            return self._fallback_article_extraction(html_content, url)

    def _parse_ai_extraction_result(self, ai_response: str) -> Dict[str, str]:
        """AI 응답을 파싱해서 제목과 본문 추출"""
        title = ""
        content = ""
        
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('CONTENT:'):
                content = line.replace('CONTENT:', '').strip()
        
        # NOT_FOUND 처리
        if title == "NOT_FOUND" or not title:
            title = ""
        if content == "NOT_FOUND" or not content:
            content = ""
        
        return {
            'title': title,
            'content': content,
            'extracted_by': 'ai'
        }

    def _fallback_article_extraction(self, html_content: str, url: str) -> Dict[str, str]:
        """AI 실패 시 폴백 기사 추출 - 개선된 버전"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 불필요한 요소 먼저 제거
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()
        
        # 기본 제목 추출
        title = ""
        title_selectors = [
            'h1.headline', 'h1[data-testid="headline"]', '.article-headline h1',
            'h1.title', 'article h1', 'main h1', 'h1'
        ]
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title_text = elem.get_text().strip()
                # 메뉴나 사이트명이 아닌 실제 제목인지 확인
                if len(title_text) > 10 and not any(exclude in title_text.lower() for exclude in ['menu', 'search', 'sign in']):
                    title = title_text
                    break
        
        # 제목이 없으면 title 태그에서 추출
        if not title:
            title_elem = soup.find('title')
            if title_elem:
                title_text = title_elem.get_text().strip()
                # 사이트명 제거
                if ' - ' in title_text:
                    title = title_text.split(' - ')[0].strip()
                elif ' | ' in title_text:
                    title = title_text.split(' | ')[0].strip()
                else:
                    title = title_text
        
        # 기본 본문 추출
        content = ""
        content_selectors = [
            'div[data-testid="article-body"]', '.article-content', '.story-content',
            '.content-body', '.post-content', 'article', '.main-content', 'main'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # 내부의 불필요한 요소 제거
                for unwanted in elem.select('.social-share, .related-articles, .advertisement'):
                    unwanted.decompose()
                
                # 단락 추출
                paragraphs = []
                for p in elem.find_all(['p', 'div']):
                    p_text = p.get_text().strip()
                    # 의미있는 단락인지 확인
                    if len(p_text) > 30 and not any(exclude in p_text.lower() for exclude in ['sign in', 'menu', 'search']):
                        paragraphs.append(p_text)
                
                if paragraphs:
                    content = ' '.join(paragraphs[:10])[:1000]  # 최대 10단락, 1000자
                    break
        
        # content가 여전히 비어있으면 모든 p 태그에서 추출
        if not content:
            all_paragraphs = []
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if len(p_text) > 50:
                    all_paragraphs.append(p_text)
            
            if all_paragraphs:
                content = ' '.join(all_paragraphs[:5])[:1000]
        
        return {
            'title': title,
            'content': content,
            'extracted_by': 'fallback'
        }

    def get_article_links_ai(self, html_content: str, base_url: str) -> List[str]:
        """AI를 사용해 페이지에서 기사 링크들 추출"""
        if not self.model:
            return self._fallback_link_extraction(html_content, base_url)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 모든 링크 추출
            all_links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    link_text = a_tag.get_text().strip()
                    all_links.append({
                        'url': full_url,
                        'text': link_text
                    })
            
            # 먼저 폴백 검증으로 필터링
            pre_filtered = []
            for link in all_links:
                if self._fallback_url_validation(link['url']):
                    pre_filtered.append(link)
            
            # AI로 추가 검증 (처음 20개만)
            valid_links = []
            for link in pre_filtered[:20]:
                if self._is_obvious_article_url(link['url']):
                    valid_links.append(link['url'])
                elif self.is_valid_article_url_ai(link['url'], link_text=link['text']):
                    valid_links.append(link['url'])
            
            return valid_links[:10]  # 최대 10개 반환
            
        except Exception as e:
            print(f"AI link extraction error: {e}")
            return self._fallback_link_extraction(html_content, base_url)

    def _fallback_link_extraction(self, html_content: str, base_url: str) -> List[str]:
        """AI 실패 시 폴백 링크 추출 - 개선된 버전"""
        print(f"[FALLBACK] Extracting links from {base_url}")
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        seen_urls = set()
        
        # 기사 링크가 있을 가능성이 높은 컨테이너 찾기
        article_containers = soup.select(
            'main, article, .content, .articles, .news-list, .story-list, '
            '[class*="article"], [class*="story"], [class*="news"], '
            '.col-md-8, .main-content, #content, .container'
        )
        
        # 컨테이너가 없으면 전체 페이지에서 찾기
        if not article_containers:
            article_containers = [soup]
            print("[FALLBACK] No specific containers found, searching entire page")
        else:
            print(f"[FALLBACK] Found {len(article_containers)} containers")
        
        # 모든 링크를 수집하고 점수를 매기기
        link_candidates = []
        
        for container in article_containers:
            for a_tag in container.find_all('a', href=True):
                href = a_tag.get('href')
                if not href:
                    continue
                    
                full_url = urljoin(base_url, href)
                
                # 중복 제거
                if full_url in seen_urls:
                    continue
                    
                seen_urls.add(full_url)
                
                # 링크 텍스트 확인
                link_text = a_tag.get_text().strip()
                
                # 점수 계산
                score = 0
                
                # URL 패턴 점수
                if self._is_obvious_article_url(full_url):
                    score += 10
                elif self._fallback_url_validation(full_url):
                    score += 5
                else:
                    continue  # 기본 검증도 통과 못하면 스킵
                
                # 링크 텍스트 길이 점수
                if len(link_text) > 50:
                    score += 3
                elif len(link_text) > 20:
                    score += 2
                elif len(link_text) > 10:
                    score += 1
                
                # h1, h2, h3 태그 내부에 있으면 가산점
                parent = a_tag.parent
                while parent and parent.name not in ['body', 'html']:
                    if parent.name in ['h1', 'h2', 'h3']:
                        score += 2
                        break
                    parent = parent.parent
                
                # 이미지가 포함된 링크면 가산점 (뉴스 기사는 종종 썸네일 포함)
                if a_tag.find('img'):
                    score += 1
                
                link_candidates.append({
                    'url': full_url,
                    'text': link_text,
                    'score': score
                })
        
        # 점수순으로 정렬
        link_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # 상위 링크들 선택
        for candidate in link_candidates[:15]:
            links.append(candidate['url'])
            print(f"[FALLBACK] Selected link (score: {candidate['score']}): {candidate['url'][:80]}...")
        
        # 링크가 너무 적으면 조건을 더 완화해서 다시 찾기
        if len(links) < 5:
            print("[FALLBACK] Too few links found, relaxing criteria...")
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if full_url not in seen_urls:
                        # 매우 관대한 조건 - 기본적인 제외 패턴만 체크
                        url_lower = full_url.lower()
                        if not any(pat in url_lower for pat in ['javascript:', 'mailto:', '#', '.pdf', '.jpg', '.png']):
                            # URL이 충분히 길고 복잡하면 추가
                            if len(urlparse(full_url).path) > 10:
                                links.append(full_url)
                                seen_urls.add(full_url)
                                if len(links) >= 10:
                                    break
        
        print(f"[FALLBACK] Total links found: {len(links)}")
        return links[:10]  # 최대 10개

    def scrape_with_ai(self, url: str) -> Dict[str, any]:
        """AI를 사용해 전체 스크랩 프로세스 수행"""
        print(f"\n[AI_SCRAPER] Starting scrape for: {url}")
        print(f"[AI_SCRAPER] AI Model Available: {self.model is not None}")
        
        try:
            # 페이지 가져오기
            print(f"[AI_SCRAPER] Fetching page...")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            
            html_content = response.content.decode('utf-8', errors='ignore')
            print(f"[AI_SCRAPER] Page fetched, content length: {len(html_content)}")
            
            # 1. 콘텐츠 분류
            print(f"[AI_SCRAPER] Classifying content...")
            classification = self.classify_content_ai(html_content, url)
            print(f"[AI_SCRAPER] Classification: {classification}")
            
            # 2. 기사가 아니면 링크 추출
            if not classification['is_article']:
                print(f"[AI_SCRAPER] Not an article, extracting links...")
                links = self.get_article_links_ai(html_content, url)
                print(f"[AI_SCRAPER] Found {len(links)} links")
                
                # 링크가 없으면 fallback으로 다시 시도
                if not links:
                    print(f"[AI_SCRAPER] No links found with AI, trying fallback...")
                    links = self._fallback_link_extraction(html_content, url)
                
                return {
                    'type': 'link_page',
                    'classification': classification,
                    'links': links,
                    'url': url
                }
            
            # 3. 기사면 제목과 본문 추출
            print(f"[AI_SCRAPER] Article detected, extracting content...")
            article_data = self.extract_article_ai(html_content, url)
            print(f"[AI_SCRAPER] Extraction complete: Title length={len(article_data.get('title', ''))}, Content length={len(article_data.get('content', ''))}")
            
            # 제목이나 본문이 없으면 fallback 시도
            if not article_data.get('title') or not article_data.get('content'):
                print(f"[AI_SCRAPER] Missing title or content, trying fallback extraction...")
                article_data = self._fallback_article_extraction(html_content, url)
            
            return {
                'type': 'article',
                'classification': classification,
                'title': article_data['title'],
                'content': article_data['content'],
                'url': url,
                'extracted_by': article_data['extracted_by'],
                'html': html_content  # HTML 콘텐츠 추가
            }
            
        except requests.RequestException as e:
            print(f"[AI_SCRAPER] Request error for {url}: {e}")
            return {
                'type': 'error',
                'error': f"Request failed: {str(e)}",
                'url': url
            }
        except Exception as e:
            print(f"[AI_SCRAPER] Unexpected error for {url}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'type': 'error',
                'error': str(e),
                'url': url
            }

# 전역 인스턴스
ai_scraper = AIScraper()