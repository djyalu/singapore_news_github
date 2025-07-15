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
    generateSecret: () => MFACore.generateSecret(),
    verifyTOTP: (secret, token) => MFACore.verifyTOTP(secret, token),
    generateHOTP: (secret, counter) => MFACore.generateHOTP(secret, counter),
    
    // Storage functions
    enableMFA: (userId, secret) => MFAStorage.enableMFA(userId, secret),
    disableMFA: (userId) => MFAStorage.disableMFA(userId),
    isMFAEnabled: (userId) => MFAStorage.isMFAEnabled(userId),
    getMFASecret: (userId) => MFAStorage.getMFASecret(userId),
    useBackupCode: (userId, code) => MFAStorage.useBackupCode(userId, code),
    getBackupCodes: (userId) => MFAStorage.getBackupCodes(userId),
    regenerateBackupCodes: (userId) => MFAStorage.regenerateBackupCodes(userId),
    
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

// 기존 함수 매핑 (하위 호환성)
window.generateSecret = window.MFA.generateSecret;
window.verifyTOTP = window.MFA.verifyTOTP;
window.generateHOTP = window.MFA.generateHOTP;
window.enableMFA = window.MFA.enableMFA;
window.disableMFA = window.MFA.disableMFA;
window.isMFAEnabled = window.MFA.isMFAEnabled;
window.getMFASecret = window.MFA.getMFASecret;
window.useBackupCode = window.MFA.useBackupCode;
window.getBackupCodes = window.MFA.getBackupCodes;
window.regenerateBackupCodes = window.MFA.regenerateBackupCodes;

export { MFACore, MFAStorage, MFAUI };