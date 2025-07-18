#!/usr/bin/env python3
"""
GitHub Actions에서 직접 이메일 테스트
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print('❌ SMTP credentials not found in environment variables')
        exit(1)
    
    print(f'📧 Testing email from: {smtp_user}')
    
    try:
        # 이메일 메시지 작성
        msg = MIMEMultipart()
        msg['Subject'] = '🔔 Singapore News Scraper 이메일 테스트'
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        
        body = """
        <h2>🎉 이메일 시스템 테스트 성공!</h2>
        <p>Singapore News Scraper의 이메일 알림 시스템이 정상 작동합니다.</p>
        <p><b>테스트 시간:</b> {}</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            이 메일은 Singapore News Scraper 시스템에서 자동 발송되었습니다.
        </p>
        """.format(os.popen('date').read().strip())
        
        msg.attach(MIMEText(body, 'html'))
        
        # SMTP 서버 연결
        print('🔌 Connecting to SMTP server...')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print('🔐 Logging in...')
        server.login(smtp_user, smtp_password)
        
        print('📤 Sending email...')
        server.send_message(msg)
        server.quit()
        
        print('✅ Email sent successfully!')
        print('📬 Check your inbox (and spam folder)')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print('\n🔍 Troubleshooting:')
        print('1. Check if 2FA is enabled on Gmail')
        print('2. Verify app password is correct')
        print('3. Check email address')
        exit(1)

if __name__ == "__main__":
    main()