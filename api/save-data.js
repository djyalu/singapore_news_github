const { Octokit } = require('@octokit/rest');

// 통합 데이터 API - 설정/사이트 저장 및 조회
module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    // GET 요청: 데이터 조회
    if (req.method === 'GET') {
        try {
            const { type } = req.query;
            
            if (!type || !['settings', 'sites'].includes(type)) {
                return res.status(400).json({ 
                    success: false, 
                    error: '타입을 지정해주세요. (?type=settings 또는 ?type=sites)' 
                });
            }

            // GitHub Personal Access Token 확인
            const githubToken = process.env.GITHUB_TOKEN;
            if (!githubToken) {
                return res.status(500).json({ 
                    success: false, 
                    error: 'GitHub token not configured.' 
                });
            }

            // GitHub 저장소 정보
            const owner = process.env.GITHUB_OWNER || 'djyalu';
            const repo = process.env.GITHUB_REPO || 'singapore_news_github';
            
            // Octokit 인스턴스 생성
            const octokit = new Octokit({
                auth: githubToken,
            });

            const filePath = type === 'settings' ? 'data/settings.json' : 'data/sites.json';
            
            // 파일 읽기
            const { data: fileData } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: filePath,
            });
            
            const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
            const jsonData = JSON.parse(content);
            
            return res.status(200).json({
                success: true,
                type: type,
                data: jsonData
            });

        } catch (error) {
            console.error('Data fetch error:', error);
            return res.status(500).json({
                success: false,
                error: `${type} 데이터를 가져올 수 없습니다.`,
                details: error.message
            });
        }
    }

    // POST 요청만 허용 (기존 저장 로직)
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { type, data } = req.body;
        
        // 타입 검증
        if (!type || !['settings', 'sites'].includes(type)) {
            return res.status(400).json({ 
                success: false, 
                error: '잘못된 데이터 타입입니다. (settings 또는 sites)' 
            });
        }

        // 데이터 검증
        if (!data) {
            return res.status(400).json({ 
                success: false, 
                error: '저장할 데이터가 없습니다.' 
            });
        }

        // GitHub Personal Access Token 확인
        const githubToken = process.env.GITHUB_TOKEN;
        if (!githubToken) {
            return res.status(500).json({ 
                success: false, 
                error: 'GitHub token not configured.' 
            });
        }

        // GitHub 저장소 정보
        const owner = process.env.GITHUB_OWNER || 'djyalu';
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';
        
        // Octokit 인스턴스 생성
        const octokit = new Octokit({
            auth: githubToken,
        });

        let filePath, commitMessage, processedData;

        if (type === 'settings') {
            // 설정 데이터 처리
            if (typeof data !== 'object') {
                return res.status(400).json({ 
                    success: false, 
                    error: '잘못된 설정 데이터입니다.' 
                });
            }

            // 필수 필드 검증
            if (data.sendChannel === 'whatsapp' && !data.whatsappChannel) {
                return res.status(400).json({ 
                    success: false, 
                    error: 'WhatsApp 채널을 선택해주세요.' 
                });
            }

            // 기본 설정 구조 확인
            processedData = {
                scrapTarget: data.scrapTarget || "recent",
                importantKeywords: data.importantKeywords || "",
                summaryOptions: data.summaryOptions || {
                    headline: true,
                    keywords: true,
                    content: true
                },
                sendChannel: data.sendChannel || "whatsapp",
                whatsappChannel: data.whatsappChannel || "",
                sendSchedule: data.sendSchedule || {
                    period: "daily",
                    time: "08:00",
                    weekdays: [],
                    date: "1"
                },
                blockedKeywords: data.blockedKeywords || "",
                scrapingMethod: data.scrapingMethod || "traditional",
                scrapingMethodOptions: data.scrapingMethodOptions || {
                    ai: {
                        provider: "gemini",
                        model: "gemini-1.5-flash",
                        fallbackToTraditional: true
                    },
                    traditional: {
                        useEnhancedFiltering: true
                    }
                },
                monitoring: data.monitoring || {}
            };

            filePath = 'data/settings.json';
            commitMessage = `Update settings via Web UI at ${new Date().toISOString()}`;

        } else if (type === 'sites') {
            // 사이트 목록 처리
            if (!Array.isArray(data)) {
                return res.status(400).json({ 
                    success: false, 
                    error: '잘못된 사이트 데이터입니다.' 
                });
            }

            processedData = data;
            filePath = 'data/sites.json';
            commitMessage = `Update sites list via Web UI at ${new Date().toISOString()}`;
        }
        
        // 현재 파일의 SHA 가져오기
        let sha;
        try {
            const { data: fileData } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: filePath,
            });
            sha = fileData.sha;
        } catch (error) {
            // 파일이 없으면 새로 생성
            console.log(`${filePath} not found, will create new file`);
        }
        
        // GitHub에 파일 저장
        const content = Buffer.from(JSON.stringify(processedData, null, 2)).toString('base64');
        
        const { data: result } = await octokit.rest.repos.createOrUpdateFileContents({
            owner,
            repo,
            path: filePath,
            message: commitMessage,
            content,
            sha, // 파일이 존재하면 SHA 필요
            committer: {
                name: 'Singapore News Bot',
                email: 'bot@singapore-news.com'
            }
        });

        return res.status(200).json({
            success: true,
            message: `${type === 'settings' ? '설정' : '사이트 목록'}이 GitHub에 저장되었습니다.`,
            data: processedData,
            commit: result.commit.sha
        });

    } catch (error) {
        console.error('Data save error:', error);
        
        let errorMessage = '데이터 저장 중 오류가 발생했습니다.';
        if (error.status === 404) {
            errorMessage = 'GitHub 저장소를 찾을 수 없습니다.';
        } else if (error.status === 401) {
            errorMessage = 'GitHub 인증에 실패했습니다.';
        }
        
        return res.status(500).json({
            success: false,
            error: errorMessage,
            details: error.message
        });
    }
};