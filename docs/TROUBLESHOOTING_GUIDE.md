# Singapore News Scraper Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues with the Singapore News Scraper system.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Scraping Problems](#scraping-problems)
4. [WhatsApp Issues](#whatsapp-issues)
5. [API Errors](#api-errors)
6. [GitHub Actions Problems](#github-actions-problems)
7. [Authentication Issues](#authentication-issues)
8. [Performance Problems](#performance-problems)
9. [Data Issues](#data-issues)
10. [Advanced Troubleshooting](#advanced-troubleshooting)

## Quick Diagnostics

### System Health Check

1. **Check API Status**
```bash
curl https://your-app.vercel.app/api/test-env
```

Expected response:
```json
{
  "status": "OK",
  "environment": {
    "GITHUB_TOKEN": "configured",
    "GITHUB_OWNER": "djyalu",
    "GITHUB_REPO": "singapore_news_github",
    "WHATSAPP_API_KEY": "configured"
  }
}
```

2. **Check GitHub Actions**
- Visit: `https://github.com/[username]/singapore_news_github/actions`
- Look for recent runs and their status

3. **Check Frontend**
- Open browser console (F12)
- Look for JavaScript errors
- Check network tab for failed requests

## Common Issues

### Issue: "GitHub Token Not Configured"

**Symptoms:**
- Error message when triggering scraping
- API returns 500 error

**Solution:**
1. Go to Vercel Dashboard
2. Navigate to Settings → Environment Variables
3. Add/Update `GITHUB_TOKEN`
4. Redeploy the project

**Verification:**
```bash
curl https://your-app.vercel.app/api/test-env
```

### Issue: "No Articles Found"

**Symptoms:**
- Scraping completes but returns 0 articles
- Empty latest.json file

**Possible Causes:**
1. News sites changed their HTML structure
2. Bot detection/blocking
3. Network issues
4. Wrong scraping method

**Solutions:**

1. **Try different scraping method:**
```json
// In settings.json
{
  "scrapingMethod": "hybrid"  // Try: traditional, ai, rss, hybrid
}
```

2. **Check specific site manually:**
```python
# Test single site
python -c "
from scripts.scraper import scrape_site
result = scrape_site('https://www.straitstimes.com', 'The Straits Times', {})
print(f'Articles found: {len(result)}')"
```

3. **Enable debug mode:**
```bash
DEBUG_SCRAPER=true python scripts/scraper.py
```

### Issue: "Scraping Timeout"

**Symptoms:**
- GitHub Actions job times out
- Partial results saved

**Solutions:**

1. **Reduce number of articles per site:**
```json
// In settings.json
{
  "maxArticlesPerSite": 2  // Reduce from 3
}
```

2. **Increase workflow timeout:**
```yaml
# In .github/workflows/scraper.yml
jobs:
  scrape:
    timeout-minutes: 60  # Increase from 45
```

3. **Use faster scraping method:**
```json
{
  "scrapingMethod": "rss"  // Fastest method
}
```

## Scraping Problems

### Problem: Specific Site Not Working

**Diagnosis:**
```python
# Test specific site extractor
python scripts/test_site_scraper.py --site "The Straits Times"
```

**Common Fixes:**

1. **Update selectors** in `scraper.py`:
```python
def extract_articles_straitstimes(soup, base_url):
    # Check current HTML structure
    # Update selectors accordingly
    article_links = soup.find_all('a', class_='new-class-name')
```

2. **Add User-Agent rotation:**
```python
headers = {
    'User-Agent': random.choice([
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ])
}
```

### Problem: AI Scraping API Limit

**Symptoms:**
- "429 Too Many Requests" error
- Gemini API quota exceeded

**Solutions:**

1. **Implement better rate limiting:**
```python
# In ai_scraper.py
RATE_LIMIT = 14  # requests per minute (down from 15)
```

2. **Use caching more effectively:**
```python
# Check cache before API call
if url in self.cache:
    return self.cache[url]
```

3. **Reduce articles per site for AI mode:**
```python
# In ai_scraper_optimized.py
if settings.get('scrapingMethod') == 'ai':
    max_articles = min(2, settings.get('maxArticlesPerSite', 3))
```

## WhatsApp Issues

### Problem: Messages Not Sending

**Diagnosis:**
```python
# Test WhatsApp API directly
python scripts/test_whatsapp.py
```

**Common Fixes:**

1. **Verify Green API credentials:**
```python
# Check format: instanceId:apiToken
api_key = "1234567890:abcdef123456"
```

2. **Confirm bot is in group:**
- Send test message to group
- Check Green API dashboard for group ID

3. **Update channel ID:**
```json
// In settings.json
{
  "whatsappChannels": [{
    "id": "120363419092108413@g.us",  // Correct format
    "enabled": true
  }]
}
```

### Problem: Message Formatting Issues

**Symptoms:**
- Messages appear broken
- Emojis not displaying
- Links not clickable

**Solutions:**

1. **Check message encoding:**
```python
# In send_whatsapp_green.py
message = message.encode('utf-8').decode('utf-8')
```

2. **Validate message length:**
```python
MAX_MESSAGE_LENGTH = 4096
if len(message) > MAX_MESSAGE_LENGTH:
    message = message[:MAX_MESSAGE_LENGTH-3] + "..."
```

## API Errors

### Error: CORS Issues

**Symptoms:**
- "Access to fetch at ... has been blocked by CORS policy"

**Solution:**
Add proper CORS headers in API functions:
```javascript
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
```

### Error: Vercel Function Timeout

**Symptoms:**
- API returns 504 Gateway Timeout
- Function execution exceeds 10 seconds

**Solutions:**

1. **Optimize function code:**
```javascript
// Cache GitHub API responses
const cache = new Map();
```

2. **Use background jobs:**
```javascript
// Return immediately, process in background
res.status(202).json({ message: "Processing started" });
```

## GitHub Actions Problems

### Problem: Workflow Not Triggering

**Symptoms:**
- Scheduled runs not happening
- Manual triggers fail

**Diagnosis:**
```bash
# Check if workflows are enabled
gh workflow list --repo djyalu/singapore_news_github
```

**Solutions:**

1. **Re-enable workflows:**
- Push any commit to reactivate
- Check Actions tab → Enable workflows

2. **Verify cron syntax:**
```yaml
schedule:
  - cron: '55 22 * * *'  # Must be valid cron
```

3. **Check permissions:**
```yaml
permissions:
  contents: write
  actions: write
```

### Problem: Workflow Fails

**Common Error Messages and Solutions:**

1. **"Python module not found"**
```yaml
# Add to workflow
- name: Install dependencies
  run: pip install -r requirements.txt
```

2. **"Permission denied"**
```yaml
# Add write permissions
permissions:
  contents: write
```

3. **"Resource not accessible by integration"**
- Regenerate GitHub token with proper scopes
- Update token in Vercel

## Authentication Issues

### Problem: Can't Login

**Diagnosis:**
```javascript
// Check in browser console
console.log(sessionStorage.getItem('user'));
```

**Solutions:**

1. **Clear browser data:**
```javascript
sessionStorage.clear();
localStorage.clear();
```

2. **Reset password:**
```json
// Update settings.json manually
{
  "users": {
    "admin": {
      "password": "NewPassword123!",
      "role": "admin"
    }
  }
}
```

### Problem: Session Expires Too Quickly

**Solution:**
Implement remember me functionality:
```javascript
// In auth.js
if (rememberMe) {
    localStorage.setItem('authToken', token);
}
```

## Performance Problems

### Problem: Slow Dashboard Loading

**Diagnosis:**
- Check Network tab in browser
- Measure API response times

**Solutions:**

1. **Implement caching:**
```javascript
// Cache API responses
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
if (cache.timestamp > Date.now() - CACHE_DURATION) {
    return cache.data;
}
```

2. **Lazy load components:**
```javascript
// Load charts only when needed
if (document.querySelector('#chart-container')) {
    import('./charts.js').then(module => {
        module.initCharts();
    });
}
```

### Problem: High API Usage

**Solutions:**

1. **Batch API calls:**
```javascript
// Instead of multiple calls
const [settings, sites, latest] = await Promise.all([
    fetch('/api/auth?type=settings'),
    fetch('/api/auth?type=sites'),
    fetch('/api/get-latest-scraped')
]);
```

2. **Implement request debouncing:**
```javascript
const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};
```

## Data Issues

### Problem: Duplicate Articles

**Diagnosis:**
```python
# Check for duplicates
python -c "
import json
with open('data/scraped/latest.json') as f:
    data = json.load(f)
urls = [a['url'] for a in data['articles']]
print(f'Total: {len(urls)}, Unique: {len(set(urls))}')"
```

**Solution:**
Enable deduplication:
```python
# In scraper.py
from deduplication import ArticleDeduplicator
deduplicator = ArticleDeduplicator()
articles = deduplicator.deduplicate(articles)
```

### Problem: Data Not Persisting

**Common Causes:**
1. GitHub API rate limit
2. Invalid JSON format
3. File size too large

**Solutions:**

1. **Check GitHub API limits:**
```bash
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

2. **Validate JSON:**
```python
import json
try:
    with open('data/scraped/latest.json') as f:
        json.load(f)
    print("JSON is valid")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

## Advanced Troubleshooting

### Enable Verbose Logging

1. **Python scripts:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **JavaScript:**
```javascript
window.DEBUG = true;
// All console.logs will be visible
```

3. **GitHub Actions:**
```yaml
- name: Run with debug
  run: |
    set -x  # Enable bash debug
    python scripts/scraper.py
  env:
    ACTIONS_STEP_DEBUG: true
```

### Network Debugging

1. **Test connectivity:**
```python
import requests
sites = ['https://www.straitstimes.com', 'https://www.channelnewsasia.com']
for site in sites:
    try:
        r = requests.get(site, timeout=10)
        print(f"{site}: {r.status_code}")
    except Exception as e:
        print(f"{site}: {e}")
```

2. **Use proxy for debugging:**
```python
proxies = {
    'http': 'http://localhost:8888',
    'https': 'http://localhost:8888'
}
response = requests.get(url, proxies=proxies)
```

### Database Inspection

1. **List all scraped files:**
```python
import os
import json
from datetime import datetime

scraped_dir = 'data/scraped'
files = sorted(os.listdir(scraped_dir))
for file in files[-10:]:  # Last 10 files
    with open(f'{scraped_dir}/{file}') as f:
        data = json.load(f)
    print(f"{file}: {len(data.get('articles', []))} articles")
```

2. **Analyze scraping patterns:**
```python
# Check success rate over time
import glob
files = glob.glob('data/scraped/news_*.json')
for file in sorted(files)[-30:]:
    # Analyze each file
    pass
```

### Emergency Recovery

1. **Reset to clean state:**
```bash
# Backup current data
cp -r data data_backup_$(date +%Y%m%d)

# Reset to defaults
git checkout data/settings.json
git checkout data/sites.json
```

2. **Force refresh all caches:**
```javascript
// Frontend
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

```python
# Backend
import os
os.remove('data/ai_cache.json')
os.remove('data/dedup_cache.json')
```

## Getting Help

1. **Enable debug mode and collect logs**
2. **Check GitHub Issues for similar problems**
3. **Prepare:**
   - Error messages
   - Steps to reproduce
   - System configuration
   - Recent changes

4. **Contact channels:**
   - GitHub Issues
   - Email support
   - Developer documentation