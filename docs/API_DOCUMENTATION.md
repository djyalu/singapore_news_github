# Singapore News Scraper API Documentation

This document provides comprehensive API documentation for all endpoints in the Singapore News Scraper system.

## Base URL

```
https://singapore-news-github.vercel.app/api
```

## Authentication

Most API endpoints require authentication. The authentication is handled through the `/api/auth` endpoint.

### Login
```http
POST /api/auth
Content-Type: application/json

{
  "type": "login",
  "username": "admin",
  "password": "Admin@123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "로그인 성공"
}
```

## API Endpoints Overview

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth` | GET/POST | Authentication & Settings | No/Yes |
| `/api/trigger-scraping` | POST | Trigger full scraping workflow | Yes |
| `/api/scrape-only` | POST | Trigger scraping only | Yes |
| `/api/send-only` | POST | Trigger WhatsApp sending only | Yes |
| `/api/get-scraping-status` | GET | Get scraping status | Yes |
| `/api/save-data` | POST | Save settings or sites | Yes |
| `/api/get-latest-scraped` | GET | Get latest scraped data | Yes |
| `/api/delete-scraped-file` | POST | Delete scraped files | Yes |
| `/api/save-scraped-articles` | POST | Save scraped articles | Yes |
| `/api/send-email` | POST | Send email notification | Yes |
| `/api/test-whatsapp` | POST | Test WhatsApp message | Yes |
| `/api/test-env` | GET | Test environment variables | No |

## Detailed API Documentation

### 1. Authentication & Settings

#### GET /api/auth
Get current settings and site configuration.

**Query Parameters:**
- `type` (required): "settings"

**Response:**
```json
{
  "settings": {
    "maxArticlesPerSite": 3,
    "scrapingTimeoutMinutes": 30,
    "whatsappChannels": [
      {
        "id": "120363419092108413@g.us",
        "name": "Singapore News Main (Test)",
        "enabled": true
      }
    ],
    "users": {
      "admin": {
        "password": "Admin@123",
        "role": "admin",
        "name": "Administrator"
      }
    },
    "scrapingMethod": "ai"
  },
  "sites": [
    {
      "name": "The Straits Times",
      "url": "https://www.straitstimes.com",
      "group": "News",
      "enabled": true
    }
  ]
}
```

#### POST /api/auth
User authentication.

**Request Body:**
```json
{
  "type": "login",
  "username": "admin",
  "password": "Admin@123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "로그인 성공"
}
```

### 2. Scraping Operations

#### POST /api/trigger-scraping
Trigger the full scraping and WhatsApp sending workflow.

**Request Body:**
```json
{
  "manual": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "스크래핑 워크플로우가 시작되었습니다",
  "run_id": 12345678,
  "run_url": "https://github.com/djyalu/singapore_news_github/actions/runs/12345678"
}
```

#### POST /api/scrape-only
Trigger scraping without WhatsApp sending.

**Request Body:**
```json
{
  "manual": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "스크래핑 워크플로우가 시작되었습니다 (스크래핑만)",
  "run_id": 12345679,
  "run_url": "https://github.com/djyalu/singapore_news_github/actions/runs/12345679"
}
```

#### POST /api/send-only
Send already scraped news to WhatsApp.

**Request Body:**
```json
{
  "manual": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "WhatsApp 전송 워크플로우가 시작되었습니다",
  "run_id": 12345680,
  "run_url": "https://github.com/djyalu/singapore_news_github/actions/runs/12345680"
}
```

### 3. Status & Data Operations

#### GET /api/get-scraping-status
Get the status of recent scraping operations.

**Query Parameters:**
- `limit` (optional): Number of recent runs to fetch (default: 5)

**Response:**
```json
{
  "runs": [
    {
      "id": 12345678,
      "name": "Singapore News Scraper",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-07-23T00:00:00Z",
      "updated_at": "2025-07-23T00:15:00Z",
      "run_number": 456,
      "html_url": "https://github.com/djyalu/singapore_news_github/actions/runs/12345678"
    }
  ]
}
```

#### GET /api/get-latest-scraped
Get the latest scraped news data.

**Response:**
```json
{
  "timestamp": "2025-07-23T00:28:22+09:00",
  "articles": [
    {
      "title": "Singapore economy grows 4% in Q2",
      "summary": "싱가포르 경제가 2분기에 4% 성장했습니다...",
      "url": "https://www.straitstimes.com/business/economy/...",
      "site": "The Straits Times",
      "group": "Economy",
      "scraped_at": "2025-07-23T00:28:22+09:00"
    }
  ],
  "stats": {
    "total": 15,
    "byGroup": {
      "News": 5,
      "Economy": 4,
      "Politics": 3,
      "Events": 3
    }
  }
}
```

### 4. Data Management

#### POST /api/save-data
Save settings or site configuration.

**Request Body (for settings):**
```json
{
  "type": "settings",
  "settings": {
    "maxArticlesPerSite": 3,
    "scrapingTimeoutMinutes": 30,
    "whatsappChannels": [...],
    "users": {...},
    "scrapingMethod": "ai"
  }
}
```

**Request Body (for sites):**
```json
{
  "type": "sites",
  "sites": [
    {
      "name": "The Straits Times",
      "url": "https://www.straitstimes.com",
      "group": "News",
      "enabled": true
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "설정이 저장되었습니다"
}
```

#### POST /api/delete-scraped-file
Delete specific scraped data files.

**Request Body:**
```json
{
  "filename": "news_20250723_002822.json"
}
```

**Response:**
```json
{
  "success": true,
  "message": "파일이 삭제되었습니다"
}
```

#### POST /api/save-scraped-articles
Save new scraped articles to GitHub.

**Request Body:**
```json
{
  "timestamp": "2025-07-23T00:28:22+09:00",
  "articles": [
    {
      "title": "Breaking News",
      "summary": "뉴스 요약...",
      "url": "https://example.com/news",
      "site": "Example Site",
      "group": "News"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "스크랩 데이터가 저장되었습니다",
  "filename": "news_20250723_002822.json"
}
```

### 5. Communication

#### POST /api/send-email
Send email notifications.

**Request Body:**
```json
{
  "to": "user@example.com",
  "subject": "Singapore News Scraper Alert",
  "body": "Your scraping job has completed successfully."
}
```

**Response:**
```json
{
  "success": true,
  "message": "이메일이 전송되었습니다"
}
```

#### POST /api/test-whatsapp
Send a test WhatsApp message.

**Request Body:**
```json
{
  "message": "테스트 메시지입니다",
  "channelId": "120363419092108413@g.us"
}
```

**Response:**
```json
{
  "success": true,
  "message": "WhatsApp 테스트 메시지가 전송되었습니다",
  "messageId": "3EB0C767D097695C4308"
}
```

### 6. System

#### GET /api/test-env
Test environment variables configuration.

**Response:**
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

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

- No explicit rate limiting is implemented
- Vercel free tier limitations apply
- GitHub API rate limits: 5000 requests/hour with authentication

## CORS Configuration

All endpoints are configured with CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Example Usage

### Using cURL

```bash
# Login
curl -X POST https://singapore-news-github.vercel.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"type":"login","username":"admin","password":"Admin@123"}'

# Trigger scraping
curl -X POST https://singapore-news-github.vercel.app/api/trigger-scraping \
  -H "Content-Type: application/json" \
  -d '{"manual":true}'

# Get latest scraped data
curl https://singapore-news-github.vercel.app/api/get-latest-scraped
```

### Using JavaScript (Fetch API)

```javascript
// Login
const loginResponse = await fetch('https://singapore-news-github.vercel.app/api/auth', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'login',
    username: 'admin',
    password: 'Admin@123'
  })
});

// Trigger scraping
const scrapingResponse = await fetch('https://singapore-news-github.vercel.app/api/trigger-scraping', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ manual: true })
});

// Get latest data
const latestData = await fetch('https://singapore-news-github.vercel.app/api/get-latest-scraped');
const data = await latestData.json();
```

## Notes

1. All timestamps are in KST (Korea Standard Time, UTC+9)
2. File naming convention: `news_YYYYMMDD_HHMMSS.json`
3. Maximum 12 API endpoints due to Vercel free tier limitations
4. All text responses are in Korean except for technical fields