const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');

// 통합 인증 API - 설정 조회 및 로그인 처리
module.exports = async (req, res) => {
    // 강화된 CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Max-Age', '86400');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    try {
        // users.json 파일 읽기 (공통 로직)
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

        // GET 요청: 인증 설정 조회
        if (req.method === 'GET') {
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
        }

        // POST 요청: 로그인 처리
        if (req.method === 'POST') {
            const { username, password, mfaToken } = req.body;

            if (!username || !password) {
                return res.status(400).json({
                    success: false,
                    error: '사용자명과 비밀번호를 입력해주세요.'
                });
            }

            // 사용자 찾기
            const user = usersData.users.find(u => u.id === username);
            
            console.log('Login attempt:', { username, userFound: !!user });
            if (user) {
                console.log('User data:', { id: user.id, hasPassword: !!user.password, passwordType: user.password?.startsWith('$2') ? 'hashed' : 'plain', mfaEnabled: user.mfa?.enabled });
            }
            
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
                console.log('Plain text comparison:', { provided: password, stored: user.password, match: password === user.password });
                isValidPassword = (password === user.password);
            }

            if (!isValidPassword) {
                return res.status(401).json({
                    success: false,
                    error: '비밀번호가 일치하지 않습니다.'
                });
            }

            // MFA 검증 (MFA가 활성화된 경우)
            if (user.mfa && user.mfa.enabled === true) {
                if (!mfaToken) {
                    return res.status(200).json({
                        success: false,
                        requireMFA: true,
                        message: 'MFA 토큰이 필요합니다.'
                    });
                }

                // MFA 토큰 검증
                const speakeasy = require('speakeasy');
                const verified = speakeasy.totp.verify({
                    secret: user.mfa.secret,
                    encoding: 'base32',
                    token: mfaToken,
                    window: 2
                });

                // TOTP 실패시 백업 코드 확인
                if (!verified) {
                    const codeIndex = user.mfa.backupCodes.indexOf(mfaToken);
                    if (codeIndex !== -1) {
                        // 백업 코드 사용 후 제거
                        user.mfa.backupCodes.splice(codeIndex, 1);
                        user.mfa.lastBackupCodeUsed = new Date().toISOString();
                        
                        // 파일 저장
                        const fs = require('fs');
                        fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2));
                        
                        console.log('Login with backup code successful');
                    } else {
                        return res.status(401).json({
                            success: false,
                            error: '유효하지 않은 MFA 토큰입니다.'
                        });
                    }
                }
            }

            // 로그인 성공 - 비밀번호는 제외하고 사용자 정보 반환
            const { password: _, ...userInfo } = user;
            return res.status(200).json({
                success: true,
                user: userInfo
            });
        }

        // 지원하지 않는 메소드
        return res.status(405).json({ error: 'Method not allowed' });

    } catch (error) {
        console.error('Auth API error:', error);
        return res.status(500).json({
            success: false,
            error: '인증 처리 중 오류가 발생했습니다.'
        });
    }
};