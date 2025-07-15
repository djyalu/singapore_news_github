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
        const sites = req.body;
        
        // 사이트 목록 검증
        if (!sites || !Array.isArray(sites)) {
            return res.status(400).json({ 
                success: false, 
                error: '잘못된 사이트 데이터입니다.' 
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
        
        // 현재 파일의 SHA 가져오기
        let sha;
        try {
            const { data: fileData } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: 'data/sites.json',
            });
            sha = fileData.sha;
        } catch (error) {
            // 파일이 없으면 새로 생성
            console.log('sites.json not found, will create new file');
        }
        
        // GitHub에 파일 저장
        const content = Buffer.from(JSON.stringify(sites, null, 2)).toString('base64');
        
        const { data: result } = await octokit.rest.repos.createOrUpdateFileContents({
            owner,
            repo,
            path: 'data/sites.json',
            message: `Update sites list via Web UI at ${new Date().toISOString()}`,
            content,
            sha, // 파일이 존재하면 SHA 필요
            committer: {
                name: 'Singapore News Bot',
                email: 'bot@singapore-news.com'
            }
        });

        return res.status(200).json({
            success: true,
            message: '사이트 목록이 GitHub에 저장되었습니다.',
            sites: sites,
            commit: result.commit.sha
        });

    } catch (error) {
        console.error('Sites save error:', error);
        
        let errorMessage = '사이트 목록 저장 중 오류가 발생했습니다.';
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