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
    message = f"📰 Singapore News Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    grouped = {}
    for article in articles:
        group = article.get('group', 'Other')
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(article)
    
    for group, group_articles in grouped.items():
        message += f"【{group}】\n"
        for article in group_articles[:5]:
            message += f"\n📌 {article['title']}\n"
            message += f"{article['summary']}\n"
            message += f"🔗 {article['url']}\n"
        message += "\n" + "="*50 + "\n\n"
    
    return message

def send_to_whatsapp(message, channel_id):
    api_key = os.environ.get('WHATSAPP_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'messaging_product': 'whatsapp',
        'to': channel_id,
        'type': 'text',
        'text': {
            'body': message
        }
    }
    
    response = requests.post(
        'https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages',
        headers=headers,
        json=data
    )
    
    return response.status_code == 200

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