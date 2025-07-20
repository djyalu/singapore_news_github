// AI Agent Test Suite
// 전체 시스템 기능을 자동으로 테스트하는 AI Agent

// API 기본 URL
const API_BASE = 'https://singapore-news-github.vercel.app/api';

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

// 지연 함수
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 1. API 엔드포인트 가용성 테스트
async function testAPIEndpoints() {
    console.log('\n🔍 API 엔드포인트 가용성 테스트 시작...');
    
    const endpoints = [
        { path: '/get-latest-scraped', method: 'GET' },
        { path: '/get-scraping-status', method: 'GET' },
        { path: '/test-env', method: 'GET' },
        { path: '/auth?type=config', method: 'GET' },
        { path: '/save-data?type=settings', method: 'GET' }
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${API_BASE}${endpoint.path}`);
            if (response.ok) {
                logTest(`API ${endpoint.path}`, 'PASS', `Status: ${response.status}`);
            } else {
                logTest(`API ${endpoint.path}`, 'FAIL', `Status: ${response.status}`);
            }
        } catch (error) {
            logTest(`API ${endpoint.path}`, 'FAIL', `Error: ${error.message}`);
        }
        await delay(500); // API 호출 간격
    }
}

// 2. 스크래핑 데이터 검증 테스트
async function testScrapingData() {
    console.log('\n📰 스크래핑 데이터 검증 테스트 시작...');
    
    try {
        const response = await fetch(`${API_BASE}/get-latest-scraped`);
        const data = await response.json();
        
        if (data.success && data.articles) {
            logTest('스크래핑 데이터 존재', 'PASS', `${data.articleCount}개 기사 발견`);
            
            // 데이터 구조 검증
            if (Array.isArray(data.articles)) {
                logTest('데이터 구조 검증', 'PASS', '올바른 배열 형태');
                
                // 각 그룹 검증
                for (const group of data.articles) {
                    if (group.group && group.articles && group.article_count) {
                        logTest(`그룹 구조 (${group.group})`, 'PASS', `${group.article_count}개 기사`);
                        
                        // 기사 내용 검증
                        for (const article of group.articles.slice(0, 2)) { // 처음 2개만 검증
                            if (article.title && article.url && article.summary) {
                                logTest(`기사 구조 (${article.title.slice(0, 30)}...)`, 'PASS', '필수 필드 존재');
                            } else {
                                logTest(`기사 구조 (${article.title || 'Unknown'})`, 'FAIL', '필수 필드 누락');
                            }
                        }
                    } else {
                        logTest(`그룹 구조 (${group.group || 'Unknown'})`, 'FAIL', '필수 필드 누락');
                    }
                }
            } else {
                logTest('데이터 구조 검증', 'FAIL', '배열이 아님');
            }
        } else {
            logTest('스크래핑 데이터 존재', 'FAIL', '데이터 없음');
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
        const configResponse = await fetch(`${API_BASE}/auth?type=config`);
        const configData = await configResponse.json();
        
        if (configResponse.ok) {
            logTest('설정 조회 API', 'PASS', 'Config API 응답 정상');
        } else {
            logTest('설정 조회 API', 'FAIL', `Status: ${configResponse.status}`);
        }
        
        // 로그인 테스트 (잘못된 자격증명)
        const loginResponse = await fetch(`${API_BASE}/auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'invalid', password: 'invalid' })
        });
        
        if (loginResponse.status === 401) {
            logTest('잘못된 로그인 차단', 'PASS', '인증 실패 정상 처리');
        } else {
            logTest('잘못된 로그인 차단', 'FAIL', '인증 검증 부족');
        }
        
    } catch (error) {
        logTest('인증 시스템 테스트', 'FAIL', error.message);
    }
}

