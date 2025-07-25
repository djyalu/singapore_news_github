# Extended Troubleshooting Guide / 확장된 문제 해결 가이드

## Table of Contents / 목차
1. [Diagnostic Tools / 진단 도구](#diagnostic-tools--진단-도구)
2. [Common Issues / 일반적인 문제](#common-issues--일반적인-문제)
3. [Scraping Issues / 스크래핑 문제](#scraping-issues--스크래핑-문제)
4. [API Issues / API 문제](#api-issues--api-문제)
5. [WhatsApp Issues / WhatsApp 문제](#whatsapp-issues--whatsapp-문제)
6. [Performance Issues / 성능 문제](#performance-issues--성능-문제)
7. [Data Issues / 데이터 문제](#data-issues--데이터-문제)
8. [Security Issues / 보안 문제](#security-issues--보안-문제)
9. [Advanced Debugging / 고급 디버깅](#advanced-debugging--고급-디버깅)
10. [Recovery Procedures / 복구 절차](#recovery-procedures--복구-절차)

## Diagnostic Tools / 진단 도구

### 1. System Health Check Script / 시스템 상태 점검 스크립트
```bash
#!/bin/bash
# scripts/health_check.sh

echo "=== Singapore News Scraper Health Check ==="
echo "Time: $(date)"
echo ""

# Check GitHub Pages
echo "1. Checking GitHub Pages..."
PAGES_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://djyalu.github.io/singapore_news_github/)
if [ $PAGES_STATUS -eq 200 ]; then
    echo "✓ GitHub Pages: OK"
else
    echo "✗ GitHub Pages: ERROR (HTTP $PAGES_STATUS)"
fi

# Check Vercel APIs
echo ""
echo "2. Checking Vercel APIs..."
API_STATUS=$(curl -s https://singapore-news-github.vercel.app/api/test-env | jq -r '.success')
if [ "$API_STATUS" = "true" ]; then
    echo "✓ Vercel APIs: OK"
else
    echo "✗ Vercel APIs: ERROR"
fi

# Check GitHub API
echo ""
echo "3. Checking GitHub API connection..."
GITHUB_STATUS=$(curl -s https://singapore-news-github.vercel.app/api/test-env | jq -r '.data.connections.github.connected')
if [ "$GITHUB_STATUS" = "true" ]; then
    echo "✓ GitHub API: OK"
else
    echo "✗ GitHub API: ERROR"
fi

# Check data files
echo ""
echo "4. Checking data files..."
for file in settings.json sites.json latest.json; do
    if [ -f "data/$file" ]; then
        echo "✓ data/$file: EXISTS"
    else
        echo "✗ data/$file: MISSING"
    fi
done

# Check recent scraping
echo ""
echo "5. Checking recent scraping..."
LATEST_FILE=$(ls -t data/scraped/news_*.json 2>/dev/null | head -1)
if [ -n "$LATEST_FILE" ]; then
    LATEST_DATE=$(basename $LATEST_FILE | sed 's/news_\([0-9]*\)_.*/\1/')
    echo "✓ Latest scraping: $LATEST_DATE"
else
    echo "✗ No scraping files found"
fi

echo ""
echo "=== Health Check Complete ==="
```

### 2. Debug Information Collector / 디버그 정보 수집기
```python
# scripts/collect_debug_info.py
import json
import os
import sys
import datetime
import subprocess
from pathlib import Path

def collect_debug_info():
    """Collect comprehensive debug information"""
    debug_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system": {},
        "files": {},
        "logs": {},
        "environment": {}
    }
    
    # System info
    debug_info["system"]["python_version"] = sys.version
    debug_info["system"]["platform"] = sys.platform
    debug_info["system"]["cwd"] = os.getcwd()
    
    # Check important files
    important_files = [
        "data/settings.json",
        "data/sites.json",
        "data/latest.json",
        ".github/workflows/scraper.yml",
        "requirements.txt",
        "vercel.json"
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            debug_info["files"][file_path] = {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # Read JSON files
            if file_path.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                        debug_info["files"][file_path]["valid_json"] = True
                        if file_path == "data/settings.json":
                            debug_info["files"][file_path]["scraping_method"] = content.get("scrapingMethod")
                except:
                    debug_info["files"][file_path]["valid_json"] = False
        else:
            debug_info["files"][file_path] = {"exists": False}
    
    # Recent logs
    scraped_files = sorted(Path("data/scraped").glob("news_*.json"), reverse=True)[:5]
    debug_info["logs"]["recent_scrapes"] = [str(f) for f in scraped_files]
    
    # Git status
    try:
        git_status = subprocess.check_output(["git", "status", "--short"], text=True)
        debug_info["system"]["git_status"] = git_status.strip() or "clean"
    except:
        debug_info["system"]["git_status"] = "error"
    
    # Environment variables (sanitized)
    env_vars = ["GITHUB_OWNER", "GITHUB_REPO", "DEBUG_MODE"]
    for var in env_vars:
        debug_info["environment"][var] = os.environ.get(var, "not set")
    
    # Output
    print(json.dumps(debug_info, indent=2))
    
    # Save to file
    with open("debug_info.json", "w") as f:
        json.dump(debug_info, f, indent=2)
    print(f"\nDebug information saved to: debug_info.json")

if __name__ == "__main__":
    collect_debug_info()
```

### 3. API Test Suite / API 테스트 스위트
```javascript
// scripts/test_apis.js
const https = require('https');

const API_BASE = 'https://singapore-news-github.vercel.app';

const tests = [
    {
        name: 'Environment Test',
        method: 'GET',
        path: '/api/test-env',
        expectedStatus: 200
    },
    {
        name: 'Get Latest Scraped',
        method: 'GET',
        path: '/api/get-latest-scraped',
        expectedStatus: 200
    },
    {
        name: 'Scraping Status',
        method: 'GET',
        path: '/api/get-scraping-status',
        expectedStatus: 200
    },
    {
        name: 'Auth Check',
        method: 'GET',
        path: '/api/auth',
        expectedStatus: 401  // Should require auth
    }
];

async function runTests() {
    console.log('=== API Test Suite ===\n');
    
    for (const test of tests) {
        await new Promise((resolve) => {
            const options = {
                hostname: 'singapore-news-github.vercel.app',
                path: test.path,
                method: test.method
            };
            
            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    const success = res.statusCode === test.expectedStatus;
                    const symbol = success ? '✓' : '✗';
                    console.log(`${symbol} ${test.name}: ${res.statusCode} ${success ? 'OK' : 'FAILED'}`);
                    
                    if (!success) {
                        console.log(`  Expected: ${test.expectedStatus}, Got: ${res.statusCode}`);
                        console.log(`  Response: ${data.substring(0, 100)}...`);
                    }
                    
                    resolve();
                });
            });
            
            req.on('error', (e) => {
                console.log(`✗ ${test.name}: ERROR - ${e.message}`);
                resolve();
            });
            
            req.end();
        });
    }
    
    console.log('\n=== Test Complete ===');
}

runTests();
```

## Common Issues / 일반적인 문제

### 1. Login Issues / 로그인 문제

#### Issue: Cannot login to dashboard / 대시보드에 로그인할 수 없음
```javascript
// Symptoms
- Login button doesn't work
- Page refreshes after login
- "Invalid credentials" despite correct password

// Diagnosis
1. Open browser console (F12)
2. Check for JavaScript errors
3. Check Network tab for failed requests
4. Verify cookies are enabled

// Solutions
// Solution 1: Clear browser data
localStorage.clear();
sessionStorage.clear();
// Then reload page

// Solution 2: Check auth.js is loaded
console.log(typeof handleLogin); // Should not be 'undefined'

// Solution 3: Manual session creation (emergency)
sessionStorage.setItem('adminLoggedIn', 'true');
sessionStorage.setItem('sessionExpiry', Date.now() + 3600000);
location.reload();
```

#### Issue: Session expires too quickly / 세션이 너무 빨리 만료됨
```javascript
// Edit js/auth.js
const SESSION_DURATION = 7200000; // 2 hours instead of 1

// Or implement remember me
function handleLogin(remember = false) {
    if (remember) {
        localStorage.setItem('rememberMe', 'true');
        // Use localStorage instead of sessionStorage
    }
}
```

### 2. Display Issues / 표시 문제

#### Issue: Dashboard shows wrong timezone / 대시보드가 잘못된 시간대를 표시
```javascript
// Check timezone calculation in app.js
function getKSTTime(date = new Date()) {
    // Correct implementation
    const utc = date.getTime() + (date.getTimezoneOffset() * 60000);
    const kst = new Date(utc + (9 * 3600000)); // UTC+9
    return kst;
}

// Test timezone
console.log('Current KST:', getKSTTime().toString());
console.log('Should be:', new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'}));
```

#### Issue: Articles not displaying / 기사가 표시되지 않음
```javascript
// Debug article loading
async function debugArticleLoading() {
    try {
        // 1. Check API response
        const response = await fetch('/api/get-latest-scraped');
        const data = await response.json();
        console.log('API Response:', data);
        
        // 2. Check data structure
        if (!data.success) {
            console.error('API Error:', data.error);
            return;
        }
        
        // 3. Check articles array
        console.log('Articles count:', data.data.articles?.length || 0);
        
        // 4. Check DOM elements
        const container = document.querySelector('.articles-grid');
        console.log('Container exists:', !!container);
        
        // 5. Manual render test
        if (data.data.articles?.length > 0) {
            container.innerHTML = data.data.articles.map(article => 
                `<div class="article-card">${article.title}</div>`
            ).join('');
        }
    } catch (error) {
        console.error('Debug failed:', error);
    }
}
```

## Scraping Issues / 스크래핑 문제

### 1. No Articles Collected / 기사가 수집되지 않음

#### Diagnosis Steps / 진단 단계
```python
# scripts/diagnose_scraping.py
import requests
from bs4 import BeautifulSoup
import json

def diagnose_site(site_name, site_config):
    """Diagnose why a site isn't being scraped"""
    print(f"\n=== Diagnosing {site_name} ===")
    
    # 1. Check URL accessibility
    try:
        response = requests.get(site_config['url'], timeout=10)
        print(f"✓ URL accessible: {response.status_code}")
    except Exception as e:
        print(f"✗ URL error: {e}")
        return
    
    # 2. Check HTML structure
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 3. Test selectors
    if 'selectors' in site_config:
        for selector_name, selector in site_config['selectors'].items():
            elements = soup.select(selector)
            print(f"Selector '{selector_name}' ({selector}): {len(elements)} matches")
            
            if len(elements) > 0 and selector_name == 'title':
                print(f"  Sample: {elements[0].get_text().strip()[:50]}...")
    
    # 4. Check for common issues
    # Bot detection
    if 'captcha' in response.text.lower() or response.status_code == 403:
        print("⚠ Possible bot detection")
    
    # JavaScript required
    if 'noscript' in response.text.lower() or len(soup.find_all()) < 10:
        print("⚠ Site may require JavaScript")
    
    # Paywall
    if 'paywall' in response.text.lower() or 'subscribe' in soup.title.string.lower():
        print("⚠ Possible paywall")

# Load sites config
with open('data/sites.json', 'r') as f:
    sites = json.load(f)

# Test each site
for site in sites['sites']:
    if site.get('enabled', True):
        diagnose_site(site['name'], site)
```

#### Common Fixes / 일반적인 수정사항

##### Fix 1: Update Selectors / 선택자 업데이트
```json
// data/sites.json
{
    "name": "The Straits Times",
    "selectors": {
        // Old selectors that stopped working
        // "article": "div.story-card",
        // "title": "h3.story-headline",
        
        // New selectors after site update
        "article": "article.card-container",
        "title": "h2.card-title, h3.card-title",
        "link": "a.card-link[href^='/singapore']"
    }
}
```

##### Fix 2: Add Headers / 헤더 추가
```python
# scripts/scraper.py
def get_headers(site_name):
    """Get site-specific headers"""
    base_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Site-specific headers
    if 'straitstimes' in site_name.lower():
        base_headers['Referer'] = 'https://www.google.com/'
    elif 'mothership' in site_name.lower():
        base_headers['Cookie'] = 'accepted_cookies=true'
    
    return base_headers
```

##### Fix 3: Use Alternative Methods / 대체 방법 사용
```python
# Switch to RSS for problematic sites
RSS_FEEDS = {
    'Mothership': 'https://mothership.sg/feed/',
    'The Independent Singapore': 'https://theindependent.sg/feed/',
    'Yahoo Singapore': 'https://sg.news.yahoo.com/rss/'
}

def scrape_via_rss(site_name, feed_url):
    """Fallback to RSS when HTML scraping fails"""
    import feedparser
    
    feed = feedparser.parse(feed_url)
    articles = []
    
    for entry in feed.entries[:5]:  # Limit to 5 articles
        articles.append({
            'title': entry.title,
            'url': entry.link,
            'summary': entry.get('summary', '')[:200],
            'published': entry.get('published', '')
        })
    
    return articles
```

### 2. Partial Scraping / 부분 스크래핑

#### Issue: Some sites work, others don't / 일부 사이트만 작동
```python
# Add retry logic with exponential backoff
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    wait = delay * (backoff ** (retries - 1))
                    print(f"Retry {retries}/{max_retries} after {wait}s...")
                    time.sleep(wait)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def scrape_site(site_config):
    # Scraping logic here
    pass
```

#### Issue: Inconsistent results / 일관성 없는 결과
```python
# Implement validation
def validate_article(article):
    """Validate scraped article data"""
    required_fields = ['title', 'url', 'summary']
    
    # Check required fields
    for field in required_fields:
        if not article.get(field):
            return False, f"Missing {field}"
    
    # Validate URL
    if not article['url'].startswith(('http://', 'https://')):
        return False, "Invalid URL"
    
    # Validate content length
    if len(article['title']) < 10:
        return False, "Title too short"
    
    if len(article['summary']) < 20:
        return False, "Summary too short"
    
    # Check for duplicate content
    if article['title'] == article['summary']:
        return False, "Title and summary are identical"
    
    return True, "Valid"

# Use in scraper
valid_articles = []
for article in scraped_articles:
    is_valid, reason = validate_article(article)
    if is_valid:
        valid_articles.append(article)
    else:
        print(f"Rejected article: {reason}")
```

## API Issues / API 문제

### 1. API Rate Limiting / API 속도 제한

#### Issue: Gemini API rate limit exceeded / Gemini API 속도 제한 초과
```python
# Implement token bucket rate limiter
import time
from collections import deque

class RateLimiter:
    def __init__(self, rate=15, per=60):
        self.rate = rate
        self.per = per
        self.requests = deque()
    
    def wait_if_needed(self):
        now = time.time()
        # Remove old requests
        while self.requests and self.requests[0] < now - self.per:
            self.requests.popleft()
        
        if len(self.requests) >= self.rate:
            # Wait until the oldest request expires
            sleep_time = self.per - (now - self.requests[0]) + 0.1
            print(f"Rate limit reached, waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            self.wait_if_needed()  # Recursive check
        
        self.requests.append(now)

# Usage
rate_limiter = RateLimiter(rate=14, per=60)  # 14 requests per minute

for url in urls_to_process:
    rate_limiter.wait_if_needed()
    # Make API call
    process_with_gemini(url)
```

#### Issue: Vercel function timeout / Vercel 함수 타임아웃
```javascript
// Split long-running tasks
// api/trigger-scraping-async.js
export default async function handler(req, res) {
    // Start scraping in background
    const workflowId = generateWorkflowId();
    
    // Store job in queue
    await storeJob({
        id: workflowId,
        status: 'queued',
        createdAt: new Date().toISOString()
    });
    
    // Trigger GitHub Action instead of running here
    await triggerGitHubAction('scraper.yml', {
        workflow_id: workflowId
    });
    
    // Return immediately
    res.status(202).json({
        success: true,
        data: {
            message: 'Scraping queued',
            workflowId: workflowId,
            statusUrl: `/api/get-scraping-status?id=${workflowId}`
        }
    });
}
```

### 2. CORS Issues / CORS 문제

#### Issue: CORS blocking API calls / CORS가 API 호출을 차단
```javascript
// vercel.json - Comprehensive CORS setup
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
        { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version" }
      ]
    }
  ]
}

// For specific domains only
const allowedOrigins = [
    'https://djyalu.github.io',
    'http://localhost:3000'
];

export default function handler(req, res) {
    const origin = req.headers.origin;
    if (allowedOrigins.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
    }
    
    // Handle preflight
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    // ... rest of handler
}
```

## WhatsApp Issues / WhatsApp 문제

### 1. Message Not Sending / 메시지가 전송되지 않음

#### Diagnosis / 진단
```python
# scripts/test_whatsapp_detailed.py
import requests
import json

def test_whatsapp_connection():
    """Detailed WhatsApp API test"""
    
    # Test 1: Check instance status
    instance_url = "https://api.green-api.com/waInstance{idInstance}/getStateInstance/{apiTokenInstance}"
    
    try:
        response = requests.get(instance_url)
        state = response.json()
        print(f"Instance State: {state}")
        
        if state.get('stateInstance') != 'authorized':
            print("ERROR: WhatsApp not authorized. Please scan QR code.")
            return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False
    
    # Test 2: Send test message
    send_url = "https://api.green-api.com/waInstance{idInstance}/sendMessage/{apiTokenInstance}"
    
    test_message = {
        "chatId": "6591234567@c.us",
        "message": "Test message from diagnostic tool"
    }
    
    try:
        response = requests.post(send_url, json=test_message)
        result = response.json()
        print(f"Send Result: {result}")
        
        if result.get('sent'):
            print("✓ Message sent successfully")
            return True
        else:
            print("✗ Message failed:", result.get('error'))
            return False
    except Exception as e:
        print(f"Send Error: {e}")
        return False

# Run test
test_whatsapp_connection()
```

#### Common Fixes / 일반적인 수정사항

##### Fix 1: Update Phone Number Format / 전화번호 형식 업데이트
```python
def format_whatsapp_number(number):
    """Ensure correct WhatsApp number format"""
    # Remove all non-digits
    number = ''.join(filter(str.isdigit, number))
    
    # Add country code if missing
    if not number.startswith('65'):
        number = '65' + number
    
    # Add WhatsApp suffix
    if not number.endswith('@c.us'):
        number = number + '@c.us'
    
    return number

# Test
print(format_whatsapp_number('91234567'))  # 6591234567@c.us
print(format_whatsapp_number('+65 9123 4567'))  # 6591234567@c.us
```

##### Fix 2: Handle Message Size Limits / 메시지 크기 제한 처리
```python
def split_long_message(message, max_length=4096):
    """Split long messages for WhatsApp"""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    lines = message.split('\n')
    current_part = ""
    
    for line in lines:
        if len(current_part) + len(line) + 1 > max_length:
            parts.append(current_part.strip())
            current_part = line + '\n'
        else:
            current_part += line + '\n'
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

# Send in parts
message_parts = split_long_message(long_message)
for i, part in enumerate(message_parts):
    send_whatsapp(f"Part {i+1}/{len(message_parts)}:\n\n{part}")
    time.sleep(2)  # Avoid rate limiting
```

## Performance Issues / 성능 문제

### 1. Slow Scraping / 느린 스크래핑

#### Optimization Techniques / 최적화 기법

##### Concurrent Scraping / 동시 스크래핑
```python
import concurrent.futures
import threading

# Thread-safe results storage
results_lock = threading.Lock()
all_results = []

def scrape_site_thread_safe(site_config):
    """Thread-safe site scraping"""
    try:
        articles = scrape_site(site_config)
        with results_lock:
            all_results.extend(articles)
        return len(articles)
    except Exception as e:
        print(f"Error scraping {site_config['name']}: {e}")
        return 0

# Concurrent execution
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for site in enabled_sites:
        future = executor.submit(scrape_site_thread_safe, site)
        futures.append((site['name'], future))
    
    # Wait for completion
    for site_name, future in futures:
        try:
            count = future.result(timeout=30)
            print(f"{site_name}: {count} articles")
        except concurrent.futures.TimeoutError:
            print(f"{site_name}: Timeout")
```

##### Caching Strategy / 캐싱 전략
```python
import hashlib
import pickle
from datetime import datetime, timedelta

class ScraperCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, url):
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url, max_age_minutes=60):
        """Get cached content if fresh"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            age = datetime.now() - data['timestamp']
            if age < timedelta(minutes=max_age_minutes):
                return data['content']
        
        return None
    
    def set(self, url, content):
        """Cache content"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.pkl"
        
        data = {
            'url': url,
            'content': content,
            'timestamp': datetime.now()
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    
    def clear_old(self, max_age_days=7):
        """Clear old cache entries"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        for cache_file in self.cache_dir.glob('*.pkl'):
            if cache_file.stat().st_mtime < cutoff.timestamp():
                cache_file.unlink()

# Usage
cache = ScraperCache()

def scrape_with_cache(url):
    # Check cache first
    content = cache.get(url)
    if content:
        print(f"Cache hit: {url}")
        return content
    
    # Scrape if not cached
    content = requests.get(url).text
    cache.set(url, content)
    return content
```

### 2. High Memory Usage / 높은 메모리 사용량

#### Memory Profiling / 메모리 프로파일링
```python
# scripts/memory_profiler.py
import tracemalloc
import gc

def profile_memory(func):
    """Decorator to profile memory usage"""
    def wrapper(*args, **kwargs):
        # Start tracing
        tracemalloc.start()
        gc.collect()
        
        # Run function
        result = func(*args, **kwargs)
        
        # Get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\n{func.__name__} memory usage:")
        print(f"Current: {current / 1024 / 1024:.2f} MB")
        print(f"Peak: {peak / 1024 / 1024:.2f} MB")
        
        return result
    return wrapper

@profile_memory
def process_large_scraping():
    # Your scraping code here
    pass
```

#### Memory Optimization / 메모리 최적화
```python
# Stream processing for large datasets
def process_articles_streaming(articles_generator):
    """Process articles one at a time to save memory"""
    processed_count = 0
    
    for article in articles_generator:
        # Process single article
        processed_article = process_article(article)
        
        # Save immediately instead of accumulating
        save_article(processed_article)
        
        processed_count += 1
        
        # Periodic garbage collection
        if processed_count % 100 == 0:
            gc.collect()
    
    return processed_count

# Generator for memory-efficient iteration
def scrape_articles_generator(site_config):
    """Yield articles one at a time"""
    page = 1
    while True:
        articles = scrape_page(site_config, page)
        if not articles:
            break
        
        for article in articles:
            yield article
        
        page += 1
```

## Data Issues / 데이터 문제

### 1. Corrupted JSON Files / 손상된 JSON 파일

#### Recovery Script / 복구 스크립트
```python
# scripts/repair_json.py
import json
import re
from pathlib import Path

def repair_json_file(file_path):
    """Attempt to repair corrupted JSON file"""
    print(f"Attempting to repair: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Common fixes
    repairs = [
        # Fix trailing commas
        (r',\s*}', '}'),
        (r',\s*]', ']'),
        
        # Fix missing quotes
        (r'(\w+):', r'"\1":'),
        
        # Fix single quotes
        (r"'([^']*)'", r'"\1"'),
        
        # Fix incomplete strings
        (r'"([^"]*?)$', r'"\1"'),
        
        # Remove control characters
        (r'[\x00-\x1f\x7f]', ''),
    ]
    
    for pattern, replacement in repairs:
        content = re.sub(pattern, replacement, content)
    
    # Try to parse
    try:
        data = json.loads(content)
        
        # Save repaired version
        backup_path = file_path.with_suffix('.bak')
        file_path.rename(backup_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Repaired successfully!")
        print(f"  Original backed up to: {backup_path}")
        print(f"  Size change: {original_size} → {len(content)}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Still invalid: {e}")
        
        # Try to extract valid portion
        try:
            # Find last valid closing brace/bracket
            for i in range(len(content) - 1, 0, -1):
                if content[i] in '}]':
                    truncated = content[:i+1]
                    data = json.loads(truncated)
                    
                    # Save truncated version
                    with open(file_path.with_suffix('.truncated.json'), 'w') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✓ Saved truncated version with {len(data)} items")
                    return True
        except:
            pass
        
        print("✗ Unable to repair file")
        return False

# Repair all JSON files in data directory
for json_file in Path('data').rglob('*.json'):
    try:
        with open(json_file) as f:
            json.load(f)
        print(f"✓ {json_file} is valid")
    except:
        repair_json_file(json_file)
```

### 2. Data Inconsistency / 데이터 불일치

#### Data Validation / 데이터 검증
```python
# scripts/validate_data.py
from datetime import datetime, timedelta
import json
from pathlib import Path

def validate_data_integrity():
    """Comprehensive data validation"""
    issues = []
    
    # Check settings.json
    try:
        with open('data/settings.json') as f:
            settings = json.load(f)
        
        # Validate settings structure
        required_keys = ['scrapingEnabled', 'scrapingMethod', 'whatsappEnabled']
        for key in required_keys:
            if key not in settings:
                issues.append(f"Missing setting: {key}")
        
        # Validate scraping method
        valid_methods = ['traditional', 'ai', 'hybrid_ai']
        if settings.get('scrapingMethod') not in valid_methods:
            issues.append(f"Invalid scraping method: {settings.get('scrapingMethod')}")
    
    except Exception as e:
        issues.append(f"Settings file error: {e}")
    
    # Check sites.json
    try:
        with open('data/sites.json') as f:
            sites_data = json.load(f)
        
        sites = sites_data.get('sites', [])
        if not sites:
            issues.append("No sites configured")
        
        for i, site in enumerate(sites):
            if not site.get('name'):
                issues.append(f"Site {i} missing name")
            if not site.get('url'):
                issues.append(f"Site {i} missing URL")
            if not site.get('group'):
                issues.append(f"Site {i} missing group")
    
    except Exception as e:
        issues.append(f"Sites file error: {e}")
    
    # Check scraped data files
    scraped_dir = Path('data/scraped')
    if scraped_dir.exists():
        json_files = list(scraped_dir.glob('news_*.json'))
        
        if not json_files:
            issues.append("No scraped data files found")
        else:
            # Check for gaps in data
            dates = []
            for f in json_files:
                match = re.search(r'news_(\d{8})_', f.name)
                if match:
                    dates.append(datetime.strptime(match.group(1), '%Y%m%d'))
            
            dates.sort()
            if dates:
                # Check for missing days
                current = dates[0]
                while current <= dates[-1]:
                    if current not in dates:
                        issues.append(f"Missing data for {current.strftime('%Y-%m-%d')}")
                    current += timedelta(days=1)
    
    # Check latest.json
    try:
        with open('data/latest.json') as f:
            latest = json.load(f)
        
        # Verify it matches the most recent scraped file
        if json_files:
            newest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            with open(newest_file) as f:
                newest_data = json.load(f)
            
            if latest != newest_data:
                issues.append("latest.json doesn't match newest scraped file")
    
    except Exception as e:
        issues.append(f"Latest file error: {e}")
    
    # Report
    if issues:
        print("❌ Data Validation Failed:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All data validation passed!")
    
    return len(issues) == 0

# Run validation
validate_data_integrity()
```

## Security Issues / 보안 문제

### 1. API Key Exposure / API 키 노출

#### Security Audit Script / 보안 감사 스크립트
```bash
#!/bin/bash
# scripts/security_audit.sh

echo "=== Security Audit ==="

# Check for exposed secrets in code
echo "1. Checking for exposed secrets..."

# Common patterns to search for
patterns=(
    "api[_-]?key"
    "secret"
    "password"
    "token"
    "ghp_"  # GitHub token prefix
)

for pattern in "${patterns[@]}"; do
    echo "Searching for: $pattern"
    grep -r -i "$pattern" --include="*.js" --include="*.py" --exclude-dir=node_modules --exclude-dir=.git . | grep -v "example\|sample\|test" | head -5
done

# Check file permissions
echo ""
echo "2. Checking file permissions..."
find . -type f -name "*.json" -perm 777 -exec ls -la {} \;

# Check git history for secrets
echo ""
echo "3. Checking git history..."
git log -p -G"api_key|secret|password" --all | grep -E "^\+.*api_key|^\+.*secret|^\+.*password" | head -10

# Check environment variables
echo ""
echo "4. Checking environment exposure..."
curl -s https://singapore-news-github.vercel.app/api/test-env | jq '.data.environment' 2>/dev/null

echo ""
echo "=== Audit Complete ==="
```

#### Secure Configuration / 안전한 설정
```javascript
// api/secure-config.js
// Never expose sensitive data
export default function handler(req, res) {
    const safeConfig = {
        github: {
            owner: process.env.GITHUB_OWNER,
            repo: process.env.GITHUB_REPO,
            // Never expose token
            hasToken: !!process.env.GITHUB_TOKEN
        },
        whatsapp: {
            // Only show configuration status
            configured: !!process.env.WHATSAPP_API_KEY,
            instance: process.env.WHATSAPP_API_KEY?.split(':')[0] || 'not set'
        }
    };
    
    res.json({ success: true, data: safeConfig });
}
```

### 2. Authentication Bypass / 인증 우회

#### Strengthen Authentication / 인증 강화
```javascript
// Enhanced auth with rate limiting and logging
const authAttempts = new Map();
const MAX_ATTEMPTS = 5;
const LOCKOUT_TIME = 15 * 60 * 1000; // 15 minutes

export default async function handler(req, res) {
    const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    const attemptKey = `auth_${ip}`;
    
    // Check lockout
    const attempts = authAttempts.get(attemptKey) || { count: 0, lastAttempt: Date.now() };
    
    if (attempts.count >= MAX_ATTEMPTS) {
        const timeSinceLast = Date.now() - attempts.lastAttempt;
        if (timeSinceLast < LOCKOUT_TIME) {
            const remainingTime = Math.ceil((LOCKOUT_TIME - timeSinceLast) / 1000);
            return res.status(429).json({
                success: false,
                error: {
                    code: 'AUTH_LOCKED',
                    message: `Too many attempts. Try again in ${remainingTime} seconds`
                }
            });
        } else {
            // Reset after lockout period
            attempts.count = 0;
        }
    }
    
    const { username, password } = req.body;
    
    // Validate credentials
    const isValid = validateCredentials(username, password);
    
    if (!isValid) {
        // Increment attempts
        attempts.count++;
        attempts.lastAttempt = Date.now();
        authAttempts.set(attemptKey, attempts);
        
        // Log failed attempt
        console.log(`Failed auth attempt from ${ip}: ${username}`);
        
        return res.status(401).json({
            success: false,
            error: {
                code: 'AUTH_INVALID',
                message: 'Invalid credentials',
                attemptsRemaining: MAX_ATTEMPTS - attempts.count
            }
        });
    }
    
    // Success - reset attempts
    authAttempts.delete(attemptKey);
    
    // Generate secure session
    const sessionId = generateSecureSessionId();
    
    res.json({
        success: true,
        data: {
            sessionId,
            expiresIn: 3600
        }
    });
}
```

## Advanced Debugging / 고급 디버깅

### 1. Remote Debugging / 원격 디버깅

#### Enable Debug Logging / 디버그 로깅 활성화
```python
# Add to scripts/scraper.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(debug=False):
    """Setup comprehensive logging"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create logger
    logger = logging.getLogger('scraper')
    logger.setLevel(log_level)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/scraper.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Usage
logger = setup_logging(debug=True)
logger.debug("Starting scraper with config: %s", config)
```

#### Remote Log Viewer / 원격 로그 뷰어
```javascript
// api/get-logs.js
import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
    // Check authentication
    if (!isAuthenticated(req)) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    const { lines = 100, level = 'all' } = req.query;
    const logFile = path.join(process.cwd(), 'logs', 'scraper.log');
    
    try {
        // Read last N lines
        const content = fs.readFileSync(logFile, 'utf8');
        const logLines = content.split('\n').slice(-lines);
        
        // Filter by level if specified
        const filtered = level === 'all' 
            ? logLines 
            : logLines.filter(line => line.includes(level.toUpperCase()));
        
        res.json({
            success: true,
            data: {
                logs: filtered,
                file: 'scraper.log',
                lines: filtered.length
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: { message: 'Failed to read logs' }
        });
    }
}
```

### 2. Performance Profiling / 성능 프로파일링

#### Comprehensive Performance Monitor / 종합 성능 모니터
```python
# scripts/performance_monitor.py
import time
import psutil
import threading
from contextlib import contextmanager

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'cpu': [],
            'memory': [],
            'disk_io': [],
            'network': []
        }
        self.monitoring = False
        
    def start_monitoring(self, interval=1):
        """Start background monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return report"""
        self.monitoring = False
        self.monitor_thread.join()
        return self.generate_report()
    
    def _monitor_loop(self, interval):
        """Background monitoring loop"""
        while self.monitoring:
            # CPU usage
            self.metrics['cpu'].append({
                'time': time.time(),
                'percent': psutil.cpu_percent(interval=0.1)
            })
            
            # Memory usage
            mem = psutil.virtual_memory()
            self.metrics['memory'].append({
                'time': time.time(),
                'percent': mem.percent,
                'used_mb': mem.used / 1024 / 1024
            })
            
            # Disk I/O
            disk = psutil.disk_io_counters()
            self.metrics['disk_io'].append({
                'time': time.time(),
                'read_mb': disk.read_bytes / 1024 / 1024,
                'write_mb': disk.write_bytes / 1024 / 1024
            })
            
            time.sleep(interval)
    
    def generate_report(self):
        """Generate performance report"""
        report = {}
        
        for metric_name, data in self.metrics.items():
            if data:
                if metric_name == 'cpu':
                    values = [d['percent'] for d in data]
                    report[metric_name] = {
                        'avg': sum(values) / len(values),
                        'max': max(values),
                        'min': min(values)
                    }
                elif metric_name == 'memory':
                    values = [d['percent'] for d in data]
                    used_mb = [d['used_mb'] for d in data]
                    report[metric_name] = {
                        'avg_percent': sum(values) / len(values),
                        'max_percent': max(values),
                        'avg_mb': sum(used_mb) / len(used_mb),
                        'max_mb': max(used_mb)
                    }
        
        return report

@contextmanager
def monitor_performance():
    """Context manager for performance monitoring"""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    start_time = time.time()
    
    try:
        yield monitor
    finally:
        duration = time.time() - start_time
        report = monitor.stop_monitoring()
        report['duration'] = duration
        
        print("\n=== Performance Report ===")
        print(f"Duration: {duration:.2f}s")
        print(f"CPU: avg={report['cpu']['avg']:.1f}%, max={report['cpu']['max']:.1f}%")
        print(f"Memory: avg={report['memory']['avg_percent']:.1f}%, max={report['memory']['max_mb']:.0f}MB")
        print("========================\n")

# Usage
with monitor_performance() as monitor:
    # Run scraping
    run_scraping()
```

## Recovery Procedures / 복구 절차

### 1. Complete System Recovery / 전체 시스템 복구

#### Step-by-step Recovery / 단계별 복구
```bash
#!/bin/bash
# scripts/full_recovery.sh

echo "=== Full System Recovery ==="
echo "This will restore the system to a working state"
echo ""

# 1. Backup current state
echo "Step 1: Backing up current state..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="backup_$timestamp"
mkdir -p $backup_dir
cp -r data/ $backup_dir/
echo "✓ Backup created: $backup_dir"

# 2. Check git status
echo ""
echo "Step 2: Checking git status..."
git_status=$(git status --porcelain)
if [ -n "$git_status" ]; then
    echo "⚠ Uncommitted changes detected:"
    echo "$git_status"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. Find last known good commit
echo ""
echo "Step 3: Finding last stable version..."
# Look for commits with "stable" or "working" in message
stable_commits=$(git log --oneline --grep="stable\|working" -n 5)
echo "Recent stable commits:"
echo "$stable_commits"
echo ""
read -p "Enter commit hash to restore (or 'skip'): " commit_hash

if [ "$commit_hash" != "skip" ]; then
    # 4. Restore files
    echo ""
    echo "Step 4: Restoring from commit $commit_hash..."
    git checkout $commit_hash -- data/
    git checkout $commit_hash -- scripts/
    git checkout $commit_hash -- api/
    echo "✓ Files restored"
fi

# 5. Validate configuration
echo ""
echo "Step 5: Validating configuration..."
python scripts/validate_data.py

# 6. Test basic functionality
echo ""
echo "Step 6: Testing basic functionality..."
curl -s https://singapore-news-github.vercel.app/api/test-env | jq '.success'

# 7. Clear caches
echo ""
echo "Step 7: Clearing caches..."
rm -rf cache/
rm -rf logs/*.log
echo "✓ Caches cleared"

# 8. Restart services
echo ""
echo "Step 8: Ready to restart services"
echo "Please:"
echo "1. Commit changes: git add . && git commit -m 'Recovery from $commit_hash'"
echo "2. Push to GitHub: git push"
echo "3. Check GitHub Actions"
echo "4. Verify Vercel deployment"

echo ""
echo "=== Recovery Complete ==="
```

### 2. Incremental Recovery / 증분 복구

#### Selective Component Recovery / 선택적 구성요소 복구
```python
# scripts/selective_recovery.py
import json
import shutil
from pathlib import Path
from datetime import datetime

class SelectiveRecovery:
    def __init__(self):
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_component(self, component):
        """Backup specific component"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{component}_{timestamp}"
        
        if component == 'settings':
            shutil.copy('data/settings.json', backup_path.with_suffix('.json'))
        elif component == 'sites':
            shutil.copy('data/sites.json', backup_path.with_suffix('.json'))
        elif component == 'scraped':
            backup_path.mkdir()
            for f in Path('data/scraped').glob('*.json'):
                shutil.copy(f, backup_path / f.name)
        
        print(f"✓ Backed up {component} to {backup_path}")
        return backup_path
    
    def restore_component(self, component, backup_file=None):
        """Restore specific component"""
        if not backup_file:
            # Find latest backup
            pattern = f"{component}_*.json" if component in ['settings', 'sites'] else f"{component}_*"
            backups = list(self.backup_dir.glob(pattern))
            if not backups:
                print(f"✗ No backups found for {component}")
                return False
            backup_file = max(backups, key=lambda f: f.stat().st_mtime)
        
        print(f"Restoring {component} from {backup_file}...")
        
        if component == 'settings':
            shutil.copy(backup_file, 'data/settings.json')
        elif component == 'sites':
            shutil.copy(backup_file, 'data/sites.json')
        elif component == 'scraped' and backup_file.is_dir():
            for f in backup_file.glob('*.json'):
                shutil.copy(f, Path('data/scraped') / f.name)
        
        print(f"✓ Restored {component}")
        return True
    
    def verify_component(self, component):
        """Verify component integrity"""
        if component in ['settings', 'sites']:
            file_path = f'data/{component}.json'
            try:
                with open(file_path) as f:
                    data = json.load(f)
                print(f"✓ {component}.json is valid")
                return True
            except Exception as e:
                print(f"✗ {component}.json is invalid: {e}")
                return False
        return True
    
    def recovery_wizard(self):
        """Interactive recovery wizard"""
        print("=== Selective Recovery Wizard ===")
        print("What would you like to recover?")
        print("1. Settings only")
        print("2. Sites configuration only")
        print("3. Scraped data")
        print("4. Everything")
        
        choice = input("Enter choice (1-4): ")
        
        components = {
            '1': ['settings'],
            '2': ['sites'],
            '3': ['scraped'],
            '4': ['settings', 'sites', 'scraped']
        }.get(choice, [])
        
        for component in components:
            # Backup current
            self.backup_component(component)
            
            # Show available backups
            pattern = f"{component}_*"
            backups = sorted(self.backup_dir.glob(pattern), reverse=True)[:5]
            
            if backups:
                print(f"\nAvailable {component} backups:")
                for i, backup in enumerate(backups):
                    print(f"{i+1}. {backup.name}")
                
                backup_choice = input("Select backup number (or Enter for latest): ")
                if backup_choice.isdigit() and 1 <= int(backup_choice) <= len(backups):
                    selected_backup = backups[int(backup_choice) - 1]
                else:
                    selected_backup = backups[0]
                
                self.restore_component(component, selected_backup)
                self.verify_component(component)
        
        print("\n=== Recovery Complete ===")

# Run recovery wizard
if __name__ == "__main__":
    recovery = SelectiveRecovery()
    recovery.recovery_wizard()
```

---
*Last Updated: January 25, 2025*