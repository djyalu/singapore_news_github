#!/usr/bin/env node

// Node.js 환경에서 테스트 실행
const https = require('https');
const http = require('http');

// 테스트 결과 저장
let testResults = {
    total: 0,
    passed: 0,
    failed: 0,
    errors: [],
    details: []
};

// 테스트 헬퍼 함수
function logTest(testName, status, message = '', data = null) {
    testResults.total++;
    const result = { testName, status, message, timestamp: new Date().toISOString(), data };
    
    if (status === 'PASS') {
        testResults.passed++;
        console.log(`✅ ${testName}: ${message}`);
    } else {
        testResults.failed++;
        testResults.errors.push(result);
        console.log(`❌ ${testName}: ${message}`);
    }
    
    testResults.details.push(result);
}

// HTTP 요청 함수
function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https:') ? https : http;
        const req = client.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve({ status: res.statusCode, data: jsonData, raw: data });
                } catch (e) {
                    resolve({ status: res.statusCode, data: null, raw: data });
                }
            });
        });
        
        req.on('error', reject);
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

// 지연 함수
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// API 기본 URL
const API_BASE = 'https://singapore-news-github.vercel.app/api';

// 1. API 엔드포인트 테스트
async function testAPIEndpoints() {
    console.log('\n🔍 API 엔드포인트 가용성 테스트 시작...');
    
    const endpoints = [
        '/get-latest-scraped',
        '/get-scraping-status', 
        '/test-env',
        '/auth?type=config'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const result = await makeRequest(`${API_BASE}${endpoint}`);
            if (result.status === 200) {
                logTest(`API ${endpoint}`, 'PASS', `Status: ${result.status}`);
            } else {
                logTest(`API ${endpoint}`, 'FAIL', `Status: ${result.status}`);
            }
        } catch (error) {
            logTest(`API ${endpoint}`, 'FAIL', `Error: ${error.message}`);
        }
        await delay(500);
    }
}

// 2. 스크래핑 데이터 검증
async function testScrapingData() {
    console.log('\n📰 스크래핑 데이터 검증 테스트 시작...');
    
    try {
        const result = await makeRequest(`${API_BASE}/get-latest-scraped`);
        
        if (result.status === 200 && result.data && result.data.success) {
            logTest('스크래핑 데이터 존재', 'PASS', `${result.data.articleCount || 0}개 기사`);
            
            if (result.data.articles && Array.isArray(result.data.articles)) {
                logTest('데이터 구조 검증', 'PASS', '올바른 배열 형태');
                
                // 각 그룹 검증
                for (const group of result.data.articles.slice(0, 3)) { // 처음 3개만
                    if (group.group && group.articles && group.article_count) {
                        logTest(`그룹 구조 (${group.group})`, 'PASS', `${group.article_count}개 기사`);
                    } else {
                        logTest(`그룹 구조`, 'FAIL', '필수 필드 누락');
                    }
                }
            } else {
                logTest('데이터 구조 검증', 'FAIL', '배열이 아니거나 없음');
            }
        } else {
            logTest('스크래핑 데이터 존재', 'FAIL', `Status: ${result.status}`);
        }
    } catch (error) {
        logTest('스크래핑 데이터 검증', 'FAIL', error.message);
    }
}

// 3. 인증 시스템 테스트
async function testAuthSystem() {
    console.log('\n🔐 인증 시스템 테스트 시작...');
    
    try {
        // 설정 조회 테스트
        const configResult = await makeRequest(`${API_BASE}/auth?type=config`);
        
        if (configResult.status === 200) {
            logTest('설정 조회 API', 'PASS', 'Config API 응답 정상');
        } else {
            logTest('설정 조회 API', 'FAIL', `Status: ${configResult.status}`);
        }
        
        // 잘못된 로그인 테스트
        const loginResult = await makeRequest(`${API_BASE}/auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'invalid', password: 'invalid' })
        });
        
        if (loginResult.status === 401) {
            logTest('잘못된 로그인 차단', 'PASS', '인증 실패 정상 처리');
        } else {
            logTest('잘못된 로그인 차단', 'FAIL', `Status: ${loginResult.status}`);
        }
        
    } catch (error) {
        logTest('인증 시스템 테스트', 'FAIL', error.message);
    }
}

// 4. 성능 테스트
async function testPerformance() {
    console.log('\n⚡ 성능 및 응답시간 테스트 시작...');
    
    const endpoints = [
        '/get-latest-scraped',
        '/get-scraping-status',
        '/test-env'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const startTime = Date.now();
            const result = await makeRequest(`${API_BASE}${endpoint}`);
            const endTime = Date.now();
            const responseTime = endTime - startTime;
            
            if (responseTime < 5000) { // 5초 이하
                logTest(`응답시간 (${endpoint})`, 'PASS', `${responseTime}ms`);
            } else {
                logTest(`응답시간 (${endpoint})`, 'FAIL', `${responseTime}ms (너무 느림)`);
            }
            
        } catch (error) {
            logTest(`응답시간 (${endpoint})`, 'FAIL', error.message);
        }
        
        await delay(300);
    }
}

// 5. 오류 처리 테스트
async function testErrorHandling() {
    console.log('\n🚨 오류 처리 테스트 시작...');
    
    try {
        // 존재하지 않는 엔드포인트
        const result = await makeRequest(`${API_BASE}/nonexistent-endpoint`);
        if (result.status === 404) {
            logTest('404 오류 처리', 'PASS', '올바른 404 응답');
        } else {
            logTest('404 오류 처리', 'FAIL', `예상외 상태: ${result.status}`);
        }
        
    } catch (error) {
        logTest('오류 처리 테스트', 'PASS', '네트워크 오류 정상 포착');
    }
}

// 전체 테스트 실행
async function runAllTests() {
    console.log('🤖 AI Agent 테스트 시작 (Node.js)');
    console.log('=' .repeat(50));
    
    const startTime = Date.now();
    
    await testAPIEndpoints();
    await testScrapingData();
    await testAuthSystem();
    await testPerformance();
    await testErrorHandling();
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // 테스트 결과 요약
    console.log('\n' + '=' .repeat(50));
    console.log('🎯 AI Agent 테스트 결과 요약');
    console.log('=' .repeat(50));
    console.log(`총 테스트: ${testResults.total}`);
    console.log(`통과: ${testResults.passed} ✅`);
    console.log(`실패: ${testResults.failed} ❌`);
    console.log(`성공률: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);
    console.log(`실행 시간: ${(totalTime / 1000).toFixed(2)}초`);
    
    if (testResults.failed > 0) {
        console.log('\n❌ 실패한 테스트:');
        testResults.errors.forEach(error => {
            console.log(`  - ${error.testName}: ${error.message}`);
        });
    }
    
    return testResults;
}

// 실행
if (require.main === module) {
    runAllTests().catch(console.error);
}

module.exports = { runAllTests, testResults };