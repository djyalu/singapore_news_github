"""
차단된 사이트들을 위한 특별 처리 핸들러
각 사이트별 맞춤 접근 방법
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

class BlockedSitesHandler:
    def __init__(self):
        self.session = requests.Session()
        
    def get_mothership_via_api(self):
        """Mothership의 비공식 API 사용"""
        articles = []
        
        # Mothership는 내부 API가 있을 수 있음
        api_endpoints = [
            'https://mothership.sg/wp-json/mothership/v2/posts',
            'https://mothership.sg/api/articles/latest',
            'https://mothership.sg/feed/json'  # JSON 피드가 있을 수도
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # API 응답 구조에 따라 파싱
                    if isinstance(data, list):
                        for item in data[:5]:
                            articles.append({
                                'site': 'Mothership',
                                'title': item.get('title', {}).get('rendered', ''),
                                'url': item.get('link', ''),
                                'content': item.get('excerpt', {}).get('rendered', '')[:200],
                                'publish_date': item.get('date', datetime.now(KST).isoformat()),
                                'extracted_by': 'api'
                            })
                    break
            except:
                continue
                
        return articles
    
    def get_today_online_via_wayback(self):
        """TODAY Online을 Wayback Machine으로 접근"""
        articles = []
        
        # 오늘 날짜의 스냅샷 찾기
        today = datetime.now().strftime('%Y%m%d')
        wayback_url = f"https://web.archive.org/web/{today}/https://www.todayonline.com/"
        
        try:
            response = requests.get(wayback_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Wayback Machine의 링크 처리
                for link in soup.select('a[href*="/read/"]')[:5]:
                    href = link.get('href')
                    if href.startswith('/web/'):
                        # Wayback 링크를 원본 링크로 변환
                        parts = href.split('/')
                        if len(parts) > 4:
                            original_url = 'https://' + '/'.join(parts[4:])
                            
                            title = link.get_text().strip()
                            if title:
                                articles.append({
                                    'site': 'TODAY Online',
                                    'title': title,
                                    'url': original_url,
                                    'content': '',
                                    'publish_date': datetime.now(KST).isoformat(),
                                    'extracted_by': 'wayback_machine'
                                })
        except:
            pass
            
        return articles
    
    def get_independent_sg_mobile(self):
        """The Independent Singapore 모바일 버전"""
        articles = []
        mobile_url = "https://m.theindependent.sg/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        }
        
        try:
            response = self.session.get(mobile_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for article in soup.select('article, .post')[:5]:
                    link = article.find('a', href=True)
                    title = article.find(['h2', 'h3'])
                    
                    if link and title:
                        articles.append({
                            'site': 'The Independent Singapore',
                            'title': title.get_text().strip(),
                            'url': link['href'],
                            'content': '',
                            'publish_date': datetime.now(KST).isoformat(),
                            'extracted_by': 'mobile_version'
                        })
        except:
            pass
            
        return articles
    
    def get_via_google_news(self, site_name):
        """Google News를 통한 우회 접근"""
        articles = []
        
        # Google News 검색 URL
        search_query = f"site:{site_name.lower().replace(' ', '')} singapore"
        google_news_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-SG&gl=SG&ceid=SG:en"
        
        try:
            # feedparser 대신 직접 파싱
            response = requests.get(google_news_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                
                for item in soup.find_all('item')[:3]:
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    if title and link:
                        # Google News 리다이렉트 URL 처리
                        actual_url = self.extract_actual_url(link.text)
                        
                        articles.append({
                            'site': site_name,
                            'title': title.text,
                            'url': actual_url or link.text,
                            'content': '',
                            'publish_date': pub_date.text if pub_date else datetime.now(KST).isoformat(),
                            'extracted_by': 'google_news'
                        })
        except:
            pass
            
        return articles
    
    def extract_actual_url(self, google_news_url):
        """Google News 리다이렉트 URL에서 실제 URL 추출"""
        try:
            # Google News URL 파라미터에서 실제 URL 추출
            if 'url=' in google_news_url:
                import urllib.parse
                parsed = urllib.parse.urlparse(google_news_url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'url' in params:
                    return params['url'][0]
        except:
            pass
        return None
    
    def get_blocked_site_articles(self, site_name, site_url):
        """차단된 사이트별 맞춤 처리"""
        articles = []
        
        if site_name == "Mothership":
            # 1. API 시도
            articles = self.get_mothership_via_api()
            # 2. Google News 백업
            if not articles:
                articles = self.get_via_google_news("Mothership")
                
        elif site_name == "TODAY Online":
            # 1. Wayback Machine
            articles = self.get_today_online_via_wayback()
            # 2. Google News 백업
            if not articles:
                articles = self.get_via_google_news("TODAY Online")
                
        elif site_name == "The Independent Singapore":
            # 1. 모바일 버전
            articles = self.get_independent_sg_mobile()
            # 2. Google News 백업
            if not articles:
                articles = self.get_via_google_news("The Independent Singapore")
                
        else:
            # 기타 차단 사이트는 Google News 사용
            articles = self.get_via_google_news(site_name)
            
        return articles