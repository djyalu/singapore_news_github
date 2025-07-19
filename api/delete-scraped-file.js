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
        const { filename } = req.body;
        
        // 파일명 검증
        if (!filename) {
            return res.status(400).json({ 
                success: false, 
                error: '삭제할 파일명이 필요합니다.' 
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
        
        // 파일 경로
        const filepath = `data/scraped/${filename}`;
        
        // 현재 파일의 SHA 가져오기 (삭제에 필요)
        let sha;
        try {
            const { data: fileData } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: filepath,
            });
            sha = fileData.sha;
        } catch (error) {
            if (error.status === 404) {
                return res.status(404).json({
                    success: false,
                    error: '파일을 찾을 수 없습니다.'
                });
            }
            throw error;
        }
        
        // GitHub에서 파일 삭제
        const { data: result } = await octokit.rest.repos.deleteFile({
            owner,
            repo,
            path: filepath,
            message: `Delete scraped file ${filename} via Web UI at ${new Date().toISOString()}`,
            sha,
            committer: {
                name: 'Singapore News Bot',
                email: 'bot@singapore-news.com'
            }
        });

        // latest.json 업데이트 (이전 파일로 되돌리기)
        try {
            // 남은 파일 목록 가져오기
            const { data: files } = await octokit.rest.repos.getContent({
                owner,
                repo,
                path: 'data/scraped',
            });
            
            // news_*.json 파일만 필터링하고 날짜순 정렬
            const newsFiles = files
                .filter(file => file.name.startsWith('news_') && file.name.endsWith('.json') && file.name !== filename)
                .sort((a, b) => b.name.localeCompare(a.name));
            
            if (newsFiles.length > 0) {
                // 가장 최신 파일로 latest.json 업데이트
                const latestFile = newsFiles[0];
                const latestData = {
                    lastUpdated: new Date().toISOString(),
                    latestFile: latestFile.name,
                    scrapingMethod: "traditional",
                    executionType: "manual"
                };
                
                // latest.json 파일 가져오기 (SHA 필요)
                const { data: latestFileData } = await octokit.rest.repos.getContent({
                    owner,
                    repo,
                    path: 'data/latest.json',
                });
                
                // latest.json 업데이트
                await octokit.rest.repos.createOrUpdateFileContents({
                    owner,
                    repo,
                    path: 'data/latest.json',
                    message: `Update latest.json after deleting ${filename}`,
                    content: Buffer.from(JSON.stringify(latestData, null, 2)).toString('base64'),
                    sha: latestFileData.sha,
                });
            }
        } catch (updateError) {
            console.error('latest.json 업데이트 실패:', updateError);
            // latest.json 업데이트 실패해도 파일 삭제는 성공으로 처리
        }

        return res.status(200).json({
            success: true,
            message: `파일 ${filename}이(가) GitHub에서 삭제되었습니다.`,
            commit: result.commit.sha
        });

    } catch (error) {
        console.error('File deletion error:', error);
        
        let errorMessage = '파일 삭제 중 오류가 발생했습니다.';
        if (error.status === 404) {
            errorMessage = '파일 또는 저장소를 찾을 수 없습니다.';
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