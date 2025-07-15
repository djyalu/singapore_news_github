/**
 * MFA UI Module
 * MFA 관련 UI 컴포넌트 및 상호작용
 */

import { MFACore } from './mfa-core.js';
import { MFAStorage } from './mfa-storage.js';

export const MFAUI = {
    currentMFASecret: null,

    /**
     * MFA 설정 시작
     */
    async setupMFA(getCurrentUser) {
        const secret = MFACore.generateSecret();
        this.currentMFASecret = secret;
        
        const currentUser = getCurrentUser();
        this.generateQRCode(secret, currentUser.userId);
        
        // Secret을 보기 좋게 4자리씩 띄어서 표시
        const formattedSecret = secret.match(/.{1,4}/g).join(' ');
        document.getElementById('secretCode').textContent = formattedSecret;
        
        console.log('MFA Setup - Generated Secret:', secret);
        
        document.getElementById('mfaSetupModal').style.display = 'block';
    },

    /**
     * QR 코드 생성
     */
    generateQRCode(secret, username) {
        const otpauth = MFACore.generateOTPAuthURL(secret, username);
        
        const qr = new QRious({
            element: document.getElementById('qrCode'),
            value: otpauth,
            size: 200
        });
        
        return otpauth;
    },

    /**
     * MFA 설정 완료
     */
    async completeMFASetup(getCurrentUser) {
        const code = document.getElementById('setupMfaCode').value.trim();
        
        console.log('MFA Setup - Verifying code:', code);
        
        try {
            const isValid = await MFACore.verifyTOTP(this.currentMFASecret, code);
            
            if (isValid) {
                const currentUser = getCurrentUser();
                const result = MFAStorage.enableMFA(currentUser.userId, this.currentMFASecret);
                
                if (result.success) {
                    this.displayBackupCodes(result.backupCodes);
                    document.getElementById('mfaSetupStep2').style.display = 'none';
                    document.getElementById('mfaSetupStep3').style.display = 'block';
                } else {
                    alert('MFA 설정에 실패했습니다: ' + result.message);
                }
            } else {
                const currentCounter = Math.floor(Date.now() / 1000 / 30);
                const expectedCode = await MFACore.generateHOTP(this.currentMFASecret, currentCounter);
                alert(`잘못된 인증 코드입니다.\n\n입력한 코드: ${code}\n예상 코드: ${expectedCode}\n\nGoogle Authenticator에 키를 정확히 입력했는지 확인하세요.`);
            }
        } catch (error) {
            console.error('MFA Setup Error:', error);
            alert('MFA 설정 중 오류가 발생했습니다: ' + error.message);
        }
    },

    /**
     * 백업 코드 표시
     */
    displayBackupCodes(codes) {
        const container = document.getElementById('backupCodesList');
        container.innerHTML = codes.map(code => `<div class="backup-code">${code}</div>`).join('');
    },

    /**
     * MFA 설정 다음 단계
     */
    nextMFAStep() {
        document.getElementById('mfaSetupStep1').style.display = 'none';
        document.getElementById('mfaSetupStep2').style.display = 'block';
    },

    /**
     * MFA 설정 완료
     */
    finishMFASetup() {
        document.getElementById('mfaSetupModal').style.display = 'none';
        location.reload();
    },

    /**
     * MFA 모달 닫기
     */
    closeMFAModal() {
        document.getElementById('mfaSetupModal').style.display = 'none';
        this.currentMFASecret = null;
    },

    /**
     * MFA 비활성화 확인
     */
    async disableMFAConfirm(getCurrentUser) {
        if (confirm('MFA를 비활성화하시겠습니까? 보안이 약해질 수 있습니다.')) {
            const currentUser = getCurrentUser();
            const result = MFAStorage.disableMFA(currentUser.userId);
            
            if (result.success) {
                alert('MFA가 비활성화되었습니다.');
                location.reload();
            } else {
                alert('MFA 비활성화에 실패했습니다: ' + result.message);
            }
        }
    },

    /**
     * 백업 코드 보기
     */
    showBackupCodes(getCurrentUser) {
        const currentUser = getCurrentUser();
        const codes = MFAStorage.getBackupCodes(currentUser.userId);
        
        const container = document.getElementById('currentBackupCodes');
        if (codes.length === 0) {
            container.innerHTML = '<p>사용 가능한 백업 코드가 없습니다.</p>';
        } else {
            container.innerHTML = `
                <p>남은 백업 코드 ${codes.length}개:</p>
                ${codes.map(code => `<div class="backup-code">${code}</div>`).join('')}
            `;
        }
        
        document.getElementById('backupCodesModal').style.display = 'block';
    },

    /**
     * 백업 코드 모달 닫기
     */
    closeBackupCodesModal() {
        document.getElementById('backupCodesModal').style.display = 'none';
    },

    /**
     * 백업 코드 재생성
     */
    async regenerateBackupCodes(getCurrentUser) {
        if (confirm('새로운 백업 코드를 생성하시겠습니까? 기존 코드는 사용할 수 없게 됩니다.')) {
            const currentUser = getCurrentUser();
            const result = MFAStorage.regenerateBackupCodes(currentUser.userId);
            
            if (result.success) {
                alert('새로운 백업 코드가 생성되었습니다.');
                this.showBackupCodes(getCurrentUser);
            } else {
                alert('백업 코드 재생성에 실패했습니다: ' + result.message);
            }
        }
    }
};