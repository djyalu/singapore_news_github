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

// 사용자 관리 함수들
function getAllUsers() {
    const users = JSON.parse(localStorage.getItem('singapore_news_users') || '[]');
    
    // 기본 관리자 계정이 없으면 추가
    if (users.length === 0) {
        const defaultAdmin = {
            id: 'admin',
            name: '관리자',
            email: 'admin@example.com',
            role: 'admin',
            password: 'Admin@123' // 실제로는 해시화되어야 함
        };
        users.push(defaultAdmin);
        localStorage.setItem('singapore_news_users', JSON.stringify(users));
    }
    
    return users;
}

function addUser(userData) {
    try {
        // 유효성 검사
        if (!userData.id || !userData.password || !userData.name || !userData.email) {
            return { success: false, message: '모든 필드를 입력해주세요.' };
        }
        
        // 비밀번호 복잡성 검사
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(userData.password)) {
            return { success: false, message: '비밀번호는 대소문자, 숫자, 특수문자를 포함하여 8자 이상이어야 합니다.' };
        }
        
        const users = getAllUsers();
        
        // 중복 ID 확인
        if (users.find(user => user.id === userData.id)) {
            return { success: false, message: '이미 존재하는 사용자 ID입니다.' };
        }
        
        // 중복 이메일 확인
        if (users.find(user => user.email === userData.email)) {
            return { success: false, message: '이미 존재하는 이메일입니다.' };
        }
        
        // 새 사용자 추가
        users.push({
            id: userData.id,
            name: userData.name,
            email: userData.email,
            role: userData.role || 'user',
            password: userData.password // 실제로는 해시화되어야 함
        });
        
        localStorage.setItem('singapore_news_users', JSON.stringify(users));
        return { success: true, message: '사용자가 추가되었습니다.' };
    } catch (error) {
        console.error('사용자 추가 오류:', error);
        return { success: false, message: '사용자 추가 중 오류가 발생했습니다.' };
    }
}

function updateUser(userId, updates) {
    try {
        const users = getAllUsers();
        const userIndex = users.findIndex(user => user.id === userId);
        
        if (userIndex === -1) {
            return { success: false, message: '사용자를 찾을 수 없습니다.' };
        }
        
        // 비밀번호 변경 시 복잡성 검사
        if (updates.password) {
            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
            if (!passwordRegex.test(updates.password)) {
                return { success: false, message: '비밀번호는 대소문자, 숫자, 특수문자를 포함하여 8자 이상이어야 합니다.' };
            }
        }
        
        // 이메일 변경 시 중복 확인
        if (updates.email && updates.email !== users[userIndex].email) {
            if (users.find(user => user.email === updates.email && user.id !== userId)) {
                return { success: false, message: '이미 존재하는 이메일입니다.' };
            }
        }
        
        // 사용자 정보 업데이트
        users[userIndex] = { ...users[userIndex], ...updates };
        localStorage.setItem('singapore_news_users', JSON.stringify(users));
        
        return { success: true, message: '사용자 정보가 수정되었습니다.' };
    } catch (error) {
        console.error('사용자 수정 오류:', error);
        return { success: false, message: '사용자 수정 중 오류가 발생했습니다.' };
    }
}

function deleteUser(userId) {
    try {
        // 관리자 계정 삭제 방지
        if (userId === 'admin') {
            return { success: false, message: '관리자 계정은 삭제할 수 없습니다.' };
        }
        
        const users = getAllUsers();
        const filteredUsers = users.filter(user => user.id !== userId);
        
        if (filteredUsers.length === users.length) {
            return { success: false, message: '사용자를 찾을 수 없습니다.' };
        }
        
        localStorage.setItem('singapore_news_users', JSON.stringify(filteredUsers));
        return { success: true, message: '사용자가 삭제되었습니다.' };
    } catch (error) {
        console.error('사용자 삭제 오류:', error);
        return { success: false, message: '사용자 삭제 중 오류가 발생했습니다.' };
    }
}