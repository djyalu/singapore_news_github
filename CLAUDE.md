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
- `data/settings.json`: Application settings (includes scrapingMethod)
- `data/sites.json`: News sites to scrape (11 sites configured)
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
- `scripts/scraper.py`: Main news scraper (traditional, AI, RSS, hybrid methods)
- `scripts/scraper_rss.py`: RSS feed-based scraper
- `scripts/scraper_hybrid.py`: Hybrid scraper (RSS + traditional)
- `scripts/send_whatsapp.py`: WhatsApp message sender
- `scripts/ai_summary.py`: AI summary generation
- `scripts/ai_summary_free.py`: Free AI summary with Gemini API
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
4. **Debug Scraper** (`debug-scraper.yml`): Debug mode scraping

## Common Tasks

### Adding New News Sites
1. Edit `data/sites.json`
2. Add site configuration with URL and group
3. For RSS support, add feed URL to `scripts/scraper_rss.py`
4. Add site-specific extractor if needed in `scripts/scraper.py`
5. Test through dashboard

### Modifying Scraping Logic
1. Edit `scripts/scraper.py` for traditional method
2. Edit `scripts/scraper_rss.py` for RSS feeds
3. Edit `scripts/scraper_hybrid.py` for hybrid method
4. Update selectors or parsing logic
5. Test via manual trigger

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
3. **Scraping fails**: 
   - Check news site selectors in `sites.json`
   - Try switching to RSS or hybrid method in settings
   - Check if site has bot protection (403 errors)
4. **AI summary fails**: 
   - Verify `GOOGLE_GEMINI_API_KEY`
   - Check daily quota (50 requests for free tier)
5. **No articles scraped (0개 기사)**:
   - URL 패턴이 너무 엄격한지 확인 (대소문자 구분 문제)
   - 뉴스 사이트 HTML 구조 변경 확인
   - `scripts/scraper.py`의 is_valid_article_url 함수 점검
   - RSS 방식으로 전환 시도 (`scrapingMethod: "rss"` 또는 `"hybrid"`)
6. **Bot blocking (403 Forbidden)**:
   - Use RSS feeds instead of direct scraping
   - Implement request delays
   - Rotate User-Agent headers

### Log Locations
- GitHub Actions: Actions tab in repository
- Vercel: Function logs in Vercel dashboard
- Client: Browser console

## Development Notes
- Korean language support throughout
- Timezone: Korea Standard Time (KST)
- Scheduled runs: 07:59 KST (하루 1회로 설정됨)
- WhatsApp channels: Test and backup channels configured
- Scraping methods: traditional, ai, rss, hybrid (default: hybrid)
- News sources: 11 sites across News, Economy, Lifestyle, Politics, Culture, Technology groups

## Dependencies
- Node.js 16+
- Python 3.x
- @octokit/rest for GitHub API
- requests, beautifulsoup4, selenium for scraping
- google-generativeai for AI summaries
- feedparser for RSS feed parsing
- pytz for timezone handling

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

### 2025-07-21 스크래핑 성능 개선 및 배포 문제 해결
**시간**: 오후 6시 - 오후 7시  
**상태**: ✅ 완료

**수행 작업**:

1. **스크래핑 성능 문제 해결**:
   - **문제**: BrokenPipeError로 인한 스크래핑 실패
   - **원인**: 과도한 DEBUG 출력으로 파이프 오류 발생
   - **해결**: 
     - `DEBUG_MODE` 환경 변수 추가로 디버그 출력 제어
     - 모든 DEBUG print 문을 조건부로 변경
     - `scripts/scraper.py` 전체 수정

2. **콘텐츠 추출 개선**:
   - **문제**: 60개 링크 중 1개만 기사로 인식
   - **원인**: 너무 엄격한 콘텐츠 검증 규칙
   - **해결**:
     - `is_real_article_content()` 함수 완화
     - 최소 텍스트 길이: 30 → 20자
     - 최소 문장 수: 2 → 1개
     - 최소 단어 수: 20 → 10개
     - 더 많은 콘텐츠 선택자 추가
   - **결과**: 1개 → 3개 기사로 증가

3. **GitHub 배포 문제 해결**:
   - **문제**: 대시보드에 7월 19일 기사만 표시
   - **원인**: `.gitignore`에 `data/scraped/*` 포함되어 있어 스크래핑 파일이 커밋되지 않음
   - **해결**: 
     - `.gitignore`에서 해당 줄 주석 처리
     - 7월 21일 스크래핑 파일 5개 수동 커밋
     - API가 올바른 최신 파일 반환하도록 수정

4. **WhatsApp 전송 오류 수정**:
   - **문제**: ModuleNotFoundError: No module named 'pytz'
   - **원인**: `requirements.txt`에 pytz 누락
   - **해결**: `pytz==2024.1` 추가

**기술적 개선사항**:
- 스크래핑 방법: AI → traditional로 변경 (성능 향상)
- 사이트당 기사 수: 8 → 3개로 축소
- GitHub Actions 타임아웃: 30분으로 증가

**최종 결과**:
- ✅ 스크래핑 성공: 3개 기사 수집 (News 1개, Economy 2개)
- ✅ GitHub 배포 완료: 7월 21일 기사 정상 표시
- ✅ WhatsApp 전송 준비 완료: pytz 의존성 해결

**체크포인트**: 
- `★ 2025-07-21 오후 7시 정상 동작 확인 - 스크래핑 및 배포 안정화`

### 2025-07-21 대시보드 동적 날짜 표시 확인
**시간**: 오후 10시  
**상태**: ✅ 확인 완료

**현황 분석**:
1. **스크래핑 상태**:
   - 최신 스크래핑: 2025-07-21 13:04 (news_20250721_130443.json)
   - 수집된 기사: 1개 (Economy 그룹)
   - 스크래핑 정상 작동 중

