/**
 * MFA Storage Module - 서버 기반
 * MFA 관련 데이터 저장 및 관리 (Vercel API 사용)
 */

export const MFAStorage = {
    API_BASE: 'https://singapore-news-github.vercel.app/api/mfa',

    /**
     * 사용자의 MFA 활성화
     */
    async enableMFA(userId, secret, token) {
        try {
            const response = await fetch(`${this.API_BASE}?action=enable&userId=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ secret, token })
            });
            
            return await response.json();
        } catch (error) {
            console.error('MFA 활성화 에러:', error);
            return { success: false, message: 'MFA 활성화 중 오류가 발생했습니다.' };
        }
    },

    /**
     * 사용자의 MFA 비활성화
     */
    async disableMFA(userId) {
        try {
            const response = await fetch(`${this.API_BASE}?action=disable&userId=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            return await response.json();
        } catch (error) {
            console.error('MFA 비활성화 에러:', error);
            return { success: false, message: 'MFA 비활성화 중 오류가 발생했습니다.' };
        }
    },

    /**
     * MFA 활성화 여부 확인
     */
    async isMFAEnabled(userId) {
        try {
            const response = await fetch(`${this.API_BASE}?action=status&userId=${userId}`);
            const result = await response.json();
            return result.success ? result.enabled : false;
        } catch (error) {
            console.error('MFA 상태 확인 에러:', error);
            return false;
        }
    },

    /**
     * MFA Secret 생성
     */
    async generateSecret(userId) {
        try {
            const response = await fetch(`${this.API_BASE}?action=generate-secret&userId=${userId}`);
            return await response.json();
        } catch (error) {
            console.error('MFA Secret 생성 에러:', error);
            return { success: false, message: 'Secret 생성 중 오류가 발생했습니다.' };
        }
    },

    /**
     * MFA 토큰 검증
     */
    async verifyToken(userId, token) {
        try {
            const response = await fetch(`${this.API_BASE}?action=verify&userId=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });
            
            return await response.json();
        } catch (error) {
            console.error('MFA 토큰 검증 에러:', error);
            return { success: false, message: '토큰 검증 중 오류가 발생했습니다.' };
        }
    },

    /**
     * 백업 코드 사용 (verifyToken과 통합)
     */
    async useBackupCode(userId, code) {
        return this.verifyToken(userId, code);
    },

    /**
     * MFA 상태 조회
     */
    async getMFAStatus(userId) {
        try {
            const response = await fetch(`${this.API_BASE}?action=status&userId=${userId}`);
            return await response.json();
        } catch (error) {
            console.error('MFA 상태 조회 에러:', error);
            return { success: false, message: 'MFA 상태 조회 중 오류가 발생했습니다.' };
        }
    }
};