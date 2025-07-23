const { Octokit } = require("@octokit/rest");

/**
 * GitHub Actions 스크래핑 워크플로우 트리거 API
 * 
 * POST /api/trigger-scraping
 * 
 * 기능:
 * - GitHub Actions의 scraper.yml 워크플로우를 수동으로 트리거
 * - 뉴스 스크래핑과 WhatsApp 전송을 모두 실행
 * 
 * 필요한 환경변수:
 * - GITHUB_TOKEN: GitHub Personal Access Token (repo, workflow 권한 필요)
 * - GITHUB_OWNER: GitHub 사용자명 또는 조직명
 * - GITHUB_REPO: 저장소 이름
 * 
 * 응답:
 * - 200: 성공적으로 워크플로우 트리거됨
 * - 401: GitHub 인증 실패
 * - 403: 권한 부족
 * - 404: 저장소 또는 워크플로우 없음
 * - 500: 서버 오류
 */
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
        const workflow_id = 'scraper.yml'; // 전체 스크래핑 + WhatsApp 전송 워크플로우

        console.log(`Triggering workflow: ${owner}/${repo}/${workflow_id}`);

        // 워크플로우 디스패치 이벤트 생성
        // workflow_dispatch 이벤트를 통해 수동으로 워크플로우 실행
        const response = await octokit.rest.actions.createWorkflowDispatch({
            owner,
            repo,
            workflow_id,
            ref: 'main', // 대상 브랜치 (main 브랜치에서 실행)
        });

        console.log('GitHub Actions triggered successfully:', response.status);

        // 성공 응답 반환
        // 실제 워크플로우 실행은 비동기로 진행되며
        // 클라이언트는 별도로 상태를 모니터링해야 함
        return res.status(200).json({
            success: true,
            message: '뉴스 스크래핑이 시작되었습니다. 잠시 후 결과가 자동으로 표시됩니다.',
            github_response_status: response.status,
            workflow_url: `https://github.com/${owner}/${repo}/actions`
        });

    } catch (error) {
        console.error('GitHub Actions trigger error:', error);
        
        // HTTP 상태 코드에 따른 구체적인 오류 메시지 생성
        let errorMessage = '스크래핑 시작 중 오류가 발생했습니다.';
        
        if (error.status === 404) {
            errorMessage = 'GitHub 저장소 또는 워크플로우를 찾을 수 없습니다. GITHUB_OWNER와 GITHUB_REPO 환경변수를 확인하세요.';
        } else if (error.status === 401) {
            errorMessage = 'GitHub 인증에 실패했습니다. GITHUB_TOKEN을 확인하세요.';
        } else if (error.status === 403) {
            errorMessage = 'GitHub Actions 실행 권한이 없습니다. 토큰에 Actions 권한이 있는지 확인하세요.';
        } else if (error.status === 422) {
            errorMessage = '워크플로우 설정이 잘못되었습니다. workflow_dispatch가 활성화되어 있는지 확인하세요.';
        }

        return res.status(500).json({
            success: false,
            error: errorMessage,
            details: error.message
        });
    }
};