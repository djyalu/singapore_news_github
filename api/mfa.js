const fs = require('fs');
const path = require('path');
const speakeasy = require('speakeasy');

// MFA API - 서버 기반 MFA 관리
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Max-Age', '86400');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
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

        const { action, userId } = req.query;
        const userIndex = usersData.users.findIndex(u => u.id === userId);
        
        if (userIndex === -1) {
            return res.status(404).json({
                success: false,
                error: '사용자를 찾을 수 없습니다.'
            });
        }

        // GET: MFA 상태 조회
        if (req.method === 'GET') {
            if (action === 'status') {
                const user = usersData.users[userIndex];
                // MFA 속성이 없으면 비활성화로 처리
                const mfaEnabled = user.mfa ? user.mfa.enabled : false;
                const hasBackupCodes = user.mfa ? user.mfa.backupCodes.length > 0 : false;
                
                return res.status(200).json({
                    success: true,
                    enabled: mfaEnabled,
                    hasBackupCodes: hasBackupCodes
                });
            }
            
            if (action === 'generate-secret') {
                const secret = speakeasy.generateSecret({
                    name: `Singapore News (${userId})`,
                    issuer: 'Singapore News Scraper',
                    length: 32
                });
                
                return res.status(200).json({
                    success: true,
                    secret: secret.base32,
                    qrCodeUrl: secret.otpauth_url
                });
            }
        }

        // POST: MFA 활성화/비활성화
        if (req.method === 'POST') {
            if (action === 'enable') {
                const { secret, token } = req.body;
                
                if (!secret || !token) {
                    return res.status(400).json({
                        success: false,
                        error: 'Secret과 토큰이 필요합니다.'
                    });
                }
                
                // 토큰 검증
                const verified = speakeasy.totp.verify({
                    secret: secret,
                    encoding: 'base32',
                    token: token,
                    window: 2
                });
                
                if (!verified) {
                    return res.status(400).json({
                        success: false,
                        error: '유효하지 않은 토큰입니다.'
                    });
                }
                
                // 백업 코드 생성
                const backupCodes = [];
                for (let i = 0; i < 10; i++) {
                    let code = '';
                    for (let j = 0; j < 8; j++) {
                        code += Math.floor(Math.random() * 10);
                    }
                    backupCodes.push(code);
                }
                
                // MFA 활성화
                usersData.users[userIndex].mfa = {
                    enabled: true,
                    secret: secret,
                    backupCodes: backupCodes,
                    enabledAt: new Date().toISOString()
                };
                
                // 파일 저장
                fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2));
                
                return res.status(200).json({
                    success: true,
                    backupCodes: backupCodes
                });
            }
            
            if (action === 'disable') {
                usersData.users[userIndex].mfa = {
                    enabled: false,
                    secret: null,
                    backupCodes: [],
                    disabledAt: new Date().toISOString()
                };
                
                // 파일 저장
                fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2));
                
                return res.status(200).json({
                    success: true
                });
            }
            
            if (action === 'verify') {
                const { token } = req.body;
                const user = usersData.users[userIndex];
                
                if (!user.mfa || !user.mfa.enabled) {
                    return res.status(400).json({
                        success: false,
                        error: 'MFA가 활성화되지 않았습니다.'
                    });
                }
                
                // TOTP 토큰 검증
                const verified = speakeasy.totp.verify({
                    secret: user.mfa.secret,
                    encoding: 'base32',
                    token: token,
                    window: 2
                });
                
                if (verified) {
                    return res.status(200).json({
                        success: true
                    });
                }
                
                // 백업 코드 검증
                const codeIndex = user.mfa.backupCodes.indexOf(token);
                if (codeIndex !== -1) {
                    // 백업 코드 사용 후 제거
                    user.mfa.backupCodes.splice(codeIndex, 1);
                    user.mfa.lastBackupCodeUsed = new Date().toISOString();
                    
                    // 파일 저장
                    fs.writeFileSync(usersFilePath, JSON.stringify(usersData, null, 2));
                    
                    return res.status(200).json({
                        success: true,
                        usedBackupCode: true,
                        remainingCodes: user.mfa.backupCodes.length
                    });
                }
                
                return res.status(400).json({
                    success: false,
                    error: '유효하지 않은 토큰입니다.'
                });
            }
        }

        return res.status(405).json({ error: 'Method not allowed' });

    } catch (error) {
        console.error('MFA API error:', error);
        return res.status(500).json({
            success: false,
            error: 'MFA 처리 중 오류가 발생했습니다.'
        });
    }
};