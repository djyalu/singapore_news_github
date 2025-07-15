// Node.js/Express 버전 (선택적)
const express = require('express');
const fetch = require('node-fetch');
const router = express.Router();

const WHAPI_URL = 'https://gate.whapi.cloud/messages/text';
const WHAPI_TOKEN = 'ZCF4emVil1iJLNRJ6Sb7ce7TsyctIEYq';

router.post('/api/send-whatsapp', async (req, res) => {
    const { channel, message } = req.body;
    
    if (!channel || !message) {
        return res.json({ success: false, error: '필수 파라미터가 누락되었습니다.' });
    }
    
    try {
        const response = await fetch(WHAPI_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${WHAPI_TOKEN}`
            },
            body: JSON.stringify({
                to: channel,
                body: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.message_id) {
            res.json({ success: true, message_id: data.message_id });
        } else {
            res.json({ success: false, error: data.error || '알 수 없는 오류' });
        }
    } catch (error) {
        console.error('WhatsApp API Error:', error);
        res.json({ success: false, error: '네트워크 오류' });
    }
});

module.exports = router;