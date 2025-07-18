module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        // 환경 변수 확인
        const smtpUser = process.env.SMTP_USER;
        const smtpPassword = process.env.SMTP_PASSWORD;
        
        return res.status(200).json({
            success: true,
            smtp_configured: !!(smtpUser && smtpPassword),
            smtp_user: smtpUser ? `${smtpUser.substring(0, 3)}...@${smtpUser.split('@')[1]}` : 'Not set',
            nodemailer_available: false // 일단 false로 설정
        });
    } catch (error) {
        return res.status(500).json({
            success: false,
            error: error.message
        });
    }
};