#!/usr/bin/env python3
"""
Green API를 사용한 WhatsApp 메시지 전송
- 월 $9부터 시작 (300 메시지)
- REST API 제공
- 현재 아키텍처와 100% 호환
"""

import json
import os
import glob
from datetime import datetime
import requests
import time

def load_settings():
    """설정 파일 로드"""
    with open('data/settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_latest_scraped_file():
    """최신 스크랩 파일 찾기"""
    files = glob.glob('data/scraped/news_*.json')
    if not files:
        return None
    return max(files, key=os.path.getctime)

def load_latest_news():
    """최신 뉴스 데이터 로드"""
    # latest.json에서 파일명 확인
    latest_file = None
    if os.path.exists('data/latest.json'):
        try:
            with open('data/latest.json', 'r', encoding='utf-8') as f:
                meta = json.load(f)
                latest_file = meta.get('latestFile')
        except:
            pass
    
    # latest.json에 지정된 파일 로드
    if latest_file:
        scraped_path = f'data/scraped/{latest_file}'
        if os.path.exists(scraped_path):
            with open(scraped_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # 또는 가장 최근 스크랩 파일 로드
    scraped_file = get_latest_scraped_file()
    if scraped_file:
        with open(scraped_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def format_message(data):
    """뉴스 기사를 WhatsApp 메시지 형식으로 변환"""
    if not data:
        return None
        
    message = f"📰 *Singapore News Update*\n"
    message += f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 데이터가 리스트 형식인 경우 (그룹별로 이미 정리됨)
    if isinstance(data, list):
        total_articles = sum(group.get('article_count', len(group.get('articles', []))) for group in data)
        message += f"📊 오늘의 주요 뉴스: {len(data)}개 그룹, 총 {total_articles}개 기사\n\n"
        
        for group_data in data:
            group_name = group_data['group']
            group_articles = group_data['articles']
            sites = group_data['sites']
            
            message += f"【 {group_name} 】\n"
            message += f"📍 출처: {', '.join(sites)}\n"
            message += "━━━━━━━━━━━━━━━━━━━━\n"
            
            for i, article in enumerate(group_articles, 1):
                message += f"\n{i}. {article.get('summary', article.get('korean_summary', '요약 없음'))}\n"
                if article.get('url'):
                    message += f"   🔗 원문: {article['url']}\n"
                message += "\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    message += "\n━━━━━━━━━━━━━━━━━━━━\n"
    message += "🤖 Singapore News Scraper\n"
    message += "📱 Powered by Green API"
    
    return message

def send_to_whatsapp_green(message, phone_number):
    """Green API를 통한 WhatsApp 메시지 전송"""
    
    # Green API 설정
    instance_id = os.environ.get('GREEN_API_INSTANCE_ID')
    api_token = os.environ.get('GREEN_API_TOKEN')
    
    if not instance_id or not api_token:
        print("❌ Green API 인증 정보가 없습니다.")
        print("\n📝 현재 환경 변수 상태:")
        print(f"   - GREEN_API_INSTANCE_ID: {'설정됨' if instance_id else '없음'}")
        print(f"   - GREEN_API_TOKEN: {'설정됨' if api_token else '없음'}")
        if instance_id:
            print(f"   - Instance ID 길이: {len(instance_id)}")
        if api_token:
            print(f"   - Token 길이: {len(api_token)}")
        print("\n📝 설정 방법:")
        print("1. https://green-api.com 에서 계정 생성")
        print("2. 인스턴스 생성 후 QR 코드로 WhatsApp 연결")
        print("3. GitHub Secrets에 추가:")
        print("   - GREEN_API_INSTANCE_ID")
        print("   - GREEN_API_TOKEN")
        return False
    
    # API 엔드포인트
    # Green API 공식 URL: https://api.green-api.com
    base_url = "https://api.green-api.com"
    api_url = f"{base_url}/waInstance{instance_id}/sendMessage/{api_token}"
    
    # 전화번호 형식 변환
    # Green API는 국가코드+번호@c.us 형식 사용
    if '@' not in phone_number:
        # 그룹 ID가 아닌 경우 개인 번호로 처리
        phone_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        phone_number = f"{phone_number}@c.us"
    
    # 메시지 전송
    payload = {
        "chatId": phone_number,
        "message": message
    }
    
    try:
        print(f"\n📤 API 호출 정보:")
        print(f"   - URL: {api_url[:50]}...")
        print(f"   - Chat ID: {phone_number}")
        print(f"   - 메시지 길이: {len(message)}자")
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"\n📥 Green API Response:")
        print(f"   - 상태 코드: {response.status_code}")
        print(f"   - 응답 헤더: {dict(response.headers)}")
        print(f"   - 응답 본문: {response.text[:500]}..." if len(response.text) > 500 else f"   - 응답 본문: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ 메시지 전송 성공!")
            try:
                result = response.json()
                if 'idMessage' in result:
                    print(f"   - 메시지 ID: {result['idMessage']}")
            except:
                pass
            return True
        else:
            print(f"\n❌ 전송 실패: {response.status_code}")
            if response.status_code == 400:
                print("   - 400 Bad Request: 요청 형식이 잘못되었습니다.")
            elif response.status_code == 401:
                print("   - 401 Unauthorized: 인증 정보가 올바르지 않습니다.")
            elif response.status_code == 403:
                print("   - 403 Forbidden: 권한이 없습니다.")
            elif response.status_code == 404:
                print("   - 404 Not Found: API 엔드포인트를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ API 호출 오류: {e}")
        return False

def check_green_api_status():
    """Green API 상태 확인"""
    instance_id = os.environ.get('GREEN_API_INSTANCE_ID')
    api_token = os.environ.get('GREEN_API_TOKEN')
    
    if not instance_id or not api_token:
        print("❌ 환경 변수가 설정되지 않았습니다.")
        print(f"   - GREEN_API_INSTANCE_ID 설정됨: {'예' if instance_id else '아니오'}")
        print(f"   - GREEN_API_TOKEN 설정됨: {'예' if api_token else '아니오'}")
        if instance_id:
            print(f"   - Instance ID 길이: {len(instance_id)}")
            print(f"   - Instance ID 앞 4자리: {instance_id[:4] if len(instance_id) >= 4 else instance_id}")
        return False
    
    try:
        # Green API 공식 URL 사용
        base_url = "https://api.green-api.com"
        url = f"{base_url}/waInstance{instance_id}/getStateInstance/{api_token}"
        
        print(f"   - 상태 확인 URL: {base_url}/waInstance{instance_id}/getStateInstance/***")
        
        response = requests.get(url, timeout=10)
        
        print(f"   - 상태 확인 응답: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('stateInstance', '')
            print(f"   - 📱 인스턴스 상태: {state}")
            
            # 추가 정보 출력
            if 'typeInstance' in data:
                print(f"   - 인스턴스 타입: {data['typeInstance']}")
            if 'deviceId' in data:
                print(f"   - 디바이스 ID: {data['deviceId'][:20]}...")
            
            return state == 'authorized'
        else:
            print(f"   - ❌ 상태 확인 실패: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   - ❌ 상태 확인 오류: {type(e).__name__}: {e}")
        return False

def save_history(channel_id, status, message_preview, article_count):
    """발송 이력 저장"""
    history_file = f'data/history/{datetime.now().strftime("%Y%m")}.json'
    os.makedirs('data/history', exist_ok=True)
    
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append({
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'timestamp': datetime.now().isoformat(),
        'channel': channel_id,
        'status': 'success' if status else 'failed',
        'header': f"뉴스 {article_count}개 발송",
        'message_preview': message_preview[:200] + '...' if len(message_preview) > 200 else message_preview,
        'message_length': len(message_preview),
        'article_count': article_count,
        'api': 'green-api'  # API 제공자 표시
    })
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 50)
    print("📱 Singapore News WhatsApp 전송")
    print("   (Green API)")
    print("=" * 50)
    
    # Green API 상태 확인
    print("\n🔍 Green API 상태 확인 중...")
    api_status = check_green_api_status()
    if not api_status:
        print("\n❌ Green API가 준비되지 않았습니다.")
        print("   인스턴스가 authorized 상태인지 확인하세요.")
        print("\n💡 디버깅 정보:")
        instance_id = os.environ.get('GREEN_API_INSTANCE_ID')
        api_token = os.environ.get('GREEN_API_TOKEN')
        if instance_id and api_token:
            print(f"   - Base URL: https://{instance_id}.api.greenapi.com")
            print(f"   - Instance ID 형식 확인: {instance_id[:10]}...")
        return
    
    # 설정 로드
    settings = load_settings()
    
    if settings.get('sendChannel') != 'whatsapp':
        print("WhatsApp is not configured as send channel")
        return
    
    # WhatsApp 채널 확인
    channel_id = settings.get('whatsappChannel')
    if not channel_id:
        print("❌ WhatsApp 채널이 설정되지 않았습니다.")
        return
    
    print(f"📱 대상 채널: {channel_id}")
    
    # 최신 뉴스 로드
    news_data = load_latest_news()
    if not news_data:
        print("❌ 발송할 뉴스가 없습니다.")
        return
    
    # 기사 개수 계산
    article_count = 0
    if isinstance(news_data, list):
        # 그룹 형식
        article_count = sum(group.get('article_count', len(group.get('articles', []))) for group in news_data)
        articles = news_data
    elif isinstance(news_data, dict) and 'articles' in news_data:
        # 단일 articles 배열
        articles = news_data['articles']
        article_count = len(articles)
    else:
        print("❌ 알 수 없는 데이터 형식")
        return
    
    print(f"📰 발송할 기사: {article_count}개")
    
    # 메시지 포맷팅
    message = format_message(news_data)
    if not message:
        print("❌ 메시지 생성 실패")
        return
    
    print(f"📝 메시지 길이: {len(message)}자")
    
    # WhatsApp 전송
    success = send_to_whatsapp_green(message, channel_id)
    
    # 발송 이력 저장
    save_history(channel_id, success, message, article_count)
    
    if success:
        print(f"\n✅ {article_count}개 기사를 WhatsApp으로 전송 완료!")
    else:
        print("\n❌ WhatsApp 메시지 전송 실패")
        print("\n💡 문제 해결 방법:")
        print("1. Green API 대시보드에서 인스턴스 상태 확인")
        print("2. QR 코드 재스캔 필요할 수 있음")
        print("3. API 토큰이 올바른지 확인")

if __name__ == "__main__":
    main()