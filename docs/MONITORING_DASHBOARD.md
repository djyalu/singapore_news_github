# Monitoring Dashboard Guide / 모니터링 대시보드 가이드

## Table of Contents / 목차
1. [Dashboard Overview / 대시보드 개요](#dashboard-overview--대시보드-개요)
2. [Real-time Monitoring / 실시간 모니터링](#real-time-monitoring--실시간-모니터링)
3. [Performance Metrics / 성능 지표](#performance-metrics--성능-지표)
4. [System Health Checks / 시스템 상태 점검](#system-health-checks--시스템-상태-점검)
5. [Alerts and Notifications / 알림 및 통지](#alerts-and-notifications--알림-및-통지)
6. [Log Analysis / 로그 분석](#log-analysis--로그-분석)
7. [Custom Dashboards / 커스텀 대시보드](#custom-dashboards--커스텀-대시보드)
8. [API Monitoring / API 모니터링](#api-monitoring--api-모니터링)
9. [Scraping Analytics / 스크래핑 분석](#scraping-analytics--스크래핑-분석)
10. [Reporting / 보고서](#reporting--보고서)

## Dashboard Overview / 대시보드 개요

### Main Dashboard Layout / 메인 대시보드 레이아웃
```
┌─────────────────────────────────────────────────────────────────┐
│                    Singapore News Scraper Monitor                │
├─────────────────┬───────────────────┬───────────────────────────┤
│ System Status   │ Active Scrapers   │ API Health              │
│ ● Operational   │ 3/16 Running      │ Latency: 120ms         │
│ Uptime: 99.9%   │ Queue: 5 items    │ Success: 99.8%         │
├─────────────────┴───────────────────┴───────────────────────────┤
│                         Real-time Metrics                        │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │ Requests/sec  ████████████████░░░░  156                 │    │
│ │ Response Time ██████░░░░░░░░░░░░░░  230ms              │    │
│ │ Error Rate    █░░░░░░░░░░░░░░░░░░░  0.2%               │    │
│ │ CPU Usage     ████████████░░░░░░░░  65%                │    │
│ │ Memory Usage  ██████████░░░░░░░░░░  52%                │    │
│ └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│ Recent Alerts                     │ Quick Actions               │
│ ⚠ High API latency (5 min ago)   │ [Trigger Scraping]         │
│ ✓ Backup completed (1 hour ago)   │ [Clear Cache]              │
│ ⚠ Storage 85% full (2 hours ago) │ [Export Report]            │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard Components / 대시보드 구성요소
1. **Status Indicators**: Overall system health
2. **Real-time Metrics**: Live performance data
3. **Alert Panel**: Recent issues and notifications
4. **Quick Actions**: Common administrative tasks
5. **Trend Charts**: Historical performance

## Real-time Monitoring / 실시간 모니터링

### 1. WebSocket Implementation / WebSocket 구현
```javascript
// Real-time monitoring client
class MonitoringClient {
    constructor(dashboardUrl) {
        this.ws = null;
        this.dashboardUrl = dashboardUrl;
        this.metrics = {};
        this.charts = {};
        this.reconnectAttempts = 0;
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupCharts();
        this.setupEventHandlers();
    }
    
    connectWebSocket() {
        this.ws = new WebSocket(`wss://${this.dashboardUrl}/monitoring`);
        
        this.ws.onopen = () => {
            console.log('Connected to monitoring server');
            this.reconnectAttempts = 0;
            this.requestInitialData();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.attemptReconnect();
        };
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < 5) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            console.log(`Reconnecting in ${delay}ms...`);
            setTimeout(() => this.connectWebSocket(), delay);
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'metrics':
                this.updateMetrics(data.payload);
                break;
            case 'alert':
                this.showAlert(data.payload);
                break;
            case 'status':
                this.updateStatus(data.payload);
                break;
            case 'chart':
                this.updateChart(data.payload);
                break;
        }
    }
    
    updateMetrics(metrics) {
        // Update metric displays
        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.getElementById(`metric-${key}`);
            if (element) {
                element.textContent = this.formatMetric(key, value);
                
                // Add animation for changes
                element.classList.add('metric-updated');
                setTimeout(() => element.classList.remove('metric-updated'), 300);
            }
            
            // Store for history
            if (!this.metrics[key]) {
                this.metrics[key] = [];
            }
            this.metrics[key].push({
                timestamp: Date.now(),
                value: value
            });
            
            // Keep last 100 data points
            if (this.metrics[key].length > 100) {
                this.metrics[key].shift();
            }
        });
    }
    
    formatMetric(key, value) {
        const formatters = {
            'response-time': (v) => `${v}ms`,
            'requests-per-second': (v) => `${v} req/s`,
            'error-rate': (v) => `${(v * 100).toFixed(2)}%`,
            'cpu-usage': (v) => `${v}%`,
            'memory-usage': (v) => `${v}%`,
            'active-connections': (v) => v.toString(),
            'queue-size': (v) => v.toString()
        };
        
        return formatters[key] ? formatters[key](value) : value.toString();
    }
}
```

### 2. Real-time Charts / 실시간 차트
```javascript
// Chart.js implementation for real-time data
class RealtimeChart {
    constructor(canvasId, config = {}) {
        this.canvas = document.getElementById(canvasId);
        this.maxDataPoints = config.maxDataPoints || 60;
        this.updateInterval = config.updateInterval || 1000;
        
        this.chart = new Chart(this.canvas, {
            type: config.type || 'line',
            data: {
                labels: [],
                datasets: [{
                    label: config.label || 'Metrics',
                    data: [],
                    borderColor: config.color || 'rgb(75, 192, 192)',
                    backgroundColor: config.backgroundColor || 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: config.yAxisLabel || 'Value'
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                animation: {
                    duration: 0 // Disable animations for performance
                }
            }
        });
    }
    
    addData(value, label = new Date().toLocaleTimeString()) {
        if (this.chart.data.labels.length >= this.maxDataPoints) {
            this.chart.data.labels.shift();
            this.chart.data.datasets[0].data.shift();
        }
        
        this.chart.data.labels.push(label);
        this.chart.data.datasets[0].data.push(value);
        this.chart.update('none'); // Update without animation
    }
    
    addMultipleData(datasets) {
        // For multiple series
        datasets.forEach((data, index) => {
            if (!this.chart.data.datasets[index]) {
                this.chart.data.datasets[index] = {
                    label: data.label,
                    data: [],
                    borderColor: data.color,
                    backgroundColor: data.backgroundColor
                };
            }
            
            this.chart.data.datasets[index].data.push(data.value);
            
            if (this.chart.data.datasets[index].data.length > this.maxDataPoints) {
                this.chart.data.datasets[index].data.shift();
            }
        });
        
        this.chart.update('none');
    }
}
```

## Performance Metrics / 성능 지표

### 1. Key Performance Indicators / 주요 성능 지표
```javascript
// KPI monitoring configuration
const KPIConfig = {
    metrics: {
        availability: {
            target: 99.9,
            warning: 99.5,
            critical: 99.0,
            unit: '%',
            calculation: 'uptime / total_time * 100'
        },
        responseTime: {
            target: 200,
            warning: 500,
            critical: 1000,
            unit: 'ms',
            percentile: 95
        },
        errorRate: {
            target: 0.1,
            warning: 1.0,
            critical: 5.0,
            unit: '%',
            calculation: 'errors / total_requests * 100'
        },
        throughput: {
            target: 1000,
            warning: 500,
            critical: 100,
            unit: 'req/s',
            aggregation: 'average'
        },
        scrapingSuccess: {
            target: 95,
            warning: 80,
            critical: 60,
            unit: '%',
            calculation: 'successful_scrapes / total_scrapes * 100'
        }
    }
};

class KPIMonitor {
    constructor(config) {
        this.config = config;
        this.currentValues = {};
        this.history = {};
    }
    
    updateMetric(name, value) {
        const metric = this.config.metrics[name];
        if (!metric) return;
        
        this.currentValues[name] = value;
        
        // Store history
        if (!this.history[name]) {
            this.history[name] = [];
        }
        
        this.history[name].push({
            timestamp: Date.now(),
            value: value
        });
        
        // Check thresholds
        const status = this.getStatus(name, value);
        
        // Update UI
        this.updateDisplay(name, value, status);
        
        // Send alerts if needed
        if (status === 'critical') {
            this.sendAlert(name, value, status);
        }
    }
    
    getStatus(name, value) {
        const metric = this.config.metrics[name];
        
        // For metrics where lower is better
        if (['responseTime', 'errorRate'].includes(name)) {
            if (value >= metric.critical) return 'critical';
            if (value >= metric.warning) return 'warning';
            if (value <= metric.target) return 'good';
            return 'normal';
        }
        
        // For metrics where higher is better
        if (value <= metric.critical) return 'critical';
        if (value <= metric.warning) return 'warning';
        if (value >= metric.target) return 'good';
        return 'normal';
    }
    
    updateDisplay(name, value, status) {
        const element = document.getElementById(`kpi-${name}`);
        if (!element) return;
        
        const metric = this.config.metrics[name];
        
        element.innerHTML = `
            <div class="kpi-card ${status}">
                <div class="kpi-title">${this.formatName(name)}</div>
                <div class="kpi-value">${value}${metric.unit}</div>
                <div class="kpi-target">Target: ${metric.target}${metric.unit}</div>
                <div class="kpi-status">
                    <span class="status-indicator ${status}"></span>
                    ${status.toUpperCase()}
                </div>
            </div>
        `;
    }
    
    formatName(name) {
        return name.replace(/([A-Z])/g, ' $1').trim()
            .replace(/^./, str => str.toUpperCase());
    }
}
```

### 2. Performance Trending / 성능 추세
```javascript
// Trend analysis for performance metrics
class PerformanceTrending {
    constructor() {
        this.trendWindow = 24 * 60 * 60 * 1000; // 24 hours
        this.trends = {};
    }
    
    calculateTrend(metricName, dataPoints) {
        if (dataPoints.length < 2) return 'stable';
        
        // Simple linear regression
        const n = dataPoints.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        
        dataPoints.forEach((point, index) => {
            sumX += index;
            sumY += point.value;
            sumXY += index * point.value;
            sumX2 += index * index;
        });
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const avgValue = sumY / n;
        
        // Calculate percentage change
        const percentChange = (slope * n / avgValue) * 100;
        
        // Determine trend
        if (Math.abs(percentChange) < 5) return 'stable';
        if (percentChange > 0) {
            return percentChange > 20 ? 'increasing-fast' : 'increasing';
        } else {
            return percentChange < -20 ? 'decreasing-fast' : 'decreasing';
        }
    }
    
    analyzeTrends(metrics) {
        const analysis = {};
        
        Object.entries(metrics).forEach(([name, history]) => {
            const recentData = history.filter(
                point => point.timestamp > Date.now() - this.trendWindow
            );
            
            const trend = this.calculateTrend(name, recentData);
            const average = recentData.reduce((sum, p) => sum + p.value, 0) / recentData.length;
            const max = Math.max(...recentData.map(p => p.value));
            const min = Math.min(...recentData.map(p => p.value));
            
            analysis[name] = {
                trend,
                average: average.toFixed(2),
                max,
                min,
                dataPoints: recentData.length,
                volatility: this.calculateVolatility(recentData)
            };
        });
        
        return analysis;
    }
    
    calculateVolatility(dataPoints) {
        if (dataPoints.length < 2) return 'low';
        
        const values = dataPoints.map(p => p.value);
        const mean = values.reduce((a, b) => a + b) / values.length;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        const stdDev = Math.sqrt(variance);
        const cv = (stdDev / mean) * 100; // Coefficient of variation
        
        if (cv < 10) return 'low';
        if (cv < 25) return 'medium';
        return 'high';
    }
    
    generateTrendReport(analysis) {
        const report = {
            timestamp: new Date().toISOString(),
            summary: {},
            recommendations: []
        };
        
        Object.entries(analysis).forEach(([metric, data]) => {
            report.summary[metric] = {
                status: this.getTrendStatus(metric, data),
                description: this.getTrendDescription(metric, data)
            };
            
            const recommendation = this.getRecommendation(metric, data);
            if (recommendation) {
                report.recommendations.push(recommendation);
            }
        });
        
        return report;
    }
    
    getTrendStatus(metric, data) {
        const concerning = ['increasing-fast', 'decreasing-fast', 'high'];
        
        if (metric === 'errorRate' && data.trend.includes('increasing')) {
            return 'critical';
        }
        
        if (metric === 'responseTime' && data.trend === 'increasing-fast') {
            return 'warning';
        }
        
        if (data.volatility === 'high') {
            return 'warning';
        }
        
        return 'normal';
    }
    
    getRecommendation(metric, data) {
        const recommendations = {
            errorRate: {
                'increasing-fast': 'Investigate error spike immediately. Check recent deployments.',
                'high-volatility': 'Error rate is unstable. Review error handling logic.'
            },
            responseTime: {
                'increasing-fast': 'Response time degrading. Check database queries and API calls.',
                'high-volatility': 'Response time inconsistent. Consider caching or load balancing.'
            },
            cpuUsage: {
                'increasing-fast': 'CPU usage rising rapidly. Scale up or optimize code.',
                'high-average': 'Consistently high CPU usage. Consider horizontal scaling.'
            }
        };
        
        if (recommendations[metric]?.[data.trend]) {
            return {
                metric,
                issue: data.trend,
                recommendation: recommendations[metric][data.trend],
                priority: this.getTrendStatus(metric, data)
            };
        }
        
        return null;
    }
}
```

## System Health Checks / 시스템 상태 점검

### 1. Automated Health Checks / 자동 상태 점검
```javascript
// Comprehensive health check system
class HealthCheckSystem {
    constructor() {
        this.checks = {
            api: {
                name: 'API Endpoints',
                interval: 60000, // 1 minute
                timeout: 5000,
                endpoints: [
                    { url: '/api/health', expected: 200 },
                    { url: '/api/get-latest-scraped', expected: 200 },
                    { url: '/api/get-scraping-status', expected: 200 }
                ]
            },
            database: {
                name: 'Data Storage',
                interval: 300000, // 5 minutes
                checks: [
                    { type: 'file-exists', path: 'data/settings.json' },
                    { type: 'file-readable', path: 'data/sites.json' },
                    { type: 'directory-writable', path: 'data/scraped' }
                ]
            },
            scraping: {
                name: 'Scraping Service',
                interval: 600000, // 10 minutes
                checks: [
                    { type: 'last-run', maxAge: 86400000 }, // 24 hours
                    { type: 'success-rate', threshold: 0.8 },
                    { type: 'active-scrapers', min: 0, max: 5 }
                ]
            },
            external: {
                name: 'External Services',
                interval: 900000, // 15 minutes
                services: [
                    { name: 'GitHub API', url: 'https://api.github.com/rate_limit' },
                    { name: 'WhatsApp API', url: 'https://api.green-api.com/waInstance/getStateInstance' },
                    { name: 'Gemini API', url: 'https://generativelanguage.googleapis.com/v1beta/models' }
                ]
            }
        };
        
        this.results = {};
        this.history = {};
    }
    
    async startHealthChecks() {
        for (const [category, config] of Object.entries(this.checks)) {
            this.scheduleCheck(category, config);
        }
    }
    
    scheduleCheck(category, config) {
        // Run immediately
        this.runCheck(category, config);
        
        // Schedule recurring
        setInterval(() => {
            this.runCheck(category, config);
        }, config.interval);
    }
    
    async runCheck(category, config) {
        console.log(`Running health check: ${config.name}`);
        const startTime = Date.now();
        const results = {
            category,
            name: config.name,
            timestamp: startTime,
            checks: []
        };
        
        try {
            switch (category) {
                case 'api':
                    results.checks = await this.checkAPIs(config);
                    break;
                case 'database':
                    results.checks = await this.checkDatabase(config);
                    break;
                case 'scraping':
                    results.checks = await this.checkScraping(config);
                    break;
                case 'external':
                    results.checks = await this.checkExternal(config);
                    break;
            }
            
            results.duration = Date.now() - startTime;
            results.status = this.calculateOverallStatus(results.checks);
            
            // Store results
            this.results[category] = results;
            this.addToHistory(category, results);
            
            // Update UI
            this.updateHealthDisplay(category, results);
            
            // Send alerts if needed
            if (results.status === 'critical') {
                this.sendHealthAlert(category, results);
            }
            
        } catch (error) {
            console.error(`Health check failed for ${category}:`, error);
            results.status = 'error';
            results.error = error.message;
        }
    }
    
    async checkAPIs(config) {
        const checks = [];
        
        for (const endpoint of config.endpoints) {
            const check = {
                name: endpoint.url,
                status: 'checking'
            };
            
            try {
                const response = await fetch(endpoint.url, {
                    timeout: config.timeout
                });
                
                check.responseTime = response.headers.get('X-Response-Time') || 'N/A';
                check.status = response.status === endpoint.expected ? 'healthy' : 'unhealthy';
                check.statusCode = response.status;
                
            } catch (error) {
                check.status = 'failed';
                check.error = error.message;
            }
            
            checks.push(check);
        }
        
        return checks;
    }
    
    async checkDatabase(config) {
        const checks = [];
        
        for (const check of config.checks) {
            const result = {
                name: `${check.type}: ${check.path}`,
                status: 'checking'
            };
            
            try {
                switch (check.type) {
                    case 'file-exists':
                        result.status = await this.fileExists(check.path) ? 'healthy' : 'unhealthy';
                        break;
                    case 'file-readable':
                        result.status = await this.fileReadable(check.path) ? 'healthy' : 'unhealthy';
                        break;
                    case 'directory-writable':
                        result.status = await this.directoryWritable(check.path) ? 'healthy' : 'unhealthy';
                        break;
                }
            } catch (error) {
                result.status = 'failed';
                result.error = error.message;
            }
            
            checks.push(result);
        }
        
        return checks;
    }
    
    calculateOverallStatus(checks) {
        const statuses = checks.map(c => c.status);
        
        if (statuses.includes('failed') || statuses.includes('error')) {
            return 'critical';
        }
        
        if (statuses.includes('unhealthy')) {
            return 'warning';
        }
        
        return 'healthy';
    }
    
    updateHealthDisplay(category, results) {
        const element = document.getElementById(`health-${category}`);
        if (!element) return;
        
        const statusClass = {
            healthy: 'success',
            warning: 'warning',
            critical: 'danger',
            error: 'danger'
        }[results.status];
        
        element.className = `health-indicator ${statusClass}`;
        element.innerHTML = `
            <div class="health-header">
                <span class="health-name">${results.name}</span>
                <span class="health-status">${results.status.toUpperCase()}</span>
            </div>
            <div class="health-details">
                ${results.checks.map(check => `
                    <div class="health-check ${check.status}">
                        <span class="check-name">${check.name}</span>
                        <span class="check-status">${check.status}</span>
                    </div>
                `).join('')}
            </div>
            <div class="health-footer">
                Last check: ${new Date(results.timestamp).toLocaleTimeString()}
                (${results.duration}ms)
            </div>
        `;
    }
}
```

### 2. Dependency Health Monitoring / 의존성 상태 모니터링
```javascript
// Monitor health of external dependencies
class DependencyMonitor {
    constructor() {
        this.dependencies = {
            github: {
                name: 'GitHub API',
                healthEndpoint: 'https://api.github.com/rate_limit',
                critical: true,
                checkInterval: 300000, // 5 minutes
                healthCheck: async () => {
                    const response = await fetch(this.dependencies.github.healthEndpoint, {
                        headers: {
                            'Authorization': `token ${process.env.GITHUB_TOKEN}`
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    return {
                        healthy: data.rate.remaining > 100,
                        details: {
                            remaining: data.rate.remaining,
                            limit: data.rate.limit,
                            reset: new Date(data.rate.reset * 1000).toLocaleTimeString()
                        }
                    };
                }
            },
            vercel: {
                name: 'Vercel Platform',
                healthEndpoint: 'https://api.vercel.com/v1/health',
                critical: true,
                checkInterval: 300000,
                healthCheck: async () => {
                    const response = await fetch(this.dependencies.vercel.healthEndpoint);
                    return {
                        healthy: response.ok,
                        details: {
                            status: response.status,
                            operational: response.ok
                        }
                    };
                }
            },
            whatsapp: {
                name: 'WhatsApp API',
                critical: false,
                checkInterval: 600000, // 10 minutes
                healthCheck: async () => {
                    // Custom WhatsApp health check
                    try {
                        const response = await fetch('/api/test-whatsapp', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ test: true })
                        });
                        
                        return {
                            healthy: response.ok,
                            details: await response.json()
                        };
                    } catch (error) {
                        return {
                            healthy: false,
                            details: { error: error.message }
                        };
                    }
                }
            }
        };
        
        this.statuses = {};
        this.alerts = [];
    }
    
    async checkAllDependencies() {
        const results = {};
        
        for (const [key, dep] of Object.entries(this.dependencies)) {
            try {
                const result = await dep.healthCheck();
                results[key] = {
                    name: dep.name,
                    healthy: result.healthy,
                    critical: dep.critical,
                    details: result.details,
                    lastCheck: new Date().toISOString()
                };
                
                // Check for status changes
                if (this.statuses[key] && this.statuses[key].healthy !== result.healthy) {
                    this.handleStatusChange(key, result.healthy);
                }
                
                this.statuses[key] = results[key];
                
            } catch (error) {
                results[key] = {
                    name: dep.name,
                    healthy: false,
                    critical: dep.critical,
                    error: error.message,
                    lastCheck: new Date().toISOString()
                };
            }
        }
        
        this.updateDependencyDisplay(results);
        return results;
    }
    
    handleStatusChange(dependency, isHealthy) {
        const dep = this.dependencies[dependency];
        
        if (!isHealthy && dep.critical) {
            this.alerts.push({
                level: 'critical',
                dependency: dep.name,
                message: `Critical dependency ${dep.name} is down!`,
                timestamp: new Date()
            });
            
            // Trigger emergency procedures
            this.triggerEmergencyProcedure(dependency);
        } else if (isHealthy) {
            this.alerts.push({
                level: 'info',
                dependency: dep.name,
                message: `${dep.name} has recovered`,
                timestamp: new Date()
            });
        }
    }
    
    triggerEmergencyProcedure(dependency) {
        switch (dependency) {
            case 'github':
                console.error('GitHub API is down - switching to cached mode');
                // Implement fallback logic
                break;
            case 'vercel':
                console.error('Vercel is down - check alternate endpoints');
                // Implement Vercel outage handling
                break;
        }
    }
}
```

## Alerts and Notifications / 알림 및 통지

### 1. Alert Configuration / 알림 설정
```javascript
// Comprehensive alerting system
class AlertingSystem {
    constructor() {
        this.rules = {
            highErrorRate: {
                condition: (metrics) => metrics.errorRate > 5,
                severity: 'critical',
                message: 'Error rate exceeds 5%',
                channels: ['email', 'slack', 'dashboard'],
                cooldown: 300000 // 5 minutes
            },
            slowResponse: {
                condition: (metrics) => metrics.responseTime > 1000,
                severity: 'warning',
                message: 'Response time exceeds 1 second',
                channels: ['dashboard', 'slack'],
                cooldown: 600000 // 10 minutes
            },
            lowDiskSpace: {
                condition: (metrics) => metrics.diskUsage > 90,
                severity: 'warning',
                message: 'Disk usage exceeds 90%',
                channels: ['email', 'dashboard'],
                cooldown: 3600000 // 1 hour
            },
            scrapingFailure: {
                condition: (metrics) => metrics.scrapingSuccessRate < 50,
                severity: 'critical',
                message: 'Scraping success rate below 50%',
                channels: ['email', 'slack', 'sms'],
                cooldown: 1800000 // 30 minutes
            },
            apiQuotaLow: {
                condition: (metrics) => metrics.apiQuotaRemaining < 100,
                severity: 'warning',
                message: 'API quota running low',
                channels: ['dashboard', 'email'],
                cooldown: 3600000
            }
        };
        
        this.channels = {
            email: new EmailChannel(),
            slack: new SlackChannel(),
            sms: new SMSChannel(),
            dashboard: new DashboardChannel()
        };
        
        this.alertHistory = [];
        this.lastAlertTime = {};
    }
    
    checkAlerts(metrics) {
        const alerts = [];
        
        for (const [ruleName, rule] of Object.entries(this.rules)) {
            if (rule.condition(metrics)) {
                // Check cooldown
                const lastAlert = this.lastAlertTime[ruleName];
                if (lastAlert && Date.now() - lastAlert < rule.cooldown) {
                    continue; // Skip due to cooldown
                }
                
                const alert = {
                    id: `${ruleName}_${Date.now()}`,
                    rule: ruleName,
                    severity: rule.severity,
                    message: rule.message,
                    timestamp: new Date(),
                    metrics: this.extractRelevantMetrics(ruleName, metrics)
                };
                
                alerts.push(alert);
                this.sendAlert(alert, rule.channels);
                
                // Update last alert time
                this.lastAlertTime[ruleName] = Date.now();
            }
        }
        
        return alerts;
    }
    
    sendAlert(alert, channels) {
        channels.forEach(channelName => {
            const channel = this.channels[channelName];
            if (channel) {
                channel.send(alert);
            }
        });
        
        // Store in history
        this.alertHistory.push(alert);
        
        // Keep only last 1000 alerts
        if (this.alertHistory.length > 1000) {
            this.alertHistory = this.alertHistory.slice(-1000);
        }
    }
    
    extractRelevantMetrics(ruleName, metrics) {
        const relevantMetrics = {
            highErrorRate: ['errorRate', 'totalRequests', 'failedRequests'],
            slowResponse: ['responseTime', 'p95ResponseTime', 'p99ResponseTime'],
            lowDiskSpace: ['diskUsage', 'diskTotal', 'diskFree'],
            scrapingFailure: ['scrapingSuccessRate', 'totalScrapes', 'failedScrapes'],
            apiQuotaLow: ['apiQuotaRemaining', 'apiQuotaLimit', 'apiQuotaReset']
        };
        
        const relevant = {};
        const fields = relevantMetrics[ruleName] || [];
        
        fields.forEach(field => {
            if (metrics[field] !== undefined) {
                relevant[field] = metrics[field];
            }
        });
        
        return relevant;
    }
}

// Alert channels implementation
class EmailChannel {
    async send(alert) {
        const emailContent = {
            to: process.env.ALERT_EMAIL,
            subject: `[${alert.severity.toUpperCase()}] ${alert.message}`,
            html: this.formatEmailBody(alert)
        };
        
        try {
            await fetch('/api/send-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(emailContent)
            });
        } catch (error) {
            console.error('Failed to send email alert:', error);
        }
    }
    
    formatEmailBody(alert) {
        return `
            <h2>Alert: ${alert.message}</h2>
            <p><strong>Severity:</strong> ${alert.severity}</p>
            <p><strong>Time:</strong> ${alert.timestamp}</p>
            <h3>Metrics:</h3>
            <pre>${JSON.stringify(alert.metrics, null, 2)}</pre>
            <p><a href="${process.env.DASHBOARD_URL}">View Dashboard</a></p>
        `;
    }
}

class SlackChannel {
    async send(alert) {
        const color = {
            critical: '#FF0000',
            warning: '#FFA500',
            info: '#0000FF'
        }[alert.severity];
        
        const payload = {
            attachments: [{
                color,
                title: alert.message,
                fields: Object.entries(alert.metrics).map(([key, value]) => ({
                    title: key,
                    value: value.toString(),
                    short: true
                })),
                footer: 'Singapore News Scraper',
                ts: Math.floor(alert.timestamp.getTime() / 1000)
            }]
        };
        
        try {
            await fetch(process.env.SLACK_WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error('Failed to send Slack alert:', error);
        }
    }
}
```

### 2. Alert Dashboard / 알림 대시보드
```html
<!-- Alert dashboard component -->
<div id="alert-dashboard" class="alert-container">
    <div class="alert-header">
        <h3>System Alerts</h3>
        <div class="alert-controls">
            <button onclick="acknowledgeAllAlerts()">Acknowledge All</button>
            <button onclick="clearResolvedAlerts()">Clear Resolved</button>
            <select id="alert-filter" onchange="filterAlerts()">
                <option value="all">All Alerts</option>
                <option value="critical">Critical Only</option>
                <option value="warning">Warnings</option>
                <option value="unacknowledged">Unacknowledged</option>
            </select>
        </div>
    </div>
    
    <div id="alert-list" class="alert-list">
        <!-- Alerts will be dynamically inserted here -->
    </div>
    
    <div class="alert-summary">
        <span class="critical-count">Critical: <span id="critical-count">0</span></span>
        <span class="warning-count">Warning: <span id="warning-count">0</span></span>
        <span class="info-count">Info: <span id="info-count">0</span></span>
    </div>
</div>

<style>
.alert-container {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
}

.alert-item {
    background: white;
    border-left: 4px solid;
    margin: 10px 0;
    padding: 15px;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.alert-item.critical {
    border-color: #ff0000;
    background-color: #fff5f5;
}

.alert-item.warning {
    border-color: #ffa500;
    background-color: #fffaf0;
}

.alert-item.info {
    border-color: #0000ff;
    background-color: #f0f0ff;
}

.alert-content {
    flex-grow: 1;
}

.alert-title {
    font-weight: bold;
    margin-bottom: 5px;
}

.alert-time {
    color: #666;
    font-size: 0.9em;
}

.alert-actions {
    display: flex;
    gap: 10px;
}

.alert-summary {
    margin-top: 20px;
    display: flex;
    justify-content: space-around;
    font-weight: bold;
}

.critical-count { color: #ff0000; }
.warning-count { color: #ffa500; }
.info-count { color: #0000ff; }
</style>

<script>
class AlertDashboard {
    constructor() {
        this.alerts = [];
        this.filter = 'all';
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.loadHistoricalAlerts();
        setInterval(() => this.updateRelativeTimes(), 60000);
    }
    
    connectWebSocket() {
        this.ws = new WebSocket('wss://your-domain/alerts');
        
        this.ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            this.addAlert(alert);
        };
    }
    
    addAlert(alert) {
        alert.id = alert.id || Date.now();
        alert.acknowledged = false;
        alert.resolved = false;
        
        this.alerts.unshift(alert);
        this.updateDisplay();
        
        // Show notification for critical alerts
        if (alert.severity === 'critical') {
            this.showNotification(alert);
        }
    }
    
    updateDisplay() {
        const filteredAlerts = this.getFilteredAlerts();
        const alertList = document.getElementById('alert-list');
        
        alertList.innerHTML = filteredAlerts.map(alert => `
            <div class="alert-item ${alert.severity} ${alert.acknowledged ? 'acknowledged' : ''}" 
                 data-alert-id="${alert.id}">
                <div class="alert-content">
                    <div class="alert-title">${alert.message}</div>
                    <div class="alert-time">${this.getRelativeTime(alert.timestamp)}</div>
                    ${alert.details ? `<div class="alert-details">${alert.details}</div>` : ''}
                </div>
                <div class="alert-actions">
                    ${!alert.acknowledged ? 
                        `<button onclick="alertDashboard.acknowledgeAlert(${alert.id})">Acknowledge</button>` : ''}
                    ${!alert.resolved ? 
                        `<button onclick="alertDashboard.resolveAlert(${alert.id})">Resolve</button>` : ''}
                    <button onclick="alertDashboard.viewDetails(${alert.id})">Details</button>
                </div>
            </div>
        `).join('');
        
        this.updateSummary();
    }
    
    getFilteredAlerts() {
        switch (this.filter) {
            case 'critical':
                return this.alerts.filter(a => a.severity === 'critical');
            case 'warning':
                return this.alerts.filter(a => a.severity === 'warning');
            case 'unacknowledged':
                return this.alerts.filter(a => !a.acknowledged);
            default:
                return this.alerts;
        }
    }
    
    updateSummary() {
        const counts = {
            critical: this.alerts.filter(a => a.severity === 'critical' && !a.resolved).length,
            warning: this.alerts.filter(a => a.severity === 'warning' && !a.resolved).length,
            info: this.alerts.filter(a => a.severity === 'info' && !a.resolved).length
        };
        
        Object.entries(counts).forEach(([severity, count]) => {
            document.getElementById(`${severity}-count`).textContent = count;
        });
    }
    
    getRelativeTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return date.toLocaleString();
    }
    
    acknowledgeAlert(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            alert.acknowledged = true;
            alert.acknowledgedBy = 'current_user';
            alert.acknowledgedAt = new Date();
            this.updateDisplay();
        }
    }
    
    showNotification(alert) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Critical Alert', {
                body: alert.message,
                icon: '/images/alert-icon.png',
                tag: alert.id
            });
        }
    }
}

const alertDashboard = new AlertDashboard();
</script>
```

## Log Analysis / 로그 분석

### 1. Log Aggregation / 로그 집계
```javascript
// Centralized log aggregation and analysis
class LogAggregator {
    constructor() {
        this.logs = [];
        this.patterns = {
            error: /ERROR|EXCEPTION|FAIL/i,
            warning: /WARN|CAUTION/i,
            performance: /SLOW|TIMEOUT|LATENCY/i,
            security: /UNAUTHORIZED|FORBIDDEN|DENIED/i
        };
        
        this.analytics = {
            errorFrequency: {},
            performanceIssues: [],
            securityEvents: [],
            topErrors: []
        };
    }
    
    ingestLog(logEntry) {
        // Parse log entry
        const parsed = this.parseLogEntry(logEntry);
        
        // Store parsed log
        this.logs.push(parsed);
        
        // Real-time analysis
        this.analyzeLog(parsed);
        
        // Keep only recent logs (last 24 hours)
        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        this.logs = this.logs.filter(log => log.timestamp > cutoff);
    }
    
    parseLogEntry(logEntry) {
        // Common log format: [timestamp] [level] [component] message
        const regex = /\[([^\]]+)\]\s*\[([^\]]+)\]\s*\[([^\]]+)\]\s*(.*)/;
        const match = logEntry.match(regex);
        
        if (match) {
            return {
                timestamp: new Date(match[1]).getTime(),
                level: match[2],
                component: match[3],
                message: match[4],
                raw: logEntry
            };
        }
        
        // Fallback for non-standard format
        return {
            timestamp: Date.now(),
            level: 'UNKNOWN',
            component: 'UNKNOWN',
            message: logEntry,
            raw: logEntry
        };
    }
    
    analyzeLog(log) {
        // Check for error patterns
        if (this.patterns.error.test(log.message)) {
            this.trackError(log);
        }
        
        // Check for performance issues
        if (this.patterns.performance.test(log.message)) {
            this.trackPerformanceIssue(log);
        }
        
        // Check for security events
        if (this.patterns.security.test(log.message)) {
            this.trackSecurityEvent(log);
        }
    }
    
    trackError(log) {
        // Extract error type
        const errorMatch = log.message.match(/Error:\s*([^:]+)/i);
        const errorType = errorMatch ? errorMatch[1].trim() : 'Unknown Error';
        
        // Track frequency
        if (!this.analytics.errorFrequency[errorType]) {
            this.analytics.errorFrequency[errorType] = {
                count: 0,
                firstSeen: log.timestamp,
                lastSeen: log.timestamp,
                samples: []
            };
        }
        
        const errorData = this.analytics.errorFrequency[errorType];
        errorData.count++;
        errorData.lastSeen = log.timestamp;
        
        // Keep sample logs
        if (errorData.samples.length < 5) {
            errorData.samples.push(log);
        }
    }
    
    generateAnalyticsReport() {
        const report = {
            timeRange: {
                start: this.logs.length > 0 ? new Date(Math.min(...this.logs.map(l => l.timestamp))) : null,
                end: new Date()
            },
            totalLogs: this.logs.length,
            errorSummary: this.getErrorSummary(),
            performanceSummary: this.getPerformanceSummary(),
            securitySummary: this.getSecuritySummary(),
            componentHealth: this.getComponentHealth()
        };
        
        return report;
    }
    
    getErrorSummary() {
        const errors = Object.entries(this.analytics.errorFrequency)
            .map(([type, data]) => ({
                type,
                count: data.count,
                trend: this.calculateTrend(data),
                severity: this.calculateSeverity(data)
            }))
            .sort((a, b) => b.count - a.count);
        
        return {
            totalErrors: errors.reduce((sum, e) => sum + e.count, 0),
            uniqueErrors: errors.length,
            topErrors: errors.slice(0, 10),
            criticalErrors: errors.filter(e => e.severity === 'critical')
        };
    }
    
    getComponentHealth() {
        const componentLogs = {};
        
        // Group logs by component
        this.logs.forEach(log => {
            if (!componentLogs[log.component]) {
                componentLogs[log.component] = {
                    total: 0,
                    errors: 0,
                    warnings: 0
                };
            }
            
            componentLogs[log.component].total++;
            
            if (log.level === 'ERROR') {
                componentLogs[log.component].errors++;
            } else if (log.level === 'WARN') {
                componentLogs[log.component].warnings++;
            }
        });
        
        // Calculate health score
        return Object.entries(componentLogs).map(([component, stats]) => ({
            component,
            healthScore: this.calculateHealthScore(stats),
            stats
        }));
    }
    
    calculateHealthScore(stats) {
        if (stats.total === 0) return 100;
        
        const errorWeight = 10;
        const warningWeight = 2;
        
        const issues = (stats.errors * errorWeight) + (stats.warnings * warningWeight);
        const score = Math.max(0, 100 - (issues / stats.total * 100));
        
        return Math.round(score);
    }
}
```

### 2. Log Visualization / 로그 시각화
```javascript
// Log pattern visualization
class LogVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
        this.initChart();
    }
    
    initChart() {
        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Errors',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)'
                    },
                    {
                        label: 'Warnings',
                        data: [],
                        borderColor: 'rgb(255, 206, 86)',
                        backgroundColor: 'rgba(255, 206, 86, 0.1)'
                    },
                    {
                        label: 'Info',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Log Level Distribution Over Time'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Count'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    updateData(logData) {
        // Group logs by time bucket and level
        const buckets = this.createTimeBuckets(logData);
        
        // Update chart data
        this.chart.data.labels = Object.keys(buckets);
        
        this.chart.data.datasets[0].data = Object.values(buckets).map(b => b.errors);
        this.chart.data.datasets[1].data = Object.values(buckets).map(b => b.warnings);
        this.chart.data.datasets[2].data = Object.values(buckets).map(b => b.info);
        
        this.chart.update();
    }
    
    createTimeBuckets(logs, bucketSize = 60000) { // 1 minute buckets
        const buckets = {};
        
        logs.forEach(log => {
            const bucketTime = Math.floor(log.timestamp / bucketSize) * bucketSize;
            
            if (!buckets[bucketTime]) {
                buckets[bucketTime] = {
                    errors: 0,
                    warnings: 0,
                    info: 0
                };
            }
            
            switch (log.level) {
                case 'ERROR':
                    buckets[bucketTime].errors++;
                    break;
                case 'WARN':
                    buckets[bucketTime].warnings++;
                    break;
                default:
                    buckets[bucketTime].info++;
            }
        });
        
        return buckets;
    }
    
    createPatternAnalysis(logs) {
        // Analyze log patterns
        const patterns = {};
        
        logs.forEach(log => {
            // Extract patterns (e.g., error codes, URLs, etc.)
            const errorCode = log.message.match(/\b[A-Z]+_[A-Z_]+\b/);
            if (errorCode) {
                patterns[errorCode[0]] = (patterns[errorCode[0]] || 0) + 1;
            }
        });
        
        // Create pattern chart
        this.createPatternChart(patterns);
    }
}
```

## Custom Dashboards / 커스텀 대시보드

### 1. Dashboard Builder / 대시보드 빌더
```javascript
// Drag-and-drop dashboard builder
class DashboardBuilder {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.widgets = [];
        this.layout = [];
        this.init();
    }
    
    init() {
        this.setupDragDrop();
        this.loadAvailableWidgets();
        this.loadSavedLayout();
    }
    
    loadAvailableWidgets() {
        this.availableWidgets = {
            'metric-card': {
                name: 'Metric Card',
                icon: '📊',
                defaultConfig: {
                    metric: 'responseTime',
                    title: 'Response Time',
                    unit: 'ms'
                }
            },
            'line-chart': {
                name: 'Line Chart',
                icon: '📈',
                defaultConfig: {
                    metrics: ['cpuUsage'],
                    timeRange: '1h'
                }
            },
            'pie-chart': {
                name: 'Pie Chart',
                icon: '🥧',
                defaultConfig: {
                    metric: 'requestsByEndpoint',
                    title: 'API Usage'
                }
            },
            'alert-list': {
                name: 'Alert List',
                icon: '🚨',
                defaultConfig: {
                    severity: 'all',
                    limit: 10
                }
            },
            'log-viewer': {
                name: 'Log Viewer',
                icon: '📝',
                defaultConfig: {
                    level: 'all',
                    tail: true
                }
            },
            'status-grid': {
                name: 'Status Grid',
                icon: '🟢',
                defaultConfig: {
                    services: ['api', 'scraper', 'database']
                }
            }
        };
    }
    
    createWidget(type, config = {}) {
        const widgetDef = this.availableWidgets[type];
        if (!widgetDef) return null;
        
        const widget = {
            id: `widget-${Date.now()}`,
            type,
            config: { ...widgetDef.defaultConfig, ...config },
            position: { x: 0, y: 0 },
            size: { width: 4, height: 3 }
        };
        
        const element = this.renderWidget(widget);
        this.widgets.push({ widget, element });
        
        return widget;
    }
    
    renderWidget(widget) {
        const div = document.createElement('div');
        div.className = 'dashboard-widget';
        div.id = widget.id;
        div.style.gridColumn = `span ${widget.size.width}`;
        div.style.gridRow = `span ${widget.size.height}`;
        
        div.innerHTML = `
            <div class="widget-header">
                <span class="widget-title">${widget.config.title || widget.type}</span>
                <div class="widget-controls">
                    <button onclick="dashboardBuilder.configureWidget('${widget.id}')">⚙️</button>
                    <button onclick="dashboardBuilder.removeWidget('${widget.id}')">❌</button>
                </div>
            </div>
            <div class="widget-content" id="${widget.id}-content">
                <!-- Widget content will be rendered here -->
            </div>
        `;
        
        // Render widget content based on type
        this.renderWidgetContent(widget, div.querySelector('.widget-content'));
        
        return div;
    }
    
    renderWidgetContent(widget, container) {
        switch (widget.type) {
            case 'metric-card':
                this.renderMetricCard(widget, container);
                break;
            case 'line-chart':
                this.renderLineChart(widget, container);
                break;
            case 'pie-chart':
                this.renderPieChart(widget, container);
                break;
            case 'alert-list':
                this.renderAlertList(widget, container);
                break;
            case 'log-viewer':
                this.renderLogViewer(widget, container);
                break;
            case 'status-grid':
                this.renderStatusGrid(widget, container);
                break;
        }
    }
    
    renderMetricCard(widget, container) {
        const updateMetric = () => {
            fetch(`/api/metrics/${widget.config.metric}`)
                .then(res => res.json())
                .then(data => {
                    container.innerHTML = `
                        <div class="metric-value">
                            ${data.value}${widget.config.unit}
                        </div>
                        <div class="metric-trend ${data.trend}">
                            ${data.trend === 'up' ? '↑' : '↓'} ${data.change}%
                        </div>
                    `;
                });
        };
        
        updateMetric();
        setInterval(updateMetric, 5000);
    }
    
    saveLayout() {
        const layout = this.widgets.map(({ widget }) => ({
            type: widget.type,
            config: widget.config,
            position: widget.position,
            size: widget.size
        }));
        
        localStorage.setItem('dashboardLayout', JSON.stringify(layout));
    }
    
    loadSavedLayout() {
        const saved = localStorage.getItem('dashboardLayout');
        if (saved) {
            const layout = JSON.parse(saved);
            layout.forEach(widgetData => {
                this.createWidget(widgetData.type, widgetData.config);
            });
        }
    }
}
```

### 2. Custom Metrics / 커스텀 지표
```javascript
// Custom metric definition system
class CustomMetrics {
    constructor() {
        this.metrics = {};
        this.calculations = {};
    }
    
