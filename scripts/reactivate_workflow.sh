#!/bin/bash
# GitHub Actions 워크플로우 재활성화 스크립트

echo "🔄 GitHub Actions 워크플로우 재활성화 중..."

# 더미 커밋으로 저장소 활동 생성
echo "Workflow reactivation - $(date +%Y-%m-%d_%H:%M:%S)" >> workflow_status.log

# Git 설정
git add workflow_status.log
git commit -m "chore: Reactivate GitHub Actions workflow [$(date +%Y-%m-%d)]"
git push

echo "✅ 커밋 완료. GitHub Actions가 재활성화되어야 합니다."
echo ""
echo "다음 단계:"
echo "1. GitHub Actions 페이지 확인: https://github.com/djyalu/singapore_news_github/actions"
echo "2. 'Singapore News Scraper' 워크플로우 상태 확인"
echo "3. 필요시 'Run workflow' 버튼으로 수동 실행"