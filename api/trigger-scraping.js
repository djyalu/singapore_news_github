const { Octokit } = require("@octokit/rest");

module.exports = async (req, res) => {
    // CORS 설정 - 모든 origin 허용
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');

    // OPTIONS 요청 처리 (preflight)
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // POST 요청만 허용
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // GitHub Personal Access Token 확인
        const githubToken = process.env.GITHUB_TOKEN;
        if (!githubToken) {
            return res.status(500).json({ 
                success: false, 
                error: 'GitHub token not configured. Please set GITHUB_TOKEN environment variable.' 
            });
        }

        // GitHub 저장소 정보 (환경변수에서 가져오거나 기본값 사용)
        const owner = process.env.GITHUB_OWNER || 'your-username'; // GitHub 사용자명으로 변경 필요
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';

        // Octokit 인스턴스 생성
        const octokit = new Octokit({
            auth: githubToken,
        });

        // GitHub Actions workflow dispatch
        const workflow_id = 'scraper.yml'; // 워크플로우 파일명

        console.log(`Triggering workflow: ${owner}/${repo}/${workflow_id}`);

        const response = await octokit.rest.actions.createWorkflowDispatch({
            owner,
            repo,
            workflow_id,
            ref: 'main', // 브랜치명
        });

        console.log('GitHub Actions triggered successfully:', response.status);

        return res.status(200).json({
            success: true,
            message: '뉴스 스크래핑이 시작되었습니다. 잠시 후 결과가 자동으로 표시됩니다.',
            github_response_status: response.status,
            workflow_url: `https://github.com/${owner}/${repo}/actions`
        });

    } catch (error) {
        console.error('GitHub Actions trigger error:', error);
        
        let errorMessage = '스크래핑 시작 중 오류가 발생했습니다.';
        
        if (error.status === 404) {
            errorMessage = 'GitHub 저장소 또는 워크플로우를 찾을 수 없습니다. GITHUB_OWNER와 GITHUB_REPO 환경변수를 확인하세요.';
        } else if (error.status === 401) {
            errorMessage = 'GitHub 인증에 실패했습니다. GITHUB_TOKEN을 확인하세요.';
        } else if (error.status === 403) {
            errorMessage = 'GitHub Actions 실행 권한이 없습니다. 토큰에 Actions 권한이 있는지 확인하세요.';
        }

        return res.status(500).json({
            success: false,
            error: errorMessage,
            details: error.message
        });
    }
};