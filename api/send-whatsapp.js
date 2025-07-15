module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    // POST 요청만 허용
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { channel, message } = req.body;

        if (!channel || !message) {
            return res.status(400).json({ 
                success: false, 
                error: '채널과 메시지는 필수입니다.' 
            });
        }

        // WhatsApp API 설정
        const whatsappApiUrl = 'https://gate.whapi.cloud/messages/text';
        const whatsappToken = process.env.WHATSAPP_API_KEY || 'ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq';

        // 채널 ID 형식 변환 (그룹 채널은 @g.us 유지)
        let toNumber = channel;
        // 그룹 채널(@g.us)은 그대로 유지, 개인 채널만 숫자로 변환

        const whatsappData = {
            to: toNumber,
            body: message,
            typing_time: 0
        };

        // WhatsApp API 호출
        const response = await fetch(whatsappApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${whatsappToken}`
            },
            body: JSON.stringify(whatsappData)
        });

        const data = await response.json();

        if (response.ok && (data.sent === true || data.id || data.message_id || (data.message && data.message.id))) {
            return res.status(200).json({
                success: true,
                messageId: data.message?.id || data.id || data.message_id || 'unknown',
                timestamp: new Date().toISOString(),
                rawResponse: data
            });
        } else {
            return res.status(400).json({
                success: false,
                error: data.message || data.error || '메시지 전송에 실패했습니다.'
            });
        }
    } catch (error) {
        console.error('WhatsApp API Error:', error);
        return res.status(500).json({
            success: false,
            error: '서버 오류가 발생했습니다.'
        });
    }
};