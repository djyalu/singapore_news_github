#!/usr/bin/env python3
"""
Singapore News Scraper 대규모 스트레스 테스트
목표: 10,000명의 동시 사용자 시뮬레이션
"""

import asyncio
import aiohttp
import time
import json
import random
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
import os
import sys
from dataclasses import dataclass
from collections import defaultdict
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# KST 시간대 설정
KST = timezone(timedelta(hours=9))

@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    function_name: str
    success: bool
    response_time: float
    status_code: int = 0
    error_message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(KST)

class StressTestManager:
    """스트레스 테스트 관리 클래스"""
    
    def __init__(self, base_url: str = "https://singapore-news-github.vercel.app"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.results: List[TestResult] = []
        self.concurrent_users = 0
        self.max_concurrent_users = 0
        self.start_time = None
        self.end_time = None
        
        # 테스트 계정 정보
        self.test_credentials = {
            "username": "admin",
            "password": "Admin@123"
        }
        
        # API 엔드포인트 목록
        self.endpoints = {
            "auth": "/auth",
            "trigger_scraping": "/trigger-scraping",
            "scrape_only": "/scrape-only",
            "send_only": "/send-only",
            "get_status": "/get-scraping-status",
            "get_latest": "/get-latest-scraped",
            "get_articles": "/get-scraped-articles",
            "save_data": "/save-data",
            "delete_file": "/delete-scraped-file"
        }
        
    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int) -> List[TestResult]:
        """단일 사용자 세션 시뮬레이션"""
        user_results = []
        
        try:
            # 1. 로그인 시도
            login_result = await self._test_login(session, user_id)
            user_results.append(login_result)
            
            if not login_result.success:
                return user_results
            
            # 2. 대시보드 접근
            dashboard_result = await self._test_dashboard_access(session, user_id)
            user_results.append(dashboard_result)
            
            # 3. 랜덤하게 기능 사용
            actions = random.sample([
                self._test_get_latest_articles,
                self._test_trigger_scraping,
                self._test_get_status,
                self._test_settings_update,
                self._test_article_search
            ], k=random.randint(2, 4))
            
            for action in actions:
                result = await action(session, user_id)
                user_results.append(result)
                
                # 사용자 행동 시뮬레이션 (랜덤 대기)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            logger.error(f"User {user_id} session error: {e}")
            
        return user_results
    
    async def _test_login(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """로그인 테스트"""
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.api_base}{self.endpoints['auth']}",
                json=self.test_credentials,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                return TestResult(
                    function_name="login",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="login",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_dashboard_access(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """대시보드 접근 테스트"""
        start_time = time.time()
        
        try:
            async with session.get(
                self.base_url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                return TestResult(
                    function_name="dashboard_access",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="dashboard_access",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_get_latest_articles(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """최신 기사 조회 테스트"""
        start_time = time.time()
        
        try:
            async with session.get(
                f"{self.api_base}{self.endpoints['get_latest']}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                if success:
                    data = await response.json()
                    # 데이터 무결성 검증
                    if not isinstance(data, dict) or 'scraped_date' not in data:
                        success = False
                
                return TestResult(
                    function_name="get_latest_articles",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="get_latest_articles",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_trigger_scraping(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """스크래핑 트리거 테스트"""
        start_time = time.time()
        
        try:
            # 실제 스크래핑을 트리거하지 않고 API 응답만 테스트
            # (실제 환경에서는 rate limiting 고려)
            async with session.post(
                f"{self.api_base}{self.endpoints['trigger_scraping']}",
                json={"test_mode": True},  # 테스트 모드 플래그
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status in [200, 202]  # 202 Accepted도 성공으로 간주
                
                return TestResult(
                    function_name="trigger_scraping",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="trigger_scraping",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_get_status(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """스크래핑 상태 조회 테스트"""
        start_time = time.time()
        
        try:
            async with session.get(
                f"{self.api_base}{self.endpoints['get_status']}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                return TestResult(
                    function_name="get_scraping_status",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="get_scraping_status",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_settings_update(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """설정 업데이트 테스트"""
        start_time = time.time()
        
        try:
            # 임시 설정 데이터 (실제로는 변경하지 않음)
            test_settings = {
                "type": "settings",
                "data": {
                    "scrapingMethod": "hybrid",
                    "test_mode": True
                }
            }
            
            async with session.post(
                f"{self.api_base}{self.endpoints['save_data']}",
                json=test_settings,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                return TestResult(
                    function_name="settings_update",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="settings_update",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _test_article_search(self, session: aiohttp.ClientSession, user_id: int) -> TestResult:
        """기사 검색 테스트"""
        start_time = time.time()
        
        try:
            # 날짜 범위로 기사 검색
            params = {
                "startDate": (datetime.now(KST) - timedelta(days=7)).isoformat(),
                "endDate": datetime.now(KST).isoformat()
            }
            
            async with session.get(
                f"{self.api_base}{self.endpoints['get_articles']}",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                return TestResult(
                    function_name="article_search",
                    success=success,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            return TestResult(
                function_name="article_search",
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def run_concurrent_test(self, num_users: int, batch_size: int = 100):
        """동시 사용자 테스트 실행"""
        self.start_time = datetime.now(KST)
        logger.info(f"=== 스트레스 테스트 시작: {num_users}명 사용자 시뮬레이션 ===")
        
        # 커넥션 풀 설정
        connector = aiohttp.TCPConnector(
            limit=1000,  # 전체 연결 제한
            limit_per_host=100  # 호스트당 연결 제한
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # 배치로 나누어 실행
            for batch_start in range(0, num_users, batch_size):
                batch_end = min(batch_start + batch_size, num_users)
                batch_users = range(batch_start, batch_end)
                
                logger.info(f"배치 실행: 사용자 {batch_start}-{batch_end}")
                
                # 동시 실행
                tasks = [
                    self.simulate_user_session(session, user_id)
                    for user_id in batch_users
                ]
                
                # 현재 동시 사용자 수 업데이트
                self.concurrent_users = len(tasks)
                self.max_concurrent_users = max(self.max_concurrent_users, self.concurrent_users)
                
                # 배치 실행
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 결과 수집
                for results in batch_results:
                    if isinstance(results, Exception):
                        logger.error(f"배치 실행 오류: {results}")
                    else:
                        self.results.extend(results)
                
                # 배치 간 짧은 대기
                await asyncio.sleep(1)
        
        self.end_time = datetime.now(KST)
        
    def generate_report(self) -> Dict:
        """종합 테스트 보고서 생성"""
        if not self.results:
            return {"error": "테스트 결과가 없습니다"}
        
        # 기능별 통계
        function_stats = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "failure": 0,
            "response_times": [],
            "errors": []
        })
        
        for result in self.results:
            stats = function_stats[result.function_name]
            stats["total"] += 1
            
            if result.success:
                stats["success"] += 1
            else:
                stats["failure"] += 1
                if result.error_message:
                    stats["errors"].append(result.error_message)
            
            stats["response_times"].append(result.response_time)
        
        # 종합 보고서 생성
        report = {
            "test_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
                "total_requests": len(self.results),
                "max_concurrent_users": self.max_concurrent_users
            },
            "function_performance": {}
        }
        
        # 기능별 성능 지표
        for func_name, stats in function_stats.items():
            response_times = stats["response_times"]
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            report["function_performance"][func_name] = {
                "total_requests": stats["total"],
                "success_count": stats["success"],
                "failure_count": stats["failure"],
                "success_rate": f"{success_rate:.2f}%",
                "response_time": {
                    "average": f"{statistics.mean(response_times):.3f}s" if response_times else "N/A",
                    "median": f"{statistics.median(response_times):.3f}s" if response_times else "N/A",
                    "min": f"{min(response_times):.3f}s" if response_times else "N/A",
                    "max": f"{max(response_times):.3f}s" if response_times else "N/A",
                    "p95": f"{statistics.quantiles(response_times, n=20)[18]:.3f}s" if len(response_times) > 20 else "N/A",
                    "p99": f"{statistics.quantiles(response_times, n=100)[98]:.3f}s" if len(response_times) > 100 else "N/A"
                },
                "unique_errors": list(set(stats["errors"]))[:5]  # 상위 5개 에러만
            }
        
        # 전체 성능 지표
        all_response_times = [r.response_time for r in self.results]
        total_success = sum(1 for r in self.results if r.success)
        
        report["overall_performance"] = {
            "success_rate": f"{(total_success / len(self.results) * 100):.2f}%",
            "average_response_time": f"{statistics.mean(all_response_times):.3f}s",
            "requests_per_second": f"{len(self.results) / report['test_summary']['duration_seconds']:.2f}" if report['test_summary']['duration_seconds'] > 0 else "N/A"
        }
        
        # 병목 지점 분석
        report["bottlenecks"] = self._analyze_bottlenecks(function_stats)
        
        # 권장사항
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_bottlenecks(self, function_stats: Dict) -> List[Dict]:
        """병목 지점 분석"""
        bottlenecks = []
        
        for func_name, stats in function_stats.items():
            if not stats["response_times"]:
                continue
                
            avg_time = statistics.mean(stats["response_times"])
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            # 느린 응답 시간
            if avg_time > 2.0:
                bottlenecks.append({
                    "type": "slow_response",
                    "function": func_name,
                    "average_time": f"{avg_time:.3f}s",
                    "severity": "high" if avg_time > 5.0 else "medium"
                })
            
            # 높은 실패율
            if success_rate < 95.0:
                bottlenecks.append({
                    "type": "high_failure_rate",
                    "function": func_name,
                    "success_rate": f"{success_rate:.2f}%",
                    "severity": "high" if success_rate < 80.0 else "medium"
                })
        
        return sorted(bottlenecks, key=lambda x: x["severity"], reverse=True)
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 전체 성공률 기반
        overall_success = float(report["overall_performance"]["success_rate"].rstrip('%'))
        if overall_success < 95.0:
            recommendations.append("전체 성공률이 95% 미만입니다. 서버 용량 증설이나 로드 밸런싱 고려가 필요합니다.")
        
        # 응답 시간 기반
        avg_response = float(report["overall_performance"]["average_response_time"].rstrip('s'))
        if avg_response > 1.0:
            recommendations.append("평균 응답 시간이 1초를 초과합니다. 캐싱 전략이나 쿼리 최적화를 검토하세요.")
        
        # 병목 지점 기반
        for bottleneck in report["bottlenecks"][:3]:  # 상위 3개만
            if bottleneck["type"] == "slow_response":
                recommendations.append(f"{bottleneck['function']} 기능의 응답 시간이 느립니다. 비동기 처리나 백그라운드 작업을 고려하세요.")
            elif bottleneck["type"] == "high_failure_rate":
                recommendations.append(f"{bottleneck['function']} 기능의 실패율이 높습니다. 에러 처리 및 재시도 로직을 강화하세요.")
        
        # 동시 사용자 처리
        if self.max_concurrent_users > 1000:
            recommendations.append("1000명 이상의 동시 사용자 처리 시 서버 리소스 모니터링을 강화하세요.")
        
        return recommendations
    
    def save_report(self, report: Dict, filename: str = "stress_test_report.json"):
        """보고서 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"테스트 보고서가 {filename}에 저장되었습니다.")
    
    def print_summary(self, report: Dict):
        """보고서 요약 출력"""
        print("\n" + "="*80)
        print("스트레스 테스트 결과 요약")
        print("="*80)
        
        print(f"\n테스트 시간: {report['test_summary']['start_time']} ~ {report['test_summary']['end_time']}")
        print(f"소요 시간: {report['test_summary']['duration_seconds']:.2f}초")
        print(f"총 요청 수: {report['test_summary']['total_requests']:,}")
        print(f"최대 동시 사용자: {report['test_summary']['max_concurrent_users']:,}명")
        
        print(f"\n전체 성공률: {report['overall_performance']['success_rate']}")
        print(f"평균 응답 시간: {report['overall_performance']['average_response_time']}")
        print(f"초당 처리량: {report['overall_performance']['requests_per_second']} req/s")
        
        print("\n기능별 성능:")
        for func_name, perf in report['function_performance'].items():
            print(f"\n  {func_name}:")
            print(f"    - 성공률: {perf['success_rate']}")
            print(f"    - 평균 응답: {perf['response_time']['average']}")
            print(f"    - P95 응답: {perf['response_time']['p95']}")
        
        if report['bottlenecks']:
            print("\n발견된 병목 지점:")
            for bottleneck in report['bottlenecks'][:3]:
                print(f"  - [{bottleneck['severity'].upper()}] {bottleneck['type']}: {bottleneck['function']}")
        
        if report['recommendations']:
            print("\n권장사항:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)


async def main():
    """메인 실행 함수"""
    # 테스트 매니저 초기화
    tester = StressTestManager()
    
    # 테스트 시나리오
    test_scenarios = [
        {"users": 100, "name": "소규모 테스트"},
        {"users": 1000, "name": "중규모 테스트"},
        {"users": 5000, "name": "대규모 테스트"},
        {"users": 10000, "name": "최대 부하 테스트"}
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n{'='*60}")
        logger.info(f"{scenario['name']} 시작: {scenario['users']}명 사용자")
        logger.info(f"{'='*60}")
        
        # 테스트 실행
        await tester.run_concurrent_test(scenario['users'])
        
        # 보고서 생성
        report = tester.generate_report()
        
        # 결과 저장 및 출력
        tester.save_report(report, f"stress_test_{scenario['users']}_users.json")
        tester.print_summary(report)
        
        # 다음 테스트 전 초기화
        tester.results.clear()
        tester.concurrent_users = 0
        tester.max_concurrent_users = 0
        
        # 테스트 간 대기
        if scenario != test_scenarios[-1]:
            logger.info("\n다음 테스트까지 30초 대기...")
            await asyncio.sleep(30)
    
    logger.info("\n모든 스트레스 테스트가 완료되었습니다.")


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())