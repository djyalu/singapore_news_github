# CLAUDE.md - Singapore News Scraper Project

## Project Overview
This is a Singapore News Scraper system that automatically scrapes Singapore news websites, generates Korean summaries using Google Gemini API, and sends them via WhatsApp. The system runs on GitHub Actions with a web dashboard hosted on GitHub Pages and API endpoints on Vercel.

## System Architecture
- **Frontend**: GitHub Pages (HTML/CSS/JavaScript)
- **Backend**: Vercel serverless functions (Node.js)
- **Automation**: GitHub Actions workflows
- **Storage**: GitHub repository (JSON files)
- **AI**: Google Gemini API for Korean summaries
- **Messaging**: WhatsApp API

## Key Scripts and Commands

### Development Commands
```bash
# Start development server
npm run dev

# Test environment variables
node api/test-env.js
```

### Python Scripts
```bash
# Main scraper (run via GitHub Actions)
python scripts/scraper.py

# Send WhatsApp messages only
python scripts/send_whatsapp.py

# Clean up old data (30+ days)
python scripts/cleanup_old_data.py
```

### Testing Commands
- No specific test framework is configured
- Manual testing through web dashboard
- API endpoints can be tested directly via Vercel

## Environment Variables (Vercel)
- `GITHUB_TOKEN`: GitHub Personal Access Token with repo and workflow permissions
- `GITHUB_OWNER`: djyalu
- `GITHUB_REPO`: singapore_news_github
- `WHATSAPP_API_KEY`: WhatsApp API key

## GitHub Secrets
- `GOOGLE_GEMINI_API_KEY`: Google Gemini API key for Korean summaries

## Key Files and Directories

### Configuration Files
- `data/settings.json`: Application settings
- `data/sites.json`: News sites to scrape
- `vercel.json`: Vercel configuration
- `requirements.txt`: Python dependencies

### API Endpoints (Vercel) - 12개 제한
- `/api/trigger-scraping.js`: Trigger scraping + WhatsApp sending workflow
- `/api/scrape-only.js`: Scraping only workflow (no WhatsApp)
- `/api/send-only.js`: WhatsApp sending only workflow
- `/api/get-scraping-status.js`: Check scraping status
- `/api/test-env.js`: Test environment variables
- `/api/auth.js`: 통합 인증 API (설정 조회 + 로그인) - GET/POST
- `/api/delete-scraped-file.js`: Delete scraped article files
- `/api/get-latest-scraped.js`: Get latest scraped data
- `/api/save-scraped-articles.js`: Save scraped articles to GitHub
- `/api/save-data.js`: 통합 데이터 저장 API (설정 + 사이트 목록) - POST
- `/api/send-email.js`: Send email notifications (SMTP)
- `/api/test-whatsapp.js`: WhatsApp 테스트 메시지 전송 (실제 API 호출)

**API 통합 완료:**
- `auth-config.js` + `auth-login.js` → `auth.js`
- `save-settings.js` + `save-sites.js` → `save-data.js`
- 새로 추가: `test-whatsapp.js` (실제 WhatsApp API 테스트)

**참고사항:**
- Vercel 무료 플랜의 API 엔드포인트 제한: 12개 (현재 12개 사용 중 - 제한 준수)
- 실제 WhatsApp 테스트 메시지 전송 가능
- 모든 API는 CORS 설정 완료되어 GitHub Pages에서 호출 가능
- 통합된 API는 `type` 파라미터로 기능 구분

### Python Scripts
- `scripts/scraper.py`: Main news scraper
- `scripts/send_whatsapp.py`: WhatsApp message sender
- `scripts/ai_summary.py`: AI summary generation
- `scripts/cleanup_old_data.py`: Data cleanup utility

### Frontend Files
- `index.html`: Main dashboard
- `js/app.js`: Main application logic
- `js/auth.js`: Authentication system
- `css/styles.css`: Styling

### Data Storage
- `data/scraped/`: Scraped news data (JSON files)
- `data/history/`: WhatsApp sending history
- `data/latest.json`: Latest scraped data

## GitHub Actions Workflows
1. **Singapore News Scraper** (`scraper.yml`): Full workflow (scraping + WhatsApp)
2. **Scrape News Only** (`scraper-only.yml`): Scraping only
3. **Send to WhatsApp** (`send-whatsapp.yml`): WhatsApp sending only

## Common Tasks

### Adding New News Sites
1. Edit `data/sites.json`
2. Add site configuration with URL and selectors
3. Test through dashboard

### Modifying Scraping Logic
1. Edit `scripts/scraper.py`
2. Update selectors or parsing logic
3. Test via manual trigger

### Updating WhatsApp Settings
1. Edit `data/settings.json`
2. Update channel IDs or message format
3. Test via "Send Only" feature

### Authentication
- Default login: `admin` / `Admin@123`
- Authentication handled in `js/auth.js`
- Uses localStorage for session management

## Data Management
- Auto-cleanup: 30 days retention
- File size limit: 50MB per cleanup
- Data format: JSON
- Backup: All data stored in GitHub repository

