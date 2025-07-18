import json
import os
import sys
from datetime import datetime, timedelta
import argparse
from monitoring import send_email, load_settings

def load_monitoring_logs(days=1):
    """최근 N일간의 모니터링 로그 로드"""
    log_dir = 'data/monitoring'
    logs = []
    
    # 현재 월과 이전 월 로그 파일 확인
    current_month = datetime.now().strftime('%Y%m')
    last_month = (datetime.now() - timedelta(days=30)).strftime('%Y%m')
    
    for month in [last_month, current_month]:
        log_file = os.path.join(log_dir, f"log_{month}.json")
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                month_logs = json.load(f)
                logs.extend(month_logs)
    
    # 날짜 필터링
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_logs = []
    
    for log in logs:
        try:
            log_date = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            if log_date >= cutoff_date:
                filtered_logs.append(log)
        except:
            continue
    
    return sorted(filtered_logs, key=lambda x: x['timestamp'])

def generate_daily_report():
    """일일 리포트 생성"""
    logs = load_monitoring_logs(1)
    
    total_runs = len(logs)
    successful_runs = sum(1 for log in logs if log.get('status') == 'success')
    failed_runs = sum(1 for log in logs if log.get('status') == 'failure')
    no_articles_runs = sum(1 for log in logs if log.get('status') == 'no_articles')
    
    total_articles = sum(log.get('article_count', 0) for log in logs if log.get('status') == 'success')
    
    # 실패 상세 정보
    failures = []
    for log in logs:
        if log.get('status') == 'failure':
            failures.append({
                'time': log.get('execution_time', 'Unknown'),
                'error': log.get('error_message', 'Unknown error')
            })
    
    # HTML 리포트 생성
    html = f"""
    <h2>📊 일일 스크래핑 리포트</h2>
    <p><b>날짜:</b> {datetime.now().strftime('%Y년 %m월 %d일')}</p>
    
    <h3>📈 실행 통계</h3>
    <ul>
        <li>총 실행 횟수: {total_runs}회</li>
        <li>성공: {successful_runs}회</li>
        <li>실패: {failed_runs}회</li>
        <li>기사 없음: {no_articles_runs}회</li>
    </ul>
    
    <h3>📰 수집 통계</h3>
    <ul>
        <li>총 수집 기사: {total_articles}개</li>
        <li>평균 기사/실행: {total_articles/successful_runs if successful_runs > 0 else 0:.1f}개</li>
    </ul>
    """
    
    if failures:
        html += """
        <h3>❌ 실패 내역</h3>
        <ul>
        """
        for failure in failures:
            html += f"<li>{failure['time']}: {failure['error']}</li>"
        html += "</ul>"
    
    return html, f"📊 일일 리포트 - {datetime.now().strftime('%Y-%m-%d')}"

def generate_weekly_report():
    """주간 리포트 생성"""
    logs = load_monitoring_logs(7)
    
    total_runs = len(logs)
    successful_runs = sum(1 for log in logs if log.get('status') == 'success')
    failed_runs = sum(1 for log in logs if log.get('status') == 'failure')
    
    total_articles = sum(log.get('article_count', 0) for log in logs if log.get('status') == 'success')
    
    # 일별 통계
    daily_stats = {}
    for log in logs:
        date = log['timestamp'].split('T')[0]
        if date not in daily_stats:
            daily_stats[date] = {'success': 0, 'failure': 0, 'articles': 0}
        
        if log.get('status') == 'success':
            daily_stats[date]['success'] += 1
            daily_stats[date]['articles'] += log.get('article_count', 0)
        elif log.get('status') == 'failure':
            daily_stats[date]['failure'] += 1
    
    # HTML 리포트 생성
    html = f"""
    <h2>📊 주간 스크래핑 리포트</h2>
    <p><b>기간:</b> {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}</p>
    
    <h3>📈 주간 요약</h3>
    <ul>
        <li>총 실행 횟수: {total_runs}회</li>
        <li>성공률: {successful_runs/total_runs*100 if total_runs > 0 else 0:.1f}%</li>
        <li>총 수집 기사: {total_articles}개</li>
    </ul>
    
    <h3>📅 일별 통계</h3>
    <table style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f5f5f5;">
            <th style="padding: 8px; border: 1px solid #ddd;">날짜</th>
            <th style="padding: 8px; border: 1px solid #ddd;">성공</th>
            <th style="padding: 8px; border: 1px solid #ddd;">실패</th>
            <th style="padding: 8px; border: 1px solid #ddd;">기사 수</th>
        </tr>
    """
    
    for date in sorted(daily_stats.keys(), reverse=True):
        stats = daily_stats[date]
        html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{date}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{stats['success']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{stats['failure']}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{stats['articles']}</td>
        </tr>
        """
    
    html += "</table>"
    
    return html, f"📊 주간 리포트 - {datetime.now().strftime('%Y년 %m월 %d일')}"

def main():
    parser = argparse.ArgumentParser(description='Send monitoring report')
    parser.add_argument('--type', choices=['daily', 'weekly'], default='daily', help='Report type')
    args = parser.parse_args()
    
    # 설정 로드
    settings = load_settings()
    monitoring = settings.get('monitoring', {})
    
    if not monitoring.get('enabled', False):
        print("Monitoring is disabled")
        return
    
    # 리포트 타입 확인
    if args.type == 'daily' and not monitoring.get('summary', {}).get('dailyReport', False):
        print("Daily reports are disabled")
        return
    
    if args.type == 'weekly' and not monitoring.get('summary', {}).get('weeklyReport', False):
        print("Weekly reports are disabled")
        return
    
    # 수신자 확인
    email_settings = monitoring.get('email', {})
    if not email_settings.get('enabled', False):
        print("Email notifications are disabled")
        return
    
    recipients = email_settings.get('recipients', [])
    if not recipients:
        print("No email recipients configured")
        return
    
    # 리포트 생성
    if args.type == 'daily':
        body, subject = generate_daily_report()
    else:
        body, subject = generate_weekly_report()
    
    # 이메일 전송
    success = send_email(subject, body, recipients, settings)
    
    if success:
        print(f"{args.type.capitalize()} report sent successfully")
    else:
        print(f"Failed to send {args.type} report")
        sys.exit(1)

if __name__ == "__main__":
    main()