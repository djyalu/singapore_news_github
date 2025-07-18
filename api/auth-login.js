const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');

// 로그인 API - JSON 파일의 사용자 정보와 대조
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
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({
                success: false,
                error: '사용자명과 비밀번호를 입력해주세요.'
            });
        }

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

        // 사용자 찾기
        const user = usersData.users.find(u => u.id === username);
        
        if (!user) {
            return res.status(401).json({
                success: false,
                error: '사용자를 찾을 수 없습니다.'
            });
        }

        // 비밀번호 검증
        let isValidPassword = false;
        
        // bcrypt 해시인지 확인
        if (user.password.startsWith('$2b$') || user.password.startsWith('$2a$')) {
            // bcrypt로 해시된 비밀번호
            isValidPassword = await bcrypt.compare(password, user.password);
        } else {
            // 임시: 평문 비밀번호 (마이그레이션 전)
            console.warn(`Warning: User ${username} has unhashed password. Please update to bcrypt hash.`);
            isValidPassword = (password === user.password);
        }

        if (isValidPassword) {
            // 비밀번호는 제외하고 사용자 정보 반환
            const { password: _, ...userInfo } = user;
            return res.status(200).json({
                success: true,
                user: userInfo
            });
        } else {
            return res.status(401).json({
                success: false,
                error: '비밀번호가 일치하지 않습니다.'
            });
        }
    } catch (error) {
        console.error('Login error:', error);
        return res.status(500).json({
            success: false,
            error: '로그인 처리 중 오류가 발생했습니다.'
        });
    }
};