    defineMetric(name, config) {
        this.metrics[name] = {
            name,
            displayName: config.displayName,
            unit: config.unit,
            type: config.type, // gauge, counter, histogram
            calculation: config.calculation,
            sources: config.sources,
            aggregation: config.aggregation || 'average'
        };
        
        // Compile calculation function
        if (config.calculation) {
            this.calculations[name] = this.compileCalculation(config.calculation);
        }
    }
    
    compileCalculation(formula) {
        // Simple formula parser
        // Supports: +, -, *, /, (), and metric references
        return new Function('metrics', `
            with (metrics) {
                return ${formula};
            }
        `);
    }
    
    calculateMetric(name, data) {
        const metric = this.metrics[name];
        if (!metric) return null;
        
        if (metric.calculation) {
            try {
                return this.calculations[name](data);
            } catch (error) {
                console.error(`Error calculating metric ${name}:`, error);
                return null;
            }
        }
        
        // Simple aggregation
        const values = metric.sources.map(source => data[source]).filter(v => v != null);
        
        switch (metric.aggregation) {
            case 'sum':
                return values.reduce((a, b) => a + b, 0);
            case 'average':
                return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
            case 'max':
                return Math.max(...values);
            case 'min':
                return Math.min(...values);
            default:
                return values[0];
        }
    }
    
