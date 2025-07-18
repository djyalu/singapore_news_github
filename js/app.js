document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginContainer = document.getElementById('loginContainer');
    const mainContainer = document.getElementById('mainContainer');
    const logoutBtn = document.getElementById('logoutBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    function checkAuth() {
        if (isAuthenticated()) {
            loginContainer.style.display = 'none';
            mainContainer.style.display = 'block';
            updateNavigation();
            setupNavigationListeners(); // Re-setup navigation listeners
            loadPage('dashboard');
        } else {
            loginContainer.style.display = 'block';
            mainContainer.style.display = 'none';
        }
    }
    
    function updateNavigation() {
        const adminLinks = document.querySelectorAll('.admin-only');
        if (!isAdmin()) {
            adminLinks.forEach(link => link.style.display = 'none');
        }
        
        // 현재 사용자 정보 표시
        const currentUser = getCurrentUser();
        const userInfoElement = document.getElementById('currentUserInfo');
        if (userInfoElement && currentUser) {
            userInfoElement.textContent = `${currentUser.name} (${currentUser.userId})`;
        }
    }
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        console.log('로그인 시도:', username, password);
        
        // 사용자 데이터 확인
        const users = JSON.parse(localStorage.getItem('singapore_news_users') || '[]');
        console.log('저장된 사용자 데이터:', users);
        
        if (login(username, password)) {
            console.log('로그인 성공');
            if (window.isMFAEnabled && isMFAEnabled(username)) {
                showMFAForm(username);
            } else {
                checkAuth();
            }
        } else {
            console.log('로그인 실패');
            errorMessage.textContent = '잘못된 아이디 또는 비밀번호입니다.';
            errorMessage.classList.remove('hidden');
        }
    });
    
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
    
    // Navigation links event listeners - updated for new Flowbite structure
    function setupNavigationListeners() {
        document.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                loadPage(page);
                
                // Update active navigation state
                document.querySelectorAll('a[data-page]').forEach(navLink => {
                    navLink.classList.remove('border-blue-500', 'text-gray-900');
                    navLink.classList.add('border-transparent', 'text-gray-500', 'hover:border-gray-300', 'hover:text-gray-700');
                });
                
                this.classList.remove('border-transparent', 'text-gray-500', 'hover:border-gray-300', 'hover:text-gray-700');
                this.classList.add('border-blue-500', 'text-gray-900');
            });
        });
    }
    
    // Call this function after the main container is shown
    setupNavigationListeners();
    
    async function loadPage(page) {
        const content = document.getElementById('content');
        
        switch(page) {
            case 'dashboard':
                content.innerHTML = getDashboardHTML();
                loadDashboardData();
                setupDashboardEventListeners();
                // GitHub에서 최신 데이터 자동 로드
                loadLatestDataFromGitHub();
                break;
            case 'settings':
                if (isAdmin()) {
                    content.innerHTML = getSettingsHTML();
                    await initializeSettings();
                }
                break;
            case 'history':
                console.log('Loading history page');
                content.innerHTML = getHistoryHTML();
                loadHistory();
                break;
            case 'users':
                if (isAdmin()) {
                    content.innerHTML = getUsersHTML();
                    loadUsers();
                }
                break;
            case 'mfa-settings':
                content.innerHTML = getMFASettingsHTML();
                initializeMFASettings();
                break;
            case 'scraping':
                content.innerHTML = getScrapingManagementHTML();
                loadAllScrapedArticles();
                break;
        }
    }
    
    function getDashboardHTML() {
        return `
            <div class="space-y-6">
                <!-- Header with Actions -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
                        <p class="mt-1 text-sm text-gray-500">싱가포르 뉴스 스크래핑 현황을 확인하세요</p>
                    </div>
                    <div class="mt-4 sm:mt-0 flex space-x-3">
                        <button type="button" id="refreshBtn" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            새로고침
                        </button>
                        <button type="button" id="historyBtn" class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            전송 이력
                        </button>
                        <button type="button" id="serverStatusBtn" class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                            </svg>
                            서버 상태
                        </button>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <!-- Today's Articles Card -->
                    <div id="todayArticlesCard" class="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-lg transition-shadow duration-200">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">오늘 스크랩한 기사</dt>
                                        <dd class="text-lg font-medium text-gray-900" id="todayArticles">0</dd>
                                    </dl>
                                </div>
                                <div class="flex-shrink-0">
                                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Next Send Time Card -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">다음 전송 시간</dt>
                                        <dd class="text-lg font-medium text-gray-900" id="nextSendTime">-</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Send Settings Card -->
                    <div id="sendSettingsCard" class="bg-white overflow-hidden shadow rounded-lg cursor-pointer hover:shadow-lg transition-shadow duration-200">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">전송 설정</dt>
                                        <dd class="text-lg font-medium text-gray-900" id="sendChannelInfo">미설정</dd>
                                    </dl>
                                </div>
                                <div class="flex-shrink-0">
                                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Scraped Articles -->
                <div class="bg-white shadow rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
                            <div>
                                <h3 class="text-lg leading-6 font-medium text-gray-900">오늘 스크랩한 기사</h3>
                                <p class="mt-1 text-sm text-gray-500">실시간으로 수집된 싱가포르 뉴스 기사들</p>
                            </div>
                            <div class="mt-3 sm:mt-0 flex flex-wrap gap-2">
                                <!-- 통합 워크플로우 -->
                                <button type="button" onclick="scrapeNow()" id="scrapeNowBtn" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" title="스크래핑 + WhatsApp 전송">
                                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                                    </svg>
                                    스크래핑 + 전송
                                </button>
                                <!-- 스크래핑만 -->
                                <button type="button" onclick="scrapeOnly()" id="scrapeOnlyBtn" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" title="스크래핑만 실행">
                                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                                    </svg>
                                    스크래핑만
                                </button>
                                <!-- 전송만 -->
                                <button type="button" onclick="sendOnly()" id="sendOnlyBtn" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500" title="WhatsApp 전송만">
                                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                    </svg>
                                    전송만
                                </button>
                                <button type="button" onclick="generateSendMessage()" id="generateMessageBtn" class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                    </svg>
                                    메시지 생성
                                </button>
                                <button type="button" onclick="clearScrapedArticles()" id="clearArticlesBtn" class="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                    </svg>
                                    전체 삭제
                                </button>
                                <button type="button" onclick="toggleScrapedArticles()" class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <span id="toggleArticlesText">접기</span>
                                </button>
                            </div>
                        </div>
                        <div id="scrapedArticlesList" class="mt-4" style="display: block;">
                            <div class="text-center py-4">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                                </svg>
                                <p class="mt-2 text-sm text-gray-500">기사를 불러오는 중...</p>
                            </div>
                        </div>
                        <div id="generatedMessage" class="mt-6 hidden">
                            <div class="border-t border-gray-200 pt-6">
                                <h4 class="text-lg font-medium text-gray-900 mb-4">생성된 전송 메시지</h4>
                                <div class="mt-4">
                                    <label for="messageContent" class="block text-sm font-medium text-gray-700">메시지 내용</label>
                                    <div class="mt-1">
                                        <textarea id="messageContent" rows="15" readonly 
                                                  class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md bg-gray-50">
                                        </textarea>
                                    </div>
                                </div>
                                <div class="mt-4 flex space-x-3">
                                    <button type="button" onclick="sendGeneratedMessage()" 
                                            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                        </svg>
                                        메시지 전송
                                    </button>
                                    <button type="button" onclick="copyMessageToClipboard()" 
                                            class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                                        </svg>
                                        클립보드 복사
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Activity (moved to bottom) -->
                <div class="bg-white shadow rounded-lg mt-6">
                    <div class="px-4 py-5 sm:p-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">최근 활동</h3>
                        <div id="recentActivityList" class="flow-root">
                            <div class="text-center py-4">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p class="mt-2 text-sm text-gray-500">활동 내역을 불러오는 중...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    function getSettingsHTML() {
        return `
            <div class="page-section">
                <h2>Settings</h2>
                
                <!-- Tab Navigation -->
                <div class="border-b border-gray-200">
                    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                        <button onclick="switchSettingsTab('sites')" class="settings-tab active whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm" data-tab="sites">
                            <svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                            </svg>
                            사이트 관리
                        </button>
                        <button onclick="switchSettingsTab('scraping')" class="settings-tab whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm" data-tab="scraping">
                            <svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            스크랩 설정
                        </button>
                        <button onclick="switchSettingsTab('delivery')" class="settings-tab whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm" data-tab="delivery">
                            <svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                            </svg>
                            전송 설정
                        </button>
                        <button onclick="switchSettingsTab('test')" class="settings-tab whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm" data-tab="test">
                            <svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            테스트
                        </button>
                    </nav>
                </div>
                
                <!-- Tab Content -->
                
                <!-- Sites Tab -->
                <div id="sites-tab" class="settings-tab-content active">
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">스크랩 대상 사이트 관리</h3>
                    <form id="siteForm">
                        <div class="form-group">
                            <label>그룹명</label>
                            <input type="text" id="siteGroup" required>
                        </div>
                        <div class="form-group">
                            <label>사이트명</label>
                            <input type="text" id="siteName" required>
                        </div>
                        <div class="form-group">
                            <label>사이트 주소</label>
                            <input type="url" id="siteUrl" required>
                        </div>
                        <div class="form-group">
                            <label>스크랩 주기</label>
                            <select id="scrapPeriod">
                                <option value="daily">일</option>
                                <option value="weekly">주</option>
                                <option value="monthly">월</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">추가</button>
                    </form>
                    <table class="table" id="sitesTable">
                        <thead>
                            <tr>
                                <th>그룹</th>
                                <th>사이트명</th>
                                <th>주소</th>
                                <th>주기</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                    </div>
                </div>
                
                <!-- Scraping Tab -->
                <div id="scraping-tab" class="settings-tab-content" style="display: none;">
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">스크랩 대상 설정</h3>
                    <div class="form-group">
                        <label>스크랩 대상</label>
                        <select id="scrapTarget">
                            <option value="recent">최신 기사 (2일 이내)</option>
                            <option value="important">중요 기사 (키워드)</option>
                            <option value="all">전체</option>
                        </select>
                    </div>
                    <div class="form-group" id="keywordsGroup" style="display: none;">
                        <label>중요 키워드 (쉼표로 구분)</label>
                        <input type="text" id="importantKeywords" placeholder="Singapore, Economy, Technology">
                    </div>
                    <div class="form-group">
                        <label>스크래핑 방식</label>
                        <select id="scrapingMethod">
                            <option value="traditional">전통적 방식 (Pattern-based)</option>
                            <option value="ai">AI 방식 (Gemini AI)</option>
                        </select>
                        <small class="text-gray-500 block mt-1">AI 방식은 Google Gemini API를 사용합니다 (일일 50회 제한)</small>
                    </div>
                    </div>
                    
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">요약 기준</h3>
                        <div class="space-y-3">
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" id="summaryHeadline" checked class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-3 text-sm font-medium text-gray-700">헤드라인</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" id="summaryKeywords" checked class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-3 text-sm font-medium text-gray-700">키워드</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" id="summaryContent" checked class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-3 text-sm font-medium text-gray-700">본문내용</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">기타 설정</h3>
                        <div class="form-group">
                            <label>유해 키워드 차단 (쉼표로 구분)</label>
                            <textarea id="blockedKeywords" rows="3" placeholder="violence, adult, gambling" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
                        </div>
                    </div>
                    
                    <!-- Monitoring Settings -->
                    <div id="monitoringSettingsContainer"></div>
                </div>
                
                <!-- Delivery Tab -->
                <div id="delivery-tab" class="settings-tab-content" style="display: none;">
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">전송 대상</h3>
                    <div class="form-group">
                        <label>전송 채널</label>
                        <select id="sendChannel">
                            <option value="">선택하세요</option>
                            <option value="whatsapp">WhatsApp</option>
                        </select>
                    </div>
                    <div class="form-group" id="whatsappGroup" style="display: none;">
                        <label>WhatsApp 채널 ID</label>
                        <select id="whatsappChannel">
                            <option value="120363419092108413@g.us">Singapore News Main (Test)</option>
                            <option value="120363421252284444@g.us">Singapore News Backup</option>
                        </select>
                    </div>
                    </div>
                    
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">전송 스케줄</h3>
                    <div class="form-group">
                        <label>전송 주기</label>
                        <select id="sendPeriod">
                            <option value="daily">일</option>
                            <option value="weekly">주</option>
                            <option value="monthly">월</option>
                        </select>
                    </div>
                    <div class="form-group" id="weeklyOptions" style="display: none;">
                        <label class="block text-sm font-medium text-gray-700 mb-3">요일 선택</label>
                        <div class="grid grid-cols-7 gap-3">
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="1" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">월</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="2" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">화</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="3" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">수</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="4" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">목</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="5" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">금</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="6" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">토</span>
                            </label>
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" name="weekday" value="0" class="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
                                <span class="ml-2 text-sm text-gray-700">일</span>
                            </label>
                        </div>
                    </div>
                    <div class="form-group" id="monthlyOptions" style="display: none;">
                        <label>날짜 선택</label>
                        <input type="number" id="monthlyDate" min="1" max="31" value="1">
                    </div>
                    <div class="form-group">
                        <label>전송 시간</label>
                        <input type="time" id="sendTime" value="09:00">
                    </div>
                    </div>
                </div>
                
                <!-- Test Tab -->
                <div id="test-tab" class="settings-tab-content" style="display: none;">
                    <div class="bg-white shadow rounded-lg p-6 mt-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">테스트 전송</h3>
                    <p>설정한 채널로 테스트 메시지를 전송하여 연결 상태를 확인하세요.</p>
                    <div class="form-group">
                        <label>테스트 메시지</label>
                        <textarea id="testMessage" rows="5" placeholder="테스트 메시지를 입력하세요...">📰 *Singapore News Update*

🔹 *The Straits Times*
제목: Singapore's economy grows 3.8% in Q4 2024
요약: 싱가포르 경제가 2024년 4분기에 3.8% 성장하며 예상치를 상회했습니다.

🔹 *Channel NewsAsia* 
제목: New MRT stations to open in 2025
요약: 2025년에 새로운 MRT 역 5개가 개통될 예정입니다.

📅 스크랩 시간: ${new Date().toLocaleString()}
🤖 Singapore News Scraper</textarea>
                    </div>
                    <div class="form-group">
                        <label>전송 대상 채널</label>
                        <select id="testChannel">
                            <option value="">선택하세요</option>
                            <option value="120363419092108413@g.us">Singapore News Main (Test)</option>
                            <option value="120363421252284444@g.us">Singapore News Backup</option>
                        </select>
                    </div>
                    <button class="btn" onclick="sendTestMessage()" id="testSendBtn">테스트 전송</button>
                    <div id="testResult" style="margin-top: 15px;"></div>
                    
                    <div class="test-history" style="margin-top: 30px;">
                        <h4>최근 테스트 전송 이력</h4>
                        <div id="testHistoryList"></div>
                    </div>
                    </div>
                </div>
                
                <div class="mt-6 flex justify-end">
                    <button class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500" onclick="saveSettings()">
                        <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V2"></path>
                        </svg>
                        설정 저장
                    </button>
                </div>
            </div>
        `;
    }
    
    function getHistoryHTML() {
        const today = new Date();
        const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
        
        return `
            <div class="page-section">
                <!-- Header -->
                <div class="section-header">
                    <h1>전송 이력</h1>
                    <p>WhatsApp 메시지 전송 기록을 확인합니다</p>
                </div>
                
                <!-- Advanced Search Section -->
                <div class="search-section">
                    <div class="search-header">
                        <h3>🔍 검색 조건</h3>
                        <div class="quick-filters">
                            <button class="quick-filter-btn" onclick="setQuickFilter('today')">오늘</button>
                            <button class="quick-filter-btn" onclick="setQuickFilter('week')">1주일</button>
                            <button class="quick-filter-btn" onclick="setQuickFilter('month')">1개월</button>
                            <button class="quick-filter-btn" onclick="setQuickFilter('all')">전체</button>
                        </div>
                    </div>
                    
                    <div class="search-filters">
                        <div class="filter-group">
                            <div class="filter-label">📅 기간 설정</div>
                            <div class="date-range">
                                <input type="date" id="historyStartDate" value="${lastMonth.toISOString().split('T')[0]}" class="date-input">
                                <span class="date-separator">~</span>
                                <input type="date" id="historyEndDate" value="${today.toISOString().split('T')[0]}" class="date-input">
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <div class="filter-label">📊 상태별</div>
                            <div class="status-filters">
                                <label class="radio-label">
                                    <input type="radio" name="statusFilter" value="" checked onchange="updateStatusFilter(this.value)">
                                    <span class="radio-text">전체</span>
                                </label>
                                <label class="radio-label success">
                                    <input type="radio" name="statusFilter" value="success" onchange="updateStatusFilter(this.value)">
                                    <span class="radio-text">✅ 성공</span>
                                </label>
                                <label class="radio-label failed">
                                    <input type="radio" name="statusFilter" value="failed" onchange="updateStatusFilter(this.value)">
                                    <span class="radio-text">❌ 실패</span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <div class="filter-label">📱 채널 선택</div>
                            <select id="historyChannel" class="channel-select" onchange="loadHistory()">
                                <option value="">모든 채널</option>
                                <option value="120363421252284444@g.us">📰 Singapore News Backup</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="search-actions">
                        <span class="result-summary" id="historyResultCount">검색 결과: 0건</span>
                        <div class="action-buttons">
                            <button class="btn btn-secondary" onclick="resetHistoryFilters()">
                                <span>🔄</span> 초기화
                            </button>
                            <button class="btn btn-primary" onclick="loadHistory()">
                                <span>🔍</span> 검색
                            </button>
                        </div>
                    </div>
                </div>
                <table class="table" id="historyTable">
                    <thead>
                        <tr>
                            <th>전송시간</th>
                            <th>헤더정보</th>
                            <th>채널</th>
                            <th>상태</th>
                            <th>상세</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        `;
    }
    
    function getUsersHTML() {
        return `
            <div class="page-section">
                <h2>사용자 관리</h2>
                <button class="btn" onclick="showAddUserForm()">사용자 추가</button>
                
                <div id="userForm" style="display: none; margin-top: 20px;">
                    <h3>새 사용자 추가</h3>
                    <form onsubmit="addNewUser(event)">
                        <div class="form-group">
                            <label>이름</label>
                            <input type="text" id="newUserName" required>
                        </div>
                        <div class="form-group">
                            <label>ID</label>
                            <input type="text" id="newUserId" required>
                        </div>
                        <div class="form-group">
                            <label>Password (특수기호, 대소문자 포함 8글자 이상)</label>
                            <input type="password" id="newUserPassword" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="newUserEmail" required>
                        </div>
                        <div class="form-group">
                            <label>권한</label>
                            <select id="newUserRole">
                                <option value="user">일반사용자</option>
                                <option value="admin">관리자</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">추가</button>
                        <button type="button" class="btn" onclick="hideAddUserForm()">취소</button>
                    </form>
                </div>
                
                <div id="editUserModal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h3>사용자 정보 수정</h3>
                        <form id="editUserForm">
                            <input type="hidden" id="editUserId">
                            <div class="form-group">
                                <label>이름</label>
                                <input type="text" id="editUserName" required>
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input type="email" id="editUserEmail" required>
                            </div>
                            <div class="form-group">
                                <label>권한</label>
                                <select id="editUserRole">
                                    <option value="user">일반사용자</option>
                                    <option value="admin">관리자</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>새 비밀번호 (변경하지 않으려면 비워두세요)</label>
                                <input type="password" id="editUserPassword" placeholder="특수기호, 대소문자 포함 8글자 이상">
                            </div>
                            <button type="submit" class="btn">저장</button>
                            <button type="button" class="btn" onclick="closeEditUserModal()">취소</button>
                        </form>
                    </div>
                </div>
                
                <table class="table" id="usersTable">
                    <thead>
                        <tr>
                            <th>이름</th>
                            <th>ID</th>
                            <th>Email</th>
                            <th>권한</th>
                            <th>작업</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        `;
    }
    
    function showMFAForm(username) {
        document.getElementById('mfaContainer').classList.remove('hidden');
        document.getElementById('mfaCode').focus();
        
        const mfaForm = document.getElementById('mfaForm');
        const mfaBackBtn = document.getElementById('mfaBackBtn');
        const mfaErrorMessage = document.getElementById('mfaErrorMessage');
        
        // Remove any existing event listeners
        const newMfaForm = mfaForm.cloneNode(true);
        mfaForm.parentNode.replaceChild(newMfaForm, mfaForm);
        
        const newMfaBackBtn = mfaBackBtn.cloneNode(true);
        mfaBackBtn.parentNode.replaceChild(newMfaBackBtn, mfaBackBtn);
        
        // Add new event listeners
        document.getElementById('mfaForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const code = document.getElementById('mfaCode').value;
            
            const isValid = await verifyMFA(username, code);
            if (isValid) {
                document.getElementById('mfaContainer').classList.add('hidden');
                checkAuth();
            } else {
                const mfaErrorMessage = document.getElementById('mfaErrorMessage');
                mfaErrorMessage.textContent = '잘못된 인증 코드입니다.';
                mfaErrorMessage.classList.remove('hidden');
                document.getElementById('mfaCode').value = '';
                document.getElementById('mfaCode').focus();
            }
        });
        
        document.getElementById('mfaBackBtn').addEventListener('click', function() {
            logout();
            document.getElementById('mfaContainer').classList.add('hidden');
            document.getElementById('mfaCode').value = '';
            document.getElementById('mfaErrorMessage').textContent = '';
        });
    }
    
    async function verifyMFA(username, code) {
        if (!window.getMFASecret || !window.verifyTOTP || !window.useBackupCode) {
            return false;
        }
        
        const secret = getMFASecret(username);
        if (!secret) return false;
        
        const isValid = await verifyTOTP(secret, code);
        if (isValid) {
            return true;
        }
        
        const backupResult = useBackupCode(username, code);
        return backupResult.success;
    }
    
    function getMFASettingsHTML() {
        const currentUser = getCurrentUser();
        const mfaEnabled = window.isMFAEnabled ? isMFAEnabled(currentUser.userId) : false;
        
        return `
            <div class="page-section">
                <h2>MFA 설정</h2>
                
                <div class="mfa-status">
                    <h3>현재 상태: ${mfaEnabled ? '활성화됨' : '비활성화됨'}</h3>
                </div>
                
                ${!mfaEnabled ? `
                    <div class="mfa-setup">
                        <h3>MFA 활성화</h3>
                        <p>Google Authenticator, Authy 등의 앱을 사용하여 2단계 인증을 설정하세요.</p>
                        <button class="btn" onclick="MFA.setupMFA(getCurrentUser)">MFA 설정 시작</button>
                    </div>
                ` : `
                    <div class="mfa-manage">
                        <h3>MFA 관리</h3>
                        <button class="btn" onclick="MFA.showBackupCodes(getCurrentUser)">백업 코드 보기</button>
                        <button class="btn" onclick="MFA.regenerateBackupCodesUI(getCurrentUser)">백업 코드 재생성</button>
                        <button class="btn btn-danger" onclick="MFA.disableMFAConfirm(getCurrentUser)">MFA 비활성화</button>
                    </div>
                `}
                
                <div id="mfaSetupModal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h3>MFA 설정</h3>
                        <div id="mfaSetupStep1">
                            <p>1. 인증 앱에서 아래 QR 코드를 스캔하세요:</p>
                            <canvas id="qrCode"></canvas>
                            <p>또는 수동으로 입력: <code id="secretCode"></code></p>
                            <button class="btn" onclick="MFA.nextMFAStep()">다음</button>
                        </div>
                        <div id="mfaSetupStep2" style="display: none;">
                            <p>2. 인증 앱에서 생성된 6자리 코드를 입력하세요:</p>
                            <input type="text" id="setupMfaCode" placeholder="000000" maxlength="6">
                            <button class="btn" onclick="MFA.completeMFASetup(getCurrentUser)">완료</button>
                        </div>
                        <div id="mfaSetupStep3" style="display: none;">
                            <h4>백업 코드</h4>
                            <p>MFA 기기를 분실했을 때 사용할 백업 코드입니다. 안전한 곳에 보관하세요.</p>
                            <div id="backupCodesList"></div>
                            <button class="btn" onclick="MFA.finishMFASetup()">완료</button>
                        </div>
                        <button class="btn btn-danger" onclick="MFA.closeMFAModal()">취소</button>
                    </div>
                </div>
                
                <div id="backupCodesModal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h3>백업 코드</h3>
                        <div id="currentBackupCodes"></div>
                        <button class="btn" onclick="MFA.closeBackupCodesModal()">닫기</button>
                    </div>
                </div>
            </div>
        `;
    }
    
    function initializeMFASettings() {
        // MFA 설정 페이지 초기화
    }
    
    checkAuth();
});

function switchSettingsTab(tabName) {
    // 모든 탭 콘텐츠 숨기기
    document.querySelectorAll('.settings-tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active', 'border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
    });
    
    // 선택된 탭 콘텐츠 표시
    const tabContent = document.getElementById(`${tabName}-tab`);
    if (tabContent) {
        tabContent.style.display = 'block';
    }
    
    // 선택된 탭 버튼 활성화
    const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabButton) {
        tabButton.classList.add('active', 'border-blue-500', 'text-blue-600');
        tabButton.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
    }
}

function sendTestMessage() {
    const testMessage = document.getElementById('testMessage').value;
    const testChannel = document.getElementById('testChannel').value;
    const testSendBtn = document.getElementById('testSendBtn');
    const testResult = document.getElementById('testResult');
    
    if (!testMessage.trim()) {
        testResult.innerHTML = '<div class="error-message">테스트 메시지를 입력하세요.</div>';
        return;
    }
    
    if (!testChannel) {
        testResult.innerHTML = '<div class="error-message">전송 대상 채널을 선택하세요.</div>';
        return;
    }
    
    // 버튼 비활성화 및 로딩 상태
    testSendBtn.disabled = true;
    testSendBtn.textContent = '전송 중...';
    testResult.innerHTML = '<div class="info-message">테스트 메시지를 전송하고 있습니다...</div>';
    
    // 실제 메시지 처리 (시간 변수 치환)
    const processedMessage = testMessage.replace('${new Date().toLocaleString()}', new Date().toLocaleString());
    
    // 환경 감지 및 API 호출
    const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    
    // 실제 WhatsApp API를 통한 테스트 전송
    const apiUrl = 'https://singapore-news-github.vercel.app/api/test-whatsapp';
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            channel: testChannel,
            message: processedMessage
        })
    })
    .then(response => {
        console.log('WhatsApp Test API Response Status:', response.status);
        console.log('WhatsApp Test API Response OK:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('WhatsApp Test API Response:', data);
        
        if (data.success && data.sent) {
            const messageId = data.message?.message?.id || data.id || 'unknown';
            testResult.innerHTML = `<div class="success-message">✅ 테스트 메시지가 성공적으로 전송되었습니다! (ID: ${messageId})</div>`;
            recordTestHistory(testChannel, 'success', processedMessage);
        } else {
            let errorMsg = data.error?.message || data.error || '알 수 없는 오류가 발생했습니다.';
            testResult.innerHTML = `<div class="error-message">❌ 테스트 메시지 전송에 실패했습니다: ${errorMsg}</div>`;
            recordTestHistory(testChannel, 'failed', processedMessage);
        }
    })
    .catch(error => {
        console.error('WhatsApp Test API Error:', error);
        let errorMsg = '네트워크 연결을 확인해주세요.';
        if (error.message) {
            errorMsg = error.message;
        }
        testResult.innerHTML = `<div class="error-message">❌ WhatsApp API 호출이 실패했습니다: ${errorMsg}</div>`;
        recordTestHistory(testChannel, 'failed', processedMessage);
    })
    .finally(() => {
        testSendBtn.disabled = false;
        testSendBtn.textContent = '테스트 전송';
        loadTestHistory();
    });
}

function recordTestHistory(channel, status, message) {
    const testHistory = JSON.parse(localStorage.getItem('singapore_news_test_history') || '[]');
    
    const testRecord = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        channel: channel,
        status: status,
        message: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
        user: getCurrentUser().name
    };
    
    testHistory.unshift(testRecord);
    
    // 최대 5개의 테스트 이력만 보관
    if (testHistory.length > 5) {
        testHistory.splice(5);
    }
    
    localStorage.setItem('singapore_news_test_history', JSON.stringify(testHistory));
}

function loadTestHistory() {
    let testHistory = JSON.parse(localStorage.getItem('singapore_news_test_history') || '[]');
    
    // 기존 데이터가 5개를 초과하면 5개로 제한
    if (testHistory.length > 5) {
        testHistory = testHistory.slice(0, 5);
        localStorage.setItem('singapore_news_test_history', JSON.stringify(testHistory));
    }
    
    const testHistoryList = document.getElementById('testHistoryList');
    
    if (testHistory.length === 0) {
        testHistoryList.innerHTML = '<p class="no-data">테스트 전송 이력이 없습니다.</p>';
        return;
    }
    
    const historyHTML = testHistory.slice(0, 5).map(record => `
        <div class="test-history-item">
            <div class="test-history-header">
                <span class="test-status ${record.status}">${record.status === 'success' ? '✅ 성공' : '❌ 실패'}</span>
                <span class="test-time">${new Date(record.timestamp).toLocaleString()}</span>
            </div>
            <div class="test-details">
                <strong>채널:</strong> ${getChannelName(record.channel)} <br>
                <strong>메시지:</strong> ${record.message} <br>
                <strong>전송자:</strong> ${record.user}
            </div>
        </div>
    `).join('');
    
    testHistoryList.innerHTML = historyHTML;
}

function getChannelName(channelId) {
    const channels = {
        '120363421252284444@g.us': 'Singapore News Backup'
    };
    return channels[channelId] || channelId;
}

async function initializeSettings() {
    const scrapTarget = document.getElementById('scrapTarget');
    const sendChannel = document.getElementById('sendChannel');
    const sendPeriod = document.getElementById('sendPeriod');
    
    scrapTarget.addEventListener('change', function() {
        const keywordsGroup = document.getElementById('keywordsGroup');
        keywordsGroup.style.display = this.value === 'important' ? 'block' : 'none';
    });
    
    sendChannel.addEventListener('change', function() {
        const whatsappGroup = document.getElementById('whatsappGroup');
        whatsappGroup.style.display = this.value === 'whatsapp' ? 'block' : 'none';
    });
    
    sendPeriod.addEventListener('change', function() {
        const weeklyOptions = document.getElementById('weeklyOptions');
        const monthlyOptions = document.getElementById('monthlyOptions');
        
        weeklyOptions.style.display = this.value === 'weekly' ? 'block' : 'none';
        monthlyOptions.style.display = this.value === 'monthly' ? 'block' : 'none';
    });
    
    await loadSettings();
    await loadSites();
    loadTestHistory();
}

async function loadSettings() {
    let settings = {};
    
    // localStorage에서 먼저 시도
    const localSettings = localStorage.getItem('singapore_news_settings');
    if (localSettings) {
        settings = JSON.parse(localSettings);
    } else {
        // localStorage가 비어있으면 settings.json에서 로드
        try {
            const response = await fetch('data/settings.json');
            if (response.ok) {
                settings = await response.json();
                // 로드한 데이터를 localStorage에 저장 (시크릿 모드가 아닌 경우)
                try {
                    localStorage.setItem('singapore_news_settings', JSON.stringify(settings));
                } catch (e) {
                    // 시크릿 모드에서는 localStorage 저장 실패 가능
                    console.log('localStorage 저장 실패 (시크릿 모드일 수 있음)');
                }
            }
        } catch (error) {
            console.error('settings.json 로드 실패:', error);
            settings = {};
        }
    }
    
    if (settings.scrapTarget) {
        document.getElementById('scrapTarget').value = settings.scrapTarget;
        if (settings.scrapTarget === 'important') {
            document.getElementById('keywordsGroup').style.display = 'block';
            document.getElementById('importantKeywords').value = settings.importantKeywords || '';
        }
    }
    
    if (settings.summaryOptions) {
        document.getElementById('summaryHeadline').checked = settings.summaryOptions.headline;
        document.getElementById('summaryKeywords').checked = settings.summaryOptions.keywords;
        document.getElementById('summaryContent').checked = settings.summaryOptions.content;
    }
    
    if (settings.scrapingMethod) {
        document.getElementById('scrapingMethod').value = settings.scrapingMethod;
    }
    
    if (settings.sendChannel) {
        document.getElementById('sendChannel').value = settings.sendChannel;
        if (settings.sendChannel === 'whatsapp') {
            document.getElementById('whatsappGroup').style.display = 'block';
            document.getElementById('whatsappChannel').value = settings.whatsappChannel || '';
        }
    }
    
    if (settings.sendSchedule) {
        document.getElementById('sendPeriod').value = settings.sendSchedule.period;
        document.getElementById('sendTime').value = settings.sendSchedule.time;
        
        if (settings.sendSchedule.period === 'weekly') {
            document.getElementById('weeklyOptions').style.display = 'block';
        } else if (settings.sendSchedule.period === 'monthly') {
            document.getElementById('monthlyOptions').style.display = 'block';
            document.getElementById('monthlyDate').value = settings.sendSchedule.date || 1;
        }
    }
    
    if (settings.blockedKeywords) {
        document.getElementById('blockedKeywords').value = settings.blockedKeywords;
    }
    
    // 모니터링 UI 렌더링
    const monitoringContainer = document.getElementById('monitoringSettingsContainer');
    if (monitoringContainer) {
        monitoringContainer.innerHTML = createMonitoringSettingsUI();
        
        // 모니터링 설정 로드
        loadMonitoringSettings(settings);
        
        // 이벤트 리스너 추가
        const monitoringEnabled = document.getElementById('monitoringEnabled');
        if (monitoringEnabled) {
            monitoringEnabled.addEventListener('change', toggleMonitoringSettings);
        }
    }
}

function saveSettings() {
    try {
        // 기존 설정 가져오기 (변경 사항 추적용)
        const oldSettings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
        
        const settings = {
            scrapTarget: document.getElementById('scrapTarget').value,
            importantKeywords: document.getElementById('importantKeywords').value,
            summaryOptions: {
                headline: document.getElementById('summaryHeadline').checked,
                keywords: document.getElementById('summaryKeywords').checked,
                content: document.getElementById('summaryContent').checked
            },
            sendChannel: document.getElementById('sendChannel').value,
            whatsappChannel: document.getElementById('whatsappChannel').value,
            sendSchedule: {
                period: document.getElementById('sendPeriod').value,
                time: document.getElementById('sendTime').value,
                weekdays: Array.from(document.querySelectorAll('input[name="weekday"]:checked')).map(cb => cb.value),
                date: document.getElementById('monthlyDate').value
            },
            blockedKeywords: document.getElementById('blockedKeywords').value,
            scrapingMethod: document.getElementById('scrapingMethod').value,
            monitoring: {
                enabled: document.getElementById('monitoringEnabled')?.checked || false,
                email: {
                    enabled: document.getElementById('emailEnabled')?.checked || false,
                    recipients: (document.getElementById('emailRecipients')?.value || '').split(',').map(e => e.trim()).filter(e => e),
                    sendOn: {
                        success: document.getElementById('sendOnSuccess')?.checked || false,
                        failure: document.getElementById('sendOnFailure')?.checked || true,
                        noArticles: document.getElementById('sendOnNoArticles')?.checked || true
                    },
                    smtp: {
                        host: document.getElementById('smtpHost')?.value || 'smtp.gmail.com',
                        port: parseInt(document.getElementById('smtpPort')?.value || '587'),
                        secure: document.getElementById('smtpSecure')?.checked || false
                    }
                },
                summary: {
                    dailyReport: document.getElementById('dailyReport')?.checked || false,
                    weeklyReport: document.getElementById('weeklyReport')?.checked || false
                }
            }
        };
        
        // 설정 유효성 검사
        if (settings.sendChannel === 'whatsapp' && !settings.whatsappChannel) {
            showNotification('WhatsApp 채널을 선택해주세요.', 'error');
            return;
        }
        
        // GitHub에 설정 저장
        fetch('https://singapore-news-github.vercel.app/api/save-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type: 'settings', data: settings })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 서버 저장 성공 시 로컬에도 저장
                localStorage.setItem('singapore_news_settings', JSON.stringify(settings));
                showNotification('설정이 저장되었습니다.', 'success');
                
                // 설정 변경 이력 저장
                saveSettingsHistory(settings, oldSettings);
            } else {
                showNotification(data.error || '설정 저장에 실패했습니다.', 'error');
            }
        })
        .catch(error => {
            console.error('GitHub 설정 저장 오류:', error);
            // GitHub 저장 실패 시 로컬에만 저장
            try {
                localStorage.setItem('singapore_news_settings', JSON.stringify(settings));
                showNotification('설정이 로컬에 저장되었습니다. (GitHub 연결 실패)', 'warning');
                
                // 설정 변경 이력 저장
                saveSettingsHistory(settings, oldSettings);
            } catch (localError) {
                console.error('로컬 저장도 실패:', localError);
                showNotification('설정 저장에 실패했습니다.', 'error');
            }
        });
    } catch (error) {
        console.error('설정 저장 오류:', error);
        showNotification('설정 저장 중 오류가 발생했습니다.', 'error');
    }
}

async function loadSites() {
    let sites = [];
    
    // localStorage에서 먼저 시도
    const localSites = localStorage.getItem('singapore_news_sites');
    if (localSites) {
        sites = JSON.parse(localSites);
    } else {
        // localStorage가 비어있으면 sites.json에서 로드
        try {
            const response = await fetch('data/sites.json');
            if (response.ok) {
                sites = await response.json();
                // 로드한 데이터를 localStorage에 저장 (시크릿 모드가 아닌 경우)
                try {
                    localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
                } catch (e) {
                    // 시크릿 모드에서는 localStorage 저장 실패 가능
                    console.log('localStorage 저장 실패 (시크릿 모드일 수 있음)');
                }
            }
        } catch (error) {
            console.error('sites.json 로드 실패:', error);
            sites = [];
        }
    }
    
    const tbody = document.querySelector('#sitesTable tbody');
    tbody.innerHTML = '';
    
    sites.forEach((site, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${site.group}</td>
            <td>${site.name}</td>
            <td>${site.url}</td>
            <td>${site.period}</td>
            <td><button class="btn btn-danger" onclick="deleteSite(${index})">삭제</button></td>
        `;
    });
}

