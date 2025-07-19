#!/usr/bin/env python3
"""Green API 테스트 스크립트"""

import os
import requests
import json

# 테스트용 설정
INSTANCE_ID = "7105285370"
API_TOKEN = input("Green API Token을 입력하세요: ")

# 상태 확인
print("\n1. API 상태 확인...")
base_url = f"https://{INSTANCE_ID}.api.greenapi.com"
status_url = f"{base_url}/waInstance{INSTANCE_ID}/getStateInstance/{API_TOKEN}"

try:
    response = requests.get(status_url)
    print(f"응답 코드: {response.status_code}")
    print(f"응답: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        state = data.get('stateInstance', '')
        print(f"✅ 인스턴스 상태: {state}")
        
        if state != 'authorized':
            print("⚠️  WhatsApp 연결이 필요합니다. Green API 대시보드에서 QR 코드를 스캔하세요.")
    else:
        print("❌ API 접근 실패")
except Exception as e:
    print(f"❌ 오류: {e}")

# 테스트 메시지 전송
if input("\n테스트 메시지를 보내시겠습니까? (y/n): ").lower() == 'y':
    phone = input("받을 전화번호 입력 (예: 821012345678): ")
    
    # 개인 번호 형식으로 변환
    if not phone.startswith('+'):
        phone = phone.replace('-', '').replace(' ', '')
    chat_id = f"{phone}@c.us"
    
    print(f"\n2. 테스트 메시지 전송 중... (대상: {chat_id})")
    
    send_url = f"{base_url}/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    
    payload = {
        "chatId": chat_id,
        "message": "🤖 Green API 테스트 메시지\n✅ 연결 성공!"
    }
    
    try:
        response = requests.post(send_url, json=payload)
        print(f"응답 코드: {response.status_code}")
        print(f"응답: {response.text}")
        
        if response.status_code == 200:
            print("✅ 메시지 전송 성공!")
        else:
            print("❌ 메시지 전송 실패")
    except Exception as e:
        print(f"❌ 오류: {e}")

print("\n테스트 완료")