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

def format_message(articles):
    message = f"📰 *Singapore News Update*\n{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n\n"
    
    grouped = {}
    for article in articles:
        group = article.get('group', 'Other')
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(article)
    
    for group, group_articles in grouped.items():
        message += f"🔹 *{group}*\n"
        for i, article in enumerate(group_articles[:3], 1):
            message += f"\n{i}. {article['title']}\n"
            summary_lines = article['summary'].split('\n')
            for line in summary_lines[:2]:  # 요약의 처음 2줄만
                if line.strip():
                    message += f"   {line.strip()}\n"
            message += f"   🔗 상세보기: {article['url']}\n"
        message += "\n"
    
    message += f"\n🤖 _Singapore News Scraper_"
    
    return message

def send_to_whatsapp(message, channel_id):
    # WhatsApp API 설정
    api_url = 'https://gate.whapi.cloud/messages/text'
    api_token = 'ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq'
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # 채널 ID 형식 처리
    if '@g.us' in channel_id:
        # 그룹 채널인 경우 - WhatsApp API 형식에 맞게 변환
        to_number = channel_id.replace('@g.us', '')
    else:
        to_number = channel_id
    
    data = {
        'to': to_number,
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

def save_history(channel_id, status, message_preview):
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
        'header': message_preview[:100] + '...',
        'message_length': len(message_preview)
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
        articles = json.load(f)
    
    if not articles:
        print("No articles to send")
        return
    
    message = format_message(articles)
    
    if len(message) > 4096:
        message = message[:4090] + '...'
    
    success = send_to_whatsapp(message, channel_id)
    save_history(channel_id, success, message)
    
    if success:
        print(f"Successfully sent {len(articles)} articles to WhatsApp")
    else:
        print("Failed to send message to WhatsApp")

if __name__ == "__main__":
    main()