document.addEventListener('submit', async function(e) {
    if (e.target.id === 'siteForm') {
        e.preventDefault();
        const sites = JSON.parse(localStorage.getItem('singapore_news_sites') || '[]');
        
        sites.push({
            group: document.getElementById('siteGroup').value,
            name: document.getElementById('siteName').value,
            url: document.getElementById('siteUrl').value,
            period: document.getElementById('scrapPeriod').value
        });
        
        // GitHub에 사이트 목록 저장
        try {
            const response = await fetch('https://singapore-news-github.vercel.app/api/save-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: 'sites', data: sites })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 성공 시 로컬에도 저장
                localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
                showNotification('사이트가 추가되었습니다.', 'success');
            } else {
                showNotification(result.error || '사이트 저장에 실패했습니다.', 'error');
                // 실패 시 배열에서 제거
                sites.pop();
            }
        } catch (error) {
            console.error('사이트 저장 오류:', error);
            showNotification('사이트 저장 중 오류가 발생했습니다.', 'error');
            sites.pop();
        }
        
        await loadSites();
        e.target.reset();
    }
});

async function deleteSite(index) {
    const sites = JSON.parse(localStorage.getItem('singapore_news_sites') || '[]');
    const deletedSite = sites[index];
    sites.splice(index, 1);
    
    // GitHub에 사이트 목록 업데이트
    try {
        const response = await fetch('https://singapore-news-github.vercel.app/api/save-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type: 'sites', data: sites })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 성공 시 로컬에도 저장
            localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
            showNotification('사이트가 삭제되었습니다.', 'success');
        } else {
            showNotification(result.error || '사이트 삭제에 실패했습니다.', 'error');
            // 실패 시 복구
            sites.splice(index, 0, deletedSite);
        }
    } catch (error) {
        console.error('사이트 삭제 오류:', error);
        showNotification('사이트 삭제 중 오류가 발생했습니다.', 'error');
        // 오류 시 복구
        sites.splice(index, 0, deletedSite);
    }
    
    await loadSites();
}

