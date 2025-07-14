# 설정 가이드

## 1. GitHub Repository 생성 및 Push

```bash
# 1. GitHub에서 새 repository 생성
# Repository name: singapore_news_scrap_v1.1

# 2. 로컬에서 remote 추가 및 push
git remote add origin https://github.com/djyalu/singapore_news_scrap_v1.1.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

## 2. GitHub Pages 활성화

1. GitHub Repository 페이지로 이동
2. Settings 탭 클릭
3. 왼쪽 메뉴에서 "Pages" 클릭
4. Source 섹션에서:
   - Source: "Deploy from a branch" 선택
   - Branch: "main" 선택
   - Folder: "/ (root)" 선택
   - Save 클릭
5. 몇 분 후 `https://djyalu.github.io/singapore_news_scrap_v1.1/` 에서 접속 가능

## 3. GitHub Actions Secrets 설정

1. Settings 탭에서 왼쪽 메뉴 "Secrets and variables" > "Actions" 클릭
2. "New repository secret" 클릭하여 다음 secrets 추가:

### OPENAI_API_KEY
- OpenAI 계정에서 API 키 발급 (https://platform.openai.com/api-keys)
- Name: `OPENAI_API_KEY`
- Secret: `sk-...` (발급받은 키)

### WHATSAPP_API_KEY
- WhatsApp Business API 설정 필요
- Meta for Developers (https://developers.facebook.com) 에서:
  1. 앱 생성 > Business 타입 선택
  2. WhatsApp 제품 추가
  3. API 설정에서 토큰 발급
- Name: `WHATSAPP_API_KEY`
- Secret: 발급받은 액세스 토큰

## 4. WhatsApp Business API 상세 설정

### 4.1 Meta Business 계정 설정
1. https://business.facebook.com 접속
2. WhatsApp Business 계정 생성
3. 전화번호 인증

### 4.2 개발자 앱 설정
1. https://developers.facebook.com 접속
2. "내 앱" > "앱 만들기"
3. "비즈니스" 타입 선택
4. 앱 이름 입력 후 생성

### 4.3 WhatsApp 제품 추가
1. 대시보드에서 "제품 추가" > "WhatsApp" 선택
2. "설정" 클릭
3. 전화번호 추가 및 인증

### 4.4 영구 토큰 발급
1. WhatsApp > API 설정
2. "영구 토큰" 섹션에서 토큰 생성
3. 이 토큰을 GitHub Secret에 저장

### 4.5 Webhook 설정 (선택사항)
1. WhatsApp > 구성 > Webhook
2. Callback URL 설정
3. Verify Token 설정

## 5. Python 스크립트 수정 필요사항

`scripts/send_whatsapp.py` 파일에서 수정:
```python
# YOUR_PHONE_NUMBER_ID 를 실제 WhatsApp Business 전화번호 ID로 변경
response = requests.post(
    'https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages',
    headers=headers,
    json=data
)
```

전화번호 ID는 WhatsApp > API 설정에서 확인 가능

## 6. 초기 데이터 디렉토리 생성

```bash
mkdir -p data/scraped
mkdir -p data/history
git add .
git commit -m "Add data directories"
git push
```

## 7. GitHub Actions 수동 실행 테스트

1. Actions 탭으로 이동
2. "Singapore News Scraper" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 실행 결과 확인

## 8. 웹사이트 접속 및 테스트

1. `https://djyalu.github.io/singapore_news_scrap_v1.1/` 접속
2. 초기 로그인 정보:
   - ID: `admin`
   - Password: `Admin@123`
3. Settings에서 원하는 설정 구성

## 문제 해결

### GitHub Pages가 작동하지 않는 경우
- Settings > Pages에서 빌드 상태 확인
- 빌드 실패 시 Actions 탭에서 로그 확인

### WhatsApp 메시지 전송 실패
- API 키가 올바른지 확인
- 전화번호 ID가 올바른지 확인
- WhatsApp Business 계정이 활성화되었는지 확인

### 스크래핑 실패
- GitHub Actions 로그 확인
- 대상 사이트의 robots.txt 확인
- 네트워크 연결 상태 확인