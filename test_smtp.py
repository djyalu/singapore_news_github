import os
import smtplib
from email.mime.text import MIMEText

# 환경변수 설정 (테스트용)
# 실제 값으로 교체하세요
smtp_user = "your-email@gmail.com"  # 여기에 이메일 주소
smtp_password = "your-app-password"  # 여기에 앱 비밀번호

try:
    # SMTP 연결 테스트
    print(f"Connecting to SMTP server...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    print(f"Logging in as {smtp_user}...")
    server.login(smtp_user, smtp_password)
    
    # 테스트 메일 발송
    msg = MIMEText("테스트 메일입니다.")
    msg['Subject'] = 'Singapore News Scraper 테스트'
    msg['From'] = smtp_user
    msg['To'] = smtp_user
    
    print("Sending email...")
    server.send_message(msg)
    server.quit()
    
    print("✅ Email sent successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n확인사항:")
    print("1. 2단계 인증이 활성화되어 있나요?")
    print("2. 앱 비밀번호를 사용하고 있나요?")
    print("3. 이메일 주소가 정확한가요?")