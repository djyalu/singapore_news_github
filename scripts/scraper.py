import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

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

def create_summary(article_data, settings):
    summary_parts = []
    
    if settings.get('summaryOptions', {}).get('headline', True):
        summary_parts.append(f"제목: {article_data['title']}")
    
    if settings.get('summaryOptions', {}).get('keywords', True):
        # 간단한 키워드 추출 (가장 자주 나오는 단어들)
        words = re.findall(r'\b\w+\b', article_data['content'].lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # 3글자 이상의 단어만
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_words:
            keywords = [word for word, _ in top_words]
            summary_parts.append(f"키워드: {', '.join(keywords)}")
    
    if settings.get('summaryOptions', {}).get('content', True):
        content_summary = article_data['content'][:200]
        if len(article_data['content']) > 200:
            content_summary += "..."
        summary_parts.append(f"요약: {content_summary}")
    
    return '\n'.join(summary_parts)

def extract_article_content(url):
    """간단한 기사 내용 추출"""
    try:
        response = requests.get(url, timeout=10)
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
    articles = []
    
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
            
            # 중복 제거 및 최대 10개로 제한
            links = list(set(links))[:10]
            
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
                    
                    articles.append({
                        'site': site['name'],
                        'group': site['group'],
                        'title': article_data['title'],
                        'url': article_url,
                        'summary': summary,
                        'publish_date': article_data['publish_date'].isoformat() if article_data['publish_date'] else None
                    })
                    
                except Exception as e:
                    print(f"Error processing article {article_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")
            continue
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Scraped {len(articles)} articles")
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