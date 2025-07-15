const { Octokit } = require("@octokit/rest");

module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // POST 요청만 허용
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const githubToken = process.env.GITHUB_TOKEN;
        const owner = process.env.GITHUB_OWNER || 'djyalu';
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';

        const octokit = new Octokit({
            auth: githubToken,
        });

        // 스크래핑만 실행
        const workflow_id = 'scraper-only.yml';

        const response = await octokit.rest.actions.createWorkflowDispatch({
            owner,
            repo,
            workflow_id,
            ref: 'main',
        });

        return res.status(200).json({
            success: true,
            message: '뉴스 스크래핑이 시작되었습니다.',
            workflow_url: `https://github.com/${owner}/${repo}/actions`
        });

    } catch (error) {
        console.error('Scraping trigger error:', error);
        
        return res.status(500).json({
            success: false,
            error: '스크래핑 시작 중 오류가 발생했습니다.',
            details: error.message
        });
    }
};