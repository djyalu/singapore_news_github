import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import traceback

def load_settings():
    with open('data/settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def send_email(subject, body, recipients, settings):
    """이메일 전송 함수"""
    try:
        # SMTP 설정
        smtp_settings = settings['monitoring']['email']['smtp']
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not smtp_user or not smtp_password:
            print("SMTP credentials not found in environment variables")
            return False
        
        # 이메일 생성
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = ', '.join(recipients)
        
        # HTML 본문
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #333;">🔔 Singapore News Scraper 알림</h2>
              <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                {body}
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
        
        # 텍스트 본문 (HTML을 지원하지 않는 클라이언트용)
        text_body = body.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # SMTP 서버 연결 및 전송
        if smtp_settings['secure']:
            server = smtplib.SMTP_SSL(smtp_settings['host'], smtp_settings['port'])
        else:
            server = smtplib.SMTP(smtp_settings['host'], smtp_settings['port'])
            server.starttls()
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {recipients}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        traceback.print_exc()
        return False

def check_and_send_notification(status, details):
    """상태에 따라 알림 전송 여부 결정"""
    settings = load_settings()
    monitoring = settings.get('monitoring', {})
    
    if not monitoring.get('enabled', False):
        print("Monitoring is disabled")
        return
    
    email_settings = monitoring.get('email', {})
    if not email_settings.get('enabled', False):
        print("Email notifications are disabled")
        return
    
    recipients = email_settings.get('recipients', [])
    if not recipients:
        print("No email recipients configured")
        return
    
    send_on = email_settings.get('sendOn', {})
    
    # 상태별 알림 여부 확인
    should_send = False
    subject = ""
    body = ""
    
    if status == 'success' and send_on.get('success', False):
        should_send = True
        subject = "✅ 뉴스 스크래핑 성공"
        body = f"""
        <b>스크래핑 결과:</b><br>
        - 수집된 기사: {details.get('article_count', 0)}개<br>
        - 그룹: {details.get('group_count', 0)}개<br>
        - 실행 시간: {details.get('execution_time', 'N/A')}<br>
        - 스크래핑 방법: {details.get('method', 'N/A')}<br><br>
        <b>상세 정보:</b><br>
        {details.get('summary', '상세 정보 없음')}
        """
    
    elif status == 'failure' and send_on.get('failure', True):
        should_send = True
        subject = "❌ 뉴스 스크래핑 실패"
        body = f"""
        <b>오류 정보:</b><br>
        - 오류 유형: {details.get('error_type', 'Unknown')}<br>
        - 오류 메시지: {details.get('error_message', 'No error message')}<br>
        - 실행 시간: {details.get('execution_time', 'N/A')}<br><br>
        <b>스택 트레이스:</b><br>
        <pre>{details.get('stack_trace', 'No stack trace available')}</pre>
        """
    
    elif status == 'no_articles' and send_on.get('noArticles', True):
        should_send = True
        subject = "⚠️ 수집된 기사 없음"
        body = f"""
        <b>경고:</b> 스크래핑은 성공했으나 수집된 기사가 없습니다.<br><br>
        - 확인된 사이트: {details.get('sites_checked', 0)}개<br>
        - 실행 시간: {details.get('execution_time', 'N/A')}<br>
        - 필터 설정: {details.get('filter_settings', 'N/A')}<br><br>
        사이트 구조 변경이나 필터 설정을 확인해주세요.
        """
    
    if should_send:
        send_email(subject, body, recipients, settings)

def create_execution_summary(scraped_file=None, error=None):
    """실행 결과 요약 생성"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
    }
    
    if error:
        summary['status'] = 'failure'
        summary['error_type'] = type(error).__name__
        summary['error_message'] = str(error)
        summary['stack_trace'] = traceback.format_exc()
    elif scraped_file:
        try:
            with open(scraped_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_articles = sum(group.get('article_count', 0) for group in data)
            
            if total_articles == 0:
                summary['status'] = 'no_articles'
                summary['sites_checked'] = len(data)
            else:
                summary['status'] = 'success'
                summary['article_count'] = total_articles
                summary['group_count'] = len(data)
                summary['method'] = data[0].get('scraping_method', 'unknown') if data else 'unknown'
                
                # 그룹별 요약
                group_summary = []
                for group in data:
                    group_summary.append(f"- {group['group']}: {group['article_count']}개 기사")
                summary['summary'] = '<br>'.join(group_summary)
        except Exception as e:
            summary['status'] = 'failure'
            summary['error_type'] = 'SummaryGenerationError'
            summary['error_message'] = str(e)
    else:
        summary['status'] = 'no_articles'
    
    return summary

def save_monitoring_log(summary):
    """모니터링 로그 저장"""
    log_dir = 'data/monitoring'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m')}.json")
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(summary)
    
    # 최근 100개만 유지
    logs = logs[-100:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 테스트 실행
    print("Testing monitoring system...")
    
    # 성공 케이스 테스트
    test_summary = {
        'status': 'success',
        'article_count': 10,
        'group_count': 3,
        'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'method': 'ai',
        'summary': '테스트 요약'
    }
    
    check_and_send_notification('success', test_summary)