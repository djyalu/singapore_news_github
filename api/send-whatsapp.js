// Direct WhatsApp sending API using Green API
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
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

        // Green API 설정 확인
        const instanceId = process.env.GREEN_API_INSTANCE_ID;
        const token = process.env.GREEN_API_TOKEN;

        if (!instanceId || !token) {
            return res.status(500).json({
                success: false,
                error: 'Green API credentials not configured'
            });
        }

        // Green API 메시지 전송
        const greenApiUrl = `https://api.green-api.com/waInstance${instanceId}/sendMessage/${token}`;
        
        console.log('Sending WhatsApp message via Green API:', {
            to: channel,
            messageLength: message.length
        });

        const response = await fetch(greenApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chatId: channel,
                message: message
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
                id: responseData.idMessage,
                message: responseData,
                timestamp: new Date().toISOString(),
                api: 'green-api'
            });
        } else {
            console.error('Green API Error:', responseData);
            return res.status(response.status).json({
                success: false,
                error: responseData.error || responseData.message || 'Green API error',
                details: responseData
            });
        }

    } catch (error) {
        console.error('WhatsApp send API Error:', error);
        return res.status(500).json({
            success: false,
            error: error.message || 'Internal server error'
        });
    }
};