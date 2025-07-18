#!/usr/bin/env python3
"""
로컬에서 이메일 테스트 (환경변수 없이)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass

def main():
    print("📧 Singapore News Scraper 이메일 테스트")
    print("=" * 50)
    
    # 사용자 입력
    smtp_user = input("Gmail 주소를 입력하세요: ")
    smtp_password = getpass.getpass("Gmail 앱 비밀번호를 입력하세요: ")
    
    if not smtp_user or not smtp_password:
        print('❌ 이메일 주소와 비밀번호를 모두 입력해주세요.')
        return
    
    print(f'\n📧 {smtp_user}로 테스트 메일 발송 중...')
    
    try:
        # 이메일 메시지 작성
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔔 Singapore News Scraper 이메일 테스트'
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        
        # HTML 본문
        html_body = """
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #333;">🎉 이메일 시스템 테스트 성공!</h2>
              <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p>Singapore News Scraper의 이메일 알림 시스템이 정상 작동합니다.</p>
                <p><b>테스트 완료:</b> SMTP 연결 및 이메일 발송</p>
                <p><b>다음 단계:</b> 대시보드에서 모니터링 설정 완료</p>
              </div>
              <hr style="margin: 20px 0;">
              <p style="color: #666; font-size: 12px;">
                이 메일은 Singapore News Scraper 시스템에서 자동 발송되었습니다.<br>
                설정 변경은 <a href="https://djyalu.github.io/singapore_news_github/">대시보드</a>에서 가능합니다.
              </p>
            </div>
          </body>
        </html>
        """
        
        # 텍스트 본문 (백업용)
        text_body = """
🎉 이메일 시스템 테스트 성공!

Singapore News Scraper의 이메일 알림 시스템이 정상 작동합니다.

테스트 완료: SMTP 연결 및 이메일 발송
다음 단계: 대시보드에서 모니터링 설정 완료

이 메일은 Singapore News Scraper 시스템에서 자동 발송되었습니다.
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # SMTP 서버 연결
        print('🔌 SMTP 서버 연결 중...')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print('🔐 로그인 중...')
        server.login(smtp_user, smtp_password)
        
        print('📤 이메일 발송 중...')
        server.send_message(msg)
        server.quit()
        
        print('✅ 이메일이 성공적으로 발송되었습니다!')
        print('📬 받은편지함을 확인해보세요 (스팸 폴더도 확인)')
        print('\n🎯 다음 단계:')
        print('1. 대시보드에서 모니터링 활성화')
        print('2. 수신자 이메일 설정')
        print('3. 알림 조건 선택')
        print('4. GitHub Actions 스크래핑 실행')
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
        print('\n🔍 문제 해결 방법:')
        print('1. Gmail 2단계 인증이 활성화되어 있는지 확인')
        print('2. 앱 비밀번호를 올바르게 입력했는지 확인')
        print('3. 이메일 주소가 정확한지 확인')
        print('4. Gmail 설정에서 "보안 수준이 낮은 앱 액세스" 확인')

if __name__ == "__main__":
    main()