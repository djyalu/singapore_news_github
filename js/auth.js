const AUTH_KEY = 'singapore_news_auth';
const USERS_KEY = 'singapore_news_users';

const defaultUsers = [
    {
        id: 'admin',
        password: 'Admin@123',
        name: '관리자',
        email: 'admin@example.com',
        role: 'admin'
    },
    {
        id: 'djyalu',
        password: 'djyalu123',
        name: 'djyalu',
        email: 'djyalu@github.com',
        role: 'admin'
    }
];

function initializeUsers() {
    // 사용자 데이터가 없으면 초기화
    const existingUsers = localStorage.getItem(USERS_KEY);
    if (!existingUsers) {
        console.log('사용자 데이터 초기화 중...');
        localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
        console.log('초기화된 사용자 데이터:', defaultUsers);
    } else {
        console.log('기존 사용자 데이터 발견:', JSON.parse(existingUsers));
        // 기본 사용자가 없으면 추가
        const users = JSON.parse(existingUsers);
        let needsUpdate = false;
        
        defaultUsers.forEach(defaultUser => {
            if (!users.find(u => u.id === defaultUser.id)) {
                users.push(defaultUser);
                needsUpdate = true;
            }
        });
        
        if (needsUpdate) {
            localStorage.setItem(USERS_KEY, JSON.stringify(users));
            console.log('기본 사용자 추가됨:', users);
        }
    }
}

function login(username, password) {
    console.log('로그인 시도:', { username, password: password ? '***' : 'empty' });
    
    if (!username || !password) {
        console.log('로그인 실패: 사용자명 또는 비밀번호가 비어있음');
        return false;
    }
    
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    console.log('저장된 사용자 목록:', users.map(u => ({ id: u.id, name: u.name, role: u.role })));
    
    const user = users.find(u => u.id === username && u.password === password);
    console.log('찾은 사용자:', user ? { id: user.id, name: user.name, role: user.role } : null);
    
    if (user) {
        const authData = {
            userId: user.id,
            name: user.name,
            role: user.role,
            email: user.email,
            loginTime: new Date().toISOString()
        };
        localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
        console.log('로그인 성공, 인증 데이터 저장:', authData);
        return true;
    }
    
    // 실패 원인 세부 분석
    const userExists = users.find(u => u.id === username);
    if (userExists) {
        console.log('로그인 실패: 비밀번호가 일치하지 않음');
    } else {
        console.log('로그인 실패: 존재하지 않는 사용자명');
    }
    return false;
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

function validatePassword(password) {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
}

function addUser(userData) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    if (users.find(u => u.id === userData.id)) {
        return { success: false, message: '이미 존재하는 ID입니다.' };
    }
    
    if (!validatePassword(userData.password)) {
        return { success: false, message: '비밀번호는 8자 이상, 대소문자와 특수문자를 포함해야 합니다.' };
    }
    
    users.push(userData);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    return { success: true };
}

function updateUser(userId, updates) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const index = users.findIndex(u => u.id === userId);
    
    if (index === -1) {
        return { success: false, message: '사용자를 찾을 수 없습니다.' };
    }
    
    if (updates.password && !validatePassword(updates.password)) {
        return { success: false, message: '비밀번호는 8자 이상, 대소문자와 특수문자를 포함해야 합니다.' };
    }
    
    users[index] = { ...users[index], ...updates };
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    return { success: true };
}

function deleteUser(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const filtered = users.filter(u => u.id !== userId);
    localStorage.setItem(USERS_KEY, JSON.stringify(filtered));
    return { success: true };
}

function getAllUsers() {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
}

initializeUsers();