// 서버 전용 인증 - 로컬 스토리지 사용 안함
let currentUser = null;

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

// 사용자 관리 함수들 - 서버에서만 실행
async function getAllUsers() {
    try {
        const apiUrl = 'https://singapore-news-github.vercel.app/api/auth';
        const response = await fetch(apiUrl);
        const result = await response.json();
        
        if (result.success && result.config) {
            return result.config.users || [];
        }
        return [];
    } catch (error) {
        console.error('사용자 목록 조회 에러:', error);
        return [];
    }
}

// 사용자 관리는 서버측에서만 처리
async function addUser(userData) {
    console.warn('사용자 추가는 서버에서만 가능합니다. data/users.json 파일을 직접 수정하세요.');
    return { success: false, message: '사용자 추가는 서버에서만 가능합니다.' };
}

async function updateUser(userId, updates) {
    console.warn('사용자 수정은 서버에서만 가능합니다. data/users.json 파일을 직접 수정하세요.');
    return { success: false, message: '사용자 수정은 서버에서만 가능합니다.' };
}

async function deleteUser(userId) {
    console.warn('사용자 삭제는 서버에서만 가능합니다. data/users.json 파일을 직접 수정하세요.');
    return { success: false, message: '사용자 삭제는 서버에서만 가능합니다.' };
}