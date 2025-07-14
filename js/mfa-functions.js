let currentMFASecret = null;

function setupMFA() {
    const secret = generateSecret();
    currentMFASecret = secret;
    
    const currentUser = getCurrentUser();
    generateQRCode(secret, currentUser.userId);
    document.getElementById('secretCode').textContent = secret;
    document.getElementById('mfaSetupModal').style.display = 'block';
}

function nextMFAStep() {
    document.getElementById('mfaSetupStep1').style.display = 'none';
    document.getElementById('mfaSetupStep2').style.display = 'block';
}

function completeMFASetup() {
    const code = document.getElementById('setupMfaCode').value;
    
    if (verifyTOTP(currentMFASecret, code)) {
        const currentUser = getCurrentUser();
        const result = enableMFA(currentUser.userId, currentMFASecret);
        
        if (result.success) {
            displayBackupCodes(result.backupCodes);
            document.getElementById('mfaSetupStep2').style.display = 'none';
            document.getElementById('mfaSetupStep3').style.display = 'block';
        } else {
            alert('MFA 설정에 실패했습니다: ' + result.message);
        }
    } else {
        alert('잘못된 인증 코드입니다. 다시 시도하세요.');
    }
}

function displayBackupCodes(codes) {
    const container = document.getElementById('backupCodesList');
    container.innerHTML = codes.map(code => `<div class="backup-code">${code}</div>`).join('');
}

function finishMFASetup() {
    document.getElementById('mfaSetupModal').style.display = 'none';
    location.reload();
}

function closeMFAModal() {
    document.getElementById('mfaSetupModal').style.display = 'none';
    currentMFASecret = null;
}

function disableMFAConfirm() {
    if (confirm('MFA를 비활성화하시겠습니까? 보안이 약해질 수 있습니다.')) {
        const currentUser = getCurrentUser();
        const result = disableMFA(currentUser.userId);
        
        if (result.success) {
            alert('MFA가 비활성화되었습니다.');
            location.reload();
        } else {
            alert('MFA 비활성화에 실패했습니다: ' + result.message);
        }
    }
}

function showBackupCodes() {
    const currentUser = getCurrentUser();
    const codes = getBackupCodes(currentUser.userId);
    
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
}

function closeBackupCodesModal() {
    document.getElementById('backupCodesModal').style.display = 'none';
}

function regenerateBackupCodes() {
    if (confirm('새로운 백업 코드를 생성하시겠습니까? 기존 코드는 사용할 수 없게 됩니다.')) {
        const currentUser = getCurrentUser();
        const result = regenerateBackupCodes(currentUser.userId);
        
        if (result.success) {
            alert('새로운 백업 코드가 생성되었습니다.');
            showBackupCodes();
        } else {
            alert('백업 코드 재생성에 실패했습니다: ' + result.message);
        }
    }
}