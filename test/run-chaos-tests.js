#!/usr/bin/env node

// Chaos Engineering Test Suite for Node.js
const https = require('https');
const http = require('http');

let chaosResults = {
    total: 0,
    passed: 0,
    failed: 0,
    warnings: 0,
    details: []
};

function logChaosTest(testName, status, message = '', data = null) {
    chaosResults.total++;
    const result = { testName, status, message, timestamp: new Date().toISOString(), data };
    
    if (status === 'PASS') {
        chaosResults.passed++;
        console.log(`✅ ${testName}: ${message}`);
    } else if (status === 'WARN') {
        chaosResults.warnings++;
        console.log(`⚠️ ${testName}: ${message}`);
    } else {
        chaosResults.failed++;
        console.log(`❌ ${testName}: ${message}`);
    }
    
    chaosResults.details.push(result);
}

function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https:') ? https : http;
        const startTime = Date.now();
        
        const req = client.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                const endTime = Date.now();
                const responseTime = endTime - startTime;
                
                try {
                    const jsonData = JSON.parse(data);
                    resolve({ 
                        status: res.statusCode, 
                        data: jsonData, 
                        raw: data, 
                        responseTime,
                        headers: res.headers 
                    });
                } catch (e) {
                    resolve({ 
                        status: res.statusCode, 
                        data: null, 
                        raw: data, 
                        responseTime,
                        headers: res.headers 
                    });
                }
            });
        });
        
        req.on('error', (error) => {
            const endTime = Date.now();
            reject({ ...error, responseTime: endTime - startTime });
        });
        
        // 타임아웃 설정
        req.setTimeout(options.timeout || 10000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const API_BASE = 'https://singapore-news-github.vercel.app/api';

// 1. 동시 다발적 요청 테스트 (부하 테스트)
async function testConcurrentRequests() {
    console.log('\n🚀 동시 요청 부하 테스트 시작...');
    
    const requestCounts = [5, 10, 20];
    
    for (const count of requestCounts) {
        try {
            console.log(`  📊 ${count}개 동시 요청 테스트...`);
            const startTime = Date.now();
            
            const promises = [];
            for (let i = 0; i < count; i++) {
                promises.push(
                    makeRequest(`${API_BASE}/get-latest-scraped`).catch(err => ({
                        error: err.message,
                        responseTime: err.responseTime || 0
                    }))
                );
            }
            
            const results = await Promise.allSettled(promises);
            const endTime = Date.now();
            const totalTime = endTime - startTime;
            
            const successful = results.filter(r => r.status === 'fulfilled' && !r.value.error).length;
            const failed = results.length - successful;
            const avgResponseTime = results
                .filter(r => r.status === 'fulfilled')
                .reduce((sum, r) => sum + (r.value.responseTime || 0), 0) / results.length;
            
            if (successful >= count * 0.8) { // 80% 이상 성공
                logChaosTest(
                    `동시 요청 ${count}개`, 
                    'PASS', 
                    `성공: ${successful}/${count}, 평균응답: ${avgResponseTime.toFixed(0)}ms, 총시간: ${totalTime}ms`
                );
            } else {
                logChaosTest(
                    `동시 요청 ${count}개`, 
                    'FAIL', 
                    `성공: ${successful}/${count}, 실패율이 높음`
                );
            }
            
        } catch (error) {
            logChaosTest(`동시 요청 ${count}개`, 'FAIL', error.message);
        }
        
        await delay(2000); // 서버 회복 시간
    }
}

// 2. 타임아웃 및 지연 테스트
async function testTimeoutHandling() {
    console.log('\n⏱️ 타임아웃 및 지연 처리 테스트 시작...');
    
    const endpoints = [
        '/get-latest-scraped',
        '/get-scraping-status'
    ];
    
    for (const endpoint of endpoints) {
        try {
            // 짧은 타임아웃으로 테스트
            const result = await makeRequest(`${API_BASE}${endpoint}`, { timeout: 1000 });
            
            if (result.responseTime < 1000) {
                logChaosTest(
                    `빠른 응답 (${endpoint})`, 
                    'PASS', 
                    `${result.responseTime}ms - 타임아웃 내 응답`
                );
            } else {
                logChaosTest(
                    `빠른 응답 (${endpoint})`, 
                    'WARN', 
                    `${result.responseTime}ms - 느린 응답`
                );
            }
            
        } catch (error) {
            if (error.message === 'Request timeout') {
                logChaosTest(
                    `타임아웃 처리 (${endpoint})`, 
                    'WARN', 
                    '타임아웃 발생 - 서버 응답 지연'
                );
            } else {
                logChaosTest(
                    `타임아웃 처리 (${endpoint})`, 
                    'FAIL', 
                    error.message
                );
            }
        }
        
        await delay(500);
    }
}

// 3. 잘못된 데이터 입력 테스트
async function testInvalidInputHandling() {
    console.log('\n🔥 잘못된 입력 데이터 처리 테스트 시작...');
    
    const invalidInputs = [
        { 
            name: '빈 JSON', 
            endpoint: '/save-data',
            method: 'POST',
            body: '{}',
            headers: { 'Content-Type': 'application/json' }
        },
        { 
            name: '잘못된 JSON', 
            endpoint: '/save-data',
            method: 'POST',
            body: 'invalid json',
            headers: { 'Content-Type': 'application/json' }
        },
        { 
            name: '대용량 JSON', 
            endpoint: '/save-data',
            method: 'POST',
            body: JSON.stringify({ data: 'x'.repeat(100000) }),
            headers: { 'Content-Type': 'application/json' }
        },
        {
            name: '특수문자 포함',
            endpoint: '/save-data',
            method: 'POST',
            body: JSON.stringify({ test: '🚀💥🔥💀' }),
            headers: { 'Content-Type': 'application/json' }
        }
    ];
    
    for (const test of invalidInputs) {
        try {
            const result = await makeRequest(`${API_BASE}${test.endpoint}`, {
                method: test.method,
                headers: test.headers,
                body: test.body
            });
            
            if (result.status >= 400) {
                logChaosTest(
                    `잘못된 입력 (${test.name})`, 
                    'PASS', 
                    `올바른 오류 응답: ${result.status}`
                );
            } else {
                logChaosTest(
                    `잘못된 입력 (${test.name})`, 
                    'WARN', 
                    `예상외 응답: ${result.status}`
                );
            }
            
        } catch (error) {
            logChaosTest(
                `잘못된 입력 (${test.name})`, 
                'PASS', 
                `네트워크 수준에서 차단됨: ${error.message}`
            );
        }
        
        await delay(300);
    }
}

// 4. 메모리 및 리소스 압박 테스트
async function testResourcePressure() {
    console.log('\n💾 리소스 압박 테스트 시작...');
    
    try {
        // 빠른 연속 요청으로 서버 압박
        console.log('  📈 빠른 연속 요청 테스트...');
        const rapidRequests = [];
        
        for (let i = 0; i < 50; i++) {
            rapidRequests.push(
                makeRequest(`${API_BASE}/get-scraping-status`).catch(err => ({ error: err.message }))
            );
            
            if (i % 10 === 0) {
                await delay(10); // 매우 짧은 지연
            }
        }
        
        const rapidResults = await Promise.allSettled(rapidRequests);
        const rapidSuccessful = rapidResults.filter(r => 
            r.status === 'fulfilled' && !r.value.error
        ).length;
        
        if (rapidSuccessful >= 40) { // 80% 이상 성공
            logChaosTest(
                '빠른 연속 요청', 
                'PASS', 
                `${rapidSuccessful}/50 성공 - 서버 안정성 양호`
            );
        } else {
            logChaosTest(
                '빠른 연속 요청', 
                'WARN', 
                `${rapidSuccessful}/50 성공 - 서버 압박 시 성능 저하`
            );
        }
        
    } catch (error) {
        logChaosTest('빠른 연속 요청', 'FAIL', error.message);
    }
}

// 5. 다양한 HTTP 메소드 테스트
async function testHTTPMethods() {
    console.log('\n🌐 HTTP 메소드 테스트 시작...');
    
    const methodTests = [
        { method: 'GET', endpoint: '/get-latest-scraped', shouldWork: true },
        { method: 'POST', endpoint: '/auth', shouldWork: true },
        { method: 'PUT', endpoint: '/get-latest-scraped', shouldWork: false },
        { method: 'DELETE', endpoint: '/get-latest-scraped', shouldWork: false },
        { method: 'PATCH', endpoint: '/get-latest-scraped', shouldWork: false },
        { method: 'HEAD', endpoint: '/get-latest-scraped', shouldWork: false }
    ];
    
    for (const test of methodTests) {
        try {
            const result = await makeRequest(`${API_BASE}${test.endpoint}`, {
                method: test.method,
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (test.shouldWork) {
                if (result.status < 400) {
                    logChaosTest(
                        `${test.method} ${test.endpoint}`, 
                        'PASS', 
                        `정상 응답: ${result.status}`
                    );
                } else {
                    logChaosTest(
                        `${test.method} ${test.endpoint}`, 
                        'FAIL', 
                        `오류 응답: ${result.status}`
                    );
                }
            } else {
                if (result.status === 405 || result.status === 404) {
                    logChaosTest(
                        `${test.method} ${test.endpoint}`, 
                        'PASS', 
                        `올바른 거부: ${result.status}`
                    );
                } else {
                    logChaosTest(
                        `${test.method} ${test.endpoint}`, 
                        'WARN', 
                        `예상외 응답: ${result.status}`
                    );
                }
            }
            
        } catch (error) {
            logChaosTest(
                `${test.method} ${test.endpoint}`, 
                'WARN', 
                `네트워크 오류: ${error.message}`
            );
        }
        
        await delay(200);
    }
}

// 6. 헤더 및 CORS 테스트
async function testCORSAndHeaders() {
    console.log('\n🔗 CORS 및 헤더 테스트 시작...');
    
    try {
        const result = await makeRequest(`${API_BASE}/get-latest-scraped`, {
            headers: {
                'Origin': 'https://djyalu.github.io',
                'User-Agent': 'ChaosTestAgent/1.0'
            }
        });
        
        const corsHeaders = result.headers['access-control-allow-origin'];
        if (corsHeaders === '*' || corsHeaders === 'https://djyalu.github.io') {
            logChaosTest(
                'CORS 헤더', 
                'PASS', 
                `올바른 CORS 설정: ${corsHeaders}`
            );
        } else {
            logChaosTest(
                'CORS 헤더', 
                'WARN', 
                `CORS 헤더 확인 필요: ${corsHeaders}`
            );
        }
        
        // Content-Type 확인
        const contentType = result.headers['content-type'];
        if (contentType && contentType.includes('application/json')) {
            logChaosTest(
                'Content-Type', 
                'PASS', 
                `올바른 Content-Type: ${contentType}`
            );
        } else {
            logChaosTest(
                'Content-Type', 
                'WARN', 
                `Content-Type 확인: ${contentType}`
            );
        }
        
    } catch (error) {
        logChaosTest('CORS 테스트', 'FAIL', error.message);
    }
}

// 전체 Chaos 테스트 실행
async function runChaosTests() {
    console.log('💥 Chaos Engineering 테스트 시작');
    console.log('=' .repeat(50));
    
    const startTime = Date.now();
    
    await testConcurrentRequests();
    await testTimeoutHandling();
    await testInvalidInputHandling();
    await testResourcePressure();
    await testHTTPMethods();
    await testCORSAndHeaders();
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // 결과 요약
    console.log('\n' + '=' .repeat(50));
    console.log('💥 Chaos Engineering 테스트 결과');
    console.log('=' .repeat(50));
    console.log(`총 테스트: ${chaosResults.total}`);
    console.log(`통과: ${chaosResults.passed} ✅`);
    console.log(`경고: ${chaosResults.warnings} ⚠️`);
    console.log(`실패: ${chaosResults.failed} ❌`);
    console.log(`시스템 안정성: ${((chaosResults.passed / chaosResults.total) * 100).toFixed(1)}%`);
    console.log(`실행 시간: ${(totalTime / 1000).toFixed(2)}초`);
    
    if (chaosResults.failed > 0) {
        console.log('\n❌ 실패한 테스트:');
        chaosResults.details.filter(t => t.status === 'FAIL').forEach(test => {
            console.log(`  - ${test.testName}: ${test.message}`);
        });
    }
    
    if (chaosResults.warnings > 0) {
        console.log('\n⚠️ 경고 사항:');
        chaosResults.details.filter(t => t.status === 'WARN').forEach(test => {
            console.log(`  - ${test.testName}: ${test.message}`);
        });
    }
    
    return chaosResults;
}

// 실행
if (require.main === module) {
    runChaosTests().catch(console.error);
}

module.exports = { runChaosTests, chaosResults };