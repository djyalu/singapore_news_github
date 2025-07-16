import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from collections import defaultdict

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

def translate_to_korean_summary(title, content):
    """기사를 한글로 요약"""
    # 간단한 요약 생성 (실제로는 번역 API를 사용할 수 있음)
    # 여기서는 핵심 정보만 추출하여 한글 템플릿으로 표시
    
    # 제목에서 주요 정보 추출
    title_lower = title.lower()
    
    # 숫자 추출 (예: 성장률, 금액 등)
    numbers = re.findall(r'\d+\.?\d*%?', title + ' ' + content)
    
    # 주요 키워드 매핑
    keyword_mapping = {
        'economy': '경제',
        'gdp': 'GDP',
        'growth': '성장',
        'singapore': '싱가포르',
        'government': '정부',
        'business': '비즈니스',
        'technology': '기술',
        'covid': '코로나',
        'pandemic': '팬데믹',
        'market': '시장',
        'investment': '투자',
        'property': '부동산',
        'transport': '교통',
        'mrt': 'MRT',
        'education': '교육',
        'health': '건강',
        'healthcare': '의료',
        'finance': '금융',
        'bank': '은행',
        'trade': '무역',
        'export': '수출',
        'import': '수입'
    }
    
    # 한글 요약 생성
    summary = f"📰 {title}\n"
    
    # 주요 내용 요약 (처음 200자)
    content_preview = content[:200].strip()
    if len(content) > 200:
        content_preview += "..."
    
    # 키워드 기반 간단 요약
    found_keywords = []
    for eng, kor in keyword_mapping.items():
        if eng in title_lower or eng in content.lower():
            found_keywords.append(kor)
    
    if found_keywords:
        summary += f"🔍 주요 키워드: {', '.join(found_keywords[:3])}\n"
    
    if numbers:
        summary += f"📊 주요 수치: {', '.join(numbers[:3])}\n"
    
    summary += f"📝 {content_preview}"
    
    return summary

def create_summary(article_data, settings):
    """설정에 따른 요약 생성"""
    summary_parts = []
    
    # 한글 요약 생성
    korean_summary = translate_to_korean_summary(
        article_data['title'], 
        article_data['content']
    )
    
    return korean_summary

def extract_article_content(url):
    """간단한 기사 내용 추출"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 제목 추출
        title = ""
        title_selectors = ['h1', '.headline', '.title', 'title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                title = title_elem.get_text().strip()
                break
        
        # 본문 추출
        content = ""
        content_selectors = [
            'article', '.article-content', '.content', '.story', 
            '.post-content', 'main', '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 스크립트, 스타일 태그 제거
                for script in content_elem(["script", "style"]):
                    script.decompose()
                content = content_elem.get_text().strip()
                break
        
        # fallback: p 태그들 수집
        if not content:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
        
        return {
            'title': title,
            'content': content[:500],  # 처음 500자만
            'publish_date': datetime.now()
        }
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def scrape_news():
    settings = load_settings()
    sites = load_sites()
    articles_by_group = defaultdict(list)
    
    blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
    important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
    
    for site in sites:
        try:
            response = requests.get(site['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 기사 링크 추출
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = site['url'].rstrip('/') + href
                    else:
                        href = site['url'].rstrip('/') + '/' + href
                
                # 기사 링크로 보이는 패턴 필터링
                if any(pattern in href.lower() for pattern in ['article', 'news', 'story', '/20']):
                    links.append(href)
            
            # 중복 제거 및 최대 5개로 제한 (그룹별 통합을 위해 줄임)
            links = list(set(links))[:5]
            
            for article_url in links:
                try:
                    article_data = extract_article_content(article_url)
                    if not article_data or not article_data['title']:
                        continue
                    
                    full_text = f"{article_data['title']} {article_data['content']}"
                    
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
            
        # 각 그룹에서 최대 3개의 주요 기사만 선택
        selected_articles = group_articles[:3]
        
        # 그룹별 통합 기사 생성
        group_summary = {
            'group': group,
            'articles': selected_articles,
            'article_count': len(selected_articles),
            'sites': list(set(article['site'] for article in selected_articles)),
            'timestamp': datetime.now().isoformat()
        }
        
        consolidated_articles.append(group_summary)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_articles, f, ensure_ascii=False, indent=2)
    
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    print(f"Scraped {total_articles} articles from {len(consolidated_articles)} groups")
    return output_file

if __name__ == "__main__":
    # 스크래핑 실행
    scrape_news()
    
    # 30일 이전 데이터 자동 정리
    try:
        from cleanup_old_data import cleanup_old_data
        cleanup_old_data(30)
        print("Old data cleanup completed")
    except ImportError:
        print("cleanup_old_data module not found, skipping cleanup")
    except Exception as e:
        print(f"Error during cleanup: {e}")