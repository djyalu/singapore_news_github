import json
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from newspaper import Article
import openai

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

def summarize_article(article, settings):
    summary_parts = []
    
    if settings['summaryOptions']['headline']:
        summary_parts.append(f"제목: {article.title}")
    
    if settings['summaryOptions']['keywords']:
        keywords = article.keywords[:5] if article.keywords else []
        if keywords:
            summary_parts.append(f"키워드: {', '.join(keywords)}")
    
    if settings['summaryOptions']['content']:
        summary_parts.append(f"요약: {article.summary[:200]}...")
    
    return '\n'.join(summary_parts)

def scrape_news():
    settings = load_settings()
    sites = load_sites()
    articles = []
    
    blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
    important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
    
    for site in sites:
        try:
            response = requests.get(site['url'], timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)[:20]
            
            for link in links:
                try:
                    article_url = link['href']
                    if not article_url.startswith('http'):
                        article_url = site['url'] + article_url
                    
                    article = Article(article_url)
                    article.download()
                    article.parse()
                    article.nlp()
                    
                    full_text = f"{article.title} {article.text}"
                    
                    if is_blocked(full_text, blocked_keywords):
                        continue
                    
                    if settings['scrapTarget'] == 'recent' and not is_recent_article(article.publish_date):
                        continue
                    
                    if settings['scrapTarget'] == 'important' and not contains_keywords(full_text, important_keywords):
                        continue
                    
                    articles.append({
                        'site': site['name'],
                        'group': site['group'],
                        'title': article.title,
                        'url': article_url,
                        'summary': summarize_article(article, settings),
                        'publish_date': article.publish_date.isoformat() if article.publish_date else None
                    })
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
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
    scrape_news()