#!/usr/bin/env python3
"""
GitHub Actions 워크플로우 모니터링 및 알림 스크립트
"""
import os
import json
from datetime import datetime, timedelta
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_workflow_health():
    """워크플로우 건강 상태 확인 및 알림"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    # 설정 파일 로드
    with open('data/settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    # latest.json 확인
    with open('data/latest.json', 'r', encoding='utf-8') as f:
        latest = json.load(f)
    
    last_updated = datetime.fromisoformat(latest['lastUpdated'])
    days_since_update = (now - last_updated).days
    
    # 문제 감지
    issues = []
    
    if days_since_update > 1:
        issues.append(f"⚠️ {days_since_update}일 동안 스크래핑이 실행되지 않았습니다.")
    
    # 오늘 스크래핑 파일 확인
    today_str = now.strftime("%Y%m%d")
    today_files = []
    scraped_dir = 'data/scraped'
    
    if os.path.exists(scraped_dir):
        for file in os.listdir(scraped_dir):
            if file.startswith(f"news_{today_str}"):
                today_files.append(file)
    
    if not today_files and now.hour > 8:  # 오전 8시 이후인데 파일이 없으면
        issues.append(f"❌ 오늘({now.strftime('%Y-%m-%d')}) 스크래핑이 실행되지 않았습니다.")
    
    # 워크플로우 실행 로그 확인
    workflow_log = 'workflow_status.log'
    if os.path.exists(workflow_log):
        with open(workflow_log, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                print(f"마지막 워크플로우 상태: {last_line}")
    
    # 문제가 있으면 알림
    if issues:
        print("\n🚨 문제 감지:")
        for issue in issues:
            print(issue)
        
        # 이메일 알림 (설정이 활성화된 경우)
        if settings.get('monitoring', {}).get('email', {}).get('enabled'):
            send_alert_email(issues, settings)
        
        return False
    else:
        print("✅ 워크플로우가 정상적으로 작동 중입니다.")
        return True

def send_alert_email(issues, settings):
    """문제 발생 시 이메일 알림 전송"""
    try:
        email_config = settings['monitoring']['email']
        recipients = email_config.get('recipients', ['go41@naver.com'])
        
        # 이메일 내용 구성
        subject = "⚠️ Singapore News Scraper 워크플로우 문제 감지"
        body = "다음 문제가 감지되었습니다:\n\n"
        body += "\n".join(issues)
        body += "\n\n조치사항:\n"
        body += "1. GitHub Actions 페이지 확인\n"
        body += "2. 워크플로우 수동 실행\n"
        body += "3. 필요시 워크플로우 재활성화"
        
        print(f"📧 알림 이메일 전송 중: {recipients}")
        # 실제 이메일 전송 로직은 SMTP 설정 필요
        
    except Exception as e:
        print(f"이메일 전송 실패: {e}")

if __name__ == "__main__":
    check_workflow_health()