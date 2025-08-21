# 🚨 GitHub Actions 워크플로우 복구 가이드

## 문제 상황
- **발생일**: 2025년 8월 19일부터
- **증상**: WhatsApp으로 뉴스가 전송되지 않음
- **원인**: GitHub Actions 워크플로우 비활성화

## 즉시 조치사항

### 1. GitHub Actions 상태 확인
1. 브라우저에서 접속: https://github.com/djyalu/singapore_news_github/actions
2. "Singapore News Scraper" 워크플로우 찾기
3. 상태 확인:
   - ⚠️ "This workflow is disabled" 메시지가 보이면 비활성화 상태
   - ✅ 최근 실행 기록이 있으면 정상

### 2. 워크플로우 재활성화

#### 방법 1: GitHub 웹에서 직접 활성화
1. Actions 탭에서 "Singapore News Scraper" 클릭
2. "Enable workflow" 버튼 클릭
3. "Run workflow" 버튼으로 수동 실행

#### 방법 2: 커밋으로 재활성화
```bash
cd /mnt/d/projects/singapore_news_github
chmod +x scripts/reactivate_workflow.sh
./scripts/reactivate_workflow.sh
```

#### 방법 3: Vercel 대시보드에서 실행
1. https://singapore-news-github.vercel.app 접속
2. 로그인 (admin / Admin@123)
3. "스크래핑 시작" 버튼 클릭

### 3. 실행 확인
```bash
# 워크플로우 상태 확인
python3 scripts/check_workflow_status.py

# 모니터링
python3 scripts/monitor_workflow.py
```

### 4. 정상 작동 확인사항
- [ ] GitHub Actions 페이지에서 워크플로우 실행 중
- [ ] data/scraped/ 폴더에 새 파일 생성
- [ ] data/latest.json 업데이트
- [ ] WhatsApp 그룹에 메시지 수신

## 예방 조치

### 자동 재활성화 설정
1. keep-alive.yml 워크플로우가 활성화되어 있는지 확인
2. 주기적으로 저장소에 커밋이 발생하도록 설정

### 모니터링 강화
```bash
# 크론탭에 추가 (매일 오전 9시 확인)
0 9 * * * cd /mnt/d/projects/singapore_news_github && python3 scripts/monitor_workflow.py
```

## 문제 지속 시

1. **GitHub Actions 로그 확인**
   - Actions 탭 → 실패한 워크플로우 클릭 → 로그 확인

2. **API 키 확인**
   - GitHub Secrets: GOOGLE_GEMINI_API_KEY, COHERE_API_KEY
   - Vercel 환경변수: GITHUB_TOKEN

3. **수동 스크래핑 테스트**
   ```bash
   python3 scripts/scraper.py
   ```

## 연락처
- 이메일 알림: go41@naver.com
- WhatsApp 그룹: 120363421252284444@g.us

---
*최종 업데이트: 2025-08-21*