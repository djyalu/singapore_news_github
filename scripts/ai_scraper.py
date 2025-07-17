import os
import re
import json
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

class AIScraper:
    def __init__(self):
        """AI 기반 스크래퍼 초기화"""
        self.api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("Warning: GOOGLE_GEMINI_API_KEY not found. AI features will be disabled.")

    def is_valid_article_url_ai(self, url: str, page_title: str = "", link_text: str = "") -> bool:
        """AI를 사용해 URL이 유효한 기사 링크인지 판단"""
        if not self.model:
            return self._fallback_url_validation(url)
        
        try:
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
                return result == "YES"
            else:
                return self._fallback_url_validation(url)
                
        except Exception as e:
            print(f"AI URL validation error: {e}")
            return self._fallback_url_validation(url)

    def _fallback_url_validation(self, url: str) -> bool:
        """AI 실패 시 폴백 URL 검증"""
        url_lower = url.lower()
        
        # 기본 제외 패턴
        exclude_patterns = [
            'javascript:', 'mailto:', 'tel:', '#', 'wa.me', 'whatsapp',
            '.pdf', '.jpg', '.png', '.gif', '.mp4', '.css', '.js',
            'subscribe', 'login', 'register', 'sign-up', 'newsletter',
            'search', '/tag/', '/category/', '/author/'
        ]
        
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
            
        # 기본 뉴스 패턴
        news_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # 날짜 패턴
            r'/singapore/', r'/asia/', r'/world/', r'/business/',
            r'/news/', r'/article/', r'/story/'
        ]
        
        return any(re.search(pattern, url_lower) for pattern in news_patterns)

    def classify_content_ai(self, html_content: str, url: str) -> Dict[str, any]:
        """AI를 사용해 HTML 콘텐츠를 분류"""
        if not self.model:
            return self._fallback_content_classification(html_content)
        
        try:
            # HTML을 텍스트로 변환 (처음 2000자)
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()[:2000]
            
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
                return {
                    'type': classification,
                    'is_article': classification == 'NEWS_ARTICLE',
                    'confidence': 'high' if classification in ['NEWS_ARTICLE', 'MENU_PAGE', 'LANDING_PAGE'] else 'low'
                }
            else:
                return self._fallback_content_classification(html_content)
                
        except Exception as e:
            print(f"AI content classification error: {e}")
            return self._fallback_content_classification(html_content)

    def _fallback_content_classification(self, html_content: str) -> Dict[str, any]:
        """AI 실패 시 폴백 콘텐츠 분류"""
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text().lower()
        
        # 기본 분류 로직
        if any(indicator in text for indicator in ['said', 'announced', 'reported', 'according to']):
            return {'type': 'NEWS_ARTICLE', 'is_article': True, 'confidence': 'medium'}
        elif any(indicator in text for indicator in ['sign in', 'menu', 'category', 'search']):
            return {'type': 'MENU_PAGE', 'is_article': False, 'confidence': 'medium'}
        else:
            return {'type': 'LANDING_PAGE', 'is_article': False, 'confidence': 'low'}

    def extract_article_ai(self, html_content: str, url: str) -> Dict[str, str]:
        """AI를 사용해 HTML에서 기사 제목과 본문 추출"""
        if not self.model:
            return self._fallback_article_extraction(html_content, url)
        
        try:
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
                return self._fallback_article_extraction(html_content, url)
                
        except Exception as e:
            print(f"AI article extraction error: {e}")
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
        """AI 실패 시 폴백 기사 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 기본 제목 추출
        title = ""
        title_selectors = ['h1', 'h2', '.headline', '.title', 'title']
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text().strip()
                break
        
        # 기본 본문 추출
        content = ""
        content_selectors = ['article', '.content', '.article-content', '.story-content', 'main']
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # 불필요한 요소 제거
                for tag in elem(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                content = elem.get_text().strip()[:1000]
                break
        
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
            
            # AI로 각 링크 검증 (처음 20개만)
            valid_links = []
            for link in all_links[:20]:
                if self.is_valid_article_url_ai(link['url'], link_text=link['text']):
                    valid_links.append(link['url'])
            
            return valid_links[:10]  # 최대 10개 반환
            
        except Exception as e:
            print(f"AI link extraction error: {e}")
            return self._fallback_link_extraction(html_content, base_url)

    def _fallback_link_extraction(self, html_content: str, base_url: str) -> List[str]:
        """AI 실패 시 폴백 링크 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if self._fallback_url_validation(full_url):
                    links.append(full_url)
        
        return list(set(links))[:10]  # 중복 제거 후 10개

    def scrape_with_ai(self, url: str) -> Dict[str, any]:
        """AI를 사용해 전체 스크랩 프로세스 수행"""
        try:
            # 페이지 가져오기
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            html_content = response.content.decode('utf-8', errors='ignore')
            
            # 1. 콘텐츠 분류
            classification = self.classify_content_ai(html_content, url)
            
            # 2. 기사가 아니면 링크 추출
            if not classification['is_article']:
                links = self.get_article_links_ai(html_content, url)
                return {
                    'type': 'link_page',
                    'classification': classification,
                    'links': links,
                    'url': url
                }
            
            # 3. 기사면 제목과 본문 추출
            article_data = self.extract_article_ai(html_content, url)
            
            return {
                'type': 'article',
                'classification': classification,
                'title': article_data['title'],
                'content': article_data['content'],
                'url': url,
                'extracted_by': article_data['extracted_by']
            }
            
        except Exception as e:
            print(f"AI scraping error for {url}: {e}")
            return {
                'type': 'error',
                'error': str(e),
                'url': url
            }

# 전역 인스턴스
ai_scraper = AIScraper()