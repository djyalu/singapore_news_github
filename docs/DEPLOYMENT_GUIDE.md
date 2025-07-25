# Deployment Guide / 배포 가이드

## Table of Contents / 목차
1. [Prerequisites / 사전 요구사항](#prerequisites--사전-요구사항)
2. [Initial Setup / 초기 설정](#initial-setup--초기-설정)
3. [GitHub Setup / GitHub 설정](#github-setup--github-설정)
4. [Vercel Deployment / Vercel 배포](#vercel-deployment--vercel-배포)
5. [GitHub Actions Setup / GitHub Actions 설정](#github-actions-setup--github-actions-설정)
6. [Environment Configuration / 환경 설정](#environment-configuration--환경-설정)
7. [Domain Configuration / 도메인 설정](#domain-configuration--도메인-설정)
8. [Testing Deployment / 배포 테스트](#testing-deployment--배포-테스트)
9. [Production Deployment / 프로덕션 배포](#production-deployment--프로덕션-배포)
10. [Rollback Procedures / 롤백 절차](#rollback-procedures--롤백-절차)

## Prerequisites / 사전 요구사항

### Required Accounts / 필수 계정
- [ ] GitHub account / GitHub 계정
- [ ] Vercel account / Vercel 계정
- [ ] Google Cloud account (for Gemini API) / Google Cloud 계정
- [ ] Green API account (for WhatsApp) / Green API 계정

### Required Tools / 필수 도구
```bash
# Check installations
git --version          # Git 2.30+
node --version         # Node.js 16+
npm --version          # npm 7+
python --version       # Python 3.8+
```

### API Keys Required / 필요한 API 키
```
1. GitHub Personal Access Token
2. Google Gemini API Key
3. Green API WhatsApp Key
```

## Initial Setup / 초기 설정

### 1. Fork Repository / 저장소 포크
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/singapore_news_github.git
cd singapore_news_github
```

### 2. Install Dependencies / 의존성 설치
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (if developing locally)
npm install
```

### 3. Configure Git / Git 설정
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## GitHub Setup / GitHub 설정

### 1. Create GitHub Personal Access Token / GitHub 개인 액세스 토큰 생성
```
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Name: "Singapore News Scraper"
4. Expiration: 90 days (or longer)
5. Select scopes:
   ✓ repo (Full control)
   ✓ workflow (Update GitHub Action workflows)
6. Generate token and save it
```

### 2. Configure Repository Settings / 저장소 설정
```
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)
5. Save

# Wait for deployment (check Actions tab)
# Your site will be available at:
https://YOUR_USERNAME.github.io/singapore_news_github/
```

### 3. Add Repository Secrets / 저장소 시크릿 추가
```
Settings → Secrets and variables → Actions → New repository secret

Add:
- Name: GOOGLE_GEMINI_API_KEY
- Value: your_gemini_api_key
```

### 4. Enable GitHub Actions / GitHub Actions 활성화
```
1. Go to Actions tab
2. Enable workflows if prompted
3. Verify workflows are visible:
   - Singapore News Scraper
   - Scrape News Only
   - Send to WhatsApp
```

## Vercel Deployment / Vercel 배포

### 1. Import Project to Vercel / Vercel에 프로젝트 가져오기
```
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import Git Repository
4. Select your forked repository
5. Configure Project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. Click "Deploy"
```

### 2. Configure Environment Variables / 환경 변수 설정
```
Project Settings → Environment Variables

Add the following:
┌─────────────────────┬──────────────────────────┐
│ Variable Name       │ Value                    │
├─────────────────────┼──────────────────────────┤
│ GITHUB_TOKEN        │ ghp_xxxxxxxxxx          │
│ GITHUB_OWNER        │ YOUR_USERNAME           │
│ GITHUB_REPO         │ singapore_news_github    │
│ WHATSAPP_API_KEY    │ instance:token          │
└─────────────────────┴──────────────────────────┘
```

### 3. Configure Vercel Functions / Vercel 함수 설정
```json
// vercel.json is already configured
{
  "functions": {
    "api/*.js": {
      "maxDuration": 60
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" }
      ]
    }
  ]
}
```

### 4. Verify Deployment / 배포 확인
```bash
# Your API endpoints will be available at:
https://YOUR_PROJECT.vercel.app/api/trigger-scraping
https://YOUR_PROJECT.vercel.app/api/get-scraping-status
# ... etc
```

## GitHub Actions Setup / GitHub Actions 설정

### 1. Update Workflow Files / 워크플로우 파일 업데이트
```yaml
# .github/workflows/scraper.yml
# Update the API_URL to your Vercel deployment
env:
  API_URL: https://YOUR_PROJECT.vercel.app
```

### 2. Configure Scheduled Runs / 예약 실행 설정
```yaml
# Current schedule: 7:55 AM KST daily
on:
  schedule:
    - cron: '55 22 * * *'  # 22:55 UTC = 07:55 KST
  workflow_dispatch:       # Manual trigger enabled
```

### 3. Set Workflow Permissions / 워크플로우 권한 설정
```
Repository Settings → Actions → General
→ Workflow permissions
→ Select "Read and write permissions"
→ Save
```

## Environment Configuration / 환경 설정

### 1. Update Frontend Configuration / 프론트엔드 설정 업데이트
```javascript
// js/config.js - Create this file
const CONFIG = {
    API_BASE_URL: 'https://YOUR_PROJECT.vercel.app',
    GITHUB_PAGES_URL: 'https://YOUR_USERNAME.github.io/singapore_news_github'
};
```

### 2. Update API Endpoints / API 엔드포인트 업데이트
```javascript
// In js/app.js, update all API calls
const API_BASE = 'https://YOUR_PROJECT.vercel.app';

// Example:
fetch(`${API_BASE}/api/get-latest-scraped`)
```

### 3. Configure CORS / CORS 설정
```javascript
// Already configured in vercel.json
// Additional CORS for specific domains:
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { 
          "key": "Access-Control-Allow-Origin", 
          "value": "https://YOUR_USERNAME.github.io" 
        }
      ]
    }
  ]
}
```

## Domain Configuration / 도메인 설정

### 1. Custom Domain for GitHub Pages / GitHub Pages 커스텀 도메인
```
1. Repository Settings → Pages
2. Custom domain: your-domain.com
3. Enforce HTTPS: ✓
4. Create CNAME file in root:
   echo "your-domain.com" > CNAME
5. Configure DNS:
   - A records: 185.199.108-111.153
   - CNAME: YOUR_USERNAME.github.io
```

### 2. Custom Domain for Vercel / Vercel 커스텀 도메인
```
1. Vercel Project Settings → Domains
2. Add domain: api.your-domain.com
3. Configure DNS:
   - CNAME: cname.vercel-dns.com
4. Wait for SSL certificate
```

### 3. Update Configuration / 설정 업데이트
```javascript
// After domain setup, update all URLs
const CONFIG = {
    API_BASE_URL: 'https://api.your-domain.com',
    GITHUB_PAGES_URL: 'https://your-domain.com'
};
```

## Testing Deployment / 배포 테스트

### 1. Frontend Tests / 프론트엔드 테스트
```bash
# Test GitHub Pages deployment
curl -I https://YOUR_USERNAME.github.io/singapore_news_github/
# Should return 200 OK

# Test resources loading
curl https://YOUR_USERNAME.github.io/singapore_news_github/css/styles.css
curl https://YOUR_USERNAME.github.io/singapore_news_github/js/app.js
```

### 2. API Tests / API 테스트
```bash
# Test API health
curl https://YOUR_PROJECT.vercel.app/api/test-env
# Should return environment status

# Test data endpoints
curl https://YOUR_PROJECT.vercel.app/api/get-latest-scraped
# Should return latest scraped data

# Test authentication
curl -X POST https://YOUR_PROJECT.vercel.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'
```

### 3. Scraping Test / 스크래핑 테스트
```bash
# Trigger test scraping
curl -X POST https://YOUR_PROJECT.vercel.app/api/scrape-only

# Monitor progress
curl https://YOUR_PROJECT.vercel.app/api/get-scraping-status
```

### 4. WhatsApp Test / WhatsApp 테스트
```bash
# Send test message
curl -X POST https://YOUR_PROJECT.vercel.app/api/test-whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message":"Deployment test successful!"}'
```

## Production Deployment / 프로덕션 배포

### 1. Pre-deployment Checklist / 배포 전 체크리스트
- [ ] All tests passing / 모든 테스트 통과
- [ ] Environment variables set / 환경 변수 설정 완료
- [ ] API keys valid / API 키 유효성 확인
- [ ] Backup current data / 현재 데이터 백업
- [ ] Update documentation / 문서 업데이트

### 2. Deploy to Production / 프로덕션 배포
```bash
# 1. Tag the release
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# 2. Merge to main branch
git checkout main
git merge development
git push origin main

# 3. Verify GitHub Pages deployment
# Check Actions tab for deployment status

# 4. Verify Vercel deployment
# Vercel auto-deploys on push to main
```

### 3. Post-deployment Verification / 배포 후 검증
```bash
# Run full system check
./scripts/health_check.sh

# Verify scheduled actions
# Check GitHub Actions schedule is active

# Monitor first automated run
# Wait for next scheduled run at 07:55 KST
```

### 4. Production Monitoring / 프로덕션 모니터링
```javascript
// Set up monitoring alerts
1. Vercel Dashboard → Project → Settings → Notifications
2. Enable email alerts for:
   - Function errors
   - High response times
   - Failed deployments

3. GitHub → Settings → Notifications
4. Watch repository for:
   - Action failures
   - Issues
   - Pull requests
```

## Rollback Procedures / 롤백 절차

### 1. Quick Rollback / 빠른 롤백
```bash
# Vercel instant rollback
1. Go to Vercel Dashboard
2. Select project → Deployments
3. Find previous stable deployment
4. Click "..." → "Promote to Production"

# GitHub Pages rollback
git revert HEAD
git push origin main
```

### 2. Full Rollback / 전체 롤백
```bash
# Revert to specific version
git checkout v0.9.0
git checkout -b rollback-v0.9.0
git push origin rollback-v0.9.0

# Update GitHub Pages
Settings → Pages → Branch: rollback-v0.9.0
```

### 3. Data Rollback / 데이터 롤백
```bash
# Restore data from backup
git checkout <commit-hash> -- data/
git commit -m "Rollback data to <date>"
git push origin main
```

### 4. Emergency Procedures / 비상 절차
```bash
# If system is completely down
1. Disable GitHub Actions workflows
2. Set Vercel environment variable:
   MAINTENANCE_MODE=true
3. Display maintenance page
4. Investigate and fix issues
5. Re-enable services gradually
```

## Deployment Best Practices / 배포 모범 사례

### 1. Staging Environment / 스테이징 환경
```bash
# Create staging branch
git checkout -b staging
git push origin staging

# Deploy to staging Vercel
# Create separate Vercel project for staging
# Test thoroughly before production
```

### 2. Blue-Green Deployment / 블루-그린 배포
```
1. Deploy new version to "green" environment
2. Test green environment thoroughly
3. Switch traffic from "blue" to "green"
4. Keep blue as instant rollback option
```

### 3. Feature Flags / 기능 플래그
```javascript
// Implement feature toggles
const FEATURES = {
    NEW_SCRAPER: process.env.ENABLE_NEW_SCRAPER === 'true',
    AI_SUMMARIES: process.env.ENABLE_AI_SUMMARIES === 'true'
};

// Gradual rollout
if (FEATURES.NEW_SCRAPER) {
    // Use new scraper
} else {
    // Use old scraper
}
```

### 4. Monitoring and Alerts / 모니터링 및 알림
```yaml
# Add to GitHub Actions
- name: Notify deployment
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment ${{ job.status }}'
  if: always()
```

## Troubleshooting Deployment / 배포 문제 해결

### Common Issues / 일반적인 문제

#### 1. GitHub Pages 404 Error
```bash
# Check repository settings
# Ensure Pages is enabled and branch is correct
# Check CNAME file if using custom domain
# Wait 10 minutes for propagation
```

#### 2. Vercel Function Timeout
```javascript
// Increase timeout in vercel.json
{
  "functions": {
    "api/*.js": {
      "maxDuration": 60  // Maximum for free tier
    }
  }
}
```

#### 3. CORS Errors
```javascript
// Ensure headers are set correctly
// Check browser console for specific origin
// Update allowed origins in vercel.json
```

#### 4. API Key Issues
```bash
# Verify environment variables
curl https://YOUR_PROJECT.vercel.app/api/test-env

# Check variable names match exactly
# Ensure no extra spaces or quotes
```

---
*Last Updated: January 25, 2025*