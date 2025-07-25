# Administrator Guide / 관리자 가이드

## Table of Contents / 목차
1. [System Overview / 시스템 개요](#system-overview--시스템-개요)
2. [Access Management / 접근 관리](#access-management--접근-관리)
3. [Configuration Management / 설정 관리](#configuration-management--설정-관리)
4. [Scraping Management / 스크래핑 관리](#scraping-management--스크래핑-관리)
5. [WhatsApp Management / WhatsApp 관리](#whatsapp-management--whatsapp-관리)
6. [Data Management / 데이터 관리](#data-management--데이터-관리)
7. [Monitoring / 모니터링](#monitoring--모니터링)
8. [Maintenance / 유지보수](#maintenance--유지보수)
9. [Emergency Procedures / 비상 절차](#emergency-procedures--비상-절차)

## System Overview / 시스템 개요

### Architecture Components / 아키텍처 구성요소
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   GitHub Pages  │────▶│  Vercel APIs    │────▶│ GitHub Actions  │
│   (Frontend)    │     │   (Backend)     │     │  (Automation)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                         ┌───────▼────────┐
                         │ GitHub Storage │
                         │  (JSON Files)  │
                         └────────────────┘
```

### Key Responsibilities / 주요 책임
- **System Configuration / 시스템 설정**: Managing settings.json and sites.json
- **User Management / 사용자 관리**: Authentication and access control
- **Scraping Control / 스크래핑 제어**: Manual triggers and monitoring
- **Data Integrity / 데이터 무결성**: Backup and recovery procedures
- **Performance Monitoring / 성능 모니터링**: System health checks

## Access Management / 접근 관리

### 1. Admin Credentials / 관리자 자격증명
```javascript
// Default credentials (CHANGE IMMEDIATELY)
Username: admin
Password: Admin@123
```

### 2. Changing Admin Password / 관리자 비밀번호 변경
```javascript
// Edit js/auth.js
const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'YourNewSecurePassword123!' // Change this
};
```

### 3. API Token Management / API 토큰 관리

#### Vercel Environment Variables
```bash
# Required tokens
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=djyalu
GITHUB_REPO=singapore_news_github
WHATSAPP_API_KEY=your_green_api_key
```

#### GitHub Secrets
```bash
# In repository settings
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
```

### 4. Access Logs / 접근 로그
```javascript
// Monitor access via Vercel dashboard
// Path: Project > Functions > Logs

// Check for unauthorized access attempts
grep "401" /var/log/vercel/functions.log
```

## Configuration Management / 설정 관리

### 1. Main Configuration File / 주요 설정 파일
```json
// data/settings.json
{
    "scrapingEnabled": true,
    "scrapingMethod": "hybrid_ai", // Options: traditional, ai, hybrid_ai
    "whatsappEnabled": true,
    "maxArticlesPerGroup": 5,
    "schedule": {
        "time": "07:55",
        "timezone": "Asia/Seoul"
    },
    "whatsapp": {
        "channels": ["65XXXXXXXX", "65YYYYYYYY"],
        "messageFormat": "summary" // Options: summary, full, links
    }
}
```

### 2. Site Configuration / 사이트 설정
```json
// data/sites.json
{
    "sites": [
        {
            "name": "The Straits Times",
            "url": "https://www.straitstimes.com/singapore",
            "group": "politics",
            "enabled": true,
            "priority": "high", // high, medium, low
            "selectors": {
                "article": "article.card",
                "title": "h3.card-title",
                "link": "a.card-link"
            }
        }
    ]
}
```

### 3. Configuration Updates / 설정 업데이트

#### Via Dashboard / 대시보드를 통해
1. Login to dashboard / 대시보드 로그인
2. Navigate to Settings / 설정으로 이동
3. Modify configuration / 설정 수정
4. Click "Save Settings" / "설정 저장" 클릭

#### Via API / API를 통해
```bash
# Update settings
curl -X POST https://singapore-news-github.vercel.app/api/save-data \
  -H "Content-Type: application/json" \
  -d '{
    "type": "settings",
    "settings": {
        "scrapingEnabled": true,
        "scrapingMethod": "ai"
    }
  }'
```

## Scraping Management / 스크래핑 관리

### 1. Manual Scraping Trigger / 수동 스크래핑 실행

#### Via Dashboard / 대시보드에서
```
1. Click "지금 스크래핑" button
2. Select scraping method
3. Monitor progress in real-time
```

#### Via API / API 호출
```bash
# Trigger full scraping + WhatsApp
curl -X POST https://singapore-news-github.vercel.app/api/trigger-scraping

# Scraping only
curl -X POST https://singapore-news-github.vercel.app/api/scrape-only
```

### 2. Scraping Methods / 스크래핑 방법

#### Traditional Method / 전통적 방법
- **Pros / 장점**: Fast, reliable / 빠르고 안정적
- **Cons / 단점**: Limited content extraction / 제한적 콘텐츠 추출
- **Use when / 사용 시기**: Sites block AI scrapers / 사이트가 AI 차단할 때

#### AI Method / AI 방법
- **Pros / 장점**: Better summaries / 더 나은 요약
- **Cons / 단점**: Slower, API limits / 느림, API 제한
- **Use when / 사용 시기**: Quality is priority / 품질이 우선일 때

#### Hybrid AI Method / 하이브리드 AI 방법
- **Pros / 장점**: Best of both worlds / 두 방법의 장점
- **Cons / 단점**: Complex debugging / 복잡한 디버깅
- **Use when / 사용 시기**: Default recommendation / 기본 권장사항

### 3. Monitoring Scraping Status / 스크래핑 상태 모니터링
```bash
# Check current status
curl https://singapore-news-github.vercel.app/api/get-scraping-status

# Response example
{
    "status": "running",
    "progress": 45,
    "currentSite": "Channel NewsAsia",
    "articlesCollected": 23,
    "startTime": "2025-01-25T08:00:00+09:00"
}
```

### 4. Troubleshooting Scraping Issues / 스크래핑 문제 해결

#### No Articles Collected / 기사 수집 안됨
```bash
# Check GitHub Actions logs
1. Go to Actions tab
2. Select failed workflow
3. Check step logs

# Common issues:
- Site structure changed
- Bot detection triggered
- API rate limits exceeded
```

#### Partial Collection / 부분 수집
```javascript
// Update selectors in sites.json
{
    "selectors": {
        "article": "new-selector",
        "title": "h2.new-title-class"
    }
}
```

## WhatsApp Management / WhatsApp 관리

### 1. Green API Configuration / Green API 설정
```javascript
// Environment variable
WHATSAPP_API_KEY=your_instance_id:your_token

// Test configuration
curl -X POST https://singapore-news-github.vercel.app/api/test-whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message from admin"}'
```

### 2. Channel Management / 채널 관리
```json
// Add/remove channels in settings.json
{
    "whatsapp": {
        "channels": [
            "6591234567",  // Main channel
            "6598765432"   // Backup channel
        ],
        "testMode": false
    }
}
```

### 3. Message Format Customization / 메시지 형식 사용자화
```python
# Edit scripts/send_whatsapp_green.py
def format_message(articles):
    header = "📰 싱가포르 뉴스 요약\n"
    # Customize format here
    return formatted_message
```

### 4. Sending History / 전송 기록
```bash
# Check sending history
ls -la data/history/

# View specific history
cat data/history/whatsapp_20250125_080000.json
```

## Data Management / 데이터 관리

### 1. Storage Structure / 저장 구조
```
data/
├── settings.json       # System settings / 시스템 설정
├── sites.json         # Site configurations / 사이트 설정
├── latest.json        # Latest scraped data / 최신 스크랩 데이터
├── scraped/           # Historical data / 과거 데이터
│   ├── news_20250125_080000.json
│   └── ...
└── history/           # WhatsApp history / WhatsApp 기록
    ├── whatsapp_20250125_080000.json
    └── ...
```

### 2. Data Retention Policy / 데이터 보존 정책
```python
# Automatic cleanup after 30 days
# Run scripts/cleanup_old_data.py

# Manual cleanup
python scripts/cleanup_old_data.py --days 15 --dry-run
python scripts/cleanup_old_data.py --days 15 --confirm
```

### 3. Backup Procedures / 백업 절차

#### Manual Backup / 수동 백업
```bash
# Create backup
git add data/
git commit -m "Backup: $(date +%Y%m%d_%H%M%S)"
git push origin backup-$(date +%Y%m%d)

# Restore from backup
git checkout backup-20250125 -- data/
```

#### Automated Backup / 자동 백업
```yaml
# Add to .github/workflows/backup.yml
name: Daily Backup
on:
  schedule:
    - cron: '0 12 * * *'  # Daily at 9 PM KST
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create backup
        run: |
          git config user.name "Backup Bot"
          git config user.email "bot@example.com"
          git add data/
          git commit -m "Automated backup: $(date)" || true
          git push || true
```

### 4. Data Export / 데이터 내보내기
```javascript
// Export via dashboard
1. Go to "스크랩 관리" (Scrape Management)
2. Select date range
3. Click "Export" button

// Export via script
node scripts/export_data.js --from 2025-01-01 --to 2025-01-31 --format csv
```

## Monitoring / 모니터링

### 1. System Health Checks / 시스템 상태 확인

#### Dashboard Status / 대시보드 상태
```javascript
// Check all systems
const healthCheck = {
    frontend: checkGitHubPages(),
    backend: checkVercelAPIs(),
    automation: checkGitHubActions(),
    storage: checkDataIntegrity()
};
```

#### API Health / API 상태
```bash
# Health check endpoint
curl https://singapore-news-github.vercel.app/api/health

# Expected response
{
    "status": "healthy",
    "services": {
        "github": "connected",
        "whatsapp": "connected",
        "gemini": "connected"
    },
    "uptime": "45 days"
}
```

### 2. Performance Metrics / 성능 지표
```javascript
// Monitor in Vercel dashboard
- API response times
- Function invocations
- Error rates
- Data transfer

// Alert thresholds
- Response time > 3s
- Error rate > 5%
- Failed scrapers > 3
```

### 3. Log Analysis / 로그 분석
```bash
# GitHub Actions logs
- Go to Actions tab
- Filter by workflow
- Check run duration and status

# Vercel function logs
- Login to Vercel
- Select project
- View function logs
- Filter by error level
```

### 4. Setting Up Alerts / 알림 설정
```javascript
// Email alerts for failures
// Add to GitHub Actions workflow
- name: Send failure notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Scraping Failed - ${{ github.run_number }}
    to: admin@example.com
```

## Maintenance / 유지보수

### 1. Regular Maintenance Tasks / 정기 유지보수 작업

#### Daily / 일일
- [ ] Check scraping success rate / 스크래핑 성공률 확인
- [ ] Verify WhatsApp delivery / WhatsApp 전송 확인
- [ ] Monitor error logs / 오류 로그 모니터링

#### Weekly / 주간
- [ ] Review collected articles quality / 수집 기사 품질 검토
- [ ] Check API usage limits / API 사용량 확인
- [ ] Update site selectors if needed / 필요시 사이트 선택자 업데이트

#### Monthly / 월간
- [ ] Clean old data files / 오래된 데이터 정리
- [ ] Review and optimize performance / 성능 검토 및 최적화
- [ ] Update dependencies / 의존성 업데이트
- [ ] Security audit / 보안 감사

### 2. Updating Dependencies / 의존성 업데이트
```bash
# Python dependencies
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt

# Node.js dependencies
npm update
npm audit fix
```

### 3. Site Selector Updates / 사이트 선택자 업데이트
```javascript
// When sites change their HTML structure
1. Inspect the site's new structure
2. Update selectors in sites.json
3. Test with single site scraping
4. Deploy changes

// Example update
{
    "selectors": {
        "article": "div.new-article-class",
        "title": "h2.new-title",
        "link": "a.article-link"
    }
}
```

### 4. Performance Optimization / 성능 최적화
```python
# Optimize scraping
- Reduce concurrent requests
- Implement caching
- Use connection pooling
- Optimize AI API calls

# Settings for optimization
{
    "performance": {
        "maxConcurrentRequests": 3,
        "requestTimeout": 30,
        "cacheEnabled": true,
        "cacheDuration": 3600
    }
}
```

## Emergency Procedures / 비상 절차

### 1. System Down / 시스템 다운

#### Immediate Actions / 즉시 조치
```bash
# 1. Check service status
curl -I https://djyalu.github.io/singapore_news_github/
curl https://singapore-news-github.vercel.app/api/health

# 2. Check GitHub status
https://www.githubstatus.com/

# 3. Check Vercel status
https://www.vercel-status.com/
```

#### Recovery Steps / 복구 단계
1. Identify the failed component / 실패한 구성요소 식별
2. Check error logs / 오류 로그 확인
3. Rollback if necessary / 필요시 롤백
4. Test functionality / 기능 테스트
5. Monitor for stability / 안정성 모니터링

### 2. Data Corruption / 데이터 손상
```bash
# Restore from GitHub
git log --oneline data/
git checkout <commit-hash> -- data/

# Validate JSON files
python -m json.tool data/settings.json
python -m json.tool data/sites.json
```

### 3. API Limits Exceeded / API 한도 초과
```javascript
// Temporary solutions
1. Switch scraping method to "traditional"
2. Reduce maxArticlesPerGroup
3. Disable non-critical sites
4. Wait for limit reset

// Long-term solutions
1. Upgrade API plan
2. Implement better caching
3. Optimize API usage
```

### 4. Security Breach / 보안 침해
```bash
# Immediate actions
1. Revoke all API tokens
2. Change admin password
3. Review access logs
4. Generate new tokens
5. Update all credentials
6. Audit recent changes

# Prevention
- Regular security audits
- Token rotation policy
- Access log monitoring
- Dependency scanning
```

### 5. Emergency Contacts / 비상 연락처
```
Technical Support: tech@example.com
Security Issues: security@example.com
WhatsApp Support: +65 1234 5678
On-call Admin: +65 8765 4321
```

## Best Practices / 모범 사례

### 1. Change Management / 변경 관리
- Always test in development first / 항상 개발 환경에서 먼저 테스트
- Document all changes / 모든 변경사항 문서화
- Keep backups before major changes / 주요 변경 전 백업 유지
- Use version control effectively / 버전 관리 효과적 사용

### 2. Security / 보안
- Rotate API keys quarterly / 분기별 API 키 교체
- Use strong passwords / 강력한 비밀번호 사용
- Monitor access logs / 접근 로그 모니터링
- Keep dependencies updated / 의존성 최신 유지

### 3. Communication / 커뮤니케이션
- Notify users of maintenance / 유지보수 사용자 알림
- Document issues and resolutions / 문제와 해결책 문서화
- Maintain change log / 변경 로그 유지
- Regular status updates / 정기 상태 업데이트

---
*Last Updated: January 25, 2025*