2. **대시보드 날짜 표시 동작**:
   - 동적으로 날짜를 반영하도록 구현됨 (app.js:2198)
   - 오늘 날짜와 스크랩 파일 날짜 비교
   - 같은 날: "오늘 스크랩한 기사"
   - 다른 날: "MM/DD 스크랩한 기사" (예: "07/19 스크랩한 기사")
   - **정상 작동 확인**: 최신 파일 날짜에 따라 자동 반영

3. **최근 스크래핑 이력**:
   - 7/19: 마지막 정상 스크래핑 (여러 기사)
   - 7/20: 스크래핑 실패 (URL 패턴 문제)
   - 7/21: URL 패턴 수정 후 스크래핑 재개

**결론**:
- 대시보드 날짜 표시는 정상적으로 동적 반영 중
- 스크래핑 기능 정상 작동 확인
- URL 패턴 수정 효과 확인됨

### 2025-07-22 스크래핑 실패 분석 및 대체 방안 구현
**시간**: 오전 12시 - 오전 12시 43분  
**상태**: ✅ 완료

**문제 상황**:
- 7개 사이트 중 2개만 스크래핑 성공 (Channel NewsAsia, Yahoo Singapore)
- The Straits Times, Business Times: 간헐적 작동
- Mothership: 403 봇 차단
- The Independent Singapore: 작동 안함
- TODAY Online: 도메인 차단

**수행 작업**:

1. **스크래핑 실패 원인 분석**:
   - URL 패턴 검증이 너무 엄격함
   - 사이트별 봇 차단 정책 (Mothership 403 에러)
   - HTML 구조 변경으로 셀렉터 불일치
   - 동적 콘텐츠 로딩 문제

2. **URL 패턴 및 셀렉터 개선**:
   - Straits Times: 구체적인 기사 셀렉터 추가
   - Generic extractor: 더 많은 공통 셀렉터 추가
   - Independent Singapore: 전용 추출기 구현 (WordPress 기반)
   - User-Agent 헤더 개선 및 다양화

3. **RSS 피드 기반 스크래핑 구현**:
   - `scripts/scraper_rss.py` 생성
   - RSS 피드 지원 사이트:
     - Mothership: https://mothership.sg/feed/
     - Channel NewsAsia: API RSS feed
     - The Independent Singapore: https://theindependent.sg/feed/
     - Singapore Business Review: https://sbr.com.sg/news.rss
     - Yahoo Singapore: https://sg.news.yahoo.com/rss/
   - 봇 차단 회피 가능, 안정적인 데이터 수집

4. **하이브리드 스크래핑 방식 구현**:
   - `scripts/scraper_hybrid.py` 생성
   - RSS 우선 시도 → 실패 시 전통적 방식
   - 최대한 많은 기사 수집 가능
   - 그룹당 최대 5개 기사까지 수집

5. **추가 뉴스 소스 확대**:
   - The New Paper
   - Tech in Asia
   - The Edge Singapore
   - AsiaOne
   - 총 11개 뉴스 소스로 확대

6. **스크래핑 방식 설정**:
   - traditional: 기존 HTML 파싱 방식
   - ai: AI 기반 스크래핑 (Gemini API)
   - rss: RSS 피드 전용
   - hybrid: RSS + 전통적 방식 결합 (기본값)

**기술적 개선사항**:
- feedparser 라이브러리 추가 (requirements.txt)
- 다양한 User-Agent 헤더 풀 구현
- Accept, Accept-Language 등 추가 헤더
- 사이트별 맞춤 헤더 설정

**최종 결과**:
- RSS 방식: 7개 기사 수집 성공 (Mothership 3, CNA 1, Independent 3)
- 하이브리드 방식: 8개 기사 수집 (RSS + Business Times 추가)
- 성공률: 29% → 73% 향상

**남은 제한사항**:
- Straits Times: 페이월 및 구조 변경
- TODAY Online: 도메인 자체 차단
- 일부 사이트: JavaScript 렌더링 필요

**체크포인트**: 
- `★ 25. 7. 22. 오전 12시 43분 동작 확인`
- 하이브리드 방식으로 안정적인 뉴스 수집 확보

### 2025-07-22 WhatsApp 메시지 형식 개선
**시간**: 오후 10시 - 오후 10시 23분  
**상태**: ✅ 완료

**수행 작업**:
1. **가로줄 제거**: 
   - 모든 구분선(━━━) 제거
   - 헤더, 그룹 구분, 푸터의 가로줄 모두 제거
   - 더 간결하고 깔끔한 메시지 형식

2. **파일 수정**:
   - `scripts/send_whatsapp_green.py` 업데이트
   - 4개 위치의 가로줄 제거

**결과**:
- 모바일 화면에서 더 나은 가독성
- 불필요한 시각적 요소 제거
- 깔끔한 WhatsApp 메시지 포맷

**체크포인트**: 
- `★ 25.7.22 오후 10시 23분 정상 동작 확인`

### 2025-07-22 WhatsApp 메시지 형식 개선
**시간**: 오전 1시 - 1시 8분  
**상태**: ✅ 완료

**수행 작업**:
1. **구분선 길이 조정**: 25자 → 22자 (10% 축소)
   - 모바일 화면에서 더 나은 가독성
   - 모든 구분선에 일괄 적용

2. **시간 표시 수정**: UTC → KST (한국 표준시)
   - pytz 라이브러리 활용한 정확한 시간대 변환
   - 잘못된 시간 표시 문제 해결 (15:56 → 00:56)

**체크포인트**: 
- `★ 2025. 7. 22 오전 1시 8분 정상 동작 확인`