#!/usr/bin/env python3
"""
이메일 테스트 스크립트
사용법: python test_email_simple.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    # 여기에 실제 값을 입력하세요
    smtp_user = input("Gmail 주소를 입력하세요: ")
    smtp_password = input("앱 비밀번호를 입력하세요: ")
    
    print(f"\n📧 이메일 테스트 시작...")
    print(f"발신자: {smtp_user}")
    
    try:
        # 이메일 메시지 작성
        msg = MIMEMultipart()
        msg['Subject'] = '🔔 Singapore News Scraper 테스트'
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        
        body = """
        이메일 시스템 테스트입니다.
        
        이 메일을 받으셨다면 SMTP 설정이 정상입니다!
        
        Singapore News Scraper
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # SMTP 서버 연결
        print("🔌 SMTP 서버에 연결 중...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 로그인 중...")
        server.login(smtp_user, smtp_password)
        
        print("📤 이메일 발송 중...")
        server.send_message(msg)
        server.quit()
        
        print("✅ 이메일이 성공적으로 발송되었습니다!")
        print("📬 받은편지함을 확인해보세요 (스팸 폴더도 확인)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n🔍 문제 해결 방법:")
        print("1. Gmail 2단계 인증이 활성화되어 있는지 확인")
        print("2. 앱 비밀번호를 올바르게 입력했는지 확인")
        print("3. 이메일 주소가 정확한지 확인")

if __name__ == "__main__":
    test_email()