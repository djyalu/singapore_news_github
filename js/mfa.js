const MFA_KEY = 'singapore_news_mfa';

function generateSecret() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let secret = '';
    for (let i = 0; i < 32; i++) {
        secret += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return secret;
}

function generateQRCode(secret, username) {
    const issuer = 'Singapore News Scraper';
    const otpauth = `otpauth://totp/${issuer}:${username}?secret=${secret}&issuer=${issuer}`;
    
    const qr = new QRious({
        element: document.getElementById('qrCode'),
        value: otpauth,
        size: 200
    });
    
    return otpauth;
}

function verifyTOTP(secret, token) {
    try {
        const totp = new jsOTP.totp();
        const currentToken = totp.getOtp(secret);
        
        // 현재 시간 윈도우와 이전/다음 윈도우 확인 (시간 동기화 오차 고려)
        const timeWindow = Math.floor(Date.now() / 1000 / 30);
        
        for (let i = -1; i <= 1; i++) {
            const testToken = totp.getOtp(secret, timeWindow + i);
            if (testToken === token) {
                return true;
            }
        }
        
        return false;
    } catch (error) {
        console.error('TOTP verification error:', error);
        return false;
    }
}

function generateBackupCodes() {
    const codes = [];
    for (let i = 0; i < 10; i++) {
        let code = '';
        for (let j = 0; j < 8; j++) {
            code += Math.floor(Math.random() * 10);
        }
        codes.push(code);
    }
    return codes;
}

function enableMFA(userId, secret) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return { success: false, message: '사용자를 찾을 수 없습니다.' };
    }
    
    const backupCodes = generateBackupCodes();
    
    users[userIndex].mfa = {
        enabled: true,
        secret: secret,
        backupCodes: backupCodes,
        enabledAt: new Date().toISOString()
    };
    
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    
    return { success: true, backupCodes: backupCodes };
}

function disableMFA(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return { success: false, message: '사용자를 찾을 수 없습니다.' };
    }
    
    users[userIndex].mfa = {
        enabled: false,
        secret: null,
        backupCodes: [],
        disabledAt: new Date().toISOString()
    };
    
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    
    return { success: true };
}

function isMFAEnabled(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const user = users.find(u => u.id === userId);
    return user && user.mfa && user.mfa.enabled;
}

function getMFASecret(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const user = users.find(u => u.id === userId);
    return user && user.mfa ? user.mfa.secret : null;
}

function useBackupCode(userId, code) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return { success: false, message: '사용자를 찾을 수 없습니다.' };
    }
    
    const user = users[userIndex];
    if (!user.mfa || !user.mfa.enabled) {
        return { success: false, message: 'MFA가 활성화되지 않았습니다.' };
    }
    
    const codeIndex = user.mfa.backupCodes.indexOf(code);
    if (codeIndex === -1) {
        return { success: false, message: '유효하지 않은 백업 코드입니다.' };
    }
    
    // 백업 코드 사용 후 제거
    user.mfa.backupCodes.splice(codeIndex, 1);
    user.mfa.lastBackupCodeUsed = new Date().toISOString();
    
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    
    return { success: true, remainingCodes: user.mfa.backupCodes.length };
}

function getBackupCodes(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const user = users.find(u => u.id === userId);
    return user && user.mfa ? user.mfa.backupCodes : [];
}

function regenerateBackupCodes(userId) {
    const users = JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex === -1) {
        return { success: false, message: '사용자를 찾을 수 없습니다.' };
    }
    
    const backupCodes = generateBackupCodes();
    users[userIndex].mfa.backupCodes = backupCodes;
    users[userIndex].mfa.backupCodesRegenerated = new Date().toISOString();
    
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    
    return { success: true, backupCodes: backupCodes };
}