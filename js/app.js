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
    }
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (login(username, password)) {
            if (window.isMFAEnabled && isMFAEnabled(username)) {
                showMFAForm(username);
            } else {
                checkAuth();
            }
        } else {
            errorMessage.textContent = '잘못된 아이디 또는 비밀번호입니다.';
        }
    });
    
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
    
    document.querySelectorAll('.nav-links a[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            loadPage(page);
        });
    });
    
    async function loadPage(page) {
        const content = document.getElementById('content');
        
        switch(page) {
            case 'dashboard':
                content.innerHTML = getDashboardHTML();
                loadDashboardData();
                break;
            case 'settings':
                if (isAdmin()) {
                    content.innerHTML = getSettingsHTML();
                    await initializeSettings();
                }
                break;
            case 'history':
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
        }
    }
    
    function getDashboardHTML() {
        return `
            <div class="page-section">
                <h2>Dashboard</h2>
                <div class="dashboard-stats">
                    <div class="stat-card">
                        <h3>오늘 스크랩한 기사</h3>
                        <p class="stat-number" id="todayArticles">0</p>
                    </div>
                    <div class="stat-card">
                        <h3>전송 예정 기사</h3>
                        <p class="stat-number" id="pendingArticles">0</p>
                    </div>
                    <div class="stat-card">
                        <h3>다음 전송 시간</h3>
                        <p class="stat-text" id="nextSendTime">-</p>
                    </div>
                </div>
                <div class="dashboard-actions">
                    <button class="btn btn-primary" onclick="refreshDashboard()">
                        <i class="icon">🔄</i> 새로고침
                    </button>
                    <button class="btn btn-secondary" onclick="loadPage('history')">
                        <i class="icon">📊</i> 전송 이력 보기
                    </button>
                </div>
                <div class="recent-activity">
                    <h3>최근 활동</h3>
                    <div id="recentActivityList" class="activity-list">
                        <p class="loading">활동 내역을 불러오는 중...</p>
                    </div>
                </div>
                <div class="scraped-articles">
                    <h3>오늘 스크랩한 기사</h3>
                    <button class="btn btn-sm" onclick="toggleScrapedArticles()" style="float: right; margin-top: -35px;">
                        <span id="toggleArticlesText">펼치기</span>
                    </button>
                    <div id="scrapedArticlesList" class="articles-list" style="display: none;">
                        <p class="loading">기사를 불러오는 중...</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    function getSettingsHTML() {
        return `
            <div class="page-section">
                <h2>Settings</h2>
                
                <div class="settings-section">
                    <h3>스크랩 대상 사이트 관리</h3>
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
                
                <div class="settings-section">
                    <h3>스크랩 대상 설정</h3>
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
                </div>
                
                <div class="settings-section">
                    <h3>요약 기준</h3>
                    <div class="checkbox-group">
                        <label>
                            <input type="checkbox" id="summaryHeadline" checked>
                            헤드라인
                        </label>
                        <label>
                            <input type="checkbox" id="summaryKeywords" checked>
                            키워드
                        </label>
                        <label>
                            <input type="checkbox" id="summaryContent" checked>
                            본문내용
                        </label>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>전송 대상</h3>
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
                
                <div class="settings-section">
                    <h3>전송 스케줄</h3>
                    <div class="form-group">
                        <label>전송 주기</label>
                        <select id="sendPeriod">
                            <option value="daily">일</option>
                            <option value="weekly">주</option>
                            <option value="monthly">월</option>
                        </select>
                    </div>
                    <div class="form-group" id="weeklyOptions" style="display: none;">
                        <label>요일 선택</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" name="weekday" value="1"> 월</label>
                            <label><input type="checkbox" name="weekday" value="2"> 화</label>
                            <label><input type="checkbox" name="weekday" value="3"> 수</label>
                            <label><input type="checkbox" name="weekday" value="4"> 목</label>
                            <label><input type="checkbox" name="weekday" value="5"> 금</label>
                            <label><input type="checkbox" name="weekday" value="6"> 토</label>
                            <label><input type="checkbox" name="weekday" value="0"> 일</label>
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
                
                <div class="settings-section">
                    <h3>기타 설정</h3>
                    <div class="form-group">
                        <label>유해 키워드 차단 (쉼표로 구분)</label>
                        <textarea id="blockedKeywords" rows="3" placeholder="violence, adult, gambling"></textarea>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>테스트 전송</h3>
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
                
                <button class="btn" onclick="saveSettings()">설정 저장</button>
            </div>
        `;
    }
    
    function getHistoryHTML() {
        const today = new Date();
        const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
        
        return `
            <div class="page-section">
                <h2>전송 이력</h2>
                <div class="history-filters">
                    <div class="filter-row">
                        <div class="form-group">
                            <label>시작일</label>
                            <input type="date" id="historyStartDate" value="${lastMonth.toISOString().split('T')[0]}">
                        </div>
                        <div class="form-group">
                            <label>종료일</label>
                            <input type="date" id="historyEndDate" value="${today.toISOString().split('T')[0]}">
                        </div>
                        <div class="form-group">
                            <label>상태</label>
                            <select id="historyStatus">
                                <option value="">전체</option>
                                <option value="success">성공</option>
                                <option value="failed">실패</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>채널</label>
                            <select id="historyChannel">
                                <option value="">전체</option>
                                <option value="120363421252284444@g.us">Singapore News Backup</option>
                            </select>
                        </div>
                    </div>
                    <div class="filter-actions">
                        <button class="btn" onclick="loadHistory()">조회</button>
                        <button class="btn" onclick="resetHistoryFilters()">초기화</button>
                        <span class="result-count" id="historyResultCount"></span>
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
        document.getElementById('mfaContainer').style.display = 'flex';
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
                document.getElementById('mfaContainer').style.display = 'none';
                checkAuth();
            } else {
                document.getElementById('mfaErrorMessage').textContent = '잘못된 인증 코드입니다.';
                document.getElementById('mfaCode').value = '';
                document.getElementById('mfaCode').focus();
            }
        });
        
        document.getElementById('mfaBackBtn').addEventListener('click', function() {
            logout();
            document.getElementById('mfaContainer').style.display = 'none';
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
    
    if (isProduction) {
        // 프로덕션 환경: 서버리스 함수 API 호출
        fetch('/api/send-whatsapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                channel: testChannel,
                message: processedMessage
            })
        })
        .then(response => {
            console.log('API Response Status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('API Response:', data);
            
            if (data.success) {
                testResult.innerHTML = '<div class="success-message">✅ 테스트 메시지가 성공적으로 전송되었습니다!</div>';
                recordTestHistory(testChannel, 'success', processedMessage);
            } else {
                const errorMsg = data.error || '알 수 없는 오류';
                testResult.innerHTML = `<div class="error-message">❌ 테스트 메시지 전송에 실패했습니다: ${errorMsg}</div>`;
                recordTestHistory(testChannel, 'failed', processedMessage);
            }
        })
        .catch(error => {
            console.error('API Error:', error);
            testResult.innerHTML = '<div class="error-message">❌ API 호출 중 오류가 발생했습니다.</div>';
            recordTestHistory(testChannel, 'failed', processedMessage);
        })
        .finally(() => {
            // 버튼 복원
            testSendBtn.disabled = false;
            testSendBtn.textContent = '테스트 전송';
            
            // 테스트 이력 새로고침
            loadTestHistory();
        });
    } else {
        // 로컬 개발 환경: 시뮬레이션 모드
        setTimeout(() => {
            const success = Math.random() > 0.2; // 80% 성공률
            
            if (success) {
                testResult.innerHTML = '<div class="success-message">✅ 테스트 메시지가 성공적으로 전송되었습니다! (시뮬레이션)</div>';
                recordTestHistory(testChannel, 'success', processedMessage);
            } else {
                testResult.innerHTML = '<div class="error-message">❌ 테스트 메시지 전송에 실패했습니다. (시뮬레이션)</div>';
                recordTestHistory(testChannel, 'failed', processedMessage);
            }
            
            // 버튼 복원
            testSendBtn.disabled = false;
            testSendBtn.textContent = '테스트 전송';
            
            // 테스트 이력 새로고침
            loadTestHistory();
        }, 1500);
    }
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
    
    // 최대 20개의 테스트 이력만 보관
    if (testHistory.length > 20) {
        testHistory.splice(20);
    }
    
    localStorage.setItem('singapore_news_test_history', JSON.stringify(testHistory));
}

