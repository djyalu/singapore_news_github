// 서버 전용 인증 - sessionStorage 사용 (탭이 열려있는 동안만 유지)
let currentUser = null;

// 페이지 로드시 세션 복원
function restoreSession() {
    const sessionData = sessionStorage.getItem('userSession');
    if (sessionData) {
        try {
            currentUser = JSON.parse(sessionData);
            // 세션 만료 확인 (24시간)
            const loginTime = new Date(currentUser.loginTime);
            const now = new Date();
            const hoursSinceLogin = (now - loginTime) / (1000 * 60 * 60);
            
            if (hoursSinceLogin > 24) {
                // 24시간 경과시 세션 만료
                sessionStorage.removeItem('userSession');
                currentUser = null;
            }
        } catch (e) {
            sessionStorage.removeItem('userSession');
            currentUser = null;
        }
    }
}

// 초기화시 세션 복원
console.log('[AUTH] 페이지 로드 - 세션 복원 시작');
restoreSession();
console.log('[AUTH] 현재 사용자:', currentUser);

// API를 통한 로그인
async function login(username, password) {
    console.log('로그인 시도:', { username, password: password ? '***' : 'empty' });
    
    if (!username || !password) {
        console.log('로그인 실패: 사용자명 또는 비밀번호가 비어있음');
        return false;
    }
    
    try {
        // 항상 Vercel API 사용 (GitHub Pages에서는 /api/ 경로 불가)
        const apiUrl = 'https://singapore-news-github.vercel.app/api/auth';
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success && result.user) {
            currentUser = {
                userId: result.user.id,
                name: result.user.name,
                role: result.user.role,
                email: result.user.email,
                loginTime: new Date().toISOString()
            };
            // 세션 저장 (탭이 열려있는 동안 유지)
            sessionStorage.setItem('userSession', JSON.stringify(currentUser));
            console.log('로그인 성공, 서버 인증 완료:', currentUser);
            return true;
        } else {
            console.log('로그인 실패:', result.error);
            return false;
        }
    } catch (error) {
        console.error('로그인 에러:', error);
        return false;
    }
}

function logout() {
    currentUser = null;
    sessionStorage.removeItem('userSession');
    window.location.reload();
}

function getCurrentUser() {
    return currentUser;
}

function isAuthenticated() {
    return currentUser !== null;
}

function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// 사용자 설정 확인 (환경 변수 설정 여부)
async function checkAuthConfig() {
    try {
        // 항상 Vercel API 사용 (GitHub Pages에서는 /api/ 경로 불가)
        const apiUrl = 'https://singapore-news-github.vercel.app/api/auth';
        
        const response = await fetch(apiUrl);
        const result = await response.json();
        
        if (result.success && result.config) {
            return result.config;
        }
    } catch (error) {
        console.error('인증 설정 확인 에러:', error);
    }
    return null;
}

// 서버 기반 사용자 관리
async function getAllUsers() {
    try {
        const apiUrl = 'https://singapore-news-github.vercel.app/api/auth';
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            console.error('사용자 목록 API 응답 오류:', response.status);
            return [];
        }
        
        const result = await response.json();
        console.log('사용자 목록 API 응답:', result);
        
        if (result.success && result.config && result.config.users) {
            const users = result.config.users;
            // 배열인지 확인
            if (Array.isArray(users)) {
                return users;
            } else {
                console.error('users가 배열이 아닙니다:', typeof users, users);
                return [];
            }
        }
        
        console.log('사용자 목록이 비어있거나 형식이 올바르지 않습니다');
        return [];
    } catch (error) {
        console.error('사용자 목록 조회 에러:', error);
        return [];
    }
}

// 사용자 관리는 서버측에서만 처리
async function addUser(userData) {
    console.warn('사용자 추가는 서버에서만 가능합니다.');
    return { 
        success: false, 
        message: '사용자 추가는 서버 환경 변수에서만 가능합니다.\n\nVercel 대시보드에서 환경 변수를 수정하세요:\n1. Vercel 대시보드 접속\n2. Settings → Environment Variables\n3. AUTH_CONFIG 환경 변수 수정' 
    };
}

