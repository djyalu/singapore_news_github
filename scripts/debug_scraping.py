#!/usr/bin/env python3
"""
스크래핑 디버그 스크립트 - 문제 진단용
"""
import os
import sys
import json
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

def test_site_access():
    """주요 뉴스 사이트 접근 테스트"""
    print("🔍 뉴스 사이트 접근성 테스트")
    print("=" * 50)
    
    # 테스트할 사이트들
    test_sites = [
        ("The Straits Times", "https://www.straitstimes.com/global"),
        ("Channel NewsAsia", "https://www.channelnewsasia.com/"),
        ("Yahoo Singapore", "https://sg.news.yahoo.com"),
        ("AsiaOne", "https://www.asiaone.com/singapore"),
        ("Mothership", "https://mothership.sg")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    results = []
    for name, url in test_sites:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status = response.status_code
            
            if status == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 기사 링크 찾기
                links = soup.find_all('a', href=True)
                article_links = [l for l in links if any(kw in l.get('href', '') for kw in ['article', 'news', 'story', '/'])]
                
                print(f"✅ {name}: 접근 성공 (링크 {len(article_links)}개 발견)")
                results.append({'site': name, 'status': 'success', 'links': len(article_links)})
            else:
                print(f"⚠️ {name}: HTTP {status}")
                results.append({'site': name, 'status': f'HTTP {status}', 'links': 0})
                
        except requests.exceptions.Timeout:
            print(f"❌ {name}: 타임아웃")
            results.append({'site': name, 'status': 'timeout', 'links': 0})
        except Exception as e:
            print(f"❌ {name}: 오류 - {str(e)[:50]}")
            results.append({'site': name, 'status': 'error', 'links': 0})
    
    return results

def check_api_status():
    """API 키 상태 확인"""
    print("\n📊 API 상태 확인")
    print("=" * 50)
    
    # 환경변수 확인
    cohere_key = os.getenv('COHERE_API_KEY')
    gemini_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    
    if cohere_key:
        print("✅ Cohere API 키 설정됨")
    else:
        print("⚠️ Cohere API 키 없음")
    
    if gemini_key:
        print("✅ Gemini API 키 설정됨")
    else:
        print("⚠️ Gemini API 키 없음")
    
    # 설정 파일 확인
    if os.path.exists('data/settings.json'):
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            method = settings.get('scrapingMethod', 'unknown')
            print(f"📝 스크래핑 방법: {method}")
            
            if method == 'hybrid':
                hybrid_config = settings.get('scrapingMethodOptions', {}).get('hybrid', {})
                print(f"   - API 우선순위: {hybrid_config.get('apiPriority', [])}")

def check_recent_errors():
    """최근 오류 패턴 확인"""
    print("\n🔴 최근 실행 문제 분석")
    print("=" * 50)
    
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    # 최근 스크래핑 파일 확인
    scraped_dir = 'data/scraped'
    recent_files = []
    
    if os.path.exists(scraped_dir):
        for file in sorted(os.listdir(scraped_dir), reverse=True)[:5]:
            if file.startswith('news_'):
                file_path = os.path.join(scraped_dir, file)
                size = os.path.getsize(file_path)
                recent_files.append((file, size))
    
    if recent_files:
        print("최근 스크래핑 파일:")
        for file, size in recent_files:
            size_kb = size / 1024
            status = "✅" if size_kb > 1 else "⚠️"
            print(f"  {status} {file}: {size_kb:.1f} KB")
    else:
        print("❌ 최근 스크래핑 파일 없음")
    
    # 마지막 성공 시점 확인
    if os.path.exists('data/latest.json'):
        with open('data/latest.json', 'r') as f:
            latest = json.load(f)
            last_update = datetime.fromisoformat(latest['lastUpdated'])
            days_ago = (now - last_update).days
            print(f"\n마지막 업데이트: {days_ago}일 전 ({latest['lastUpdated'][:10]})")

def suggest_fixes():
    """해결 방안 제시"""
    print("\n💡 권장 해결 방법")
    print("=" * 50)
    
    print("""
1. 즉시 수동 테스트:
   python3 scripts/scraper.py
   
2. 스크래핑 방법 변경 (settings.json):
   - 'hybrid' → 'traditional' (API 문제 시)
   - 'traditional' → 'hybrid' (사이트 차단 시)
   
3. GitHub Actions 로그 확인:
   - https://github.com/djyalu/singapore_news_github/actions
   - 최근 실행 클릭 → 상세 로그 확인
   
4. API 키 재설정:
   - GitHub Secrets에서 API 키 업데이트
   - COHERE_API_KEY, GOOGLE_GEMINI_API_KEY
    """)

if __name__ == "__main__":
    print("🔧 Singapore News Scraper 디버그")
    print("=" * 50)
    
    # 각 테스트 실행
    site_results = test_site_access()
    check_api_status()
    check_recent_errors()
    suggest_fixes()
    
    # 결과 요약
    print("\n📈 진단 요약")
    print("=" * 50)
    
    working_sites = sum(1 for r in site_results if r['status'] == 'success')
    total_sites = len(site_results)
    
    print(f"사이트 접근성: {working_sites}/{total_sites} 정상")
    
    if working_sites < total_sites / 2:
        print("⚠️ 대부분의 사이트 접근 실패 - 네트워크 또는 봇 차단 문제")
    elif working_sites == total_sites:
        print("✅ 모든 사이트 접근 가능 - 스크래핑 로직 점검 필요")