function loadTestHistory() {
    const testHistory = JSON.parse(localStorage.getItem('singapore_news_test_history') || '[]');
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
}

function saveSettings() {
    try {
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
            blockedKeywords: document.getElementById('blockedKeywords').value
        };
        
        // 설정 유효성 검사
        if (settings.sendChannel === 'whatsapp' && !settings.whatsappChannel) {
            showNotification('WhatsApp 채널을 선택해주세요.', 'error');
            return;
        }
        
        localStorage.setItem('singapore_news_settings', JSON.stringify(settings));
        showNotification('설정이 저장되었습니다.', 'success');
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
        
        localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
        await loadSites();
        e.target.reset();
    }
});

async function deleteSite(index) {
    const sites = JSON.parse(localStorage.getItem('singapore_news_sites') || '[]');
    sites.splice(index, 1);
    localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
    await loadSites();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const tbody = document.querySelector('#historyTable tbody');
    tbody.innerHTML = '';
    
    // 필터 값 가져오기
    const startDate = document.getElementById('historyStartDate')?.value;
    const endDate = document.getElementById('historyEndDate')?.value;
    const statusFilter = document.getElementById('historyStatus')?.value;
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
        const statusClass = record.status === 'success' ? 'status-success' : 'status-failed';
        row.innerHTML = `
            <td>${new Date(record.timestamp).toLocaleString()}</td>
            <td>${record.header || '-'}</td>
            <td>${getChannelName(record.channel)}</td>
            <td><span class="${statusClass}">${record.status === 'success' ? '성공' : '실패'}</span></td>
            <td><button class="btn btn-sm" onclick="showHistoryDetail('${record.id}')">상세</button></td>
        `;
    });
    
    if (filteredHistory.length === 0) {
        const row = tbody.insertRow();
        row.innerHTML = '<td colspan="5" style="text-align: center;">조회 결과가 없습니다.</td>';
    }
}

