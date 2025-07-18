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

### Log Locations
- GitHub Actions: Actions tab in repository
- Vercel: Function logs in Vercel dashboard
- Client: Browser console

## Development Notes
- Korean language support throughout
- Timezone: Korea Standard Time (KST)
- Scheduled runs: 09:00, 13:00, 18:00 KST
- WhatsApp channels: Test and backup channels configured

## Dependencies
- Node.js 16+
- Python 3.x
- @octokit/rest for GitHub API
- requests, beautifulsoup4, selenium for scraping
- google-generativeai for AI summaries