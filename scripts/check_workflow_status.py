#!/usr/bin/env python3
"""
GitHub Actions 워크플로우 실행 상태 확인 스크립트
"""
import os
import json
from datetime import datetime, timedelta
import pytz

def check_recent_scraping():
    """최근 스크래핑 파일 확인"""
    kst = pytz.timezone('Asia/Seoul')
    scraped_dir = 'data/scraped'
    
    # 최근 5일간의 날짜 확인
    today = datetime.now(kst)
    dates_to_check = []
    
    for i in range(5):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y%m%d")
        dates_to_check.append(date_str)
    
    print("📅 최근 5일간 스크래핑 파일 확인:")
    print("-" * 50)
    
    for date_str in dates_to_check:
        # 해당 날짜의 파일 찾기
        files_found = []
        if os.path.exists(scraped_dir):
            for file in os.listdir(scraped_dir):
                if file.startswith(f"news_{date_str}"):
                    files_found.append(file)
        
        date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        if files_found:
            print(f"✅ {date_formatted}: {len(files_found)}개 파일")
            for file in files_found[:3]:  # 최대 3개만 표시
                print(f"   - {file}")
        else:
            print(f"❌ {date_formatted}: 스크래핑 없음")
    
    # latest.json 확인
    print("\n📊 Latest.json 상태:")
    print("-" * 50)
    if os.path.exists('data/latest.json'):
        with open('data/latest.json', 'r', encoding='utf-8') as f:
            latest = json.load(f)
            last_updated = datetime.fromisoformat(latest['lastUpdated'])
            days_ago = (today - last_updated).days
            print(f"최종 업데이트: {latest['lastUpdated']}")
            print(f"최신 파일: {latest['latestFile']}")
            print(f"경과 일수: {days_ago}일 전")
            
            if days_ago > 2:
                print(f"⚠️ 경고: {days_ago}일 동안 업데이트 없음!")
    
    # WhatsApp 전송 기록 확인
    print("\n📱 WhatsApp 전송 기록:")
    print("-" * 50)
    history_file = f'data/history/{today.strftime("%Y%m")}.json'
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        # 최근 5일간의 전송 기록 확인
        for date_str in dates_to_check[:5]:
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            found = False
            for record in history:
                record_date = record['timestamp'][:10]
                if record_date == date_formatted:
                    print(f"✅ {date_formatted}: {record['status']} - {record['header']}")
                    found = True
                    break
            if not found:
                print(f"❌ {date_formatted}: 전송 기록 없음")

if __name__ == "__main__":
    check_recent_scraping()