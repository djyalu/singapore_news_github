const { Octokit } = require('@octokit/rest');

export default async function handler(req, res) {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // OPTIONS 요청 처리
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { time } = req.body;
        
        if (!time || !/^\d{2}:\d{2}$/.test(time)) {
            return res.status(400).json({ error: 'Invalid time format' });
        }

        const [hours, minutes] = time.split(':').map(Number);
        
        // KST to UTC 변환 (KST = UTC + 9)
        let utcHours = hours - 9;
        if (utcHours < 0) {
            utcHours += 24;
        }

        const cronExpression = `${minutes} ${utcHours} * * *`;

        const octokit = new Octokit({
            auth: process.env.GITHUB_TOKEN
        });

        // scraper.yml 파일 가져오기
        const { data: fileData } = await octokit.repos.getContent({
            owner: process.env.GITHUB_OWNER || 'djyalu',
            repo: process.env.GITHUB_REPO || 'singapore_news_github',
            path: '.github/workflows/scraper.yml'
        });

        // Base64 디코딩
        const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
        
        // cron 표현식 업데이트
        const updatedContent = content.replace(
            /- cron: '[^']+'/,
            `- cron: '${cronExpression}'`
        ).replace(
            /# 하루 1번 실행 \(한국시간 기준: [^)]+\)/,
            `# 하루 1번 실행 (한국시간 기준: 오전 ${hours}시)`
        );

        // 파일 업데이트
        await octokit.repos.createOrUpdateFileContents({
            owner: process.env.GITHUB_OWNER || 'djyalu',
            repo: process.env.GITHUB_REPO || 'singapore_news_github',
            path: '.github/workflows/scraper.yml',
            message: `Update schedule to ${time} KST`,
            content: Buffer.from(updatedContent).toString('base64'),
            sha: fileData.sha
        });

        res.status(200).json({ 
            success: true, 
            message: `스케줄이 ${time} (KST)로 업데이트되었습니다.`,
            cron: cronExpression
        });

    } catch (error) {
        console.error('Schedule update error:', error);
        res.status(500).json({ 
            error: '스케줄 업데이트 실패', 
            details: error.message 
        });
    }
}