function resetHistoryFilters() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    
    document.getElementById('historyStartDate').value = lastMonth.toISOString().split('T')[0];
    document.getElementById('historyEndDate').value = today.toISOString().split('T')[0];
    document.getElementById('historyStatus').value = '';
    document.getElementById('historyChannel').value = '';
    
    loadHistory();
}

function showHistoryDetail(recordId) {
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const record = history.find(r => r.id === recordId);
    
    if (record) {
        alert(`전송 상세 정보\n\n` +
              `전송 시간: ${new Date(record.timestamp).toLocaleString()}\n` +
              `채널: ${getChannelName(record.channel)}\n` +
              `상태: ${record.status === 'success' ? '성공' : '실패'}\n` +
              `헤더: ${record.header}\n` +
              `메시지 길이: ${record.message_length || 0}자`);
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
    updatePendingArticles();
    updateNextSendTime();
    loadRecentActivity();
}

function refreshDashboard() {
    const refreshBtn = event.target;
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
                const lastUpdate = new Date(data.lastUpdated);
                if (lastUpdate.toDateString() === today && data.articles) {
                    todayCount = data.articles.length;
                }
            }
        } catch (error) {
            console.error('스크랩 데이터 파싱 오류:', error);
        }
    }
    
    // 실제 스크랩이 구현되기 전까지는 시뮬레이션 데이터도 함께 표시
    if (todayCount === 0) {
        // 시뮬레이션 데이터 생성 및 저장
        todayCount = Math.floor(Math.random() * 30) + 10;
        const simulatedData = {
            lastUpdated: new Date().toISOString(),
            articles: Array(todayCount).fill(null).map((_, i) => ({
                id: `sim-${Date.now()}-${i}`,
                title: `시뮬레이션 기사 ${i + 1}`,
                source: 'Simulation',
                timestamp: new Date().toISOString()
            }))
        };
        localStorage.setItem('singapore_news_scraped_data', JSON.stringify(simulatedData));
    }
    
    const element = document.getElementById('todayArticles');
    if (element) {
        const currentValue = parseInt(element.textContent) || 0;
        animateNumber(element, currentValue, todayCount);
    }
}

