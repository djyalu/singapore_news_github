// Rate Limiter for API Calls
// Chaos Engineering: API 호출 제한 관리

class RateLimiter {
    constructor(maxRequests = 10, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = [];
    }

    // 요청 가능 여부 확인
    canMakeRequest() {
        const now = Date.now();
        // 오래된 요청 제거
        this.requests = this.requests.filter(time => now - time < this.windowMs);
        
        if (this.requests.length >= this.maxRequests) {
            const oldestRequest = this.requests[0];
            const waitTime = this.windowMs - (now - oldestRequest);
            console.warn(`Rate limit reached. Wait ${Math.ceil(waitTime / 1000)}s`);
            return { allowed: false, waitTime };
        }
        
        return { allowed: true };
    }

    // 요청 기록
    recordRequest() {
        this.requests.push(Date.now());
    }

    // 대기 후 요청
    async waitAndRequest(requestFn) {
        const check = this.canMakeRequest();
        
        if (!check.allowed) {
            console.log(`Rate limited. Waiting ${check.waitTime}ms...`);
            await new Promise(resolve => setTimeout(resolve, check.waitTime));
        }
        
        this.recordRequest();
        return await requestFn();
    }

    // 현재 상태
    getStatus() {
        const now = Date.now();
        this.requests = this.requests.filter(time => now - time < this.windowMs);
        
        return {
            current: this.requests.length,
            max: this.maxRequests,
            remaining: this.maxRequests - this.requests.length,
            resetIn: this.requests.length > 0 ? 
                this.windowMs - (now - this.requests[0]) : 0
        };
    }
}

// API별 rate limiter 인스턴스
const rateLimiters = {
    github: new RateLimiter(30, 60000), // GitHub API: 30 requests per minute
    vercel: new RateLimiter(100, 60000), // Vercel API: 100 requests per minute
    whatsapp: new RateLimiter(20, 60000) // WhatsApp API: 20 messages per minute
};

// Rate limited fetch wrapper
async function rateLimitedFetch(url, options = {}) {
    let limiter;
    
    if (url.includes('api.github.com')) {
        limiter = rateLimiters.github;
    } else if (url.includes('vercel.app')) {
        limiter = rateLimiters.vercel;
    } else if (url.includes('whatsapp')) {
        limiter = rateLimiters.whatsapp;
    } else {
        // 기본 fetch 사용
        return fetch(url, options);
    }
    
    return await limiter.waitAndRequest(() => fetch(url, options));
}

// Circuit Breaker Pattern
class CircuitBreaker {
    constructor(threshold = 5, timeout = 60000) {
        this.failureCount = 0;
        this.threshold = threshold;
        this.timeout = timeout;
        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
        this.nextRetry = null;
    }

    async execute(requestFn) {
        if (this.state === 'OPEN') {
            if (Date.now() < this.nextRetry) {
                throw new Error('Circuit breaker is OPEN');
            }
            this.state = 'HALF_OPEN';
        }

        try {
            const result = await requestFn();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }

    onSuccess() {
        this.failureCount = 0;
        this.state = 'CLOSED';
    }

    onFailure() {
        this.failureCount++;
        if (this.failureCount >= this.threshold) {
            this.state = 'OPEN';
            this.nextRetry = Date.now() + this.timeout;
            console.error(`Circuit breaker opened. Retry after ${new Date(this.nextRetry)}`);
        }
    }

    getStatus() {
        return {
            state: this.state,
            failures: this.failureCount,
            nextRetry: this.nextRetry ? new Date(this.nextRetry) : null
        };
    }
}

// API별 circuit breaker
const circuitBreakers = {
    scraping: new CircuitBreaker(3, 30000), // 3 failures, 30s timeout
    whatsapp: new CircuitBreaker(5, 60000)  // 5 failures, 60s timeout
};

// Export
window.rateLimiter = {
    rateLimiters,
    circuitBreakers,
    rateLimitedFetch,
    getRateLimiterStatus: () => {
        const status = {};
        for (const [name, limiter] of Object.entries(rateLimiters)) {
            status[name] = limiter.getStatus();
        }
        return status;
    },
    getCircuitBreakerStatus: () => {
        const status = {};
        for (const [name, breaker] of Object.entries(circuitBreakers)) {
            status[name] = breaker.getStatus();
        }
        return status;
    }
};