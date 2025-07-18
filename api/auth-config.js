const fs = require('fs');
const path = require('path');

// 인증 설정 API - JSON 파일에서 사용자 정보 가져오기
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // users.json 파일 읽기
        const usersFilePath = path.join(process.cwd(), 'data', 'users.json');
        let usersData;
        
        try {
            const fileContent = fs.readFileSync(usersFilePath, 'utf8');
            usersData = JSON.parse(fileContent);
        } catch (error) {
            console.error('Error reading users.json:', error);
            return res.status(500).json({
                success: false,
                error: '사용자 데이터를 읽을 수 없습니다.'
            });
        }
        
        // 비밀번호는 전송하지 않고, 사용자 정보만 반환
        const authConfig = {
            users: usersData.users.map(user => ({
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role,
                configured: true
            }))
        };

        return res.status(200).json({
            success: true,
            config: authConfig
        });
    } catch (error) {
        console.error('Auth config error:', error);
        return res.status(500).json({
            success: false,
            error: '인증 설정을 가져오는 중 오류가 발생했습니다.'
        });
    }
};