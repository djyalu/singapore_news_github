# Vercel 배포 설정 가이드

## 1. Vercel CLI 설치 (선택사항)

```bash
npm i -g vercel
```

## 2. 수동으로 Vercel Token 받기

1. https://vercel.com/account/tokens 접속
2. "Create" 클릭
3. Token 이름 입력 (예: singapore-news-github)
4. Scope는 기본값 유지
5. "Create Token" 클릭
6. 생성된 토큰 복사 (한 번만 표시됨!)

## 3. Vercel 프로젝트 정보 얻기

### 방법 1: Vercel CLI 사용
```bash
vercel link
# 프로젝트 선택 후
vercel env pull .env.local
```

`.env.local` 파일에서 확인:
- VERCEL_ORG_ID
- VERCEL_PROJECT_ID

### 방법 2: Vercel 대시보드에서 확인
1. 프로젝트 Settings → General
2. URL에서 확인: `https://vercel.com/[ORG_ID]/[PROJECT_NAME]/settings`
3. Project ID는 페이지 하단에 표시

## 4. GitHub Secrets 추가

GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

추가할 Secrets:
- `VERCEL_TOKEN`: 위에서 생성한 토큰
- `VERCEL_ORG_ID`: 조직/계정 ID
- `VERCEL_PROJECT_ID`: 프로젝트 ID

## 5. 프론트엔드 코드 수정

`js/app.js`에서 API URL 업데이트:

```javascript
// 로컬 개발
const API_URL = window.location.hostname === 'localhost' 
  ? '/api/send-whatsapp' 
  : 'https://singapore-news-github-[username].vercel.app/api/send-whatsapp';
```

## 6. 테스트

1. `git push origin main` 실행
2. GitHub Actions 확인
3. Vercel 대시보드에서 배포 상태 확인
4. 배포된 URL에서 WhatsApp 테스트 전송

## 문제 해결

### CORS 오류
`api/send-whatsapp.js`의 CORS 헤더 확인

### 404 오류
- `vercel.json` 파일 확인
- API 경로가 `/api/send-whatsapp`인지 확인

### 인증 오류
- 환경 변수 설정 확인
- WhatsApp API 토큰 유효성 확인