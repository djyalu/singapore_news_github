const AUTH_KEY = 'singapore_news_auth';

// API를 통한 로그인
async function login(username, password) {
    console.log('로그인 시도:', { username, password: password ? '***' : 'empty' });
    
    if (!username || !password) {
        console.log('로그인 실패: 사용자명 또는 비밀번호가 비어있음');
        return false;
    }
    
    try {
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const apiUrl = isProduction ? '/api/auth-login' : 'https://singapore-news-github.vercel.app/api/auth-login';
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success && result.user) {
            const authData = {
                userId: result.user.id,
                name: result.user.name,
                role: result.user.role,
                email: result.user.email,
                loginTime: new Date().toISOString()
            };
            localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
            console.log('로그인 성공, 인증 데이터 저장:', authData);
            return true;
        } else {
            console.log('로그인 실패:', result.error);
            return false;
        }
    } catch (error) {
        console.error('로그인 에러:', error);
        // 오프라인 모드 또는 API 오류 시 임시 로그인 허용 (개발 환경에서만)
        if (!window.location.hostname.includes('github.io') && !window.location.hostname.includes('vercel')) {
            console.warn('개발 환경에서 임시 로그인 허용');
            if (username === 'admin' || username === 'djyalu') {
                const authData = {
                    userId: username,
                    name: username === 'admin' ? '관리자' : 'djyalu',
                    role: 'admin',
                    email: `${username}@example.com`,
                    loginTime: new Date().toISOString()
                };
                localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
                return true;
            }
        }
        return false;
    }
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    window.location.reload();
}

function getCurrentUser() {
    const authData = localStorage.getItem(AUTH_KEY);
    return authData ? JSON.parse(authData) : null;
}

function isAuthenticated() {
    return getCurrentUser() !== null;
}

function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'admin';
}

// 사용자 설정 확인 (환경 변수 설정 여부)
async function checkAuthConfig() {
    try {
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const apiUrl = isProduction ? '/api/auth-config' : 'https://singapore-news-github.vercel.app/api/auth-config';
        
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