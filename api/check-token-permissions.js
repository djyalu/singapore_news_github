const { Octokit } = require('@octokit/rest');

export default async function handler(req, res) {
    try {
        const octokit = new Octokit({
            auth: process.env.GITHUB_TOKEN
        });

        // 토큰 권한 확인
        const { data: user } = await octokit.users.getAuthenticated();
        
        // 워크플로우 파일 접근 테스트
        try {
            const { data: workflow } = await octokit.repos.getContent({
                owner: process.env.GITHUB_OWNER || 'djyalu',
                repo: process.env.GITHUB_REPO || 'singapore_news_github',
                path: '.github/workflows/scraper.yml'
            });
            
            res.status(200).json({
                success: true,
                user: user.login,
                permissions: {
                    workflow: true,
                    repo: true
                },
                message: 'GitHub Token has required permissions'
            });
        } catch (error) {
            if (error.status === 404) {
                res.status(403).json({
                    success: false,
                    error: 'Workflow file not found or no access',
                    permissions: {
                        workflow: false,
                        repo: true
                    }
                });
            } else {
                throw error;
            }
        }
    } catch (error) {
        res.status(401).json({
            success: false,
            error: 'Invalid token or insufficient permissions',
            details: error.message
        });
    }
}