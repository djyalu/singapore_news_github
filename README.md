# Singapore News Scraper

싱가포르 뉴스를 자동으로 스크랩하고 WhatsApp으로 전송하는 시스템입니다.

## 기능

- 싱가포르 주요 뉴스 사이트 스크랩
- 최신 기사, 중요 기사 필터링
- 기사 요약 (헤드라인, 키워드, 본문)
- WhatsApp 채널로 자동 전송
- 유해 콘텐츠 필터링
- 사용자 권한 관리 (관리자/일반사용자)

## 설치 및 실행

1. GitHub Pages 활성화
   - Settings > Pages > Source를 `Deploy from a branch`로 설정
   - Branch를 `main`, 폴더를 `/root`로 설정

2. GitHub Secrets 설정
   - `OPENAI_API_KEY`: OpenAI API 키
   - `WHATSAPP_API_KEY`: WhatsApp Business API 키

3. 기본 로그인 정보
   - ID: admin
   - Password: Admin@123

## 구조

- `/` - 메인 웹 인터페이스
- `/scripts` - 스크래핑 및 전송 스크립트
- `/data` - 설정 및 데이터 파일
- `/.github/workflows` - GitHub Actions 워크플로우

## WhatsApp 채널

- Singapore News Main (Test): 120363419092108413@g.us
- Singapore News Backup: 120363421252284444@g.us