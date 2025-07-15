# 배포 구조 설명

## 현재 구조 (하이브리드 방식)

```
사용자 → GitHub Pages (웹사이트) → Vercel (API) → WhatsApp
         djyalu.github.io           vercel.app
```

### 1. GitHub Pages (프론트엔드)
- **URL**: https://djyalu.github.io/singapore_news_github
- **역할**: HTML, CSS, JS 파일 호스팅
- **장점**: 
  - 완전 무료
  - GitHub과 자동 연동
  - 간단한 설정

### 2. Vercel (API 서버)
- **URL**: https://singapore-news-github.vercel.app/api/send-whatsapp
- **역할**: WhatsApp API 호출만 처리
- **장점**:
  - 서버리스 함수 지원
  - CORS 문제 해결
  - API 키 안전하게 보관

## 작동 방식

1. 사용자가 GitHub Pages 웹사이트 방문
2. "테스트 전송" 버튼 클릭
3. JavaScript가 Vercel API 호출
4. Vercel이 WhatsApp API 호출
5. WhatsApp 메시지 전송

## 왜 이렇게 나눈 건가요?

### GitHub Pages 한계
- 정적 파일만 제공 (서버 기능 없음)
- API 키를 안전하게 보관할 수 없음
- 외부 API 직접 호출 시 CORS 오류

### Vercel 역할
- 서버 기능 제공 (API 호출)
- 환경 변수로 API 키 보호
- CORS 정책 설정 가능

## 대안: Vercel 단독 사용

Vercel에서 모든 것을 호스팅할 수도 있습니다:

```bash
# vercel.json 수정
{
  "buildCommand": "echo 'No build'",
  "outputDirectory": ".",
  "framework": null
}
```

장점:
- 한 곳에서 모든 관리
- 더 간단한 설정

단점:
- Vercel 무료 한도 고려 필요
- GitHub Pages보다 복잡한 설정

## 추천 사항

현재 하이브리드 방식이 최적입니다:
- GitHub Pages: 무료로 웹사이트 호스팅
- Vercel: API 기능만 사용 (효율적)