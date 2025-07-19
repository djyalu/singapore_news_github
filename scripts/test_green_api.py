#!/usr/bin/env python3
"""
Green API 연결 테스트 스크립트
GitHub Actions에서 실행하여 문제를 진단합니다.
"""

import os
import requests
import json

def test_green_api():
    print("=" * 50)
    print("Green API 연결 테스트")
    print("=" * 50)
    
    # 환경 변수 확인
    instance_id = os.environ.get('GREEN_API_INSTANCE_ID')
    api_token = os.environ.get('GREEN_API_TOKEN')
    
    print("\n1. 환경 변수 확인:")
    print(f"   - GREEN_API_INSTANCE_ID: {'설정됨' if instance_id else '❌ 없음'}")
    print(f"   - GREEN_API_TOKEN: {'설정됨' if api_token else '❌ 없음'}")
    
    if instance_id:
        print(f"   - Instance ID 길이: {len(instance_id)}자")
        print(f"   - Instance ID 앞 4자리: {instance_id[:4]}...")
    
    if api_token:
        print(f"   - Token 길이: {len(api_token)}자")
        print(f"   - Token 앞 4자리: {api_token[:4]}...")
    
    if not instance_id or not api_token:
        print("\n❌ 필수 환경 변수가 설정되지 않았습니다.")
        print("\n📝 해결 방법:")
        print("1. GitHub repository Settings > Secrets and variables > Actions")
        print("2. 다음 secrets 추가:")
        print("   - GREEN_API_INSTANCE_ID")
        print("   - GREEN_API_TOKEN")
        return False
    
    # API 상태 확인
    print("\n2. Green API 인스턴스 상태 확인:")
    try:
        base_url = f"https://{instance_id}.api.greenapi.com"
        status_url = f"{base_url}/waInstance{instance_id}/getStateInstance/{api_token}"
        
        print(f"   - API URL: {base_url}")
        print(f"   - 상태 체크 중...")
        
        response = requests.get(status_url, timeout=10)
        
        print(f"   - HTTP 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('stateInstance', 'unknown')
            print(f"   - 인스턴스 상태: {state}")
            
            if state == 'authorized':
                print("   ✅ WhatsApp 연결 상태: 정상")
            else:
                print(f"   ❌ WhatsApp 연결 상태: {state}")
                print("\n📝 해결 방법:")
                print("1. Green API 대시보드 접속")
                print("2. 인스턴스 페이지에서 QR 코드 스캔")
                print("3. WhatsApp 연결 확인")
            
            # 추가 정보 출력
            print("\n3. 인스턴스 세부 정보:")
            for key, value in data.items():
                if key != 'stateInstance':
                    print(f"   - {key}: {value}")
                    
        else:
            print(f"   ❌ API 응답 오류: {response.status_code}")
            print(f"   - 응답 내용: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ❌ API 연결 시간 초과")
        print("\n📝 해결 방법:")
        print("1. 인터넷 연결 확인")
        print("2. Green API 서버 상태 확인")
        
    except Exception as e:
        print(f"   ❌ 오류 발생: {type(e).__name__}: {e}")
        print("\n📝 해결 방법:")
        print("1. Instance ID와 Token이 올바른지 확인")
        print("2. Green API 대시보드에서 인스턴스 상태 확인")
    
    # 테스트 메시지 전송 (옵션)
    print("\n4. 테스트 메시지 전송 시도:")
    test_number = os.environ.get('TEST_PHONE_NUMBER', '')
    
    if test_number:
        print(f"   - 테스트 번호: {test_number}")
        try:
            send_url = f"{base_url}/waInstance{instance_id}/sendMessage/{api_token}"
            
            # 전화번호 형식 변환
            if '@' not in test_number:
                test_number = test_number.replace('+', '').replace('-', '').replace(' ', '')
                test_number = f"{test_number}@c.us"
            
            payload = {
                "chatId": test_number,
                "message": "🧪 Green API 테스트 메시지\n✅ API 연결 성공!"
            }
            
            response = requests.post(send_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ 테스트 메시지 전송 성공!")
                result = response.json()
                if 'idMessage' in result:
                    print(f"   - 메시지 ID: {result['idMessage']}")
            else:
                print(f"   ❌ 전송 실패: {response.status_code}")
                print(f"   - 응답: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 전송 오류: {e}")
    else:
        print("   - TEST_PHONE_NUMBER 환경 변수가 설정되지 않아 테스트 메시지를 보내지 않습니다.")
    
    print("\n" + "=" * 50)
    print("테스트 완료")
    print("=" * 50)

if __name__ == "__main__":
    test_green_api()