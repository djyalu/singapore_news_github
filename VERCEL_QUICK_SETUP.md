# Vercel API 연결 빠른 설정 가이드

## 1단계: Vercel 가입 및 프로젝트 생성 (5분)

### 1.1 Vercel 가입
1. https://vercel.com 접속
2. "Sign Up" 클릭
3. "Continue with GitHub" 선택
4. GitHub 계정으로 로그인

### 1.2 프로젝트 Import
1. Vercel 대시보드에서 "Add New..." → "Project" 클릭
2. "Import Git Repository" 섹션에서 "singapore_news_github" 찾기
3. "Import" 버튼 클릭

### 1.3 프로젝트 설정
1. Framework Preset: "Other" 선택
2. Root Directory: 그대로 두기 (./）
3. "Deploy" 버튼 클릭

### 1.4 배포 완료 대기 (1-2분)
- 배포 완료 후 URL 확인 (예: https://singapore-news-github-abc123.vercel.app)

## 2단계: 코드 수정 (2분)

### 2.1 app.js 파일 수정
`js/app.js` 파일을 열고 599번째 줄 찾기:

```javascript
// 변경 전
const VERCEL_URL = 'https://singapore-news-github.vercel.app'; // TODO: 실제 Vercel URL로 변경

// 변경 후 (실제 URL로 변경)
const VERCEL_URL = 'https://singapore-news-github-abc123.vercel.app'; // 여기에 Vercel 배포 URL 입력
```

### 2.2 변경사항 저장

## 3단계: GitHub에 Push (1분)

### VS Code 터미널 또는 Git Bash에서:
```bash
git add js/app.js
git commit -m "Update Vercel API URL"
git push origin main
```

### 또는 GitHub Desktop에서:
1. 변경사항 확인
2. Commit 메시지: "Update Vercel API URL"
3. "Commit to main" 클릭
4. "Push origin" 클릭

## 4단계: 테스트 (1분)

1. https://djyalu.github.io/singapore_news_github 접속
2. 로그인 (admin / Admin@123)
3. Settings → 테스트 전송
4. "Singapore News Backup" 선택
5. "테스트 전송" 클릭

## 완료! 🎉

이제 WhatsApp으로 실제 메시지가 전송됩니다.

---

## 문제 해결

### "네트워크 오류" 발생 시:
1. Vercel URL이 정확한지 확인
2. https:// 포함되어 있는지 확인
3. 브라우저 개발자 도구(F12) → Console 탭에서 오류 확인

### 메시지가 전송되지 않을 때:
1. WhatsApp 그룹 ID가 올바른지 확인 (120363421252284444@g.us)
2. Vercel 대시보드에서 Function 로그 확인

### Vercel URL 확인 방법:
1. https://vercel.com/dashboard 접속
2. 프로젝트 클릭
3. 상단의 "Visit" 버튼 옆 URL 확인

---

## 고급 설정 (선택사항)

### 환경 변수 추가하기
Vercel 프로젝트 Settings → Environment Variables:
- `WHATSAPP_API_KEY`: ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq

### 커스텀 도메인 연결
1. Settings → Domains
2. 도메인 추가 (예: api.yourdomain.com)
3. DNS 설정 추가