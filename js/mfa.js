const MFA_KEY = 'singapore_news_mfa';

function generateSecret() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let secret = '';
    // 16바이트 = 26자 base32 (padding 제외)
    for (let i = 0; i < 16; i++) {
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

function base32Decode(secret) {
    const base32Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let bits = '';
    let hex = '';
    
    // Remove spaces and convert to uppercase
    secret = secret.replace(/\s/g, '').toUpperCase();
    
    for (let i = 0; i < secret.length; i++) {
        const val = base32Chars.indexOf(secret.charAt(i));
        if (val === -1) throw new Error('Invalid base32 character');
        bits += val.toString(2).padStart(5, '0');
    }
    
    for (let i = 0; i + 8 <= bits.length; i += 8) {
        hex += parseInt(bits.substr(i, 8), 2).toString(16).padStart(2, '0');
    }
    
    return hex;
}

function hexToBytes(hex) {
    const bytes = [];
    for (let i = 0; i < hex.length; i += 2) {
        bytes.push(parseInt(hex.substr(i, 2), 16));
    }
    return new Uint8Array(bytes);
}

async function generateHOTP(secret, counter) {
    const key = hexToBytes(base32Decode(secret));
    const counterBytes = new Uint8Array(8);
    
    // Convert counter to 8-byte array (big-endian)
    for (let i = 7; i >= 0; i--) {
        counterBytes[i] = counter & 0xff;
        counter = Math.floor(counter / 256);
    }
    
    // Import the key
    const cryptoKey = await crypto.subtle.importKey(
        'raw',
        key,
        { name: 'HMAC', hash: 'SHA-1' },
        false,
        ['sign']
    );
    
    // Generate HMAC
    const signature = await crypto.subtle.sign('HMAC', cryptoKey, counterBytes);
    const signatureArray = new Uint8Array(signature);
    
    // Dynamic truncation
    const offset = signatureArray[signatureArray.length - 1] & 0x0f;
    const code = (
        ((signatureArray[offset] & 0x7f) << 24) |
        ((signatureArray[offset + 1] & 0xff) << 16) |
        ((signatureArray[offset + 2] & 0xff) << 8) |
        (signatureArray[offset + 3] & 0xff)
    ) % 1000000;
    
    return code.toString().padStart(6, '0');
}

async function verifyTOTP(secret, token) {
    try {
        const timeStep = 30; // 30 seconds
        const currentTime = Math.floor(Date.now() / 1000);
        const currentCounter = Math.floor(currentTime / timeStep);
        
        // Check current window and adjacent windows (for time sync issues)
        for (let i = -2; i <= 2; i++) {
            const counter = currentCounter + i;
            const expectedToken = await generateHOTP(secret, counter);
            
            if (expectedToken === token.toString().padStart(6, '0')) {
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