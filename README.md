# Singapore News Scraper

싱가포르 뉴스를 자동으로 스크래핑하고 WhatsApp으로 전송하는 시스템입니다.

## 기능

- 🌏 싱가포르 주요 뉴스 사이트 자동 스크래핑
- 🤖 AI 기반 한글 요약 (Google Gemini API)
- 📱 WhatsApp 자동 전송
- ⏰ 스케줄링 기능 (하루 3회 자동 실행)
- 🔧 웹 대시보드를 통한 관리
- 🔄 GitHub Actions 연동
- 🗂️ 30일 또는 50MB 제한 자동 정리
- 👤 사용자 관리 및 인증 시스템

## 시스템 아키텍처

```mermaid
graph TB
    subgraph "Frontend - GitHub Pages"
        A[Web Dashboard<br/>HTML/JS/CSS]
        B[localStorage<br/>캐시 데이터]
        A <--> B
    end
    
    subgraph "Vercel Serverless"
        C[API Endpoints]
        C1[trigger-scraping]
        C2[save-settings]
        C3[get-latest-scraped]
        C4[send-whatsapp]
        C --> C1
        C --> C2
        C --> C3
        C --> C4
    end
    
    subgraph "GitHub Repository"
        D[settings.json<br/>설정 파일]
        E[sites.json<br/>사이트 목록]
        F[scraped data<br/>스크랩 데이터]
        G[history<br/>전송 이력]
    end
    
    subgraph "GitHub Actions"
        H[Scraper Workflow<br/>스크래핑 + 전송]
        I[Scraper-Only<br/>스크래핑만]
        J[Send-WhatsApp<br/>전송만]
    end
    
    subgraph "External Services"
        L[News Websites<br/>뉴스 사이트들]
        M[WhatsApp API<br/>메시지 전송]
        N[Google Gemini API<br/>한글 요약]
    end
    
    A -->|API 호출| C
    C1 -->|워크플로우 트리거| H
    C2 -->|설정 저장| D
    C3 -->|데이터 읽기| F
    
    H -->|뉴스 수집| L
    H -->|AI 요약| N
    H -->|데이터 저장| F
    H -->|메시지 전송| M
    H -->|이력 저장| G
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bfb,stroke:#333,stroke-width:2px
```

## 환경 설정

### 1. Vercel 환경변수 설정

Vercel 프로젝트에서 다음 환경변수를 설정해야 합니다:

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # GitHub Personal Access Token
GITHUB_OWNER=djyalu                                    # GitHub 사용자명
GITHUB_REPO=singapore_news_github                      # 저장소 이름
WHATSAPP_API_KEY=ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq     # WhatsApp API 키
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

### 4. Google Gemini API 설정 (한글 요약)

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. GitHub Repository → Settings → Secrets and variables → Actions
5. "New repository secret" 클릭
6. Name: `GOOGLE_GEMINI_API_KEY`
7. Value: 생성한 API 키 붙여넣기

**무료 한도**: 일일 1,500회 요청 (충분함)

## 사용법

### 웹 대시보드

**URL**: `https://djyalu.github.io/singapore_news_github/`

1. 브라우저에서 애플리케이션에 접속
2. 기본 계정으로 로그인: `admin` / `Admin@123`
3. Dashboard에서 다음 기능 사용:
   - **"지금 스크랩하기"**: 뉴스 스크래핑 + WhatsApp 전송
   - **개별 실행**: API를 통해 스크래핑만 또는 전송만 실행 가능
4. 진행 상황을 실시간으로 모니터링

### 자동 스케줄링

GitHub Actions가 다음 시간에 자동으로 실행됩니다:
- 한국시간 기준: 09:00, 13:00, 18:00 (UTC: 00:00, 04:00, 09:00)
- 실행 내용: 스크래핑 + WhatsApp 전송

### 수동 실행 (GitHub Actions)

1. **통합 실행**: Actions → "Singapore News Scraper" → "Run workflow"
2. **스크래핑만**: Actions → "Scrape News Only" → "Run workflow"
3. **전송만**: Actions → "Send to WhatsApp" → "Run workflow"

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
                   ┌──────────────────────────┐
                   │ /api/trigger-scraping    │ (스크래핑 + 전송)
                   │ /api/scrape-only         │ (스크래핑만)
                   │ /api/send-only           │ (전송만)
                   │ /api/get-scraping-status │ (상태 확인)
                   │ /api/save-settings       │ (설정 저장)
                   └──────────────────────────┘
```

## API 엔드포인트

### POST /api/trigger-scraping
스크래핑과 WhatsApp 전송을 모두 실행합니다.

### POST /api/scrape-only
뉴스 스크래핑만 실행합니다 (WhatsApp 전송 없이).

### POST /api/send-only
저장된 뉴스를 WhatsApp으로 전송만 합니다.

### GET /api/get-scraping-status
최근 스크래핑 작업의 상태를 조회합니다.

### POST /api/save-settings
애플리케이션 설정을 저장합니다.

### GET /api/test-env
환경변수 설정 상태를 확인합니다.

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
│   ├── scraper.yml        # 통합 워크플로우 (스크래핑 + 전송)
│   ├── scraper-only.yml   # 스크래핑만 실행
│   └── send-whatsapp.yml  # WhatsApp 전송만 실행
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
- GitHub 토큰 권한 확인 (`repo`, `workflow` 권한 필요)
- GitHub Actions 워크플로우 활성화 확인
- Repository Settings → Actions → General → Workflow permissions → "Read and write permissions" 선택

### 2. WhatsApp 전송 실패
- `WHATSAPP_API_KEY` 환경변수 확인
- WhatsApp 채널 ID 올바른지 확인
- API 토큰 유효성 확인

### 3. 상태 모니터링 오류
- GitHub API 호출 제한 확인
- 네트워크 연결 상태 확인
- GitHub Actions 실행 권한 확인

## GitHub Actions 워크플로우

### 1. Singapore News Scraper (통합)
- **자동 실행**: 하루 3회 (09:00, 13:00, 18:00 KST)
- **기능**: 뉴스 스크래핑 → WhatsApp 전송 → 데이터 정리
- **수동 실행**: 가능

### 2. Scrape News Only
- **자동 실행**: 없음 (수동만)
- **기능**: 뉴스 스크래핑만
- **용도**: 전송 없이 데이터만 수집

### 3. Send to WhatsApp
- **자동 실행**: 없음 (수동만)
- **기능**: 저장된 뉴스 전송만
- **용도**: 이미 스크래핑된 데이터 재전송

## WhatsApp 채널

- Singapore News Main (Test): 120363419092108413@g.us
- Singapore News Backup: 120363421252284444@g.us