    // Example custom metrics
    setupDefaultMetrics() {
        // Efficiency metric
        this.defineMetric('efficiency', {
            displayName: 'System Efficiency',
            unit: '%',
            type: 'gauge',
            calculation: '(successfulRequests / totalRequests) * 100',
            sources: ['successfulRequests', 'totalRequests']
        });
        
        // Cost per request
        this.defineMetric('costPerRequest', {
            displayName: 'Cost per Request',
            unit: '$',
            type: 'gauge',
            calculation: 'totalCost / totalRequests',
            sources: ['totalCost', 'totalRequests']
        });
        
        // Composite health score
        this.defineMetric('healthScore', {
            displayName: 'Overall Health Score',
            unit: '',
            type: 'gauge',
            calculation: `
                (availability * 0.3 + 
                 (100 - errorRate) * 0.3 + 
                 (100 - (responseTime / 10)) * 0.2 + 
                 scrapingSuccessRate * 0.2)
            `,
            sources: ['availability', 'errorRate', 'responseTime', 'scrapingSuccessRate']
        });
    }
}
```

## API Monitoring / API 모니터링

### 1. Endpoint Monitoring / 엔드포인트 모니터링
```javascript
// Comprehensive API endpoint monitoring
class APIMonitor {
    constructor() {
        this.endpoints = [
            {
                name: 'Health Check',
                url: '/api/health',
                method: 'GET',
                expectedStatus: 200,
                timeout: 5000,
                critical: true
            },
            {
                name: 'Get Latest Scraped',
                url: '/api/get-latest-scraped',
                method: 'GET',
                expectedStatus: 200,
                timeout: 10000,
                critical: true
            },
            {
                name: 'Trigger Scraping',
                url: '/api/trigger-scraping',
                method: 'POST',
                expectedStatus: [200, 202],
                timeout: 30000,
                critical: false
            }
        ];
        
        this.results = new Map();
        this.history = new Map();
    }
    
