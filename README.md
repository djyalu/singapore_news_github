# Singapore News Scraper

싱가포르 뉴스를 자동으로 스크래핑하고 WhatsApp으로 전송하는 시스템입니다.

## 기능

- 🌏 싱가포르 주요 뉴스 사이트 자동 스크래핑
- 🤖 AI 기반 요약 및 키워드 추출
- 📱 WhatsApp 자동 전송
- ⏰ 스케줄링 기능 (하루 3회 자동 실행)
- 🔧 웹 대시보드를 통한 관리
- 🔄 GitHub Actions 연동
- 🗂️ 30일 데이터 보관 및 자동 정리

## 환경 설정

### 1. Vercel 환경변수 설정

Vercel 프로젝트에서 다음 환경변수를 설정해야 합니다:

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your-github-username
GITHUB_REPO=singapore_news_github
WHATSAPP_API_KEY=your-whatsapp-api-key
```

### 2. GitHub Personal Access Token 생성

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" 클릭
3. 권한 선택:
   - `repo` (전체 저장소 접근)
   - `workflow` (GitHub Actions 관리)
4. 생성된 토큰을 `GITHUB_TOKEN` 환경변수에 설정

### 3. WhatsApp API 설정

WhatsApp API 토큰을 `WHATSAPP_API_KEY` 환경변수에 설정합니다.

## 사용법

### 웹 대시보드

1. 브라우저에서 애플리케이션에 접속
2. 기본 계정으로 로그인: `admin` / `Admin@123`
3. Dashboard에서 "지금 스크랩하기" 버튼 클릭
4. GitHub Actions에서 실제 스크래핑 실행
5. 진행 상황을 실시간으로 모니터링

### 자동 스케줄링

GitHub Actions가 다음 시간에 자동으로 실행됩니다:
- 한국시간 기준: 09:00, 13:00, 18:00 (UTC: 00:00, 04:00, 09:00)

### 수동 실행

GitHub 저장소 → Actions 탭 → "Singapore News Scraper" → "Run workflow"

## 아키텍처

```
Frontend (Vercel)     GitHub Actions        Data Storage
┌─────────────────┐   ┌──────────────────┐  ┌─────────────────┐
│                 │   │                  │  │                 │
│  Web Dashboard  │──▶│  scraper.py      │─▶│  data/scraped/  │
│                 │   │                  │  │                 │
│  - 스크래핑 트리거 │   │  - 뉴스 수집      │  │  - JSON 파일     │
│  - 상태 모니터링  │   │  - WhatsApp 전송 │  │  - 30일 보관     │
│  - 설정 관리     │   │  - 데이터 정리    │  │  - 자동 삭제     │
│                 │   │                  │  │                 │
└─────────────────┘   └──────────────────┘  └─────────────────┘
         │                       │                     │
         └───────────────────────┼─────────────────────┘
                                 │
                    API Endpoints (Vercel)
                   ┌──────────────────────┐
                   │ /api/trigger-scraping │
                   │ /api/get-scraping-status │
                   │ /api/save-settings   │
                   └──────────────────────┘
```

## API 엔드포인트

### POST /api/trigger-scraping
GitHub Actions에서 스크래핑 워크플로우를 실행합니다.

### GET /api/get-scraping-status
최근 스크래핑 작업의 상태를 조회합니다.

### POST /api/save-settings
애플리케이션 설정을 저장합니다.

## 파일 구조

```
├── api/                    # Vercel API 함수
│   ├── trigger-scraping.js # GitHub Actions 트리거
│   ├── get-scraping-status.js # 상태 조회
│   └── save-settings.js    # 설정 저장
├── scripts/                # Python 스크립트
│   ├── scraper.py         # 메인 스크래퍼
│   ├── send_whatsapp.py   # WhatsApp 전송
│   ├── scheduler.py       # 스케줄러
│   └── cleanup_old_data.py # 데이터 정리
├── data/                   # 데이터 저장소
│   ├── settings.json      # 애플리케이션 설정
│   ├── sites.json         # 뉴스 사이트 목록
│   ├── scraped/           # 스크래핑된 데이터
│   └── history/           # 전송 이력
├── .github/workflows/      # GitHub Actions
│   └── scraper.yml        # 스크래핑 워크플로우
├── js/                     # Frontend JavaScript
│   ├── app.js             # 메인 애플리케이션
│   └── auth.js            # 인증 시스템
└── index.html             # 메인 페이지
```

## 데이터 관리

- **보관 기간**: 30일
- **자동 정리**: 스크래핑 실행 시마다 30일 이전 데이터 삭제
- **데이터 형식**: JSON
- **용량 관리**: GitHub 저장소 용량 제한 준수

## 문제 해결

### 1. 스크래핑이 시작되지 않는 경우
- Vercel 환경변수 확인 (`GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`)
- GitHub 토큰 권한 확인
- GitHub Actions 워크플로우 활성화 확인

### 2. WhatsApp 전송 실패
- `WHATSAPP_API_KEY` 환경변수 확인
- WhatsApp 채널 ID 올바른지 확인
- API 토큰 유효성 확인

### 3. 상태 모니터링 오류
- GitHub API 호출 제한 확인
- 네트워크 연결 상태 확인
- GitHub Actions 실행 권한 확인

## WhatsApp 채널

- Singapore News Main (Test): 120363419092108413@g.us
- Singapore News Backup: 120363421252284444@g.us