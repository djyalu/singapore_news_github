# System Architecture / 시스템 아키텍처

## Table of Contents / 목차
1. [System Overview / 시스템 개요](#system-overview--시스템-개요)
2. [Architecture Diagram / 아키텍처 다이어그램](#architecture-diagram--아키텍처-다이어그램)
3. [Component Details / 구성요소 상세](#component-details--구성요소-상세)
4. [Data Flow / 데이터 흐름](#data-flow--데이터-흐름)
5. [Technology Stack / 기술 스택](#technology-stack--기술-스택)
6. [Deployment Architecture / 배포 아키텍처](#deployment-architecture--배포-아키텍처)
7. [Security Architecture / 보안 아키텍처](#security-architecture--보안-아키텍처)
8. [Scalability Design / 확장성 설계](#scalability-design--확장성-설계)
9. [Integration Points / 통합 지점](#integration-points--통합-지점)
10. [Future Architecture / 미래 아키텍처](#future-architecture--미래-아키텍처)

## System Overview / 시스템 개요

Singapore News Scraper is a distributed system that automatically collects news from Singapore websites, generates Korean summaries using AI, and delivers them via WhatsApp. The system leverages multiple cloud services for high availability and scalability.

싱가포르 뉴스 스크래퍼는 싱가포르 웹사이트에서 뉴스를 자동으로 수집하고, AI를 사용하여 한국어 요약을 생성하며, WhatsApp을 통해 전달하는 분산 시스템입니다. 이 시스템은 높은 가용성과 확장성을 위해 여러 클라우드 서비스를 활용합니다.

### Key Principles / 핵심 원칙
- **Serverless First**: Minimize infrastructure management / 인프라 관리 최소화
- **Event-Driven**: Asynchronous processing / 비동기 처리
- **Stateless Design**: Horizontal scalability / 수평적 확장성
- **API-Centric**: Clear service boundaries / 명확한 서비스 경계
- **Cloud Native**: Leverage managed services / 관리형 서비스 활용

## Architecture Diagram / 아키텍처 다이어그램

### High-Level Architecture / 상위 수준 아키텍처
```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Users / 사용자                               │
└────────────────────┬───────────────────────┬───────────────────────────┘
                     │                       │
                     ▼                       ▼
        ┌─────────────────────┐   ┌─────────────────────┐
        │   GitHub Pages      │   │   WhatsApp          │
        │   (Frontend)        │   │   (Notifications)   │
        └──────────┬──────────┘   └─────────▲───────────┘
                   │                         │
                   ▼                         │
        ┌─────────────────────────────────────────────┐
        │            Vercel Edge Network              │
        │         (API Gateway & Functions)           │
        └────────┬────────────────────────┬───────────┘
                 │                        │
                 ▼                        ▼
    ┌───────────────────────┐  ┌────────────────────┐
    │   GitHub Actions      │  │   External APIs    │
    │   (Automation)        │  │   - Gemini AI      │
    │   - Scheduled Jobs    │  │   - Green API      │
    │   - Workflows         │  │   - News Sites     │
    └──────────┬────────────┘  └────────────────────┘
               │
               ▼
    ┌───────────────────────┐
    │   GitHub Repository   │
    │   (Data Storage)      │
    │   - JSON Files        │
    │   - Configuration     │
    └───────────────────────┘
```

### Detailed Component Architecture / 상세 구성요소 아키텍처
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   HTML5     │  │  JavaScript │  │    CSS3     │            │
│  │   Pages     │  │  (Vanilla)  │  │   Styles    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────────────────────────────────────────┐           │
│  │            Service Worker (PWA)                  │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Scraping   │  │   WhatsApp   │  │    Data      │         │
│  │   Control    │  │  Integration │  │  Management  │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • trigger    │  │ • send-only  │  │ • get-latest │         │
│  │ • scrape-only│  │ • test       │  │ • save       │         │
│  │ • status     │  │              │  │ • delete     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Auth      │  │  Monitoring  │  │    Email     │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐           │
│  │           GitHub Actions Workflows               │           │
│  ├─────────────────────────────────────────────────┤           │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐│           │
│  │  │  Scraper   │  │  WhatsApp  │  │  Cleanup   ││           │
│  │  │  Workflow  │  │  Workflow  │  │  Workflow  ││           │
│  │  └────────────┘  └────────────┘  └────────────┘│           │
│  └─────────────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────────────┐           │
│  │            Python Scripts                        │           │
│  ├─────────────────────────────────────────────────┤           │
│  │  • scraper.py      • ai_scraper.py             │           │
│  │  • scraper_rss.py  • scraper_hybrid.py         │           │
│  │  • send_whatsapp_green.py                      │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐           │
│  │              GitHub Repository                   │           │
│  ├─────────────────────────────────────────────────┤           │
│  │  /data                                          │           │
│  │    ├── settings.json    # System configuration  │           │
│  │    ├── sites.json       # Site definitions      │           │
│  │    ├── latest.json      # Latest scraped data   │           │
│  │    ├── /scraped         # Historical data       │           │
│  │    └── /history         # WhatsApp logs         │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details / 구성요소 상세

### 1. Frontend Components / 프론트엔드 구성요소

#### GitHub Pages Static Hosting
```javascript
// Architecture decisions
{
    "hosting": "GitHub Pages",
    "reasons": [
        "Free hosting for public repositories",
        "Automatic SSL certificates",
        "Global CDN distribution",
        "Git-based deployment"
    ],
    "limitations": [
        "Static files only",
        "No server-side processing",
        "Build size limits"
    ]
}
```

#### Client-Side Architecture
```javascript
// Modular JavaScript architecture
const AppArchitecture = {
    modules: {
        auth: {
            file: 'js/auth.js',
            responsibilities: ['User authentication', 'Session management']
        },
        app: {
            file: 'js/app.js',
            responsibilities: ['Main application logic', 'API integration', 'UI updates']
        },
        config: {
            file: 'js/config.js',
            responsibilities: ['Configuration management', 'Environment settings']
        }
    },
    
    patterns: [
        'Module pattern for encapsulation',
        'Event-driven communication',
        'Promise-based async operations',
        'Component-based UI updates'
    ]
};
```

### 2. API Layer Components / API 레이어 구성요소

#### Vercel Serverless Functions
```javascript
// Function architecture pattern
export default async function handler(req, res) {
    // 1. Request validation
    const validation = validateRequest(req);
    if (!validation.valid) {
        return res.status(400).json({ 
            success: false, 
            error: validation.error 
        });
    }
    
    // 2. Authentication check
    const auth = await checkAuthentication(req);
    if (!auth.authenticated) {
        return res.status(401).json({ 
            success: false, 
            error: 'Unauthorized' 
        });
    }
    
    // 3. Business logic
    try {
        const result = await processBusinessLogic(req.body);
        
        // 4. Response formatting
        res.status(200).json({
            success: true,
            data: result,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        // 5. Error handling
        handleError(error, res);
    }
}
```

#### API Gateway Pattern
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Client    │────▶│  Vercel Edge    │────▶│   Function      │
│   (Frontend)    │     │   (Gateway)     │     │   Handler       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Middleware       │
                    │  • CORS            │
                    │  • Rate Limiting   │
                    │  • Logging         │
                    └─────────────────────┘
```

### 3. Processing Layer / 처리 레이어

#### GitHub Actions Architecture
```yaml
# Workflow architecture
name: Scraping Pipeline
on:
  schedule:
    - cron: '55 22 * * *'  # Daily execution
  workflow_dispatch:       # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    
    strategy:
      matrix:
        python-version: [3.9]
    
    steps:
      - name: Setup Environment
        # Environment preparation
        
      - name: Execute Scraping
        # Main processing logic
        
      - name: Post-processing
        # Data validation and storage
        
      - name: Notification
        # Status updates
```

#### Scraping Engine Architecture
```python
# Modular scraping architecture
class ScraperArchitecture:
    def __init__(self):
        self.components = {
            'extractors': {
                'traditional': TraditionalExtractor(),
                'ai': AIExtractor(),
                'rss': RSSExtractor(),
                'hybrid': HybridExtractor()
            },
            'processors': {
                'text': TextProcessor(),
                'summary': SummaryGenerator(),
                'translator': KoreanTranslator()
            },
            'storage': {
                'github': GitHubStorage(),
                'cache': LocalCache()
            }
        }
    
    def scrape_pipeline(self, method='hybrid'):
        # 1. Select extractor
        extractor = self.components['extractors'][method]
        
        # 2. Extract articles
        raw_articles = extractor.extract()
        
        # 3. Process articles
        processed = []
        for article in raw_articles:
            # Text processing
            article = self.components['processors']['text'].process(article)
            
            # Generate summary
            article = self.components['processors']['summary'].generate(article)
            
            # Translate to Korean
            article = self.components['processors']['translator'].translate(article)
            
            processed.append(article)
        
        # 4. Store results
        self.components['storage']['github'].save(processed)
        
        return processed
```

### 4. Storage Architecture / 저장소 아키텍처

#### Data Schema Design
```javascript
// settings.json schema
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["scrapingEnabled", "scrapingMethod", "whatsappEnabled"],
    "properties": {
        "scrapingEnabled": { "type": "boolean" },
        "scrapingMethod": { 
            "type": "string",
            "enum": ["traditional", "ai", "hybrid_ai"]
        },
        "whatsappEnabled": { "type": "boolean" },
        "maxArticlesPerGroup": { 
            "type": "integer",
            "minimum": 1,
            "maximum": 10
        },
        "schedule": {
            "type": "object",
            "properties": {
                "time": { "type": "string", "pattern": "^\\d{2}:\\d{2}$" },
                "timezone": { "type": "string" }
            }
        }
    }
}

// Article data schema
{
    "type": "object",
    "required": ["id", "title", "url", "source", "group"],
    "properties": {
        "id": { "type": "string" },
        "title": { "type": "string" },
        "summary": { "type": "string" },
        "url": { "type": "string", "format": "uri" },
        "source": { "type": "string" },
        "group": { 
            "type": "string",
            "enum": ["politics", "economy", "society", "tech", "lifestyle"]
        },
        "publishDate": { "type": "string", "format": "date-time" },
        "scrapedAt": { "type": "string", "format": "date-time" },
        "extracted_by": { "type": "string" }
    }
}
```

#### File Organization Strategy
```
/data
├── settings.json           # Singleton configuration
├── sites.json             # Site definitions
├── latest.json            # Symlink to latest scraped file
├── /scraped               # Time-series data
│   ├── news_20250125_080000.json
│   ├── news_20250125_200000.json
│   └── ...
└── /history               # Audit trail
    ├── whatsapp_20250125_080100.json
    └── ...

# Naming convention: {type}_{YYYYMMDD}_{HHMMSS}.json
# Retention: 30 days automatic cleanup
# Backup: Git history serves as backup
```

## Data Flow / 데이터 흐름

### 1. Scraping Data Flow / 스크래핑 데이터 흐름
```
User Trigger / Scheduled Job
         │
         ▼
    Vercel API
         │
         ▼
  GitHub Actions
         │
    ┌────┴────┐
    ▼         ▼
News Sites  Gemini AI
    │         │
    └────┬────┘
         ▼
   Processing
         │
         ▼
  GitHub Storage
         │
    ┌────┴────┐
    ▼         ▼
Dashboard  WhatsApp
```

### 2. API Request Flow / API 요청 흐름
```
Frontend Request
      │
      ▼
 DNS Resolution
      │
      ▼
Vercel Edge Network
      │
      ▼
 Edge Function
      │
      ├──▶ Authentication
      │
      ├──▶ Validation
      │
      ├──▶ Business Logic
      │
      ├──▶ External APIs
      │
      └──▶ Response
```

### 3. WhatsApp Message Flow / WhatsApp 메시지 흐름
```
Scraped Articles
      │
      ▼
Message Formatter
      │
      ▼
 Green API Client
      │
      ▼
  WhatsApp API
      │
      ▼
Message Validation
      │
      ▼
 Channel Routing
      │
      ▼
  User Devices
```

## Technology Stack / 기술 스택

### Frontend Technologies
```yaml
Core:
  - HTML5: Semantic markup
  - CSS3: Modern styling with flexbox/grid
  - JavaScript: ES6+ vanilla JS
  
Libraries:
  - None: Intentionally dependency-free
  
Tools:
  - Git: Version control
  - GitHub Pages: Hosting
  
Future Considerations:
  - React/Vue: If complexity increases
  - TypeScript: For type safety
  - Webpack: For bundling
```

### Backend Technologies
```yaml
Runtime:
  - Node.js 16+: Vercel functions
  - Python 3.9+: Scraping scripts
  
Frameworks:
  - None: Lightweight approach
  
Libraries:
  Python:
    - requests: HTTP client
    - beautifulsoup4: HTML parsing
    - feedparser: RSS parsing
    - google-generativeai: AI summaries
    - pytz: Timezone handling
  
  Node.js:
    - @octokit/rest: GitHub API
    - Built-in modules preferred
```

### Infrastructure Technologies
```yaml
Hosting:
  - GitHub Pages: Static frontend
  - Vercel: Serverless functions
  - GitHub Actions: Automation
  
Storage:
  - GitHub Repository: JSON data
  - Git LFS: Not used (small files)
  
CDN:
  - GitHub Pages CDN: Global distribution
  - Vercel Edge Network: API caching
  
Monitoring:
  - Vercel Analytics: Basic metrics
  - GitHub Actions logs: Execution tracking
```

### External Services
```yaml
AI Services:
  - Google Gemini API: Text summarization
  - Fallback: Basic extractive summary
  
Messaging:
  - Green API: WhatsApp integration
  - Future: Telegram, Email
  
News Sources:
  - 16 Singapore news websites
  - RSS feeds where available
  - HTML scraping as fallback
```

## Deployment Architecture / 배포 아키텍처

### Multi-Environment Strategy
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Development │────▶│   Staging   │────▶│ Production  │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
  Local Dev         Branch Deploy        Main Branch
  localhost:3000    staging.app          app.com
```

### CI/CD Pipeline
```yaml
# Deployment pipeline
on:
  push:
    branches: [main, staging]

jobs:
  test:
    steps:
      - Lint code
      - Run tests
      - Security scan
  
  build:
    needs: test
    steps:
      - Build assets
      - Optimize images
      - Generate manifests
  
  deploy:
    needs: build
    steps:
      - Deploy to environment
      - Smoke tests
      - Notify team
```

### Zero-Downtime Deployment
```
1. Blue-Green Strategy
   Active (Blue) ──────▶ Users
   Standby (Green) ────▶ New Version
   
2. Switch Traffic
   Active (Green) ─────▶ Users
   Standby (Blue) ─────▶ Old Version
   
3. Rollback Ready
   Instant switch back if issues
```

## Security Architecture / 보안 아키텍처

### Security Layers
```
┌─────────────────────────────────────┐
│         Application Layer           │
│  • Input validation                 │
│  • Output encoding                  │
│  • Session management               │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│          Network Layer              │
│  • HTTPS everywhere                 │
│  • CORS policies                    │
│  • Rate limiting                    │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         Storage Layer               │
│  • Encrypted secrets                │
│  • Access control                   │
│  • Audit logging                    │
└─────────────────────────────────────┘
```

### Authentication Flow
```
User Login Request
       │
       ▼
Validate Credentials
       │
   ┌───┴───┐
   │       │
Success  Failure
   │       │
   ▼       ▼
Create   Rate
Session  Limit
   │       
   ▼       
Store    
Token    
```

### API Security
```javascript
// Security middleware stack
const securityMiddleware = [
    corsHandler({
        origin: process.env.ALLOWED_ORIGINS?.split(','),
        credentials: true
    }),
    
    rateLimiter({
        windowMs: 15 * 60 * 1000,  // 15 minutes
        max: 100                     // limit each IP
    }),
    
    helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                styleSrc: ["'self'", "'unsafe-inline'"]
            }
        }
    }),
    
    inputValidator({
        stripUnknown: true,
        abortEarly: false
    })
];
```

## Scalability Design / 확장성 설계

### Horizontal Scaling Strategy
```
Current State (100 users/day)
┌─────────────┐
│  1 Instance │
└─────────────┘

Scaled State (10,000 users/day)
┌─────┬─────┬─────┐
│ Inst│ Inst│ Inst│
│  1  │  2  │  3  │
└─────┴─────┴─────┘
   Load Balancer
```

### Performance Optimization
```python
# Caching strategy
class CachingArchitecture:
    layers = {
        'edge': {
            'location': 'Vercel Edge Network',
            'ttl': 300,  # 5 minutes
            'content': ['Static assets', 'API responses']
        },
        'application': {
            'location': 'Function memory',
            'ttl': 60,   # 1 minute
            'content': ['Computed results', 'External API calls']
        },
        'storage': {
            'location': 'GitHub repository',
            'ttl': 86400,  # 24 hours
            'content': ['Scraped articles', 'Processed summaries']
        }
    }
```

### Database Sharding Strategy
```
# Future: When data exceeds single repo limits

Sharding by Date:
├── data-2025-01/
├── data-2025-02/
└── data-2025-03/

Sharding by Category:
├── data-politics/
├── data-economy/
└── data-tech/
```

## Integration Points / 통합 지점

### External API Integrations
```javascript
// Integration abstraction layer
class IntegrationManager {
    constructor() {
        this.integrations = {
            gemini: new GeminiIntegration({
                apiKey: process.env.GEMINI_API_KEY,
                retryPolicy: exponentialBackoff,
                timeout: 30000
            }),
            
            whatsapp: new WhatsAppIntegration({
                apiKey: process.env.WHATSAPP_API_KEY,
                baseUrl: 'https://api.green-api.com',
                maxMessageLength: 4096
            }),
            
            github: new GitHubIntegration({
                token: process.env.GITHUB_TOKEN,
                owner: process.env.GITHUB_OWNER,
                repo: process.env.GITHUB_REPO
            })
        };
    }
    
    async callWithFallback(integration, method, ...args) {
        try {
            return await this.integrations[integration][method](...args);
        } catch (error) {
            // Fallback logic
            return this.handleIntegrationError(integration, error);
        }
    }
}
```

### Webhook Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GitHub    │────▶│   Webhook   │────▶│   Action    │
│   Events    │     │   Handler   │     │   Trigger   │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │ Validation  │
                    │ • Signature │
                    │ • Payload   │
                    └─────────────┘
```

### Event Bus Design
```javascript
// Future: Event-driven architecture
class EventBus {
    constructor() {
        this.events = {
            'article.scraped': [],
            'summary.generated': [],
            'message.sent': [],
            'error.occurred': []
        };
    }
    
    emit(event, data) {
        this.events[event]?.forEach(handler => {
            setImmediate(() => handler(data));
        });
    }
    
    on(event, handler) {
        this.events[event] = this.events[event] || [];
        this.events[event].push(handler);
    }
}
```

## Future Architecture / 미래 아키텍처

### Microservices Evolution
```
Current: Monolithic Functions
┌─────────────────────────┐
│   All API Endpoints     │
│   in Single Project     │
└─────────────────────────┘

Future: Microservices
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Scraping │ │ Summary  │ │ Delivery │
│ Service  │ │ Service  │ │ Service  │
└──────────┘ └──────────┘ └──────────┘
     │            │            │
     └────────────┴────────────┘
              Message Bus
```

### Advanced Features Roadmap
```yaml
Phase 1 (Current):
  - Basic scraping and delivery
  - Simple authentication
  - Manual triggers

Phase 2 (Next 6 months):
  - Multi-language support
  - Advanced analytics
  - User preferences
  - Mobile app

Phase 3 (Next year):
  - Machine learning for relevance
  - Real-time notifications
  - Multiple delivery channels
  - API marketplace

Phase 4 (Future):
  - Distributed scraping network
  - Blockchain for data integrity
  - Federation with other scrapers
  - AI-powered insights
```

### Infrastructure Evolution
```
Step 1: Current
- GitHub Pages + Vercel
- Simple and free

Step 2: Growth
- Add CloudFlare CDN
- Redis for caching
- PostgreSQL for data

Step 3: Scale
- Kubernetes deployment
- Multi-region presence
- Advanced monitoring

Step 4: Enterprise
- Private cloud option
- On-premise deployment
- SLA guarantees
```

---
*Last Updated: January 25, 2025*
*Version: 1.0.0*