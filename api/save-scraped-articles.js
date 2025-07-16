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
        const { articles } = req.body;
        
        // 기사 데이터 검증
        if (!articles || !Array.isArray(articles)) {
            return res.status(400).json({ 
                success: false, 
                error: '잘못된 기사 데이터입니다.' 
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
        
        // 파일명 생성 (현재 시간 기준)
        const now = new Date();
        const timestamp = now.toISOString().replace(/[-:]/g, '').replace('T', '_').split('.')[0];
        const filename = `news_${timestamp}.json`;
        const filepath = `data/scraped/${filename}`;
        
        // 저장할 데이터 구조
        const dataToSave = {
            timestamp: now.toISOString(),
            count: articles.length,
            articles: articles
        };
        
        // GitHub에 파일 저장
        const content = Buffer.from(JSON.stringify(dataToSave, null, 2)).toString('base64');
        
        const { data: result } = await octokit.rest.repos.createOrUpdateFileContents({
            owner,
            repo,
            path: filepath,
            message: `Save scraped articles via Web UI at ${now.toISOString()}`,
            content,
            committer: {
                name: 'Singapore News Bot',
                email: 'bot@singapore-news.com'
            }
        });

        return res.status(200).json({
            success: true,
            message: '기사가 GitHub에 저장되었습니다.',
            filename: filename,
            count: articles.length,
            commit: result.commit.sha
        });

    } catch (error) {
        console.error('Articles save error:', error);
        
        let errorMessage = '기사 저장 중 오류가 발생했습니다.';
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