function updatePendingArticles() {
    // 설정에서 전송 대기 중인 기사 확인
    const settings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    let pendingCount = 0;
    
    if (scrapedData && settings.sendChannel) {
        try {
            const data = JSON.parse(scrapedData);
            if (data.articles) {
                // 아직 전송되지 않은 기사 수
                const sentHistory = JSON.parse(localStorage.getItem('singapore_news_sent_articles') || '[]');
                const sentIds = new Set(sentHistory.map(h => h.articleId));
                
                pendingCount = data.articles.filter(article => !sentIds.has(article.id)).length;
            }
        } catch (error) {
            console.error('대기 기사 계산 오류:', error);
        }
    }
    
    const element = document.getElementById('pendingArticles');
    if (element) {
        const currentValue = parseInt(element.textContent) || 0;
        animateNumber(element, currentValue, pendingCount);
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
    
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const testHistory = JSON.parse(localStorage.getItem('singapore_news_test_history') || '[]');
    
    // 모든 활동을 합치고 정렬
    const allActivities = [
        ...history.map(h => ({...h, type: 'send'})),
        ...testHistory.map(h => ({...h, type: 'test'}))
    ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    if (allActivities.length === 0) {
        activityList.innerHTML = '<p class="no-data">최근 활동이 없습니다.</p>';
        return;
    }
    
    const recentActivities = allActivities.slice(0, 5);
    activityList.innerHTML = recentActivities.map(activity => {
        const time = new Date(activity.timestamp).toLocaleString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric'
        });
        
        const icon = activity.type === 'test' ? '🧪' : '📤';
        const status = activity.status === 'success' ? 
            '<span class="status-success">성공</span>' : 
            '<span class="status-failed">실패</span>';
        
        return `
            <div class="activity-item">
                <span class="activity-icon">${icon}</span>
                <div class="activity-content">
                    <div class="activity-title">
                        ${activity.type === 'test' ? '테스트 전송' : '뉴스 전송'}
                        ${status}
                    </div>
                    <div class="activity-time">${time}</div>
                </div>
            </div>
        `;
    }).join('');
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
    
    if (articlesList.style.display === 'none') {
        articlesList.style.display = 'block';
        toggleText.textContent = '접기';
        loadScrapedArticles();
    } else {
        articlesList.style.display = 'none';
        toggleText.textContent = '펼치기';
    }
}

function loadScrapedArticles() {
    const articlesList = document.getElementById('scrapedArticlesList');
    if (!articlesList) return;
    
    const scrapedData = localStorage.getItem('singapore_news_scraped_data');
    
    if (!scrapedData) {
        articlesList.innerHTML = '<p class="no-data">스크랩된 기사가 없습니다.</p>';
        return;
    }
    
    try {
        const data = JSON.parse(scrapedData);
        const today = new Date().toDateString();
        const lastUpdate = new Date(data.lastUpdated);
        
        if (lastUpdate.toDateString() !== today || !data.articles || data.articles.length === 0) {
            articlesList.innerHTML = '<p class="no-data">오늘 스크랩된 기사가 없습니다.</p>';
            return;
        }
        
        // 기사를 소스별로 그룹화
        const groupedArticles = data.articles.reduce((groups, article) => {
            const source = article.source || 'Unknown';
            if (!groups[source]) groups[source] = [];
            groups[source].push(article);
            return groups;
        }, {});
        
        let html = '';
        Object.entries(groupedArticles).forEach(([source, articles]) => {
            html += `
                <div class="article-group">
                    <h4 class="article-source">${source} (${articles.length})</h4>
                    ${articles.map(article => `
                        <div class="article-item">
                            <div class="article-title">${article.title}</div>
                            ${article.summary ? `<div class="article-summary">${article.summary}</div>` : ''}
                            <div class="article-meta">
                                <span class="article-time">${new Date(article.timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}</span>
                                ${article.url ? `<a href="${article.url}" target="_blank" class="article-link">원문 보기 →</a>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        });
        
        articlesList.innerHTML = html;
    } catch (error) {
        console.error('기사 로드 오류:', error);
        articlesList.innerHTML = '<p class="error-message">기사를 불러오는 중 오류가 발생했습니다.</p>';
    }
}