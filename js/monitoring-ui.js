// 모니터링 설정 UI 생성 함수
function createMonitoringSettingsUI() {
    return `
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
            🔔 모니터링 및 알림 설정
        </h3>
        
        <!-- 모니터링 활성화 -->
        <div class="mb-6">
            <label class="flex items-center">
                <input type="checkbox" id="monitoringEnabled" class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <span class="text-sm font-medium text-gray-700">모니터링 활성화</span>
            </label>
            <p class="text-xs text-gray-500 mt-1 ml-6">스크래핑 결과를 모니터링하고 알림을 받습니다.</p>
        </div>
        
        <!-- 이메일 알림 설정 -->
        <div id="emailSettingsSection" class="space-y-4 ml-6" style="display: none;">
            <div class="border-l-4 border-blue-500 pl-4">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">이메일 알림</h4>
                
                <!-- 이메일 활성화 -->
                <div class="mb-4">
                    <label class="flex items-center">
                        <input type="checkbox" id="emailEnabled" class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                        <span class="text-sm text-gray-700">이메일 알림 사용</span>
                    </label>
                </div>
                
                <!-- 수신자 이메일 -->
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        수신자 이메일 (쉼표로 구분)
                    </label>
                    <input type="text" id="emailRecipients" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                           placeholder="admin@example.com, manager@example.com">
                </div>
                
                <!-- 알림 조건 -->
                <div class="mb-4">
                    <p class="text-sm font-medium text-gray-700 mb-2">알림 발송 조건:</p>
                    <div class="space-y-2 ml-4">
                        <label class="flex items-center">
                            <input type="checkbox" id="sendOnSuccess" class="mr-2 rounded border-gray-300 text-blue-600">
                            <span class="text-sm text-gray-600">스크래핑 성공 시</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" id="sendOnFailure" checked class="mr-2 rounded border-gray-300 text-blue-600">
                            <span class="text-sm text-gray-600">스크래핑 실패 시</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" id="sendOnNoArticles" checked class="mr-2 rounded border-gray-300 text-blue-600">
                            <span class="text-sm text-gray-600">수집된 기사가 없을 때</span>
                        </label>
                    </div>
                </div>
                
                <!-- SMTP 설정 (고급) -->
                <details class="mb-4">
                    <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                        고급 설정 (SMTP)
                    </summary>
                    <div class="mt-3 space-y-3 p-3 bg-gray-50 rounded">
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">SMTP 서버</label>
                            <input type="text" id="smtpHost" value="smtp.gmail.com"
                                   class="w-full px-2 py-1 text-sm border border-gray-300 rounded">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">포트</label>
                            <input type="number" id="smtpPort" value="587"
                                   class="w-full px-2 py-1 text-sm border border-gray-300 rounded">
                        </div>
                        <div>
                            <label class="flex items-center">
                                <input type="checkbox" id="smtpSecure" class="mr-2 rounded border-gray-300">
                                <span class="text-xs text-gray-700">보안 연결 (SSL/TLS)</span>
                            </label>
                        </div>
                    </div>
                </details>
                
                <!-- 이메일 테스트 -->
                <button onclick="testEmailNotification()" 
                        class="bg-blue-100 text-blue-700 px-4 py-2 rounded text-sm hover:bg-blue-200 transition-colors">
                    📧 테스트 이메일 발송
                </button>
            </div>
        </div>
        
        <!-- 정기 리포트 -->
        <div id="reportSettingsSection" class="mt-6 ml-6" style="display: none;">
            <div class="border-l-4 border-green-500 pl-4">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">정기 리포트</h4>
                <div class="space-y-2">
                    <label class="flex items-center">
                        <input type="checkbox" id="dailyReport" class="mr-2 rounded border-gray-300 text-green-600">
                        <span class="text-sm text-gray-600">일일 요약 리포트 (매일 오후 11시)</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" id="weeklyReport" class="mr-2 rounded border-gray-300 text-green-600">
                        <span class="text-sm text-gray-600">주간 요약 리포트 (매주 일요일)</span>
                    </label>
                </div>
            </div>
        </div>
    </div>
    `;
}

// 모니터링 설정 로드
function loadMonitoringSettings(settings) {
    if (!settings.monitoring) return;
    
    const monitoring = settings.monitoring;
    
    // 모니터링 활성화
    const monitoringEnabled = document.getElementById('monitoringEnabled');
    if (monitoringEnabled) {
        monitoringEnabled.checked = monitoring.enabled || false;
        toggleMonitoringSettings();
    }
    
    // 이메일 설정
    if (monitoring.email) {
        document.getElementById('emailEnabled').checked = monitoring.email.enabled || false;
        document.getElementById('emailRecipients').value = (monitoring.email.recipients || []).join(', ');
        
        if (monitoring.email.sendOn) {
            document.getElementById('sendOnSuccess').checked = monitoring.email.sendOn.success || false;
            document.getElementById('sendOnFailure').checked = monitoring.email.sendOn.failure !== false;
            document.getElementById('sendOnNoArticles').checked = monitoring.email.sendOn.noArticles !== false;
        }
        
        if (monitoring.email.smtp) {
            document.getElementById('smtpHost').value = monitoring.email.smtp.host || 'smtp.gmail.com';
            document.getElementById('smtpPort').value = monitoring.email.smtp.port || 587;
            document.getElementById('smtpSecure').checked = monitoring.email.smtp.secure || false;
        }
    }
    
    // 정기 리포트
    if (monitoring.summary) {
        document.getElementById('dailyReport').checked = monitoring.summary.dailyReport || false;
        document.getElementById('weeklyReport').checked = monitoring.summary.weeklyReport || false;
    }
}

// 모니터링 토글
function toggleMonitoringSettings() {
    const enabled = document.getElementById('monitoringEnabled').checked;
    document.getElementById('emailSettingsSection').style.display = enabled ? 'block' : 'none';
    document.getElementById('reportSettingsSection').style.display = enabled ? 'block' : 'none';
}

// 테스트 이메일 발송
async function testEmailNotification() {
    const recipients = document.getElementById('emailRecipients').value
        .split(',')
        .map(e => e.trim())
        .filter(e => e);
    
    if (!recipients.length) {
        showNotification('수신자 이메일을 입력해주세요.', 'error');
        return;
    }
    
    const testButton = event.target;
    testButton.disabled = true;
    testButton.textContent = '📧 발송 중...';
    
    try {
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const apiUrl = isProduction ? '/api/send-email' : 'https://singapore-news-github.vercel.app/api/send-email';
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipients: recipients,
                subject: '🔔 Singapore News Scraper 테스트 이메일',
                body: `
                    <h3>테스트 이메일입니다</h3>
                    <p>이메일 알림이 정상적으로 설정되었습니다.</p>
                    <p>발송 시간: ${new Date().toLocaleString('ko-KR')}</p>
                `,
                isTest: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('테스트 이메일이 발송되었습니다!', 'success');
        } else {
            throw new Error(result.error || '이메일 발송 실패');
        }
    } catch (error) {
        showNotification(`이메일 발송 실패: ${error.message}`, 'error');
    } finally {
        testButton.disabled = false;
        testButton.textContent = '📧 테스트 이메일 발송';
    }
}