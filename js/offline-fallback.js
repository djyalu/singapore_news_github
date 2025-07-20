// Offline Fallback Data Management
// Chaos Engineering: 네트워크 실패시 대비책

// 타임스탬프를 KST로 정확하게 변환하는 함수 (app.js와 동일)
function formatTimestampToKST(timestamp) {
    try {
        const date = new Date(timestamp);
        
        // 타임스탬프가 'Z'로 끝나거나 timezone offset이 있으면 UTC로 처리
        if (timestamp.includes('Z') || timestamp.includes('+') || timestamp.includes('-')) {
            return date.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
        }
        
        // timezone 정보가 없는 경우 UTC로 가정하고 KST로 변환
        const utcDate = new Date(timestamp + 'Z');
        return utcDate.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    } catch (error) {
        console.error('Timestamp formatting error:', error);
        return new Date(timestamp).toLocaleString('ko-KR');
    }
}

const offlineFallback = {
    // 샘플 오프라인 데이터
    sampleData: [
        {
            group: "News",
            articles: [
                {
                    site: "Offline Cache",
                    title: "오프라인 모드입니다",
                    url: "#",
                    summary: "📰 네트워크 연결이 복구되면 최신 뉴스가 표시됩니다.",
                    content: "현재 오프라인 상태입니다. 네트워크 연결을 확인해주세요.",
                    publish_date: new Date().toISOString()
                }
            ],
            article_count: 1,
            sites: ["Offline Cache"],
            timestamp: new Date().toISOString()
        }
    ],

    // 마지막 성공한 데이터 저장
    saveLastSuccessfulData: function(data) {
        try {
            sessionStorage.setItem('lastSuccessfulNewsData', JSON.stringify({
                data: data,
                timestamp: new Date().toISOString()
            }));
        } catch (e) {
            console.error('오프라인 데이터 저장 실패:', e);
        }
    },

    // 오프라인 데이터 로드
    getOfflineData: function() {
        try {
            const stored = sessionStorage.getItem('lastSuccessfulNewsData');
            if (stored) {
                const parsed = JSON.parse(stored);
                // 24시간 이내 데이터만 사용
                const hoursSince = (new Date() - new Date(parsed.timestamp)) / (1000 * 60 * 60);
                if (hoursSince < 24) {
                    return parsed.data;
                }
            }
        } catch (e) {
            console.error('오프라인 데이터 로드 실패:', e);
        }
        return this.sampleData;
    },

    // 네트워크 상태 확인
    isOnline: function() {
        return navigator.onLine;
    },

    // 네트워크 상태 모니터링
    startMonitoring: function() {
        window.addEventListener('online', () => {
            console.log('네트워크 연결됨');
            showNotification('온라인 상태로 전환되었습니다.', 'success');
            // 자동으로 최신 데이터 로드
            if (typeof loadLatestDataFromGitHub === 'function') {
                loadLatestDataFromGitHub();
            }
        });

        window.addEventListener('offline', () => {
            console.log('네트워크 연결 끊김');
            showNotification('오프라인 모드로 전환되었습니다.', 'warning');
        });
    }
};

// 자동 시작
offlineFallback.startMonitoring();

// 전역 함수로 노출
window.displayOfflineData = function() {
    const data = offlineFallback.getOfflineData();
    
    // 오프라인 표시 추가
    const offlineNotice = document.createElement('div');
    offlineNotice.className = 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4';
    offlineNotice.innerHTML = `
        <p class="font-bold">오프라인 모드</p>
        <p>저장된 데이터를 표시하고 있습니다. 네트워크 연결을 확인해주세요.</p>
    `;
    
    const articlesList = document.getElementById('scrapedArticlesList');
    if (articlesList) {
        articlesList.innerHTML = '';
        articlesList.appendChild(offlineNotice);
        
        // 오프라인 데이터 표시
        data.forEach(group => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'article-group bg-gray-50 p-4 rounded-lg mb-4';
            groupDiv.innerHTML = `
                <h4 class="font-bold text-lg mb-2">【${group.group}】</h4>
                <div class="articles-list">
                    ${group.articles.map((article, idx) => `
                        <div class="article-item p-3 bg-white rounded mb-2">
                            <h5 class="font-semibold">${idx + 1}. ${article.title}</h5>
                            <p class="text-sm text-gray-600 mt-1">${article.summary}</p>
                            <p class="text-xs text-gray-500 mt-2">📅 ${formatTimestampToKST(article.publish_date)}</p>
                        </div>
                    `).join('')}
                </div>
            `;
            articlesList.appendChild(groupDiv);
        });
    }
};