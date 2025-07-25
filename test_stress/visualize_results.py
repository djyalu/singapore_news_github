#!/usr/bin/env python3
"""
스트레스 테스트 결과 시각화
ASCII 차트로 결과를 시각적으로 표현
"""

import json
import os

def load_results():
    """시뮬레이션 결과 로드"""
    with open('stress_test_10k_users_simulation.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_ascii_chart(data_points, title, y_label, width=80, height=20):
    """ASCII 차트 생성"""
    if not data_points:
        return ""
    
    # 데이터 정규화
    max_val = max(data_points, key=lambda x: x[1])[1]
    min_val = min(data_points, key=lambda x: x[1])[1]
    
    # 차트 생성
    chart = []
    chart.append(f"\n{title}")
    chart.append("=" * width)
    
    # Y축 라벨
    chart.append(f"{y_label}")
    chart.append("")
    
    # 그래프 영역
    graph_width = width - 10
    graph_height = height - 5
    
    # 각 행 생성
    for h in range(graph_height, -1, -1):
        row = ""
        y_val = min_val + (max_val - min_val) * (h / graph_height)
        row += f"{y_val:7.1f} │"
        
        for i, (x, y) in enumerate(data_points):
            x_pos = int(i * graph_width / len(data_points))
            y_pos = int((y - min_val) / (max_val - min_val) * graph_height)
            
            if y_pos == h:
                row += "█"
            elif y_pos > h:
                row += "│"
            else:
                row += " "
        
        chart.append(row)
    
    # X축
    chart.append(" " * 8 + "└" + "─" * graph_width)
    
    # X축 라벨
    x_labels = " " * 10
    for i, (x, _) in enumerate(data_points):
        if i % 2 == 0:  # 라벨이 겹치지 않도록
            x_labels += f"{x:<10}"
    chart.append(x_labels)
    chart.append(" " * 30 + "사용자 수")
    
    return "\n".join(chart)

def create_performance_table(results):
    """성능 비교 테이블 생성"""
    table = []
    table.append("\n기능별 성능 매트릭스 (10,000명 사용자 기준)")
    table.append("=" * 80)
    table.append(f"{'기능':<20} {'성공률':>10} {'평균응답':>12} {'상태':>10} {'권장조치':<25}")
    table.append("-" * 80)
    
    last_scenario = results['scenarios'][-1]  # 10,000명 테스트
    
    for func_name, perf in last_scenario['function_performance'].items():
        success_rate = float(perf['success_rate'].rstrip('%'))
        avg_response = float(perf['response_time']['average'].rstrip('s'))
        
        # 상태 판단
        if success_rate >= 95 and avg_response < 1.0:
            status = "✅ 정상"
            action = "현재 상태 유지"
        elif success_rate >= 90 or avg_response < 2.0:
            status = "⚠️  주의"
            action = "모니터링 강화"
        else:
            status = "❌ 위험"
            action = "즉시 개선 필요"
        
        # 기능명 한글화
        func_name_kr = {
            'login': '로그인',
            'dashboard_access': '대시보드 접근',
            'get_latest_articles': '최신 기사 조회',
            'trigger_scraping': '스크래핑 트리거',
            'get_scraping_status': '상태 조회',
            'settings_update': '설정 업데이트',
            'article_search': '기사 검색'
        }.get(func_name, func_name)
        
        table.append(f"{func_name_kr:<20} {perf['success_rate']:>10} {perf['response_time']['average']:>12} {status:>10} {action:<25}")
    
    return "\n".join(table)

def create_capacity_chart():
    """시스템 용량 차트"""
    chart = []
    chart.append("\n시스템 용량 및 안정성 지표")
    chart.append("=" * 80)
    chart.append("")
    chart.append("사용자 수    성공률    시스템 상태")
    chart.append("─" * 80)
    
    levels = [
        (100, 95, "████████████████████ 100% - 최적 상태"),
        (500, 92, "██████████████████░░ 92% - 양호"),
        (1000, 87, "█████████████████░░░ 87% - 권장 한계선 ←"),
        (2000, 82, "████████████████░░░░ 82% - 주의 필요"),
        (5000, 75, "███████████████░░░░░ 75% - 성능 저하"),
        (10000, 65, "█████████████░░░░░░░ 65% - 위험 수준")
    ]
    
    for users, success, bar in levels:
        chart.append(f"{users:>6}명     {success}%    {bar}")
    
    chart.append("")
    chart.append("권장: 1,000명 이하에서 운영")
    chart.append("한계: 5,000명 (긴급 대응 필요)")
    chart.append("위험: 10,000명 (시스템 재설계 필요)")
    
    return "\n".join(chart)

def create_cost_benefit_analysis():
    """비용 대비 효과 분석"""
    analysis = []
    analysis.append("\n투자 대비 효과 분석")
    analysis.append("=" * 80)
    analysis.append("")
    analysis.append("현재 상태 (무료)")
    analysis.append("├─ 안정적 사용자: 1,000명")
    analysis.append("├─ 월 비용: $0")
    analysis.append("└─ 성능: ★★☆☆☆")
    analysis.append("")
    analysis.append("단기 개선 ($35/월)")
    analysis.append("├─ 안정적 사용자: 5,000명 (+400%)")
    analysis.append("├─ 구성: Vercel Pro + Redis")
    analysis.append("└─ 성능: ★★★★☆")
    analysis.append("")
    analysis.append("전체 최적화 ($70/월)")
    analysis.append("├─ 안정적 사용자: 10,000명 (+900%)")
    analysis.append("├─ 구성: Vercel Pro + Redis + CDN + Monitoring")
    analysis.append("└─ 성능: ★★★★★")
    
    return "\n".join(analysis)

def main():
    """메인 실행 함수"""
    print("스트레스 테스트 결과 시각화")
    print("=" * 80)
    
    # 결과 로드
    results = load_results()
    
    # 1. 성공률 차트
    success_data = []
    response_data = []
    
    for scenario in results['scenarios']:
        users = scenario['user_count']
        success_rate = float(scenario['overall_performance']['success_rate'].rstrip('%'))
        avg_response = float(scenario['overall_performance']['average_response_time'].rstrip('s'))
        
        success_data.append((users, success_rate))
        response_data.append((users, avg_response))
    
    print(create_ascii_chart(success_data, "성공률 vs 사용자 수", "성공률 (%)", height=15))
    print(create_ascii_chart(response_data, "응답 시간 vs 사용자 수", "응답시간 (초)", height=15))
    
    # 2. 성능 테이블
    print(create_performance_table(results))
    
    # 3. 시스템 용량 차트
    print(create_capacity_chart())
    
    # 4. 비용 대비 효과 분석
    print(create_cost_benefit_analysis())
    
    # 5. 핵심 요약
    print("\n" + "=" * 80)
    print("핵심 요약")
    print("=" * 80)
    print("✅ 현재 안정적 처리 가능: 1,000명")
    print("⚠️  최적화 후 처리 가능: 5,000명 ($35/월)")
    print("🚀 전체 업그레이드 후: 10,000명 ($70/월)")
    print("")
    print("가장 시급한 개선 사항:")
    print("1. 스크래핑 트리거 비동기 처리 (성공률 64.95% → 90%)")
    print("2. Redis 캐싱 도입 (응답시간 50% 단축)")
    print("3. CDN 적용 (대시보드 로딩 70% 개선)")
    print("=" * 80)

if __name__ == "__main__":
    main()