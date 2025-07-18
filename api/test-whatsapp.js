// WhatsApp 테스트 전송 API - 실제 WhatsApp API를 통한 테스트 메시지 전송
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { channel, message } = req.body;

        if (!channel || !message) {
            return res.status(400).json({
                success: false,
                error: 'Channel and message are required'
            });
        }

        // WhatsApp API key 확인
        const apiKey = process.env.WHATSAPP_API_KEY;
        if (!apiKey) {
            return res.status(500).json({
                success: false,
                error: 'WhatsApp API key not configured'
            });
        }

        // 테스트 메시지 포맷팅
        const testMessage = `🧪 *테스트 메시지*\n${new Date().toLocaleString('ko-KR')}\n━━━━━━━━━━━━━━━━━━━━\n\n${message}\n\n━━━━━━━━━━━━━━━━━━━━\n🤖 _Singapore News Scraper Test_`;

        // Whapi.cloud API 호출
        const whapiUrl = 'https://gate.whapi.cloud/messages/text';
        
        console.log('Sending WhatsApp test message:', {
            to: channel,
            messageLength: testMessage.length
        });

        const response = await fetch(whapiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                to: channel,
                body: testMessage
            })
        });

        const responseData = await response.json();
        
        console.log('WhatsApp API Response:', {
            status: response.status,
            ok: response.ok,
            data: responseData
        });
        
        if (response.ok) {
            return res.status(200).json({
                success: true,
                sent: true,
                id: responseData.id || responseData.message_id,
                message: responseData,
                timestamp: new Date().toISOString()
            });
        } else {
            console.error('Whapi.cloud API Error:', responseData);
            return res.status(response.status).json({
                success: false,
                error: responseData.error || responseData.message || 'WhatsApp API error',
                details: responseData
            });
        }

    } catch (error) {
        console.error('WhatsApp Test API Error:', error);
        return res.status(500).json({
            success: false,
            error: error.message || 'Internal server error'
        });
    }
};