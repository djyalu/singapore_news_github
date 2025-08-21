#!/usr/bin/env python3
"""
스크래핑 패턴 분석 - 왜 특정 날짜에만 전송이 안 되는지 확인
"""
import os
import json
from datetime import datetime
import pytz

def analyze_scraping_history():
    """8월 스크래핑 기록 분석"""
    kst = pytz.timezone('Asia/Seoul')
    scraped_dir = 'data/scraped'
    
    print("📊 8월 스크래핑 기록 분석")
    print("=" * 60)
    
    # 8월 데이터 수집
    august_data = {}
    
    if os.path.exists(scraped_dir):
        for file in os.listdir(scraped_dir):
            if file.startswith('news_202508'):
                file_path = os.path.join(scraped_dir, file)
                date_str = file[5:13]  # 20250801 형식
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 기사 수 계산
                total_articles = 0
                for group in data:
                    if 'articles' in group:
                        total_articles += len(group['articles'])
                
                if date_str not in august_data:
                    august_data[date_str] = []
                
                august_data[date_str].append({
                    'file': file,
                    'articles': total_articles,
                    'size': os.path.getsize(file_path)
                })
    
    # WhatsApp 전송 기록 로드
    send_history = []
    history_file = 'data/history/202508.json'
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            send_history = json.load(f)
    
    # 날짜별 분석
    print("\n📅 날짜별 스크래핑 및 전송 상황:")
    print("-" * 60)
    print("날짜        | 스크래핑 | 기사수 | WhatsApp | 상태")
    print("-" * 60)
    
    for day in range(1, 22):  # 8월 1일부터 21일까지
        date_str = f"202508{day:02d}"
        date_formatted = f"2025-08-{day:02d}"
        
        # 스크래핑 데이터 확인
        scraped = "✅" if date_str in august_data else "❌"
        article_count = 0
        if date_str in august_data:
            for item in august_data[date_str]:
                article_count += item['articles']
        
        # WhatsApp 전송 확인
        whatsapp_sent = "❌"
        for record in send_history:
            if record['timestamp'].startswith(date_formatted):
                whatsapp_sent = "✅"
                break
        
        # 상태 판단
        if scraped == "✅" and whatsapp_sent == "✅":
            status = "정상"
        elif scraped == "✅" and whatsapp_sent == "❌":
            status = "⚠️ 전송 실패"
        elif scraped == "❌" and whatsapp_sent == "❌":
            status = "스크래핑 실패"
        else:
            status = "?"
        
        if scraped == "✅" or day <= 21:
            print(f"{date_formatted} | {scraped:^8} | {article_count:^6} | {whatsapp_sent:^8} | {status}")
    
    # 패턴 분석
    print("\n🔍 패턴 분석:")
    print("-" * 60)
    
    # 전송 실패한 날짜 찾기
    failed_dates = []
    for date_str in august_data:
        date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        sent = False
        for record in send_history:
            if record['timestamp'].startswith(date_formatted):
                sent = True
                break
        if not sent:
            failed_dates.append(date_formatted)
    
    if failed_dates:
        print(f"⚠️ 스크래핑은 성공했지만 WhatsApp 전송 실패한 날짜:")
        for date in failed_dates:
            print(f"   - {date}")
            # 해당 날짜 데이터 확인
            date_str = date.replace('-', '')
            if date_str in august_data:
                for item in august_data[date_str]:
                    print(f"     파일: {item['file']} ({item['articles']}개 기사, {item['size']/1024:.1f}KB)")
    
    # 최소 기사 수 확인
    print("\n📈 기사 수 통계:")
    article_counts = []
    for date_str in august_data:
        for item in august_data[date_str]:
            article_counts.append(item['articles'])
    
    if article_counts:
        print(f"평균: {sum(article_counts)/len(article_counts):.1f}개")
        print(f"최소: {min(article_counts)}개")
        print(f"최대: {max(article_counts)}개")
        
        # 최소 기사 수 확인
        if min(article_counts) == 0:
            print("\n⚠️ 기사가 0개인 경우가 있어 WhatsApp 전송이 안 되었을 가능성이 있습니다.")

if __name__ == "__main__":
    analyze_scraping_history()