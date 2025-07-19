#!/usr/bin/env python3
"""
Whapi 서비스 중단 시 이메일로 뉴스 전송
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_latest_news():
    """최신 스크랩된 뉴스 데이터 로드"""
    try:
        with open('data/latest.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def create_email_content(news_data):
    """이메일용 HTML 콘텐츠 생성"""
    if not news_data or not news_data.get('articles'):
        return None, "뉴스 없음"
    
    articles = news_data['articles']
    article_count = len(articles)
    
    # 그룹별로 기사 정리
    groups = {}
    for article in articles:
        group = article.get('group', 'News')
        if group not in groups:
            groups[group] = []
        groups[group].append(article)
    
    # HTML 이메일 생성
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
            <h1 style="color: #333;">📰 Singapore News Update</h1>
            <p style="color: #666;">{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            <p style="color: #666;">총 {len(groups)}개 그룹, {article_count}개 기사</p>
        </div>
    """
    
    for group_name, group_articles in groups.items():
        sources = list(set([a.get('source', '') for a in group_articles]))
        sources_str = ', '.join(sources)
        
        html += f"""
        <div style="margin-top: 30px;">
            <h2 style="color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px;">
                【 {group_name} 】
            </h2>
            <p style="color: #999; font-size: 14px;">📍 출처: {sources_str}</p>
        """
        
        for idx, article in enumerate(group_articles, 1):
            title = article.get('title', '제목 없음')
            summary = article.get('korean_summary', '')
            link = article.get('link', '#')
            
            # 한국어 요약 정리
            summary_html = summary.replace('\n', '<br>')
            
            html += f"""
            <div style="background-color: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #333; margin-top: 0;">{idx}. {title}</h3>
                <div style="color: #666; line-height: 1.6;">
                    {summary_html}
                </div>
                <a href="{link}" style="color: #0066cc; text-decoration: none; display: inline-block; margin-top: 10px;">
                    🔗 원문 보기
                </a>
            </div>
            """
        
        html += "</div>"
    
    html += """
        <div style="margin-top: 40px; padding: 20px; background-color: #f5f5f5; border-radius: 10px; text-align: center; color: #999;">
            <p>🤖 Singapore News Scraper</p>
            <p style="font-size: 12px;">Whapi 서비스 중단으로 임시 이메일 발송</p>
        </div>
    </body>
    </html>
    """
    
    return html, f"뉴스 {article_count}개"

def send_email(html_content, header):
    """이메일 발송"""
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ SMTP 설정이 없습니다.")
        return False
    
    # 설정에서 수신자 목록 가져오기
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            recipients = settings.get('monitoring', {}).get('email', {}).get('recipients', [])
            
            if not recipients:
                recipients = [smtp_user]  # 기본값: 발신자에게 전송
    except:
        recipients = [smtp_user]
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'📰 Singapore News - {header}'
        msg['From'] = smtp_user
        msg['To'] = ', '.join(recipients)
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 이메일 발송 성공: {', '.join(recipients)}")
        return True
        
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False

def main():
    print("📧 Singapore News 이메일 발송 시작...")
    print("⚠️  Whapi 서비스 중단으로 임시 이메일 발송")
    
    # 최신 뉴스 로드
    news_data = load_latest_news()
    if not news_data:
        print("❌ 뉴스 데이터가 없습니다.")
        return
    
    # 이메일 콘텐츠 생성
    html_content, header = create_email_content(news_data)
    if not html_content:
        print("❌ 발송할 뉴스가 없습니다.")
        return
    
    # 이메일 발송
    success = send_email(html_content, header)
    
    # 발송 이력 저장
    if success:
        history_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "channel": "email",
            "status": "success",
            "header": header,
            "message_preview": "이메일로 발송됨",
            "message_length": len(html_content),
            "article_count": len(news_data.get('articles', []))
        }
        
        # 이력 파일 업데이트
        month_str = datetime.now().strftime("%Y%m")
        history_file = f'data/history/{month_str}.json'
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
        
        history.append(history_entry)
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        print("✅ 발송 이력 저장 완료")

if __name__ == "__main__":
    main()