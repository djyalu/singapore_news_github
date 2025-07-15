// Vercel URL 자동 확인 스크립트
// 이 스크립트는 올바른 Vercel URL을 찾아서 app.js 파일을 업데이트합니다

const fs = require('fs');
const path = require('path');

// 가능한 Vercel URL 패턴들
const possibleUrls = [
    'https://singapore-news-github.vercel.app',
    'https://singapore-news-github-djyalu.vercel.app',
    'https://singapore-news-github-git-main-djyalu.vercel.app'
];

async function checkUrls() {
    console.log('🔍 Vercel URL 확인 중...');
    
    for (const url of possibleUrls) {
        try {
            console.log(`테스트 중: ${url}`);
            const response = await fetch(`${url}/api/send-whatsapp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    channel: 'test',
                    message: 'test'
                })
            });
            
            if (response.status === 400) { // 잘못된 파라미터 응답 = API 작동 중
                console.log(`✅ 작동하는 URL 발견: ${url}`);
                updateAppJs(url);
                return;
            }
        } catch (error) {
            console.log(`❌ ${url} - 연결 실패`);
        }
    }
    
    console.log('⚠️  작동하는 URL을 찾지 못했습니다.');
    console.log('수동으로 Vercel 대시보드에서 URL을 확인해주세요.');
}

function updateAppJs(correctUrl) {
    const appJsPath = path.join(__dirname, '..', 'js', 'app.js');
    let content = fs.readFileSync(appJsPath, 'utf8');
    
    // URL 패턴 찾기 및 교체
    const urlPattern = /const VERCEL_URL = '[^']*'/;
    const newLine = `const VERCEL_URL = '${correctUrl}'`;
    
    if (content.match(urlPattern)) {
        content = content.replace(urlPattern, newLine);
        fs.writeFileSync(appJsPath, content);
        console.log(`✅ app.js 파일이 업데이트되었습니다: ${correctUrl}`);
    } else {
        console.log('❌ app.js에서 URL 패턴을 찾을 수 없습니다.');
    }
}

// 스크립트 실행
checkUrls();