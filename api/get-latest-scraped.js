const { Octokit } = require("@octokit/rest");

module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
    res.setHeader('Access-Control-Allow-Credentials', 'true');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // GET 요청만 허용
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // 쿼리 파라미터 확인
        const { all, type, month } = req.query;
        const githubToken = process.env.GITHUB_TOKEN;
        const owner = process.env.GITHUB_OWNER || 'djyalu';
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';

        const octokit = new Octokit({
            auth: githubToken,
        });

        // 히스토리 데이터 요청인 경우
        if (type === 'history') {
            const historyPath = month ? `data/history/${month}.json` : 'data/history';
            
            if (month) {
                // 특정 월 히스토리 파일 조회
                try {
                    const { data: fileData } = await octokit.rest.repos.getContent({
                        owner,
                        repo,
                        path: historyPath,
                    });
                    
                    const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
                    const historyData = JSON.parse(content);
                    
                    return res.status(200).json({
                        success: true,
                        type: 'history',
                        month: month,
                        data: historyData
                    });
                } catch (error) {
                    if (error.status === 404) {
                        return res.status(200).json({
                            success: true,
                            type: 'history',
                            month: month,
                            data: []
                        });
                    }
                    throw error;
                }
            } else {
                // 히스토리 디렉토리 내 모든 파일 목록 조회
                const { data: historyFiles } = await octokit.rest.repos.getContent({
                    owner,
                    repo,
                    path: historyPath,
                });
                
                const monthFiles = historyFiles
                    .filter(file => file.name.match(/^\d{6}\.json$/))
                    .sort((a, b) => b.name.localeCompare(a.name));
                
                return res.status(200).json({
                    success: true,
                    type: 'history',
                    files: monthFiles.map(file => ({
                        name: file.name,
                        month: file.name.replace('.json', ''),
                        download_url: file.download_url,
                        size: file.size
                    }))
                });
            }
        }

        // data/scraped 디렉토리의 파일 목록 가져오기 (기존 로직)
        const { data: files } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: 'data/scraped',
        });

        // news_*.json 파일만 필터링하고 날짜순 정렬
        const newsFiles = files
            .filter(file => file.name.startsWith('news_') && file.name.endsWith('.json'))
            .sort((a, b) => b.name.localeCompare(a.name));

        if (newsFiles.length === 0) {
            return res.status(404).json({
                success: false,
                error: '스크래핑된 데이터가 없습니다.'
            });
        }

        // all=true인 경우 파일 목록만 반환
        if (all === 'true') {
            return res.status(200).json({
                success: true,
                files: newsFiles.map(file => ({
                    name: file.name,
                    download_url: file.download_url,
                    size: file.size
                })),
                count: newsFiles.length
            });
        }

        // 가장 최신 파일의 내용 가져오기
        const latestFile = newsFiles[0];
        const { data: fileContent } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: latestFile.path,
        });

        // Base64 디코딩
        const content = Buffer.from(fileContent.content, 'base64').toString('utf-8');
        const articles = JSON.parse(content);

        // 파일명에서 날짜 추출
        const dateMatch = latestFile.name.match(/news_(\d{8})_(\d{6})\.json/);
        let timestamp = new Date().toISOString();
        
        if (dateMatch) {
            const [_, dateStr, timeStr] = dateMatch;
            const year = dateStr.substr(0, 4);
            const month = dateStr.substr(4, 2);
            const day = dateStr.substr(6, 2);
            const hour = timeStr.substr(0, 2);
            const minute = timeStr.substr(2, 2);
            const second = timeStr.substr(4, 2);
            timestamp = new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`).toISOString();
        }

        return res.status(200).json({
            success: true,
            filename: latestFile.name,
            lastUpdated: timestamp,
            articleCount: articles.length,
            articles: articles
        });

    } catch (error) {
        console.error('Get scraped data error:', error);
        
        return res.status(500).json({
            success: false,
            error: '스크래핑 데이터 조회 중 오류가 발생했습니다.',
            details: error.message
        });
    }
};