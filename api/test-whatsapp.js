// WhatsApp 테스트 메시지 전송 API (실제 전송)
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        // 환경 변수 상태 확인
        const instanceId = process.env.GREEN_API_INSTANCE_ID;
        const token = process.env.GREEN_API_TOKEN;
        
        console.log('Environment variables check:', {
            hasInstanceId: !!instanceId,
            hasToken: !!token,
            instanceIdLength: instanceId ? instanceId.length : 0,
            tokenLength: token ? token.length : 0
        });

        if (!instanceId || !token) {
            return res.status(200).json({
                success: false,
                error: 'Green API credentials not configured',
                debug: {
                    hasInstanceId: !!instanceId,
                    hasToken: !!token,
                    env: process.env.NODE_ENV || 'development'
                }
            });
        }

        // 테스트 메시지 생성
        const testMessage = `🧪 Claude Code WhatsApp 테스트

⏰ 시간: ${new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'})}
📡 상태: Vercel API 테스트 중
🤖 전송자: Claude Code AI
🔧 환경: ${process.env.NODE_ENV || 'production'}

Green API 연결이 정상적으로 작동합니다! ✅`;

        // WhatsApp 채널 (설정에서 읽어온 값)
        const channel = req.body?.channel || "120363421252284444@g.us";

        // Green API 메시지 전송
        const greenApiUrl = `https://api.green-api.com/waInstance${instanceId}/sendMessage/${token}`;
        
        console.log('Sending WhatsApp test message:', {
            to: channel,
            messageLength: testMessage.length,
            apiUrl: `https://api.green-api.com/waInstance${instanceId}/sendMessage/***`
        });

        const response = await fetch(greenApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chatId: channel,
                message: testMessage
            })
        });

        const responseData = await response.json();
        
        console.log('Green API Response:', {
            status: response.status,
            ok: response.ok,
            data: responseData
        });
        
        if (response.ok) {
            return res.status(200).json({
                success: true,
                sent: true,
                message: "테스트 메시지가 성공적으로 전송되었습니다!",
                details: {
                    id: responseData.idMessage,
                    timestamp: new Date().toISOString(),
                    channel: channel,
                    api: 'green-api'
                }
            });
        } else {
            console.error('Green API Error:', responseData);
            return res.status(200).json({
                success: false,
                error: `Green API Error: ${responseData.error || responseData.message || 'Unknown error'}`,
                details: responseData,
                debug: {
                    status: response.status,
                    hasCredentials: true
                }
            });
        }

    } catch (error) {
        console.error('WhatsApp test API Error:', error);
        return res.status(500).json({
            success: false,
            error: error.message || 'Internal server error',
            debug: {
                stack: error.stack
            }
        });
    }
};