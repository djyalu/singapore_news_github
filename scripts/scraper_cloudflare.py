"""
Cloudflare 보호를 우회하는 스크래퍼
cloudscraper 라이브러리를 사용하여 JavaScript 챌린지 해결
"""

import cloudscraper
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import pytz

# KST 타임존
KST = pytz.timezone('Asia/Seoul')

class CloudflareScraper:
    def __init__(self):
        # cloudscraper 인스턴스 생성
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # 추가 헤더 설정
        self.scraper.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def fetch_with_cloudflare_bypass(self, url, max_retries=3):
        """Cloudflare 보호를 우회하여 페이지 가져오기"""
        for attempt in range(max_retries):
            try:
                # 요청 전 랜덤 딜레이
                time.sleep(random.uniform(2, 5))
                
                # cloudscraper로 요청
                response = self.scraper.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 503:
                    print(f"[CloudflareScraper] 503 error, retrying... (attempt {attempt + 1})")
                    time.sleep(10)  # Cloudflare 챌린지 대기
                    continue
                else:
                    print(f"[CloudflareScraper] Status {response.status_code} for {url}")
                    
            except Exception as e:
                print(f"[CloudflareScraper] Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
        return None
    
    def extract_mothership_articles(self):
        """Mothership 기사 추출 (Cloudflare 우회)"""
        url = "https://mothership.sg/"
        html = self.fetch_with_cloudflare_bypass(url)
        
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Mothership 기사 링크 추출
        article_links = soup.select('a[href*="/article/"]')
        
        for link in article_links[:5]:  # 최대 5개
            article_url = link.get('href')
            if not article_url.startswith('http'):
                article_url = f"https://mothership.sg{article_url}"
                
            # 개별 기사 페이지 가져오기
            article_html = self.fetch_with_cloudflare_bypass(article_url)
            if article_html:
                article_soup = BeautifulSoup(article_html, 'html.parser')
                
                # 제목 추출
                title = article_soup.select_one('h1')
                if title:
                    title_text = title.get_text().strip()
                    
                    # 내용 추출
                    content = article_soup.select_one('.content-wrapper, .article-content, [class*="content"]')
                    content_text = content.get_text().strip()[:200] if content else ""
                    
                    articles.append({
                        'site': 'Mothership',
                        'title': title_text,
                        'url': article_url,
                        'content': content_text,
                        'publish_date': datetime.now(KST).isoformat(),
                        'extracted_by': 'cloudflare_bypass'
                    })
                    
        return articles