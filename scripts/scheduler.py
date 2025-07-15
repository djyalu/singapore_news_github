#!/usr/bin/env python3
"""
Singapore News WhatsApp Scheduler
한국시간 매일 오전 8시에 스크랩된 기사를 WhatsApp으로 전송
"""

import schedule
import time
import subprocess
import os
import sys
from datetime import datetime
import pytz

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def send_daily_news():
    """매일 오전 8시에 실행되는 함수"""
    print(f"[{datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}] Starting daily news sending...")
    
    try:
        # 먼저 스크래핑 실행
        scraper_result = subprocess.run([
            sys.executable, 'scripts/scraper.py'
        ], capture_output=True, text=True, cwd='/mnt/d/projects/singapore_news_github')
        
        if scraper_result.returncode != 0:
            print(f"Scraper failed: {scraper_result.stderr}")
            return
        
        print("Scraping completed successfully")
        
        # WhatsApp 전송 실행
        whatsapp_result = subprocess.run([
            sys.executable, 'scripts/send_whatsapp.py'
        ], capture_output=True, text=True, cwd='/mnt/d/projects/singapore_news_github')
        
        if whatsapp_result.returncode == 0:
            print("WhatsApp message sent successfully")
            print(whatsapp_result.stdout)
        else:
            print(f"WhatsApp sending failed: {whatsapp_result.stderr}")
            
    except Exception as e:
        print(f"Error in daily news sending: {e}")

def main():
    """메인 스케줄러 함수"""
    print("Singapore News WhatsApp Scheduler starting...")
    print(f"Current time: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}")
    print("Scheduling daily news sending at 08:00 KST...")
    
    # 한국시간 오전 8시에 스케줄 등록
    schedule.every().day.at("08:00").do(send_daily_news)
    
    # 테스트용 - 즉시 실행하고 싶다면 주석 해제
    # send_daily_news()
    
    print("Scheduler is running... Press Ctrl+C to stop")
    
    try:
        while True:
            # 한국시간 기준으로 스케줄 체크
            current_time = datetime.now(KST)
            schedule.run_pending()
            
            # 다음 실행 시간 표시 (1시간마다)
            if current_time.minute == 0:
                next_run = schedule.next_run()
                if next_run:
                    next_run_kst = next_run.astimezone(KST)
                    print(f"[{current_time.strftime('%H:%M')}] Next run: {next_run_kst.strftime('%Y-%m-%d %H:%M:%S KST')}")
            
            time.sleep(60)  # 1분마다 체크
            
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()