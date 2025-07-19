// Minimal working version
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginContainer = document.getElementById('loginContainer');
    const mainContainer = document.getElementById('mainContainer');
    const logoutBtn = document.getElementById('logoutBtn');
    const errorMessage = document.getElementById('errorMessage');

    // Check if already logged in
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
        showMainContainer();
    }

    // Login form handler
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('https://singapore-news-github.vercel.app/api/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const result = await response.json();
            
            if (result.success) {
                localStorage.setItem('currentUser', JSON.stringify(result.user));
                showMainContainer();
            } else {
                errorMessage.textContent = result.error || '로그인 실패';
                errorMessage.classList.remove('hidden');
            }
        } catch (error) {
            errorMessage.textContent = '로그인 중 오류가 발생했습니다.';
            errorMessage.classList.remove('hidden');
        }
    });

    // Logout handler
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('currentUser');
        location.reload();
    });

    function showMainContainer() {
        loginContainer.style.display = 'none';
        mainContainer.style.display = 'block';
        
        const user = JSON.parse(localStorage.getItem('currentUser'));
        const userInfo = document.getElementById('currentUserInfo');
        if (userInfo && user) {
            userInfo.textContent = `${user.name} (${user.id})`;
        }
        
        // Load dashboard
        const content = document.getElementById('content');
        content.innerHTML = `
            <div class="page-section">
                <h2>대시보드</h2>
                <p>로그인 성공! 이제 기능을 사용할 수 있습니다.</p>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-xl font-bold mb-4">주요 기능</h3>
                    <ul class="space-y-2">
                        <li>✅ 뉴스 스크래핑</li>
                        <li>✅ WhatsApp 전송</li>
                        <li>✅ 전송 이력 확인</li>
                        <li>✅ 설정 관리</li>
                    </ul>
                </div>
            </div>
        `;
    }

    // Navigation handlers
    document.querySelectorAll('a[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            loadPage(page);
        });
    });

    function loadPage(page) {
        const content = document.getElementById('content');
        
        switch(page) {
            case 'dashboard':
                content.innerHTML = `
                    <div class="page-section">
                        <h2>대시보드</h2>
                        <p>대시보드 페이지입니다.</p>
                    </div>
                `;
                break;
            case 'settings':
                content.innerHTML = `
                    <div class="page-section">
                        <h2>설정</h2>
                        <p>설정 페이지입니다.</p>
                    </div>
                `;
                break;
            case 'history':
                content.innerHTML = `
                    <div class="page-section">
                        <h2>전송 이력</h2>
                        <p>전송 이력 페이지입니다.</p>
                    </div>
                `;
                break;
            default:
                content.innerHTML = `
                    <div class="page-section">
                        <h2>${page}</h2>
                        <p>페이지 준비 중입니다.</p>
                    </div>
                `;
        }
    }
});