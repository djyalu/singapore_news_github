import json
import os
import glob
from datetime import datetime
import requests

def load_settings():
    with open('data/settings.json', 'r') as f:
        return json.load(f)

def get_latest_scraped_file():
    files = glob.glob('data/scraped/news_*.json')
    if not files:
        return None
    return max(files, key=os.path.getctime)

def format_message(consolidated_articles):
    """그룹별로 통합된 기사들을 하나의 메시지로 포맷"""
    message = f"📰 *Singapore News Update*\n{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 전체 기사 개수 계산
    total_articles = sum(group['article_count'] for group in consolidated_articles)
    message += f"📊 오늘의 주요 뉴스: {len(consolidated_articles)}개 그룹, 총 {total_articles}개 기사\n\n"
    
    # 각 그룹별로 기사 표시
    for group_data in consolidated_articles:
        group_name = group_data['group']
        articles = group_data['articles']
        sites = group_data['sites']
        
        message += f"【 {group_name} 】\n"
        message += f"📍 출처: {', '.join(sites)}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━\n"
        
        # 그룹 내 기사들 표시
        for i, article in enumerate(articles, 1):
            # 각 기사의 한글 요약 표시
            message += f"\n{i}. {article['summary']}\n"
            message += f"   🔗 원문: {article['url']}\n"
            message += "\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 푸터 추가
    message += f"\n💡 *요약 정보*\n"
    message += f"• 스크랩 시간: {datetime.now().strftime('%H:%M')}\n"
    message += f"• 총 {len(consolidated_articles)}개 카테고리에서 {total_articles}개 기사 수집\n"
    message += f"\n🤖 _Singapore News Scraper Bot_"
    
    return message

def send_to_whatsapp(message, channel_id):
    # WhatsApp API 설정
    api_url = 'https://gate.whapi.cloud/messages/text'
    api_token = os.environ.get('WHATSAPP_API_KEY')
    
    if not api_token:
        print("Error: WHATSAPP_API_KEY environment variable not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # 그룹 채널 ID 그대로 사용
    data = {
        'to': channel_id,
        'body': message,
        'typing_time': 0
    }
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"WhatsApp API Response: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False

def save_history(channel_id, status, message_preview, article_count):
    history_file = f'data/history/{datetime.now().strftime("%Y%m")}.json'
    os.makedirs('data/history', exist_ok=True)
    
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    
    history.append({
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'timestamp': datetime.now().isoformat(),
        'channel': channel_id,
        'status': 'success' if status else 'failed',
        'header': f"뉴스 {article_count}개 발송",
        'message_preview': message_preview[:200] + '...' if len(message_preview) > 200 else message_preview,
        'message_length': len(message_preview),
        'article_count': article_count
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    settings = load_settings()
    
    if settings.get('sendChannel') != 'whatsapp':
        print("WhatsApp is not configured as send channel")
        return
    
    channel_id = settings.get('whatsappChannel')
    if not channel_id:
        print("No WhatsApp channel configured")
        return
    
    scraped_file = get_latest_scraped_file()
    if not scraped_file:
        print("No scraped data found")
        return
    
    with open(scraped_file, 'r') as f:
        consolidated_articles = json.load(f)
    
    if not consolidated_articles:
        print("No articles to send")
        return
    
    # 전체 기사 개수 계산
    total_articles = sum(group['article_count'] for group in consolidated_articles)
    
    # 메시지 생성
    message = format_message(consolidated_articles)
    
    # WhatsApp 메시지 길이 제한 확인
    if len(message) > 4096:
        # 메시지가 너무 길면 그룹별로 요약
        message = f"📰 *Singapore News Update*\n{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"📊 오늘의 주요 뉴스: {len(consolidated_articles)}개 그룹, 총 {total_articles}개 기사\n\n"
        
        for group_data in consolidated_articles:
            message += f"【{group_data['group']}】 {group_data['article_count']}개 기사\n"
            # 첫 번째 기사만 간단히 표시
            if group_data['articles']:
                first_article = group_data['articles'][0]
                message += f"• {first_article['title'][:50]}...\n"
            message += "\n"
        
        message += "\n📱 전체 내용은 웹사이트에서 확인하세요.\n"
        message += f"\n🤖 _Singapore News Scraper Bot_"
    
    success = send_to_whatsapp(message, channel_id)
    save_history(channel_id, success, message, total_articles)
    
    if success:
        print(f"Successfully sent {total_articles} articles from {len(consolidated_articles)} groups to WhatsApp")
    else:
        print("Failed to send message to WhatsApp")

if __name__ == "__main__":
    main()