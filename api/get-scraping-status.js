const { Octokit } = require("@octokit/rest");

module.exports = async (req, res) => {
    // CORS 설정 - 모든 origin 허용
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Content-Type', 'application/json');

    // OPTIONS 요청 처리 (preflight)
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // GET 요청만 허용
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // GitHub Personal Access Token 확인
        const githubToken = process.env.GITHUB_TOKEN;
        if (!githubToken) {
            return res.status(500).json({ 
                success: false, 
                error: 'GitHub token not configured' 
            });
        }

        // GitHub 저장소 정보
        const owner = process.env.GITHUB_OWNER || 'your-username';
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';

        // Octokit 인스턴스 생성
        const octokit = new Octokit({
            auth: githubToken,
        });

        // 최근 워크플로우 실행 상태 조회
        const workflowRuns = await octokit.rest.actions.listWorkflowRunsForRepo({
            owner,
            repo,
            per_page: 10, // 최근 10개 조회
        });

        // 스크래핑 워크플로우만 필터링
        const scrapingRuns = workflowRuns.data.workflow_runs.filter(run => 
            run.name === 'Singapore News Scraper'
        );

        const latestRun = scrapingRuns[0];

        if (!latestRun) {
            return res.status(200).json({
                success: true,
                status: 'no_runs',
                message: '실행된 스크래핑이 없습니다.'
            });
        }

        // 상태 매핑
        const statusMap = {
            'queued': { status: 'pending', message: '대기 중...', icon: '⏳' },
            'in_progress': { status: 'running', message: '스크래핑 실행 중...', icon: '🔄' },
            'completed': { 
                status: latestRun.conclusion === 'success' ? 'success' : 'error', 
                message: latestRun.conclusion === 'success' ? '스크래핑 완료' : '스크래핑 실패',
                icon: latestRun.conclusion === 'success' ? '✅' : '❌'
            },
            'cancelled': { status: 'cancelled', message: '스크래핑 취소됨', icon: '⭕' }
        };

        const currentStatus = statusMap[latestRun.status] || { 
            status: 'unknown', 
            message: `알 수 없는 상태: ${latestRun.status}`,
            icon: '❓'
        };

        // 실행 시간 계산
        const startTime = new Date(latestRun.created_at);
        const endTime = latestRun.updated_at ? new Date(latestRun.updated_at) : new Date();
        const duration = Math.round((endTime - startTime) / 1000); // 초 단위

        return res.status(200).json({
            success: true,
            ...currentStatus,
            run_id: latestRun.id,
            created_at: latestRun.created_at,
            updated_at: latestRun.updated_at,
            duration_seconds: duration,
            html_url: latestRun.html_url,
            conclusion: latestRun.conclusion,
            workflow_url: `https://github.com/${owner}/${repo}/actions`
        });

    } catch (error) {
        console.error('GitHub Actions status error:', error);
        
        return res.status(500).json({
            success: false,
            error: '스크래핑 상태 조회 중 오류가 발생했습니다.',
            details: error.message
        });
    }
};