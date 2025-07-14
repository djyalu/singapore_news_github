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
            checkAuth();
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
    
    checkAuth();
});

function initializeSettings() {
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
    
    loadSettings();
    loadSites();
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('singapore_news_settings') || '{}');
    
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

function loadSites() {
    const sites = JSON.parse(localStorage.getItem('singapore_news_sites') || '[]');
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