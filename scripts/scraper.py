import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from urllib.parse import urljoin, urlparse

def load_settings():
    with open('data/settings.json', 'r') as f:
        return json.load(f)

def load_sites():
    with open('data/sites.json', 'r') as f:
        return json.load(f)

def is_recent_article(article_date):
    if not article_date:
        return True
    return (datetime.now() - article_date).days <= 2

def contains_keywords(text, keywords):
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def is_blocked(text, blocked_keywords):
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in blocked_keywords)

def clean_text(text):
    """텍스트 정제 - HTML 태그, 특수문자, 공백 제거"""
    # 줄바꿈을 공백으로 변경
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # 다중 공백을 단일 공백으로
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return text.strip()

def extract_article_content_straits_times(url, soup):
    """The Straits Times 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': datetime.now()
    }
    
    # 제목 추출
    title_elem = soup.select_one('h1.headline, h1[data-testid="headline"], .article-headline h1')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 본문 추출
    content_elem = soup.select_one('div[data-testid="article-body"], .article-content, .paywall-content')
    if content_elem:
        # 불필요한 요소 제거
        for elem in content_elem.select('.related-articles, .advertisement, script, style'):
            elem.decompose()
        
        paragraphs = content_elem.find_all('p')
        content = ' '.join([clean_text(p.get_text()) for p in paragraphs if p.get_text().strip()])
        article['content'] = content[:1000]  # 1000자로 제한
    
    # 날짜 추출
    date_elem = soup.select_one('time, .published-date, [data-testid="publish-date"]')
    if date_elem:
        try:
            if date_elem.get('datetime'):
                article['publish_date'] = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            else:
                article['publish_date'] = datetime.now()
        except:
            article['publish_date'] = datetime.now()
    
    return article

def extract_article_content_moe(url, soup):
    """Ministry of Education 전용 콘텐츠 추출"""
    article = {
        'title': '',
        'content': '',
        'publish_date': datetime.now()
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
        'publish_date': datetime.now()
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
        article['publish_date'] = datetime.now()  # 간단히 현재 날짜 사용
    
    return article

def extract_article_content_generic(url, soup):
    """범용 콘텐츠 추출 (폴백)"""
    article = {
        'title': '',
        'content': '',
        'publish_date': datetime.now()
    }
    
    # 제목 추출
    title_elem = soup.find('h1')
    if not title_elem:
        title_elem = soup.find('title')
    if title_elem:
        article['title'] = clean_text(title_elem.get_text())
    
    # 본문 추출
    # 가장 긴 텍스트를 가진 요소 찾기
    main_content = ""
    for elem in soup.find_all(['article', 'main', 'div']):
        text = clean_text(elem.get_text())
        if len(text) > len(main_content):
            main_content = text
    
    article['content'] = main_content[:1000]
    
    return article

def extract_article_content(url):
    """URL에 따라 적절한 추출 방법 선택"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 도메인에 따라 다른 추출 방법 사용
        domain = urlparse(url).netloc.lower()
        
        if 'straitstimes.com' in domain:
            return extract_article_content_straits_times(url, soup)
        elif 'moe.gov.sg' in domain:
            return extract_article_content_moe(url, soup)
        elif 'nac.gov.sg' in domain or 'catch.sg' in domain:
            return extract_article_content_nac(url, soup)
        else:
            return extract_article_content_generic(url, soup)
            
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def get_article_links_straits_times(soup, base_url):
    """The Straits Times 전용 링크 추출"""
    links = []
    
    # 실제 기사 링크 패턴
    article_patterns = [
        r'/singapore/',
        r'/asia/',
        r'/world/',
        r'/business/',
        r'/sport/',
        r'/lifestyle/',
        r'/multimedia/'
    ]
    
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        full_url = urljoin(base_url, href)
        
        # 기사 URL 패턴 확인
        if any(pattern in href for pattern in article_patterns):
            # 제외할 패턴
            exclude_patterns = ['subscribe', 'login', 'register', 'terms', 'privacy']
            if not any(exclude in href.lower() for exclude in exclude_patterns):
                links.append(full_url)
    
    return list(set(links))[:10]  # 중복 제거 후 10개까지