async function updateUser(userId, updates) {
    console.warn('사용자 수정은 서버에서만 가능합니다.');
    return { 
        success: false, 
        message: '사용자 수정은 서버 환경 변수에서만 가능합니다.\n\nVercel 대시보드에서 AUTH_CONFIG 환경 변수를 수정하세요.' 
    };
}

async function deleteUser(userId) {
    console.warn('사용자 삭제는 서버에서만 가능합니다.');
    return { 
        success: false, 
        message: '사용자 삭제는 서버 환경 변수에서만 가능합니다.\n\nVercel 대시보드에서 AUTH_CONFIG 환경 변수를 수정하세요.' 
    };
}

// DOM 로드 완료 후 로그인 폼 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    console.log('[AUTH] DOM 로드 완료, 로그인 시스템 초기화');
    
    // 이미 로그인되어 있으면 대시보드로 이동
    if (isAuthenticated()) {
        console.log('[AUTH] 이미 로그인됨, 대시보드 표시');
        showDashboard();
        return;
    }
    
    // 로그인 폼 이벤트 리스너 추가
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('[AUTH] 로그인 폼 이벤트 리스너 추가');
        loginForm.addEventListener('submit', handleLogin);
    } else {
        console.error('[AUTH] 로그인 폼을 찾을 수 없습니다');
    }
});

// 로그인 폼 처리
async function handleLogin(e) {
    e.preventDefault();
    console.log('[AUTH] 로그인 폼 제출');
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // 에러 메시지 초기화
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.style.display = 'none';
        errorMessage.textContent = '';
        errorMessage.classList.add('hidden');
        console.log('[AUTH] 에러 메시지 초기화됨');
    }
    
    // 입력 검증
    if (!username || !password) {
        showLoginError('사용자명과 비밀번호를 입력해주세요.');
        return;
    }
    
    // 로그인 시도
    const success = await login(username, password);
    
    if (success) {
        console.log('[AUTH] 로그인 성공, 대시보드로 이동');
        showDashboard();
    } else {
        showLoginError('로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요.');
    }
}

// 로그인 에러 표시
function showLoginError(message) {
    console.log('[AUTH] 에러 표시:', message);
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.classList.remove('hidden');
        console.log('[AUTH] 에러 메시지 표시됨');
    } else {
        console.error('[AUTH] 에러 메시지 요소를 찾을 수 없음');
        alert(message);
    }
}

// 대시보드 표시
function showDashboard() {
    console.log('[AUTH] showDashboard 호출됨');
    
    const loginContainer = document.getElementById('loginContainer');
    const mainContainer = document.getElementById('mainContainer');
    
    console.log('[AUTH] 컨테이너 요소들:', {
        loginContainer: !!loginContainer,
        mainContainer: !!mainContainer
    });
    
    if (loginContainer && mainContainer) {
        console.log('[AUTH] 컨테이너 표시 상태 변경');
        loginContainer.style.display = 'none';
        mainContainer.style.display = 'block';
        
        // app.js의 초기화 함수 호출 (있다면)
        if (typeof initializeDashboard === 'function') {
            console.log('[AUTH] initializeDashboard 함수 호출');
            initializeDashboard();
        } else {
            console.error('[AUTH] initializeDashboard 함수를 찾을 수 없음');
        }
        
        // 사용자 정보 업데이트 (있다면)
        if (typeof updateNavigation === 'function') {
            console.log('[AUTH] updateNavigation 함수 호출');
            updateNavigation();
        } else {
            console.warn('[AUTH] updateNavigation 함수를 찾을 수 없음');
        }
    } else {
        console.error('[AUTH] 필요한 컨테이너 요소를 찾을 수 없음');
    }
}