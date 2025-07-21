#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS 피드 기반 뉴스 스크래퍼
"""

import feedparser
import requests
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict
from urllib.parse import urlparse
import re

# RSS 피드 목록
RSS_FEEDS = {
    'Mothership': 'https://mothership.sg/feed/',
    'Singapore Business Review': 'https://sbr.com.sg/news.rss',
    'Channel NewsAsia': 'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml',
    'The Independent Singapore': 'https://theindependent.sg/feed/',
    # 추가 피드들을 여기에 넣을 수 있음
}

# 그룹 매핑
SITE_GROUP_MAPPING = {
    'Mothership': 'Lifestyle',
    'Singapore Business Review': 'Economy',
    'Channel NewsAsia': 'News',
    'The Independent Singapore': 'Politics',
}

def load_settings():
    """설정 파일 로드"""
    try:
        # Vercel API 엔드포인트 호출
        api_url = 'https://singapore-news-github.vercel.app/api/auth.js?type=config'
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('settings'):
                print("[SETTINGS] Loaded settings from server API")
                return data['settings']
    except Exception as e:
        print(f"[SETTINGS] Failed to load from API: {e}")
    
    # 로컬 파일 폴백
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            print("[SETTINGS] Loaded settings from local file")
            return json.load(f)
    except:
        print("[SETTINGS] Using default settings")
        return {
            'scrapTarget': 'all',
            'blockedKeywords': '',
            'importantKeywords': 'singapore,싱가포르',
            'maxArticlesPerSite': 3
        }

def is_recent_article(pub_date, hours=24):
    """최근 기사인지 확인"""
    if not pub_date:
        return True
    
    try:
        # 문자열인 경우 datetime으로 변환
        if isinstance(pub_date, str):
            pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
        
        now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
        time_diff = now - pub_date
        return time_diff.total_seconds() < (hours * 3600)
    except:
        return True

def clean_text(text):
    """텍스트 정리"""
    if not text:
        return ''
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 중복 공백 제거
    text = ' '.join(text.split())
    # 특수 문자 정리
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    
    return text.strip()

def create_keyword_summary(title, content):
    """키워드 기반 한글 요약"""
    keywords = {
        'singapore': '싱가포르', 'economy': '경제', 'government': '정부',
        'education': '교육', 'health': '보건', 'transport': '교통',
        'technology': '기술', 'business': '비즈니스', 'covid': '코로나',
        'minister': '장관', 'policy': '정책', 'development': '개발',
        'housing': '주택', 'hdb': '주택', 'property': '부동산',
        'police': '법률', 'court': '법률', 'crime': '범죄',
        'market': '경제', 'investment': '경제', 'trade': '경제',
        'malaysia': '국제', 'indonesia': '국제', 'asean': '국제'
    }
    
    found_keywords = []
    text_lower = (title + ' ' + content).lower()
    
    for eng, kor in keywords.items():
        if eng in text_lower:
            found_keywords.append(kor)
    
    found_keywords = list(dict.fromkeys(found_keywords))[:3]
    
    if found_keywords:
        summary = f"📰 {', '.join(found_keywords)} 관련 뉴스"
    else:
        summary = f"📰 싱가포르 최신 뉴스"
    
    summary += f"\n📢 {title[:80]}{'...' if len(title) > 80 else ''}"
    
    return summary

def scrape_rss_feed(feed_url, site_name, settings):
    """RSS 피드에서 기사 수집"""
    articles = []
    
    try:
        print(f"\n[RSS] Fetching feed from {site_name}: {feed_url}")
        
        # feedparser로 RSS 피드 파싱
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"[RSS] Warning: Feed parsing error for {site_name}: {feed.bozo_exception}")
        
        print(f"[RSS] Found {len(feed.entries)} entries in {site_name} feed")
        
        # 설정에서 가져올 최대 기사 수
        max_articles = int(settings.get('maxArticlesPerSite', 3))
        blocked_keywords = [kw.strip() for kw in settings.get('blockedKeywords', '').split(',') if kw.strip()]
        important_keywords = [kw.strip() for kw in settings.get('importantKeywords', '').split(',') if kw.strip()]
        
        for entry in feed.entries[:max_articles * 2]:  # 필터링을 고려해 더 많이 가져옴
            try:
                # 제목과 내용 추출
                title = clean_text(entry.get('title', ''))
                
                # 내용 추출 (여러 필드 시도)
                content = ''
                for field in ['summary', 'description', 'content']:
                    if hasattr(entry, field):
                        if field == 'content' and isinstance(entry.content, list):
                            content = clean_text(entry.content[0].get('value', ''))
                        else:
                            content = clean_text(getattr(entry, field, ''))
                        if content:
                            break
                
                if not title or not content:
                    continue
                
                # URL 추출
                url = entry.get('link', '')
                if not url:
                    continue
                
                # 발행일 추출
                pub_date = None
                for date_field in ['published_parsed', 'updated_parsed']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        try:
                            pub_date = datetime(*getattr(entry, date_field)[:6])
                            break
                        except:
                            pass
                
                if not pub_date:
                    pub_date = datetime.now()
                
                # 필터링
                full_text = f"{title} {content}"
                
                # 차단 키워드 확인
                if blocked_keywords and any(kw.lower() in full_text.lower() for kw in blocked_keywords):
                    print(f"[RSS] Blocked by keywords: {title[:50]}...")
                    continue
                
                # 최근 기사 확인
                if settings['scrapTarget'] == 'recent' and not is_recent_article(pub_date):
                    print(f"[RSS] Not recent: {title[:50]}...")
                    continue
                
                # 중요 키워드 확인
                if settings['scrapTarget'] == 'important' and important_keywords:
                    if not any(kw.lower() in full_text.lower() for kw in important_keywords):
                        print(f"[RSS] No important keywords: {title[:50]}...")
                        continue
                
                # 요약 생성
                summary = create_keyword_summary(title, content)
                
                # 기사 추가
                article = {
                    'site': site_name,
                    'title': title,
                    'url': url,
                    'summary': summary,
                    'content': content[:1000],  # 최대 1000자
                    'publish_date': pub_date.isoformat() if pub_date else datetime.now().isoformat()
                }
                
                articles.append(article)
                print(f"[RSS] Added article: {title[:50]}...")
                
                if len(articles) >= max_articles:
                    break
                    
            except Exception as e:
                print(f"[RSS] Error processing entry: {e}")
                continue
                
    except Exception as e:
        print(f"[RSS] Error fetching feed from {site_name}: {e}")
    
    return articles

def scrape_news_rss():
    """RSS 피드 기반 뉴스 스크래핑"""
    settings = load_settings()
    articles_by_group = defaultdict(list)
    
    # 각 RSS 피드에서 기사 수집
    for site_name, feed_url in RSS_FEEDS.items():
        articles = scrape_rss_feed(feed_url, site_name, settings)
        
        if articles:
            group = SITE_GROUP_MAPPING.get(site_name, 'News')
            articles_by_group[group].extend(articles)
            print(f"[RSS] Collected {len(articles)} articles from {site_name}")
    
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
            'timestamp': datetime.now().isoformat(),
            'scraping_method': 'rss',
            'execution_type': 'manual'
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
        'latestFile': f'news_{timestamp}.json',
        'scrapingMethod': 'rss',
        'executionType': 'manual'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    print(f"\n[RSS] Total scraped: {total_articles} articles from {len(consolidated_articles)} groups")
    return output_file

if __name__ == "__main__":
    output_file = scrape_news_rss()
    print(f"\n[RSS] Scraping completed. Output: {output_file}")