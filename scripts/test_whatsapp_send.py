#!/usr/bin/env python3
"""
WhatsApp 전송 테스트 및 디버깅 스크립트
"""
import os
import json
import sys
from datetime import datetime
import pytz

def test_whatsapp_conditions():
    """WhatsApp 전송 조건 테스트"""
    print("🔍 WhatsApp 전송 조건 테스트")
    print("=" * 60)
    
    # 1. latest.json 확인
    print("\n1️⃣ latest.json 파일 확인:")
    if os.path.exists('data/latest.json'):
        with open('data/latest.json', 'r', encoding='utf-8') as f:
            latest = json.load(f)
            print(f"   ✅ latest.json 존재")
            print(f"   - 최신 파일: {latest.get('latestFile')}")
            print(f"   - 마지막 업데이트: {latest.get('lastUpdated')}")
            latest_file = latest.get('latestFile')
    else:
        print(f"   ❌ latest.json 없음 → WhatsApp 전송 안 됨")
        return False
    
    # 2. 스크래핑 파일 확인
    print("\n2️⃣ 스크래핑 파일 확인:")
    if latest_file:
        scraped_path = f'data/scraped/{latest_file}'
        if os.path.exists(scraped_path):
            print(f"   ✅ {latest_file} 파일 존재")
            
            with open(scraped_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 기사 수 계산
            article_count = 0
            if isinstance(data, list):
                for group in data:
                    if 'articles' in group:
                        article_count += len(group['articles'])
                    article_count += group.get('article_count', 0)
            
            print(f"   - 기사 수: {article_count}개")
            
            if article_count == 0:
                print(f"   ⚠️ 기사가 0개 → 전송할 내용 없음")
            else:
                print(f"   ✅ 기사 {article_count}개 → 전송 가능")
        else:
            print(f"   ❌ {latest_file} 파일 없음")
            return False
    
    # 3. Green API 환경변수 확인
    print("\n3️⃣ Green API 환경변수:")
    instance_id = os.environ.get('GREEN_API_INSTANCE_ID')
    api_token = os.environ.get('GREEN_API_TOKEN')
    
    if instance_id:
        print(f"   ✅ GREEN_API_INSTANCE_ID 설정됨")
    else:
        print(f"   ❌ GREEN_API_INSTANCE_ID 없음 (GitHub Actions에서만 설정)")
    
    if api_token:
        print(f"   ✅ GREEN_API_TOKEN 설정됨")
    else:
        print(f"   ❌ GREEN_API_TOKEN 없음 (GitHub Actions에서만 설정)")
    
    # 4. 설정 파일 확인
    print("\n4️⃣ settings.json 설정:")
    if os.path.exists('data/settings.json'):
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        send_channel = settings.get('sendChannel')
        whatsapp_channel = settings.get('whatsappChannel')
        scraping_method = settings.get('scrapingMethod')
        
        print(f"   - 전송 채널: {send_channel}")
        print(f"   - WhatsApp 채널: {whatsapp_channel}")
        print(f"   - 스크래핑 방법: {scraping_method}")
        
        if send_channel != 'whatsapp':
            print(f"   ❌ WhatsApp 전송 비활성화")
            return False
        else:
            print(f"   ✅ WhatsApp 전송 활성화")
    
    # 5. 최근 전송 기록 분석
    print("\n5️⃣ 최근 WhatsApp 전송 실패 원인 추정:")
    
    # 8월 19-20일 데이터 확인
    test_dates = ['20250819', '20250820', '20250821']
    for date_str in test_dates:
        files = []
        scraped_dir = 'data/scraped'
        if os.path.exists(scraped_dir):
            for file in os.listdir(scraped_dir):
                if file.startswith(f'news_{date_str}'):
                    files.append(file)
        
        if files:
            print(f"\n   📅 {date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}:")
            for file in files:
                file_path = os.path.join(scraped_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                article_count = 0
                if isinstance(data, list):
                    for group in data:
                        if 'articles' in group:
                            article_count += len(group['articles'])
                
                print(f"      - {file}: {article_count}개 기사")
                
                if article_count == 0:
                    print(f"        → ❌ 기사 0개로 전송 실패 가능")
                elif article_count < 2:
                    print(f"        → ⚠️ 기사 너무 적음 (하지만 전송은 되어야 함)")
                else:
                    print(f"        → ✅ 정상 전송 되어야 함")

if __name__ == "__main__":
    test_whatsapp_conditions()