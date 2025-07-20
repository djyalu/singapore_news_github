// Chaos Engineering Test Suite
// 이 파일은 시스템의 안정성을 테스트하기 위한 도구입니다

// Test 1: 대량의 기사 데이터 생성
function generateLargeDataset(articleCount = 100) {
    const groups = ['News', 'Economy', 'Sports', 'Technology'];
    const sites = ['The Straits Times', 'Channel NewsAsia', 'The Business Times'];
    
    const data = [];
    
    for (let g = 0; g < groups.length; g++) {
        const groupArticles = [];
        const articlesPerGroup = Math.floor(articleCount / groups.length);
        
        for (let i = 0; i < articlesPerGroup; i++) {
            groupArticles.push({
                site: sites[Math.floor(Math.random() * sites.length)],
                title: `Test Article ${g}-${i}: ${generateRandomTitle()}`,
                url: `https://example.com/article-${g}-${i}`,
                summary: `📰 테스트 기사 요약 ${i}: ${generateRandomSummary()}`,
                content: generateLongContent(),
                publish_date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
            });
        }
        
        data.push({
            group: groups[g],
            articles: groupArticles,
            article_count: groupArticles.length,
            sites: [...new Set(groupArticles.map(a => a.site))],
            timestamp: new Date().toISOString()
        });
    }
    
    return data;
}

function generateRandomTitle() {
    const words = ['Singapore', 'announces', 'new', 'policy', 'growth', 'technology', 'business', 'innovation'];
    const length = 5 + Math.floor(Math.random() * 5);
    let title = [];
    for (let i = 0; i < length; i++) {
        title.push(words[Math.floor(Math.random() * words.length)]);
    }
    return title.join(' ');
}

function generateRandomSummary() {
    const keywords = ['경제', '정책', '기술', '혁신', '성장', '개발', '싱가포르'];
    return keywords.slice(0, 3).join(', ') + ' 관련 뉴스';
}

function generateLongContent() {
    const sentences = [];
    for (let i = 0; i < 50; i++) {
        sentences.push(`This is test sentence number ${i}. It contains various words like Singapore, business, technology, and innovation.`);
    }
    return sentences.join(' ');
}

// Test 2: API 응답 지연 시뮬레이션
async function simulateSlowAPI(delay = 5000) {
    console.log(`Simulating ${delay}ms API delay...`);
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ success: true, data: generateLargeDataset(10) });
        }, delay);
    });
}

// Test 3: 간헐적 실패 시뮬레이션
async function simulateIntermittentFailure(failureRate = 0.5) {
    if (Math.random() < failureRate) {
        throw new Error('Simulated network failure');
    }
    return { success: true, data: generateLargeDataset(5) };
}

// Test 4: 동시 다발적 요청 테스트
async function simulateConcurrentRequests(requestCount = 10) {
    console.log(`Sending ${requestCount} concurrent requests...`);
    const promises = [];
    
    for (let i = 0; i < requestCount; i++) {
        promises.push(
            fetch('https://singapore-news-github.vercel.app/api/get-latest-scraped')
                .then(res => res.json())
                .catch(err => ({ error: err.message }))
        );
    }
    
    const results = await Promise.allSettled(promises);
    console.log('Concurrent request results:', results);
    return results;
}

// Test 5: 메모리 누수 테스트
function testMemoryLeak() {
    const leakyArray = [];
    let iteration = 0;
    
    const interval = setInterval(() => {
        iteration++;
        // 대량의 데이터를 계속 추가
        leakyArray.push(generateLargeDataset(10));
        
        console.log(`Memory test iteration ${iteration}, array length: ${leakyArray.length}`);
        
        if (iteration >= 10) {
            clearInterval(interval);
            console.log('Memory leak test completed');
            // 정리
            leakyArray.length = 0;
        }
    }, 1000);
}

// Test Runner
async function runChaosTests() {
    console.log('=== Starting Chaos Engineering Tests ===');
    
    try {
        // Test 1: 대용량 데이터
        console.log('\n1. Testing large dataset handling...');
        const largeData = generateLargeDataset(100);
        console.log(`Generated ${largeData.reduce((sum, g) => sum + g.article_count, 0)} articles`);
        
        // Test 2: 느린 API
        console.log('\n2. Testing slow API response...');
        const slowResult = await simulateSlowAPI(3000);
        console.log('Slow API test completed:', slowResult.success);
        
        // Test 3: 간헐적 실패
        console.log('\n3. Testing intermittent failures...');
        let successCount = 0;
        let failureCount = 0;
        for (let i = 0; i < 10; i++) {
            try {
                await simulateIntermittentFailure(0.3);
                successCount++;
            } catch (e) {
                failureCount++;
            }
        }
        console.log(`Success: ${successCount}, Failures: ${failureCount}`);
        
        // Test 4: 동시 요청
        console.log('\n4. Testing concurrent requests...');
        await simulateConcurrentRequests(5);
        
        // Test 5: 메모리 테스트
        console.log('\n5. Testing memory handling...');
        testMemoryLeak();
        
    } catch (error) {
        console.error('Chaos test error:', error);
    }
}

// Export for use in console
window.chaosTest = {
    generateLargeDataset,
    simulateSlowAPI,
    simulateIntermittentFailure,
    simulateConcurrentRequests,
    testMemoryLeak,
    runChaosTests
};

console.log('Chaos Engineering Test Suite loaded. Run chaosTest.runChaosTests() to start.');