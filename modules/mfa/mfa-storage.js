/**
 * MFA Storage Module
 * MFA 관련 데이터 저장 및 관리
 */

export const MFAStorage = {
    USERS_KEY: 'singapore_news_users',

    /**
     * 백업 코드 생성 (10개)
     */
    generateBackupCodes() {
        const codes = [];
        for (let i = 0; i < 10; i++) {
            let code = '';
            for (let j = 0; j < 8; j++) {
                code += Math.floor(Math.random() * 10);
            }
            codes.push(code);
        }
        return codes;
    },

    /**
     * 사용자의 MFA 활성화
     */
    enableMFA(userId, secret) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
        const userIndex = users.findIndex(u => u.id === userId);
        
        if (userIndex === -1) {
            return { success: false, message: '사용자를 찾을 수 없습니다.' };
        }
        
        const backupCodes = this.generateBackupCodes();
        
        users[userIndex].mfa = {
            enabled: true,
            secret: secret,
            backupCodes: backupCodes,
            enabledAt: new Date().toISOString()
        };
        
        localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
        
        return { success: true, backupCodes: backupCodes };
    },

    /**
     * 사용자의 MFA 비활성화
     */
    disableMFA(userId) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
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
        
        localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
        
        return { success: true };
    },

    /**
     * MFA 활성화 여부 확인
     */
    isMFAEnabled(userId) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
        const user = users.find(u => u.id === userId);
        return user && user.mfa && user.mfa.enabled;
    },

    /**
     * MFA Secret 가져오기
     */
    getMFASecret(userId) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
        const user = users.find(u => u.id === userId);
        return user && user.mfa ? user.mfa.secret : null;
    },

    /**
     * 백업 코드 사용
     */
    useBackupCode(userId, code) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
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
        
        localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
        
        return { success: true, remainingCodes: user.mfa.backupCodes.length };
    },

    /**
     * 백업 코드 가져오기
     */
    getBackupCodes(userId) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
        const user = users.find(u => u.id === userId);
        return user && user.mfa ? user.mfa.backupCodes : [];
    },

    /**
     * 백업 코드 재생성
     */
    regenerateBackupCodes(userId) {
        const users = JSON.parse(localStorage.getItem(this.USERS_KEY) || '[]');
        const userIndex = users.findIndex(u => u.id === userId);
        
        if (userIndex === -1) {
            return { success: false, message: '사용자를 찾을 수 없습니다.' };
        }
        
        const backupCodes = this.generateBackupCodes();
        users[userIndex].mfa.backupCodes = backupCodes;
        users[userIndex].mfa.backupCodesRegenerated = new Date().toISOString();
        
        localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
        
        return { success: true, backupCodes: backupCodes };
    }
};