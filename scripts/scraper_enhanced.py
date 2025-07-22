#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Web Scraper with Better Success Rate
- User-Agent rotation
- Better error handling
- Retry mechanism
- Cookie support
"""

import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import random
import time
from collections import defaultdict
from urllib.parse import urljoin, urlparse
from text_processing import TextProcessor
from deduplication import ArticleDeduplicator

# User-Agent 로테이션
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0',
]

def get_headers():
    """랜덤 헤더 생성"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

def fetch_with_retry(url, max_retries=3, delay=2):
    """재시도 로직이 포함된 페이지 가져오기"""
    session = requests.Session()
    
    for attempt in range(max_retries):
        try:
            # 요청 간 지연
            if attempt > 0:
                time.sleep(delay * attempt)
            
            # 쿠키 처리를 위한 세션 사용
            response = session.get(
                url, 
                headers=get_headers(), 
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print(f"[FETCH] 403 Forbidden for {url} (attempt {attempt + 1})")
                # 403인 경우 다른 User-Agent로 재시도
                continue
            elif response.status_code == 429:
                print(f"[FETCH] 429 Too Many Requests for {url}")
                time.sleep(delay * 3)  # 더 긴 대기
                continue
            else:
                print(f"[FETCH] Status {response.status_code} for {url}")
                
        except requests.exceptions.Timeout:
            print(f"[FETCH] Timeout for {url} (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError:
            print(f"[FETCH] Connection error for {url} (attempt {attempt + 1})")
        except Exception as e:
            print(f"[FETCH] Error for {url}: {type(e).__name__}")
    
    return None

def load_settings():
    """설정 파일 로드"""
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"scrapTarget": "recent", "blockedKeywords": ""}

def load_sites():
    """사이트 목록 로드"""
    try:
        with open('data/sites.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def is_recent_article(publish_date_str):
    """최근 기사인지 확인 (2일 이내)"""
    try:
        if isinstance(publish_date_str, str):
            publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
        else:
            publish_date = publish_date_str
        
        cutoff_date = datetime.now() - timedelta(days=2)
        return publish_date.replace(tzinfo=None) >= cutoff_date.replace(tzinfo=None)
    except:
        return True  # 날짜 파싱 실패시 포함

def extract_article_urls(soup, base_url, site_name):
    """향상된 기사 URL 추출"""
    urls = set()
    
    # 사이트별 특별 처리
    if 'straitstimes.com' in base_url:
        # Straits Times 특별 처리
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/singapore/' in href or '/asia/' in href or '/world/' in href:
                full_url = urljoin(base_url, href)
                urls.add(full_url)
    
    elif 'businesstimes.com.sg' in base_url:
        # Business Times 특별 처리
        for link in soup.find_all('a', href=True):
            href = link['href']
            if re.search(r'/(singapore|companies-markets|opinion|lifestyle)/', href):
                full_url = urljoin(base_url, href)
                urls.add(full_url)
    
    elif 'todayonline.com' in base_url:
        # TODAY Online - JavaScript 렌더링 필요
        print(f"[EXTRACT] {site_name} requires JavaScript rendering")
        return urls
    
    else:
        # 일반적인 URL 추출
        for link in soup.find_all('a', href=True):
            href = link['href']
            # 기사 URL 패턴
            if re.search(r'/(news|article|story|post|[0-9]{4}/[0-9]{2})', href):
                full_url = urljoin(base_url, href)
                if base_url.split('/')[2] in full_url:  # 같은 도메인인지 확인
                    urls.add(full_url)
    
    print(f"[EXTRACT] Found {len(urls)} URLs from {site_name}")
    return list(urls)

def extract_article_content(url, site_name):
    """향상된 기사 내용 추출"""
    response = fetch_with_retry(url)
    if not response:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 사이트별 특별 처리
    content_extractors = {
        'The Straits Times': lambda s: extract_straits_times(s),
        'Channel NewsAsia': lambda s: extract_cna(s),
        'Mothership': lambda s: extract_mothership(s),
        'The Business Times': lambda s: extract_business_times(s),
        'Yahoo Singapore News': lambda s: extract_yahoo(s),
        'The Independent Singapore': lambda s: extract_independent(s),
        'The New Paper': lambda s: extract_tnp(s),
        'AsiaOne': lambda s: extract_asiaone(s),
        'MustShareNews': lambda s: extract_mustsharenews(s),
        'Coconuts Singapore': lambda s: extract_coconuts(s),
    }
    
    extractor = content_extractors.get(site_name, extract_generic)
    return extractor(soup)

def extract_generic(soup):
    """일반적인 콘텐츠 추출"""
    article = {}
    
    # 제목
    title = soup.find('h1') or soup.find('title')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    # 날짜
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{1,2}\s+\w+\s+\d{4}',
        r'\w+\s+\d{1,2},\s+\d{4}'
    ]
    
    date_text = ''
    for pattern in date_patterns:
        date_match = soup.find(text=re.compile(pattern))
        if date_match:
            date_text = date_match
            break
    
    article['publish_date'] = str(datetime.now())
    
    # 내용
    content_tags = soup.find_all(['p', 'div'], class_=re.compile('content|article|body|text'))
    content = ' '.join([tag.get_text(strip=True) for tag in content_tags[:5]])
    article['content'] = content[:500] if content else 'No content'
    
    return article

def extract_straits_times(soup):
    """Straits Times 전용 추출"""
    article = {}
    
    # 제목
    title = soup.find('h1', class_='headline')
    if not title:
        title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    # 날짜
    date_elem = soup.find('time') or soup.find('div', class_='story-postdate')
    article['publish_date'] = str(datetime.now())
    
    # 내용
    content_div = soup.find('div', class_='story-content') or soup.find('div', class_='article-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'Premium content'
    
    return article

def extract_cna(soup):
    """Channel NewsAsia 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='article-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_mothership(soup):
    """Mothership 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='content-wrapper') or soup.find('div', class_='entry-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_business_times(soup):
    """Business Times 전용 추출"""
    article = {}
    
    title = soup.find('h1', class_='headline')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    article['publish_date'] = str(datetime.now())
    
    # Premium content 체크
    if soup.find('div', class_='paywall'):
        article['content'] = 'Premium content - subscription required'
    else:
        content_div = soup.find('div', class_='article-content')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
            article['content'] = content[:500]
        else:
            article['content'] = 'No content available'
    
    return article

def extract_yahoo(soup):
    """Yahoo Singapore 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='caas-body')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_independent(soup):
    """The Independent Singapore 전용 추출"""
    article = {}
    
    title = soup.find('h1', class_='entry-title')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time', class_='entry-date')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='entry-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_tnp(soup):
    """The New Paper 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    article['publish_date'] = str(datetime.now())
    
    content_div = soup.find('div', class_='article-body')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_asiaone(soup):
    """AsiaOne 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    article['publish_date'] = str(datetime.now())
    
    content_div = soup.find('div', class_='body-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_mustsharenews(soup):
    """MustShareNews 전용 추출"""
    article = {}
    
    title = soup.find('h1', class_='post-title')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='post-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def extract_coconuts(soup):
    """Coconuts Singapore 전용 추출"""
    article = {}
    
    title = soup.find('h1')
    article['title'] = title.get_text(strip=True) if title else 'No title'
    
    date_elem = soup.find('time')
    article['publish_date'] = date_elem.get('datetime', str(datetime.now())) if date_elem else str(datetime.now())
    
    content_div = soup.find('div', class_='post-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
        article['content'] = content[:500]
    else:
        article['content'] = 'No content available'
    
    return article

def scrape_site(site):
    """단일 사이트 스크래핑"""
    print(f"\n[SCRAPE] Processing {site['name']}...")
    
    # 메인 페이지 가져오기
    response = fetch_with_retry(site['url'])
    if not response:
        print(f"[SCRAPE] Failed to fetch {site['name']}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # URL 추출
    urls = extract_article_urls(soup, site['url'], site['name'])
    
    articles = []
    for url in urls[:5]:  # 사이트당 최대 5개
        print(f"[SCRAPE] Fetching article: {url}")
        article_data = extract_article_content(url, site['name'])
        
        if article_data:
            article_data['site'] = site['name']
            article_data['url'] = url
            
            # 최근 기사만 포함
            if is_recent_article(article_data.get('publish_date')):
                articles.append(article_data)
                print(f"[SCRAPE] Added article: {article_data['title'][:50]}...")
        
        # 요청 간 지연
        time.sleep(random.uniform(1, 2))
    
    return articles

def scrape_news_enhanced():
    """향상된 뉴스 스크래핑"""
    print("\n=== Enhanced News Scraper ===")
    print(f"Time: {datetime.now()}")
    
    settings = load_settings()
    sites = load_sites()
    
    # 결과 저장용
    all_articles = []
    site_success = {}
    
    # 사이트별 스크래핑
    for site in sites:
        try:
            articles = scrape_site(site)
            if articles:
                all_articles.extend(articles)
                site_success[site['name']] = len(articles)
                print(f"[SUCCESS] {site['name']}: {len(articles)} articles")
            else:
                site_success[site['name']] = 0
                print(f"[FAILED] {site['name']}: No articles")
        except Exception as e:
            print(f"[ERROR] {site['name']}: {type(e).__name__}")
            site_success[site['name']] = 0
    
    # 요약 및 그룹화
    processor = TextProcessor()
    grouped_articles = defaultdict(list)
    
    for article in all_articles:
        # 기사 요약 - TextProcessor의 process_article 사용
        processed = processor.process_article(
            article['title'],
            article['content'],
            article.get('publish_date', str(datetime.now())),
            article.get('url', ''),
            article.get('site', ''),
            settings
        )
        article['summary'] = processed.get('summary', article['title'])
        
        # 그룹화
        site_info = next((s for s in sites if s['name'] == article['site']), {})
        group = site_info.get('group', 'News')
        grouped_articles[group].append(article)
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/scraped/news_{timestamp}.json'
    
    result = []
    for group, articles in grouped_articles.items():
        # 중복 제거
        deduplicator = ArticleDeduplicator()
        unique_articles = deduplicator.remove_duplicates(articles)
        
        result.append({
            'group': group,
            'articles': unique_articles,
            'article_count': len(unique_articles),
            'sites': list(set(a['site'] for a in unique_articles)),
            'timestamp': datetime.now().isoformat(),
            'scraping_method': 'enhanced',
            'execution_type': 'manual'
        })
    
    # 파일 저장
    os.makedirs('data/scraped', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # latest.json 업데이트
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump({
            'lastUpdated': datetime.now().isoformat(),
            'latestFile': os.path.basename(filename),
            'scrapingMethod': 'enhanced',
            'executionType': 'manual'
        }, f, ensure_ascii=False, indent=2)
    
    # 성공률 출력
    print("\n=== Scraping Summary ===")
    total_sites = len(sites)
    successful_sites = sum(1 for v in site_success.values() if v > 0)
    total_articles = sum(site_success.values())
    
    print(f"Total sites: {total_sites}")
    print(f"Successful sites: {successful_sites} ({successful_sites/total_sites*100:.1f}%)")
    print(f"Total articles: {total_articles}")
    print(f"\nSite breakdown:")
    for site, count in site_success.items():
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {site}: {count} articles")
    
    return filename

if __name__ == "__main__":
    scrape_news_enhanced()