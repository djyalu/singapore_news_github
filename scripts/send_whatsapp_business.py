#!/usr/bin/env python3
"""
WhatsApp Business API를 사용한 메시지 전송
무료: 1000건/월
현재 아키텍처와 100% 호환
"""

import os
import json
import requests
from datetime import datetime

# WhatsApp Business API 설정
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_BUSINESS_TOKEN')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID')
WHATSAPP_API_VERSION = 'v17.0'

def send_whatsapp_message(to_number, message):
    """WhatsApp Business API를 통한 메시지 전송"""
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        print("❌ WhatsApp Business API 인증 정보가 없습니다.")
        print("\n📝 설정 방법:")
        print("1. https://developers.facebook.com 접속")
        print("2. 'My Apps' → 'Create App' → 'Business' 선택")
        print("3. WhatsApp 제품 추가")
        print("4. 전화번호 추가 및 인증")
        print("5. 영구 토큰 생성")
        print("6. GitHub Secrets에 추가:")
        print("   - WHATSAPP_BUSINESS_TOKEN")
        print("   - WHATSAPP_PHONE_ID")
        return False
    
    # API 엔드포인트
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_ID}/messages"
    
    # 헤더
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 그룹 ID 처리
    if '@g.us' in to_number:
        # 그룹은 다른 방식으로 처리 필요
        print("⚠️  그룹 메시지는 WhatsApp Business API에서 제한적입니다.")
        # 그룹 대신 개별 번호로 전송하도록 수정 필요
        return False
    
    # 페이로드
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")
        return False

def load_settings():
    """설정 파일 로드"""
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 로드 실패: {e}")
        return None

def load_latest_news():
    """최신 스크랩된 뉴스 데이터 로드"""
    try:
        with open('data/latest.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def format_message(articles):
    """뉴스 기사를 WhatsApp 메시지 형식으로 변환"""
    if not articles:
        return None
        
    message = f"📰 Singapore News Update\n"
    message += f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 그룹별로 기사 정리
    groups = {}
    for article in articles:
        group = article.get('group', 'News')
        if group not in groups:
            groups[group] = []
        groups[group].append(article)
    
    message += f"📊 오늘의 주요 뉴스: {len(groups)}개 그룹, 총 {len(articles)}개 기사\n\n"
    
    for group_name, group_articles in groups.items():
        message += f"【 {group_name} 】\n"
        sources = list(set([a.get('source', '') for a in group_articles]))
        message += f"📍 출처: {', '.join(sources)}\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, article in enumerate(group_articles, 1):
            title = article.get('title', '제목 없음')
            korean_summary = article.get('korean_summary', '요약 없음')
            
            message += f"{idx}. 📰 {article.get('summary_category', '일반 뉴스')}\n"
            message += f"📝 {title[:50]}...\n" if len(title) > 50 else f"📝 {title}\n"
            message += f"🔍 {korean_summary}\n\n"
            
            # WhatsApp Business API는 메시지 길이 제한이 있음
            if len(message) > 3000:
                message += "\n... (더 많은 뉴스는 웹사이트에서 확인)"
                break
    
    message += "\n━━━━━━━━━━━━━━━━━━━━\n"
    message += "🤖 Singapore News Scraper"
    
    return message

def main():
    print("=" * 50)
    print("📱 Singapore News WhatsApp 전송")
    print("   (WhatsApp Business API)")
    print("=" * 50)
    
    # 설정 로드
    settings = load_settings()
    if not settings:
        print("❌ 설정을 로드할 수 없습니다.")
        return
    
    # 전화번호 설정 (그룹 대신 개별 번호 사용 필요)
    # 예: +821234567890
    to_number = os.environ.get('WHATSAPP_TO_NUMBER')
    if not to_number:
        print("❌ 수신자 번호가 설정되지 않았습니다.")
        print("   환경변수 WHATSAPP_TO_NUMBER를 설정하세요.")
        print("   예: +821234567890")
        return
    
    print(f"📱 대상 번호: {to_number}")
    
    # 최신 뉴스 로드
    news_data = load_latest_news()
    if not news_data or not news_data.get('articles'):
        print("❌ 발송할 뉴스가 없습니다.")
        return
    
    articles = news_data['articles']
    print(f"📰 발송할 기사: {len(articles)}개")
    
    # 메시지 포맷팅
    message = format_message(articles)
    if not message:
        print("❌ 메시지 생성 실패")
        return
    
    print(f"📝 메시지 길이: {len(message)}자")
    
    # WhatsApp 전송
    success = send_whatsapp_message(to_number, message)
    
    # 발송 이력 저장
    status = "success" if success else "failed"
    header = f"뉴스 {len(articles)}개 발송"
    
    history_entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "channel": to_number,
        "status": status,
        "header": header,
        "message_preview": message[:300] + "...",
        "message_length": len(message),
        "article_count": len(articles),
        "api": "whatsapp-business"
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
    
    if success:
        print("\n✅ WhatsApp 메시지 전송 완료!")
    else:
        print("\n❌ WhatsApp 메시지 전송 실패")

if __name__ == "__main__":
    main()