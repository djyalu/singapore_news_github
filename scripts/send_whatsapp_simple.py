#!/usr/bin/env python3
"""
간단한 Green API WhatsApp 전송 테스트
"""

import os
import json
import requests
from datetime import datetime

# 환경변수 확인
instance_id = os.environ.get('GREEN_API_INSTANCE_ID', '')
api_token = os.environ.get('GREEN_API_TOKEN', '')

print(f"Instance ID 설정됨: {'예' if instance_id else '아니오'}")
print(f"API Token 설정됨: {'예' if api_token else '아니오'}")

if instance_id and api_token:
    print(f"Instance ID: {instance_id}")
    print(f"Instance ID 길이: {len(instance_id)}")
    print(f"Instance ID 타입: {type(instance_id)}")
    
    # URL 생성
    # Green API 공식 형식: https://api.green-api.com/waInstance{ID}/method/{TOKEN}
    base_url = "https://api.green-api.com"
    status_url = f"{base_url}/waInstance{instance_id}/getStateInstance/{api_token}"
    
    print(f"\n상태 확인 URL: {status_url}")
    
    try:
        response = requests.get(status_url, timeout=10)
        print(f"응답 코드: {response.status_code}")
        print(f"응답: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('stateInstance', '')
            print(f"\n✅ WhatsApp 상태: {state}")
            
            if state == 'authorized':
                # 테스트 메시지 전송
                settings = json.load(open('data/settings.json', 'r'))
                channel = settings.get('whatsappChannel', '')
                
                if channel:
                    send_url = f"{base_url}/waInstance{instance_id}/sendMessage/{api_token}"
                    payload = {
                        "chatId": channel,
                        "message": f"🤖 Green API 테스트\n✅ 연결 성공!\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                    
                    send_response = requests.post(send_url, json=payload)
                    print(f"\n메시지 전송 결과: {send_response.status_code}")
                    print(f"응답: {send_response.text[:200]}")
                    
    except Exception as e:
        print(f"\n❌ 오류: {type(e).__name__}: {e}")
        
        # DNS 테스트
        import socket
        try:
            ip = socket.gethostbyname("api.green-api.com")
            print(f"\nDNS 해석 성공: api.green-api.com → {ip}")
        except:
            print("\nDNS 해석 실패")
else:
    print("\n환경변수가 설정되지 않았습니다.")
    print("GitHub Secrets에서 다음을 확인하세요:")
    print("- GREEN_API_INSTANCE_ID = 7105285370")
    print("- GREEN_API_TOKEN = (실제 토큰값)")