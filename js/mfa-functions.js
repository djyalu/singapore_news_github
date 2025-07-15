let currentMFASecret = null;

// generateHOTP 함수가 mfa.js에 정의되어 있으므로 
// window 객체를 통해 접근 가능하도록 함
const generateHOTP = window.generateHOTP || async function(secret, counter) {
    // Fallback implementation
    return '000000';
};

function setupMFA() {
    const secret = generateSecret();
    currentMFASecret = secret;
    
    const currentUser = getCurrentUser();
    generateQRCode(secret, currentUser.userId);
    
    // Secret을 보기 좋게 4자리씩 띄어서 표시
    const formattedSecret = secret.match(/.{1,4}/g).join(' ');
    document.getElementById('secretCode').textContent = formattedSecret;
    
    console.log('MFA Setup - Generated Secret:', secret);
    console.log('MFA Setup - Formatted Secret:', formattedSecret);
    
    document.getElementById('mfaSetupModal').style.display = 'block';
}

function nextMFAStep() {
    document.getElementById('mfaSetupStep1').style.display = 'none';
    document.getElementById('mfaSetupStep2').style.display = 'block';
}

async function completeMFASetup() {
    const code = document.getElementById('setupMfaCode').value.trim();
    
    console.log('MFA Setup - Secret:', currentMFASecret);
    console.log('MFA Setup - Entered Code:', code);
    
    try {
        // 현재 시간의 모든 코드 출력 (디버깅용)
        const timeStep = 30;
        const currentTime = Math.floor(Date.now() / 1000);
        const currentCounter = Math.floor(currentTime / timeStep);
        
        console.log('Debug - Current Time:', new Date().toISOString());
        console.log('Debug - Unix Time:', currentTime);
        console.log('Debug - Counter:', currentCounter);
        
        for (let i = -2; i <= 2; i++) {
            const testCode = await generateHOTP(currentMFASecret, currentCounter + i);
            console.log(`Debug - Window ${i}: ${testCode}`);
        }
        
        const isValid = await verifyTOTP(currentMFASecret, code);
        console.log('MFA Setup - Verification Result:', isValid);
        
        if (isValid) {
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
            // 현재 예상되는 코드 표시
            const expectedCode = await generateHOTP(currentMFASecret, currentCounter);
            alert(`잘못된 인증 코드입니다.\n\n입력한 코드: ${code}\n예상 코드: ${expectedCode}\n\nGoogle Authenticator에 다음 키를 수동으로 입력했는지 확인하세요:\n${currentMFASecret}`);
        }
    } catch (error) {
        console.error('MFA Setup Error:', error);
        alert('MFA 설정 중 오류가 발생했습니다: ' + error.message);
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