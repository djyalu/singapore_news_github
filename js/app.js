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
            if (isMFAEnabled(username)) {
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
    
    function loadPage(page) {
        const content = document.getElementById('content');
        
        switch(page) {
            case 'dashboard':
                content.innerHTML = getDashboardHTML();
                break;
            case 'settings':
                if (isAdmin()) {
                    content.innerHTML = getSettingsHTML();
                    initializeSettings();
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
                        <p class="stat-number">0</p>
                    </div>
                    <div class="stat-card">
                        <h3>전송 예정 기사</h3>
                        <p class="stat-number">0</p>
                    </div>
                    <div class="stat-card">
                        <h3>다음 전송 시간</h3>
                        <p class="stat-text">-</p>
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
                        <textarea id="testMessage" rows="3" placeholder="테스트 메시지를 입력하세요...">🧪 테스트 메시지입니다.

Singapore News Scraper 시스템이 정상적으로 작동하고 있습니다.

📅 전송 시간: ${new Date().toLocaleString()}
⚙️ 시스템 상태: 정상</textarea>
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
                
                <button class="btn" onclick="saveSettings()">설정 저장</button>
            </div>
        `;
    }
    
    function getHistoryHTML() {
        return `
            <div class="page-section">
                <h2>전송 이력</h2>
                <div class="form-group">
                    <label>기간 선택</label>
                    <input type="date" id="historyStartDate">
                    <input type="date" id="historyEndDate">
                    <button class="btn" onclick="loadHistory()">조회</button>
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
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('mfaContainer').style.display = 'block';
        
        const mfaForm = document.getElementById('mfaForm');
        const mfaBackBtn = document.getElementById('mfaBackBtn');
        const mfaErrorMessage = document.getElementById('mfaErrorMessage');
        
        mfaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('mfaCode').value;
            
            if (verifyMFA(username, code)) {
                checkAuth();
            } else {
                mfaErrorMessage.textContent = '잘못된 인증 코드입니다.';
            }
        });
        
        mfaBackBtn.addEventListener('click', function() {
            logout();
            document.getElementById('mfaContainer').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
        });
    }
    
    function verifyMFA(username, code) {
        const secret = getMFASecret(username);
        if (!secret) return false;
        
        if (verifyTOTP(secret, code)) {
            return true;
        }
        
        const backupResult = useBackupCode(username, code);
        return backupResult.success;
    }
    
    function getMFASettingsHTML() {
        const currentUser = getCurrentUser();
        const mfaEnabled = isMFAEnabled(currentUser.userId);
        
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
                        <button class="btn" onclick="setupMFA()">MFA 설정 시작</button>
                    </div>
                ` : `
                    <div class="mfa-manage">
                        <h3>MFA 관리</h3>
                        <button class="btn" onclick="showBackupCodes()">백업 코드 보기</button>
                        <button class="btn" onclick="regenerateBackupCodes()">백업 코드 재생성</button>
                        <button class="btn btn-danger" onclick="disableMFAConfirm()">MFA 비활성화</button>
                    </div>
                `}
                
                <div id="mfaSetupModal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h3>MFA 설정</h3>
                        <div id="mfaSetupStep1">
                            <p>1. 인증 앱에서 아래 QR 코드를 스캔하세요:</p>
                            <canvas id="qrCode"></canvas>
                            <p>또는 수동으로 입력: <code id="secretCode"></code></p>
                            <button class="btn" onclick="nextMFAStep()">다음</button>
                        </div>
                        <div id="mfaSetupStep2" style="display: none;">
                            <p>2. 인증 앱에서 생성된 6자리 코드를 입력하세요:</p>
                            <input type="text" id="setupMfaCode" placeholder="000000" maxlength="6">
                            <button class="btn" onclick="completeMFASetup()">완료</button>
                        </div>
                        <div id="mfaSetupStep3" style="display: none;">
                            <h4>백업 코드</h4>
                            <p>MFA 기기를 분실했을 때 사용할 백업 코드입니다. 안전한 곳에 보관하세요.</p>
                            <div id="backupCodesList"></div>
                            <button class="btn" onclick="finishMFASetup()">완료</button>
                        </div>
                        <button class="btn btn-danger" onclick="closeMFAModal()">취소</button>
                    </div>
                </div>
                
                <div id="backupCodesModal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <h3>백업 코드</h3>
                        <div id="currentBackupCodes"></div>
                        <button class="btn" onclick="closeBackupCodesModal()">닫기</button>
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
    
    // 시뮬레이션 전송 (실제 환경에서는 API 호출)
    setTimeout(() => {
        const success = Math.random() > 0.3; // 70% 성공률로 시뮬레이션
        
        if (success) {
            testResult.innerHTML = '<div class="success-message">✅ 테스트 메시지가 성공적으로 전송되었습니다!</div>';
            recordTestHistory(testChannel, 'success', processedMessage);
        } else {
            testResult.innerHTML = '<div class="error-message">❌ 테스트 메시지 전송에 실패했습니다. 설정을 확인하세요.</div>';
            recordTestHistory(testChannel, 'failed', processedMessage);
        }
        
        // 버튼 복원
        testSendBtn.disabled = false;
        testSendBtn.textContent = '테스트 전송';
        
        // 테스트 이력 새로고침
        loadTestHistory();
    }, 2000);
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
        '120363419092108413@g.us': 'Singapore News Main (Test)',
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
    
    localStorage.setItem('singapore_news_settings', JSON.stringify(settings));
    alert('설정이 저장되었습니다.');
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

document.addEventListener('submit', function(e) {
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
        loadSites();
        e.target.reset();
    }
});

function deleteSite(index) {
    const sites = JSON.parse(localStorage.getItem('singapore_news_sites') || '[]');
    sites.splice(index, 1);
    localStorage.setItem('singapore_news_sites', JSON.stringify(sites));
    loadSites();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('singapore_news_history') || '[]');
    const tbody = document.querySelector('#historyTable tbody');
    tbody.innerHTML = '';
    
    history.forEach(record => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${new Date(record.timestamp).toLocaleString()}</td>
            <td>${record.header}</td>
            <td>${record.channel}</td>
            <td>${record.status}</td>
            <td><button class="btn" onclick="showHistoryDetail('${record.id}')">상세</button></td>
        `;
    });
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
        alert('사용자가 추가되었습니다.');
        hideAddUserForm();
        loadUsers();
        event.target.reset();
    } else {
        alert(result.message);
    }
}

function resetUserPassword(userId) {
    const newPassword = prompt('새 비밀번호를 입력하세요 (특수기호, 대소문자 포함 8글자 이상):');
    if (newPassword) {
        const result = updateUser(userId, { password: newPassword });
        if (result.success) {
            alert('비밀번호가 변경되었습니다.');
        } else {
            alert(result.message);
        }
    }
}

function deleteUserConfirm(userId) {
    if (confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
        deleteUser(userId);
        loadUsers();
        alert('사용자가 삭제되었습니다.');
    }
}

function showEditUserModal(userId) {
    const users = getAllUsers();
    const user = users.find(u => u.id === userId);
    
    if (!user) {
        alert('사용자를 찾을 수 없습니다.');
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
        alert('사용자 정보가 수정되었습니다.');
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
        alert('사용자 정보 수정에 실패했습니다: ' + result.message);
    }
}