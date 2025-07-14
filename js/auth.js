const AUTH_KEY = 'singapore_news_auth';
const USERS_KEY = 'singapore_news_users';

const defaultUsers = [
    {
        id: 'admin',
        password: 'Admin@123',
        name: '관리자',
        email: 'admin@example.com',
        role: 'admin'
    }
];

function initializeUsers() {
    const users = localStorage.getItem(USERS_KEY);
    if (!users) {
        localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
    }
}

function login(username, password) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const user = users.find(u => u.id === username && u.password === password);
    
    if (user) {
        const authData = {
            userId: user.id,
            name: user.name,
            role: user.role,
            email: user.email,
            loginTime: new Date().toISOString()
        };
        localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
        return true;
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