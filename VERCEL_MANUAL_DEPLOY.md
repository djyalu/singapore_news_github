# 수동 Vercel 배포 가이드

## 현재 상황
- ✅ WhatsApp API: 접근 가능 
- ❌ Vercel API: GitHub Actions 배포 실패
- ✅ GitHub Pages: 정상 작동

## 왜 Vercel이 여전히 필요한가?

### CORS 정책으로 인한 제한
```javascript
// ❌ 브라우저에서 직접 호출 불가 (CORS 오류)
fetch('https://gate.whapi.cloud/messages/text', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'  // 보안 위험!
    }
})
```

```javascript
// ✅ Vercel 서버를 통한 우회 호출
fetch('https://your-vercel-app.vercel.app/api/send-whatsapp', {
    method: 'POST',
    body: JSON.stringify({ channel, message })
})
```

## 빠른 해결 방법

### 1. 수동 Vercel 배포 (5분)
```bash
# 1. Vercel CLI 설치
npm i -g vercel

# 2. 로그인
vercel login

# 3. 배포 (프로젝트 폴더에서)
vercel --prod
```

### 2. 또는 Vercel 웹사이트에서
1. https://vercel.com/dashboard 접속
2. 프로젝트 선택
3. "Redeploy" 클릭

### 3. 배포 완료 후
1. 배포 URL 확인 (예: https://singapore-news-github-abc123.vercel.app)
2. `js/app.js` 파일의 601번 줄 URL 업데이트
3. GitHub에 푸시

## 대안: 간소화된 구조

만약 Vercel 설정이 복잡하다면:

### 방법 1: 프록시 서버 사용
- 무료 프록시 서비스 이용 (예: cors-anywhere)
- 보안상 권장하지 않음

### 방법 2: 로컬 서버 연동
- 로컬에서 Python/Node.js 서버 실행
- 개발 목적으로만 사용

## 권장 사항
Vercel 수동 배포를 통해 문제 해결하는 것이 가장 안전하고 효율적입니다.

**수동 배포 후 테스트:**
1. https://djyalu.github.io/singapore_news_github 접속
2. 설정 → 테스트 전송
3. 실제 WhatsApp 메시지 확인