def get_article_links_moe(soup, base_url):
    """MOE 전용 링크 추출"""
    links = []
    
    # MOE는 주로 press-releases와 news 섹션
    for a in soup.select('a[href*="press-releases"], a[href*="/news/"]'):
        href = a.get('href', '')
        full_url = urljoin(base_url, href)
        
        # 실제 기사인지 확인 (날짜 패턴 포함)
        if re.search(r'/20\d{2}/', href):
            links.append(full_url)
    
    return list(set(links))[:10]

def get_article_links_generic(soup, base_url):
    """범용 링크 추출"""
    links = []
    
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        full_url = urljoin(base_url, href)
        
        # 기본 필터링
        if any(pattern in href.lower() for pattern in ['article', 'news', 'story', '/20']):
            links.append(full_url)
    
    return list(set(links))[:10]

def create_summary(article_data, settings):
    """설정에 따른 요약 생성"""
    try:
        # 무료 AI 요약 시도
        from ai_summary_free import get_free_summary
        summary = get_free_summary(
            article_data['title'], 
            article_data['content']
        )
        # Gemini API 사용 성공 여부 확인
        if summary and not summary.startswith('📰 ' + article_data['title']):
            return summary
    except Exception as e:
        print(f"AI summary error: {e}")
    
    # 폴백: 향상된 키워드 기반 요약
    return create_keyword_summary(article_data['title'], article_data['content'])

def create_keyword_summary(title, content):
    """향상된 키워드 기반 한글 요약"""
    # 키워드 매핑
    keywords = {
        'singapore': '싱가포르', 'economy': '경제', 'government': '정부',
        'education': '교육', 'health': '보건', 'transport': '교통',
        'technology': '기술', 'business': '비즈니스', 'covid': '코로나',
        'minister': '장관', 'policy': '정책', 'development': '개발'
    }
    
    # 제목과 내용에서 핵심 키워드 추출
    found_keywords = []
    text_lower = (title + ' ' + content).lower()
    
    for eng, kor in keywords.items():
        if eng in text_lower:
            found_keywords.append(kor)
    
    # 요약 생성
    if found_keywords:
        summary = f"📰 {', '.join(found_keywords[:3])} 관련 뉴스\n"
    else:
        summary = f"📰 싱가포르 최신 뉴스\n"
    
    # 내용 요약
    sentences = content.split('.')[:2]  # 처음 2문장
    if sentences:
        summary += f"📝 {'. '.join(sentences).strip()}..."
    
    return summary

def scrape_news():
    settings = load_settings()
    sites = load_sites()
    articles_by_group = defaultdict(list)
    
    blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
    important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
    
    for site in sites:
        try:
            print(f"Scraping {site['name']}...")
            response = requests.get(site['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 사이트별 링크 추출
            domain = urlparse(site['url']).netloc.lower()
            if 'straitstimes.com' in domain:
                links = get_article_links_straits_times(soup, site['url'])
            elif 'moe.gov.sg' in domain:
                links = get_article_links_moe(soup, site['url'])
            else:
                links = get_article_links_generic(soup, site['url'])
            
            print(f"Found {len(links)} article links")
            
            # 기사별 처리
            for article_url in links[:5]:  # 사이트당 최대 5개
                try:
                    print(f"  Processing: {article_url}")
                    article_data = extract_article_content(article_url)
                    
                    if not article_data or not article_data['title'] or len(article_data['content']) < 50:
                        continue
                    
                    full_text = f"{article_data['title']} {article_data['content']}"
                    
                    # 필터링
                    if is_blocked(full_text, blocked_keywords):
                        continue
                    
                    if settings['scrapTarget'] == 'recent' and not is_recent_article(article_data['publish_date']):
                        continue
                    
                    if settings['scrapTarget'] == 'important' and not contains_keywords(full_text, important_keywords):
                        continue
                    
                    # 요약 생성
                    summary = create_summary(article_data, settings)
                    
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
                    print(f"Error processing article {article_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")
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
            'timestamp': datetime.now().isoformat()
        }
        
        consolidated_articles.append(group_summary)
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_articles, f, ensure_ascii=False, indent=2)
    
    # latest.json 파일 업데이트
    latest_info = {
        'lastUpdated': datetime.now().isoformat(),
        'latestFile': f'news_{timestamp}.json'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    print(f"\nScraped {total_articles} articles from {len(consolidated_articles)} groups")
    return output_file

if __name__ == "__main__":
    scrape_news()