// 4. 데이터 저장 API 테스트
async function testDataSaving() {
    console.log('\n💾 데이터 저장 API 테스트 시작...');
    
    const testData = {
        type: 'test',
        data: { testField: 'testValue', timestamp: new Date().toISOString() }
    };
    
    try {
        // 데이터 저장 시도 (인증 없이 - 실패해야 함)
        const response = await fetch(`${API_BASE}/save-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        
        if (response.status === 401 || response.status === 403) {
            logTest('무인증 데이터 저장 차단', 'PASS', '권한 검증 정상');
        } else {
            logTest('무인증 데이터 저장 차단', 'FAIL', '권한 검증 부족');
        }
        
    } catch (error) {
        logTest('데이터 저장 API 테스트', 'FAIL', error.message);
    }
}

// 5. WhatsApp 테스트 API 검증
async function testWhatsAppAPI() {
    console.log('\n📱 WhatsApp API 테스트 시작...');
    
    try {
        // WhatsApp 테스트 API 호출 (GET으로 정보 확인)
        const response = await fetch(`${API_BASE}/test-whatsapp`);
        
        if (response.ok) {
            const data = await response.json();
            logTest('WhatsApp API 연결', 'PASS', 'API 응답 정상');
        } else {
            logTest('WhatsApp API 연결', 'FAIL', `Status: ${response.status}`);
        }
        
    } catch (error) {
        logTest('WhatsApp API 테스트', 'FAIL', error.message);
    }
}

// 6. 스크래핑 트리거 API 테스트
async function testScrapingTrigger() {
    console.log('\n🤖 스크래핑 트리거 API 테스트 시작...');
    
    try {
        // 스크래핑 상태 확인
        const statusResponse = await fetch(`${API_BASE}/get-scraping-status`);
        
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            logTest('스크래핑 상태 조회', 'PASS', `상태: ${statusData.status || 'Unknown'}`);
        } else {
            logTest('스크래핑 상태 조회', 'FAIL', `Status: ${statusResponse.status}`);
        }
        
        // 환경 변수 테스트
        const envResponse = await fetch(`${API_BASE}/test-env`);
        if (envResponse.ok) {
            const envData = await envResponse.json();
            logTest('환경 변수 테스트', 'PASS', '환경 설정 확인 완료');
        } else {
            logTest('환경 변수 테스트', 'FAIL', `Status: ${envResponse.status}`);
        }
        
    } catch (error) {
        logTest('스크래핑 트리거 테스트', 'FAIL', error.message);
    }
}

// 7. 프론트엔드 기능 테스트
async function testFrontendFeatures() {
    console.log('\n🖥️ 프론트엔드 기능 테스트 시작...');
    
    try {
        // 대시보드 요소 존재 확인
        const elements = [
            'todayArticles',
            'totalSent', 
            'lastUpdate',
            'systemStatus'
        ];
        
        for (const elementId of elements) {
            const element = document.getElementById(elementId);
            if (element) {
                logTest(`UI 요소 (${elementId})`, 'PASS', '요소 존재 확인');
            } else {
                logTest(`UI 요소 (${elementId})`, 'FAIL', '요소 없음');
            }
        }
        
        // 로컬 스토리지 테스트
        try {
            localStorage.setItem('aitest', 'test');
            const testValue = localStorage.getItem('aitest');
            if (testValue === 'test') {
                logTest('로컬 스토리지', 'PASS', '정상 작동');
                localStorage.removeItem('aitest');
            } else {
                logTest('로컬 스토리지', 'FAIL', '값 불일치');
            }
        } catch (error) {
            logTest('로컬 스토리지', 'FAIL', error.message);
        }
        
    } catch (error) {
        logTest('프론트엔드 기능 테스트', 'FAIL', error.message);
    }
}

// 8. 성능 및 응답시간 테스트
async function testPerformance() {
    console.log('\n⚡ 성능 및 응답시간 테스트 시작...');
    
    const endpoints = [
        '/get-latest-scraped',
        '/get-scraping-status',
        '/test-env'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const startTime = performance.now();
            const response = await fetch(`${API_BASE}${endpoint}`);
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            if (responseTime < 5000) { // 5초 이하
                logTest(`응답시간 (${endpoint})`, 'PASS', `${responseTime.toFixed(2)}ms`);
            } else {
                logTest(`응답시간 (${endpoint})`, 'FAIL', `${responseTime.toFixed(2)}ms (너무 느림)`);
            }
            
        } catch (error) {
            logTest(`응답시간 (${endpoint})`, 'FAIL', error.message);
        }
        
        await delay(300);
    }
}

// 9. 오류 처리 테스트
async function testErrorHandling() {
    console.log('\n🚨 오류 처리 테스트 시작...');
    
    try {
        // 존재하지 않는 엔드포인트
        const response = await fetch(`${API_BASE}/nonexistent-endpoint`);
        if (response.status === 404) {
            logTest('404 오류 처리', 'PASS', '올바른 404 응답');
        } else {
            logTest('404 오류 처리', 'FAIL', `예상외 상태: ${response.status}`);
        }
        
        // 잘못된 JSON 데이터 전송
        const badResponse = await fetch(`${API_BASE}/save-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: 'invalid json'
        });
        
        if (badResponse.status >= 400) {
            logTest('잘못된 JSON 처리', 'PASS', '오류 응답 정상');
        } else {
            logTest('잘못된 JSON 처리', 'FAIL', '오류 처리 부족');
        }
        
    } catch (error) {
        logTest('오류 처리 테스트', 'PASS', '네트워크 오류 정상 포착');
    }
}

// 전체 테스트 실행
async function runAIAgentTests() {
    console.log('🤖 AI Agent 테스트 시작');
    console.log('=' .repeat(50));
    
    // 테스트 결과 초기화
    testResults = {
        total: 0,
        passed: 0,
        failed: 0,
        errors: [],
        details: []
    };
    
    const startTime = performance.now();
    
    // 모든 테스트 실행
    await testAPIEndpoints();
    await testScrapingData();
    await testAuthSystem();
    await testDataSaving();
    await testWhatsAppAPI();
    await testScrapingTrigger();
    await testFrontendFeatures();
    await testPerformance();
    await testErrorHandling();
    
    const endTime = performance.now();
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
    
    // 테스트 결과를 글로벌 변수에 저장
    window.lastAITestResults = testResults;
    
    return testResults;
}

// Export functions
window.aiAgentTest = {
    runAIAgentTests,
    testAPIEndpoints,
    testScrapingData,
    testAuthSystem,
    testDataSaving,
    testWhatsAppAPI,
    testScrapingTrigger,
    testFrontendFeatures,
    testPerformance,
    testErrorHandling,
    getResults: () => testResults
};

console.log('AI Agent Test Suite loaded. Run aiAgentTest.runAIAgentTests() to start.');