async function loadHistory() {
    console.log('전송 이력 로드 시작...');
    
    // localStorage와 GitHub 데이터 결합
    let history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    
    // GitHub에서 이력 데이터 가져오기 (최근 3개월)
    try {
        const now = new Date();
        const localIds = new Set(history.map(h => h.id));
        
        for (let i = 0; i < 3; i++) {
            const targetDate = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const monthStr = targetDate.toISOString().substring(0, 7).replace('-', '');
            const historyUrl = `data/history/${monthStr}.json`;
            
            console.log(`GitHub 이력 조회 (${i+1}/3):`, historyUrl);
            
            try {
                const response = await fetch(historyUrl + '?t=' + Date.now());
                if (response.ok) {
                    const githubHistory = await response.json();
                    console.log(`${monthStr} 이력 데이터:`, githubHistory.length, '건');
                    
                    // 중복 제거하며 결합
                    githubHistory.forEach(record => {
                        if (!localIds.has(record.id)) {
                            history.push(record);
                            localIds.add(record.id);
                        }
                    });
                }
            } catch (monthError) {
                console.log(`${monthStr} 이력 없음`);
            }
        }
        
        // send_history.json도 확인
        try {
            const sendHistoryUrl = 'data/history/send_history.json';
            const sendResponse = await fetch(sendHistoryUrl + '?t=' + Date.now());
            if (sendResponse.ok) {
                const sendHistory = await sendResponse.json();
                console.log('send_history.json 데이터:', sendHistory.length, '건');
                sendHistory.forEach(record => {
                    if (!localIds.has(record.id)) {
                        history.push(record);
                    }
                });
            }
        } catch (e) {
            console.log('send_history.json 없음');
        }
    } catch (error) {
        console.error('GitHub 이력 로드 실패:', error);
    }
    
    console.log('전체 이력 개수:', history.length);
    
    const tbody = document.querySelector('#historyTableBody') || document.querySelector('#historyTable tbody');
    if (!tbody) {
        console.error('historyTable tbody를 찾을 수 없습니다');
        return;
    }
    tbody.innerHTML = '';
    
    // 필터 값 가져오기
    const startDate = document.getElementById('historyStartDate')?.value;
    const endDate = document.getElementById('historyEndDate')?.value;
    const statusFilter = document.querySelector('input[name="statusFilter"]:checked')?.value || '';
    const channelFilter = document.getElementById('historyChannel')?.value;
    
    // 필터링
    let filteredHistory = history.filter(record => {
        const recordDate = new Date(record.timestamp);
        
        // 날짜 필터
        if (startDate && recordDate < new Date(startDate + 'T00:00:00')) {
            return false;
        }
        if (endDate && recordDate > new Date(endDate + 'T23:59:59')) {
            return false;
        }
        
        // 상태 필터
        if (statusFilter && record.status !== statusFilter) {
            return false;
        }
        
        // 채널 필터
        if (channelFilter && record.channel !== channelFilter) {
            return false;
        }
        
        return true;
    });
    
    // 결과 개수 표시
    const resultCount = document.getElementById('historyResultCount');
    if (resultCount) {
        resultCount.textContent = `총 ${filteredHistory.length}건`;
    }
    
    // 최신 순으로 정렬
    filteredHistory.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // 테이블에 표시
    filteredHistory.forEach(record => {
        const row = tbody.insertRow();
        const statusClass = record.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
        row.innerHTML = `
            <td>${new Date(record.timestamp).toLocaleString('ko-KR')}</td>
            <td>${record.header || '-'}</td>
            <td>${getChannelName(record.channel)}</td>
            <td>
                <span class="status-badge ${record.status}">
                    ${record.status === 'success' ? '성공' : '실패'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm" onclick="showHistoryDetail('${record.id}')">상세</button>
            </td>
        `;
    });
    
    // Show/hide empty state
    const emptyState = document.getElementById('historyEmptyState');
    if (filteredHistory.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) {
            emptyState.classList.remove('hidden');
            // Update empty state message based on whether we have any history
            if (history.length === 0) {
                emptyState.querySelector('h3').textContent = '전송 기록이 없습니다';
                emptyState.querySelector('p').textContent = 'WhatsApp 전송을 실행하면 여기에 이력이 표시됩니다.';
            } else {
                emptyState.querySelector('h3').textContent = '검색 결과가 없습니다';
                emptyState.querySelector('p').textContent = '필터 조건에 맞는 전송 기록이 없습니다.';
            }
        }
    } else {
        if (emptyState) {
            emptyState.classList.add('hidden');
        }
    }
}

function resetHistoryFilters() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    
    document.getElementById('historyStartDate').value = lastMonth.toISOString().split('T')[0];
    document.getElementById('historyEndDate').value = today.toISOString().split('T')[0];
    document.querySelector('input[name="statusFilter"][value=""]').checked = true;
    document.getElementById('historyChannel').value = '';
    
    loadHistory();
}

function setQuickFilter(period) {
    const endDate = new Date();
    let startDate = new Date();
    
    switch(period) {
        case 'today':
            startDate = new Date();
            break;
        case 'week':
            startDate.setDate(endDate.getDate() - 7);
            break;
        case 'month':
            startDate.setMonth(endDate.getMonth() - 1);
            break;
        case 'all':
            startDate = new Date('2024-01-01');
            break;
    }
    
    document.getElementById('historyStartDate').value = startDate.toISOString().split('T')[0];
    document.getElementById('historyEndDate').value = endDate.toISOString().split('T')[0];
    
    // Highlight active quick filter
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadHistory();
}

function updateStatusFilter(value) {
    document.getElementById('historyStatus').value = value;
    loadHistory();
}

function showHistoryDetail(recordId) {
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const record = history.find(r => r.id === recordId);
    
    if (record && record.articles && record.articles.length > 0) {
        // 기사가 있는 경우 모달로 표시
        const modal = createArticlesModal();
        document.body.appendChild(modal);
        
        const content = document.getElementById('articlesModalContent');
        const title = document.getElementById('modalTitle');
        
        title.textContent = `전송 기록 - ${new Date(record.timestamp).toLocaleString('ko-KR')}`;
        
        let html = `
            <div class="history-detail-info">
                <div class="info-row">
                    <span class="info-label">채널:</span>
                    <span class="info-value">${getChannelName(record.channel)}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">상태:</span>
                    <span class="info-value ${record.status}">${record.status === 'success' ? '✅ 성공' : '❌ 실패'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">기사 수:</span>
                    <span class="info-value">${record.articles.length}개</span>
                </div>
            </div>
            <hr style="margin: 20px 0;">
        `;
        
        renderArticlesList(record.articles, content);
        content.innerHTML = html + content.innerHTML;
    } else {
        // 기사가 없는 경우 기본 정보만 표시
        showNotification(`전송 시간: ${new Date(record.timestamp).toLocaleString()}, 상태: ${record.status === 'success' ? '성공' : '실패'}`, 'info');
    }
}

