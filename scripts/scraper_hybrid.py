#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
하이브리드 스크래퍼: RSS + 전통적 스크래핑 결합
"""

import json
import os
from datetime import datetime
import pytz
from collections import defaultdict

# RSS 스크래퍼와 전통적 스크래퍼 가져오기
from scraper_rss import scrape_news_rss, RSS_FEEDS
from scraper import scrape_news_traditional, load_settings, load_sites, get_kst_now, get_kst_now_iso

def scrape_news_hybrid():
    """하이브리드 방식: RSS + Enhanced + Selenium"""
    print("[HYBRID] Starting hybrid scraping (RSS + Enhanced + Selenium)...")
    
    settings = load_settings()
    sites = load_sites()
    
    # RSS로 수집한 사이트 추적
    rss_sites = set(RSS_FEEDS.keys())
    rss_collected = set()
    
    # 먼저 RSS로 시도
    print("\n[HYBRID] Phase 1: RSS Scraping")
    articles_by_group = defaultdict(list)
    
    try:
        # RSS 스크래핑 수행 (파일에 저장하지 않고 메모리에만)
        from scraper_rss import scrape_rss_feed, SITE_GROUP_MAPPING
        
        for site_name, feed_url in RSS_FEEDS.items():
            articles = scrape_rss_feed(feed_url, site_name, settings)
            if articles:
                group = SITE_GROUP_MAPPING.get(site_name, 'News')
                articles_by_group[group].extend(articles)
                rss_collected.add(site_name)
                print(f"[HYBRID] RSS: Collected {len(articles)} articles from {site_name}")
            else:
                print(f"[HYBRID] RSS: No articles from {site_name}")
                
    except Exception as e:
        print(f"[HYBRID] RSS scraping error: {e}")
    
    # Enhanced 스크래핑으로 나머지 사이트 수집
    print("\n[HYBRID] Phase 2: Enhanced Scraping for remaining sites")
    
    # RSS로 수집하지 못한 사이트들만 필터링
    remaining_sites = [site for site in sites if site['name'] not in rss_collected]
    
    # Selenium이 필요한 사이트와 일반 사이트 분리
    selenium_required = ['TODAY Online', 'The Edge Singapore', 'Tech in Asia', 'AsiaOne']
    enhanced_sites = [s for s in remaining_sites if s['name'] not in selenium_required]
    selenium_sites = [s for s in remaining_sites if s['name'] in selenium_required]
    
    # Enhanced 스크래핑 수행
    if enhanced_sites:
        print(f"[HYBRID] Enhanced scraping for: {[s['name'] for s in enhanced_sites]}")
        
        try:
            # Enhanced 스크래퍼 임포트 및 실행
            from scraper_enhanced import scrape_site
            
            for site in enhanced_sites:
                try:
                    articles = scrape_site(site)
                    if articles:
                        group = site.get('group', 'News')
                        articles_by_group[group].extend(articles)
                        print(f"[HYBRID] Enhanced: Collected {len(articles)} articles from {site['name']}")
                except Exception as e:
                    print(f"[HYBRID] Enhanced scraping error for {site['name']}: {e}")
                    
        except ImportError:
            print("[HYBRID] Enhanced scraper not available, falling back to traditional")
            # 전통적 방식으로 폴백
            if enhanced_sites:
                remaining_sites = enhanced_sites
    
    # Selenium 스크래핑 수행 (GitHub Actions가 아닌 경우에만)
    if selenium_sites and not os.environ.get('GITHUB_ACTIONS'):
        print(f"\n[HYBRID] Phase 3: Selenium scraping for: {[s['name'] for s in selenium_sites]}")
        
        try:
            from scraper_selenium import scrape_with_selenium
            
            selenium_articles = scrape_with_selenium([s['name'] for s in selenium_sites])
            
            # 그룹별로 기사 추가
            for article in selenium_articles:
                site_info = next((s for s in sites if s['name'] == article['site']), {})
                group = site_info.get('group', 'News')
                articles_by_group[group].append(article)
            
            print(f"[HYBRID] Selenium: Collected {len(selenium_articles)} articles total")
            
        except ImportError:
            print("[HYBRID] Selenium not available (normal in GitHub Actions)")
        except Exception as e:
            print(f"[HYBRID] Selenium scraping error: {e}")
    
    # 전체 결과 통합
    print("\n[HYBRID] Phase 3: Consolidating results")
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
        
        # 각 그룹에서 최대 5개의 기사 (하이브리드는 더 많이)
        selected_articles = unique_articles[:5]
        
        # 그룹별 통합 기사 생성
        group_summary = {
            'group': group,
            'articles': selected_articles,
            'article_count': len(selected_articles),
            'sites': list(set(article['site'] for article in selected_articles)),
            'timestamp': get_kst_now_iso(),
            'scraping_method': 'hybrid',
            'execution_type': 'manual'
        }
        
        consolidated_articles.append(group_summary)
    
    # 결과 저장
    timestamp = get_kst_now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/scraped/news_{timestamp}.json'
    
    os.makedirs('data/scraped', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_articles, f, ensure_ascii=False, indent=2)
    
    # latest.json 파일 업데이트
    latest_info = {
        'lastUpdated': get_kst_now_iso(),
        'latestFile': f'news_{timestamp}.json',
        'scrapingMethod': 'hybrid',
        'executionType': 'manual'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    # 결과 요약
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    total_sites = len(set(article['site'] for group in consolidated_articles for article in group['articles']))
    
    print(f"\n[HYBRID] === Final Results ===")
    print(f"[HYBRID] Total articles: {total_articles}")
    print(f"[HYBRID] Total sites: {total_sites}")
    print(f"[HYBRID] RSS sites: {len(rss_collected)} ({', '.join(rss_collected)})")
    print(f"[HYBRID] Traditional sites: {len(remaining_sites)}")
    print(f"[HYBRID] Output: {output_file}")
    
    return output_file

if __name__ == "__main__":
    output_file = scrape_news_hybrid()
    print(f"\n[HYBRID] Scraping completed.")