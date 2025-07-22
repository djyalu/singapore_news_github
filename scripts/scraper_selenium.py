#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium-based Dynamic Scraper for JavaScript-heavy sites
- Handles TODAY Online, The Edge Singapore, etc.
- Requires Chrome/Chromium and chromedriver
"""

import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import re
from text_processing import TextProcessor
from deduplication import ArticleDeduplicator

def setup_driver():
    """Selenium WebDriver 설정"""
    options = Options()
    options.add_argument('--headless')  # 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    
    # Chrome 실행 파일 경로 (GitHub Actions)
    if os.environ.get('GITHUB_ACTIONS'):
        options.add_argument('--disable-software-rasterizer')
        options.binary_location = '/usr/bin/google-chrome-stable'
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"[SELENIUM] Failed to setup driver: {e}")
        return None

def scrape_today_online(driver):
    """TODAY Online 스크래핑"""
    print("[SELENIUM] Scraping TODAY Online...")
    articles = []
    
    try:
        driver.get('https://www.todayonline.com')
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # JavaScript 실행 대기
        time.sleep(3)
        
        # 기사 링크 수집
        article_elements = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/news/']")
        urls = [elem.get_attribute('href') for elem in article_elements[:5]]
        
        for url in urls:
            try:
                driver.get(url)
                time.sleep(2)
                
                # 제목
                title_elem = driver.find_element(By.TAG_NAME, "h1")
                title = title_elem.text
                
                # 날짜
                try:
                    date_elem = driver.find_element(By.CSS_SELECTOR, "time")
                    publish_date = date_elem.get_attribute('datetime')
                except:
                    publish_date = str(datetime.now())
                
                # 내용
                content_elems = driver.find_elements(By.CSS_SELECTOR, "div.article-content p")
                content = ' '.join([elem.text for elem in content_elems[:3]])
                
                articles.append({
                    'site': 'TODAY Online',
                    'title': title,
                    'url': url,
                    'content': content[:500],
                    'publish_date': publish_date
                })
                
            except Exception as e:
                print(f"[SELENIUM] Error scraping article {url}: {e}")
                continue
    
    except Exception as e:
        print(f"[SELENIUM] Error scraping TODAY Online: {e}")
    
    return articles

def scrape_edge_singapore(driver):
    """The Edge Singapore 스크래핑"""
    print("[SELENIUM] Scraping The Edge Singapore...")
    articles = []
    
    try:
        driver.get('https://www.theedgesingapore.com')
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "article"))
        )
        
        time.sleep(3)
        
        # 기사 링크 수집
        article_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/singapore/']")
        urls = [link.get_attribute('href') for link in article_links[:5]]
        
        for url in urls:
            try:
                driver.get(url)
                time.sleep(2)
                
                # 제목
                title_elem = driver.find_element(By.CSS_SELECTOR, "h1.article-title")
                title = title_elem.text
                
                # 날짜
                publish_date = str(datetime.now())
                
                # 내용 (페이월 체크)
                paywall = driver.find_elements(By.CSS_SELECTOR, ".paywall-content")
                if paywall:
                    content = "Premium content - subscription required"
                else:
                    content_elems = driver.find_elements(By.CSS_SELECTOR, ".article-body p")
                    content = ' '.join([elem.text for elem in content_elems[:3]])
                
                articles.append({
                    'site': 'The Edge Singapore',
                    'title': title,
                    'url': url,
                    'content': content[:500],
                    'publish_date': publish_date
                })
                
            except Exception as e:
                print(f"[SELENIUM] Error scraping article {url}: {e}")
                continue
    
    except Exception as e:
        print(f"[SELENIUM] Error scraping The Edge Singapore: {e}")
    
    return articles

def scrape_tech_in_asia(driver):
    """Tech in Asia 스크래핑"""
    print("[SELENIUM] Scraping Tech in Asia...")
    articles = []
    
    try:
        driver.get('https://www.techinasia.com/singapore')
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "post-item"))
        )
        
        time.sleep(3)
        
        # 기사 링크 수집
        article_elements = driver.find_elements(By.CSS_SELECTOR, ".post-item a")
        urls = [elem.get_attribute('href') for elem in article_elements[:5]]
        
        for url in urls:
            try:
                driver.get(url)
                time.sleep(2)
                
                # 제목
                title_elem = driver.find_element(By.TAG_NAME, "h1")
                title = title_elem.text
                
                # 날짜
                try:
                    date_elem = driver.find_element(By.CSS_SELECTOR, "time")
                    publish_date = date_elem.get_attribute('datetime')
                except:
                    publish_date = str(datetime.now())
                
                # 내용
                content_elems = driver.find_elements(By.CSS_SELECTOR, ".content-wrapper p")
                content = ' '.join([elem.text for elem in content_elems[:3]])
                
                articles.append({
                    'site': 'Tech in Asia',
                    'title': title,
                    'url': url,
                    'content': content[:500],
                    'publish_date': publish_date
                })
                
            except Exception as e:
                print(f"[SELENIUM] Error scraping article {url}: {e}")
                continue
    
    except Exception as e:
        print(f"[SELENIUM] Error scraping Tech in Asia: {e}")
    
    return articles

def scrape_asiaone(driver):
    """AsiaOne 스크래핑"""
    print("[SELENIUM] Scraping AsiaOne...")
    articles = []
    
    try:
        driver.get('https://www.asiaone.com/singapore')
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "article-item"))
        )
        
        time.sleep(3)
        
        # 기사 링크 수집
        article_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/singapore/']")
        urls = [link.get_attribute('href') for link in article_links[:5]]
        
        for url in urls:
            try:
                driver.get(url)
                time.sleep(2)
                
                # 제목
                title_elem = driver.find_element(By.TAG_NAME, "h1")
                title = title_elem.text
                
                # 날짜
                publish_date = str(datetime.now())
                
                # 내용
                content_elems = driver.find_elements(By.CSS_SELECTOR, ".body-content p")
                content = ' '.join([elem.text for elem in content_elems[:3]])
                
                articles.append({
                    'site': 'AsiaOne',
                    'title': title,
                    'url': url,
                    'content': content[:500],
                    'publish_date': publish_date
                })
                
            except Exception as e:
                print(f"[SELENIUM] Error scraping article {url}: {e}")
                continue
    
    except Exception as e:
        print(f"[SELENIUM] Error scraping AsiaOne: {e}")
    
    return articles

def scrape_with_selenium(sites_to_scrape):
    """Selenium을 사용한 동적 사이트 스크래핑"""
    driver = setup_driver()
    if not driver:
        print("[SELENIUM] Driver setup failed")
        return []
    
    all_articles = []
    
    try:
        # 사이트별 스크래핑 함수 매핑
        scrapers = {
            'TODAY Online': scrape_today_online,
            'The Edge Singapore': scrape_edge_singapore,
            'Tech in Asia': scrape_tech_in_asia,
            'AsiaOne': scrape_asiaone,
        }
        
        for site_name in sites_to_scrape:
            if site_name in scrapers:
                print(f"\n[SELENIUM] Processing {site_name}...")
                articles = scrapers[site_name](driver)
                all_articles.extend(articles)
                print(f"[SELENIUM] Got {len(articles)} articles from {site_name}")
                
                # 사이트 간 지연
                time.sleep(2)
    
    finally:
        driver.quit()
    
    return all_articles

def is_recent_article(publish_date_str):
    """최근 기사인지 확인"""
    try:
        if isinstance(publish_date_str, str):
            publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
        else:
            publish_date = publish_date_str
        
        cutoff_date = datetime.now() - timedelta(days=2)
        return publish_date.replace(tzinfo=None) >= cutoff_date.replace(tzinfo=None)
    except:
        return True

def main():
    """메인 실행 함수"""
    print("\n=== Selenium Dynamic Scraper ===")
    print(f"Time: {datetime.now()}")
    
    # 동적 스크래핑이 필요한 사이트들
    dynamic_sites = ['TODAY Online', 'The Edge Singapore', 'Tech in Asia', 'AsiaOne']
    
    # Selenium으로 스크래핑
    articles = scrape_with_selenium(dynamic_sites)
    
    # 최근 기사만 필터링
    recent_articles = [a for a in articles if is_recent_article(a.get('publish_date'))]
    
    print(f"\nTotal articles scraped: {len(articles)}")
    print(f"Recent articles: {len(recent_articles)}")
    
    # 결과 저장 (테스트용)
    if recent_articles:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/scraped/selenium_test_{timestamp}.json'
        
        os.makedirs('data/scraped', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recent_articles, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    return recent_articles

if __name__ == "__main__":
    main()