    async monitorAll() {
        const results = await Promise.all(
            this.endpoints.map(endpoint => this.monitorEndpoint(endpoint))
        );
        
        this.updateDashboard(results);
        this.checkSLAs(results);
        
        return results;
    }
    
    async monitorEndpoint(endpoint) {
        const startTime = performance.now();
        const result = {
            endpoint: endpoint.name,
            timestamp: new Date(),
            success: false,
            responseTime: null,
            statusCode: null,
            error: null
        };
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), endpoint.timeout);
            
            const response = await fetch(endpoint.url, {
                method: endpoint.method,
                signal: controller.signal,
                headers: {
                    'X-Monitor': 'true'
                }
            });
            
            clearTimeout(timeoutId);
            
            result.responseTime = performance.now() - startTime;
            result.statusCode = response.status;
            
            const expectedStatuses = Array.isArray(endpoint.expectedStatus) 
                ? endpoint.expectedStatus 
                : [endpoint.expectedStatus];
            
            result.success = expectedStatuses.includes(response.status);
            
            // Additional checks
            if (endpoint.validateResponse) {
                const data = await response.json();
                result.validationResult = endpoint.validateResponse(data);
                result.success = result.success && result.validationResult.valid;
            }
            
        } catch (error) {
            result.error = error.message;
            result.responseTime = performance.now() - startTime;
            
            if (error.name === 'AbortError') {
                result.error = 'Timeout';
            }
        }
        
        // Store result
        this.results.set(endpoint.name, result);
        
        // Add to history
        if (!this.history.has(endpoint.name)) {
            this.history.set(endpoint.name, []);
        }
        this.history.get(endpoint.name).push(result);
        
        // Keep only last 1000 results
        const history = this.history.get(endpoint.name);
        if (history.length > 1000) {
            history.shift();
        }
        
        return result;
    }
    
    calculateSLA(endpointName, timeWindow = 86400000) { // 24 hours
        const history = this.history.get(endpointName) || [];
        const cutoff = Date.now() - timeWindow;
        
        const relevantResults = history.filter(r => r.timestamp > cutoff);
        
        if (relevantResults.length === 0) {
            return { availability: 0, avgResponseTime: 0, errorRate: 0 };
        }
        
        const successful = relevantResults.filter(r => r.success).length;
        const availability = (successful / relevantResults.length) * 100;
        
        const responseTimes = relevantResults
            .filter(r => r.responseTime !== null)
            .map(r => r.responseTime);
        
        const avgResponseTime = responseTimes.length > 0
            ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
            : 0;
        
        const errors = relevantResults.filter(r => r.error).length;
        const errorRate = (errors / relevantResults.length) * 100;
        
        return {
            availability: availability.toFixed(2),
            avgResponseTime: avgResponseTime.toFixed(0),
            errorRate: errorRate.toFixed(2),
            totalChecks: relevantResults.length
        };
    }
    
    updateDashboard(results) {
        const container = document.getElementById('api-monitor');
        if (!container) return;
        
        container.innerHTML = `
            <div class="api-monitor-grid">
                ${results.map(result => `
                    <div class="api-endpoint-card ${result.success ? 'success' : 'failure'}">
                        <div class="endpoint-name">${result.endpoint}</div>
                        <div class="endpoint-status">
                            ${result.success ? '✅' : '❌'} 
                            ${result.statusCode || 'N/A'}
                        </div>
                        <div class="endpoint-time">
                            ${result.responseTime ? `${result.responseTime.toFixed(0)}ms` : 'N/A'}
                        </div>
                        ${result.error ? `<div class="endpoint-error">${result.error}</div>` : ''}
                        <div class="endpoint-sla">
                            ${this.renderSLA(result.endpoint)}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    renderSLA(endpointName) {
        const sla = this.calculateSLA(endpointName);
        return `
            <small>
                24h: ${sla.availability}% uptime | 
                ${sla.avgResponseTime}ms avg
            </small>
        `;
    }
}
```

### 2. API Usage Analytics / API 사용 분석
```javascript
// API usage tracking and analytics
class APIUsageAnalytics {
    constructor() {
        this.usage = {
            byEndpoint: {},
            byUser: {},
            byHour: new Array(24).fill(0),
            byDay: new Array(7).fill(0)
        };
        
        this.quotas = {
            '/api/trigger-scraping': { limit: 100, window: 86400000 },
            '/api/send-only': { limit: 50, window: 3600000 }
        };
    }
    
