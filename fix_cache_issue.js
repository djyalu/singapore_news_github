// 캐시 문제 해결용 임시 스크립트
// 기존 loadScrapedArticles 함수를 수정하여 삭제 상태를 확인하도록 함

function addDeleteStateCheck() {
    const originalLoadScrapedArticles = window.loadScrapedArticles;
    
    window.loadScrapedArticles = async function() {
        const articlesList = document.getElementById('scrapedArticlesList');
        if (!articlesList) return;
        
        // 삭제 상태 확인
        const isDeleted = localStorage.getItem('singapore_news_articles_deleted') === 'true';
        
        if (isDeleted) {
            // 삭제된 상태이면 빈 상태로 표시
            articlesList.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
            return;
        }
        
        // 원래 함수 실행
        return originalLoadScrapedArticles.call(this);
    };
}

// 스크래핑 완료 시 삭제 상태 해제
function clearDeletedState() {
    localStorage.removeItem('singapore_news_articles_deleted');
}

// 페이지 로드 시 적용
if (typeof window !== 'undefined') {
    addDeleteStateCheck();
}

console.log('Cache fix applied: Delete state check added');