# Vercel 배포 간단 가이드

## 왜 Vercel이 필요한가?

- GitHub Pages = 정적 웹사이트만 호스팅 (HTML, CSS, JS)
- WhatsApp API 호출 = 서버 필요
- Vercel = 무료 서버리스 함수 제공

## 빠른 설정 (5분)

### 1. Vercel 가입
https://vercel.com → "Sign Up" → GitHub으로 로그인

### 2. 프로젝트 Import
1. "Add New..." → "Project" 클릭
2. "singapore_news_github" 저장소 선택
3. "Import" 클릭
4. 모든 설정 기본값 유지하고 "Deploy" 클릭

### 3. 배포 URL 확인
배포 완료 후 URL 복사 (예: https://singapore-news-github-abc123.vercel.app)

### 4. 코드 수정
`js/app.js` 파일 599번 줄의 URL 변경:
```javascript
const VERCEL_URL = 'https://singapore-news-github-abc123.vercel.app'; // 여기에 실제 URL 입력
```

### 5. GitHub에 Push
```bash
git add .
git commit -m "Update Vercel URL"
git push
```

## 완료!

이제 WhatsApp 테스트 메시지가 실제로 전송됩니다.

## 선택사항: GitHub Actions 자동 배포

위 과정이 작동하면, 자동 배포를 원할 경우 `docs/VERCEL_SETUP.md` 참조