## Security Considerations
- API keys stored in Vercel environment variables
- GitHub tokens with minimal required permissions
- No sensitive data in repository
- Client-side authentication for dashboard

## Troubleshooting

### Common Issues
1. **GitHub Actions not triggering**: Check `GITHUB_TOKEN` permissions
2. **WhatsApp sending fails**: Verify `WHATSAPP_API_KEY`
3. **Scraping fails**: Check news site selectors in `sites.json`
4. **AI summary fails**: Verify `GOOGLE_GEMINI_API_KEY`
5. **No articles scraped (0개 기사)**:
   - URL 패턴이 너무 엄격한지 확인 (대소문자 구분 문제)
   - 뉴스 사이트 HTML 구조 변경 확인
   - `scripts/scraper.py`의 is_valid_article_url 함수 점검

### Log Locations
- GitHub Actions: Actions tab in repository
- Vercel: Function logs in Vercel dashboard
- Client: Browser console

## Development Notes
- Korean language support throughout
- Timezone: Korea Standard Time (KST)
- Scheduled runs: 07:59 KST (하루 1회로 설정됨)
- WhatsApp channels: Test and backup channels configured

## Dependencies
- Node.js 16+
- Python 3.x
- @octokit/rest for GitHub API
- requests, beautifulsoup4, selenium for scraping
- google-generativeai for AI summaries

## 작업 이력

### 2025-07-20 시스템 복원 및 정리
**시간**: 오후 10시 - 10시 42분  
**상태**: ✅ 완료

**수행 작업**:
1. **시스템 복원**: 안정 버전(commit 11f65bd)으로 리셋
2. **CSS 문법 오류 수정**: `border-transparent: 1px` → `border: 1px solid transparent`
3. **시스템 정상 동작 확인**:
   - Vercel API 엔드포인트 테스트 (모두 200 OK)
   - GitHub Pages 대시보드 접근 확인
   - 데이터 파일 상태 점검 (settings.json, sites.json, latest.json)
   - 로그인 기능 동작 확인

**파일 정리 (18개 파일 제거)**:
- `js/app-minimal.js` - localStorage 사용 백업 파일
- `test-*.html` (4개) - 테스트용 HTML 파일
- `test_*.py` (10개) - 테스트용 Python 스크립트
- `fix_*.js`, `fix_*.py` - 임시 수정 파일
- `*_backup.*` - 백업 데이터 파일들

**결과**:
- sessionStorage 기반 인증 시스템으로 통일
- 깔끔한 프로젝트 구조 확보
- 모든 핵심 기능 정상 동작 확인

**체크포인트**: 
- `★ 25.7.20 오후 10시 30분 정상 동작 확인 버전`
- `★ 정상 동작 확인 - 2025.7.20 오후 10시 42분`

### 2025-07-21 스크랩 관리 기능 개선 및 스크래핑 오류 수정
**시간**: 오전 9시 - 오후 6시  
**상태**: ✅ 완료

**수행 작업**:

1. **스크랩 관리 페이지 개선**:
   - 개별 파일 삭제 버튼 추가 (기존에 누락되어 있었음)
   - 날짜 범위 필터링 기능 구현 (시작일/종료일 선택)
   - 빠른 날짜 선택 버튼 추가 (오늘/최근 7일/최근 30일/전체)
   - 라디오 버튼 방식으로 하나만 선택 가능하도록 구현
   - 통계 정보 표시 오류 수정 (파일 수, 기사 수, 날짜 범위, 사이트 수)

2. **스크래핑 실패 원인 분석 및 수정**:
   - **문제**: 2025-07-20 오전 07:59 예약 스크래핑에서 0개 기사 수집
   - **원인**: Straits Times URL 패턴 검증이 너무 엄격
     - 소문자만 허용 (`[a-z0-9-]`)
     - 모든 URL이 "ST URL pattern match: False"로 필터링됨
   - **해결**: URL 패턴을 대소문자 모두 허용하도록 수정 (`[a-zA-Z0-9-]`)
   - `scripts/scraper.py` 924-937줄 수정

3. **UI/UX 개선 사항**:
   - 날짜 필터링 시 다양한 날짜 형식 지원
   - 디버깅 로그 추가로 문제 추적 용이
   - KST 시간대 정확한 처리

**기술적 세부사항**:
- `processScrapedFiles()`: 통계 계산 로직 개선
- `filterScrapedArticles()`: 날짜 범위 필터링 구현
- `setDateRange()`: 빠른 날짜 선택 기능
- `displayScrapedArticles()`: 삭제 버튼 추가

**결과**:
- 스크랩 관리 페이지에서 효율적인 데이터 관리 가능
- URL 패턴 검증 개선으로 정상적인 기사 수집 가능
- 사용자 친화적인 날짜 필터링 인터페이스

**남은 과제**:
- 다음 예약 실행(07:59 KST)에서 정상 작동 확인 필요
- 다른 뉴스 사이트들의 URL 패턴도 점검 필요