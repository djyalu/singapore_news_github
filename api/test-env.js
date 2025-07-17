module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        const envStatus = {
            GITHUB_TOKEN: !!process.env.GITHUB_TOKEN ? 'SET' : 'NOT_SET',
            GITHUB_OWNER: process.env.GITHUB_OWNER || 'NOT_SET',
            GITHUB_REPO: process.env.GITHUB_REPO || 'NOT_SET',
            WHATSAPP_API_KEY: !!process.env.WHATSAPP_API_KEY ? 'SET' : 'NOT_SET',
            GOOGLE_GEMINI_API_KEY: !!process.env.GOOGLE_GEMINI_API_KEY ? 'SET' : 'NOT_SET',
            timestamp: new Date().toISOString()
        };

        return res.status(200).json({
            success: true,
            environment: envStatus,
            message: 'Environment variables check'
        });

    } catch (error) {
        console.error('Environment check error:', error);
        return res.status(500).json({
            success: false,
            error: error.message
        });
    }
};