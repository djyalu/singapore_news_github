#!/usr/bin/env python3
"""
스트레스 테스트 실행 스크립트
로컬 모의 서버 또는 실제 Vercel 서버에 대해 테스트 수행
"""

import asyncio
import sys
import os
import argparse
import subprocess
import time
import signal
import json
from datetime import datetime, timezone, timedelta

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stress_test import StressTestManager

KST = timezone(timedelta(hours=9))

def start_mock_server():
    """모의 서버 시작"""
    print("모의 서버를 시작합니다...")
    # 백그라운드에서 Flask 서버 실행
    server_process = subprocess.Popen(
        [sys.executable, "mock_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 서버 시작 대기
    time.sleep(3)
    
    if server_process.poll() is not None:
        print("모의 서버 시작 실패!")
        return None
    
    print("모의 서버가 시작되었습니다 (PID: {})".format(server_process.pid))
    return server_process

def stop_mock_server(server_process):
    """모의 서버 중지"""
    if server_process:
        print("\n모의 서버를 중지합니다...")
        server_process.terminate()
        server_process.wait()
        print("모의 서버가 중지되었습니다.")

async def run_comprehensive_test(base_url: str, test_mode: str = "progressive"):
    """종합 스트레스 테스트 실행"""
    
    print(f"\n{'='*80}")
    print(f"Singapore News Scraper 종합 스트레스 테스트")
    print(f"테스트 모드: {test_mode}")
    print(f"대상 서버: {base_url}")
    print(f"시작 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"{'='*80}\n")
    
    # 테스트 매니저 초기화
    tester = StressTestManager(base_url)
    
    # 테스트 시나리오 정의
    if test_mode == "progressive":
        # 점진적 증가 테스트
        test_scenarios = [
            {"users": 10, "name": "워밍업 테스트", "batch_size": 10},
            {"users": 50, "name": "기본 부하 테스트", "batch_size": 25},
            {"users": 100, "name": "소규모 테스트", "batch_size": 50},
            {"users": 500, "name": "중간 규모 테스트", "batch_size": 100},
            {"users": 1000, "name": "중규모 테스트", "batch_size": 200},
            {"users": 5000, "name": "대규모 테스트", "batch_size": 500},
            {"users": 10000, "name": "최대 부하 테스트", "batch_size": 1000}
        ]
    elif test_mode == "spike":
        # 스파이크 테스트
        test_scenarios = [
            {"users": 100, "name": "기준선 테스트", "batch_size": 100},
            {"users": 5000, "name": "급증 테스트", "batch_size": 1000},
            {"users": 100, "name": "복구 테스트", "batch_size": 100}
        ]
    elif test_mode == "endurance":
        # 지속성 테스트
        test_scenarios = [
            {"users": 1000, "name": "지속성 테스트 1회차", "batch_size": 200},
            {"users": 1000, "name": "지속성 테스트 2회차", "batch_size": 200},
            {"users": 1000, "name": "지속성 테스트 3회차", "batch_size": 200}
        ]
    else:
        # 빠른 테스트
        test_scenarios = [
            {"users": 100, "name": "빠른 테스트", "batch_size": 50}
        ]
    
    # 전체 결과 저장
    all_results = {
        "test_mode": test_mode,
        "base_url": base_url,
        "start_time": datetime.now(KST).isoformat(),
        "scenarios": []
    }
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*60}")
        print(f"시나리오 {i+1}/{len(test_scenarios)}: {scenario['name']}")
        print(f"동시 사용자: {scenario['users']:,}명")
        print(f"{'='*60}")
        
        # 테스트 실행
        await tester.run_concurrent_test(
            scenario['users'], 
            batch_size=scenario['batch_size']
        )
        
        # 보고서 생성
        report = tester.generate_report()
        report["scenario_name"] = scenario['name']
        report["user_count"] = scenario['users']
        
        # 결과 저장
        filename = f"stress_test_{test_mode}_{scenario['users']}_users.json"
        tester.save_report(report, filename)
        
        # 요약 출력
        tester.print_summary(report)
        
        # 전체 결과에 추가
        all_results["scenarios"].append(report)
        
        # 다음 테스트 전 초기화
        tester.results.clear()
        tester.concurrent_users = 0
        tester.max_concurrent_users = 0
        
        # 테스트 간 대기 (마지막 제외)
        if i < len(test_scenarios) - 1:
            wait_time = 10 if test_mode == "quick" else 30
            print(f"\n다음 테스트까지 {wait_time}초 대기...")
            await asyncio.sleep(wait_time)
    
    # 전체 테스트 완료
    all_results["end_time"] = datetime.now(KST).isoformat()
    
    # 종합 보고서 생성
    generate_final_report(all_results)
    
    print(f"\n{'='*80}")
    print("모든 스트레스 테스트가 완료되었습니다!")
    print(f"종료 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}")
    print(f"{'='*80}")

def generate_final_report(all_results):
    """종합 최종 보고서 생성"""
    
    print("\n" + "="*80)
    print("종합 테스트 보고서")
    print("="*80)
    
    # 시나리오별 성공률 비교
    print("\n시나리오별 성공률:")
    for scenario in all_results["scenarios"]:
        print(f"  - {scenario['scenario_name']} ({scenario['user_count']:,}명): {scenario['overall_performance']['success_rate']}")
    
    # 최대 처리량 찾기
    max_rps = 0
    best_scenario = None
    for scenario in all_results["scenarios"]:
        rps_str = scenario['overall_performance']['requests_per_second']
        if rps_str != "N/A":
            rps = float(rps_str)
            if rps > max_rps:
                max_rps = rps
                best_scenario = scenario['scenario_name']
    
    print(f"\n최대 처리량: {max_rps:.2f} req/s ({best_scenario})")
    
    # 병목 지점 종합
    all_bottlenecks = {}
    for scenario in all_results["scenarios"]:
        for bottleneck in scenario.get("bottlenecks", []):
            key = f"{bottleneck['type']}_{bottleneck['function']}"
            if key not in all_bottlenecks:
                all_bottlenecks[key] = {
                    "count": 0,
                    "details": bottleneck
                }
            all_bottlenecks[key]["count"] += 1
    
    if all_bottlenecks:
        print("\n주요 병목 지점 (빈도순):")
        sorted_bottlenecks = sorted(all_bottlenecks.items(), key=lambda x: x[1]["count"], reverse=True)
        for key, data in sorted_bottlenecks[:5]:
            print(f"  - {data['details']['function']}: {data['details']['type']} (발생 횟수: {data['count']})")
    
    # 시스템 한계 분석
    print("\n시스템 성능 한계:")
    
    # 성공률 95% 이상을 유지하는 최대 사용자 수 찾기
    max_stable_users = 0
    for scenario in all_results["scenarios"]:
        success_rate = float(scenario['overall_performance']['success_rate'].rstrip('%'))
        if success_rate >= 95.0:
            max_stable_users = max(max_stable_users, scenario['user_count'])
    
    print(f"  - 안정적 처리 가능 사용자 수 (성공률 95% 이상): {max_stable_users:,}명")
    
    # 최종 권장사항
    print("\n최종 권장사항:")
    recommendations = set()
    for scenario in all_results["scenarios"]:
        for rec in scenario.get("recommendations", []):
            recommendations.add(rec)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # 종합 보고서 저장
    filename = f"final_report_{all_results['test_mode']}_{datetime.now(KST).strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n종합 보고서가 {filename}에 저장되었습니다.")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Singapore News Scraper 스트레스 테스트')
    parser.add_argument(
        '--target',
        choices=['local', 'vercel'],
        default='local',
        help='테스트 대상 (local: 로컬 모의 서버, vercel: 실제 Vercel 서버)'
    )
    parser.add_argument(
        '--mode',
        choices=['quick', 'progressive', 'spike', 'endurance'],
        default='progressive',
        help='테스트 모드'
    )
    
    args = parser.parse_args()
    
    # 서버 URL 설정
    if args.target == 'local':
        base_url = "http://localhost:5000"
        server_process = start_mock_server()
        
        if not server_process:
            print("테스트를 중단합니다.")
            return
    else:
        base_url = "https://singapore-news-github.vercel.app"
        server_process = None
        
        print("\n경고: 실제 Vercel 서버에 대한 테스트는 서비스에 영향을 줄 수 있습니다.")
        confirm = input("계속하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("테스트를 취소합니다.")
            return
    
    try:
        # 비동기 테스트 실행
        asyncio.run(run_comprehensive_test(base_url, args.mode))
        
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n테스트 중 오류 발생: {e}")
    finally:
        # 모의 서버 정리
        if server_process:
            stop_mock_server(server_process)

if __name__ == "__main__":
    main()