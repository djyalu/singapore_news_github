# Security Guide / 보안 가이드

## Table of Contents / 목차
1. [Security Overview / 보안 개요](#security-overview--보안-개요)
2. [Security Policies / 보안 정책](#security-policies--보안-정책)
3. [Authentication Security / 인증 보안](#authentication-security--인증-보안)
4. [API Security / API 보안](#api-security--api-보안)
5. [Data Security / 데이터 보안](#data-security--데이터-보안)
6. [Infrastructure Security / 인프라 보안](#infrastructure-security--인프라-보안)
7. [Security Best Practices / 보안 모범 사례](#security-best-practices--보안-모범-사례)
8. [Vulnerability Management / 취약점 관리](#vulnerability-management--취약점-관리)
9. [Incident Response / 보안 사고 대응](#incident-response--보안-사고-대응)
10. [Security Checklist / 보안 체크리스트](#security-checklist--보안-체크리스트)

## Security Overview / 보안 개요

Singapore News Scraper implements multiple layers of security to protect user data, prevent unauthorized access, and ensure system integrity. This guide outlines our security measures and best practices.

싱가포르 뉴스 스크래퍼는 사용자 데이터 보호, 무단 액세스 방지, 시스템 무결성 보장을 위해 다층 보안을 구현합니다. 이 가이드는 보안 조치와 모범 사례를 설명합니다.

### Security Principles / 보안 원칙
- **Defense in Depth**: Multiple security layers / 심층 방어: 다중 보안 계층
- **Least Privilege**: Minimal access rights / 최소 권한: 최소한의 접근 권한
- **Zero Trust**: Verify everything / 제로 트러스트: 모든 것을 검증
- **Security by Design**: Built-in security / 설계상 보안: 내장된 보안

## Security Policies / 보안 정책

### 1. Access Control Policy / 접근 제어 정책
```yaml
Roles and Permissions:
  Admin:
    - Full system access
    - Configuration management
    - User management
    - Data export/import
  
  User:
    - Read-only access
    - Personal settings
    - View articles
  
  API:
    - Specific endpoint access
    - Rate limited
    - Token-based auth
```

### 2. Data Classification / 데이터 분류
```yaml
Public:
  - Scraped news articles
  - Public configuration
  - Documentation

Internal:
  - System logs
  - Performance metrics
  - Error reports

Confidential:
  - API keys
  - User credentials
  - Session tokens

Restricted:
  - Database backups
  - Security logs
  - Encryption keys
```

### 3. Password Policy / 비밀번호 정책
```javascript
const passwordPolicy = {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
    prohibitCommonPasswords: true,
    prohibitUserInfo: true,
    expirationDays: 90,
    historyCount: 5
};

function validatePassword(password, username) {
    // Length check
    if (password.length < passwordPolicy.minLength) {
        return { valid: false, error: 'Password too short' };
    }
    
    // Complexity checks
    if (passwordPolicy.requireUppercase && !/[A-Z]/.test(password)) {
        return { valid: false, error: 'Must contain uppercase letter' };
    }
    
    if (passwordPolicy.requireLowercase && !/[a-z]/.test(password)) {
        return { valid: false, error: 'Must contain lowercase letter' };
    }
    
    if (passwordPolicy.requireNumbers && !/\d/.test(password)) {
        return { valid: false, error: 'Must contain number' };
    }
    
    if (passwordPolicy.requireSpecialChars && !/[!@#$%^&*]/.test(password)) {
        return { valid: false, error: 'Must contain special character' };
    }
    
    // Common password check
    if (commonPasswords.includes(password.toLowerCase())) {
        return { valid: false, error: 'Password too common' };
    }
    
    // Username similarity check
    if (password.toLowerCase().includes(username.toLowerCase())) {
        return { valid: false, error: 'Password contains username' };
    }
    
    return { valid: true };
}
```

## Authentication Security / 인증 보안

### 1. Session Management / 세션 관리
```javascript
// Secure session configuration
const sessionConfig = {
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true,          // HTTPS only
        httpOnly: true,        // No JavaScript access
        maxAge: 3600000,       // 1 hour
        sameSite: 'strict'     // CSRF protection
    }
};

// Session validation
function validateSession(sessionId) {
    const session = sessions.get(sessionId);
    
    if (!session) {
        return { valid: false, reason: 'Session not found' };
    }
    
    if (Date.now() > session.expiresAt) {
        sessions.delete(sessionId);
        return { valid: false, reason: 'Session expired' };
    }
    
    if (session.ipAddress !== request.ipAddress) {
        return { valid: false, reason: 'IP mismatch' };
    }
    
    // Refresh session
    session.lastActivity = Date.now();
    return { valid: true, session };
}
```

### 2. Multi-Factor Authentication / 다중 인증
```javascript
// TOTP implementation
const speakeasy = require('speakeasy');

function setupMFA(userId) {
    const secret = speakeasy.generateSecret({
        name: 'Singapore News Scraper',
        issuer: 'SG News',
        length: 32
    });
    
    // Save secret for user
    saveUserSecret(userId, secret.base32);
    
    return {
        secret: secret.base32,
        qrCode: secret.otpauth_url
    };
}

function verifyMFA(userId, token) {
    const secret = getUserSecret(userId);
    
    return speakeasy.totp.verify({
        secret: secret,
        encoding: 'base32',
        token: token,
        window: 2  // Allow 2 time steps for clock drift
    });
}
```

### 3. Brute Force Protection / 무차별 공격 방어
```javascript
const loginAttempts = new Map();
const LOCKOUT_THRESHOLD = 5;
const LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minutes

function checkBruteForce(identifier) {
    const key = `login_${identifier}`;
    const attempts = loginAttempts.get(key) || {
        count: 0,
        firstAttempt: Date.now(),
        lockedUntil: 0
    };
    
    // Check if currently locked
    if (attempts.lockedUntil > Date.now()) {
        const remainingTime = Math.ceil((attempts.lockedUntil - Date.now()) / 1000);
        throw new Error(`Account locked. Try again in ${remainingTime} seconds`);
    }
    
    // Reset if window expired
    if (Date.now() - attempts.firstAttempt > LOCKOUT_DURATION) {
        attempts.count = 0;
        attempts.firstAttempt = Date.now();
    }
    
    return attempts;
}

function recordFailedAttempt(identifier) {
    const attempts = checkBruteForce(identifier);
    attempts.count++;
    
    if (attempts.count >= LOCKOUT_THRESHOLD) {
        attempts.lockedUntil = Date.now() + LOCKOUT_DURATION;
        
        // Log security event
        logSecurityEvent({
            type: 'ACCOUNT_LOCKED',
            identifier,
            attempts: attempts.count,
            timestamp: new Date()
        });
    }
    
    loginAttempts.set(`login_${identifier}`, attempts);
}
```

## API Security / API 보안

### 1. API Key Management / API 키 관리
```javascript
// API key generation
const crypto = require('crypto');

function generateAPIKey() {
    const key = crypto.randomBytes(32).toString('hex');
    const hash = crypto.createHash('sha256').update(key).digest('hex');
    
    return {
        key: `sgn_${key}`,  // Prefixed for identification
        hash: hash          // Store hash, not plaintext
    };
}

// API key validation
function validateAPIKey(apiKey) {
    if (!apiKey || !apiKey.startsWith('sgn_')) {
        return { valid: false, error: 'Invalid API key format' };
    }
    
    const keyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
    const storedKey = getStoredAPIKey(keyHash);
    
    if (!storedKey) {
        return { valid: false, error: 'API key not found' };
    }
    
    if (storedKey.revoked) {
        return { valid: false, error: 'API key revoked' };
    }
    
    if (storedKey.expiresAt && Date.now() > storedKey.expiresAt) {
        return { valid: false, error: 'API key expired' };
    }
    
    // Update last used
    updateAPIKeyUsage(keyHash);
    
    return { valid: true, key: storedKey };
}
```

### 2. Rate Limiting / 속도 제한
```javascript
// Advanced rate limiting with sliding window
class RateLimiter {
    constructor(options = {}) {
        this.windowMs = options.windowMs || 60000; // 1 minute
        this.maxRequests = options.maxRequests || 60;
        this.keyGenerator = options.keyGenerator || (req => req.ip);
        this.storage = new Map();
    }
    
    async limit(req) {
        const key = this.keyGenerator(req);
        const now = Date.now();
        const windowStart = now - this.windowMs;
        
        // Get or create request log
        let requests = this.storage.get(key) || [];
        
        // Remove old requests
        requests = requests.filter(timestamp => timestamp > windowStart);
        
        // Check limit
        if (requests.length >= this.maxRequests) {
            const oldestRequest = Math.min(...requests);
            const resetTime = oldestRequest + this.windowMs;
            
            throw {
                status: 429,
                message: 'Rate limit exceeded',
                retryAfter: Math.ceil((resetTime - now) / 1000),
                limit: this.maxRequests,
                remaining: 0,
                reset: new Date(resetTime)
            };
        }
        
        // Add current request
        requests.push(now);
        this.storage.set(key, requests);
        
        return {
            limit: this.maxRequests,
            remaining: this.maxRequests - requests.length,
            reset: new Date(now + this.windowMs)
        };
    }
}

// Usage
const apiLimiter = new RateLimiter({
    windowMs: 60000,
    maxRequests: 60,
    keyGenerator: (req) => req.headers['x-api-key'] || req.ip
});
```

### 3. Input Validation / 입력 검증
```javascript
// Comprehensive input validation
const validator = require('validator');

class InputValidator {
    static validateEmail(email) {
        if (!email || !validator.isEmail(email)) {
            throw new ValidationError('Invalid email format');
        }
        
        // Additional checks
        const domain = email.split('@')[1];
        if (blockedDomains.includes(domain)) {
            throw new ValidationError('Email domain not allowed');
        }
        
        return validator.normalizeEmail(email);
    }
    
    static validateURL(url) {
        if (!url || !validator.isURL(url, { 
            protocols: ['http', 'https'],
            require_protocol: true 
        })) {
            throw new ValidationError('Invalid URL format');
        }
        
        // Check for malicious patterns
        const maliciousPatterns = [
            /javascript:/i,
            /data:text\/html/i,
            /vbscript:/i
        ];
        
        for (const pattern of maliciousPatterns) {
            if (pattern.test(url)) {
                throw new ValidationError('Malicious URL detected');
            }
        }
        
        return url;
    }
    
    static sanitizeHTML(html) {
        const DOMPurify = require('isomorphic-dompurify');
        
        return DOMPurify.sanitize(html, {
            ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
            ALLOWED_ATTR: ['href', 'title'],
            ALLOW_DATA_ATTR: false
        });
    }
    
    static validateJSON(jsonString) {
        try {
            const parsed = JSON.parse(jsonString);
            
            // Prevent prototype pollution
            if ('__proto__' in parsed || 'constructor' in parsed || 'prototype' in parsed) {
                throw new ValidationError('Potentially malicious JSON');
            }
            
            return parsed;
        } catch (error) {
            throw new ValidationError('Invalid JSON format');
        }
    }
}
```

## Data Security / 데이터 보안

### 1. Encryption at Rest / 저장 데이터 암호화
```javascript
const crypto = require('crypto');

class DataEncryption {
    constructor(masterKey) {
        this.algorithm = 'aes-256-gcm';
        this.masterKey = Buffer.from(masterKey, 'hex');
    }
    
    encrypt(data) {
        // Generate random IV
        const iv = crypto.randomBytes(16);
        
        // Create cipher
        const cipher = crypto.createCipheriv(this.algorithm, this.masterKey, iv);
        
        // Encrypt data
        const encrypted = Buffer.concat([
            cipher.update(JSON.stringify(data), 'utf8'),
            cipher.final()
        ]);
        
        // Get auth tag
        const authTag = cipher.getAuthTag();
        
        // Combine IV + authTag + encrypted data
        return Buffer.concat([iv, authTag, encrypted]).toString('base64');
    }
    
    decrypt(encryptedData) {
        const buffer = Buffer.from(encryptedData, 'base64');
        
        // Extract components
        const iv = buffer.slice(0, 16);
        const authTag = buffer.slice(16, 32);
        const encrypted = buffer.slice(32);
        
        // Create decipher
        const decipher = crypto.createDecipheriv(this.algorithm, this.masterKey, iv);
        decipher.setAuthTag(authTag);
        
        // Decrypt
        const decrypted = Buffer.concat([
            decipher.update(encrypted),
            decipher.final()
        ]);
        
        return JSON.parse(decrypted.toString('utf8'));
    }
}

// Key rotation
class KeyRotation {
    static async rotateKeys() {
        const newKey = crypto.randomBytes(32).toString('hex');
        const oldKey = process.env.ENCRYPTION_KEY;
        
        // Re-encrypt all sensitive data
        const sensitiveData = await getAllSensitiveData();
        
        for (const item of sensitiveData) {
            const decrypted = decrypt(item.data, oldKey);
            const reencrypted = encrypt(decrypted, newKey);
            await updateEncryptedData(item.id, reencrypted);
        }
        
        // Update key in secure storage
        await updateEncryptionKey(newKey);
        
        // Log rotation event
        logSecurityEvent({
            type: 'KEY_ROTATION',
            timestamp: new Date(),
            itemsRotated: sensitiveData.length
        });
    }
}
```

### 2. Secure Communication / 안전한 통신
```javascript
// TLS configuration
const tlsConfig = {
    minVersion: 'TLSv1.2',
    ciphers: [
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-SHA256',
        'ECDHE-RSA-AES256-SHA384'
    ].join(':'),
    honorCipherOrder: true,
    secureOptions: crypto.constants.SSL_OP_NO_TLSv1 | crypto.constants.SSL_OP_NO_TLSv1_1
};

// Certificate pinning
class CertificatePinning {
    static validateCertificate(cert) {
        const fingerprint = crypto
            .createHash('sha256')
            .update(cert.raw)
            .digest('hex');
        
        if (!allowedFingerprints.includes(fingerprint)) {
            throw new SecurityError('Certificate validation failed');
        }
        
        // Additional checks
        const now = new Date();
        if (now < cert.valid_from || now > cert.valid_to) {
            throw new SecurityError('Certificate expired or not yet valid');
        }
        
        return true;
    }
}
```

### 3. Data Sanitization / 데이터 정제
```javascript
// Comprehensive data sanitization
class DataSanitizer {
    static sanitizeForLog(data) {
        const sensitive = ['password', 'apiKey', 'token', 'secret'];
        const sanitized = { ...data };
        
        for (const key of Object.keys(sanitized)) {
            if (sensitive.some(s => key.toLowerCase().includes(s))) {
                sanitized[key] = '[REDACTED]';
            } else if (typeof sanitized[key] === 'object') {
                sanitized[key] = this.sanitizeForLog(sanitized[key]);
            }
        }
        
        return sanitized;
    }
    
    static sanitizeFilename(filename) {
        // Remove path traversal attempts
        return filename
            .replace(/\.\./g, '')
            .replace(/[\/\\]/g, '')
            .replace(/^\./, '')
            .substring(0, 255);
    }
    
    static sanitizeSQL(input) {
        // Basic SQL injection prevention
        // Note: Use parameterized queries instead
        return input
            .replace(/['";\\]/g, '')
            .replace(/--/g, '')
            .replace(/\/\*/g, '')
            .replace(/\*\//g, '');
    }
}
```

## Infrastructure Security / 인프라 보안

### 1. Server Hardening / 서버 강화
```bash
#!/bin/bash
# Server hardening script

# Update system
apt-get update && apt-get upgrade -y

# Install security tools
apt-get install -y fail2ban ufw unattended-upgrades

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw enable

# Configure fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Configure automatic updates
dpkg-reconfigure -plow unattended-upgrades

# Set up intrusion detection
apt-get install -y aide
aideinit

# Kernel hardening
cat >> /etc/sysctl.conf << EOF
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 1
EOF

sysctl -p
```

### 2. Container Security / 컨테이너 보안
```dockerfile
# Secure Dockerfile
FROM node:16-alpine AS builder

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application
COPY --chown=nodejs:nodejs . .

# Production stage
FROM node:16-alpine

# Install security updates
RUN apk update && \
    apk upgrade && \
    apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Set working directory
WORKDIR /app

# Copy from builder
COPY --from=builder --chown=nodejs:nodejs /app .

# Use non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node healthcheck.js

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "server.js"]
```

### 3. Network Security / 네트워크 보안
```yaml
# Security group configuration
SecurityGroups:
  WebServer:
    Ingress:
      - Protocol: tcp
        Port: 443
        Source: 0.0.0.0/0  # HTTPS from anywhere
      - Protocol: tcp
        Port: 80
        Source: 0.0.0.0/0  # HTTP (redirect to HTTPS)
    Egress:
      - Protocol: tcp
        Port: 443
        Destination: 0.0.0.0/0  # HTTPS to anywhere
      - Protocol: tcp
        Port: 53
        Destination: 0.0.0.0/0  # DNS
  
  Database:
    Ingress:
      - Protocol: tcp
        Port: 5432
        Source: WebServerSecurityGroup  # Only from web servers
    Egress:
      - Protocol: tcp
        Port: 0-65535
        Destination: 127.0.0.1/32  # Localhost only

# WAF rules
WAFRules:
  - Name: RateLimitRule
    Action: Block
    Condition:
      Type: RateBasedRule
      RateLimit: 2000
      
  - Name: SQLInjectionRule
    Action: Block
    Condition:
      Type: SqlInjectionMatchSet
      
  - Name: XSSRule
    Action: Block
    Condition:
      Type: XssMatchSet
```

## Security Best Practices / 보안 모범 사례

### 1. Secure Coding Practices / 안전한 코딩 관행
```javascript
// ✅ Good: Parameterized queries
const query = 'SELECT * FROM articles WHERE id = ? AND group = ?';
db.query(query, [articleId, groupName]);

// ❌ Bad: String concatenation
const query = `SELECT * FROM articles WHERE id = ${articleId}`;

// ✅ Good: Environment variables
const apiKey = process.env.API_KEY;

// ❌ Bad: Hardcoded secrets
const apiKey = 'sk_live_abcd1234';

// ✅ Good: Secure random generation
const token = crypto.randomBytes(32).toString('hex');

// ❌ Bad: Predictable values
const token = Date.now().toString();

// ✅ Good: Constant-time comparison
const isValid = crypto.timingSafeEqual(
    Buffer.from(providedToken),
    Buffer.from(storedToken)
);

// ❌ Bad: Regular comparison (vulnerable to timing attacks)
const isValid = providedToken === storedToken;
```

### 2. Security Headers / 보안 헤더
```javascript
// Comprehensive security headers
app.use((req, res, next) => {
    // Prevent clickjacking
    res.setHeader('X-Frame-Options', 'DENY');
    
    // Prevent MIME type sniffing
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // Enable XSS filter
    res.setHeader('X-XSS-Protection', '1; mode=block');
    
    // Force HTTPS
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
    
    // Content Security Policy
    res.setHeader('Content-Security-Policy', 
        "default-src 'self'; " +
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
        "style-src 'self' 'unsafe-inline'; " +
        "img-src 'self' data: https:; " +
        "font-src 'self'; " +
        "connect-src 'self' https://api.example.com; " +
        "frame-ancestors 'none'; " +
        "base-uri 'self'; " +
        "form-action 'self';"
    );
    
    // Referrer Policy
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    // Permissions Policy
    res.setHeader('Permissions-Policy', 
        'geolocation=(), microphone=(), camera=(), payment=()'
    );
    
    next();
});
```

### 3. Logging and Monitoring / 로깅 및 모니터링
```javascript
// Security event logging
class SecurityLogger {
    static logEvent(event) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            type: event.type,
            severity: event.severity || 'INFO',
            source: event.source,
            userId: event.userId,
            ipAddress: event.ipAddress,
            userAgent: event.userAgent,
            details: this.sanitizeDetails(event.details),
            stackTrace: event.error?.stack
        };
        
        // Write to secure log
        secureLogger.log(logEntry);
        
        // Alert on critical events
        if (event.severity === 'CRITICAL') {
            this.sendSecurityAlert(logEntry);
        }
    }
    
    static sanitizeDetails(details) {
        // Remove sensitive information
        const sanitized = { ...details };
        const sensitiveKeys = ['password', 'token', 'apiKey', 'secret'];
        
        for (const key of Object.keys(sanitized)) {
            if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
                sanitized[key] = '[REDACTED]';
            }
        }
        
        return sanitized;
    }
    
    static sendSecurityAlert(event) {
        // Send to security team
        emailService.send({
            to: process.env.SECURITY_TEAM_EMAIL,
            subject: `CRITICAL Security Event: ${event.type}`,
            body: this.formatAlertEmail(event)
        });
        
        // Send to monitoring service
        monitoringService.alert({
            severity: 'critical',
            title: event.type,
            description: event.details
        });
    }
}

// Usage
SecurityLogger.logEvent({
    type: 'SUSPICIOUS_LOGIN_ATTEMPT',
    severity: 'WARNING',
    source: 'auth-service',
    userId: attemptedUserId,
    ipAddress: req.ip,
    userAgent: req.headers['user-agent'],
    details: {
        reason: 'Multiple failed attempts',
        attemptCount: 5
    }
});
```

## Vulnerability Management / 취약점 관리

### 1. Dependency Scanning / 의존성 스캔
```bash
#!/bin/bash
# Automated dependency scanning

# JavaScript dependencies
echo "Scanning JavaScript dependencies..."
npm audit --audit-level=moderate
npx snyk test

# Python dependencies
echo "Scanning Python dependencies..."
pip-audit
safety check

# Docker images
echo "Scanning Docker images..."
docker scan myapp:latest

# Generate report
echo "Generating vulnerability report..."
{
    echo "Vulnerability Scan Report"
    echo "Date: $(date)"
    echo "========================"
    npm audit --json > npm-audit.json
    safety check --json > safety-check.json
} > vulnerability-report.txt
```

### 2. Security Testing / 보안 테스트
```javascript
// Security test suite
const securityTests = {
    async testSQLInjection() {
        const maliciousInputs = [
            "' OR '1'='1",
            "1; DROP TABLE users--",
            "' UNION SELECT * FROM users--"
        ];
        
        for (const input of maliciousInputs) {
            const response = await api.search(input);
            assert(response.status !== 500, 'SQL injection vulnerability detected');
            assert(!response.body.includes('SQL'), 'SQL error exposed');
        }
    },
    
    async testXSS() {
        const xssPayloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")'
        ];
        
        for (const payload of xssPayloads) {
            const response = await api.createArticle({ title: payload });
            const article = await api.getArticle(response.id);
            assert(!article.title.includes('<script'), 'XSS vulnerability detected');
        }
    },
    
    async testAuthentication() {
        // Test without auth
        const response = await api.getProtectedResource();
        assert(response.status === 401, 'Missing authentication check');
        
        // Test with invalid token
        const invalidResponse = await api.getProtectedResource('invalid-token');
        assert(invalidResponse.status === 401, 'Invalid token accepted');
        
        // Test expired token
        const expiredToken = generateExpiredToken();
        const expiredResponse = await api.getProtectedResource(expiredToken);
        assert(expiredResponse.status === 401, 'Expired token accepted');
    }
};
```

### 3. Penetration Testing / 침투 테스트
```yaml
# Penetration testing checklist
Authentication:
  - [ ] Brute force protection
  - [ ] Session fixation
  - [ ] Password reset vulnerabilities
  - [ ] Multi-factor authentication bypass

Authorization:
  - [ ] Privilege escalation
  - [ ] Insecure direct object references
  - [ ] Missing function level access control

Input Validation:
  - [ ] SQL injection
  - [ ] NoSQL injection
  - [ ] XSS (reflected, stored, DOM-based)
  - [ ] XXE injection
  - [ ] Command injection
  - [ ] LDAP injection

Session Management:
  - [ ] Session hijacking
  - [ ] Session fixation
  - [ ] Insecure session storage
  - [ ] Missing session timeout

Cryptography:
  - [ ] Weak encryption algorithms
  - [ ] Insecure random number generation
  - [ ] Missing encryption
  - [ ] Key management issues

Business Logic:
  - [ ] Race conditions
  - [ ] Time-of-check time-of-use
  - [ ] Business constraint bypass
```

## Incident Response / 보안 사고 대응

### 1. Incident Response Plan / 사고 대응 계획
```yaml
Incident Response Phases:
  1. Preparation:
     - Incident response team contacts
     - Communication channels
     - Tools and resources
     - Documentation templates
  
  2. Detection & Analysis:
     - Log analysis
     - Indicator identification
     - Scope determination
     - Impact assessment
  
  3. Containment:
     - Short-term containment
     - System isolation
     - Evidence preservation
     - Long-term containment
  
  4. Eradication:
     - Malware removal
     - Vulnerability patching
     - System hardening
     - Account cleanup
  
  5. Recovery:
     - System restoration
     - Monitoring enhancement
     - Validation testing
     - Return to operations
  
  6. Lessons Learned:
     - Incident documentation
     - Process improvement
     - Training updates
     - Policy updates
```

### 2. Incident Response Procedures / 사고 대응 절차
```javascript
// Automated incident response
class IncidentResponse {
    static async handleSecurityIncident(incident) {
        const incidentId = generateIncidentId();
        
        // 1. Log incident
        await this.logIncident(incidentId, incident);
        
        // 2. Assess severity
        const severity = this.assessSeverity(incident);
        
        // 3. Immediate containment
        if (severity >= SEVERITY.HIGH) {
            await this.containThreat(incident);
        }
        
        // 4. Notify stakeholders
        await this.notifyStakeholders(incidentId, incident, severity);
        
        // 5. Collect evidence
        await this.collectEvidence(incidentId, incident);
        
        // 6. Begin investigation
        const investigation = await this.startInvestigation(incidentId);
        
        return {
            incidentId,
            severity,
            status: 'INVESTIGATING',
            investigation
        };
    }
    
    static async containThreat(incident) {
        switch (incident.type) {
            case 'BRUTE_FORCE':
                await this.blockIP(incident.sourceIP);
                await this.lockAccount(incident.targetAccount);
                break;
                
            case 'DATA_BREACH':
                await this.revokeAllTokens();
                await this.forcePasswordReset();
                break;
                
            case 'MALWARE':
                await this.isolateSystem(incident.affectedSystem);
                await this.runAntimalware(incident.affectedSystem);
                break;
        }
    }
    
    static async collectEvidence(incidentId, incident) {
        const evidence = {
            logs: await this.collectLogs(incident.timeRange),
            networkCapture: await this.captureNetworkTraffic(incident),
            systemSnapshot: await this.createSystemSnapshot(incident.affectedSystem),
            memoryDump: await this.createMemoryDump(incident.affectedSystem)
        };
        
        // Store evidence securely
        await this.storeEvidence(incidentId, evidence);
        
        // Create chain of custody
        await this.createChainOfCustody(incidentId, evidence);
    }
}
```

### 3. Post-Incident Analysis / 사고 후 분석
```javascript
// Post-incident review template
const postIncidentReview = {
    incidentId: 'INC-2025-001',
    date: '2025-01-25',
    
    summary: {
        type: 'Data Breach',
        severity: 'High',
        duration: '2 hours',
        impact: 'Limited user data exposure',
        rootCause: 'Unpatched vulnerability'
    },
    
    timeline: [
        { time: '10:00', event: 'Suspicious activity detected' },
        { time: '10:15', event: 'Incident confirmed' },
        { time: '10:20', event: 'Containment started' },
        { time: '11:00', event: 'Threat eliminated' },
        { time: '12:00', event: 'Systems restored' }
    ],
    
    lessonsLearned: [
        'Need automated patch management',
        'Improve detection capabilities',
        'Update incident response procedures'
    ],
    
    actionItems: [
        {
            action: 'Implement automated patching',
            owner: 'DevOps Team',
            dueDate: '2025-02-01'
        },
        {
            action: 'Deploy advanced threat detection',
            owner: 'Security Team',
            dueDate: '2025-02-15'
        }
    ]
};
```

## Security Checklist / 보안 체크리스트

### Development Security Checklist / 개발 보안 체크리스트
```yaml
Before Commit:
  Code Review:
    - [ ] No hardcoded secrets
    - [ ] Input validation implemented
    - [ ] Output encoding applied
    - [ ] Error messages sanitized
    - [ ] Logging excludes sensitive data
  
  Dependencies:
    - [ ] No known vulnerabilities
    - [ ] Minimal required permissions
    - [ ] From trusted sources
    - [ ] License compatible
  
  Testing:
    - [ ] Security tests pass
    - [ ] No security warnings
    - [ ] Code coverage adequate

Before Deployment:
  Configuration:
    - [ ] Production secrets rotated
    - [ ] Debug mode disabled
    - [ ] Security headers configured
    - [ ] HTTPS enforced
  
  Access Control:
    - [ ] Authentication required
    - [ ] Authorization implemented
    - [ ] Rate limiting enabled
    - [ ] CORS configured
  
  Monitoring:
    - [ ] Logging configured
    - [ ] Alerts set up
    - [ ] Backup verified
    - [ ] Recovery tested
```

### Operational Security Checklist / 운영 보안 체크리스트
```yaml
Daily:
  - [ ] Check security alerts
  - [ ] Review access logs
  - [ ] Monitor rate limits
  - [ ] Verify backups

Weekly:
  - [ ] Review user activities
  - [ ] Check for updates
  - [ ] Analyze security metrics
  - [ ] Test incident response

Monthly:
  - [ ] Rotate credentials
  - [ ] Update dependencies
  - [ ] Security assessment
  - [ ] Team training

Quarterly:
  - [ ] Penetration testing
  - [ ] Architecture review
  - [ ] Policy updates
  - [ ] Disaster recovery drill
```

---
*Security is everyone's responsibility. Report security issues to security@example.com*

*보안은 모든 사람의 책임입니다. 보안 문제를 security@example.com으로 신고하세요*

*Last Updated: January 25, 2025*