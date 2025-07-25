# Performance Tuning Guide / 성능 튜닝 가이드

## Table of Contents / 목차
1. [Performance Overview / 성능 개요](#performance-overview--성능-개요)
2. [Performance Metrics / 성능 지표](#performance-metrics--성능-지표)
3. [Frontend Optimization / 프론트엔드 최적화](#frontend-optimization--프론트엔드-최적화)
4. [Backend Optimization / 백엔드 최적화](#backend-optimization--백엔드-최적화)
5. [Database Optimization / 데이터베이스 최적화](#database-optimization--데이터베이스-최적화)
6. [Scraping Optimization / 스크래핑 최적화](#scraping-optimization--스크래핑-최적화)
7. [API Optimization / API 최적화](#api-optimization--api-최적화)
8. [Caching Strategies / 캐싱 전략](#caching-strategies--캐싱-전략)
9. [Load Testing / 부하 테스트](#load-testing--부하-테스트)
10. [Monitoring & Profiling / 모니터링 및 프로파일링](#monitoring--profiling--모니터링-및-프로파일링)

## Performance Overview / 성능 개요

### Current Performance Benchmarks / 현재 성능 벤치마크
```yaml
Page Load Times:
  Dashboard: 1.8s (Target: <2s)
  Article List: 1.2s (Target: <1.5s)
  Settings: 0.8s (Target: <1s)

API Response Times:
  GET /api/get-latest-scraped: 300ms (Target: <500ms)
  POST /api/trigger-scraping: 200ms (Target: <300ms)
  GET /api/get-scraping-status: 100ms (Target: <200ms)

Scraping Performance:
  Traditional Method: 5 minutes (16 sites)
  AI Method: 7 minutes (16 sites)
  Hybrid Method: 6 minutes (16 sites)

Concurrent Users:
  Current Capacity: 1,000
  Target Capacity: 10,000
```

### Performance Goals / 성능 목표
- **Response Time**: 95th percentile < 1 second
- **Throughput**: 1,000 requests/second
- **Error Rate**: < 0.1%
- **Availability**: 99.9% uptime

## Performance Metrics / 성능 지표

### Key Performance Indicators (KPIs)
```javascript
// Performance monitoring setup
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            responseTime: new Histogram(),
            throughput: new Counter(),
            errorRate: new Counter(),
            activeConnections: new Gauge()
        };
    }
    
    trackRequestTime(endpoint, duration) {
        this.metrics.responseTime.observe(
            { endpoint },
            duration
        );
    }
    
    trackThroughput(endpoint) {
        this.metrics.throughput.inc({ endpoint });
    }
    
    getMetrics() {
        return {
            avgResponseTime: this.metrics.responseTime.mean(),
            p95ResponseTime: this.metrics.responseTime.percentile(0.95),
            p99ResponseTime: this.metrics.responseTime.percentile(0.99),
            requestsPerSecond: this.metrics.throughput.rate(),
            errorRate: this.calculateErrorRate(),
            activeConnections: this.metrics.activeConnections.value()
        };
    }
}
```

### Web Vitals Monitoring
```javascript
// Client-side performance metrics
function measureWebVitals() {
    // Largest Contentful Paint (LCP)
    new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
    }).observe({ entryTypes: ['largest-contentful-paint'] });
    
    // First Input Delay (FID)
    new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
            console.log('FID:', entry.processingStart - entry.startTime);
        });
    }).observe({ entryTypes: ['first-input'] });
    
    // Cumulative Layout Shift (CLS)
    let clsValue = 0;
    new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
                clsValue += entry.value;
                console.log('CLS:', clsValue);
            }
        }
    }).observe({ entryTypes: ['layout-shift'] });
}
```

## Frontend Optimization / 프론트엔드 최적화

### 1. Resource Optimization / 리소스 최적화

#### Bundle Size Reduction
```javascript
// Webpack configuration for optimization
module.exports = {
    optimization: {
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    priority: -10
                },
                common: {
                    minChunks: 2,
                    priority: -20,
                    reuseExistingChunk: true
                }
            }
        },
        minimize: true,
        minimizer: [
            new TerserPlugin({
                terserOptions: {
                    compress: {
                        drop_console: true,
                        drop_debugger: true
                    }
                }
            })
        ]
    }
};
```

#### Image Optimization
```html
<!-- Responsive images with WebP support -->
<picture>
    <source 
        srcset="image-small.webp 480w,
                image-medium.webp 800w,
                image-large.webp 1200w"
        type="image/webp">
    <source 
        srcset="image-small.jpg 480w,
                image-medium.jpg 800w,
                image-large.jpg 1200w"
        type="image/jpeg">
    <img src="image-medium.jpg" 
         alt="Description"
         loading="lazy"
         decoding="async">
</picture>
```

#### CSS Optimization
```css
/* Critical CSS inline in HTML */
<style>
/* Only above-the-fold styles */
body { margin: 0; font-family: system-ui; }
.header { background: #fff; height: 60px; }
.main { max-width: 1200px; margin: 0 auto; }
</style>

/* Non-critical CSS loaded asynchronously */
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
```

### 2. JavaScript Optimization / JavaScript 최적화

#### Code Splitting
```javascript
// Dynamic imports for code splitting
const loadDashboard = () => import('./dashboard.js');
const loadSettings = () => import('./settings.js');
const loadArticles = () => import('./articles.js');

// Route-based code splitting
const router = {
    '/dashboard': async () => {
        const module = await loadDashboard();
        module.init();
    },
    '/settings': async () => {
        const module = await loadSettings();
        module.init();
    },
    '/articles': async () => {
        const module = await loadArticles();
        module.init();
    }
};
```

#### Debouncing and Throttling
```javascript
// Debounce for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce((e) => {
    performSearch(e.target.value);
}, 300));

// Throttle for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

window.addEventListener('scroll', throttle(() => {
    updateScrollPosition();
}, 100));
```

#### Virtual Scrolling
```javascript
// Virtual scrolling for large lists
class VirtualScroll {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleCount = Math.ceil(container.clientHeight / itemHeight);
        this.startIndex = 0;
        
        this.init();
    }
    
    init() {
        // Create scrollable area
        this.scroller = document.createElement('div');
        this.scroller.style.height = `${this.items.length * this.itemHeight}px`;
        this.scroller.style.position = 'relative';
        
        // Create viewport
        this.viewport = document.createElement('div');
        this.viewport.style.height = '100%';
        this.viewport.style.overflow = 'auto';
        
        this.viewport.appendChild(this.scroller);
        this.container.appendChild(this.viewport);
        
        // Handle scroll
        this.viewport.addEventListener('scroll', () => this.handleScroll());
        
        // Initial render
        this.render();
    }
    
    handleScroll() {
        const scrollTop = this.viewport.scrollTop;
        const newStartIndex = Math.floor(scrollTop / this.itemHeight);
        
        if (newStartIndex !== this.startIndex) {
            this.startIndex = newStartIndex;
            this.render();
        }
    }
    
    render() {
        // Clear existing items
        this.scroller.innerHTML = '';
        
        // Render visible items
        const endIndex = Math.min(
            this.startIndex + this.visibleCount + 1,
            this.items.length
        );
        
        for (let i = this.startIndex; i < endIndex; i++) {
            const item = this.createItemElement(this.items[i], i);
            item.style.position = 'absolute';
            item.style.top = `${i * this.itemHeight}px`;
            this.scroller.appendChild(item);
        }
    }
    
    createItemElement(item, index) {
        const element = document.createElement('div');
        element.className = 'virtual-item';
        element.style.height = `${this.itemHeight}px`;
        element.textContent = item.title;
        return element;
    }
}
```

### 3. Network Optimization / 네트워크 최적화

#### Resource Hints
```html
<!-- DNS prefetch for external domains -->
<link rel="dns-prefetch" href="//api.example.com">
<link rel="dns-prefetch" href="//cdn.example.com">

<!-- Preconnect for critical resources -->
<link rel="preconnect" href="https://api.example.com" crossorigin>

<!-- Prefetch for likely next pages -->
<link rel="prefetch" href="/articles.html">
<link rel="prefetch" href="/settings.html">

<!-- Preload critical resources -->
<link rel="preload" href="/css/critical.css" as="style">
<link rel="preload" href="/js/app.js" as="script">
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
```

#### Service Worker Caching
```javascript
// Service worker for offline support and caching
const CACHE_NAME = 'sg-news-v1';
const urlsToCache = [
    '/',
    '/css/styles.css',
    '/js/app.js',
    '/images/logo.png'
];

// Install event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

// Fetch event with cache-first strategy
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                
                // Clone the request
                const fetchRequest = event.request.clone();
                
                return fetch(fetchRequest).then((response) => {
                    // Check if valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    // Clone the response
                    const responseToCache = response.clone();
                    
                    // Cache the response
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });
                    
                    return response;
                });
            })
    );
});
```

## Backend Optimization / 백엔드 최적화

### 1. Node.js Optimization / Node.js 최적화

#### Clustering
```javascript
// Utilize all CPU cores
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
    console.log(`Master ${process.pid} is running`);
    
    // Fork workers
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }
    
    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        // Replace dead worker
        cluster.fork();
    });
} else {
    // Workers can share any TCP connection
    require('./server.js');
    console.log(`Worker ${process.pid} started`);
}
```

#### Memory Management
```javascript
// Prevent memory leaks
class MemoryManager {
    constructor() {
        this.cache = new Map();
        this.maxCacheSize = 1000;
        
        // Monitor memory usage
        setInterval(() => {
            const usage = process.memoryUsage();
            console.log('Memory Usage:', {
                rss: `${Math.round(usage.rss / 1024 / 1024)}MB`,
                heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)}MB`,
                heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`,
                external: `${Math.round(usage.external / 1024 / 1024)}MB`
            });
            
            // Force GC if needed
            if (usage.heapUsed > 500 * 1024 * 1024) { // 500MB
                if (global.gc) {
                    global.gc();
                    console.log('Manual GC triggered');
                }
            }
        }, 60000); // Every minute
    }
    
    set(key, value) {
        // Implement LRU cache
        if (this.cache.size >= this.maxCacheSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }
    
    get(key) {
        const value = this.cache.get(key);
        if (value) {
            // Move to end (most recently used)
            this.cache.delete(key);
            this.cache.set(key, value);
        }
        return value;
    }
}
```

#### Async Operations
```javascript
// Optimize async operations
const { promisify } = require('util');
const pipeline = promisify(require('stream').pipeline);

// Batch processing
async function batchProcess(items, batchSize = 10) {
    const results = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        const batchResults = await Promise.all(
            batch.map(item => processItem(item))
        );
        results.push(...batchResults);
        
        // Allow event loop to process other tasks
        await new Promise(resolve => setImmediate(resolve));
    }
    
    return results;
}

// Stream processing for large data
async function processLargeFile(inputFile, outputFile) {
    const readStream = fs.createReadStream(inputFile);
    const writeStream = fs.createWriteStream(outputFile);
    
    const transformStream = new Transform({
        transform(chunk, encoding, callback) {
            // Process chunk
            const processed = processChunk(chunk);
            callback(null, processed);
        }
    });
    
    await pipeline(readStream, transformStream, writeStream);
}
```

### 2. Python Optimization / Python 최적화

#### Concurrent Scraping
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class OptimizedScraper:
    def __init__(self):
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def scrape_all_sites(self, sites):
        """Scrape all sites concurrently"""
        async with aiohttp.ClientSession() as self.session:
            tasks = [self.scrape_site(site) for site in sites]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            return [r for r in results if not isinstance(r, Exception)]
    
    async def scrape_site(self, site):
        """Scrape single site asynchronously"""
        try:
            async with self.session.get(site['url'], timeout=30) as response:
                html = await response.text()
                
                # CPU-intensive parsing in thread pool
                articles = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.parse_html,
                    html,
                    site
                )
                
                return articles
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")
            return []
    
    def parse_html(self, html, site):
        """Parse HTML (CPU-intensive)"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')  # lxml is faster than html.parser
        
        articles = []
        for element in soup.select(site['selectors']['article'])[:10]:
            article = self.extract_article(element, site)
            if article:
                articles.append(article)
        
        return articles

# Multiprocessing for CPU-bound tasks
def parallel_ai_processing(articles, num_processes=None):
    """Process articles with AI in parallel"""
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Chunk articles for balanced distribution
        chunk_size = max(1, len(articles) // num_processes)
        chunks = [articles[i:i + chunk_size] 
                  for i in range(0, len(articles), chunk_size)]
        
        # Process chunks in parallel
        results = pool.map(process_chunk_with_ai, chunks)
        
        # Flatten results
        return [item for sublist in results for item in sublist]
```

#### Memory-Efficient Processing
```python
import gc
from memory_profiler import profile

class MemoryEfficientProcessor:
    def __init__(self):
        self.chunk_size = 100
        
    @profile
    def process_large_dataset(self, filename):
        """Process large file in chunks"""
        processed_count = 0
        
        # Use generator for memory efficiency
        for chunk in self.read_in_chunks(filename):
            processed = self.process_chunk(chunk)
            self.save_results(processed)
            
            processed_count += len(processed)
            
            # Explicit garbage collection
            del chunk
            del processed
            gc.collect()
            
            print(f"Processed {processed_count} items")
    
    def read_in_chunks(self, filename):
        """Generator to read file in chunks"""
        import pandas as pd
        
        for chunk in pd.read_json(filename, lines=True, chunksize=self.chunk_size):
            yield chunk
    
    def process_chunk(self, chunk):
        """Process a single chunk"""
        # Use vectorized operations where possible
        import numpy as np
        
        # Example: Vectorized string operations
        chunk['processed'] = chunk['text'].str.lower().str.strip()
        
        # Use numba for numerical operations
        from numba import jit
        
        @jit(nopython=True)
        def fast_calculation(values):
            result = np.zeros_like(values)
            for i in range(len(values)):
                result[i] = values[i] * 2.5 + 10
            return result
        
        if 'numeric_field' in chunk:
            chunk['calculated'] = fast_calculation(chunk['numeric_field'].values)
        
        return chunk
```

## Database Optimization / 데이터베이스 최적화

### 1. Query Optimization / 쿼리 최적화
```sql
-- Optimize article retrieval
-- Bad: Multiple queries
SELECT * FROM articles WHERE group_id = 1;
SELECT * FROM articles WHERE group_id = 2;
SELECT * FROM articles WHERE group_id = 3;

-- Good: Single query with IN clause
SELECT * FROM articles WHERE group_id IN (1, 2, 3);

-- Better: Use JOIN for related data
SELECT 
    a.id,
    a.title,
    a.summary,
    a.url,
    g.name as group_name,
    s.name as source_name
FROM articles a
INNER JOIN groups g ON a.group_id = g.id
INNER JOIN sources s ON a.source_id = s.id
WHERE a.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY a.created_at DESC
LIMIT 100;

-- Create appropriate indexes
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_group_id ON articles(group_id);
CREATE INDEX idx_articles_source_id ON articles(source_id);
CREATE INDEX idx_articles_composite ON articles(group_id, created_at DESC);
```

### 2. Connection Pooling / 연결 풀링
```javascript
// Database connection pool configuration
const { Pool } = require('pg');

const pool = new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    
    // Pool configuration
    max: 20,                    // Maximum connections
    idleTimeoutMillis: 30000,   // Close idle connections after 30s
    connectionTimeoutMillis: 2000, // Timeout for new connections
    
    // Performance options
    statement_timeout: 30000,    // 30s query timeout
    query_timeout: 30000,
    
    // Connection optimization
    ssl: {
        rejectUnauthorized: false
    }
});

// Health check
pool.on('error', (err, client) => {
    console.error('Unexpected error on idle client', err);
});

// Query with automatic connection management
async function query(text, params) {
    const start = Date.now();
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    
    console.log('Query executed', {
        query: text,
        duration,
        rows: res.rowCount
    });
    
    return res;
}
```

### 3. Data Partitioning / 데이터 분할
```sql
-- Partition articles by date for better performance
CREATE TABLE articles (
    id BIGSERIAL,
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT NOT NULL,
    source_id INTEGER,
    group_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE articles_2025_01 PARTITION OF articles
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE articles_2025_02 PARTITION OF articles
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Automatic partition creation
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    start_date := date_trunc('month', CURRENT_DATE);
    end_date := start_date + interval '1 month';
    partition_name := 'articles_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF articles
        FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly execution
SELECT cron.schedule('create-partitions', '0 0 1 * *', 'SELECT create_monthly_partition()');
```

## Scraping Optimization / 스크래핑 최적화

### 1. Intelligent Request Management / 지능적 요청 관리
```python
import time
from collections import deque
from urllib.robotparser import RobotFileParser

class SmartScraper:
    def __init__(self):
        self.rate_limiters = {}
        self.robot_parsers = {}
        self.session_pool = []
        
    def get_rate_limiter(self, domain):
        """Get or create rate limiter for domain"""
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = RateLimiter(
                requests_per_second=2,  # Conservative default
                burst_size=5
            )
        return self.rate_limiters[domain]
    
    def check_robots_txt(self, url):
        """Check if URL is allowed by robots.txt"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[domain] = rp
            except:
                # If robots.txt is not accessible, allow all
                return True
        
        return self.robot_parsers[domain].can_fetch("*", url)
    
    async def smart_request(self, url, retries=3):
        """Make request with smart retry and backoff"""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc
        rate_limiter = self.get_rate_limiter(domain)
        
        for attempt in range(retries):
            # Check rate limit
            await rate_limiter.acquire()
            
            try:
                # Check robots.txt
                if not self.check_robots_txt(url):
                    raise ValueError(f"URL blocked by robots.txt: {url}")
                
                # Make request
                async with self.get_session().get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                    elif response.status >= 500:  # Server error
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise ValueError(f"HTTP {response.status}")
                        
            except asyncio.TimeoutError:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        
        raise ValueError(f"Failed after {retries} attempts")

class RateLimiter:
    def __init__(self, requests_per_second=1, burst_size=1):
        self.rate = requests_per_second
        self.burst = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)
                self.tokens = 1
            
            self.tokens -= 1
```

### 2. Content Extraction Optimization / 콘텐츠 추출 최적화
```python
from lxml import etree
from selectolax.parser import HTMLParser
import re

class FastExtractor:
    def __init__(self):
        # Compile regex patterns once
        self.date_patterns = [
            re.compile(r'(\d{4}-\d{2}-\d{2})'),
            re.compile(r'(\d{1,2}\s+\w+\s+\d{4})'),
            re.compile(r'(\w+\s+\d{1,2},\s+\d{4})')
        ]
        
        # Precompile XPath expressions
        self.xpath_cache = {}
    
    def extract_with_lxml(self, html, selectors):
        """Fast extraction using lxml"""
        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)
        
        results = []
        for selector in selectors:
            # Cache compiled XPath
            if selector not in self.xpath_cache:
                self.xpath_cache[selector] = etree.XPath(selector)
            
            elements = self.xpath_cache[selector](tree)
            results.extend(elements)
        
        return results
    
    def extract_with_selectolax(self, html, css_selectors):
        """Ultra-fast extraction using selectolax"""
        tree = HTMLParser(html)
        
        results = []
        for selector in css_selectors:
            for node in tree.css(selector):
                results.append({
                    'text': node.text(strip=True),
                    'html': node.html,
                    'attrs': node.attributes
                })
        
        return results
    
    def extract_dates_fast(self, text):
        """Fast date extraction using precompiled patterns"""
        for pattern in self.date_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return None

# Benchmark different parsers
def benchmark_parsers(html):
    import timeit
    
    # BeautifulSoup
    bs_time = timeit.timeit(
        lambda: BeautifulSoup(html, 'html.parser').find_all('article'),
        number=100
    )
    
    # lxml
    lxml_time = timeit.timeit(
        lambda: etree.HTML(html).xpath('//article'),
        number=100
    )
    
    # selectolax
    selectolax_time = timeit.timeit(
        lambda: HTMLParser(html).css('article'),
        number=100
    )
    
    print(f"BeautifulSoup: {bs_time:.3f}s")
    print(f"lxml: {lxml_time:.3f}s")
    print(f"selectolax: {selectolax_time:.3f}s")
```

## API Optimization / API 최적화

### 1. Response Compression / 응답 압축
```javascript
// Enable compression for API responses
const compression = require('compression');

app.use(compression({
    // Enable compression for responses > 1KB
    threshold: 1024,
    
    // Compression level (0-9)
    level: 6,
    
    // Custom filter function
    filter: (req, res) => {
        // Don't compress if client doesn't support
        if (req.headers['x-no-compression']) {
            return false;
        }
        
        // Use compression for JSON and text
        return compression.filter(req, res);
    }
}));

// Content negotiation for response format
app.get('/api/articles', (req, res) => {
    const articles = getArticles();
    
    // Check Accept header
    const acceptHeader = req.get('Accept');
    
    if (acceptHeader.includes('application/msgpack')) {
        // MessagePack is more efficient than JSON
        const msgpack = require('msgpack');
        res.type('application/msgpack');
        res.send(msgpack.pack(articles));
    } else if (acceptHeader.includes('application/protobuf')) {
        // Protocol Buffers for typed data
        const protobuf = require('protobufjs');
        const ArticleList = protobuf.loadSync('articles.proto').lookupType('ArticleList');
        const message = ArticleList.create({ articles });
        res.type('application/protobuf');
        res.send(ArticleList.encode(message).finish());
    } else {
        // Default to JSON
        res.json(articles);
    }
});
```

### 2. GraphQL Optimization / GraphQL 최적화
```javascript
// Implement DataLoader for N+1 query prevention
const DataLoader = require('dataloader');

const createLoaders = () => ({
    articleLoader: new DataLoader(async (ids) => {
        const articles = await db.query(
            'SELECT * FROM articles WHERE id = ANY($1)',
            [ids]
        );
        
        // Map results to match input order
        const articleMap = {};
        articles.rows.forEach(article => {
            articleMap[article.id] = article;
        });
        
        return ids.map(id => articleMap[id]);
    }),
    
    authorLoader: new DataLoader(async (articleIds) => {
        const authors = await db.query(
            'SELECT * FROM authors WHERE article_id = ANY($1)',
            [articleIds]
        );
        
        // Group by article ID
        const authorMap = {};
        authors.rows.forEach(author => {
            if (!authorMap[author.article_id]) {
                authorMap[author.article_id] = [];
            }
            authorMap[author.article_id].push(author);
        });
        
        return articleIds.map(id => authorMap[id] || []);
    })
});

// GraphQL resolver with DataLoader
const resolvers = {
    Query: {
        articles: async (parent, args, context) => {
            const { limit = 10, offset = 0 } = args;
            const result = await context.db.query(
                'SELECT id FROM articles ORDER BY created_at DESC LIMIT $1 OFFSET $2',
                [limit, offset]
            );
            
            // Use DataLoader to batch fetch
            return Promise.all(
                result.rows.map(row => context.loaders.articleLoader.load(row.id))
            );
        }
    },
    
    Article: {
        authors: (article, args, context) => {
            // DataLoader handles batching and caching
            return context.loaders.authorLoader.load(article.id);
        }
    }
};
```

### 3. API Gateway Optimization / API 게이트웨이 최적화
```javascript
// Rate limiting with sliding window
const slidingWindowRateLimiter = {
    windows: new Map(),
    
    async checkLimit(key, limit, windowMs) {
        const now = Date.now();
        const windowStart = now - windowMs;
        
        // Get or create window
        let window = this.windows.get(key);
        if (!window) {
            window = [];
            this.windows.set(key, window);
        }
        
        // Remove old entries
        window = window.filter(timestamp => timestamp > windowStart);
        
        // Check limit
        if (window.length >= limit) {
            const oldestRequest = Math.min(...window);
            const resetTime = oldestRequest + windowMs;
            
            return {
                allowed: false,
                remaining: 0,
                reset: resetTime
            };
        }
        
        // Add current request
        window.push(now);
        this.windows.set(key, window);
        
        return {
            allowed: true,
            remaining: limit - window.length,
            reset: now + windowMs
        };
    }
};

// Request coalescing for identical requests
const requestCoalescer = {
    pending: new Map(),
    
    async coalesce(key, requestFn) {
        // Check if identical request is pending
        if (this.pending.has(key)) {
            return this.pending.get(key);
        }
        
        // Create new request
        const promise = requestFn()
            .finally(() => {
                // Clean up after completion
                this.pending.delete(key);
            });
        
        this.pending.set(key, promise);
        return promise;
    }
};

// Usage
app.get('/api/expensive-operation/:id', async (req, res) => {
    const { id } = req.params;
    const key = `expensive-${id}`;
    
    try {
        const result = await requestCoalescer.coalesce(key, async () => {
            // Expensive operation
            return await performExpensiveOperation(id);
        });
        
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

## Caching Strategies / 캐싱 전략

### 1. Multi-Level Caching / 다단계 캐싱
```javascript
class MultiLevelCache {
    constructor() {
        // L1: In-memory cache (fastest, smallest)
        this.l1Cache = new LRUCache({
            max: 100,
            ttl: 1000 * 60 * 5 // 5 minutes
        });
        
        // L2: Redis cache (fast, medium)
        this.l2Cache = redis.createClient({
            host: process.env.REDIS_HOST
        });
        
        // L3: CDN cache (slower, largest)
        this.cdnHeaders = {
            'Cache-Control': 'public, max-age=3600',
            'Surrogate-Control': 'max-age=86400'
        };
    }
    
    async get(key) {
        // Check L1
        let value = this.l1Cache.get(key);
        if (value) {
            console.log('L1 cache hit');
            return value;
        }
        
        // Check L2
        value = await this.l2Cache.get(key);
        if (value) {
            console.log('L2 cache hit');
            // Promote to L1
            this.l1Cache.set(key, value);
            return JSON.parse(value);
        }
        
        // Cache miss
        console.log('Cache miss');
        return null;
    }
    
    async set(key, value, ttl = 3600) {
        // Set in all levels
        this.l1Cache.set(key, value);
        await this.l2Cache.setex(key, ttl, JSON.stringify(value));
        
        // Return CDN headers for HTTP response
        return {
            'Cache-Control': `public, max-age=${ttl}`,
            'ETag': this.generateETag(value)
        };
    }
    
    generateETag(value) {
        const crypto = require('crypto');
        return crypto
            .createHash('md5')
            .update(JSON.stringify(value))
            .digest('hex');
    }
}

// Cache warming strategy
class CacheWarmer {
    constructor(cache) {
        this.cache = cache;
        this.warmupInterval = 1000 * 60 * 30; // 30 minutes
    }
    
    async warmCache() {
        console.log('Starting cache warmup...');
        
        const criticalQueries = [
            { key: 'articles:latest', fn: () => getLatestArticles() },
            { key: 'articles:popular', fn: () => getPopularArticles() },
            { key: 'stats:dashboard', fn: () => getDashboardStats() }
        ];
        
        for (const query of criticalQueries) {
            try {
                const data = await query.fn();
                await this.cache.set(query.key, data);
                console.log(`Warmed cache for ${query.key}`);
            } catch (error) {
                console.error(`Failed to warm ${query.key}:`, error);
            }
        }
    }
    
    start() {
        // Initial warmup
        this.warmCache();
        
        // Schedule periodic warmup
        setInterval(() => this.warmCache(), this.warmupInterval);
    }
}
```

### 2. Smart Cache Invalidation / 스마트 캐시 무효화
```javascript
class SmartCacheInvalidator {
    constructor(cache) {
        this.cache = cache;
        this.dependencies = new Map();
    }
    
    // Track cache dependencies
    addDependency(cacheKey, dependencyKey) {
        if (!this.dependencies.has(dependencyKey)) {
            this.dependencies.set(dependencyKey, new Set());
        }
        this.dependencies.get(dependencyKey).add(cacheKey);
    }
    
    // Invalidate related caches
    async invalidate(dependencyKey) {
        const affected = this.dependencies.get(dependencyKey);
        if (!affected) return;
        
        const invalidationPromises = [];
        
        for (const cacheKey of affected) {
            invalidationPromises.push(this.cache.delete(cacheKey));
            console.log(`Invalidating cache: ${cacheKey}`);
        }
        
        await Promise.all(invalidationPromises);
        
        // Clean up dependencies
        this.dependencies.delete(dependencyKey);
    }
    
    // Tag-based invalidation
    async invalidateByTags(tags) {
        const keysToInvalidate = new Set();
        
        for (const [key, keyTags] of this.cache.entries()) {
            if (tags.some(tag => keyTags.includes(tag))) {
                keysToInvalidate.add(key);
            }
        }
        
        for (const key of keysToInvalidate) {
            await this.cache.delete(key);
        }
        
        console.log(`Invalidated ${keysToInvalidate.size} cache entries`);
    }
}

// Usage example
const cacheInvalidator = new SmartCacheInvalidator(cache);

// When caching articles
app.get('/api/articles/:id', async (req, res) => {
    const { id } = req.params;
    const cacheKey = `article:${id}`;
    
    let article = await cache.get(cacheKey);
    
    if (!article) {
        article = await db.getArticle(id);
        await cache.set(cacheKey, article);
        
        // Track dependencies
        cacheInvalidator.addDependency(cacheKey, `source:${article.sourceId}`);
        cacheInvalidator.addDependency(cacheKey, `group:${article.groupId}`);
    }
    
    res.json(article);
});

// When updating source
app.put('/api/sources/:id', async (req, res) => {
    const { id } = req.params;
    
    await db.updateSource(id, req.body);
    
    // Invalidate all articles from this source
    await cacheInvalidator.invalidate(`source:${id}`);
    
    res.json({ success: true });
});
```

## Load Testing / 부하 테스트

### 1. Load Testing Scripts / 부하 테스트 스크립트
```javascript
// k6 load testing script
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 100 },   // Ramp up to 100 users
        { duration: '5m', target: 100 },   // Stay at 100 users
        { duration: '2m', target: 500 },   // Ramp up to 500 users
        { duration: '5m', target: 500 },   // Stay at 500 users
        { duration: '2m', target: 1000 },  // Ramp up to 1000 users
        { duration: '5m', target: 1000 },  // Stay at 1000 users
        { duration: '5m', target: 0 },     // Ramp down to 0 users
    ],
    thresholds: {
        http_req_duration: ['p(95)<1000'], // 95% of requests under 1s
        errors: ['rate<0.1'],              // Error rate under 10%
    },
};

const BASE_URL = 'https://singapore-news-github.vercel.app';

export default function () {
    // Simulate user journey
    const responses = {};
    
    // 1. Load homepage
    responses.home = http.get(`${BASE_URL}/`);
    check(responses.home, {
        'homepage loaded': (r) => r.status === 200,
    });
    errorRate.add(responses.home.status !== 200);
    
    sleep(1);
    
    // 2. Login
    responses.login = http.post(`${BASE_URL}/api/auth`, JSON.stringify({
        username: 'testuser',
        password: 'testpass'
    }), {
        headers: { 'Content-Type': 'application/json' },
    });
    check(responses.login, {
        'login successful': (r) => r.status === 200,
    });
    
    sleep(1);
    
    // 3. Get articles
    responses.articles = http.get(`${BASE_URL}/api/get-latest-scraped`);
    check(responses.articles, {
        'articles loaded': (r) => r.status === 200,
        'articles returned': (r) => JSON.parse(r.body).data.articles.length > 0,
    });
    
    sleep(Math.random() * 3 + 1); // Random think time
}

// Custom metrics collection
export function handleSummary(data) {
    return {
        'summary.json': JSON.stringify(data),
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
    };
}
```

### 2. Stress Testing / 스트레스 테스트
```python
# Locust stress testing
from locust import HttpUser, task, between
import random

class NewsScraperUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before running tasks"""
        response = self.client.post("/api/auth", json={
            "username": "testuser",
            "password": "testpass"
        })
        
        if response.status_code == 200:
            self.token = response.json()["data"]["sessionId"]
        else:
            print(f"Login failed: {response.status_code}")
    
    @task(3)
    def view_articles(self):
        """Most common operation"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Random parameters
        params = {
            "limit": random.choice([10, 20, 50]),
            "group": random.choice(["politics", "economy", "tech", None])
        }
        
        if params["group"] is None:
            del params["group"]
        
        with self.client.get("/api/get-latest-scraped", 
                            params=params,
                            headers=headers,
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    response.success()
                else:
                    response.failure(f"API error: {data.get('error')}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def trigger_scraping(self):
        """Less common but resource-intensive"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.post("/api/trigger-scraping",
                             json={"method": "traditional"},
                             headers=headers,
                             catch_response=True) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def check_status(self):
        """Moderate frequency operation"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        self.client.get("/api/get-scraping-status", headers=headers)

# Run with: locust -f locustfile.py --host=https://singapore-news-github.vercel.app
```

## Monitoring & Profiling / 모니터링 및 프로파일링

### 1. Application Performance Monitoring / 애플리케이션 성능 모니터링
```javascript
// Custom APM implementation
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.intervals = new Map();
    }
    
    startTransaction(name) {
        const transaction = {
            name,
            startTime: process.hrtime.bigint(),
            spans: []
        };
        
        return {
            addSpan(spanName) {
                const span = {
                    name: spanName,
                    startTime: process.hrtime.bigint()
                };
                
                return {
                    end() {
                        span.endTime = process.hrtime.bigint();
                        span.duration = Number(span.endTime - span.startTime) / 1e6; // Convert to ms
                        transaction.spans.push(span);
                    }
                };
            },
            
            end() {
                transaction.endTime = process.hrtime.bigint();
                transaction.duration = Number(transaction.endTime - transaction.startTime) / 1e6;
                
                // Store metrics
                if (!this.metrics.has(name)) {
                    this.metrics.set(name, []);
                }
                this.metrics.get(name).push(transaction);
                
                // Log slow transactions
                if (transaction.duration > 1000) {
                    console.warn(`Slow transaction: ${name} took ${transaction.duration}ms`);
                    console.warn('Spans:', transaction.spans);
                }
            }.bind(this)
        };
    }
    
    getStats(transactionName) {
        const transactions = this.metrics.get(transactionName) || [];
        if (transactions.length === 0) return null;
        
        const durations = transactions.map(t => t.duration);
        durations.sort((a, b) => a - b);
        
        return {
            count: durations.length,
            min: durations[0],
            max: durations[durations.length - 1],
            avg: durations.reduce((a, b) => a + b) / durations.length,
            p50: durations[Math.floor(durations.length * 0.5)],
            p95: durations[Math.floor(durations.length * 0.95)],
            p99: durations[Math.floor(durations.length * 0.99)]
        };
    }
}

// Usage
const monitor = new PerformanceMonitor();

app.get('/api/articles', async (req, res) => {
    const transaction = monitor.startTransaction('GET /api/articles');
    
    try {
        // Database query
        const dbSpan = transaction.addSpan('database.query');
        const articles = await db.getArticles();
        dbSpan.end();
        
        // Processing
        const processSpan = transaction.addSpan('processing');
        const processed = await processArticles(articles);
        processSpan.end();
        
        // Serialization
        const serializeSpan = transaction.addSpan('serialization');
        const json = JSON.stringify(processed);
        serializeSpan.end();
        
        res.json(processed);
    } finally {
        transaction.end();
    }
});
```

### 2. Real-time Monitoring Dashboard / 실시간 모니터링 대시보드
```javascript
// WebSocket-based real-time monitoring
const WebSocket = require('ws');

class MonitoringDashboard {
    constructor(server) {
        this.wss = new WebSocket.Server({ server });
        this.clients = new Set();
        this.metrics = {
            requests: new Map(),
            errors: new Map(),
            performance: new Map()
        };
        
        this.setupWebSocket();
        this.startMetricsCollection();
    }
    
    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            this.clients.add(ws);
            
            // Send initial data
            ws.send(JSON.stringify({
                type: 'init',
                data: this.getMetricsSummary()
            }));
            
            ws.on('close', () => {
                this.clients.delete(ws);
            });
        });
    }
    
    startMetricsCollection() {
        // Collect metrics every second
        setInterval(() => {
            const summary = this.getMetricsSummary();
            this.broadcast({
                type: 'update',
                data: summary
            });
        }, 1000);
        
        // Clean old metrics every minute
        setInterval(() => {
            this.cleanOldMetrics();
        }, 60000);
    }
    
    recordRequest(endpoint, duration, status) {
        const now = Date.now();
        
        // Record in time bucket
        const bucket = Math.floor(now / 1000) * 1000;
        
        if (!this.metrics.requests.has(bucket)) {
            this.metrics.requests.set(bucket, {
                count: 0,
                duration: 0,
                endpoints: new Map()
            });
        }
        
        const bucketData = this.metrics.requests.get(bucket);
        bucketData.count++;
        bucketData.duration += duration;
        
        if (!bucketData.endpoints.has(endpoint)) {
            bucketData.endpoints.set(endpoint, { count: 0, duration: 0 });
        }
        
        const endpointData = bucketData.endpoints.get(endpoint);
        endpointData.count++;
        endpointData.duration += duration;
        
        // Record errors
        if (status >= 400) {
            if (!this.metrics.errors.has(bucket)) {
                this.metrics.errors.set(bucket, 0);
            }
            this.metrics.errors.set(bucket, this.metrics.errors.get(bucket) + 1);
        }
    }
    
    getMetricsSummary() {
        const now = Date.now();
        const oneMinuteAgo = now - 60000;
        
        let totalRequests = 0;
        let totalDuration = 0;
        let totalErrors = 0;
        const endpointStats = new Map();
        
        // Aggregate last minute
        for (const [bucket, data] of this.metrics.requests) {
            if (bucket >= oneMinuteAgo) {
                totalRequests += data.count;
                totalDuration += data.duration;
                
                for (const [endpoint, stats] of data.endpoints) {
                    if (!endpointStats.has(endpoint)) {
                        endpointStats.set(endpoint, { count: 0, duration: 0 });
                    }
                    const eps = endpointStats.get(endpoint);
                    eps.count += stats.count;
                    eps.duration += stats.duration;
                }
            }
        }
        
        for (const [bucket, count] of this.metrics.errors) {
            if (bucket >= oneMinuteAgo) {
                totalErrors += count;
            }
        }
        
        return {
            timestamp: now,
            requests: {
                total: totalRequests,
                perSecond: totalRequests / 60,
                avgDuration: totalRequests > 0 ? totalDuration / totalRequests : 0
            },
            errors: {
                total: totalErrors,
                rate: totalRequests > 0 ? totalErrors / totalRequests : 0
            },
            endpoints: Array.from(endpointStats.entries()).map(([endpoint, stats]) => ({
                endpoint,
                count: stats.count,
                avgDuration: stats.count > 0 ? stats.duration / stats.count : 0
            })).sort((a, b) => b.count - a.count).slice(0, 10)
        };
    }
    
    broadcast(message) {
        const data = JSON.stringify(message);
        for (const client of this.clients) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(data);
            }
        }
    }
    
    cleanOldMetrics() {
        const fiveMinutesAgo = Date.now() - 300000;
        
        for (const [bucket] of this.metrics.requests) {
            if (bucket < fiveMinutesAgo) {
                this.metrics.requests.delete(bucket);
            }
        }
        
        for (const [bucket] of this.metrics.errors) {
            if (bucket < fiveMinutesAgo) {
                this.metrics.errors.delete(bucket);
            }
        }
    }
}
```

---
*Performance optimization is an ongoing process. Monitor, measure, and iterate.*

*성능 최적화는 지속적인 프로세스입니다. 모니터링하고, 측정하고, 반복하세요.*

*Last Updated: January 25, 2025*