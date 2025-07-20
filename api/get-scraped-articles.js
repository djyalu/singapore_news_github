const { Octokit } = require('@octokit/rest');

module.exports = async (req, res) => {
    // CORS 헤더 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    const { date } = req.query;
    
    if (!date) {
        return res.status(400).json({ 
            success: false, 
            error: '날짜 파라미터가 필요합니다. 형식: YYYYMMDD' 
        });
    }
    
    try {
        const octokit = new Octokit({
            auth: process.env.GITHUB_TOKEN
        });
        
        const owner = process.env.GITHUB_OWNER || 'djyalu';
        const repo = process.env.GITHUB_REPO || 'singapore_news_github';
        
        // 해당 날짜의 스크랩 파일들 찾기
        const { data: files } = await octokit.repos.getContent({
            owner,
            repo,
            path: 'data/scraped'
        });
        
        // 해당 날짜의 파일들 필터링 (news_YYYYMMDD_*.json)
        const dateFiles = files.filter(file => {
            return file.name.startsWith(`news_${date}`) && file.name.endsWith('.json');
        });
        
        if (dateFiles.length === 0) {
            return res.status(200).json({ 
                success: true, 
                articles: [],
                message: '해당 날짜의 스크랩 데이터가 없습니다.'
            });
        }
        
        // 가장 최근 파일 선택 (파일명 역순 정렬)
        const latestFile = dateFiles.sort((a, b) => b.name.localeCompare(a.name))[0];
        
        // 파일 내용 가져오기
        const { data: fileContent } = await octokit.repos.getContent({
            owner,
            repo,
            path: `data/scraped/${latestFile.name}`
        });
        
        // Base64 디코딩
        const content = Buffer.from(fileContent.content, 'base64').toString('utf-8');
        const articles = JSON.parse(content);
        
        return res.status(200).json({
            success: true,
            articles: articles,
            filename: latestFile.name,
            date: date
        });
        
    } catch (error) {
        console.error('스크랩 데이터 조회 오류:', error);
        return res.status(500).json({ 
            success: false, 
            error: error.message || '스크랩 데이터를 가져오는 중 오류가 발생했습니다.' 
        });
    }
};