const { Octokit } = require('@octokit/rest');

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
            blockedKeywords: settings.blockedKeywords || "",
            scrapingMethod: settings.scrapingMethod || "traditional",
            scrapingMethodOptions: settings.scrapingMethodOptions || {
                ai: {
                    provider: "gemini",
                    model: "gemini-1.5-flash",
                    fallbackToTraditional: true
                },
                traditional: {
                    useEnhancedFiltering: true
                }
            }
        };
        
        // 현재 파일의 SHA 가져오기
        let sha;
        try {
            const { data: fileData } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: 'data/settings.json',
            });
            sha = fileData.sha;
        } catch (error) {
            // 파일이 없으면 새로 생성
            console.log('settings.json not found, will create new file');
        }
        
        // GitHub에 파일 저장
        const content = Buffer.from(JSON.stringify(defaultSettings, null, 2)).toString('base64');
        
        const { data: result } = await octokit.rest.repos.createOrUpdateFileContents({
            owner,
            repo,
            path: 'data/settings.json',
            message: `Update settings via Web UI at ${new Date().toISOString()}`,
            content,
            sha, // 파일이 존재하면 SHA 필요
            committer: {
                name: 'Singapore News Bot',
                email: 'bot@singapore-news.com'
            }
        });

        return res.status(200).json({
            success: true,
            message: '설정이 GitHub에 저장되었습니다.',
            settings: defaultSettings,
            commit: result.commit.sha
        });

    } catch (error) {
        console.error('Settings save error:', error);
        return res.status(500).json({
            success: false,
            error: '설정 저장 중 오류가 발생했습니다.'
        });
    }
};