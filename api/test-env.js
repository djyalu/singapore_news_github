module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Content-Type', 'application/json');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // GET 요청만 허용
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // 환경 변수 체크 (민감한 정보는 제외)
        const envStatus = {
            success: true,
            timestamp: new Date().toISOString(),
            environment: {
                // GitHub 설정
                github_token: !!process.env.GITHUB_TOKEN,
                github_owner: !!process.env.GITHUB_OWNER,
                github_repo: !!process.env.GITHUB_REPO,
                
                // WhatsApp 설정
                whatsapp_api_key: !!process.env.WHATSAPP_API_KEY,
                
                // 시스템 정보
                node_env: process.env.NODE_ENV || 'development',
                vercel_region: process.env.VERCEL_REGION || 'unknown',
                
                // 버전 정보
                node_version: process.version,
                platform: process.platform
            },
            status: 'Environment variables check completed'
        };

        // 필수 환경 변수 확인
        const required = ['GITHUB_TOKEN', 'GITHUB_OWNER', 'GITHUB_REPO'];
        const missing = required.filter(key => !process.env[key]);
        
        if (missing.length > 0) {
            envStatus.success = false;
            envStatus.error = `Missing required environment variables: ${missing.join(', ')}`;
            envStatus.missing_vars = missing;
        }

        return res.status(200).json(envStatus);

    } catch (error) {
        console.error('Environment test error:', error);
        
        return res.status(500).json({
            success: false,
            error: 'Environment test failed',
            details: error.message,
            timestamp: new Date().toISOString()
        });
    }
};