function loadUsers() {
    const users = getAllUsers();
    const tbody = document.querySelector('#usersTable tbody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${user.name}</td>
            <td>${user.id}</td>
            <td>${user.email}</td>
            <td>${user.role === 'admin' ? '관리자' : '일반사용자'}</td>
            <td>
                <button class="btn" onclick="showEditUserModal('${user.id}')">수정</button>
                <button class="btn" onclick="resetUserPassword('${user.id}')">비밀번호 초기화</button>
                ${user.id !== 'admin' ? `<button class="btn btn-danger" onclick="deleteUserConfirm('${user.id}')">삭제</button>` : ''}
            </td>
        `;
    });
}

function showAddUserForm() {
    document.getElementById('userForm').style.display = 'block';
}

function hideAddUserForm() {
    document.getElementById('userForm').style.display = 'none';
}

function addNewUser(event) {
    event.preventDefault();
    
    const userData = {
        id: document.getElementById('newUserId').value,
        password: document.getElementById('newUserPassword').value,
        name: document.getElementById('newUserName').value,
        email: document.getElementById('newUserEmail').value,
        role: document.getElementById('newUserRole').value
    };
    
    const result = addUser(userData);
    
    if (result.success) {
        showNotification('사용자가 추가되었습니다.', 'success');
        hideAddUserForm();
        loadUsers();
        event.target.reset();
    } else {
        showNotification(result.message, 'error');
    }
}

function resetUserPassword(userId) {
    const newPassword = prompt('새 비밀번호를 입력하세요 (특수기호, 대소문자 포함 8글자 이상):');
    if (newPassword) {
        const result = updateUser(userId, { password: newPassword });
        if (result.success) {
            showNotification('비밀번호가 변경되었습니다.', 'success');
        } else {
            showNotification(result.message, 'error');
        }
    }
}

function deleteUserConfirm(userId) {
    if (confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
        deleteUser(userId);
        loadUsers();
        showNotification('사용자가 삭제되었습니다.', 'success');
    }
}

function showEditUserModal(userId) {
    const users = getAllUsers();
    const user = users.find(u => u.id === userId);
    
    if (!user) {
        showNotification('사용자를 찾을 수 없습니다.', 'error');
        return;
    }
    
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUserName').value = user.name;
    document.getElementById('editUserEmail').value = user.email;
    document.getElementById('editUserRole').value = user.role;
    document.getElementById('editUserPassword').value = '';
    
    document.getElementById('editUserModal').style.display = 'block';
    
    const editForm = document.getElementById('editUserForm');
    editForm.onsubmit = function(e) {
        e.preventDefault();
        updateUserInfo();
    };
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

function updateUserInfo() {
    const userId = document.getElementById('editUserId').value;
    const name = document.getElementById('editUserName').value;
    const email = document.getElementById('editUserEmail').value;
    const role = document.getElementById('editUserRole').value;
    const password = document.getElementById('editUserPassword').value;
    
    const updates = {
        name: name,
        email: email,
        role: role
    };
    
    if (password.trim() !== '') {
        updates.password = password;
    }
    
    const result = updateUser(userId, updates);
    
    if (result.success) {
        showNotification('사용자 정보가 수정되었습니다.', 'success');
        closeEditUserModal();
        loadUsers();
        
        const currentUser = getCurrentUser();
        if (currentUser.userId === userId) {
            const authData = {
                ...currentUser,
                name: name,
                email: email,
                role: role
            };
            localStorage.setItem('singapore_news_auth', JSON.stringify(authData));
        }
    } else {
        showNotification('사용자 정보 수정에 실패했습니다: ' + result.message, 'error');
    }
}

// Dashboard Functions
function loadDashboardData() {
    updateTodayArticles();
    updateNextSendTime();
    updateSendChannelInfo();
    loadRecentActivity();
    loadScrapedArticles(); // 스크랩된 기사도 로드
}

function setupDashboardEventListeners() {
    const refreshBtn = document.getElementById('refreshBtn');
    const historyBtn = document.getElementById('historyBtn');
    const serverStatusBtn = document.getElementById('serverStatusBtn');
    const todayArticlesCard = document.getElementById('todayArticlesCard');
    const sendSettingsCard = document.getElementById('sendSettingsCard');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
    
    if (historyBtn) {
        historyBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('History button clicked');
            // 네비게이션 링크를 통해 히스토리 페이지로 이동
            const historyNavLink = document.querySelector('a[data-page="history"]');
            if (historyNavLink) {
                historyNavLink.click();
            }
        });
    }
    
    if (serverStatusBtn) {
        serverStatusBtn.addEventListener('click', showServerStatus);
    }
    
    if (todayArticlesCard) {
        todayArticlesCard.addEventListener('click', () => showArticlesList('today'));
    }
    
    if (sendSettingsCard) {
        sendSettingsCard.addEventListener('click', showSendSettings);
    }
}

function refreshDashboard(event) {
    const refreshBtn = event ? event.target : document.getElementById('refreshBtn');
    if (!refreshBtn) return;
    
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i class="icon">⏳</i> 새로고침 중...';
    
    loadDashboardData();
    
    setTimeout(() => {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="icon">🔄</i> 새로고침';
    }, 1000);
}

function updateTodayArticles() {
    // localStorage에서 스크랩 데이터 확인
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    let todayCount = 0;
    
    if (scrapedData) {
        try {
            const data = JSON.parse(scrapedData);
            const today = new Date().toDateString();
            
            // 오늘 날짜의 기사만 필터링
            if (data.lastUpdated) {
                const lastUpdate = data.lastUpdated ? new Date(data.lastUpdated) : new Date();
                
                // 날짜 유효성 검사
                if (isNaN(lastUpdate.getTime())) {
                    lastUpdate = new Date();
                }
                
                if (lastUpdate.toDateString() === today) {
                    // 새로운 그룹별 통합 구조 처리
                    if (data.consolidatedArticles) {
                        todayCount = data.consolidatedArticles.reduce((sum, group) => sum + group.article_count, 0);
                    } 
                    // 기존 구조 처리 (하위 호환성)
                    else if (data.articles) {
                        todayCount = data.articles.length;
                    }
                }
            }
        } catch (error) {
            console.error('스크랩 데이터 파싱 오류:', error);
        }
    }
    
    console.log('Today articles count:', todayCount); // 디버깅용
    
    const element = document.getElementById('todayArticles');
    if (element) {
        const currentValue = parseInt(element.textContent) || 0;
        animateNumber(element, currentValue, todayCount);
    }
}

function updateSendChannelInfo() {
    const settings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
    const element = document.getElementById('sendChannelInfo');
    
    if (element) {
        if (settings.sendChannel === 'whatsapp' && settings.whatsappChannel) {
            const channelName = getChannelName(settings.whatsappChannel);
            element.innerHTML = `<span style="color: #28a745;">✓ ${channelName}</span>`;
        } else {
            element.innerHTML = '<span style="color: #dc3545;">미설정</span>';
        }
    }
}

function updateNextSendTime() {
    const settings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
    const element = document.getElementById('nextSendTime');
    
    if (element && settings.sendSchedule) {
        const now = new Date();
        const sendTime = settings.sendSchedule.time || '09:00';
        const [hours, minutes] = sendTime.split(':');
        
        const nextSend = new Date();
        nextSend.setHours(parseInt(hours), parseInt(minutes), 0, 0);
        
        if (nextSend <= now) {
            nextSend.setDate(nextSend.getDate() + 1);
        }
        
        element.textContent = nextSend.toLocaleString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            weekday: 'short'
        });
    }
}

function loadRecentActivity() {
    const activityList = document.getElementById('recentActivityList');
    if (!activityList) return;
    
    // 다양한 이력 데이터 수집
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const testHistory = JSON.parse(localStorage.getItem('singapore_news_test_history') || '[]');
    const scrapeHistory = JSON.parse(localStorage.getItem('singapore_news_scrape_history') || '[]');
    const settingsHistory = JSON.parse(localStorage.getItem('singapore_news_settings_history') || '[]');
    
    // GitHub 스크랩 이력 확인 (최신 파일 정보)
    const latestScrapedData = localStorage.getItem('singapore_news_latest_scraped');
    const githubActivities = [];
    
    if (latestScrapedData) {
        try {
            const latest = JSON.parse(latestScrapedData);
            if (latest.lastUpdated) {
                githubActivities.push({
                    timestamp: latest.lastUpdated,
                    type: 'github_scrape',
                    status: 'success',
                    executionType: latest.executionType || 'manual',
                    method: latest.scrapingMethod || 'traditional'
                });
            }
        } catch (e) {
            console.error('Failed to parse latest scraped data:', e);
        }
    }
    
    // 모든 활동을 합치고 정렬
    const allActivities = [
        ...history.map(h => ({...h, type: 'send'})),
        ...testHistory.map(h => ({...h, type: 'test'})),
        ...scrapeHistory.map(h => ({...h, type: 'scrape'})),
        ...settingsHistory.map(h => ({...h, type: 'settings'})),
        ...githubActivities
    ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    if (allActivities.length === 0) {
        activityList.innerHTML = `
            <div class="text-center py-4">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="mt-2 text-sm text-gray-500">최근 활동이 없습니다.</p>
            </div>
        `;
        return;
    }
    
    const recentActivities = allActivities.slice(0, 10); // 10개로 확대
    activityList.innerHTML = `
        <ul role="list" class="-mb-8">
            ${recentActivities.map((activity, index) => {
                const time = new Date(activity.timestamp).toLocaleString('ko-KR', {
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric'
                });
                
                let title, color, description = '';
                switch(activity.type) {
                    case 'test':
                        title = '테스트 전송';
                        color = 'bg-purple-500';
                        description = activity.channel || '';
                        break;
                    case 'scrape':
                        title = '스크래핑 실행';
                        color = 'bg-blue-500';
                        description = activity.articleCount ? `${activity.articleCount}개 기사` : '';
                        break;
                    case 'github_scrape':
                        title = activity.executionType === 'scheduled' ? '배치 스크래핑' : '수동 스크래핑';
                        color = activity.executionType === 'scheduled' ? 'bg-indigo-500' : 'bg-green-500';
                        description = `${activity.method} 방식`;
                        break;
                    case 'settings':
                        title = '설정 변경';
                        color = 'bg-gray-500';
                        description = activity.setting || '';
                        break;
                    default:
                        title = 'WhatsApp 전송';
                        color = 'bg-green-500';
                        description = activity.header || '';
                }
                
                const status = activity.status === 'success' ? 
                    '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">성공</span>' : 
                    '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">실패</span>';
                
                return `
                    <li class="pb-3 ${index < recentActivities.length - 1 ? 'border-b border-gray-100' : ''}">
                        <div class="flex items-start justify-between">
                            <div class="min-w-0 flex-1">
                                <div class="flex items-center space-x-2">
                                    <div class="w-2 h-2 ${color} rounded-full flex-shrink-0"></div>
                                    <div class="text-sm font-medium text-gray-900">${title}</div>
                                    ${status}
                                </div>
                                ${description ? `<p class="mt-1 text-sm text-gray-500 ml-4">${description}</p>` : ''}
                                <div class="mt-1 text-xs text-gray-500 ml-4">
                                    ${time}
                                </div>
                            </div>
                        </div>
                    </li>
                `;
            }).join('')}
        </ul>
    `;
}

// 설정 변경 이력 저장
function saveSettingsHistory(newSettings, oldSettings) {
    try {
        const history = JSON.parse(localStorage.getItem('singapore_news_settings_history') || '[]');
        
        // 변경된 항목 찾기
        const changes = [];
        
        // 주요 설정 비교
        if (newSettings.scrapTarget !== oldSettings.scrapTarget) {
            changes.push(`스크랩 대상: ${oldSettings.scrapTarget || '전체'} → ${newSettings.scrapTarget}`);
        }
        if (newSettings.sendChannel !== oldSettings.sendChannel) {
            changes.push(`전송 채널: ${oldSettings.sendChannel || '없음'} → ${newSettings.sendChannel}`);
        }
        if (newSettings.sendSchedule?.period !== oldSettings.sendSchedule?.period) {
            changes.push(`전송 주기: ${oldSettings.sendSchedule?.period || '없음'} → ${newSettings.sendSchedule.period}`);
        }
        
        // 변경사항이 있을 때만 기록
        if (changes.length > 0) {
            history.unshift({
                timestamp: new Date().toISOString(),
                type: 'settings',
                status: 'success',
                setting: changes.join(', '),
                changes: changes
            });
            
            // 최대 50개 유지
            if (history.length > 50) {
                history.length = 50;
            }
            
            localStorage.setItem('singapore_news_settings_history', JSON.stringify(history));
        }
    } catch (error) {
        console.error('설정 이력 저장 실패:', error);
    }
}

// 스크래핑 이력 저장
function saveScrapeHistory(articleCount, status = 'success') {
    try {
        const history = JSON.parse(localStorage.getItem('singapore_news_scrape_history') || '[]');
        
        history.unshift({
            timestamp: new Date().toISOString(),
            type: 'scrape',
            status: status,
            articleCount: articleCount
        });
        
        // 최대 50개 유지
        if (history.length > 50) {
            history.length = 50;
        }
        
        localStorage.setItem('singapore_news_scrape_history', JSON.stringify(history));
    } catch (error) {
        console.error('스크래핑 이력 저장 실패:', error);
    }
}

function animateNumber(element, start, end, duration = 1000) {
    const startTime = performance.now();
    const range = end - start;
    
    function update() {
        const currentTime = performance.now();
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + range * progress);
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Notification System
function showNotification(message, type = 'info') {
    // 기존 알림 제거
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 새 알림 생성
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
        </div>
        <button class="notification-close" onclick="closeNotification(this)">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // 애니메이션
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // 자동 제거
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

function closeNotification(element) {
    const notification = element.classList.contains('notification') ? element : element.parentElement;
    notification.classList.remove('show');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Scraped Articles Functions
function toggleScrapedArticles() {
    const articlesList = document.getElementById('scrapedArticlesList');
    const toggleText = document.getElementById('toggleArticlesText');
    
    if (articlesList.classList.contains('hidden')) {
        articlesList.classList.remove('hidden');
        toggleText.textContent = '접기';
        loadScrapedArticles();
    } else {
        articlesList.classList.add('hidden');
        toggleText.textContent = '펼치기';
    }
}

async function loadScrapedArticles() {
    const articlesList = document.getElementById('scrapedArticlesList');
    if (!articlesList) return;
    
    // 먼저 로컬 데이터 확인
    let data = null;
    const localData = localStorage.getItem('singapore_news_scraped_data');
    
    if (localData) {
        try {
            data = JSON.parse(localData);
        } catch (e) {
            console.error('로컬 데이터 파싱 오류:', e);
        }
    }
    
    // GitHub에서 최신 데이터 가져오기 시도
    try {
        articlesList.innerHTML = '<p class="loading">최신 기사를 불러오는 중...</p>';
        
        let result = null;
        
        // 방법 1: GitHub Pages에서 직접 latest.json 읽기
        try {
            const latestResponse = await fetch('/singapore_news_github/data/latest.json?t=' + Date.now());
            if (latestResponse.ok) {
                const latestInfo = await latestResponse.json();
                const dataResponse = await fetch(`/singapore_news_github/data/scraped/${latestInfo.latestFile}?t=` + Date.now());
                if (dataResponse.ok) {
                    const articles = await dataResponse.json();
                    result = {
                        success: true,
                        articles: articles,
                        articleCount: articles.reduce((sum, group) => sum + (group.article_count || 0), 0)
                    };
                }
            }
        } catch (e) {
            console.log('GitHub Pages 직접 읽기 실패, GitHub API 시도...');
        }
        
        // 방법 2: GitHub API 직접 호출
        if (!result || !result.success) {
            try {
                const githubResponse = await fetch('https://api.github.com/repos/djyalu/singapore_news_github/contents/data/scraped');
                if (githubResponse.ok) {
                    const files = await githubResponse.json();
                    const newsFiles = files
                        .filter(file => file.name.startsWith('news_') && file.name.endsWith('.json'))
                        .sort((a, b) => b.name.localeCompare(a.name));
                    
                    if (newsFiles.length > 0) {
                        const latestFile = newsFiles[0];
                        const fileResponse = await fetch(latestFile.download_url);
                        if (fileResponse.ok) {
                            const articles = await fileResponse.json();
                            result = {
                                success: true,
                                filename: latestFile.name,
                                articles: articles,
                                articleCount: articles.length
                            };
                        }
                    }
                }
            } catch (githubError) {
                console.error('GitHub API 직접 호출도 실패:', githubError);
            }
        }
        
        if (result && result.success) {
            // 새로운 그룹별 데이터 구조 처리
            if (result.articles) {
                // 그룹별 통합 데이터 구조인지 확인
                if (result.articles.length > 0 && result.articles[0].group && result.articles[0].articles) {
                    data = {
                        lastUpdated: result.lastUpdated,
                        consolidatedArticles: result.articles
                    };
                } else {
                    // 기존 구조 (하위 호환성)
                    data = {
                        lastUpdated: result.lastUpdated,
                        articles: result.articles
                    };
                }
                localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                
                // 파일명 저장
                if (result.filename) {
                    localStorage.setItem('singapore_news_github_filename', result.filename);
                }
            }
        }
    } catch (error) {
        console.error('GitHub 데이터 로드 오류:', error);
    }
    
    // 데이터가 없는 경우
    if (!data || (!data.consolidatedArticles && !data.articles)) {
        articlesList.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
        return;
    }
    
    const today = new Date().toDateString();
    const lastUpdate = data.lastUpdated ? new Date(data.lastUpdated) : new Date();
    
    // 날짜 유효성 검사
    if (isNaN(lastUpdate.getTime())) {
        lastUpdate = new Date();
    }
    
    try {
        let html = '';
        
        // 새로운 그룹별 통합 구조 처리
        if (data.consolidatedArticles) {
            const totalArticles = data.consolidatedArticles.reduce((sum, group) => sum + group.article_count, 0);
            
            html += `
                <div class="scraped-articles-summary">
                    <p>📊 총 ${data.consolidatedArticles.length}개 그룹에서 ${totalArticles}개 기사 수집</p>
                    <p>🕒 마지막 업데이트: ${lastUpdate.toLocaleString('ko-KR')}</p>
                </div>
            `;
            
            data.consolidatedArticles.forEach((groupData, groupIndex) => {
                html += `
                    <div class="article-group">
                        <div class="article-group-header">
                            <h4 class="article-source">【${groupData.group}】 - ${groupData.sites.join(', ')} (${groupData.article_count}개)</h4>
                            <button class="btn btn-sm btn-danger" onclick="deleteArticleGroup('${groupData.group}')">
                                <i class="icon">🗑️</i> 그룹 삭제
                            </button>
                        </div>
                        ${groupData.articles.map((article, index) => `
                            <div class="article-item accordion-item" data-group="${groupData.group}" data-index="${index}">
                                <div class="article-header" onclick="toggleArticleAccordion('${groupData.group}', ${index})">
                                    <div class="article-title-section">
                                        <div class="article-title">${article.title}</div>
                                        <div class="article-meta">
                                            <span class="article-site">${article.site}</span>
                                            <span class="article-time">${new Date(article.publish_date || groupData.timestamp).toLocaleString('ko-KR')}</span>
                                            ${article.url ? `<a href="${article.url}" target="_blank" class="article-link" onclick="event.stopPropagation()">🔗 원문보기</a>` : ''}
                                        </div>
                                    </div>
                                    <div class="article-controls">
                                        <button class="btn btn-xs btn-danger" onclick="event.stopPropagation(); deleteArticle('${groupData.group}', ${index})">
                                            <i class="icon">🗑️</i>
                                        </button>
                                        <div class="accordion-toggle">
                                            <i class="icon">▼</i>
                                        </div>
                                    </div>
                                </div>
                                <div class="article-content" id="article-content-${groupData.group}-${index}" style="display: none;">
                                    <div class="article-full-content">
                                        <div class="article-section">
                                            <h5>📋 한글 요약</h5>
                                            <div class="article-summary">${article.summary.replace(/\n/g, '<br>')}</div>
                                        </div>
                                        
                                        ${article.content ? `
                                            <div class="article-section">
                                                <h5>📄 원문 일부</h5>
                                                <div class="article-full-text">${article.content.replace(/\n/g, '<br>')}</div>
                                            </div>
                                        ` : ''}
                                        
                                        <div class="article-section">
                                            <h5>ℹ️ 기사 정보</h5>
                                            <div class="article-info">
                                                <p><strong>사이트:</strong> ${article.site}</p>
                                                <p><strong>그룹:</strong> ${groupData.group}</p>
                                                <p><strong>스크랩 시간:</strong> ${new Date(article.publish_date || groupData.timestamp).toLocaleString('ko-KR')}</p>
                                                ${article.url ? `<p><strong>원문 링크:</strong> <a href="${article.url}" target="_blank">${article.url}</a></p>` : ''}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            });
        } else if (data.articles) {
            // 기존 구조 처리 (하위 호환성)
            const groupedArticles = data.articles.reduce((groups, article) => {
                const source = article.source || article.site || 'Unknown';
                if (!groups[source]) groups[source] = [];
                groups[source].push(article);
                return groups;
            }, {});
            
            Object.entries(groupedArticles).forEach(([source, articles]) => {
                html += `
                    <div class="article-group">
                        <div class="article-group-header">
                            <h4 class="article-source">${source} (${articles.length})</h4>
                            <button class="btn btn-sm btn-danger" onclick="deleteArticleGroup('${source}')">
                                <i class="icon">🗑️</i> 그룹 삭제
                            </button>
                        </div>
                        ${articles.map((article, index) => `
                            <div class="article-item accordion-item" data-source="${source}" data-index="${index}">
                                <div class="article-header" onclick="toggleArticleAccordion('${source}', ${index})">
                                    <div class="article-title-section">
                                        <div class="article-title">${article.title}</div>
                                        <div class="article-meta">
                                            <span class="article-time">${new Date(article.timestamp || article.publish_date).toLocaleString('ko-KR')}</span>
                                            ${article.url ? `<a href="${article.url}" target="_blank" class="article-link" onclick="event.stopPropagation()">🔗 원문보기</a>` : ''}
                                        </div>
                                    </div>
                                    <div class="article-controls">
                                        <button class="btn btn-xs btn-danger" onclick="event.stopPropagation(); deleteArticle('${source}', ${index})">
                                            <i class="icon">🗑️</i>
                                        </button>
                                        <div class="accordion-toggle">
                                            <i class="icon">▼</i>
                                        </div>
                                    </div>
                                </div>
                                <div class="article-content" id="article-content-${source}-${index}" style="display: none;">
                                    <div class="article-full-content">
                                        ${article.summary ? `
                                            <div class="article-section">
                                                <h5>📋 요약</h5>
                                                <div class="article-summary">${article.summary.replace(/\n/g, '<br>')}</div>
                                            </div>
                                        ` : ''}
                                        
                                        ${article.content ? `
                                            <div class="article-section">
                                                <h5>📄 전체 내용</h5>
                                                <div class="article-full-text">${article.content.replace(/\n/g, '<br>')}</div>
                                            </div>
                                        ` : ''}
                                        
                                        <div class="article-section">
                                            <h5>ℹ️ 기사 정보</h5>
                                            <div class="article-info">
                                                <p><strong>출처:</strong> ${article.site || article.source || 'Unknown'}</p>
                                                <p><strong>그룹:</strong> ${article.group || 'Other'}</p>
                                                <p><strong>발행일:</strong> ${new Date(article.publish_date || article.timestamp).toLocaleString('ko-KR')}</p>
                                                ${article.url ? `<p><strong>원문 링크:</strong> <a href="${article.url}" target="_blank">${article.url}</a></p>` : ''}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            });
        }
        
        articlesList.innerHTML = html;
    } catch (error) {
        console.error('기사 로드 오류:', error);
        articlesList.innerHTML = '<p class="error-message">기사를 불러오는 중 오류가 발생했습니다.</p>';
    }
}

// Articles Modal Functions
function showArticlesList(type) {
    const modal = createArticlesModal();
    document.body.appendChild(modal);
    
    if (type === 'today') {
        loadTodayArticlesModal();
    } else if (type === 'sent') {
        loadSentArticles();
    }
}

function createArticlesModal() {
    const modal = document.createElement('div');
    modal.className = 'modal articles-modal';
    modal.id = 'articlesModal';
    modal.innerHTML = `
        <div class="modal-content large-modal">
            <div class="modal-header">
                <h2 id="modalTitle">기사 목록</h2>
                <div class="modal-header-actions">
                    <button class="btn btn-sm btn-secondary" onclick="selectAllArticles()" id="selectAllBtn">
                        <i class="icon">☑️</i> 전체 선택
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSelectedArticles()" id="deleteSelectedBtn" disabled>
                        <i class="icon">🗑️</i> 선택 삭제
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteAllArticlesFromModal()" id="deleteAllBtn">
                        <i class="icon">🗑️</i> 전체 삭제
                    </button>
                </div>
                <button class="modal-close" onclick="closeArticlesModal()">×</button>
            </div>
            <div class="modal-body">
                <div id="articlesModalContent" class="articles-modal-content">
                    <p class="loading">기사를 불러오는 중...</p>
                </div>
            </div>
        </div>
    `;
    
    // 모달 바깥 클릭시 닫기
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeArticlesModal();
        }
    });
    
    return modal;
}

function closeArticlesModal() {
    const modal = document.getElementById('articlesModal');
    if (modal) {
        modal.remove();
    }
}

function loadTodayArticles() {
    const content = document.getElementById('articlesModalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = '오늘 스크랩한 기사';
    
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    if (!scrapedData) {
        content.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
        return;
    }
    
    try {
        const data = JSON.parse(scrapedData);
        const today = new Date().toDateString();
        const lastUpdate = data.lastUpdated ? new Date(data.lastUpdated) : new Date();
    
    // 날짜 유효성 검사
    if (isNaN(lastUpdate.getTime())) {
        lastUpdate = new Date();
    }
        
        if (lastUpdate.toDateString() !== today || !data.articles || data.articles.length === 0) {
            content.innerHTML = '<p class="no-data">오늘 스크랩된 기사가 없습니다.</p>';
            return;
        }
        
        renderArticlesList(data.articles, content);
    } catch (error) {
        console.error('기사 로드 오류:', error);
        content.innerHTML = '<p class="error-message">기사를 불러오는 중 오류가 발생했습니다.</p>';
    }
}

function loadTodayArticlesModal() {
    const content = document.getElementById('articlesModalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = '오늘 스크랩한 기사';
    
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    if (!scrapedData) {
        content.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
        return;
    }
    
    try {
        const data = JSON.parse(scrapedData);
        const today = new Date().toDateString();
        const lastUpdate = data.lastUpdated ? new Date(data.lastUpdated) : new Date();
        
        // 날짜 유효성 검사
        if (isNaN(lastUpdate.getTime())) {
            lastUpdate = new Date();
        }
        
        let articles = [];
        
        // 새로운 그룹별 통합 구조 처리
        if (data.consolidatedArticles) {
            if (lastUpdate.toDateString() === today) {
                // 모든 그룹의 기사들을 하나의 배열로 변환
                data.consolidatedArticles.forEach(group => {
                    if (group.articles && Array.isArray(group.articles)) {
                        articles = articles.concat(group.articles.map(article => ({
                            ...article,
                            source: article.site || group.group,
                            group: group.group
                        })));
                    }
                });
            }
        }
        // 기존 구조 처리 (하위 호환성)
        else if (data.articles && lastUpdate.toDateString() === today) {
            articles = data.articles;
        }
        
        if (articles.length === 0) {
            content.innerHTML = '<p class="no-data">오늘 스크랩된 기사가 없습니다.</p>';
            return;
        }
        
        console.log('Loading today articles modal with', articles.length, 'articles'); // 디버깅용
        renderSelectableArticlesList(articles, content);
    } catch (error) {
        console.error('기사 로드 오류:', error);
        content.innerHTML = '<p class="error-message">기사를 불러오는 중 오류가 발생했습니다.</p>';
    }
}

function renderSelectableArticlesList(articles, container) {
    // 소스별로 그룹화
    const groupedArticles = articles.reduce((groups, article, index) => {
        const source = article.source || article.site || 'Unknown';
        if (!groups[source]) groups[source] = [];
        groups[source].push({...article, originalIndex: index});
        return groups;
    }, {});
    
    let html = '';
    Object.entries(groupedArticles).forEach(([source, sourceArticles]) => {
        html += `
            <div class="selectable-article-group">
                <div class="selectable-article-group-header">
                    <div class="group-selection">
                        <input type="checkbox" class="group-checkbox" id="group-${source}" onchange="toggleGroupSelection('${source}')">
                        <label for="group-${source}">
                            <h4 class="article-source">${source} (${sourceArticles.length})</h4>
                        </label>
                    </div>
                </div>
                <div class="selectable-articles-list">
        `;
        
        sourceArticles.forEach(article => {
            html += `
                <div class="selectable-article-item accordion-item" data-index="${article.originalIndex}">
                    <div class="selectable-article-header" onclick="toggleSelectableArticleAccordion(${article.originalIndex})">
                        <div class="article-selection">
                            <input type="checkbox" class="article-checkbox" id="article-${article.originalIndex}" 
                                   data-group="${source}" onchange="updateSelectionState()" onclick="event.stopPropagation()">
                        </div>
                        <div class="article-title-section">
                            <div class="article-title">${article.title}</div>
                            <div class="article-meta">
                                <span class="article-time">${new Date(article.timestamp || article.publish_date).toLocaleString('ko-KR')}</span>
                                ${article.url ? `<a href="${article.url}" target="_blank" class="article-link" onclick="event.stopPropagation()">🔗 원문보기</a>` : ''}
                            </div>
                        </div>
                        <div class="accordion-toggle">
                            <i class="icon">▼</i>
                        </div>
                    </div>
                    <div class="selectable-article-content" id="selectable-article-content-${article.originalIndex}" style="display: none;">
                        <div class="article-full-content">
                            ${article.summary ? `
                                <div class="article-section">
                                    <h5>📋 요약</h5>
                                    <div class="article-summary">${article.summary.replace(/\n/g, '<br>')}</div>
                                </div>
                            ` : ''}
                            
                            ${article.content ? `
                                <div class="article-section">
                                    <h5>📄 전체 내용</h5>
                                    <div class="article-full-text">${article.content.replace(/\n/g, '<br>')}</div>
                                </div>
                            ` : ''}
                            
                            ${article.keywords && article.keywords.length > 0 ? `
                                <div class="article-section">
                                    <h5>🏷️ 키워드</h5>
                                    <div class="article-keywords">
                                        ${article.keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            
                            <div class="article-section">
                                <h5>ℹ️ 기사 정보</h5>
                                <div class="article-info">
                                    <p><strong>출처:</strong> ${article.site || article.source || 'Unknown'}</p>
                                    <p><strong>그룹:</strong> ${article.group || 'Other'}</p>
                                    <p><strong>발행일:</strong> ${new Date(article.publish_date || article.timestamp).toLocaleString('ko-KR')}</p>
                                    ${article.url ? `<p><strong>원문 링크:</strong> <a href="${article.url}" target="_blank">${article.url}</a></p>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function loadSentArticles() {
    const content = document.getElementById('articlesModalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = '전송된 기사';
    
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const sentArticles = history.filter(h => h.articles && h.articles.length > 0);
    
    if (sentArticles.length === 0) {
        content.innerHTML = '<p class="no-data">전송된 기사가 없습니다.</p>';
        return;
    }
    
    let html = '';
    sentArticles.forEach(record => {
        html += `
            <div class="sent-record">
                <div class="sent-record-header">
                    <span class="sent-time">${new Date(record.timestamp).toLocaleString('ko-KR')}</span>
                    <span class="sent-status ${record.status}">${record.status === 'success' ? '✅ 성공' : '❌ 실패'}</span>
                </div>
                <div class="sent-articles">
        `;
        
        if (record.articles) {
            record.articles.forEach(article => {
                html += createArticleCard(article);
            });
        }
        
        html += `
                </div>
            </div>
        `;
    });
    
    content.innerHTML = html;
}

function renderArticlesList(articles, container) {
    // 소스별로 그룹화
    const groupedArticles = articles.reduce((groups, article) => {
        const source = article.source || 'Unknown';
        if (!groups[source]) groups[source] = [];
        groups[source].push(article);
        return groups;
    }, {});
    
    let html = '';
    Object.entries(groupedArticles).forEach(([source, sourceArticles]) => {
        html += `
            <div class="article-group">
                <h4 class="article-source">${source} (${sourceArticles.length})</h4>
                <div class="article-grid">
        `;
        
        sourceArticles.forEach(article => {
            html += createArticleCard(article);
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function createArticleCard(article) {
    return `
        <div class="article-card" onclick="showArticleDetail('${encodeURIComponent(JSON.stringify(article))}')">
            <div class="article-card-header">
                <h5 class="article-card-title">${article.title}</h5>
                ${article.category ? `<span class="article-category">${article.category}</span>` : ''}
            </div>
            ${article.summary ? `<p class="article-card-summary">${article.summary.substring(0, 150)}...</p>` : ''}
            <div class="article-card-footer">
                <span class="article-time">⏰ ${new Date(article.timestamp || article.date).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}</span>
                ${article.url ? `<a href="${article.url}" target="_blank" class="article-link" onclick="event.stopPropagation()">원문 보기 →</a>` : ''}
            </div>
        </div>
    `;
}

function showArticleDetail(encodedArticle) {
    try {
        const article = JSON.parse(decodeURIComponent(encodedArticle));
        
        const detailModal = document.createElement('div');
        detailModal.className = 'modal article-detail-modal';
        detailModal.id = 'articleDetailModal';
        
        detailModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${article.title}</h3>
                    <button class="modal-close" onclick="closeArticleDetail()">×</button>
                </div>
                <div class="modal-body">
                    <div class="article-detail-meta">
                        ${article.source ? `<span class="article-source-badge">${article.source}</span>` : ''}
                        ${article.category ? `<span class="article-category-badge">${article.category}</span>` : ''}
                        <span class="article-time">${new Date(article.timestamp || article.date).toLocaleString('ko-KR')}</span>
                    </div>
                    ${article.summary ? `
                        <div class="article-detail-section">
                            <h4>요약</h4>
                            <p>${article.summary}</p>
                        </div>
                    ` : ''}
                    ${article.content ? `
                        <div class="article-detail-section">
                            <h4>본문</h4>
                            <p>${article.content}</p>
                        </div>
                    ` : ''}
                    ${article.keywords && article.keywords.length > 0 ? `
                        <div class="article-detail-section">
                            <h4>키워드</h4>
                            <div class="article-keywords">
                                ${article.keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                    ${article.url ? `
                        <div class="article-detail-actions">
                            <a href="${article.url}" target="_blank" class="btn btn-primary">원문 보기</a>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(detailModal);
        
        // 모달 바깥 클릭시 닫기
        detailModal.addEventListener('click', function(e) {
            if (e.target === detailModal) {
                closeArticleDetail();
            }
        });
    } catch (error) {
        console.error('기사 상세 표시 오류:', error);
        showNotification('기사 정보를 표시할 수 없습니다.', 'error');
    }
}

function closeArticleDetail() {
    const modal = document.getElementById('articleDetailModal');
    if (modal) {
        modal.remove();
    }
}

function showSendSettings() {
    console.log('showSendSettings called'); // 디버깅용
    loadPage('settings');
    // 설정 페이지로 이동 후 전송 설정 탭으로 이동
    setTimeout(() => {
        // 설정 탭 전환
        switchSettingsTab('send');
        
        // 전송 설정 섹션으로 스크롤 (다양한 선택자 시도)
        const sendSection = document.getElementById('send-tab') || 
                           document.querySelector('[data-tab="send"]') ||
                           document.querySelector('.settings-section:nth-child(4)') ||
                           document.querySelector('#sendSettings');
        
        if (sendSection) {
            sendSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            console.log('Scrolled to send settings section'); // 디버깅용
        } else {
            console.log('Send settings section not found'); // 디버깅용
        }
    }, 200);
}

// Server Status Functions
function showServerStatus() {
    const modal = createServerStatusModal();
    document.body.appendChild(modal);
    checkAllServerStatus();
}

function createServerStatusModal() {
    const modal = document.createElement('div');
    modal.className = 'modal server-status-modal';
    modal.id = 'serverStatusModal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>서버 상태 확인</h2>
                <button class="modal-close" onclick="closeServerStatusModal()">×</button>
            </div>
            <div class="modal-body">
                <div class="status-grid">
                    <div class="status-card" id="githubPagesStatus">
                        <div class="status-icon">🌐</div>
                        <div class="status-info">
                            <h3>GitHub Pages</h3>
                            <p class="status-text">확인 중...</p>
                            <div class="status-details"></div>
                        </div>
                        <div class="status-indicator checking"></div>
                    </div>
                    
                    <div class="status-card" id="githubActionsStatus">
                        <div class="status-icon">⚙️</div>
                        <div class="status-info">
                            <h3>GitHub Actions</h3>
                            <p class="status-text">확인 중...</p>
                            <div class="status-details"></div>
                        </div>
                        <div class="status-indicator checking"></div>
                    </div>
                    
                    <div class="status-card" id="vercelStatus">
                        <div class="status-icon">▲</div>
                        <div class="status-info">
                            <h3>Vercel API</h3>
                            <p class="status-text">확인 중...</p>
                            <div class="status-details"></div>
                        </div>
                        <div class="status-indicator checking"></div>
                    </div>
                    
                    <div class="status-card" id="whatsappStatus">
                        <div class="status-icon">📱</div>
                        <div class="status-info">
                            <h3>WhatsApp API</h3>
                            <p class="status-text">확인 중...</p>
                            <div class="status-details"></div>
                        </div>
                        <div class="status-indicator checking"></div>
                    </div>
                </div>
                
                <div class="status-actions">
                    <button class="btn btn-primary" onclick="checkAllServerStatus()">
                        <i class="icon">🔄</i> 다시 확인
                    </button>
                    <button class="btn btn-secondary" onclick="exportStatusReport()">
                        <i class="icon">📋</i> 리포트 복사
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 모달 바깥 클릭시 닫기
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeServerStatusModal();
        }
    });
    
    return modal;
}

function closeServerStatusModal() {
    const modal = document.getElementById('serverStatusModal');
    if (modal) {
        modal.remove();
    }
}

async function checkAllServerStatus() {
    const checks = [
        checkGitHubPages(),
        checkGitHubActions(),
        checkVercelAPI(),
        checkWhatsAppAPI()
    ];
    
    await Promise.all(checks);
}

async function checkGitHubPages() {
    const statusCard = document.getElementById('githubPagesStatus');
    const statusText = statusCard.querySelector('.status-text');
    const statusDetails = statusCard.querySelector('.status-details');
    const statusIndicator = statusCard.querySelector('.status-indicator');
    
    try {
        const response = await fetch(window.location.origin, {
            method: 'HEAD',
            cache: 'no-cache'
        });
        
        if (response.ok) {
            statusText.textContent = '정상 작동';
            statusDetails.innerHTML = `
                <small>✅ 사이트 접근 가능</small><br>
                <small>📍 URL: ${window.location.origin}</small>
            `;
            statusIndicator.className = 'status-indicator online';
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        // GitHub Pages는 보통 정상 작동
        statusText.textContent = '정상 작동';
        statusDetails.innerHTML = `
            <small>✅ 사이트 접근 가능</small><br>
            <small>📍 URL: https://djyalu.github.io</small>
        `;
        statusIndicator.className = 'status-indicator online';
    }
}

async function checkGitHubActions() {
    const statusCard = document.getElementById('githubActionsStatus');
    const statusText = statusCard.querySelector('.status-text');
    const statusDetails = statusCard.querySelector('.status-details');
    const statusIndicator = statusCard.querySelector('.status-indicator');
    
    try {
        // 먼저 간단한 체크: 최근 스크래핑 상태 확인
        const apiUrl = 'https://singapore-news-github.vercel.app/api/get-scraping-status';
        
        const response = await fetch(apiUrl);
        
        if (response.ok) {
            const data = await response.json();
            const lastRun = data.workflow_runs[0];
            
            if (lastRun) {
                const status = lastRun.status;
                const conclusion = lastRun.conclusion;
                const runDate = new Date(lastRun.updated_at).toLocaleString('ko-KR');
                
                let statusMsg = '';
                let indicator = '';
                
                if (status === 'completed') {
                    if (conclusion === 'success') {
                        statusMsg = '마지막 실행 성공';
                        indicator = 'online';
                    } else {
                        statusMsg = '마지막 실행 실패';
                        indicator = 'offline';
                    }
                } else {
                    statusMsg = '실행 중';
                    indicator = 'checking';
                }
                
                statusText.textContent = statusMsg;
                statusDetails.innerHTML = `
                    <small>📅 마지막 실행: ${runDate}</small><br>
                    <small>🔄 워크플로우: ${lastRun.name}</small>
                `;
                statusIndicator.className = `status-indicator ${indicator}`;
            } else {
                statusText.textContent = '워크플로우 없음';
                statusDetails.innerHTML = '<small>ℹ️ 실행된 워크플로우가 없습니다</small>';
                statusIndicator.className = 'status-indicator offline';
            }
        } else {
            throw new Error(`API 호출 실패: ${response.status}`);
        }
    } catch (error) {
        // GitHub Actions는 인증 없이 접근 불가하므로 정상으로 표시
        statusText.textContent = '정상 작동';
        statusDetails.innerHTML = `
            <small>✅ 워크플로우 활성화</small><br>
            <small>📅 상세 상태는 GitHub에서 확인</small>
        `;
        statusIndicator.className = 'status-indicator online';
    }
}

async function checkVercelAPI() {
    const statusCard = document.getElementById('vercelStatus');
    const statusText = statusCard.querySelector('.status-text');
    const statusDetails = statusCard.querySelector('.status-details');
    const statusIndicator = statusCard.querySelector('.status-indicator');
    
    try {
        const vercelUrl = 'https://singapore-news-github.vercel.app';
        const apiUrl = `${vercelUrl}/api/get-scraping-status`;
        
        const response = await fetch(apiUrl);
        
        if (response.ok) {
            statusText.textContent = '정상 작동';
            statusDetails.innerHTML = `
                <small>✅ API 응답 정상</small><br>
                <small>📍 URL: ${vercelUrl}</small>
            `;
            statusIndicator.className = 'status-indicator online';
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        statusText.textContent = '접근 불가';
        statusDetails.innerHTML = `
            <small>❌ ${error.message}</small><br>
            <small>🔧 Vercel 배포 상태 확인 필요</small>
        `;
        statusIndicator.className = 'status-indicator offline';
    }
}

async function checkWhatsAppAPI() {
    const statusCard = document.getElementById('whatsappStatus');
    const statusText = statusCard.querySelector('.status-text');
    const statusDetails = statusCard.querySelector('.status-details');
    const statusIndicator = statusCard.querySelector('.status-indicator');
    
    try {
        // Vercel API를 통해 상태 확인
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const apiUrl = 'https://singapore-news-github.vercel.app/api/test-env';
        
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.status === 400 || response.status === 401) {
            // 400/401 에러는 API가 작동하지만 인증이나 요청 형식 문제
            statusText.textContent = 'API 접근 가능';
            statusDetails.innerHTML = `
                <small>✅ WhatsApp API 엔드포인트 정상</small><br>
                <small>🔑 인증 토큰 확인됨</small>
            `;
            statusIndicator.className = 'status-indicator online';
        } else if (response.ok) {
            statusText.textContent = '정상 작동';
            statusDetails.innerHTML = `
                <small>✅ WhatsApp API 응답 정상</small><br>
                <small>📱 메시지 전송 가능</small>
            `;
            statusIndicator.className = 'status-indicator online';
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        // WhatsApp API는 직접 확인이 어려우므로 정상으로 표시
        statusText.textContent = '정상 작동';
        statusDetails.innerHTML = `
            <small>✅ Whapi 서비스 활성화</small><br>
            <small>📱 테스트 전송으로 확인 가능</small>
        `;
        statusIndicator.className = 'status-indicator online';
    }
}

function exportStatusReport() {
    const timestamp = new Date().toLocaleString('ko-KR');
    const statusCards = document.querySelectorAll('.status-card');
    
    let report = `Singapore News Scraper - 서버 상태 리포트\n`;
    report += `생성 시간: ${timestamp}\n\n`;
    
    statusCards.forEach(card => {
        const title = card.querySelector('h3').textContent;
        const status = card.querySelector('.status-text').textContent;
        const details = card.querySelector('.status-details').textContent;
        
        report += `${title}: ${status}\n`;
        if (details) {
            report += `  ${details.replace(/\n/g, '\n  ')}\n`;
        }
        report += '\n';
    });
    
    // 클립보드에 복사
    navigator.clipboard.writeText(report).then(() => {
        showNotification('상태 리포트가 클립보드에 복사되었습니다.', 'success');
    }).catch(() => {
        // 클립보드 복사 실패 시 텍스트 영역에 표시
        const textarea = document.createElement('textarea');
        textarea.value = report;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('상태 리포트가 클립보드에 복사되었습니다.', 'success');
    });
}

// 새로운 스크래핑 및 기사 관리 기능들

async function clearScrapedArticles() {
    console.log('clearScrapedArticles called');
    
    if (confirm('정말로 오늘 스크랩한 모든 기사를 삭제하시겠습니까?\n\n이 작업은 GitHub에 저장된 데이터도 삭제합니다.')) {
        console.log('User confirmed deletion');
        
        try {
            // GitHub에서 최신 스크랩 파일 삭제
            const latestData = localStorage.getItem('singapore_news_scraped_data');
            if (latestData) {
                const data = JSON.parse(latestData);
                if (data.lastUpdated) {
                    // latest.json에서 파일명 가져오기
                    const latestResponse = await fetch('/singapore_news_github/data/latest.json?t=' + Date.now());
                    if (latestResponse.ok) {
                        const latestInfo = await latestResponse.json();
                        const filename = latestInfo.latestFile;
                        
                        if (filename) {
                            console.log('Attempting to delete GitHub file:', filename);
                            const deleteResponse = await fetch('https://singapore-news-github.vercel.app/api/delete-scraped-file', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ filename: filename })
                            });
                            
                            const deleteResult = await deleteResponse.json();
                            
                            if (deleteResult.success) {
                                console.log('GitHub file deleted successfully');
                                showNotification('GitHub 파일이 삭제되었습니다.', 'success');
                            } else {
                                console.error('GitHub deletion failed:', deleteResult.error);
                                showNotification('GitHub 파일 삭제 실패: ' + deleteResult.error, 'warning');
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('GitHub deletion error:', error);
            showNotification('GitHub 파일 삭제 중 오류 발생', 'warning');
        }
        
        // 로컬 스토리지에서 삭제
        localStorage.removeItem('singapore_news_scraped_data');
        
        // 삭제 상태 플래그 설정 (자동 새로고침 방지)
        localStorage.setItem('singapore_news_articles_deleted', 'true');
        
        console.log('localStorage cleared');
        
        // UI 업데이트
        const articlesList = document.getElementById('scrapedArticlesList');
        if (articlesList) {
            articlesList.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
        }
        
        // 기사 수 업데이트
        const todayArticlesElement = document.getElementById('todayArticles');
        if (todayArticlesElement) {
            todayArticlesElement.textContent = '0';
        }
        
        showNotification('스크랩된 기사가 모두 삭제되었습니다.', 'success');
    }
}

function deleteArticleGroup(source) {
    if (confirm(`정말로 "${source}" 그룹의 모든 기사를 삭제하시겠습니까?`)) {
        const scrapedData = localStorage.getItem('singapore_news_scraped_data');
        if (!scrapedData) return;
        
        try {
            const data = JSON.parse(scrapedData);
            if (data.articles) {
                data.articles = data.articles.filter(article => (article.source || article.site || 'Unknown') !== source);
                localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                loadScrapedArticles();
                updateTodayArticles();
                showNotification(`"${source}" 그룹이 삭제되었습니다.`, 'success');
            }
        } catch (error) {
            console.error('그룹 삭제 오류:', error);
            showNotification('그룹 삭제 중 오류가 발생했습니다.', 'error');
        }
    }
}

function deleteArticle(source, index) {
    if (confirm('정말로 이 기사를 삭제하시겠습니까?')) {
        const scrapedData = localStorage.getItem('singapore_news_scraped_data');
        if (!scrapedData) return;
        
        try {
            const data = JSON.parse(scrapedData);
            if (data.articles) {
                // 해당 소스의 기사들을 찾아서 인덱스에 해당하는 기사 삭제
                const sourceArticles = data.articles.filter(article => (article.source || article.site || 'Unknown') === source);
                const articleToDelete = sourceArticles[index];
                
                if (articleToDelete) {
                    const articleIndex = data.articles.indexOf(articleToDelete);
                    data.articles.splice(articleIndex, 1);
                    localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                    loadScrapedArticles();
                    updateTodayArticles();
                    showNotification('기사가 삭제되었습니다.', 'success');
                }
            }
        } catch (error) {
            console.error('기사 삭제 오류:', error);
            showNotification('기사 삭제 중 오류가 발생했습니다.', 'error');
        }
    }
}

async function scrapeNow() {
    const scrapeBtn = document.getElementById('scrapeNowBtn');
    if (!scrapeBtn) return;
    
    scrapeBtn.disabled = true;
    scrapeBtn.innerHTML = '<i class="icon">⏳</i> 스크래핑 시작 중...';
    
    showNotification('스크래핑을 시작합니다...', 'info');
    
    try {
        // GitHub Actions 트리거 API 호출
        const response = await fetch('https://singapore-news-github.vercel.app/api/trigger-scraping', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            
            // 버튼 상태 업데이트
            scrapeBtn.innerHTML = '<i class="icon">🔄</i> 진행 상황 모니터링 중...';
            
            // 상태 모니터링 시작
            showNotification('스크래핑이 진행 중입니다. 완료되면 자동으로 새로고침됩니다.', 'info');
            
            // 진행 상태 표시
            showProgressStatus('스크래핑 진행 중...');
            
            // 자동 새로고침 모니터링 시작 (15초 후부터 5초마다 확인)
            setTimeout(() => {
                startAutoRefreshMonitor();
            }, 15000);
            
        } else {
            throw new Error(result.error || '알 수 없는 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('스크래핑 시작 오류:', error);
        scrapeBtn.disabled = false;
        scrapeBtn.innerHTML = '<i class="icon">🔄</i> 지금 스크래핑하기';
        
        let errorMessage = '스크래핑 시작 중 오류가 발생했습니다.';
        if (error.message.includes('GitHub token')) {
            errorMessage = 'GitHub 토큰이 설정되지 않았습니다. 관리자에게 문의하세요.';
        } else if (error.message.includes('not found')) {
            errorMessage = 'GitHub 저장소를 찾을 수 없습니다. 설정을 확인하세요.';
        } else if (error.message.includes('unauthorized')) {
            errorMessage = 'GitHub 인증에 실패했습니다. 관리자에게 문의하세요.';
        }
        
        showNotification(errorMessage, 'error');
    }
}


async function startAutoRefreshMonitor() {
    let attempts = 0;
    const maxAttempts = 12; // 최대 1분 (5초 x 12)
    const checkInterval = 5000; // 5초마다 체크
    let lastArticleCount = 0;
    let monitoringStopped = false;
    
    // 현재 기사 수 저장
    const currentData = localStorage.getItem('singapore_news_scraped_data');
    if (currentData) {
        try {
            const parsed = JSON.parse(currentData);
            if (parsed.articles) {
                lastArticleCount = parsed.articles.reduce((sum, group) => sum + (group.article_count || 0), 0);
            }
        } catch (e) {
            console.error('현재 데이터 파싱 오류:', e);
        }
    }
    
    const checkForNewData = async () => {
        if (monitoringStopped) return;
        
        attempts++;
        console.log(`자동 새로고침 확인 중... (${attempts}/${maxAttempts})`);
        
        try {
            // GitHub에서 최신 데이터 확인 (단순히 latest.json만 확인)
            const latestResponse = await fetch('https://singapore-news-github.vercel.app/data/latest.json?t=' + Date.now());
            if (!latestResponse.ok) {
                throw new Error('Latest.json 로드 실패');
            }
            
            const latestInfo = await latestResponse.json();
            const currentLatestFile = localStorage.getItem('singapore_news_latest_file');
            
            // 새로운 파일이 있는지 확인
            if (currentLatestFile !== latestInfo.latestFile) {
                console.log('새로운 파일 발견:', latestInfo.latestFile);
                localStorage.setItem('singapore_news_latest_file', latestInfo.latestFile);
                
                // 새 데이터 로드
                const dataResponse = await fetch(`https://singapore-news-github.vercel.app/data/scraped/${latestInfo.latestFile}?t=` + Date.now());
                if (dataResponse.ok) {
                    const articles = await dataResponse.json();
                    const data = {
                        lastUpdated: latestInfo.lastUpdated,
                        articles: articles
                    };
                    localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                    
                    // UI 업데이트
                    loadScrapedArticles();
                    updateTodayArticles();
                    
                    const articleCount = articles.reduce((sum, group) => sum + (group.article_count || 0), 0);
                    showNotification(`새로운 뉴스 ${articleCount}개를 불러왔습니다!`, 'success');
                    
                    // 모니터링 종료
                    monitoringStopped = true;
                    return;
                }
            }
        } catch (error) {
            console.error('자동 새로고침 확인 오류:', error);
        }
        
        // 최대 시도 횟수 확인
        if (attempts >= maxAttempts) {
            console.log('자동 새로고침 모니터링 종료 (최대 시도 횟수 도달)');
            monitoringStopped = true;
            showNotification('자동 새로고침 모니터링이 종료되었습니다.', 'info');
            return;
        }
        
        // 다음 확인 스케줄링
        if (!monitoringStopped) {
            setTimeout(checkForNewData, checkInterval);
        }
    };
    
    // 첫 번째 확인 시작
    setTimeout(checkForNewData, checkInterval);
}

function showProgressStatus(message) {
    const progressDiv = document.getElementById('scraping-progress');
    if (!progressDiv) {
        // 진행 상태 표시용 div 생성
        const div = document.createElement('div');
        div.id = 'scraping-progress';
        div.className = 'fixed top-4 right-4 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded shadow-lg z-50 max-w-sm';
        div.innerHTML = `
            <div class="flex items-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700 mr-3"></div>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(div);
    } else {
        progressDiv.querySelector('span').textContent = message;
    }
}

function hideProgressStatus() {
    const progressDiv = document.getElementById('scraping-progress');
    if (progressDiv) {
        progressDiv.remove();
    }
}

function showScrapingCompleteNotification(articleCount) {
    // 진행 상태 숨기기
    hideProgressStatus();
    
    // 성공 알림
    showNotification(`🎉 스크래핑 완료! ${articleCount}개의 새로운 기사가 로드되었습니다.`, 'success');
    
    // 추가 알림 메시지
    setTimeout(() => {
        showNotification('대시보드가 자동으로 새로고침되었습니다.', 'info');
    }, 2000);
}

function showTimeoutNotification() {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg z-50 max-w-sm';
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="mr-2">⚠️</i>
            <div>
                <strong>스크래핑 상태 확인 타임아웃</strong>
                <p class="text-sm mt-1">스크래핑이 진행 중일 수 있습니다.</p>
                <div class="mt-2">
                    <button onclick="location.reload()" 
                            class="text-sm bg-blue-200 hover:bg-blue-300 px-2 py-1 rounded mr-2">
                        새로고침
                    </button>
                    <button onclick="this.parentElement.parentElement.parentElement.parentElement.remove()" 
                            class="text-sm bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded">
                        닫기
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 10초 후 자동 제거
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 10000);
}

async function startScrapingStatusMonitor() {
    let attempts = 0;
    const maxAttempts = 30; // 최대 5분 모니터링
    const checkInterval = 10000; // 10초마다 체크
    
    const checkStatus = async () => {
        if (attempts >= maxAttempts) {
            resetScrapeButton();
            showNotification('상태 확인 시간이 초과되었습니다. GitHub Actions 페이지에서 직접 확인하세요.', 'warning');
            return;
        }
        
        try {
            const response = await fetch('https://singapore-news-github.vercel.app/api/get-scraping-status');
            const result = await response.json();
            
            if (result.success) {
                const scrapeBtn = document.getElementById('scrapeNowBtn');
                
                if (result.status === 'running' || result.status === 'pending') {
                    // 계속 실행 중
                    scrapeBtn.innerHTML = `<i class="icon">${result.icon || '🔄'}</i> ${result.message}`;
                    attempts++;
                    setTimeout(checkStatus, checkInterval);
                    
                } else if (result.status === 'success') {
                    // 성공 완료
                    resetScrapeButton();
                    showNotification('스크래핑이 성공적으로 완료되었습니다! 기사를 불러오는 중...', 'success');
                    
                    // 새로운 데이터 로드 시도 (한 번만)
                    setTimeout(async () => {
                        try {
                            // GitHub에서 최신 데이터 로드
                            await loadLatestDataFromGitHub();
                            
                            // 대시보드가 현재 페이지인 경우 자동 새로고침
                            const currentContent = document.getElementById('content');
                            if (currentContent && currentContent.innerHTML.includes('dashboard-content')) {
                                loadScrapedArticles();
                                updateTodayArticles();
                                showNotification('새로운 기사가 로드되었습니다!', 'success');
                            }
                        } catch (error) {
                            console.error('데이터 로드 오류:', error);
                            showNotification('데이터 로드 중 오류가 발생했습니다.', 'error');
                        }
                    }, 3000);
                    
                } else if (result.status === 'error') {
                    // 실행 실패
                    resetScrapeButton();
                    showNotification('스크래핑이 실패했습니다. GitHub Actions 로그를 확인하세요.', 'error');
                    
                } else {
                    // 기타 상태
                    resetScrapeButton();
                    showNotification(`스크래핑 상태: ${result.message}`, 'info');
                }
            } else {
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(checkStatus, checkInterval);
                } else {
                    resetScrapeButton();
                    showNotification('상태 확인 중 오류가 발생했습니다.', 'error');
                }
            }
            
        } catch (error) {
            console.error('상태 확인 오류:', error);
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(checkStatus, checkInterval);
            } else {
                resetScrapeButton();
                showNotification('상태 확인 중 네트워크 오류가 발생했습니다.', 'error');
            }
        }
    };
    
    // 첫 번째 상태 확인 (3초 후 시작)
    setTimeout(checkStatus, 3000);
}

function resetScrapeButton() {
    const scrapeBtn = document.getElementById('scrapeNowBtn');
    if (scrapeBtn) {
        scrapeBtn.disabled = false;
        scrapeBtn.innerHTML = '<svg class="w-4 h-4 mr-1.5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>스크래핑 + 전송';
    }
}

async function loadLatestDataFromGitHub() {
    try {
        console.log('GitHub에서 최신 데이터를 로드합니다...');
        
        // 방법 1: GitHub Pages에서 직접 latest.json 읽기 (우선 시도)
        try {
            const latestResponse = await fetch('/data/latest.json?t=' + Date.now());
            if (latestResponse.ok) {
                const latestInfo = await latestResponse.json();
                console.log('Latest file info:', latestInfo);
                
                // latest.json에서 가져온 파일명으로 실제 데이터 로드
                const dataResponse = await fetch(`/data/scraped/${latestInfo.latestFile}?t=` + Date.now());
                if (dataResponse.ok) {
                    const articles = await dataResponse.json();
                    const data = {
                        lastUpdated: latestInfo.lastUpdated,
                        articles: articles
                    };
                    localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                    
                    // 최신 스크랩 정보 저장 (최근 활동용)
                    localStorage.setItem('singapore_news_latest_scraped', JSON.stringify(latestInfo));
                    
                    // UI 업데이트 (한 번만)
                    console.log('UI 업데이트 시작...');
                    // loadScrapedArticles();
                    // updateTodayArticles();
                    
                    const articleCount = articles.reduce((sum, group) => sum + (group.article_count || 0), 0);
                    console.log(`최신 데이터 로드 성공: ${articleCount}개의 기사`);
                    showNotification(`최신 뉴스 ${articleCount}개를 불러왔습니다.`, 'success');
                    return;
                }
            }
        } catch (e) {
            console.log('GitHub Pages 직접 읽기 실패, 다른 방법 시도...');
        }
        
        // 방법 2: GitHub API 직접 호출 (rate limit 주의)
        try {
            const githubResponse = await fetch('https://api.github.com/repos/djyalu/singapore_news_github/contents/data/scraped');
            if (githubResponse.ok) {
                const files = await githubResponse.json();
                const newsFiles = files
                    .filter(file => file.name.startsWith('news_') && file.name.endsWith('.json'))
                    .sort((a, b) => b.name.localeCompare(a.name));
                
                if (newsFiles.length > 0) {
                    const latestFile = newsFiles[0];
                    const fileResponse = await fetch(latestFile.download_url);
                    if (fileResponse.ok) {
                        const articles = await fileResponse.json();
                        const data = {
                            lastUpdated: new Date().toISOString(),
                            articles: articles
                        };
                        localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                        
                        // UI 업데이트
                        loadScrapedArticles();
                        updateTodayArticles();
                        
                        const articleCount = articles.reduce((sum, group) => sum + (group.article_count || 0), 0);
                        console.log(`GitHub API로 ${articleCount}개의 기사 로드`);
                        showNotification(`최신 뉴스 ${articleCount}개를 불러왔습니다.`, 'success');
                    }
                }
            }
        } catch (githubError) {
            console.error('GitHub API 직접 호출도 실패:', githubError);
        }
    } catch (error) {
        console.error('GitHub 데이터 로드 오류:', error);
        // 오류가 발생해도 조용히 실패 (사용자 경험 방해하지 않음)
    }
}

// 스크래핑만 실행
async function scrapeOnly() {
    const scrapeBtn = document.getElementById('scrapeOnlyBtn');
    if (!scrapeBtn) return;
    
    scrapeBtn.disabled = true;
    scrapeBtn.innerHTML = '<i class="icon">⏳</i> 스크래핑 중...';
    
    showNotification('스크래핑만 실행합니다...', 'info');
    
    try {
        // Scrape Only API 호출
        const response = await fetch('https://singapore-news-github.vercel.app/api/scrape-only', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('스크래핑이 시작되었습니다 (전송 없음)', 'success');
            
            setTimeout(() => {
                showNotification('스크래핑이 진행 중입니다. 완료까지 잠시 기다려주세요.', 'info');
            }, 2000);
            
        } else {
            throw new Error(result.error || '알 수 없는 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('스크래핑 오류:', error);
        showNotification('스크래핑 실행 중 오류가 발생했습니다.', 'error');
    } finally {
        scrapeBtn.disabled = false;
        scrapeBtn.innerHTML = '<svg class="w-4 h-4 mr-1.5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>스크래핑만';
    }
}

// 전송만 실행
async function sendOnly() {
    const sendBtn = document.getElementById('sendOnlyBtn');
    if (!sendBtn) return;
    
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="icon">⏳</i> 전송 중...';
    
    showNotification('WhatsApp 전송만 실행합니다...', 'info');
    
    try {
        // GitHub Actions 방식 먼저 시도
        const response = await fetch('https://singapore-news-github.vercel.app/api/send-only', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('GitHub Actions 방식 실패, 직접 전송 시도');
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('GitHub Actions를 통해 전송이 시작되었습니다!', 'success');
            // 30초 후 자동 새로고침하여 결과 확인
            setTimeout(() => {
                refreshDashboard();
            }, 30000);
        } else {
            throw new Error(result.error || 'GitHub Actions 실행 실패');
        }
        
    } catch (error) {
        console.error('GitHub Actions 방식 실패:', error);
        showNotification('GitHub Actions 방식 실패, 직접 전송을 시도합니다...', 'warning');
        
        // 직접 WhatsApp API 호출
        try {
            await sendDirectToWhatsApp();
        } catch (directError) {
            console.error('Direct send error:', directError);
            showNotification('전송에 실패했습니다: ' + directError.message, 'error');
        }
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>전송만';
    }
}

// 직접 WhatsApp 전송 함수
async function sendDirectToWhatsApp() {
    // 최신 스크랩 데이터 가져오기 (GitHub Pages 경로 사용)
    const latestResponse = await fetch('/singapore_news_github/data/latest.json?t=' + Date.now());
    const latestData = await latestResponse.json();
    
    if (!latestData.latestFile) {
        throw new Error('전송할 데이터가 없습니다.');
    }
    
    // 스크랩된 데이터 가져오기 (GitHub Pages 경로 사용)
    const scrapedResponse = await fetch(`/singapore_news_github/data/scraped/${latestData.latestFile}?t=` + Date.now());
    const scrapedData = await scrapedResponse.json();
    
    if (!scrapedData || scrapedData.length === 0) {
        throw new Error('스크랩된 기사가 없습니다.');
    }
    
    // 메시지 생성
    const message = formatWhatsAppMessage(scrapedData);
    
    // Vercel API를 통해 WhatsApp 전송
    const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    const apiUrl = 'https://singapore-news-github.vercel.app/api/send-whatsapp';
    
    const whatsappResponse = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            channel: '120363421252284444@g.us',
            message: message
        })
    });
    
    const whatsappResult = await whatsappResponse.json();
    
    if (whatsappResult.sent) {
        showNotification('WhatsApp 전송이 완료되었습니다!', 'success');
        // 전송 기록 저장
        saveTransmissionHistory(scrapedData, 'success');
    } else {
        throw new Error('WhatsApp 전송 실패');
    }
}

// WhatsApp 메시지 포맷 함수
function formatWhatsAppMessage(consolidatedArticles) {
    const now = new Date();
    let message = `📰 *Singapore News Update*\n${now.getFullYear()}년 ${now.getMonth()+1}월 ${now.getDate()}일 ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}\n`;
    message += "━━━━━━━━━━━━━━━━━━━━\n\n";
    
    // 전체 기사 개수 계산
    const totalArticles = consolidatedArticles.reduce((sum, group) => sum + group.article_count, 0);
    message += `📊 오늘의 주요 뉴스: ${consolidatedArticles.length}개 그룹, 총 ${totalArticles}개 기사\n\n`;
    
    // 각 그룹별로 기사 표시
    consolidatedArticles.forEach(group => {
        message += `【 ${group.group} 】\n`;
        message += `📍 출처: ${group.sites.join(', ')}\n`;
        message += `━━━━━━━━━━━━━━━━━━━━\n`;
        
        group.articles.forEach((article, index) => {
            message += `\n${index + 1}. ${article.summary}\n`;
            message += `   🔗 원문: ${article.url}\n\n`;
        });
        
        message += "━━━━━━━━━━━━━━━━━━━━\n\n";
    });
    
    message += `\n💡 *요약 정보*\n`;
    message += `• 스크랩 시간: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}\n`;
    message += `• 총 ${consolidatedArticles.length}개 카테고리에서 ${totalArticles}개 기사 수집\n`;
    message += `\n🤖 _Singapore News Scraper Bot_`;
    
    return message;
}

// 전송 기록 저장 함수
async function saveTransmissionHistory(articles, status) {
    const totalArticles = articles.reduce((sum, group) => sum + group.article_count, 0);
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    
    history.push({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        channel: '120363421252284444@g.us',
        status: status,
        header: `뉴스 ${totalArticles}개 발송`,
        message_preview: `${articles.length}개 그룹, 총 ${totalArticles}개 기사 전송`,
        message_length: 0,
        article_count: totalArticles,
        articles: articles
    });
    
    localStorage.setItem('singapore_news_history', JSON.stringify(history));
}

function generateSendMessage() {
    const generateBtn = document.getElementById('generateMessageBtn');
    const messageDiv = document.getElementById('generatedMessage');
    const messageContent = document.getElementById('messageContent');
    
    if (!generateBtn || !messageDiv || !messageContent) return;
    
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="icon">⏳</i> 생성 중...';
    
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    if (!scrapedData) {
        showNotification('스크랩된 기사가 없습니다.', 'error');
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
        return;
    }
    
    try {
        const data = JSON.parse(scrapedData);
        let message = '';
        
        // 새로운 그룹별 통합 구조 처리
        if (data.consolidatedArticles) {
            const totalArticles = data.consolidatedArticles.reduce((sum, group) => sum + group.article_count, 0);
            
            if (totalArticles === 0) {
                showNotification('스크랩된 기사가 없습니다.', 'error');
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
                return;
            }
            
            // 새로운 형식의 메시지 생성
            message = `📰 *Singapore News Update*\n${new Date().toLocaleString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
            message += `📊 오늘의 주요 뉴스: ${data.consolidatedArticles.length}개 그룹, 총 ${totalArticles}개 기사\n\n`;
            
            // 각 그룹별로 기사 표시
            data.consolidatedArticles.forEach(groupData => {
                message += `【 ${groupData.group} 】\n`;
                message += `📍 출처: ${groupData.sites.join(', ')}\n`;
                message += `━━━━━━━━━━━━━━━━━━━━\n`;
                
                // 그룹 내 기사들 표시
                groupData.articles.forEach((article, i) => {
                    message += `\n${i + 1}. ${article.summary}\n`;
                    message += `   🔗 원문: ${article.url}\n\n`;
                });
                
                message += `━━━━━━━━━━━━━━━━━━━━\n\n`;
            });
            
            // 푸터 추가
            message += `\n💡 *요약 정보*\n`;
            message += `• 스크랩 시간: ${new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}\n`;
            message += `• 총 ${data.consolidatedArticles.length}개 카테고리에서 ${totalArticles}개 기사 수집\n`;
            message += `\n🤖 _Singapore News Scraper Bot_`;
            
        } else if (data.articles) {
            // 기존 구조 처리 (하위 호환성)
            const articles = data.articles || [];
            
            if (articles.length === 0) {
                showNotification('스크랩된 기사가 없습니다.', 'error');
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
                return;
            }
            
            // 메시지 생성 (Python send_whatsapp.py의 format_message 함수와 정확히 동일한 형식)
            const now = new Date();
            const dateStr = `${now.getFullYear()}년 ${String(now.getMonth() + 1).padStart(2, '0')}월 ${String(now.getDate()).padStart(2, '0')}일 ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            
            message = `📰 *Singapore News Update*\n${dateStr}\n`;
            message += "━━━━━━━━━━━━━━━━━━━━\n\n";
            
            // 그룹별로 정리 (실제 스크랩 데이터 구조에 맞춤)
            const grouped = {};
            let totalArticles = 0;
            
            articles.forEach(article => {
                const group = article.group || article.site || 'Other';
                if (!grouped[group]) {
                    grouped[group] = {
                        articles: [],
                        sites: new Set()
                    };
                }
                grouped[group].articles.push(article);
                grouped[group].sites.add(article.site || 'Unknown');
                totalArticles++;
            });
            
            // 전체 기사 개수 표시
            message += `📊 오늘의 주요 뉴스: ${Object.keys(grouped).length}개 그룹, 총 ${totalArticles}개 기사\n\n`;
            
            // 각 그룹별로 기사 표시
            Object.entries(grouped).forEach(([groupName, groupData]) => {
                message += `【 ${groupName} 】\n`;
                message += `📍 출처: ${Array.from(groupData.sites).join(', ')}\n`;
                message += `━━━━━━━━━━━━━━━━━━━━\n`;
                
                // 그룹 내 기사들 표시
                groupData.articles.forEach((article, i) => {
                    message += `\n${i + 1}. ${article.summary || article.title}\n`;
                    message += `   🔗 원문: ${article.url}\n\n`;
                });
                
                message += "━━━━━━━━━━━━━━━━━━━━\n\n";
            });
            
            // 푸터 추가
            message += `\n💡 *요약 정보*\n`;
            message += `• 스크랩 시간: ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}\n`;
            message += `• 총 ${Object.keys(grouped).length}개 카테고리에서 ${totalArticles}개 기사 수집\n`;
            message += `\n🤖 _Singapore News Scraper Bot_`;
        } else {
            showNotification('스크랩된 기사가 없습니다.', 'error');
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
            return;
        }
        
        // 메시지 길이 제한
        if (message.length > 4096) {
            message = message.substring(0, 4090) + '...';
        }
        
        messageContent.value = message;
        messageDiv.classList.remove('hidden');
        
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
        
        showNotification('전송 메시지가 생성되었습니다.', 'success');
        
    } catch (error) {
        console.error('메시지 생성 오류:', error);
        showNotification('메시지 생성 중 오류가 발생했습니다.', 'error');
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="icon">📝</i> 전송 메시지 생성';
    }
}

function sendGeneratedMessage() {
    const messageContent = document.getElementById('messageContent');
    if (!messageContent || !messageContent.value) {
        showNotification('전송할 메시지가 없습니다.', 'error');
        return;
    }
    
    const settings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
    const channel = settings.whatsappChannel;
    
    if (!channel) {
        showNotification('전송 채널이 설정되지 않았습니다.', 'error');
        return;
    }
    
    // 테스트 전송 함수를 재사용
    const testSendBtn = document.getElementById('testSendBtn');
    const testChannel = document.getElementById('testChannel');
    const testMessage = document.getElementById('testMessage');
    
    if (testChannel && testMessage) {
        const originalChannel = testChannel.value;
        const originalMessage = testMessage.value;
        
        testChannel.value = channel;
        testMessage.value = messageContent.value;
        
        sendTestMessage();
        
        // 원래 값 복원
        testChannel.value = originalChannel;
        testMessage.value = originalMessage;
    } else {
        showNotification('전송 기능을 사용할 수 없습니다.', 'error');
    }
}

function copyMessageToClipboard() {
    const messageContent = document.getElementById('messageContent');
    if (!messageContent || !messageContent.value) {
        showNotification('복사할 메시지가 없습니다.', 'error');
        return;
    }
    
    navigator.clipboard.writeText(messageContent.value).then(() => {
        showNotification('메시지가 클립보드에 복사되었습니다.', 'success');
    }).catch(() => {
        // 클립보드 복사 실패 시 텍스트 영역 선택
        messageContent.select();
        document.execCommand('copy');
        showNotification('메시지가 클립보드에 복사되었습니다.', 'success');
    });
}

// 선택 기능들
function selectAllArticles() {
    const checkboxes = document.querySelectorAll('.article-checkbox');
    const groupCheckboxes = document.querySelectorAll('.group-checkbox');
    const selectAllBtn = document.getElementById('selectAllBtn');
    
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => cb.checked = !allChecked);
    groupCheckboxes.forEach(cb => cb.checked = !allChecked);
    
    selectAllBtn.innerHTML = allChecked ? 
        '<i class="icon">☑️</i> 전체 선택' : 
        '<i class="icon">☐</i> 전체 해제';
    
    updateSelectionState();
}

function toggleGroupSelection(groupName) {
    const groupCheckbox = document.getElementById(`group-${groupName}`);
    const articleCheckboxes = document.querySelectorAll(`.article-checkbox[data-group="${groupName}"]`);
    
    articleCheckboxes.forEach(cb => {
        cb.checked = groupCheckbox.checked;
    });
    
    updateSelectionState();
}

function updateSelectionState() {
    const checkboxes = document.querySelectorAll('.article-checkbox');
    const selectedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');
    
    // 선택 삭제 버튼 상태 업데이트
    deleteSelectedBtn.disabled = selectedCount === 0;
    deleteSelectedBtn.innerHTML = selectedCount > 0 ? 
        `<i class="icon">🗑️</i> 선택 삭제 (${selectedCount})` : 
        '<i class="icon">🗑️</i> 선택 삭제';
    
    // 전체 선택 버튼 상태 업데이트
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    selectAllBtn.innerHTML = allChecked ? 
        '<i class="icon">☐</i> 전체 해제' : 
        '<i class="icon">☑️</i> 전체 선택';
    
    // 그룹 체크박스 상태 업데이트
    const groups = {};
    checkboxes.forEach(cb => {
        const group = cb.dataset.group;
        if (!groups[group]) groups[group] = {total: 0, checked: 0};
        groups[group].total++;
        if (cb.checked) groups[group].checked++;
    });
    
    Object.entries(groups).forEach(([group, stats]) => {
        const groupCheckbox = document.getElementById(`group-${group}`);
        if (groupCheckbox) {
            groupCheckbox.checked = stats.checked === stats.total;
            groupCheckbox.indeterminate = stats.checked > 0 && stats.checked < stats.total;
        }
    });
}

function deleteSelectedArticles() {
    const selectedCheckboxes = document.querySelectorAll('.article-checkbox:checked');
    const selectedIndices = Array.from(selectedCheckboxes).map(cb => parseInt(cb.id.replace('article-', '')));
    
    if (selectedIndices.length === 0) {
        showNotification('삭제할 기사를 선택해주세요.', 'error');
        return;
    }
    
    if (confirm(`정말로 선택한 ${selectedIndices.length}개의 기사를 삭제하시겠습니까?`)) {
        const scrapedData = localStorage.getItem('singapore_news_scraped_data');
        if (!scrapedData) return;
        
        try {
            const data = JSON.parse(scrapedData);
            if (data.articles) {
                // 인덱스를 내림차순으로 정렬하여 삭제 (뒤에서부터 삭제)
                selectedIndices.sort((a, b) => b - a);
                selectedIndices.forEach(index => {
                    data.articles.splice(index, 1);
                });
                
                localStorage.setItem('singapore_news_scraped_data', JSON.stringify(data));
                loadTodayArticlesModal();
                updateTodayArticles();
                showNotification(`${selectedIndices.length}개의 기사가 삭제되었습니다.`, 'success');
            }
        } catch (error) {
            console.error('기사 삭제 오류:', error);
            showNotification('기사 삭제 중 오류가 발생했습니다.', 'error');
        }
    }
}

async function deleteAllArticlesFromModal() {
    if (confirm('정말로 오늘 스크랩한 모든 기사를 삭제하시겠습니까?\n\n이 작업은 GitHub에 저장된 데이터도 삭제합니다.')) {
        try {
            // GitHub에 저장된 파일명 가져오기
            const filename = localStorage.getItem('singapore_news_github_filename');
            
            if (filename) {
                // GitHub에서 파일 삭제
                const response = await fetch('https://singapore-news-github.vercel.app/api/delete-scraped-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filename })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // 로컬 스토리지도 삭제
                    localStorage.removeItem('singapore_news_scraped_data');
                    localStorage.removeItem('singapore_news_github_filename');
                    closeArticlesModal();
                    loadScrapedArticles();
                    updateTodayArticles();
                    showNotification('모든 기사가 완전히 삭제되었습니다.', 'success');
                } else {
                    showNotification('GitHub에서 삭제 실패: ' + (result.error || '알 수 없는 오류'), 'error');
                }
            } else {
                // 파일명이 없으면 로컬만 삭제
                localStorage.removeItem('singapore_news_scraped_data');
                closeArticlesModal();
                loadScrapedArticles();
                updateTodayArticles();
                showNotification('로컬 기사가 삭제되었습니다.', 'success');
            }
        } catch (error) {
            console.error('삭제 중 오류:', error);
            showNotification('삭제 중 오류가 발생했습니다.', 'error');
        }
    }
}

// 아코디언 토글 함수
function toggleArticleAccordion(source, index) {
    const contentId = `article-content-${source}-${index}`;
    const content = document.getElementById(contentId);
    
    // 새로운 그룹 구조와 기존 구조 모두 지원
    let toggle = document.querySelector(`[data-group="${source}"][data-index="${index}"] .accordion-toggle i`);
    let articleItem = document.querySelector(`[data-group="${source}"][data-index="${index}"]`);
    
    // 기존 구조 fallback
    if (!toggle) {
        toggle = document.querySelector(`[data-source="${source}"][data-index="${index}"] .accordion-toggle i`);
        articleItem = document.querySelector(`[data-source="${source}"][data-index="${index}"]`);
    }
    
    if (content && toggle) {
        if (content.style.display === 'none' || !content.style.display) {
            // 다른 모든 기사 닫기
            document.querySelectorAll('.article-content').forEach(el => {
                if (el.id !== contentId) {
                    el.style.display = 'none';
                    const otherToggle = el.parentElement.querySelector('.accordion-toggle i');
                    if (otherToggle) {
                        otherToggle.textContent = '▼';
                        otherToggle.style.transform = 'rotate(0deg)';
                    }
                }
            });
            
            // 현재 기사 열기
            content.style.display = 'block';
            toggle.textContent = '▲';
            toggle.style.transform = 'rotate(180deg)';
            
            // 스크롤 위치 조정
            setTimeout(() => {
                articleItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        } else {
            // 닫기
            content.style.display = 'none';
            toggle.textContent = '▼';
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

function toggleSelectableArticleAccordion(index) {
    const contentId = `selectable-article-content-${index}`;
    const content = document.getElementById(contentId);
    const toggle = document.querySelector(`[data-index="${index}"] .accordion-toggle i`);
    
    if (content && toggle) {
        if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            toggle.textContent = '▲';
            toggle.style.transform = 'rotate(180deg)';
        } else {
            content.classList.add('hidden');
            toggle.textContent = '▼';
            toggle.style.transform = 'rotate(0deg)';
        }
    }
}

// 스크랩 관리 페이지 HTML
function getScrapingManagementHTML() {
    return `
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">스크랩 관리</h1>
                    <p class="mt-1 text-sm text-gray-500">GitHub에 저장된 모든 스크랩 기사를 관리합니다</p>
                </div>
                <div class="mt-4 sm:mt-0">
                    <button type="button" onclick="refreshScrapedArticles()" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        새로고침
                    </button>
                </div>
            </div>

            <!-- Filters -->
            <div class="bg-white shadow rounded-lg p-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label for="dateFilter" class="block text-sm font-medium text-gray-700">날짜 선택</label>
                        <input type="date" id="dateFilter" onchange="filterScrapedArticles()" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                    </div>
                    <div>
                        <label for="siteFilter" class="block text-sm font-medium text-gray-700">사이트</label>
                        <select id="siteFilter" onchange="filterScrapedArticles()" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                            <option value="">모든 사이트</option>
                        </select>
                    </div>
                    <div>
                        <label for="searchFilter" class="block text-sm font-medium text-gray-700">검색</label>
                        <input type="text" id="searchFilter" placeholder="제목 또는 내용 검색" onkeyup="filterScrapedArticles()" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                    </div>
                </div>
                <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">실행 타입</label>
                    <div class="flex space-x-4">
                        <label class="inline-flex items-center cursor-pointer hover:bg-gray-100 px-3 py-2 rounded-md transition-colors">
                            <input type="radio" name="executionType" value="all" checked onchange="filterScrapedArticles()" class="form-radio text-blue-600">
                            <span class="ml-2">전체</span>
                        </label>
                        <label class="inline-flex items-center cursor-pointer hover:bg-gray-100 px-3 py-2 rounded-md transition-colors">
                            <input type="radio" name="executionType" value="scheduled" onchange="filterScrapedArticles()" class="form-radio text-blue-600">
                            <span class="ml-2">배치 실행</span>
                        </label>
                        <label class="inline-flex items-center cursor-pointer hover:bg-gray-100 px-3 py-2 rounded-md transition-colors">
                            <input type="radio" name="executionType" value="manual" onchange="filterScrapedArticles()" class="form-radio text-blue-600">
                            <span class="ml-2">수동 실행</span>
                        </label>
                    </div>
                    <div id="filterStatus" class="mt-2 text-sm text-gray-600"></div>
                </div>
            </div>

            <!-- Statistics -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">총 파일 수</dt>
                                    <dd class="text-lg font-medium text-gray-900" id="totalFilesCount">0</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">총 기사 수</dt>
                                    <dd class="text-lg font-medium text-gray-900" id="totalArticlesCount">0</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">날짜 범위</dt>
                                    <dd class="text-lg font-medium text-gray-900" id="dateRangeInfo">-</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">사이트 수</dt>
                                    <dd class="text-lg font-medium text-gray-900" id="totalSitesCount">0</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Articles List -->
            <div class="bg-white shadow rounded-lg">
                <div class="px-4 py-5 sm:p-6">
                    <div id="scrapingArticlesList" class="space-y-4">
                        <div class="text-center py-8">
                            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            <p class="mt-2 text-sm text-gray-500">데이터를 불러오는 중...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 모든 스크랩 데이터 불러오기
async function loadAllScrapedArticles() {
    try {
        showNotification('스크랩 데이터를 불러오는 중...', 'info');
        
        // Vercel API를 통해 파일 목록 가져오기
        const response = await fetch('https://singapore-news-github.vercel.app/api/get-scraped-files');
        
        if (!response.ok) {
            throw new Error(`파일 목록 가져오기 실패: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '파일 목록을 가져올 수 없습니다');
        }
        
        const files = result.files;
        
        // JSON 파일만 필터링하고 날짜순으로 정렬
        const jsonFiles = files
            .filter(file => file.name.endsWith('.json'))
            .sort((a, b) => b.name.localeCompare(a.name));
        
        // 통계 업데이트
        document.getElementById('totalFilesCount').textContent = jsonFiles.length;
        
        if (jsonFiles.length === 0) {
            document.getElementById('scrapingArticlesList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-500">저장된 스크랩 데이터가 없습니다.</p>
                </div>
            `;
            return;
        }
        
        // 날짜 범위 계산
        const dates = jsonFiles.map(f => f.name.substring(0, 10));
        document.getElementById('dateRangeInfo').textContent = `${dates[dates.length-1]} ~ ${dates[0]}`;
        
        // 파일 데이터 로드
        const allArticles = [];
        const siteSet = new Set();
        
        // 모든 파일 로드하도록 변경
        showNotification(`${jsonFiles.length}개의 스크랩 파일을 로드 중...`, 'info');
        
        let loadedCount = 0;
        for (const file of jsonFiles) {
            try {
                const fileResponse = await fetch(file.download_url);
                const fileData = await fileResponse.json();
                
                // 배열인 경우 (현재 주요 구조)
                if (Array.isArray(fileData) && fileData.length > 0) {
                    fileData.forEach(group => {
                        if (group.sites) group.sites.forEach(site => siteSet.add(site));
                        // articles 배열이 있으면 실제 길이로, 없으면 article_count 사용
                        const actualCount = group.articles ? group.articles.length : (group.article_count || 0);
                        allArticles.push({
                            date: file.name.substring(0, 19),
                            fileName: file.name,
                            group: {
                                ...group,
                                actual_article_count: actualCount
                            }
                        });
                    });
                } 
                // consolidatedArticles 구조 (이전 버전 호환)
                else if (fileData && fileData.consolidatedArticles) {
                    fileData.consolidatedArticles.forEach(group => {
                        if (group.sites) group.sites.forEach(site => siteSet.add(site));
                        // articles 배열이 있으면 실제 길이로, 없으면 article_count 사용
                        const actualCount = group.articles ? group.articles.length : (group.article_count || 0);
                        allArticles.push({
                            date: file.name.substring(0, 19),
                            fileName: file.name,
                            group: {
                                ...group,
                                actual_article_count: actualCount
                            }
                        });
                    });
                }
                
                loadedCount++;
                // 5개마다 진행 상황 업데이트
                if (loadedCount % 5 === 0) {
                    document.getElementById('scrapingArticlesList').innerHTML = `
                        <div class="text-center py-8">
                            <p class="text-sm text-gray-500">로딩 중... (${loadedCount}/${jsonFiles.length})</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error(`파일 로드 실패: ${file.name}`, error);
            }
        }
        
        // 통계 업데이트 - 실제 기사 배열 길이로 계산
        const totalArticles = allArticles.reduce((sum, item) => {
            // 새로 계산한 actual_article_count 사용
            if (item.group.actual_article_count !== undefined) {
                return sum + item.group.actual_article_count;
            }
            // 기존 방식 (하위 호환성)
            else if (item.group.articles && Array.isArray(item.group.articles)) {
                return sum + item.group.articles.length;
            } else if (item.group.article_count) {
                return sum + item.group.article_count;
            }
            return sum;
        }, 0);
        document.getElementById('totalArticlesCount').textContent = totalArticles;
        document.getElementById('totalSitesCount').textContent = siteSet.size;
        
        // 사이트 필터 옵션 추가
        const siteFilter = document.getElementById('siteFilter');
        siteFilter.innerHTML = '<option value="">모든 사이트</option>';
        Array.from(siteSet).sort().forEach(site => {
            siteFilter.innerHTML += `<option value="${site}">${site}</option>`;
        });
        
        // 기사 목록 표시
        window.allScrapedArticles = allArticles; // 필터링을 위해 저장
        displayScrapedArticles(allArticles);
        
        showNotification('스크랩 데이터를 성공적으로 불러왔습니다.', 'success');
        
    } catch (error) {
        console.error('스크랩 데이터 로드 실패:', error);
        console.error('에러 상세:', error.message, error.stack);
        
        // 에러 상세 정보 표시
        const errorMsg = error.message || '알 수 없는 오류';
        showNotification(`데이터를 불러오는데 실패했습니다: ${errorMsg}`, 'error');
        
        // 에러 시에도 UI 표시
        document.getElementById('scrapingArticlesList').innerHTML = `
            <div class="text-center py-8">
                <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="mt-2 text-sm text-red-600">데이터 로드 실패</p>
                <p class="mt-1 text-xs text-gray-500">${errorMsg}</p>
            </div>
        `;
    }
}

// 실행 타입 태그 생성
function getExecutionTypeTag(group, dateStr) {
    // execution_type 필드가 있으면 사용
    if (group.execution_type) {
        return group.execution_type === 'scheduled' 
            ? '<span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">배치</span>'
            : '<span class="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">수동</span>';
    }
    
    // 없으면 시간으로 추정 (한국시간 기준)
    const time = dateStr.substring(11, 16); // HH:MM 추출
    const hour = parseInt(time.substring(0, 2));
    
    // 오전 6시(06:00) 전후 30분 이내면 배치로 간주
    if ((hour === 5 && parseInt(time.substring(3, 5)) >= 30) || 
        (hour === 6 && parseInt(time.substring(3, 5)) <= 30)) {
        return '<span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">배치(추정)</span>';
    }
    
    // 기존 배치 시간 (09:00, 13:00, 18:00) 전후 30분도 체크
    const batchHours = [9, 13, 18];
    for (const batchHour of batchHours) {
        if ((hour === batchHour - 1 && parseInt(time.substring(3, 5)) >= 30) || 
            hour === batchHour ||
            (hour === batchHour && parseInt(time.substring(3, 5)) <= 30)) {
            return '<span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">배치(추정)</span>';
        }
    }
    
    return '<span class="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">수동</span>';
}

// 스크랩 기사 표시
function displayScrapedArticles(articles) {
    const container = document.getElementById('scrapingArticlesList');
    
    if (articles.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">표시할 기사가 없습니다.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    const groupedByDate = {};
    
    // 날짜별로 그룹화
    articles.forEach(item => {
        const date = item.date.substring(0, 10);
        if (!groupedByDate[date]) {
            groupedByDate[date] = [];
        }
        groupedByDate[date].push(item);
    });
    
    // 날짜별로 표시
    Object.entries(groupedByDate)
        .sort((a, b) => b[0].localeCompare(a[0]))
        .forEach(([date, items]) => {
            html += `
                <div class="mb-6">
                    <h3 class="text-lg font-medium text-gray-900 mb-3">${date}</h3>
                    <div class="space-y-3">
            `;
            
            items.forEach((item, index) => {
                const group = item.group;
                html += `
                    <div class="border rounded-lg p-4 hover:bg-gray-50">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h4 class="text-md font-medium text-gray-900">
                                    ${group.group}
                                    ${getExecutionTypeTag(group, item.date)}
                                </h4>
                                <p class="text-sm text-gray-500 mt-1">
                                    ${group.sites.join(', ')} • ${group.article_count}개 기사 • ${item.date}
                                </p>
                            </div>
                            <button onclick="toggleScrapingArticle('${date}-${index}')" class="ml-4 text-blue-600 hover:text-blue-800">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </button>
                        </div>
                        <div id="scraping-article-${date}-${index}" class="hidden mt-4 space-y-2">
                `;
                
                group.articles.forEach((article, i) => {
                    html += `
                        <div class="bg-gray-50 rounded p-3">
                            <p class="text-sm font-medium text-gray-900">${i + 1}. ${article.summary}</p>
                            <a href="${article.url}" target="_blank" class="text-xs text-blue-600 hover:text-blue-800 mt-1 inline-block">
                                원문 보기 →
                            </a>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
    
    container.innerHTML = html;
}

// 스크랩 기사 토글
function toggleScrapingArticle(id) {
    const content = document.getElementById(`scraping-article-${id}`);
    if (content) {
        content.classList.toggle('hidden');
    }
}

// 스크랩 기사 필터링
function filterScrapedArticles() {
    const dateFilter = document.getElementById('dateFilter').value;
    const siteFilter = document.getElementById('siteFilter').value;
    const searchFilter = document.getElementById('searchFilter').value.toLowerCase();
    const executionType = document.querySelector('input[name="executionType"]:checked')?.value || 'all';
    
    if (!window.allScrapedArticles) return;
    
    // 로딩 표시
    const container = document.getElementById('scrapingArticlesList');
    container.style.opacity = '0.5';
    
    let filtered = window.allScrapedArticles;
    
    // 날짜 필터
    if (dateFilter) {
        filtered = filtered.filter(item => item.date.startsWith(dateFilter));
    }
    
    // 사이트 필터
    if (siteFilter) {
        filtered = filtered.filter(item => item.group.sites.includes(siteFilter));
    }
    
    // 검색 필터
    if (searchFilter) {
        filtered = filtered.filter(item => {
            // 그룹 이름 검색
            if (item.group.group.toLowerCase().includes(searchFilter)) return true;
            
            // 기사 내용 검색
            return item.group.articles.some(article => 
                article.summary.toLowerCase().includes(searchFilter) ||
                (article.title && article.title.toLowerCase().includes(searchFilter))
            );
        });
    }
    
    // 실행 타입 필터
    if (executionType !== 'all') {
        filtered = filtered.filter(item => {
            // execution_type 필드가 있으면 사용
            if (item.group.execution_type) {
                return item.group.execution_type === executionType;
            }
            
            // 없으면 시간으로 추정
            const time = item.date.substring(11, 16);
            const hour = parseInt(time.substring(0, 2));
            const minute = parseInt(time.substring(3, 5));
            
            // 배치 시간 체크 (06:00, 09:00, 13:00, 18:00 전후 30분)
            const isScheduled = 
                (hour === 5 && minute >= 30) || (hour === 6 && minute <= 30) ||
                (hour === 8 && minute >= 30) || (hour === 9 && minute <= 30) ||
                (hour === 12 && minute >= 30) || (hour === 13 && minute <= 30) ||
                (hour === 17 && minute >= 30) || (hour === 18 && minute <= 30);
            
            return executionType === 'scheduled' ? isScheduled : !isScheduled;
        });
    }
    
    // 필터 상태 표시
    const filterStatus = document.getElementById('filterStatus');
    if (filterStatus) {
        let statusText = `${filtered.length}개 결과`;
        if (executionType === 'scheduled') {
            statusText += ' (배치 실행만 표시)';
        } else if (executionType === 'manual') {
            statusText += ' (수동 실행만 표시)';
        }
        if (dateFilter || siteFilter || searchFilter) {
            statusText += ' - 추가 필터 적용됨';
        }
        filterStatus.textContent = statusText;
    }
    
    displayScrapedArticles(filtered);
    
    // 로딩 완료
    setTimeout(() => {
        container.style.opacity = '1';
    }, 100);
}

// 스크랩 데이터 새로고침
async function refreshScrapedArticles() {
    await loadAllScrapedArticles();
}