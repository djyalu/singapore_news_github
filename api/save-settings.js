const fs = require('fs');
const path = require('path');

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
        const settings = req.body;
        
        // 설정 검증
        if (!settings || typeof settings !== 'object') {
            return res.status(400).json({ 
                success: false, 
                error: '잘못된 설정 데이터입니다.' 
            });
        }

        // 필수 필드 검증
        if (settings.sendChannel === 'whatsapp' && !settings.whatsappChannel) {
            return res.status(400).json({ 
                success: false, 
                error: 'WhatsApp 채널을 선택해주세요.' 
            });
        }

        // 설정 파일 경로
        const settingsPath = path.join(process.cwd(), 'data', 'settings.json');
        
        // 기본 설정 구조 확인
        const defaultSettings = {
            scrapTarget: settings.scrapTarget || "recent",
            importantKeywords: settings.importantKeywords || "",
            summaryOptions: settings.summaryOptions || {
                headline: true,
                keywords: true,
                content: true
            },
            sendChannel: settings.sendChannel || "whatsapp",
            whatsappChannel: settings.whatsappChannel || "",
            sendSchedule: settings.sendSchedule || {
                period: "daily",
                time: "08:00",
                weekdays: [],
                date: "1"
            },
            blockedKeywords: settings.blockedKeywords || ""
        };

        // 설정 파일에 저장
        fs.writeFileSync(settingsPath, JSON.stringify(defaultSettings, null, 2), 'utf8');

        return res.status(200).json({
            success: true,
            message: '설정이 저장되었습니다.',
            settings: defaultSettings
        });

    } catch (error) {
        console.error('Settings save error:', error);
        return res.status(500).json({
            success: false,
            error: '설정 저장 중 오류가 발생했습니다.'
        });
    }
};