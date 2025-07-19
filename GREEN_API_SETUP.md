# Green API 설정 가이드

## 1. Green API 계정 생성

1. https://green-api.com 접속
2. "Sign Up" 클릭하여 계정 생성
3. 이메일 인증 완료

## 2. 인스턴스 생성

1. 대시보드에서 "Create Instance" 클릭
2. 요금제 선택:
   - **Developer** ($9/월): 300 메시지/월
   - **Business** ($39/월): 3,000 메시지/월
   - **Professional** ($79/월): 10,000 메시지/월

3. 결제 정보 입력

## 3. WhatsApp 연결

1. 인스턴스 생성 후 QR 코드 표시됨
2. WhatsApp 모바일 앱에서:
   - 설정 → 연결된 기기 → 기기 연결
   - QR 코드 스캔
3. 연결 상태가 "authorized"로 변경되는지 확인

## 4. API 인증 정보 확인

대시보드에서 다음 정보 확인:
- **Instance ID**: 1101234567
- **API Token**: fb4986a9d9cb40ef9be...

## 5. GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions에서 추가:

```
GREEN_API_INSTANCE_ID = 1101234567
GREEN_API_TOKEN = fb4986a9d9cb40ef9be...
```

## 6. 스크립트 전환

1. 현재 `send_whatsapp.py`를 `send_whatsapp_green.py`로 교체:
```bash
mv scripts/send_whatsapp.py scripts/send_whatsapp_old.py
mv scripts/send_whatsapp_green.py scripts/send_whatsapp.py
```

2. 또는 GitHub Actions에서 직접 green 버전 실행:
```yaml
- name: Send to WhatsApp
  env:
    GREEN_API_INSTANCE_ID: ${{ secrets.GREEN_API_INSTANCE_ID }}
    GREEN_API_TOKEN: ${{ secrets.GREEN_API_TOKEN }}
  run: |
    python scripts/send_whatsapp_green.py
```

## 7. 테스트

1. 수동으로 스크립트 실행:
```bash
export GREEN_API_INSTANCE_ID="your_instance_id"
export GREEN_API_TOKEN="your_api_token"
python scripts/send_whatsapp_green.py
```

2. GitHub Actions에서 수동 트리거

## 주의사항

- WhatsApp 연결이 끊어지면 QR 코드 재스캔 필요
- 메시지 한도 초과 시 추가 요금 발생
- 그룹 메시지는 그룹 ID 형식: 123456789@g.us
- 개인 메시지는 전화번호@c.us 형식

## 문제 해결

1. **"not authorized" 오류**
   - Green API 대시보드에서 QR 코드 재스캔
   
2. **메시지 전송 실패**
   - 전화번호 형식 확인 (국가코드 포함)
   - API 토큰 유효성 확인
   
3. **API 한도 초과**
   - 요금제 업그레이드 고려
   - 메시지 발송 주기 조정