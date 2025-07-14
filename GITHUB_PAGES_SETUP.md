# GitHub Pages 설정 방법

## 방법 1: Repository를 Public으로 변경 (권장)

1. GitHub Repository 페이지로 이동
2. Settings 탭 클릭
3. 페이지 맨 아래 "Danger Zone" 섹션
4. "Change repository visibility" 클릭
5. "Change to public" 선택
6. Repository 이름을 입력하여 확인
7. "I understand, change repository visibility" 클릭

### Public으로 변경 후:
1. Settings > Pages로 다시 이동
2. Source: "Deploy from a branch" 선택
3. Branch: "main", Folder: "/ (root)" 선택
4. Save 클릭

## 방법 2: GitHub Pro 업그레이드 (월 $4)

Private repository에서 GitHub Pages를 사용하려면:
1. GitHub 계정 Settings로 이동
2. "Billing and plans" 클릭
3. "Upgrade" 선택
4. GitHub Pro 플랜 선택

## 방법 3: 대안 - Vercel 사용 (무료)

Private repository를 유지하면서 무료로 호스팅하려면:

### Vercel 설정:
1. https://vercel.com 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. GitHub repository 연결
5. 프로젝트 설정:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: 비워둠
   - Output Directory: ./
6. "Deploy" 클릭

### Vercel 환경변수 설정:
1. Project Settings > Environment Variables
2. 다음 변수 추가:
   - OPENAI_API_KEY
   - WHATSAPP_API_KEY

## 방법 4: 대안 - Netlify 사용 (무료)

### Netlify 설정:
1. https://netlify.com 접속
2. GitHub 계정으로 로그인
3. "Add new site" > "Import an existing project"
4. GitHub repository 연결
5. 배포 설정:
   - Base directory: 비워둠
   - Build command: 비워둠
   - Publish directory: ./
6. "Deploy site" 클릭

### 보안 고려사항

Public repository 사용 시 주의:
1. API 키는 절대 코드에 직접 넣지 말고 GitHub Secrets 사용
2. 민감한 데이터는 .gitignore에 추가
3. WhatsApp 채널 ID는 환경변수로 관리 권장

### .gitignore 파일 추가:
```
# API Keys
.env
.env.local

# Data files
data/scraped/*
data/history/*
!data/scraped/.gitkeep
!data/history/.gitkeep

# Logs
*.log

# OS files
.DS_Store
Thumbs.db
```