    trackRequest(request) {
        const endpoint = request.url.pathname;
        const user = request.headers.get('x-api-key') || 'anonymous';
        const hour = new Date().getHours();
        const day = new Date().getDay();
        
        // Track by endpoint
        if (!this.usage.byEndpoint[endpoint]) {
            this.usage.byEndpoint[endpoint] = {
                count: 0,
                totalTime: 0,
                errors: 0
            };
        }
        
        this.usage.byEndpoint[endpoint].count++;
        
        // Track by user
        if (!this.usage.byUser[user]) {
            this.usage.byUser[user] = {
                requests: 0,
                endpoints: {}
            };
        }
        
        this.usage.byUser[user].requests++;
        
        // Track by time
        this.usage.byHour[hour]++;
        this.usage.byDay[day]++;
        
        // Check quotas
        this.checkQuota(endpoint, user);
    }
    
    checkQuota(endpoint, user) {
        const quota = this.quotas[endpoint];
        if (!quota) return { allowed: true };
        
        const key = `${endpoint}:${user}`;
        const now = Date.now();
        
        // Get usage in window
        const windowStart = now - quota.window;
        const usage = this.getUsageInWindow(key, windowStart, now);
        
        if (usage >= quota.limit) {
            return {
                allowed: false,
                limit: quota.limit,
                used: usage,
                resetAt: windowStart + quota.window
            };
        }
        
        return {
            allowed: true,
            limit: quota.limit,
            used: usage,
            remaining: quota.limit - usage
        };
    }
    
