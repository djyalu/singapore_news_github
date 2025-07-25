# API Reference / API 레퍼런스

## Table of Contents / 목차
1. [Overview / 개요](#overview--개요)
2. [Authentication / 인증](#authentication--인증)
3. [Endpoints / 엔드포인트](#endpoints--엔드포인트)
4. [Request/Response Formats / 요청/응답 형식](#requestresponse-formats--요청응답-형식)
5. [Error Handling / 오류 처리](#error-handling--오류-처리)
6. [Rate Limiting / 속도 제한](#rate-limiting--속도-제한)
7. [Code Examples / 코드 예제](#code-examples--코드-예제)
8. [WebSocket Events / WebSocket 이벤트](#websocket-events--websocket-이벤트)
9. [Testing / 테스트](#testing--테스트)
10. [Migration Guide / 마이그레이션 가이드](#migration-guide--마이그레이션-가이드)

## Overview / 개요

### Base URL
```
Production: https://singapore-news-github.vercel.app/api
Staging: https://singapore-news-github-staging.vercel.app/api
```

### API Version
```
Current Version: 1.0.0
Last Updated: 2025-01-25
```

### Response Format
```javascript
// Success Response
{
    "success": true,
    "data": { ... },
    "timestamp": "2025-01-25T09:00:00+09:00"
}

// Error Response
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": { ... }
    },
    "timestamp": "2025-01-25T09:00:00+09:00"
}
```

## Authentication / 인증

### 1. Login Endpoint / 로그인 엔드포인트

#### `POST /api/auth`
Authenticate user and receive session token / 사용자 인증 및 세션 토큰 수신

**Request Body:**
```json
{
    "username": "admin",
    "password": "Admin@123"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Login successful",
        "user": {
            "username": "admin",
            "role": "admin"
        },
        "sessionId": "session_xxxxx",
        "expiresIn": 3600
    }
}
```

**Error Codes:**
- `AUTH_INVALID_CREDENTIALS`: Invalid username or password
- `AUTH_MISSING_FIELDS`: Missing required fields
- `AUTH_RATE_LIMITED`: Too many login attempts

### 2. Get Settings (with Auth) / 설정 조회 (인증 포함)

#### `GET /api/auth`
Retrieve current settings (requires authentication) / 현재 설정 조회 (인증 필요)

**Response:**
```json
{
    "success": true,
    "data": {
        "settings": {
            "scrapingEnabled": true,
            "scrapingMethod": "hybrid_ai",
            "whatsappEnabled": true,
            "maxArticlesPerGroup": 5
        }
    }
}
```

## Endpoints / 엔드포인트

### 1. Scraping Control / 스크래핑 제어

#### `POST /api/trigger-scraping`
Trigger full scraping workflow with WhatsApp sending / WhatsApp 전송을 포함한 전체 스크래핑 워크플로우 실행

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "method": "hybrid_ai",  // Optional: override default method
    "sites": ["all"],       // Optional: specific sites or "all"
    "sendWhatsApp": true    // Optional: control WhatsApp sending
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Scraping workflow triggered successfully",
        "workflowId": "run_12345",
        "estimatedTime": 600,
        "statusUrl": "/api/get-scraping-status?id=run_12345"
    }
}
```

#### `POST /api/scrape-only`
Trigger scraping without WhatsApp sending / WhatsApp 전송 없이 스크래핑만 실행

**Request Body:**
```json
{
    "method": "traditional",
    "maxArticles": 10,
    "sites": ["straitstimes", "channelnewsasia"]
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Scraping started",
        "workflowId": "run_12346",
        "method": "traditional",
        "targetSites": 2
    }
}
```

#### `GET /api/get-scraping-status`
Get current scraping status / 현재 스크래핑 상태 조회

**Query Parameters:**
- `id` (optional): Specific workflow ID

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "running",
        "progress": 65,
        "phase": "collecting",
        "currentSite": "Channel NewsAsia",
        "sitesCompleted": 8,
        "totalSites": 16,
        "articlesCollected": 42,
        "startTime": "2025-01-25T08:00:00+09:00",
        "estimatedCompletion": "2025-01-25T08:10:00+09:00",
        "logs": [
            {
                "time": "08:00:15",
                "message": "Starting scraping process",
                "level": "info"
            }
        ]
    }
}
```

### 2. WhatsApp Integration / WhatsApp 통합

#### `POST /api/send-only`
Send WhatsApp messages for already scraped articles / 이미 스크랩된 기사에 대해 WhatsApp 메시지 전송

**Request Body:**
```json
{
    "articles": "latest",     // or specific article IDs
    "channels": ["all"],      // or specific channel IDs
    "testMode": false
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "WhatsApp messages sent",
        "sent": 5,
        "failed": 0,
        "channels": ["6591234567", "6598765432"],
        "historyFile": "whatsapp_20250125_090000.json"
    }
}
```

#### `POST /api/test-whatsapp`
Send test WhatsApp message / WhatsApp 테스트 메시지 전송

**Request Body:**
```json
{
    "message": "Test message from API",
    "channel": "6591234567"  // Optional: specific channel
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Test message sent successfully",
        "messageId": "msg_xxxxx",
        "channel": "6591234567",
        "timestamp": "2025-01-25T09:00:00+09:00"
    }
}
```

### 3. Data Management / 데이터 관리

#### `GET /api/get-latest-scraped`
Get latest scraped articles / 최신 스크랩 기사 조회

**Query Parameters:**
- `limit` (number): Maximum articles to return (default: 50)
- `group` (string): Filter by group (politics, economy, etc.)
- `date` (string): Specific date (YYYY-MM-DD)

**Response:**
```json
{
    "success": true,
    "data": {
        "count": 16,
        "date": "2025-01-25",
        "groups": {
            "politics": 3,
            "economy": 5,
            "society": 2,
            "tech": 3,
            "lifestyle": 3
        },
        "articles": [
            {
                "id": "st_20250125_001",
                "title": "Singapore Economy Shows Strong Growth",
                "summary": "싱가포르 경제가 강한 성장세를 보이고 있습니다...",
                "url": "https://www.straitstimes.com/...",
                "source": "The Straits Times",
                "group": "economy",
                "publishDate": "2025-01-25T08:30:00+08:00",
                "scrapedAt": "2025-01-25T08:00:00+09:00",
                "extracted_by": "hybrid_ai"
            }
        ]
    }
}
```

#### `POST /api/save-scraped-articles`
Save scraped articles to GitHub / 스크랩된 기사를 GitHub에 저장

**Request Body:**
```json
{
    "articles": [
        {
            "title": "New Policy Announced",
            "summary": "새로운 정책이 발표되었습니다...",
            "url": "https://example.com/article1",
            "source": "Channel NewsAsia",
            "group": "politics"
        }
    ],
    "metadata": {
        "scrapingMethod": "ai",
        "processTime": 325.5
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Articles saved successfully",
        "filename": "news_20250125_090000.json",
        "articlesCount": 1,
        "commitSha": "abc123def456"
    }
}
```

#### `DELETE /api/delete-scraped-file`
Delete specific scraped file / 특정 스크랩 파일 삭제

**Request Body:**
```json
{
    "filename": "news_20250120_080000.json"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "File deleted successfully",
        "filename": "news_20250120_080000.json",
        "commitSha": "xyz789abc123"
    }
}
```

### 4. Configuration / 설정

#### `POST /api/save-data`
Save settings or sites configuration / 설정 또는 사이트 구성 저장

**Request Body (Settings):**
```json
{
    "type": "settings",
    "settings": {
        "scrapingEnabled": true,
        "scrapingMethod": "hybrid_ai",
        "whatsappEnabled": true,
        "maxArticlesPerGroup": 5,
        "schedule": {
            "time": "07:55",
            "timezone": "Asia/Seoul"
        }
    }
}
```

**Request Body (Sites):**
```json
{
    "type": "sites",
    "sites": [
        {
            "name": "The Straits Times",
            "url": "https://www.straitstimes.com/singapore",
            "group": "politics",
            "enabled": true,
            "priority": "high"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Configuration saved successfully",
        "type": "settings",
        "commitSha": "def456ghi789"
    }
}
```

### 5. Monitoring / 모니터링

#### `GET /api/test-env`
Test environment variables and API connections / 환경 변수 및 API 연결 테스트

**Response:**
```json
{
    "success": true,
    "data": {
        "environment": {
            "GITHUB_TOKEN": "set",
            "GITHUB_OWNER": "djyalu",
            "GITHUB_REPO": "singapore_news_github",
            "WHATSAPP_API_KEY": "set"
        },
        "connections": {
            "github": {
                "connected": true,
                "rateLimit": {
                    "remaining": 4999,
                    "reset": "2025-01-25T10:00:00Z"
                }
            },
            "whatsapp": {
                "connected": true,
                "instance": "active"
            }
        },
        "timestamp": "2025-01-25T09:00:00+09:00"
    }
}
```

### 6. Email Notifications / 이메일 알림

#### `POST /api/send-email`
Send email notifications / 이메일 알림 전송

**Request Body:**
```json
{
    "to": "admin@example.com",
    "subject": "Scraping Report - 2025-01-25",
    "body": "Daily scraping completed successfully...",
    "html": "<h1>Daily Report</h1><p>Scraping completed...</p>",
    "attachments": [
        {
            "filename": "report.json",
            "content": "base64_encoded_content"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Email sent successfully",
        "messageId": "email_xxxxx",
        "accepted": ["admin@example.com"]
    }
}
```

## Request/Response Formats / 요청/응답 형식

### Request Headers / 요청 헤더
```
Content-Type: application/json
Accept: application/json
X-API-Version: 1.0.0
X-Request-ID: unique-request-id  // Optional for tracking
```

### Pagination / 페이지네이션
```javascript
// Request with pagination
GET /api/get-latest-scraped?page=2&limit=20

// Paginated response
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "page": 2,
            "limit": 20,
            "total": 150,
            "pages": 8,
            "hasNext": true,
            "hasPrev": true
        }
    }
}
```

### Filtering / 필터링
```javascript
// Multiple filters
GET /api/get-latest-scraped?group=economy&source=straitstimes&date=2025-01-25

// Date range filtering
GET /api/get-latest-scraped?startDate=2025-01-20&endDate=2025-01-25
```

### Sorting / 정렬
```javascript
// Sort parameters
GET /api/get-latest-scraped?sort=publishDate&order=desc

// Multiple sort fields
GET /api/get-latest-scraped?sort=group,publishDate&order=asc,desc
```

## Error Handling / 오류 처리

### Error Response Format / 오류 응답 형식
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request parameters",
        "details": {
            "field": "email",
            "reason": "Invalid email format"
        },
        "timestamp": "2025-01-25T09:00:00+09:00",
        "requestId": "req_xxxxx"
    }
}
```

### Common Error Codes / 일반적인 오류 코드
```javascript
// 4xx Client Errors
400 - BAD_REQUEST: Invalid request format
401 - UNAUTHORIZED: Authentication required
403 - FORBIDDEN: Insufficient permissions
404 - NOT_FOUND: Resource not found
409 - CONFLICT: Resource conflict
422 - VALIDATION_ERROR: Validation failed
429 - RATE_LIMITED: Too many requests

// 5xx Server Errors
500 - INTERNAL_ERROR: Server error
502 - BAD_GATEWAY: External service error
503 - SERVICE_UNAVAILABLE: Service temporarily unavailable
504 - TIMEOUT: Request timeout
```

### Error Handling Examples / 오류 처리 예제
```javascript
// JavaScript
try {
    const response = await fetch('/api/trigger-scraping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ method: 'ai' })
    });
    
    const data = await response.json();
    
    if (!data.success) {
        switch (data.error.code) {
            case 'RATE_LIMITED':
                console.log('Please wait before trying again');
                break;
            case 'VALIDATION_ERROR':
                console.log('Invalid parameters:', data.error.details);
                break;
            default:
                console.log('Error:', data.error.message);
        }
    }
} catch (error) {
    console.error('Network error:', error);
}
```

## Rate Limiting / 속도 제한

### Limits / 제한
```
Default Rate Limits:
- Anonymous: 60 requests per hour
- Authenticated: 300 requests per hour
- Scraping endpoints: 10 requests per hour
- WhatsApp endpoints: 30 requests per hour
```

### Rate Limit Headers / 속도 제한 헤더
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 298
X-RateLimit-Reset: 1706142000
X-RateLimit-Reset-After: 3600
```

### Rate Limit Response / 속도 제한 응답
```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMITED",
        "message": "Too many requests",
        "details": {
            "limit": 300,
            "remaining": 0,
            "resetAt": "2025-01-25T10:00:00+09:00",
            "retryAfter": 3600
        }
    }
}
```

## Code Examples / 코드 예제

### JavaScript (Browser) / JavaScript (브라우저)
```javascript
// Complete scraping workflow
async function performScraping() {
    try {
        // 1. Trigger scraping
        const startResponse = await fetch('https://singapore-news-github.vercel.app/api/trigger-scraping', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                method: 'hybrid_ai',
                sendWhatsApp: true
            })
        });
        
        const startData = await startResponse.json();
        const workflowId = startData.data.workflowId;
        
        // 2. Poll for status
        const checkStatus = async () => {
            const statusResponse = await fetch(`https://singapore-news-github.vercel.app/api/get-scraping-status?id=${workflowId}`);
            const statusData = await statusResponse.json();
            
            console.log(`Progress: ${statusData.data.progress}%`);
            
            if (statusData.data.status === 'completed') {
                console.log('Scraping completed!');
                // 3. Get results
                const resultsResponse = await fetch('https://singapore-news-github.vercel.app/api/get-latest-scraped');
                const results = await resultsResponse.json();
                console.log(`Collected ${results.data.count} articles`);
            } else if (statusData.data.status === 'running') {
                // Continue polling
                setTimeout(checkStatus, 5000);
            } else {
                console.error('Scraping failed:', statusData.data.error);
            }
        };
        
        setTimeout(checkStatus, 5000);
        
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### Python / 파이썬
```python
import requests
import time
import json

class SingaporeNewsAPI:
    def __init__(self, base_url='https://singapore-news-github.vercel.app/api'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def trigger_scraping(self, method='hybrid_ai', send_whatsapp=True):
        """Trigger scraping workflow"""
        response = self.session.post(
            f'{self.base_url}/trigger-scraping',
            json={
                'method': method,
                'sendWhatsApp': send_whatsapp
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self, workflow_id=None):
        """Get scraping status"""
        params = {'id': workflow_id} if workflow_id else {}
        response = self.session.get(
            f'{self.base_url}/get-scraping-status',
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_articles(self, limit=50, group=None):
        """Get latest scraped articles"""
        params = {'limit': limit}
        if group:
            params['group'] = group
        
        response = self.session.get(
            f'{self.base_url}/get-latest-scraped',
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, workflow_id, timeout=600):
        """Wait for scraping to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status(workflow_id)
            
            if status['data']['status'] == 'completed':
                return status
            elif status['data']['status'] == 'failed':
                raise Exception(f"Scraping failed: {status['data']['error']}")
            
            print(f"Progress: {status['data']['progress']}%")
            time.sleep(5)
        
        raise TimeoutError("Scraping timeout")

# Usage example
api = SingaporeNewsAPI()

# Start scraping
result = api.trigger_scraping(method='traditional')
workflow_id = result['data']['workflowId']

# Wait for completion
final_status = api.wait_for_completion(workflow_id)

# Get articles
articles = api.get_latest_articles(limit=20, group='economy')
print(f"Found {articles['data']['count']} articles")
```

### cURL / cURL 명령
```bash
# Authentication
curl -X POST https://singapore-news-github.vercel.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'

# Trigger scraping with options
curl -X POST https://singapore-news-github.vercel.app/api/trigger-scraping \
  -H "Content-Type: application/json" \
  -d '{
    "method": "ai",
    "sites": ["straitstimes", "channelnewsasia"],
    "sendWhatsApp": false
  }'

# Get latest articles with filters
curl -G https://singapore-news-github.vercel.app/api/get-latest-scraped \
  --data-urlencode "group=economy" \
  --data-urlencode "limit=10" \
  --data-urlencode "date=2025-01-25"

# Save settings
curl -X POST https://singapore-news-github.vercel.app/api/save-data \
  -H "Content-Type: application/json" \
  -d '{
    "type": "settings",
    "settings": {
      "scrapingEnabled": true,
      "maxArticlesPerGroup": 3
    }
  }'
```

### Node.js / Node.js
```javascript
const axios = require('axios');

class NewsScraperClient {
    constructor(baseURL = 'https://singapore-news-github.vercel.app/api') {
        this.client = axios.create({
            baseURL,
            timeout: 60000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response.data,
            error => {
                if (error.response?.data?.error) {
                    const apiError = new Error(error.response.data.error.message);
                    apiError.code = error.response.data.error.code;
                    apiError.details = error.response.data.error.details;
                    throw apiError;
                }
                throw error;
            }
        );
    }
    
    async triggerScraping(options = {}) {
        const response = await this.client.post('/trigger-scraping', {
            method: options.method || 'hybrid_ai',
            sites: options.sites || ['all'],
            sendWhatsApp: options.sendWhatsApp !== false
        });
        return response.data;
    }
    
    async getStatus(workflowId) {
        const response = await this.client.get('/get-scraping-status', {
            params: { id: workflowId }
        });
        return response.data;
    }
    
    async getLatestArticles(options = {}) {
        const response = await this.client.get('/get-latest-scraped', {
            params: {
                limit: options.limit || 50,
                group: options.group,
                date: options.date,
                page: options.page
            }
        });
        return response.data;
    }
    
    async saveSettings(settings) {
        const response = await this.client.post('/save-data', {
            type: 'settings',
            settings
        });
        return response.data;
    }
    
    async sendTestWhatsApp(message) {
        const response = await this.client.post('/test-whatsapp', {
            message
        });
        return response.data;
    }
}

// Usage
const client = new NewsScraperClient();

(async () => {
    try {
        // Start scraping
        const { workflowId } = await client.triggerScraping({
            method: 'traditional',
            sendWhatsApp: false
        });
        
        console.log(`Started workflow: ${workflowId}`);
        
        // Poll status
        let status;
        do {
            await new Promise(resolve => setTimeout(resolve, 5000));
            status = await client.getStatus(workflowId);
            console.log(`Progress: ${status.progress}%`);
        } while (status.status === 'running');
        
        // Get results
        const articles = await client.getLatestArticles({
            limit: 20,
            group: 'tech'
        });
        
        console.log(`Found ${articles.count} articles`);
        
    } catch (error) {
        console.error('Error:', error.message);
        if (error.code === 'RATE_LIMITED') {
            console.log(`Retry after: ${error.details.retryAfter} seconds`);
        }
    }
})();
```

## WebSocket Events / WebSocket 이벤트

### Connection / 연결
```javascript
// WebSocket endpoint (if implemented)
const ws = new WebSocket('wss://singapore-news-github.vercel.app/ws');

ws.on('open', () => {
    console.log('Connected to WebSocket');
    
    // Subscribe to events
    ws.send(JSON.stringify({
        type: 'subscribe',
        events: ['scraping.progress', 'scraping.complete']
    }));
});
```

### Event Types / 이벤트 타입
```javascript
// Scraping progress
{
    "type": "scraping.progress",
    "data": {
        "workflowId": "run_12345",
        "progress": 45,
        "currentSite": "Channel NewsAsia",
        "articlesCollected": 23
    }
}

// Scraping complete
{
    "type": "scraping.complete",
    "data": {
        "workflowId": "run_12345",
        "totalArticles": 56,
        "duration": 425.3,
        "status": "success"
    }
}

// Error event
{
    "type": "scraping.error",
    "data": {
        "workflowId": "run_12345",
        "error": "Site timeout: The Straits Times",
        "phase": "collecting"
    }
}
```

## Testing / 테스트

### Test Environment / 테스트 환경
```bash
# Use staging environment for testing
BASE_URL=https://singapore-news-github-staging.vercel.app/api

# Test credentials
TEST_USERNAME=testuser
TEST_PASSWORD=Test@123
```

### Integration Tests / 통합 테스트
```javascript
// Jest test example
describe('Singapore News API', () => {
    let client;
    
    beforeAll(() => {
        client = new NewsScraperClient(process.env.API_BASE_URL);
    });
    
    test('should trigger scraping successfully', async () => {
        const response = await client.triggerScraping({
            method: 'traditional',
            sendWhatsApp: false
        });
        
        expect(response.workflowId).toBeDefined();
        expect(response.estimatedTime).toBeGreaterThan(0);
    });
    
    test('should handle rate limiting', async () => {
        // Make many requests quickly
        const promises = Array(10).fill().map(() => 
            client.getLatestArticles()
        );
        
        await expect(Promise.all(promises)).rejects.toThrow('RATE_LIMITED');
    });
    
    test('should validate input parameters', async () => {
        await expect(
            client.triggerScraping({ method: 'invalid' })
        ).rejects.toThrow('VALIDATION_ERROR');
    });
});
```

### Load Testing / 부하 테스트
```javascript
// K6 load test script
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'], // 95% of requests under 3s
        http_req_failed: ['rate<0.1'],     // Error rate under 10%
    },
};

export default function () {
    const response = http.get('https://singapore-news-github.vercel.app/api/get-latest-scraped');
    
    check(response, {
        'status is 200': (r) => r.status === 200,
        'response has data': (r) => JSON.parse(r.body).success === true,
    });
    
    sleep(1);
}
```

## Migration Guide / 마이그레이션 가이드

### From v0.9 to v1.0 / v0.9에서 v1.0으로
```javascript
// Old API (v0.9)
GET /api/auth-config  // Deprecated
POST /api/auth-login  // Deprecated

// New API (v1.0)
GET /api/auth   // Get settings (authenticated)
POST /api/auth  // Login

// Migration code
async function migrateAuth() {
    // Old way
    // const config = await fetch('/api/auth-config');
    // const login = await fetch('/api/auth-login', {...});
    
    // New way
    const login = await fetch('/api/auth', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    
    const settings = await fetch('/api/auth', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
    });
}
```

### Breaking Changes / 주요 변경사항
```javascript
// 1. Consolidated endpoints
- /api/save-settings → /api/save-data (type: "settings")
- /api/save-sites → /api/save-data (type: "sites")

// 2. Response format standardization
// Old format
{ message: "Success", data: {...} }

// New format
{ success: true, data: {...}, timestamp: "..." }

// 3. Error format changes
// Old format
{ error: "Something went wrong" }

// New format
{ 
    success: false, 
    error: { 
        code: "ERROR_CODE", 
        message: "Description",
        details: {...}
    }
}
```

### Deprecation Timeline / 지원 중단 일정
```
v0.9 endpoints: Deprecated as of 2025-01-01
v0.9 endpoints: Will be removed 2025-04-01
v1.0 minimum support: Until 2026-01-01
```

---
*Last Updated: January 25, 2025*
*API Version: 1.0.0*