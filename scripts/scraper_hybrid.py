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

# 전통적 스크래퍼 가져오기
try:
    from scraper import scrape_news_traditional, load_settings, load_sites, get_kst_now, get_kst_now_iso
except ImportError:
    # 상대 임포트 시도
    import sys
    sys.path.append(os.path.dirname(__file__))
    from scraper import scrape_news_traditional, load_settings, load_sites, get_kst_now, get_kst_now_iso

def create_basic_summary(title, content):
    """기본 키워드 기반 요약 생성"""
    # 간단한 한국어 요약 생성
    content_preview = content[:100] + "..." if len(content) > 100 else content
    return f"📰 싱가포르 최신 뉴스\n📢 {title[:50]}{'...' if len(title) > 50 else ''}"

def scrape_news_hybrid():
    """하이브리드 방식: Traditional 링크 수집 + AI 요약"""
    print("[HYBRID] Starting hybrid scraping (Traditional Links + AI Summary)...")
    
    settings = load_settings()
    sites = load_sites()
    
    # Phase 1: Traditional 방식으로 기사 링크 수집
    print("\n[HYBRID] Phase 1: Traditional Link Collection")
    articles_by_group = defaultdict(list)
    
    # Traditional 스크래퍼로 기사 링크와 기본 정보 수집
    try:
        traditional_file = scrape_news_traditional()
        if traditional_file and os.path.exists(traditional_file):
            # Traditional 스크래핑 결과 파일 읽기
            with open(traditional_file, 'r', encoding='utf-8') as f:
                traditional_articles = json.load(f)
            
            # 기사 데이터를 하이브리드 구조로 변환
            for group_data in traditional_articles:
                group = group_data['group']
                for article in group_data['articles']:
                    articles_by_group[group].append({
                        'site': article['site'],
                        'title': article['title'],
                        'url': article['url'],
                        'content': article['content'],
                        'publish_date': article['publish_date'],
                        'extracted_by': 'traditional'
                    })
            print(f"[HYBRID] Traditional: Loaded articles from {len(traditional_articles)} groups")
        else:
            print("[HYBRID] Traditional scraping returned no file or file not found")
    except Exception as e:
        print(f"[HYBRID] Traditional scraping error: {e}")
        import traceback
        traceback.print_exc()
    
    # Phase 2: AI 요약 생성
    print("\n[HYBRID] Phase 2: AI Summary Generation")
    
    # AI 요약이 가능한지 확인 (Cohere 또는 Gemini)
    cohere_available = bool(os.environ.get('COHERE_API_KEY'))
    gemini_available = bool(os.environ.get('GOOGLE_GEMINI_API_KEY'))
    ai_available = cohere_available or gemini_available
    
    print(f"[HYBRID] Cohere API available: {cohere_available}")
    print(f"[HYBRID] Gemini API available: {gemini_available}")
    
    if ai_available:
        try:
            # AI 요약 모듈 임포트 시도
            try:
                from ai_summary_simple import translate_to_korean_summary_cohere, translate_to_korean_summary_gemini
            except ImportError:
                import sys
                sys.path.append(os.path.dirname(__file__))
                from ai_summary_simple import translate_to_korean_summary_cohere, translate_to_korean_summary_gemini
            
            # 각 기사에 대해 AI 요약 생성
            ai_count = 0
            max_ai_summaries = 25  # 최대 AI 요약 수 제한 (Cohere 월 1000개 제한 고려)
            
            for group, group_articles in articles_by_group.items():
                for article in group_articles:
                    if ai_count >= max_ai_summaries:
                        print(f"[HYBRID] AI summary limit reached ({max_ai_summaries})")
                        article['summary'] = create_basic_summary(article['title'], article['content'])
                        continue
                        
                    try:
                        ai_summary = None
                        api_used = None
                        
                        # Cohere API 우선 시도
                        if cohere_available and ai_count < max_ai_summaries:
                            print(f"[HYBRID] Trying Cohere API for: {article['title'][:50]}...")
                            ai_summary = translate_to_korean_summary_cohere(
                                article['title'], 
                                article['content']
                            )
                            if ai_summary:
                                api_used = 'cohere'
                                ai_count += 1
                        
                        # Cohere 실패시 Gemini 시도
                        if not ai_summary and gemini_available and ai_count < max_ai_summaries:
                            print(f"[HYBRID] Trying Gemini API for: {article['title'][:50]}...")
                            ai_summary = translate_to_korean_summary_gemini(
                                article['title'], 
                                article['content']
                            )
                            if ai_summary:
                                api_used = 'gemini'
                                ai_count += 1
                        
                        if ai_summary:
                            article['summary'] = ai_summary
                            article['extracted_by'] = f'hybrid_{api_used}'
                            print(f"[HYBRID] AI summary generated using {api_used} ({ai_count}/{max_ai_summaries})")
                        else:
                            # AI 요약 실패시 기본 요약 사용
                            article['summary'] = create_basic_summary(article['title'], article['content'])
                            article['extracted_by'] = 'hybrid_fallback'
                            print(f"[HYBRID] Using basic summary for: {article['title'][:50]}...")
                            
                    except Exception as e:
                        print(f"[HYBRID] AI summary error for {article['title'][:30]}: {e}")
                        article['summary'] = create_basic_summary(article['title'], article['content'])
                        article['extracted_by'] = 'hybrid_error'
        except ImportError as e:
            print(f"[HYBRID] AI summary module import error: {e}")
            ai_available = False
    
    if not ai_available:
        print("[HYBRID] Using basic keyword summaries")
        for group, group_articles in articles_by_group.items():
            for article in group_articles:
                article['summary'] = create_basic_summary(article['title'], article['content'])
    
    # Phase 3: 결과 통합 및 최종 처리
    print("\n[HYBRID] Phase 3: Final Processing")
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
            'scraping_method': 'hybrid_ai',
            'execution_type': 'auto'
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
        'scrapingMethod': 'hybrid_ai',
        'executionType': 'auto'
    }
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(latest_info, f, ensure_ascii=False, indent=2)
    
    # 결과 요약
    total_articles = sum(len(group['articles']) for group in consolidated_articles)
    total_sites = len(set(article['site'] for group in consolidated_articles for article in group['articles']))
    
    print(f"\n[HYBRID] === Final Results ===")
    print(f"[HYBRID] Scraping Method: Traditional Links + AI Summary")
    print(f"[HYBRID] Total articles: {total_articles}")
    print(f"[HYBRID] Total sites: {total_sites}")
    print(f"[HYBRID] AI summaries: {sum(1 for group in consolidated_articles for article in group['articles'] if article.get('extracted_by') == 'hybrid_ai')}")
    print(f"[HYBRID] Basic summaries: {sum(1 for group in consolidated_articles for article in group['articles'] if article.get('extracted_by') != 'hybrid_ai')}")
    print(f"[HYBRID] Output: {output_file}")
    
    return output_file

if __name__ == "__main__":
    output_file = scrape_news_hybrid()
    print(f"\n[HYBRID] Scraping completed.")