    generateUsageReport() {
        const report = {
            summary: {
                totalRequests: Object.values(this.usage.byEndpoint)
                    .reduce((sum, e) => sum + e.count, 0),
                uniqueUsers: Object.keys(this.usage.byUser).length,
                busiestHour: this.usage.byHour.indexOf(Math.max(...this.usage.byHour)),
                busiestDay: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][
                    this.usage.byDay.indexOf(Math.max(...this.usage.byDay))
                ]
            },
            topEndpoints: this.getTopEndpoints(),
            topUsers: this.getTopUsers(),
            hourlyDistribution: this.usage.byHour,
            quotaUsage: this.getQuotaUsage()
        };
        
        return report;
    }
    
    getTopEndpoints(limit = 10) {
        return Object.entries(this.usage.byEndpoint)
            .map(([endpoint, data]) => ({
                endpoint,
                requests: data.count,
                avgTime: data.totalTime / data.count,
                errorRate: (data.errors / data.count) * 100
            }))
            .sort((a, b) => b.requests - a.requests)
            .slice(0, limit);
    }
    
    visualizeUsage() {
        // Create usage heatmap
        const heatmapData = [];
        
        for (let day = 0; day < 7; day++) {
            for (let hour = 0; hour < 24; hour++) {
                heatmapData.push({
                    day,
                    hour,
                    value: this.getUsageForDayHour(day, hour)
                });
            }
        }
        
        this.renderHeatmap(heatmapData);
    }
}
```

## Scraping Analytics / 스크래핑 분석

### 1. Scraping Performance Analytics / 스크래핑 성능 분석
```javascript
// Detailed scraping analytics
class ScrapingAnalytics {
    constructor() {
        this.sessions = [];
        this.siteStats = {};
        this.articleStats = {
            total: 0,
            byGroup: {},
            bySite: {},
            byMethod: {}
        };
    }
    
