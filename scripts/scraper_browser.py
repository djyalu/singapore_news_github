"""
Selenium 기반 브라우저 자동화 스크래퍼
JavaScript 렌더링이 필요한 사이트용
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[WARNING] Selenium not available")

import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

class BrowserScraper:
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            self.driver = None
            return
            
        # Chrome 옵션 설정
        self.options = Options()
        
        # Headless 모드 (서버 환경)
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # 봇 탐지 회피
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent 설정
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # 기타 옵션
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--proxy-server="direct://"')
        self.options.add_argument('--proxy-bypass-list=*')
        self.options.add_argument('--start-maximized')
        
        self.driver = None
    
    def init_driver(self):
        """드라이버 초기화"""
        if not SELENIUM_AVAILABLE:
            return False
            
        try:
            # GitHub Actions 환경에서는 chromedriver가 PATH에 있음
            self.driver = webdriver.Chrome(options=self.options)
            
            # 봇 탐지 회피 스크립트
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            return True
        except Exception as e:
            print(f"[BrowserScraper] Failed to init driver: {e}")
            return False
    
    def close_driver(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def wait_and_scroll(self, wait_time=2):
        """페이지 로딩 대기 및 스크롤"""
        time.sleep(wait_time)
        
        # 스크롤로 동적 콘텐츠 로딩
        if self.driver:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    
    def get_page_with_js(self, url, wait_selector=None):
        """JavaScript 렌더링이 필요한 페이지 가져오기"""
        if not self.driver:
            if not self.init_driver():
                return None
                
        try:
            # 페이지 로드
            self.driver.get(url)
            
            # 특정 요소 대기
            if wait_selector:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            else:
                self.wait_and_scroll()
            
            # 페이지 소스 반환
            return self.driver.page_source
            
        except Exception as e:
            print(f"[BrowserScraper] Error loading {url}: {e}")
            return None
    
    def extract_today_online(self):
        """TODAY Online 기사 추출 (Selenium 사용)"""
        if not SELENIUM_AVAILABLE:
            return []
            
        url = "https://www.todayonline.com/"
        html = self.get_page_with_js(url, wait_selector="article")
        
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # TODAY Online 기사 추출
        article_elements = soup.select('article, .article-card, [class*="article"]')
        
        for elem in article_elements[:5]:
            link = elem.find('a', href=True)
            if link:
                article_url = link['href']
                if not article_url.startswith('http'):
                    article_url = f"https://www.todayonline.com{article_url}"
                    
                title = elem.find(['h2', 'h3', 'h4'])
                if title:
                    articles.append({
                        'site': 'TODAY Online',
                        'title': title.get_text().strip(),
                        'url': article_url,
                        'content': '',
                        'publish_date': datetime.now(KST).isoformat(),
                        'extracted_by': 'selenium'
                    })
                    
        return articles
    
    def extract_tech_in_asia(self):
        """Tech in Asia 기사 추출 (Selenium + 로그인 필요)"""
        if not SELENIUM_AVAILABLE:
            return []
            
        # Tech in Asia는 로그인이 필요하므로 공개 페이지만
        url = "https://www.techinasia.com/search?query=singapore"
        html = self.get_page_with_js(url, wait_selector="[class*='post-card']")
        
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 검색 결과에서 기사 추출
        for card in soup.select('[class*="post-card"]')[:3]:
            link = card.find('a', href=True)
            title = card.find(['h3', 'h4'])
            
            if link and title:
                articles.append({
                    'site': 'Tech in Asia',
                    'title': title.get_text().strip(),
                    'url': f"https://www.techinasia.com{link['href']}",
                    'content': '',
                    'publish_date': datetime.now(KST).isoformat(),
                    'extracted_by': 'selenium'
                })
                
        return articles