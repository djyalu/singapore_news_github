#!/usr/bin/env python3
"""
WAHA (WhatsApp HTTP API)를 사용한 메시지 전송
- 무료 오픈소스
- REST API 제공
- Docker 또는 클라우드 호스팅 필요
"""

import os
import json
import requests
from datetime import datetime

# WAHA API 설정
WAHA_API_URL = os.environ.get('WAHA_API_URL', 'http://localhost:3000')  # WAHA 서버 주소
WAHA_SESSION = os.environ.get('WAHA_SESSION', 'default')  # 세션 이름

def check_waha_status():
    """WAHA 서버 상태 확인"""
    try:
        response = requests.get(f"{WAHA_API_URL}/api/sessions/{WAHA_SESSION}")
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'WORKING'
        return False
    except:
        return False

def send_whatsapp_message(chat_id, message):
    """WAHA API를 통한 WhatsApp 메시지 전송"""
    
    if not check_waha_status():
        print("❌ WAHA 서버가 응답하지 않거나 세션이 활성화되지 않았습니다.")
        print(f"   서버 주소: {WAHA_API_URL}")
        print(f"   세션: {WAHA_SESSION}")
        return False
    
    # 메시지 전송 API 호출
    url = f"{WAHA_API_URL}/api/sendText"
    
    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code in [200, 201]:
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
        
    message = f"📰 *Singapore News Update*\n"
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
    
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    message += "🤖 _Singapore News Scraper (WAHA)_"
    
    return message

def main():
    print("=" * 50)
    print("📱 Singapore News WhatsApp 전송 (WAHA)")
    print("=" * 50)
    
    # WAHA 상태 확인
    if not check_waha_status():
        print("\n💡 WAHA 설치 방법:")
        print("1. Docker 설치 후 실행:")
        print("   docker run -p 3000:3000 devlikeapro/waha")
        print("2. 브라우저에서 http://localhost:3000 접속")
        print("3. QR 코드로 WhatsApp 연결")
        print("4. 환경변수 설정:")
        print("   export WAHA_API_URL=http://your-server:3000")
        return
    
    # 설정 로드
    settings = load_settings()
    if not settings:
        print("❌ 설정을 로드할 수 없습니다.")
        return
    
    # WhatsApp 채널 확인
    whatsapp_channel = settings.get('whatsappChannel')
    if not whatsapp_channel:
        print("❌ WhatsApp 채널이 설정되지 않았습니다.")
        return
    
    print(f"📱 대상 채널: {whatsapp_channel}")
    
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
    success = send_whatsapp_message(whatsapp_channel, message)
    
    # 발송 이력 저장
    status = "success" if success else "failed"
    header = f"뉴스 {len(articles)}개 발송"
    
    history_entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "channel": whatsapp_channel,
        "status": status,
        "header": header,
        "message_preview": message[:300] + "...",
        "message_length": len(message),
        "article_count": len(articles),
        "api": "waha"  # API 제공자 표시
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