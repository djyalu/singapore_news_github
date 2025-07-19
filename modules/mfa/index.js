/**
 * MFA Module Index
 * MFA 모듈의 메인 진입점
 */

import { MFACore } from './mfa-core.js';
import { MFAStorage } from './mfa-storage.js';
import { MFAUI } from './mfa-ui.js';

// 전역 객체로 내보내기 (기존 코드와의 호환성을 위해)
window.MFA = {
    // Core functions
    generateSecret: (userId) => MFAStorage.generateSecret(userId),
    verifyTOTP: (secret, token) => MFACore.verifyTOTP(secret, token),
    generateHOTP: (secret, counter) => MFACore.generateHOTP(secret, counter),
    
    // Storage functions (서버 기반)
    enableMFA: (userId, secret, token) => MFAStorage.enableMFA(userId, secret, token),
    disableMFA: (userId) => MFAStorage.disableMFA(userId),
    isMFAEnabled: (userId) => MFAStorage.isMFAEnabled(userId),
    getMFAStatus: (userId) => MFAStorage.getMFAStatus(userId),
    verifyToken: (userId, token) => MFAStorage.verifyToken(userId, token),
    useBackupCode: (userId, code) => MFAStorage.useBackupCode(userId, code),
    
    // UI functions
    setupMFA: (getCurrentUser) => MFAUI.setupMFA(getCurrentUser),
    completeMFASetup: (getCurrentUser) => MFAUI.completeMFASetup(getCurrentUser),
    nextMFAStep: () => MFAUI.nextMFAStep(),
    finishMFASetup: () => MFAUI.finishMFASetup(),
    closeMFAModal: () => MFAUI.closeMFAModal(),
    disableMFAConfirm: (getCurrentUser) => MFAUI.disableMFAConfirm(getCurrentUser),
    showBackupCodes: (getCurrentUser) => MFAUI.showBackupCodes(getCurrentUser),
    closeBackupCodesModal: () => MFAUI.closeBackupCodesModal(),
    regenerateBackupCodesUI: (getCurrentUser) => MFAUI.regenerateBackupCodes(getCurrentUser)
};

// 기존 함수 매핑 (하위 호환성) - 서버 기반으로 업데이트
window.generateSecret = window.MFA.generateSecret;
window.verifyTOTP = window.MFA.verifyTOTP;
window.generateHOTP = window.MFA.generateHOTP;
window.enableMFA = window.MFA.enableMFA;
window.disableMFA = window.MFA.disableMFA;
window.isMFAEnabled = window.MFA.isMFAEnabled;
window.getMFASecret = window.MFA.getMFAStatus; // 서버 기반으로 변경
window.useBackupCode = window.MFA.useBackupCode;
window.verifyMFAToken = window.MFA.verifyToken; // 새로운 함수 추가

export { MFACore, MFAStorage, MFAUI };