    startSession(config) {
        const session = {
            id: `session_${Date.now()}`,
            startTime: new Date(),
            config,
            sites: [],
            articles: [],
            errors: [],
            status: 'running'
        };
        
        this.sessions.push(session);
        return session.id;
    }
    
    updateSession(sessionId, update) {
        const session = this.sessions.find(s => s.id === sessionId);
        if (!session) return;
        
        Object.assign(session, update);
        
        if (update.status === 'completed' || update.status === 'failed') {
            session.endTime = new Date();
            session.duration = session.endTime - session.startTime;
            
            // Calculate statistics
            this.calculateSessionStats(session);
        }
    }
    
    recordSiteResult(sessionId, site, result) {
        const session = this.sessions.find(s => s.id === sessionId);
        if (!session) return;
        
        const siteResult = {
            site: site.name,
            startTime: result.startTime,
            endTime: result.endTime,
            duration: result.endTime - result.startTime,
            articlesFound: result.articles.length,
            errors: result.errors,
            status: result.status
        };
        
        session.sites.push(siteResult);
        
        // Update site statistics
        this.updateSiteStats(site.name, siteResult);
    }
    
    updateSiteStats(siteName, result) {
        if (!this.siteStats[siteName]) {
            this.siteStats[siteName] = {
                totalScrapes: 0,
                successfulScrapes: 0,
                totalArticles: 0,
                totalDuration: 0,
                errors: []
            };
        }
        
        const stats = this.siteStats[siteName];
        stats.totalScrapes++;
        
        if (result.status === 'success') {
            stats.successfulScrapes++;
            stats.totalArticles += result.articlesFound;
        }
        
        stats.totalDuration += result.duration;
        
        if (result.errors && result.errors.length > 0) {
            stats.errors.push(...result.errors);
        }
    }
    
    generateAnalyticsReport(timeRange = 'day') {
        const cutoff = this.getTimeRangeCutoff(timeRange);
        const recentSessions = this.sessions.filter(s => s.startTime > cutoff);
        
        const report = {
            timeRange,
            summary: this.generateSummary(recentSessions),
            sitePerformance: this.analyzeSitePerformance(recentSessions),
            articleDistribution: this.analyzeArticleDistribution(recentSessions),
            errorAnalysis: this.analyzeErrors(recentSessions),
            trends: this.analyzeTrends(recentSessions)
        };
        
        return report;
    }
    
    generateSummary(sessions) {
        const completed = sessions.filter(s => s.status === 'completed');
        
        return {
            totalSessions: sessions.length,
            successfulSessions: completed.length,
            successRate: (completed.length / sessions.length * 100).toFixed(2) + '%',
            totalArticles: sessions.reduce((sum, s) => sum + s.articles.length, 0),
            avgArticlesPerSession: (sessions.reduce((sum, s) => sum + s.articles.length, 0) / sessions.length).toFixed(1),
            avgDuration: this.calculateAvgDuration(completed)
        };
    }
    
    analyzeSitePerformance(sessions) {
        const sitePerf = {};
        
        sessions.forEach(session => {
            session.sites.forEach(site => {
                if (!sitePerf[site.site]) {
                    sitePerf[site.site] = {
                        attempts: 0,
                        successes: 0,
                        articles: 0,
                        avgDuration: 0,
                        durations: []
                    };
                }
                
                const perf = sitePerf[site.site];
                perf.attempts++;
                
                if (site.status === 'success') {
                    perf.successes++;
                    perf.articles += site.articlesFound;
                }
                
                perf.durations.push(site.duration);
            });
        });
        
        // Calculate averages
        Object.values(sitePerf).forEach(perf => {
            perf.successRate = (perf.successes / perf.attempts * 100).toFixed(2) + '%';
            perf.avgArticles = (perf.articles / perf.successes).toFixed(1);
            perf.avgDuration = (perf.durations.reduce((a, b) => a + b, 0) / perf.durations.length / 1000).toFixed(2) + 's';
            delete perf.durations; // Remove raw data
        });
        
        return sitePerf;
    }
    
    visualizeAnalytics() {
        // Create comprehensive dashboard
        const dashboard = document.getElementById('scraping-analytics');
        
        dashboard.innerHTML = `
            <div class="analytics-grid">
                <div class="analytics-card">
                    <h3>Session Success Rate</h3>
                    <canvas id="success-rate-chart"></canvas>
                </div>
                <div class="analytics-card">
                    <h3>Articles by Site</h3>
                    <canvas id="articles-by-site"></canvas>
                </div>
                <div class="analytics-card">
                    <h3>Scraping Duration Trend</h3>
                    <canvas id="duration-trend"></canvas>
                </div>
                <div class="analytics-card">
                    <h3>Error Distribution</h3>
                    <canvas id="error-distribution"></canvas>
                </div>
            </div>
        `;
        
        this.renderCharts();
    }
}
```

### 2. Content Quality Analytics / 콘텐츠 품질 분석
```javascript
// Analyze quality of scraped content
class ContentQualityAnalyzer {
    constructor() {
        this.qualityMetrics = {
            completeness: 0,
            accuracy: 0,
            freshness: 0,
            diversity: 0
        };
    }
    
    analyzeArticle(article) {
        const scores = {
            completeness: this.scoreCompleteness(article),
            titleQuality: this.scoreTitleQuality(article),
            summaryQuality: this.scoreSummaryQuality(article),
            metadata: this.scoreMetadata(article),
            freshness: this.scoreFreshness(article)
        };
        
        const overallScore = Object.values(scores).reduce((a, b) => a + b, 0) / Object.keys(scores).length;
        
        return {
            articleId: article.id,
            scores,
            overallScore,
            issues: this.identifyIssues(article, scores)
        };
    }
    
    scoreCompleteness(article) {
        const requiredFields = ['title', 'url', 'summary', 'source', 'publishDate'];
        const presentFields = requiredFields.filter(field => article[field] && article[field].trim());
        
        return (presentFields.length / requiredFields.length) * 100;
    }
    
    scoreTitleQuality(article) {
        if (!article.title) return 0;
        
        let score = 100;
        
        // Length check
        if (article.title.length < 10) score -= 20;
        if (article.title.length > 200) score -= 10;
        
        // Check for truncation
        if (article.title.endsWith('...')) score -= 10;
        
        // Check for special characters/encoding issues
        if (/[�]/g.test(article.title)) score -= 30;
        
        return Math.max(0, score);
    }
    
    scoreSummaryQuality(article) {
        if (!article.summary) return 0;
        
        let score = 100;
        
        // Length check
        if (article.summary.length < 50) score -= 30;
        if (article.summary.length > 1000) score -= 10;
        
        // Check for repetition with title
        if (article.summary === article.title) score -= 50;
        
        // Language quality (simple check)
        const sentences = article.summary.split(/[.!?]+/).filter(s => s.trim());
        if (sentences.length < 2) score -= 20;
        
        return Math.max(0, score);
    }
    
