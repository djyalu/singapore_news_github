#!/usr/bin/env python3
"""DNS 및 Green API 테스트"""

import socket
import requests

# 테스트할 URL들
test_urls = [
    "7105.api.greenapi.com",
    "api.greenapi.com",
    "api.green-api.com",
    "7103.api.greenapi.com"
]

print("=== DNS 해석 테스트 ===\n")

for url in test_urls:
    try:
        ip = socket.gethostbyname(url)
        print(f"✅ {url} → {ip}")
    except socket.gaierror:
        print(f"❌ {url} → DNS 해석 실패")

print("\n=== HTTPS 연결 테스트 ===\n")

# 올바른 Green API URL 테스트
test_full_urls = [
    "https://7105.api.greenapi.com",
    "https://api.green-api.com",
    "https://7103.api.greenapi.com"
]

for url in test_full_urls:
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {url} → 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ {url} → 오류: {type(e).__name__}")

print("\n=== 권장 사항 ===")
print("Green API 대시보드에서 정확한 API URL을 확인하세요.")
print("보통 다음 형식 중 하나입니다:")
print("- https://7105.api.greenapi.com")
print("- https://api.green-api.com/waInstance7105285370")