    generateQualityReport(articles) {
        const analyses = articles.map(article => this.analyzeArticle(article));
        
        const report = {
            totalArticles: articles.length,
            averageScore: analyses.reduce((sum, a) => sum + a.overallScore, 0) / analyses.length,
            scoreDistribution: this.getScoreDistribution(analyses),
            commonIssues: this.aggregateIssues(analyses),
            recommendations: this.generateRecommendations(analyses)
        };
        
        return report;
    }
    
    getScoreDistribution(analyses) {
        const bins = {
            excellent: 0,  // 90-100
            good: 0,       // 70-89
            fair: 0,       // 50-69
            poor: 0        // 0-49
        };
        
        analyses.forEach(analysis => {
            if (analysis.overallScore >= 90) bins.excellent++;
            else if (analysis.overallScore >= 70) bins.good++;
            else if (analysis.overallScore >= 50) bins.fair++;
            else bins.poor++;
        });
        
        return bins;
    }
}
```

## Reporting / 보고서

### 1. Automated Report Generation / 자동 보고서 생성
```javascript
// Comprehensive reporting system
class ReportGenerator {
    constructor() {
        this.templates = {
            daily: this.dailyReportTemplate,
            weekly: this.weeklyReportTemplate,
            monthly: this.monthlyReportTemplate,
            incident: this.incidentReportTemplate
        };
    }
    
    async generateReport(type, options = {}) {
        const template = this.templates[type];
        if (!template) throw new Error(`Unknown report type: ${type}`);
        
        // Gather data
        const data = await this.gatherReportData(type, options);
        
        // Generate report
        const report = template.call(this, data);
        
        // Save report
        const filename = this.saveReport(type, report);
        
        // Distribute report
        await this.distributeReport(type, filename, options.recipients);
        
        return filename;
    }
    
    async gatherReportData(type, options) {
        const data = {
            period: this.getReportPeriod(type, options),
            metrics: await this.getMetrics(options.period),
            incidents: await this.getIncidents(options.period),
            performance: await this.getPerformanceData(options.period),
            availability: await this.getAvailabilityData(options.period)
        };
        
        return data;
    }
    
    dailyReportTemplate(data) {
        return `
# Daily Operations Report
**Date**: ${data.period.date}
**Generated**: ${new Date().toISOString()}

## Executive Summary
- **Availability**: ${data.availability.percentage}%
- **Total Requests**: ${data.metrics.totalRequests.toLocaleString()}
- **Articles Scraped**: ${data.metrics.articlesScraped}
- **Incidents**: ${data.incidents.length}

## System Performance
### Response Times
- Average: ${data.performance.avgResponseTime}ms
- 95th Percentile: ${data.performance.p95ResponseTime}ms
- 99th Percentile: ${data.performance.p99ResponseTime}ms

### Error Rates
- Overall: ${data.performance.errorRate}%
- By Endpoint:
${Object.entries(data.performance.errorsByEndpoint)
    .map(([endpoint, rate]) => `  - ${endpoint}: ${rate}%`)
    .join('\n')}

## Scraping Summary
- Sessions Run: ${data.metrics.scrapingSessions}
- Success Rate: ${data.metrics.scrapingSuccessRate}%
- Articles by Category:
${Object.entries(data.metrics.articlesByCategory)
    .map(([category, count]) => `  - ${category}: ${count}`)
    .join('\n')}

## Incidents
${data.incidents.length === 0 ? 'No incidents reported.' : 
  data.incidents.map(incident => `
### ${incident.title}
- **Time**: ${incident.time}
- **Duration**: ${incident.duration}
- **Impact**: ${incident.impact}
- **Resolution**: ${incident.resolution}
`).join('\n')}

## Recommendations
${this.generateRecommendations(data)}

---
*This report was automatically generated by Singapore News Scraper Monitoring System*
        `;
    }
    
    generateRecommendations(data) {
        const recommendations = [];
        
        // Performance recommendations
        if (data.performance.avgResponseTime > 500) {
            recommendations.push('- Consider implementing caching to reduce response times');
        }
        
        if (data.performance.errorRate > 1) {
            recommendations.push('- Investigate error patterns and implement fixes');
        }
        
        // Availability recommendations
        if (data.availability.percentage < 99.9) {
            recommendations.push('- Review system reliability and implement redundancy');
        }
        
        // Scraping recommendations
        if (data.metrics.scrapingSuccessRate < 90) {
            recommendations.push('- Update scraping selectors for failing sites');
        }
        
        return recommendations.length > 0 
            ? recommendations.join('\n') 
            : '- System operating within normal parameters';
    }
    
    async distributeReport(type, filename, recipients = []) {
        // Default recipients by report type
        const defaultRecipients = {
            daily: ['ops-team@example.com'],
            weekly: ['management@example.com'],
            monthly: ['executives@example.com'],
            incident: ['on-call@example.com', 'management@example.com']
        };
        
        const allRecipients = [...new Set([...recipients, ...defaultRecipients[type]])];
        
        // Send via email
        for (const recipient of allRecipients) {
            await this.emailReport(recipient, type, filename);
        }
        
        // Post to Slack
        if (process.env.SLACK_WEBHOOK_URL) {
            await this.postToSlack(type, filename);
        }
        
        // Archive to S3
        if (process.env.S3_BUCKET) {
            await this.archiveToS3(filename);
        }
    }
}
```

### 2. Interactive Dashboard Reports / 대화형 대시보드 보고서
```html
<!-- Interactive report viewer -->
<div id="report-viewer" class="report-container">
    <div class="report-header">
        <h2>System Reports</h2>
        <div class="report-controls">
            <select id="report-type">
                <option value="daily">Daily Report</option>
                <option value="weekly">Weekly Report</option>
                <option value="monthly">Monthly Report</option>
                <option value="custom">Custom Range</option>
            </select>
            <input type="date" id="report-date" />
            <button onclick="generateReport()">Generate Report</button>
            <button onclick="exportReport()">Export PDF</button>
        </div>
    </div>
    
    <div class="report-content" id="report-content">
        <!-- Report will be rendered here -->
    </div>
    
    <div class="report-charts">
        <div class="chart-grid">
            <div class="chart-container">
                <canvas id="performance-chart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="availability-chart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="scraping-chart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="errors-chart"></canvas>
            </div>
        </div>
    </div>
</div>

<script>
class InteractiveReportViewer {
    constructor() {
        this.currentReport = null;
        this.charts = {};
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadDefaultReport();
    }
    
    async generateReport() {
        const type = document.getElementById('report-type').value;
        const date = document.getElementById('report-date').value;
        
        // Show loading state
        this.showLoading();
        
        try {
            const response = await fetch('/api/generate-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, date })
            });
            
            const report = await response.json();
            this.currentReport = report;
            this.renderReport(report);
            this.updateCharts(report);
            
        } catch (error) {
            this.showError('Failed to generate report: ' + error.message);
        }
    }
    
    renderReport(report) {
        const content = document.getElementById('report-content');
        
        // Convert markdown to HTML
        const html = this.markdownToHTML(report.content);
        
        content.innerHTML = `
            <div class="report-document">
                <div class="report-metadata">
                    <span>Generated: ${new Date(report.generated).toLocaleString()}</span>
                    <span>Period: ${report.period.start} to ${report.period.end}</span>
                </div>
                <div class="report-body">
                    ${html}
                </div>
            </div>
        `;
        
        // Add interactive elements
        this.addInteractivity();
    }
    
    updateCharts(report) {
        // Update performance chart
        this.updatePerformanceChart(report.data.performance);
        
        // Update availability chart
        this.updateAvailabilityChart(report.data.availability);
        
        // Update scraping chart
        this.updateScrapingChart(report.data.scraping);
        
        // Update errors chart
        this.updateErrorsChart(report.data.errors);
    }
    
    async exportReport() {
        if (!this.currentReport) {
            alert('Please generate a report first');
            return;
        }
        
        // Generate PDF
        const pdf = new jsPDF();
        const content = document.getElementById('report-content');
        
        // Add content to PDF
        pdf.html(content, {
            callback: function (pdf) {
                pdf.save(`report_${new Date().toISOString().split('T')[0]}.pdf`);
            }
        });
    }
    
    addInteractivity() {
        // Add click handlers for drill-down
        document.querySelectorAll('.metric-value').forEach(element => {
            element.addEventListener('click', (e) => {
                const metric = e.target.dataset.metric;
                this.showMetricDetails(metric);
            });
        });
        
        // Add tooltips
        tippy('[data-tooltip]', {
            content: (reference) => reference.getAttribute('data-tooltip'),
            placement: 'top'
        });
    }
}

const reportViewer = new InteractiveReportViewer();
</script>
```

---
*Effective monitoring is the key to maintaining a healthy system. Use these tools to stay ahead of issues.*

*효과적인 모니터링은 건강한 시스템을 유지하는 열쇠입니다. 이러한 도구를 사용하여 문제를 미리 파악하세요.*

*Last Updated: January 25, 2025*